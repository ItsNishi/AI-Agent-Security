# Defense Patterns for AI Agent Security

## 1. Input Sanitization

### Strip HTML Comments

The most direct defense against trojanized skill attacks. Before the LLM processes any skill or context file, strip HTML comments.

```python
import re

def Strip_Html_Comments(Content: str) -> str:
	"""Remove HTML comments from markdown content before LLM processing."""
	return re.sub(r"<!--[\s\S]*?-->", "", Content)
```

**Limitation**: This only catches one encoding. Attackers can use:
- Zero-width Unicode characters (U+200B, U+FEFF) to hide text
- Base64-encoded instructions that the LLM is told to decode
- Markdown reference-style links with instruction payloads
- Unicode homoglyphs that look like whitespace but aren't

### Validate Tool Calls

Before executing any tool the agent wants to invoke, check it against an allowlist:

```python
Allowed_Commands = {
	"npm audit",
	"pip-audit",
	"govulncheck",
	"git status",
	"git diff",
}

def Validate_Command(Command: str) -> bool:
	"""Check if a command is in the approved list."""
	Base_Command = Command.strip().split("|")[0].strip()
	return Base_Command in Allowed_Commands
```

**Key rule**: Never allow piped commands (`|`) to pass through unexamined. `curl | bash` is almost never legitimate in an automated context.

## 2. Architectural Defenses

### Sandboxing

Run agent tool calls in isolated environments with restricted capabilities:

- **No network access** by default (allowlist specific domains if needed)
- **Read-only filesystem** except for designated output directories
- **No access to credentials**, environment variables, or SSH keys
- **Resource limits** (CPU, memory, time) to prevent abuse

Implementation options:
- Docker containers with `--network=none`
- seccomp/AppArmor profiles
- Firejail for lightweight sandboxing
- VM-level isolation for high-security contexts

### Permission Models

Classify tool calls by risk level:

| Level | Examples | Approval |
|---|---|---|
| **Read** | File read, search, list | Auto-approve |
| **Write** | File create/edit | Auto-approve in project dir |
| **Execute** | Shell commands | User approval required |
| **Network** | HTTP requests, curl | User approval + URL allowlist |
| **Destructive** | Delete, force-push, rm | Explicit user confirmation |

### Human-in-the-Loop

Critical operations should always require explicit user approval:

- Any shell command execution
- Network requests to external URLs
- File operations outside the project directory
- Git operations that affect remote repos (push, PR creation)

The Claude Code permission model already implements this partially -- tool calls can be configured to require approval. The defense gap is that skills/CLAUDE.md content is treated as pre-approved instructions.

**Approval fatigue caveat**: Lakera's Q4 2025 data shows users routinely set "always allow" on tool calls, completely negating this defense. Permission models only work if they balance security with usability.

### Microsoft Spotlighting

Microsoft's technique for separating system instructions from data content using special delimiters. Reduces success rate of indirect prompt injection by making it harder for injected content to be interpreted as instructions.

### Instruction Hierarchy (OpenAI Approach)

Formal trust levels for different instruction sources:

```
System (highest trust)
    |
Developer instructions
    |
User messages
    |
Tool output (lowest trust)
```

Content at lower levels cannot override higher-level instructions. OpenAI published research on training models to respect this hierarchy, but enforcement remains imperfect.

### Dual-LLM Pattern

One LLM processes the task, a second monitors the first for injection indicators:

- Monitor LLM reviews all inputs before the primary LLM sees them
- Monitor LLM reviews all outputs before they reach the user
- High overhead (doubles compute cost) but catches many attacks
- The monitor itself can potentially be injected -- turtles all the way down

## 3. Agent-Specific Mitigations

### Skill Vetting

Before installing any skill:

1. **Read the raw source** -- not the rendered preview
2. **Search for HTML comments**: `grep -n '<!--' SKILL.md`
3. **Search for encoded content**: `grep -nE '(base64|atob|decode|\\x[0-9a-f])' SKILL.md`
4. **Check for pipe-to-shell patterns**: `grep -nE '(curl|wget|fetch).*\|.*(bash|sh|python|node)' SKILL.md`
5. **Review the description field** for persistence triggers ("ALWAYS", "every task", "automatically")
6. **Verify the author** -- check their GitHub history, account age, other repos

### Output Validation

Monitor what the agent produces, not just what it receives:

- Flag any generated shell commands containing `curl | bash`, encoded payloads, or network exfiltration patterns
- Compare tool call patterns against a baseline (a "security review" skill shouldn't be making network requests)
- Log all tool calls for post-incident analysis

### Instruction Hierarchy

Enforce a strict trust hierarchy:

```
System prompt (highest trust)
    |
Platform-level CLAUDE.md
    |
Project-level CLAUDE.md
    |
User messages
    |
Skills / plugins
    |
MCP tool descriptions
    |
External data (lowest trust -- treat as untrusted input)
```

Content at lower trust levels should never be able to override higher-level instructions. This is the fundamental architectural fix for prompt injection -- but it's extremely difficult to enforce in practice because LLMs don't have a native concept of trust levels.

## 4. MCP-Specific Defenses

### Tool Definition Pinning

Hash tool definitions on first approval. Alert on any changes. This prevents rug pull attacks where a server modifies tool behavior after initial trust is established.

```python
import hashlib
import json

def Pin_Tool_Definition(Tool_Def: dict) -> str:
	"""Generate a hash of a tool definition for change detection."""
	Canonical = json.dumps(Tool_Def, sort_keys=True)
	return hashlib.sha256(Canonical.encode()).hexdigest()

def Verify_Tool_Definition(Tool_Def: dict, Expected_Hash: str) -> bool:
	"""Verify a tool definition hasn't changed since approval."""
	return Pin_Tool_Definition(Tool_Def) == Expected_Hash
```

### Tool Namespacing

Require `server_name/tool_name` format to prevent shadowing. If two servers both expose `read_file`, the agent must distinguish `trusted_fs/read_file` from `sketchy_util/read_file`.

### Cross-Server Isolation

Isolate each server's tool descriptions so they cannot influence how other servers' tools are used. A malicious `add` tool's description should not be able to instruct the LLM to redirect `send_email` to an attacker's address.

### MCP Scanner (Pre-Connection)

Invariant Labs' [`mcp-scan`](https://github.com/invariantlabs-ai/mcp-scan) scans MCP tool definitions for injection payloads before connecting. Analyzes descriptions, parameter schemas, and metadata for suspicious content. Should be part of any MCP server vetting process.

### What the MCP Spec Should Address

The protocol currently lacks:
- Mandatory authentication between client and server
- Tool integrity verification (hashing, signing, pinning)
- Permission/capability model (weather tool has same influence as shell_exec)
- Audit logging requirements
- Isolation model for multi-server environments

Source: [AuthZed MCP Breach Timeline](https://authzed.com/blog/timeline-mcp-breaches), [Practical DevSecOps MCP Security](https://www.practical-devsecops.com/mcp-security-vulnerabilities/)

## 5. Memory Poisoning Defenses

Memory poisoning is classified as ASI06 in OWASP Agentic AI Top 10 (2026). Unlike session-scoped injection, poisoned memory persists across sessions.

### Defenses (from Unit 42 Research)

- **Content filtering for untrusted sources** -- sanitize all external content before it enters the summarization pipeline
- **URL allowlists** restricting agent web access to known-good sources
- **Guardrails with prompt-attack policies** -- e.g., Amazon Bedrock Guardrails
- **Lambda pre-processing** -- custom validation rules before memory storage
- **Comprehensive logging** -- Model Invocation Logs and Trace features for forensic analysis
- **Real-time monitoring** -- detect anomalous memory writes

### Key Insight

The attack exploits forged XML tags placed outside `<conversation>` blocks. The summarization LLM interprets these as system instructions rather than user content. Defense requires treating ALL content entering the memory pipeline as untrusted input -- including the output of the summarization step itself.

Source: [Unit 42 -- Memory Poisoning](https://unit42.paloaltonetworks.com/indirect-prompt-injection-poisons-ai-longterm-memory/)

## 6. Vibe Coding Defenses

Vibe-coded applications (built rapidly with AI, minimal human review) have consistently terrible security posture. Key stats from Veracode's GenAI Code Security Report 2025:

- **45%** of AI-generated code introduces security vulnerabilities
- **71%** of AI-generated auth code has vulnerabilities
- **86%** XSS prevention failure rate

### Secure Development Practices

**Review AI code like third-party code:**
- Never deploy AI-generated auth logic without manual review
- Run SAST on ALL AI-generated code regardless of perceived simplicity
- Validate encryption, error handling, and access control manually

**Prompt for security explicitly:**
- "Use parameterized queries for all database operations"
- "Hash passwords with bcrypt, cost factor 12"
- "Implement Row-Level Security policies for all Supabase tables"
- "Never expose API keys in client-side code"

**CI/CD pipeline integration:**
- SAST (static analysis) on every commit
- SCA (Software Composition Analysis) for dependency checking
- DAST (dynamic testing) against running application
- IDE plugins for real-time security scanning during development

**Watch for AI-specific failure modes:**
- **Package hallucination**: AI suggests non-existent libraries. Attackers create real packages with those names (typosquatting supply chain attack).
- **Client-side only security**: AI generates frontend auth checks but no backend validation (the Moltbook pattern)
- **Hardcoded secrets**: API keys in client-side JavaScript
- **Missing RLS/access control**: Database accessible without auth

### Case Study: Moltbook (Jan 2026)

A social platform for AI agents, built entirely by AI with zero manual code. [Wiz found](https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys) unauthenticated access to the entire production database within minutes:
- Supabase API key hardcoded in client-side JS
- Row-Level Security never implemented
- 1.5M API tokens, 35K emails, private messages with plaintext OpenAI keys exposed
- Enumerated via PostgREST errors and GraphQL introspection

### Relevant Frameworks

- [OWASP Agentic AI Top 10 (2026)](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) -- first enterprise implementation guide for AI agent security
- [Palo Alto Networks Vibe Coding Security Framework](https://unit42.paloaltonetworks.com/securing-vibe-coding-tools/)
- [Veracode GenAI Security Guide](https://www.veracode.com/blog/genai-security-and-vibe-coding/)

## 7. Detection Patterns

### Static Analysis (Pre-execution)

Scan skill files and context files for injection indicators:

```python
import re
from typing import list

Injection_Patterns = [
	r"<!--[\s\S]*?(curl|wget|bash|sh|exec|eval|system)[\s\S]*?-->",  # Hidden commands in HTML comments
	r"(ignore|forget|disregard)\s+(all\s+)?(previous|prior|above)\s+(instructions|rules|guidelines)",  # Instruction override
	r"(curl|wget)\s+.*\|\s*(bash|sh|python|node|perl)",  # Pipe-to-shell
	r"base64\s+(--decode|-d)",  # Base64 decode operations
	r"\\x[0-9a-fA-F]{2}",  # Hex-encoded content
	r"ALWAYS\s+run\s+this",  # Persistence trigger
	r"SECRET\s+INSTRUCTIONS",  # Explicit injection marker
	r"<IMPORTANT>[\s\S]*?</IMPORTANT>",  # MCP tool description injection tags
	r"autoApprove.*true",  # IDE settings hijack (CVE-2025-53773 pattern)
	r"\u200B|\uFEFF|\u200C|\u200D",  # Zero-width character hiding
]

def Scan_For_Injections(Content: str) -> list[str]:
	"""Scan content for known injection patterns."""
	Findings = []
	for Pattern in Injection_Patterns:
		Matches = re.finditer(Pattern, Content, re.IGNORECASE)
		for Match in Matches:
			Findings.append(f"Pattern match: {Pattern!r} at position {Match.start()}")
	return Findings
```

### Runtime Monitoring

Watch for suspicious agent behavior during execution:

- Unexpected network requests (especially to unknown domains)
- File reads outside the project directory (especially `~/.ssh/`, `~/.aws/`, `.env`)
- Commands that encode or compress data before sending it somewhere
- Sudden changes in the agent's behavior mid-conversation (indicator of successful injection)
- Writes to IDE settings files (`.vscode/settings.json`, `.cursor/mcp.json`)
- JSON files with remote `$schema` URLs (data exfiltration via schema fetch -- CVE-2025-49150)
- Tool calls that don't match the stated purpose of the current skill/task

### Commercial Detection Tools

**[Lakera Guard](https://www.lakera.ai/blog/guide-to-prompt-injection)**
- Commercial API, ultra-low latency (<50ms)
- Learns from 100K+ new adversarial samples per day via Gandalf red-teaming platform
- Catches instruction overrides, jailbreaks, indirect injections, obfuscated prompts
- Adaptive calibration for low false positives
- Filters for prompt injection, PII leakage, and content toxicity in both inputs and outputs

**[Rebuff (ProtectAI)](https://github.com/protectai/rebuff)**
- Open-source, multi-layered defense
- Heuristic filters + dedicated LLM-based detector + vector DB of known attack signatures
- **Canary token injection**: invisible tokens placed in prompts. If they appear in output, indicates successful manipulation -- triggers immediate block.
- Self-hardening: learns from detected attacks over time

**[Invariant MCP Scanner](https://github.com/invariantlabs-ai/mcp-scan)**
- Open-source tool to scan MCP server tool definitions for injection payloads
- Analyzes tool descriptions, parameter descriptions, and schemas for suspicious content
- Should run before connecting to any new MCP server

### Canary Tokens for Agents

Place invisible markers in agent context. If a canary appears in output or tool calls, the agent has been compromised:

```python
import uuid

def Generate_Canary() -> str:
	"""Generate a unique canary token to embed in agent context."""
	return f"CANARY-{uuid.uuid4().hex[:12]}"

def Check_Output_For_Canary(Output: str, Canary: str) -> bool:
	"""Check if agent output contains a canary (indicates injection success)."""
	return Canary in Output
```

Rebuff uses this technique in production. The canary is injected into the system prompt; if the model's output contains it, something manipulated the model into leaking internal context.

## 8. The Fundamental Problem

Prompt injection is unsolved. All current defenses are mitigations, not solutions. The core issue:

> LLMs cannot reliably distinguish between instructions and data.

Every defense pattern above can be bypassed by a sufficiently creative attacker. The current best practice is **defense in depth** -- layer multiple mitigations so that bypassing one doesn't compromise the entire system.

As [AuthZed noted](https://authzed.com/blog/timeline-mcp-breaches): "MCP presents a cutting-edge threat surface, yet the breaches detailed are rooted in timeless flaws: over-privilege, inadequate input validation, and insufficient isolation. AI changes the interface, not the fundamentals of security."

The most promising research directions:
- **Formal instruction boundaries** -- architectural changes to LLMs that create a hard separation between system instructions and user/data content
- **Capability-based security** -- agents that can only perform explicitly granted actions, regardless of what their instructions say
- **Verified tool calls** -- cryptographic verification that a tool call originated from legitimate instructions, not injected content
- **Cryptographic tool provenance** -- signed tool definitions verifiable against a trusted registry
- **Multi-agent verification pipelines** -- separate agents for planning, execution, and review with independent contexts
- **Immune system-inspired defense** -- multi-layer detection combining pattern matching (innate) with adaptive detection (learned)

### Standards and Frameworks

- **[OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)** -- prompt injection is #1 risk
- **OWASP Agentic AI Top 10 (2026)** -- covers AI coding agents, memory poisoning (ASI06), tool poisoning
- **[AIVSS](https://aivss.owasp.org/)** -- AI Vulnerability Scoring System for agentic AI risks
- **NIST AI Risk Management Framework** -- general AI security guidance
- **[Vulnerable MCP Project](https://vineethsai.github.io/vulnerablemcp/)** -- comprehensive MCP security database

### Key Research Sources

- [Invariant Labs -- MCP Tool Poisoning](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)
- [Simon Willison -- MCP Has Prompt Injection Problems](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/)
- [Embrace The Red -- Copilot RCE (CVE-2025-53773)](https://embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/)
- [Unit 42 -- Memory Poisoning](https://unit42.paloaltonetworks.com/indirect-prompt-injection-poisons-ai-longterm-memory/)
- [Unit 42 -- MCP Attack Vectors](https://unit42.paloaltonetworks.com/model-context-protocol-attack-vectors/)
- [Lakera -- Q4 2025 Attack Trends](https://www.lakera.ai/blog/the-year-of-the-agent-what-recent-attacks-revealed-in-q4-2025-and-what-it-means-for-2026)
- [The Hacker News -- IDEsaster 30+ CVEs](https://thehackernews.com/2025/12/researchers-uncover-30-flaws-in-ai.html)
- [Wiz -- Moltbook Breach](https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys)
- [arXiv -- Prompt Injection in Agentic Coding Assistants (Jan 2026 SoK)](https://arxiv.org/html/2601.17548v1)
- [MDPI -- Comprehensive Prompt Injection Review (2025)](https://www.mdpi.com/2078-2489/17/1/54)
- [AuthZed -- Timeline of MCP Breaches](https://authzed.com/blog/timeline-mcp-breaches)
