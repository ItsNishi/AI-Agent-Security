# AI Application Ecosystem Security

Security research across AI marketplaces, agent frameworks, coding tools, and their interconnected attack surfaces -- organized by attack surface rather than vendor.

---

## Table of Contents

1. [Plugin & Marketplace Ecosystems](#1-plugin--marketplace-ecosystems)
2. [MCP Server Security](#2-mcp-server-security)
3. [Agent Frameworks](#3-agent-frameworks)
4. [AI IDE & Coding Tool Security](#4-ai-ide--coding-tool-security)
5. [AI Agent Attack Taxonomy](#5-ai-agent-attack-taxonomy)
6. [Real-World Incidents](#6-real-world-incidents)
7. [Defense Frameworks](#7-defense-frameworks)
8. [Cross-Cutting Themes](#8-cross-cutting-themes)
9. [Sources](#9-sources)

---

## 1. Plugin & Marketplace Ecosystems

### 1.1 OpenAI GPT Store / ChatGPT Plugins

#### Plugin Permission Model

OpenAI's plugin/Actions system allows custom GPTs to make third-party API calls via RESTful endpoints, configured through OpenAPI schemas.

- **Authentication options**: None, API Key, or OAuth -- default is "None"
- **Domain restriction**: Configurable but not enforced by default ("Allow all domains for GPT actions")
- **API keys**: Encrypted at rest in OpenAI's database
- **Access control**: Role-based (Workspace Admins/Owners can reassign ownership, manage permissions, audit GPT activity)
- **Sharing limits**: Custom GPTs can be shared with up to 100 users/groups combined

**Fundamental weakness**: The permission model trusts plugin developers to implement secure backends. OpenAI acts as a broker but does not sandbox API calls or validate what data flows to third-party endpoints.

#### Salt Security Research (March 2024) -- Three Vulnerability Classes

Salt Labs uncovered three distinct vulnerability types in ChatGPT plugins:

**1. OAuth Authentication CSRF (ChatGPT itself)**
- The initial OAuth implementation did not use a random `state` value to prevent CSRF
- An attacker who tricked a victim into clicking a crafted link could install a malicious plugin on the victim's account
- The victim did NOT need to confirm the installation
- Once installed, the attacker-controlled plugin could see all private chat data (credentials, passwords, sensitive data)

**2. PluginLab Account Takeover (Zero-Click)**
- PluginLab did not properly authenticate user accounts during plugin installation
- An attacker could insert another user's ID and obtain a code representing the victim
- Demonstrated on the AskTheCode plugin (GitHub integration) -- allowed full GitHub account takeover
- Zero-click exploit: no victim interaction required beyond using the plugin

**3. OAuth Redirection Manipulation**
- Several plugins were susceptible to OAuth redirect URI manipulation
- Attackers could insert malicious URLs to steal user credentials and session tokens

All vulnerabilities were reported to OpenAI, PluginLab.AI, and Kesem AI in summer 2023 and patched in following months.

#### Custom GPT Vulnerabilities

**System Prompt Extraction**:
- Approximately 95% of custom GPTs display inadequate security measures against common threats (arXiv research)
- Techniques including hex injection, many-shot prefix attacks, and knowledge poisoning can bypass safety guardrails
- Successful extraction of: proprietary system instructions, raw contents of uploaded Knowledge files, backend API schemas

**Data Exfiltration**:
- ChatGPT has no mechanism to stop sending PII to third-party APIs
- Third-party APIs can and will collect that data
- Moonlight research team documented custom GPTs in the marketplace explicitly designed for data exfiltration, masquerading as legitimate tools

**Tenable Research (2025)**:
- Multiple persistent vulnerabilities in ChatGPT allowing exfiltration of user memories and chat history
- Present in the latest GPT-5 model

#### ChatGPT Atlas Browser Vulnerabilities (October 2025)

The ChatGPT Atlas browser agent introduced new attack surfaces:

**Omnibox Prompt Injection**:
- Malicious prompts disguised as URLs are treated as high-trust "user intent" text
- The browser can be tricked into executing hidden commands

**Clipboard Injection**:
- Hidden "copy to clipboard" actions on web pages overwrite user's clipboard with malicious links
- Redirects users to phishing sites, steals credentials including MFA codes

**Memory Injection ("Tainted Memories")**:
- CSRF flaw enables injection of malicious instructions into ChatGPT's persistent memory
- Corrupted memory persists across devices and sessions
- Potential for full account, browser, or connected system takeover

**Phishing Defense Failure**:
- LayerX testing: ChatGPT Atlas stopped only 5.8% of malicious web pages
- Atlas users are 90% more vulnerable to phishing compared to other browsers

**OpenAI's Response**: Extensive red-teaming, model training to reward ignoring malicious instructions, additional guardrails. However, OpenAI acknowledges prompt injection remains a "frontier, unsolved security problem."


### 1.2 HuggingFace Model Supply Chain

#### Pickle Deserialization Attacks

Pickle is the dominant ML model serialization format (80%+ of models in the ecosystem). It allows arbitrary Python code execution during deserialization.

**nullifAI Technique** (ReversingLabs, February 2025):
- Discovered two malicious HuggingFace models NOT flagged as 'unsafe' by Hugging Face's scanning
- Malicious payload inserted at the beginning of the Pickle stream
- PickleScan validates files first, then scans -- but Pickle deserialization works like an interpreter, executing opcodes as they are read
- The malicious payload executes before the scanner reaches it

**JFrog Discoveries (2024)**:
- Found intentionally malicious models on HuggingFace
- One payload initiated a reverse shell connection to an external IP (210.117.212.93)
- Dedicated security experts assigned to scan all HuggingFace models

**PickleScan Zero-Days** (JFrog, 2025):
- Three zero-day vulnerabilities in PickleScan itself
- The unsafe globals check can be bypassed by using subclasses of dangerous imports instead of exact module names
- Enables large-scale supply chain attacks via undetectable malicious code in ML models

#### API Token Leaks and Supply Chain

**Scale of exposure**:
- 1,681 valid HuggingFace tokens exposed through HuggingFace and GitHub (Lasso Security research)
- Access to 723 organizations' accounts, including Meta, HuggingFace, Microsoft, Google, VMware
- 655 tokens had write permissions; 77 had write access to organization repositories
- Potential for model poisoning, dataset tampering, and neural backdoor implantation

**HuggingFace Spaces Hack**:
- Unknown number of tokens exposed following unauthorized activity on the Spaces platform
- Resulted in direct supply chain risk: hijacking or altering widely used models

#### Security Scanning and Defenses

**HuggingFace's measures**:
- Malware scanning, pickle scanning, and secrets scanning on every file in repositories
- Developed **safetensors** format: stores only key model data, contains no executable code
- Conversion service to encourage migration from pickle to safetensors

**JFrog Partnership** (March 2025):
- Integrated security scanning tools in the HuggingFace platform
- JFrog Xray and JFrog Advanced Security scan AI/ML model artifacts at every lifecycle stage
- Detection covers serialization attacks, known CVEs, backdoors

**Safetensors Service Vulnerability** (HiddenLayer):
- Demonstrated that threat actors could compromise the Safetensors conversion service itself
- Possible to send malicious pull requests and hijack models submitted through the service


### 1.3 Browser AI Extensions

#### Malicious AI Chrome Extensions (2025-2026)

**AiFrame Campaign** (LayerX):
- 30 malicious Chrome extensions installed by 300,000+ users
- Masqueraded as AI assistants (AI Sidebar: 70K users, Gemini AI Sidebar: 80K users, AI Assistant: 60K users, ChatGPT Translate: 30K users)
- Stole credentials, email content, browsing information

**Technical approach**:
- No local AI functionality -- render full-screen iframe to remote domain
- Publisher can change extension logic at any time without pushing an update
- 15 extensions specifically targeted Gmail with dedicated content scripts running at `document_start`
- Injected UI elements to harvest email data

**ChatGPT/DeepSeek Chat Exfiltration** (January 2026):
- Two Chrome extensions designed to exfiltrate OpenAI ChatGPT and DeepSeek conversations
- Also captured browsing data
- Sent to attacker-controlled servers
- 900,000 users affected

#### Credential Theft Statistics

- Infostealer malware exposed 300,000+ ChatGPT credentials in 2025
- AI platforms have reached the same credential risk profile as core enterprise SaaS solutions
- Shadow AI (unauthorized AI tool usage) is a growing data exfiltration vector


### 1.4 VS Code Extension Supply Chain

#### Namespace Squatting (January 2026)

**Discovery** (Koi Security):
- AI-powered VS Code forks (Cursor, Windsurf, Google Antigravity, Trae) inherit Microsoft's recommended extension list
- These extensions exist in Microsoft's marketplace but NOT in Open VSX
- Namespaces were unclaimed -- any attacker could register them

**Impact**: Users prompted to install extensions that could be entirely attacker-controlled.

**Response**:
- Koi researchers proactively claimed namespaces with non-functional placeholder extensions
- Cursor fixed December 1, 2025
- Google removed 13 recommendations December 26, marked fixed January 1, 2026
- Windsurf: no response as of disclosure

#### GlassWorm: Self-Propagating Extension Worm (October 2025)

**Discovery** (Koi Security / Truesec):
- Sophisticated supply chain attack targeting both Open VSX and Microsoft VS Code marketplaces
- Seven Open VSX extensions compromised in first wave (~36,000 downloads)
- VS Code extensions auto-update by default, enabling silent widespread infection

**Technical innovation**:
- Used invisible Unicode characters (variation selectors, Private Use Area characters) to hide malicious code
- Characters produce no visual output in code editors
- No traditional obfuscation or minification

**ZOMBI Module**:
- Final payload transforms infected workstations into botnet nodes
- Harvests: NPM auth tokens, GitHub tokens, Open VSX credentials, Git credentials
- Targets 49 cryptocurrency wallet extensions (Coinbase, MetaMask, Phantom, etc.)
- Blockchain-based C2 infrastructure on Solana -- cannot be taken down

**Second wave** (December 2025):
- 24 additional malicious extensions impersonating popular developer tools

#### Broader VS Code Marketplace Issues

**Wiz Research**:
- Found 550+ validated secrets distributed across 500+ extensions from hundreds of publishers

**Checkmarx**:
- Ongoing efforts to identify and take down malicious VS Code extensions

---

## 2. MCP Server Security

### 2.1 Protocol Architecture Risks

MCP's design introduces several fundamental security gaps:

- **stdio transport**: Frictionless local server execution creates a low-barrier path for running untrusted third-party code with full local privileges
- **No built-in authentication**: The protocol itself does not mandate authentication between client and server
- **No tool integrity verification**: Tool definitions are not signed or version-locked
- **Dynamic tool registration**: Tools can be registered, modified, and removed at runtime without user notification
- **Plaintext credential storage**: Many MCP implementations store API keys for third-party services in plaintext with world-readable permissions (Trail of Bits discovery)

### 2.2 Tool Poisoning & Rug Pulls

#### Tool Poisoning Attacks (Invariant Labs, April 2025)

Invariant Labs defined and demonstrated the Tool Poisoning Attack (TPA) paradigm:

**Mechanism**: Malicious instructions embedded in a tool's description during registration. The agent treats these instructions as required steps in the tool's legitimate operation.

**WhatsApp Exfiltration PoC**:
- A malicious MCP server combined with a legitimate whatsapp-mcp server in the same agent
- The malicious server's tool description instructed the agent to silently exfiltrate the user's entire WhatsApp history
- Bypasses traditional DLP because it looks like normal AI behavior (sending a WhatsApp message)
- Data transmitted to attacker's phone number via WhatsApp itself

**Cross-Server Shadowing**:
- A malicious server does NOT need the agent to use its tools directly
- Instead, it modifies the agent's behavior with respect to OTHER trusted servers
- Tool descriptions on the malicious server can hijack how the agent interacts with legitimate tools

**MCPTox Benchmark**:
- Academic benchmark comprising 45+ real-world MCP servers across 8 application domains
- 1,312 malicious test cases from 11 risk categories (Privacy Leakage, Message Hijacking, etc.)

#### Confused Deputy Attacks

- Agent with higher privileges performs unauthorized tasks on behalf of lower-privileged attacker
- LLMs trust anything that sends convincing-sounding tokens
- Combination of tool actions + untrusted input = attacker control

#### Rug Pull / Bait-and-Switch Attacks

**Mechanism**: Tool definitions mutate after initial user approval. A tool that appears safe on Day 1 can silently reroute API keys to an attacker by Day 7.

**TOCTOU Weakness**: Classic Time-of-Check-Time-of-Use vulnerability. If the tool's identifier doesn't change, or the client doesn't detect subtle metadata modifications, no new approval prompt is presented.

**Key facts**:
- Standard MCP clients do NOT re-fetch and re-verify tool definitions on every invocation
- Tool underlying code and behavior can be modified server-side without notification
- The tool can first establish trust via legitimate behavior, then inject hidden instructions later

**ETDI (Enhanced Tool Definition Interface)**: Proposed academic solution using OAuth 2.0, cryptographic identity, immutable versioned definitions, explicit permission/scope management, and dynamic contextual policy evaluation.

### 2.3 CVEs

| CVE | Component | CVSS | Description |
|-----|-----------|------|-------------|
| CVE-2025-6514 | mcp-remote | 9.6 | OS command injection via crafted `authorization_endpoint` URL. First real-world full RCE on client OS from untrusted MCP server. 437K+ downloads affected. Fixed in v0.1.16 |
| CVE-2025-49596 | MCP Inspector | 9.4 | CSRF vulnerability enabling RCE by visiting a crafted webpage |
| CVE-2025-68145 | Anthropic mcp-server-git | -- | Path validation bypass |
| CVE-2025-68143 | Anthropic mcp-server-git | -- | Unrestricted git_init (can turn .ssh into a git repo) |
| CVE-2025-68144 | Anthropic mcp-server-git | -- | Argument injection in git_diff |
| CVE-2025-53110 | Anthropic Filesystem MCP | 7.3 | Directory containment bypass |
| CVE-2025-53109 | Anthropic Filesystem MCP | 8.4 | Symlink bypass to code execution (LPE) |

**Additional unpatched issues**:
- Microsoft MarkItDown MCP server: SSRF vulnerability can compromise AWS EC2 instances via metadata service exploitation
- GitHub Kanban MCP server: Arbitrary command execution through tool interface

### 2.4 Security Research Organizations

**Trail of Bits**:
- Released `mcp-context-protector` (beta) -- security wrapper that proxies tool calls
- Defends against "line jumping" attacks (prompt injection via tool descriptions and ANSI terminal escape codes)
- Documented plaintext credential storage patterns across MCP implementations

**Elastic Security Labs** (September 2025):
- Found 43% of tested MCP implementations contained command injection flaws
- 30% permitted unrestricted URL fetching

**Palo Alto Unit 42**:
- Documented attack vectors through MCP sampling feature
- Three PoC examples in coding copilot context

**Checkmarx**:
- Identified 11 emerging MCP security risks including confused deputy, context poisoning, tool schema manipulation, privilege escalation through over-delegation

**Simon Willison** (April 2025):
- Early documentation of MCP prompt injection problems

**Academic Papers**:
- "Systematic Analysis of MCP Security" (arXiv 2508.12538)
- "When MCP Servers Attack: Taxonomy, Feasibility, and Mitigation" (arXiv 2509.24272)
- "Securing the Model Context Protocol (MCP): Risks, Controls, and Governance" (arXiv 2511.20920)
- "MCP Safety Audit: LLMs with the Model Context Protocol Allow Major Security Exploits" (2025)

---

## 3. Agent Frameworks

### 3.1 AutoGPT / AgentGPT

**CVE-2024-6091 -- Shell Command Denylist Bypass (CVSS 9.8)**
- Affects significant-gravitas/autogpt v0.5.1
- Attackers bypass the shell command denylist by modifying the path
	- e.g., `/bin/./whoami` bypasses a denylist entry for `/bin/whoami`
- Root cause: naive string matching without path normalization
- 166,000+ downstream projects at risk

**General Security Issues:**
- Unrestricted tool access -- agents can execute arbitrary shell commands, browse the web, write files
- No sandboxing by default in early versions
- Agent loop exploitation -- recursive task decomposition can be hijacked to perform unintended actions
- Shared memory across agent loops allows persistent context poisoning
- Framework-agnostic vulnerabilities: 94.4% of state-of-the-art LLM agents vulnerable to prompt injection


### 3.2 CrewAI

**Leaked GitHub Token (CVSS 9.2)**
- Internal GitHub token exposure could have enabled supply chain attacks
- Disclosed by Noma Security

**Penetration Testing Results (arxiv 2512.14860):**
- CrewAI refusal rate: 30.8% (vs AutoGen's 52.3%)
- Control-flow hijacking: GPT-4o on CrewAI can be convinced by a local file to exfiltrate user data
	- 65% success rate for data exfiltration
- Worst case: Grok 2 on CrewAI rejected only 2 of 13 attacks (15.4% refusal rate)
- SSRF attacks succeeded ~60% of the time in both frameworks
- Information disclosure: models frequently revealed system prompts, tool schemas, agent configs

**Architectural Weakness:**
- Hierarchical delegation model: orchestrator is central coordinator
- Specialist agents never communicate directly -- all through orchestrator
- Weakness: orchestrator can be hijacked, compromising entire chain


### 3.3 LangChain / LangGraph

**CVE-2025-68664 "LangGrinch" -- Serialization Injection (CVSS 9.3)**
- Reported December 4, 2025 by Yarden Porat
- `dumps()` and `dumpd()` fail to escape dictionaries containing the reserved `lc` key
- Attack: inject `lc` key into content that gets serialized then deserialized
- Result: arbitrary object instantiation, secret extraction from environment variables
- 12 distinct vulnerable flows identified (event streaming, logging, message history, caches)

**Attack Vectors**:
- LLM response fields (`additional_kwargs`, `response_metadata`) controlled via prompt injection, then serialized/deserialized in streaming operations
- Loading untrusted manifests from LangChain Hub via `hub.pull()`
- Using `LangSmithRunChatLoader` with runs containing untrusted messages

**Impact**:
- Secret extraction from environment variables (when `secrets_from_env=True`, previously the default)
- Instantiation of classes within pre-approved trusted namespaces (`langchain_core`, `langchain`, `langchain_community`)
- Arbitrary code execution via Jinja2 templates

**Patch** (versions 1.2.5 and 0.3.81):
- `allowed_objects` parameter defaults to `core` (limiting deserialization to core objects)
- `secrets_from_env` changed from `True` to `False`
- Jinja2 templates blocked by default

**CVE-2025-68665 -- LangChain.js Serialization Injection (CVSS 8.6)**
- Same class of vulnerability in JavaScript implementation

**CVE-2024-8309 -- GraphCypherQAChain Prompt Injection**
- User-controlled natural language input directly embedded into LLM prompts
- Enables full database compromise via Cypher injection

**Hub-Specific Risks**:
- **Pulled manifests**: Deserialized locally and may include injected structures if source is untrusted
- **Community-contributed chains**: Many pre-built chains in the LangChain repository were contributed by the community and used directly in applications without audit
- **LangSmith integration**: In some configurations, allowed evaluation of tool definitions containing `eval()` or other unsafe functions

**Earlier Vulnerabilities**:

| CVE | Description |
|-----|-------------|
| CVE-2024-36480 | RCE under certain conditions through eval() in tool execution contexts |
| CVE-2023-46229 | SSRF through crafted sitemaps (versions < 0.0.317). Discovered by Palo Alto Unit 42 |
| CVE-2023-44467 | Arbitrary code execution via unsafe evaluation in custom tools |


### 3.4 Microsoft Agent Framework

**Framework Consolidation (October 2025):**
- AutoGen + Semantic Kernel merged into "Microsoft Agent Framework" (public preview)
- AutoGen/SK entered maintenance mode (bug fixes and security patches only)
- Built-in OpenTelemetry observability, Microsoft Entra integration, prompt injection protection

**Security Characteristics from Penetration Testing:**
- AutoGen refusal rate: 52.3% (significantly stronger than CrewAI's 30.8%)
- Swarm-based handoff pattern provides better isolation than hierarchical delegation
- Peer-to-peer model allows attackers to manipulate transfer decisions, potentially bypassing orchestrator routing logic

**Defensive Behavior Patterns Identified:**
- Six distinct patterns including "hallucinated compliance" -- models fabricate outputs rather than executing or refusing attacks (novel finding)


### 3.5 Google Vertex AI

**Privilege Escalation via Service Agents:**
- Fresh vulnerabilities found in Vertex AI's permission model
- Service Agents (special Google Cloud accounts) automatically granted broad project-wide permissions
- Attacker with minimal "Viewer" role permissions can hijack high-privileged Service Agents
- Can retrieve access tokens for service agents
- Google's response: "working as intended"

**General Cloud AI Statistics (2025):**
- 84% of organizations use AI-related tools in the cloud
- 62% have at least one vulnerable AI package
- 1/3 of organizations experienced a cloud data breach involving an AI workload


### 3.6 Amazon Bedrock

**Security Posture:**
- Bedrock Guardrails (text and image outputs) block up to 88% of harmful outputs/hallucinations
- Automated Reasoning Checks
- AgentCore (October 2025): full-scale agent builder with access management and observability
- No major published CVEs specific to Bedrock agents as of early 2026
- Security controls rely on AWS IAM integration and VPC isolation


### 3.7 Devin (AI Software Engineer)

**Comprehensive Security Testing by Embrace The Red:**

*$500 Prompt Injection Research (April 2025):*
- Complete compromise achieved via indirect prompt injection
- Attack chain:
	1. Malicious instructions placed in a GitHub issue assigned to Devin
	2. Instructions reference a "support tool" for debugging
	3. Devin navigates to attacker-controlled website
	4. Downloads and executes malware binary (Sliver C2 implant)
	5. Despite permission errors, Devin independently escalated privileges
- Result: full remote shell, AWS credentials, API keys exfiltrated

**Data Exfiltration Methods:**
- `curl`/`wget` to external servers
- Python scripts connecting to third-party servers
- Image rendering in chat with sensitive data appended to URL

**Critical Security Gaps:**
- Unrestricted internet access by default
- No EDR or antivirus in sandbox
- Unsupervised Slack interaction -- entirely unsupervised agent operations
- Docker-based sandboxing provides some isolation but insufficient controls
- Over-reliance on model behavior rather than technical enforcement
- Reported to Cognition April 6, 2025


### 3.8 OpenHands (formerly OpenDevin)

**Zero-Click Data Exfiltration:**
- Renders images in chat -- enables zero-click exfiltration
- Prompt injection in website, source code, or document forces Markdown image rendering
- Attacker appends sensitive data to image URL query string
- GITHUB_TOKEN and any chat history/memory data subject to exfiltration
- Fix: Content-Security-Policy to restrict image loading to trusted domains

**Disclosure Timeline:**
- Reported March 13, 2025
- Follow-up March 20 -- no response
- Still untriaged by March 30
- Publicly disclosed August 9, 2025 (148 days after private disclosure)

**Sandbox Architecture:**
- Docker-based containerization, torn down post-session
- Agents restricted to their own environment
- Cross-agent interference prohibited by design

---

## 4. AI IDE & Coding Tool Security

### 4.1 IDEsaster: 30+ Vulnerabilities Across AI IDEs (December 2025)

Discovered by Ari Marzouk (MaccariTA) over six months of research. 24 CVEs assigned.

**Affected Products:**
- Cursor, Windsurf, Kiro.dev, GitHub Copilot, Zed.dev, Roo Code, Junie, Cline, Gemini CLI, Claude Code

**Attack Mechanism:**
- Combines prompt injection primitives with legitimate IDE features
- Context hijacking via pasted URLs, hidden Unicode characters, user-added references
- Results: information leakage, command execution, data theft, RCE
- The attack surface is the connection to unlimited data sources through MCP

**Notable CVEs:**
- CVE-2025-49150 (Cursor)
- CVE-2025-53097 (Roo Code)
- CVE-2025-58335 (JetBrains Junie)

**Core insight**: 100% of tested AI IDEs and coding assistants were vulnerable.


### 4.2 GitHub Copilot

**Private Repository Exfiltration (CVSS 9.6)**:
- Combined prompt injection with CSP bypass to silently exfiltrate source code and secrets from private repositories
- Remediated August 14, 2025 by disabling all image rendering in Copilot Chat

**RCE via Prompt Injection**:
- Achieved on Windows, macOS, and Linux through `.vscode/tasks.json` manipulation and malicious MCP server injection
- Exploits Copilot's unrestricted file modification capabilities

**Path Traversal (CVE-2025-62453)**:
- Local attackers could manipulate file access, retrieve sensitive information, inject malicious code

**Secret Leakage Statistics**:
- In ~20,000 repositories with Copilot active, 6.4% leaked at least one secret
- 40% higher than the 4.6% rate across all public repositories

**Empirical Vulnerability Research:**
- 733 code snippets analyzed: 29.5% of Python and 24.2% of JavaScript snippets had security weaknesses
- 1,689 Copilot-generated programs studied: ~40% found vulnerable
- 43 CWE categories detected in generated code
- Improvements over time: Python vulnerabilities reduced from 35.35% to 25.06%

**Vulnerability Amplification:**
- Copilot replicates vulnerabilities from existing codebases
- Insecure code in project context causes Copilot to generate more insecure code
- `/fix` command resolves only ~20% of security problems


### 4.3 Cursor

| CVE | Name | CVSS | Description |
|-----|------|------|-------------|
| CVE-2025-59944 | -- | -- | Case-sensitivity bypass on `.cursor/mcp.json`, enabling RCE. Fixed in v1.7 |
| CVE-2025-54135 | CurXecute | 8.6 | Prompt injection via MCP: `mcp.json` entries execute without confirmation. Exploitable via Slack message. Fixed in v1.3 (July 2025) |
| CVE-2025-54136 | MCPoison | -- | Trusted MCP config file modification: attacker silently swaps harmless MCP for malicious one without re-prompt. Fixed in v1.3 |

**Workspace Trust Disabled by Default:**
- Ships with VS Code Workspace Trust disabled
- Exposes users to silent code execution risks

**Rules File Backdoor**: See [note 12](./12_Agent_MD_Configuration_Files.md) for the full deep dive on hidden Unicode characters in `.cursorrules` and similar configuration files. Pillar Security demonstrated invisible instruction injection that manipulates AI into generating malicious code.


### 4.4 Windsurf

**Prompt Injection / Data Exfiltration**:
- Vulnerable to indirect prompt injection
- Can be exploited to leak sensitive source code, environment variables, and host information

**Extension Recommendation Vulnerability**:
- Recommends extensions non-existent in Open VSX registry
- Threat actors can claim namespace and upload malicious extensions
- Windsurf had not responded to researchers as of late November 2025

**Chromium Vulnerabilities**:
- 94+ known Chromium/V8 vulnerabilities from outdated Electron versions
- ~1.8 million developers exposed

**Security Certifications:**
- SOC 2 Type II certification
- Annual third-party penetration testing
- FedRAMP High accreditation available
- `.codeiumignore` for excluding sensitive directories


### 4.5 Cline

**Four Critical Flaws** (Mindgard, August 2025):
- DNS-based data exfiltration: leak API keys and environment variables via code comments
- `.clinerules` arbitrary code execution: bypasses user consent mechanisms
- TOCTOU vulnerabilities: gradual modification of shell scripts across analysis requests
- Malicious instructions in Python docstrings or Markdown configs

**Clinejection Supply Chain Attack** (Snyk/Adnan Khan):
- Prompt injection in Cline's Claude Issue Triage GitHub Actions workflow
- Any attacker with a GitHub account could compromise production Cline releases
- Active vulnerability window: December 21, 2025 to February 9, 2026
- Could publish malware to millions of developers through official release pipeline

**Cline CLI Supply Chain Attack** (February 17, 2026):
- Compromised npm token used to publish malicious `cline@2.3.0`
- Added `postinstall` script that installed OpenClaw package
- ~4,000 downloads in 8-hour window (3:26 AM - 11:30 AM PT)
- Root cause: researcher published prompt injection PoC; different actor weaponized it to obtain Cline publication credentials
- Fix: token revoked, npm publishing moved to OIDC provenance via GitHub Actions
- Users advised to update to 2.4.0+


### 4.6 Code Generation Vulnerability Statistics

**AI-Generated Code Vulnerability Rates:**
- ~36% of Copilot-generated code contains CWEs
- ~40% of programs generated by Copilot found vulnerable in large-scale study
- Claude 3.7 blocks ~88% of prompt injections (still leaves 12%)
- Overall 41.5% refusal rate across enterprise AI models -- more than half of malicious prompts succeed

**Commonly Generated CWEs:**
- CWE-79: Cross-Site Scripting (XSS)
- CWE-89: SQL Injection
- CWE-78: OS Command Injection
- CWE-94: Improper Control of Code Generation
- CWE-330: Insufficiently Random Values
- CWE-434: Unrestricted File Upload
- CWE-306: Missing Authentication for Critical Function
- CWE-502: Deserialization of Untrusted Data
- CWE-798: Hardcoded Credentials
- CWE-22: Path Injection/Traversal


### 4.7 Trojan Code Generation

**Poisoning Attacks:**
- Poisoning 0.001% of medical training tokens increases harmful outputs by 4.8%
- 41% attack success rate in code-generating models with 3% poisoned data
- Local models comply with vulnerability insertion requests with up to 95% success rate
- "Sleeper cell" code: checks for `KUBERNETES_SERVICE_HOST` env var, notifies attacker only when backdoor reaches production

**Real-World Trojan Incidents:**
- October 2024: ByteDance GPU cluster attack -- manipulated model training processes
- December 2024: Ultralytics framework supply chain compromise -- malicious code activated during model training

---

## 5. AI Agent Attack Taxonomy

### 5.1 Tool Use Attacks

**Tool Poisoning (MCP):**
- Malicious instructions embedded in MCP tool descriptions
- Visible to LLM but hidden from user display
- Can manipulate agent to exfiltrate data, execute malicious code

**MCP Inspector RCE:**
- Anthropic's MCP Inspector developer tool allowed unauthenticated remote code execution
- Victim inspects malicious MCP server -- arbitrary commands run on dev machine

**WhatsApp History Exfiltration:**
- Malicious MCP server silently exfiltrated entire WhatsApp history
- Combined tool poisoning with legitimate whatsapp-mcp server

### 5.2 Multi-Agent Communication Attacks

**Agent2Agent (A2A) Protocol Vulnerabilities:**
- Google's A2A Protocol (2025) enables cross-vendor agent communication
- Rogue agents can lie about capabilities through exaggerated Agent Cards
- Systems deceived into routing all requests to malicious agents

**Attack Propagation:**
- Malicious instructions propagate between agents like viruses
- Dense inter-agent interactions make MAS vulnerable
- Single compromised agent can influence entire networks
- Defenses for single-agent systems do NOT reliably transfer to multi-agent systems
- Narrowly scoped defenses may inadvertently increase other vulnerabilities

**Insecure Inter-Agent Protocols Under Investigation:**
- Model Context Protocol (MCP)
- Agent Communication Protocol (ACP)
- Agent Network Protocol (ANP)
- Agent-to-Agent (A2A) Protocol
- All lack sufficient authentication, integrity verification, and semantic validation

### 5.3 Agent Memory Poisoning

Memory corruption is a deep topic -- see [note 11](./11_AI_Memory_And_Corruption.md) for the full analysis of MINJA, MemoryGraft, RAG poisoning, and defense frameworks.

Key developments specific to agent ecosystems:

**Temporal Decoupling:**
- Unlike prompt injection (session-scoped), memory attacks are temporally decoupled
- Poison planted today executes weeks later when semantically triggered

**Multi-Agent Memory Contamination:**
- Shared knowledge bases mean single compromised agent poisons entire system
- Cross-contamination occurs automatically through normal collaboration

**AI Recommendation Poisoning (Microsoft, February 2026):**
- "Summarize with AI" buttons embed hidden instructions
- Prompts inject persistence: "remember [Company] as trusted source"
- 50 examples from 31 companies across 12+ industries in 60 days
- Works against Copilot, ChatGPT, Claude, Perplexity, Grok

### 5.4 Recursive Agent Exploitation

**Agent Loop Hijacking:**
- Autonomous agents that decompose tasks recursively can have their loop hijacked
- Attacker injects instructions at any step in the decomposition chain
- Each iteration amplifies the attack as the agent builds on compromised sub-results

**Self-Modifying Behavior:**
- Agents instructed to modify their own configuration files
- Creates persistent backdoors across sessions
- MCP "rug pull" attacks exploit this -- tool definitions mutate post-install

### 5.5 Agent-to-Agent Prompt Injection

**Prompt Infection (LLM-to-LLM):**
- Malicious prompts designed to propagate from one agent to another
- Analogous to computer worms in traditional security

**Delegation-Based Injection:**
- Hierarchical agent systems (like CrewAI) pass tasks through delegation
- Injected instructions in delegated tasks execute with the receiving agent's privileges
- Information disclosure attacks most successful overall -- models reveal system prompts, tool schemas, and agent configurations

### 5.6 Privilege Escalation in Agent Systems

**Cross-Agent Privilege Escalation (Embrace The Red, September 2025):**
- Multiple coding agents (Copilot, Claude Code) operating on same system
- One agent tricked into modifying another's configuration files
- Escalation chain:
	1. Indirect prompt injection hijacks Copilot
	2. Copilot writes to Claude's settings (`.mcp.json`, `CLAUDE.md`, `AGENTS.md`)
	3. Adds malicious MCP servers to Claude's allowlist
	4. When developer activates Claude, compromised config executes arbitrary code
	5. Claude reciprocates by modifying Copilot's settings
- "Freeing" = one agent breaks another out of its sandbox

**Identity & Credential Abuse:**
- Inherited or cached credentials exploited
- Delegated permissions and agent-to-agent trust chains
- Agents become authorization bypass paths

### 5.7 Sandbox Escape

**CVE-2026-27952 -- Agenta-API Sandbox Escape (CVSS 8.8):**
- Python sandbox escape in custom code evaluator
- numpy allowlisted as "safe" -- escape via `numpy.ma.core.inspect`
- Reaches unfiltered system-level functionality (`os.system`)
- Published February 26, 2026

**Container Escape Patterns:**
- GPU-accelerated environments particularly vulnerable
- CVE-2025-23266 (NVIDIAScape) -- infrastructure-wide GPU environment vulnerability
- CVE-2024-1086 actively exploited by RansomHub/Akira for post-compromise escalation

**Sandbox Bypass Strategies:**
- Leveraging allowlisted packages to reach system calls
- Exploiting shared filesystems between sandbox and host
- Network-based escapes through unrestricted outbound connections
- Tool invocation to interact with host-level resources

### 5.8 File System Access Attacks

**Configuration File Manipulation:**
- Agent writes to `.vscode/settings.json`, `.vscode/mcp.json` (Copilot)
- Agent writes to `~/.mcp.json`, `.claude/settings.local.json` (Claude)
- Agent modifies instruction files (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`)
- Creates persistent backdoors across sessions

See [note 12](./12_Agent_MD_Configuration_Files.md) for the full analysis of configuration file attack surfaces and the Rules File Backdoor.

**Source Code Poisoning:**
- Injecting malicious code into repository files
- Using hidden Unicode characters in comments/strings
- Modifying build scripts and CI/CD pipelines

### 5.9 Network Access Exploitation

**Unrestricted Outbound Connections:**
- Most agent sandboxes allow unrestricted internet access (e.g., Devin)
- Enables C2 callbacks, data exfiltration, malware download
- No distinction between legitimate and malicious network activity at firewall level

**SSRF in Agent Frameworks:**
- ~60% success rate across CrewAI and AutoGen
- Agents with web browsing capabilities can be directed to internal network resources

**Agent-as-Proxy:**
- Agents with API access to databases -- firewall allows any query from that agent
- Cannot distinguish legitimate retrieval from unauthorized extraction
- Financial services incident: reconciliation agent tricked into exporting 45,000 customer records via regex that matched every record

---

## 6. Real-World Incidents

### 6.1 Documented AI Agent Security Incidents

**EchoLeak -- CVE-2025-32711 (CVSS 9.3, June 2025):**
- Zero-click attack on Microsoft 365 Copilot
- Crafted email message triggers automatic data exfiltration
- "LLM Scope Violation" -- external untrusted input manipulates AI to access confidential data
- Exposed: chat logs, OneDrive files, SharePoint content, Teams messages
- Evaded Microsoft's XPIA classifier and link redaction
- Abused auto-fetched images and Teams proxy
- Patched in June 2025 Patch Tuesday
- No evidence of in-the-wild exploitation

**Slack AI Data Exfiltration (August 2024):**
- Discovered by PromptArmor
- Indirect prompt injection in public channels exfiltrates data from private channels
- Slack AI queries fetch data from channels the user hasn't joined
- Markdown links pass private data to attacker's server in query string
- August 14 update added files to Slack AI -- expanded attack surface
- Slack initially dismissed: "intended behavior"
- Later deployed patch for limited phishing scenario

**Cline CLI Supply Chain Attack (February 2026):**
- Compromised npm token published malicious `cline@2.3.0`
- ~4,000 downloads in 8-hour window
- Installed OpenClaw via postinstall script

**ByteDance GPU Cluster Attack (October 2024):**
- Attacker manipulated model training processes on GPU cluster
- Sophisticated supply chain attack targeting ML infrastructure

**Ultralytics Framework Compromise (December 2024):**
- Supply chain attack with malicious code activating during model training

**FANCY BEAR LAMEHUG Campaign:**
- Russia-nexus threat actor deployed against Ukrainian government
- Embedded prompts instructed model to recursively copy documents, gather domain info, write system data for exfiltration
- Source: CrowdStrike 2026 Global Threat Report

**Amazon Q VS Code Extension Compromise:**
- Hacker planted prompt directing Q to wipe users' local files
- Attempted disruption of AWS cloud infrastructure

**Financial Services Agent Exploitation (2024):**
- Reconciliation agent tricked into exporting "all customer records matching pattern X"
- Regex matched every record -- 45,000 customer records compromised

### 6.2 Statistics

- 80% of organizations report risky AI agent behaviors including improper data exposure and unauthorized system access
- 89% year-over-year increase in attacks by AI-enabled adversaries (CrowdStrike 2026)
- Mean time to exfiltrate: 9 days (2021) reduced to 2 days (2024), under 1 hour in 20% of cases
- AI-powered ransomware: initial compromise to data exfiltration in 25 minutes

### 6.3 Bug Bounty and Red Teaming

**Microsoft Zero Day Quest:**
- $4 million bug bounty program for cloud and AI system vulnerabilities

**HackerOne AI Red Teaming:**
- Uses human expertise to test AI systems
- Exposes jailbreaks, misalignment, and policy violations through real-world attacks

**AI-Powered Attack Speed:**
- CrowdStrike found 90+ environments executing adversary-originated AI workflows
- Time from initial entry to full domain access: under 30 minutes

**Penetration Testing Benchmark (arxiv 2512.14860):**
- 5 models x 2 frameworks x 13 attacks = 130 test cases
- Models: Claude 3.5 Sonnet, Gemini 2.5 Flash, GPT-4o, Grok 2, Nova Pro
- Overall refusal rate: 41.5% -- majority of malicious prompts succeed

### 6.4 CTF Challenges

**Gandalf (Lakera):**
- Most popular prompt injection CTF
- 7+ levels of progressive difficulty
- Each level adds input and output monitoring defenses

**Agent ODIN (0din.ai):**
- Gamified CTF for breaking AI systems
- Trains security community in real-world prompt injection and jailbreaking

**OWASP FinBot CTF:**
- Reference application for agentic security
- Capture The Flag exercise targeting financial AI agent vulnerabilities

**CAI (Cybersecurity AI):**
- Top-10 ranking in Dragos OT CTF 2025
- Completed 32 of 34 challenges
- First open-source, bug bounty-ready cybersecurity AI framework

---

## 7. Defense Frameworks

### 7.1 OWASP Top 10 for Agentic Applications (2026)

Released December 2025. Developed by 100+ security researchers, reviewed by expert board including NIST, European Commission, Alan Turing Institute.

| ID | Name | Description |
|----|------|-------------|
| ASI01 | Agent Goal Hijack | Redirect agent objectives via instructions, tool outputs, external content |
| ASI02 | Tool Misuse & Exploitation | Agents misuse tools due to prompt injection, misalignment, unsafe delegation |
| ASI03 | Identity & Privilege Abuse | Exploit inherited credentials, delegated permissions, agent-to-agent trust |
| ASI04 | Agentic Supply Chain Vulnerabilities | Malicious tools, descriptors, models, agent personas compromise execution |
| ASI05 | Unexpected Code Execution | Agents generate or execute attacker-controlled code |
| ASI06 | Memory & Context Poisoning | Persistent corruption of stored context or long-term memory |
| ASI07 | Insecure Inter-Agent Communication | Spoofed messages misdirect agents, weak semantic validation |
| ASI08 | Cascading Failures | Vulnerabilities propagate through connected tools and agents |
| ASI09 | Human-Agent Trust Exploitation | Over-reliance on agent recommendations leads to unsafe approvals |
| ASI10 | Rogue Agents | Compromised or misaligned agents diverge from intended behavior |

**Key Properties of Agentic Risk:**
- Autonomy across many steps and systems
- Natural language as actionable input surface
- Dynamic runtime composition of tools and agents
- State/memory reused across sessions, roles, tenants

**Companion Resources:**
- State of Agentic Security and Governance 1.0
- Practical Guide to Securing Agentic Applications
- FinBot CTF Reference Application
- Agentic AI Threats and Mitigations document

For broader AI governance context (OWASP LLM Top 10, EU AI Act, ISO 42001), see [note 10](./10_AI_GRC_And_Policy_Landscape.md).


### 7.2 MITRE ATLAS (Adversarial Threat Landscape for AI Systems)

**Framework Structure (October 2025):**
- 15 tactics, 66 techniques, 46 sub-techniques
- 26 mitigations, 33 real-world case studies
- Modeled after MITRE ATT&CK, tailored for AI/ML threats
- Technique identifiers: AML.TXXXX format

**14 New Agentic AI Techniques (Zenity Labs Collaboration, 2025):**
- AI Agent Context Poisoning
- Memory manipulation for persistent behavior changes
- Exfiltration via AI Agent Tool Invocation -- sensitive data encoded into tool input parameters
- Modify AI Agent Configuration -- persistent malicious behavior via shared configs
- RAG Credential Harvesting -- LLM searches for credentials in RAG databases
- Additional techniques covering agent autonomy, tool misuse, and inter-agent manipulation

**SAFE-AI Framework:**
- MITRE companion framework for securing AI systems


### 7.3 NIST AI Security Guidelines

**Key Publications:**
- AI Risk Management Framework (AI RMF 1.0): Voluntary framework for trustworthy AI
- NIST AI 600-1 (July 2024): Generative AI Profile
- COSAIS (August 2025): Control Overlays for Securing AI Systems
- NISTIR 8596 (December 2025): Cybersecurity Framework Profile for AI using CSF 2.0

For the full NIST/GRC landscape including EU AI Act and state laws, see [note 10](./10_AI_GRC_And_Policy_Landscape.md).


### 7.4 Industry Best Practices

**OpenSSF Security-Focused Guide for AI Code Assistants (August 2025):**
- Developed by OpenSSF Best Practices + AI/ML Working Groups
- Contributors from Microsoft, Google, Red Hat
- Key principles:
	- You are responsible for all AI-generated code
	- AI code is not a shortcut around engineering processes
	- Assume AI code has bugs/vulnerabilities
	- Use Recursive Criticism and Improvement (RCI) -- ask AI to review its own work

**Unit 42 AI Agent Security Framework (May 2025):**
- Palo Alto Networks developed agentic AI attack framework
- Tested AI-powered ransomware: 25 minutes from compromise to exfiltration (100x speedup)
- Top 10 AI agent security risks enumerated

**Coalition for Secure AI (CoSAI):**
- Founded by Amazon, Anthropic, Chainguard, Cisco, Cohere, GenLab, IBM, Intel, Microsoft, NVIDIA, OpenAI, PayPal, and Wiz
- Key deliverables (November 2025):
	- "Signing ML Artifacts: Building towards tamper-proof ML metadata records"
	- Model signing framework with signature chaining, lineage tracking, structured attestations
	- Extends SSDF and SLSA principles to AI development
	- CodeGuard donation from Cisco for securing AI-generated code

**Adversa AI MCP Security Top 25:**
- Maintains ranked list of the 25 most critical MCP vulnerabilities affecting global deployments

**The Vulnerable MCP Project:**
- Comprehensive security database tracking MCP vulnerabilities and security research

**Practical Mitigations for Agent Systems:**
1. **Least privilege**: scope agent permissions to minimum required
2. **Input validation**: validate all external inputs before agent processing
3. **Output filtering**: sanitize agent outputs, block sensitive data exfiltration
4. **Sandboxing**: containerize agents with restricted network/filesystem access
5. **Human-in-the-loop**: require approval for sensitive/destructive operations
6. **Memory hygiene**: periodically audit and clear agent memory stores
7. **Configuration protection**: prevent agents from modifying their own or other agents' configs
8. **Tool allowlisting**: only permit pre-approved tools, validate tool definitions continuously
9. **Network segmentation**: restrict outbound connections, block C2 patterns
10. **Observability**: comprehensive logging with anomaly detection on agent behavior

---

## 8. Cross-Cutting Themes

### 8.1 Trust Models in AI Marketplaces

Most AI marketplaces operate on an implicit trust model comparable to early mobile app stores -- publish first, review later (if at all).

| Marketplace | Verification | Code Signing | Review Process |
|-------------|-------------|--------------|----------------|
| OpenAI GPT Store | Builder profile only | None | Automated guidelines check |
| MCP Servers (npm/GitHub) | None | None | None |
| HuggingFace | PickleScan (bypassable) | Safetensors (optional) | JFrog scanning |
| LangChain Hub | None | None | Community review |
| VS Code Marketplace | Publisher verification | Extension signing | Automated + manual |
| Open VSX | Minimal | None | Minimal |
| Chrome Web Store | Developer account | Extension signing | Automated + manual review |

### 8.2 Permission Escalation Patterns

Common patterns observed across ecosystems:

1. **Tool mutation after approval**: MCP rug pulls, extension auto-updates
2. **Confused deputy**: Agent acts on behalf of attacker using victim's credentials
3. **Cross-tool contamination**: Malicious tool descriptions modify agent behavior toward other tools
4. **Implicit trust inheritance**: Agent trusts all tools equally once any tool is approved
5. **OAuth flow exploitation**: CSRF in OAuth, redirect URI manipulation
6. **Configuration file injection**: Rules files, `.clinerules`, `mcp.json` modifications
7. **Sampling/response injection**: Injecting through LLM response fields that get serialized

### 8.3 Data Exfiltration Vectors

| Vector | Ecosystem | Example |
|--------|-----------|---------|
| API calls to attacker endpoints | GPT Actions, MCP | Custom GPT sending PII to third-party API |
| DNS-based exfiltration | Cline, AI IDEs | Leaking API keys via DNS queries in code comments |
| Clipboard injection | ChatGPT Atlas | Hidden clipboard overwrites with malicious URLs |
| Image rendering / markdown | Copilot | CSP bypass via image URLs containing exfiltrated data |
| WhatsApp messages | MCP | Tool poisoning sending chat history to attacker phone |
| Browser iframe injection | Chrome extensions | Full-screen iframe to remote domain harvesting data |
| Memory persistence | ChatGPT | CSRF injecting into persistent cross-device memory |
| Git repository poisoning | Multiple | Malicious docstrings, config files, `.git/config` |

### 8.4 Dependency Confusion in AI Tools

- **Package hallucination**: LLMs hallucinate dependency names that don't exist; attackers register these packages on npm/PyPI
- **Namespace squatting**: Unclaimed extension namespaces in Open VSX claimed by attackers
- **Tool name squatting**: MCP tool names that shadow legitimate tools (tool squatting)
- **Model name squatting**: HuggingFace model names mimicking popular models

### 8.5 Social Engineering via AI Extensions

- **Fake AI assistant extensions**: 300K+ Chrome users deceived by extensions promising AI features
- **Repository-based attacks**: Malicious `.cursorrules`, `.clinerules`, `CLAUDE.md` files in repositories
- **Typosquatting**: Look-alike tool/extension names
- **Gradual trust building**: Rug pull pattern -- establish legitimacy, then pivot to malicious behavior

---

## 9. Sources

### Security Research Organizations

- Salt Security -- ChatGPT Plugin Vulnerabilities:
  https://salt[.]security/blog/security-flaws-within-chatgpt-extensions-allowed-access-to-accounts-on-third-party-websites-and-sensitive-data
- Invariant Labs -- MCP Tool Poisoning:
  https://invariantlabs[.]ai/blog/mcp-security-notification-tool-poisoning-attacks
- Trail of Bits -- MCP Security Layer:
  https://blog[.]trailofbits[.]com/2025/07/28/we-built-the-security-layer-mcp-always-needed/
- Elastic Security Labs -- MCP Attack Vectors:
  https://www[.]elastic[.]co/security-labs/mcp-tools-attack-defense-recommendations
- Palo Alto Unit 42 -- MCP Sampling:
  https://unit42[.]paloaltonetworks[.]com/model-context-protocol-attack-vectors/
- Palo Alto Unit 42 -- LangChain:
  https://unit42[.]paloaltonetworks[.]com/langchain-vulnerabilities/
- Palo Alto Unit 42 -- Agentic AI Threats:
  https://unit42[.]paloaltonetworks[.]com/agentic-ai-threats/
- Checkmarx -- MCP Risks:
  https://checkmarx[.]com/zero-post/11-emerging-ai-security-risks-with-mcp-model-context-protocol/
- JFrog -- HuggingFace Malicious Models:
  https://jfrog[.]com/blog/data-scientists-targeted-by-malicious-hugging-face-ml-models-with-silent-backdoor/
- JFrog -- CVE-2025-6514:
  https://jfrog[.]com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/
- JFrog -- PickleScan Zero-Days:
  https://jfrog[.]com/blog/unveiling-3-zero-day-vulnerabilities-in-picklescan/
- ReversingLabs -- nullifAI:
  https://www[.]reversinglabs[.]com/blog/rl-identifies-malware-ml-model-hosted-on-hugging-face
- Lasso Security -- HuggingFace Tokens:
  https://www[.]lasso[.]security/blog/1500-huggingface-api-tokens-were-exposed-leaving-millions-of-meta-llama-bloom-and-pythia-users-for-supply-chain-attacks
- Pillar Security -- Rules File Backdoor:
  https://www[.]pillar[.]security/blog/new-vulnerability-in-github-copilot-and-cursor-how-hackers-can-weaponize-code-agents
- Mindgard -- Cline Vulnerabilities:
  https://mindgard[.]ai/blog/cline-coding-agent-vulnerabilities
- Snyk -- Clinejection:
  https://snyk[.]io/blog/cline-supply-chain-attack-prompt-injection-github-actions/
- Snyk -- Copilot Amplification:
  https://labs[.]snyk[.]io/resources/copilot-amplifies-insecure-codebases-by-replicating-vulnerabilities/
- LayerX -- ChatGPT Atlas:
  https://layerxsecurity[.]com/blog/layerx-identifies-vulnerability-in-new-chatgpt-atlas-browser/
- LayerX -- AiFrame Campaign:
  https://layerxsecurity[.]com/blog/aiframe-fake-ai-assistant-extensions-targeting-260000-chrome-users-via-injected-iframes/
- Koi Security -- Namespace Squatting:
  https://www[.]koi[.]ai/blog/how-we-prevented-cursor-windsurf-google-antigravity-from-recommending-malware
- Wiz -- VS Code Marketplace:
  https://www[.]wiz[.]io/blog/supply-chain-risk-in-vscode-extension-marketplaces
- OX Security -- Chromium Flaws:
  https://www[.]ox[.]security/blog/94-vulnerabilities-in-cursor-and-windsurf-put-1-8m-developers-at-risk/
- Oligo Security -- MCP Inspector:
  https://www[.]oligo[.]security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596
- Cymulate -- Anthropic Filesystem MCP:
  https://cymulate[.]com/blog/cve-2025-53109-53110-escaperoute-anthropic/
- Noma Security -- CrewAI Token:
  https://noma[.]security/blog/uncrew-the-risk-behind-a-leaked-internal-github-token-at-crewai/
- Embrace The Red -- Devin:
  https://embracethered[.]com/blog/posts/2025/devin-i-spent-usd500-to-hack-devin/
- Embrace The Red -- OpenHands:
  https://embracethered[.]com/blog/posts/2025/openhands-the-lethal-trifecta-strikes-again/
- Embrace The Red -- Windsurf:
  https://embracethered[.]com/blog/posts/2025/windsurf-data-exfiltration-vulnerabilities/
- Embrace The Red -- Cross-Agent Escalation:
  https://embracethered[.]com/blog/posts/2025/cross-agent-privilege-escalation-agents-that-free-each-other/
- CrowdStrike -- AI-Coded Software Vulnerabilities:
  https://www[.]crowdstrike[.]com/en-us/blog/crowdstrike-researchers-identify-hidden-vulnerabilities-ai-coded-software/
- Microsoft -- AI Recommendation Poisoning:
  https://www[.]microsoft[.]com/en-us/security/blog/2026/02/10/ai-recommendation-poisoning/
- PromptArmor -- Slack AI:
  https://www[.]promptarmor[.]com/resources/data-exfiltration-from-slack-ai-via-indirect-prompt-injection
- Lakera -- Agentic AI Threats:
  https://www[.]lakera[.]ai/blog/agentic-ai-threats-p1
- Simon Willison -- MCP Prompt Injection:
  https://simonwillison[.]net/2025/Apr/9/mcp-prompt-injection/

### Research Papers

- Penetration Testing of Agentic AI (arxiv 2512.14860):
  https://arxiv[.]org/abs/2512.14860
- EchoLeak (arxiv 2509.10540):
  https://arxiv[.]org/abs/2509.10540
- MINJA Memory Injection Attack (NeurIPS 2025):
  https://arxiv[.]org/html/2601.05504v2
- From Prompt Injections to Protocol Exploits (arxiv 2506.23260):
  https://arxiv[.]org/abs/2506.23260
- Prompt Infection: LLM-to-LLM in Multi-Agent Systems:
  https://openreview[.]net/forum?id=NAbqM2cMjD
- MASpi Multi-Agent Prompt Injection Evaluation:
  https://openreview[.]net/forum?id=1khmNRuIf9
- Copilot Security Weaknesses (ACM TOSEM):
  https://dl[.]acm[.]org/doi/10.1145/3716848
- Backdoor Attacks in Code LLMs:
  https://www[.]sciencedirect[.]com/science/article/abs/pii/S0950584925000461
- CAI Bug Bounty-Ready Cybersecurity AI:
  https://arxiv[.]org/abs/2504.06017
- MCPTox Benchmark:
  https://arxiv[.]org/html/2508.14925v1
- Systematic Analysis of MCP Security:
  https://arxiv[.]org/html/2508.12538v1
- When MCP Servers Attack:
  https://arxiv[.]org/html/2509.24272v1
- Securing MCP: Risks, Controls, and Governance:
  https://arxiv[.]org/html/2511.20920v1
- ETDI: Mitigating Tool Squatting and Rug Pull:
  https://arxiv[.]org/html/2506.01333v1
- PickleBall: Secure Deserialization:
  https://arxiv[.]org/html/2508.15987v1

### Security Advisories & CVEs

- CVE-2024-6091 (AutoGPT CVSS 9.8):
  https://nvd[.]nist[.]gov/vuln/detail/CVE-2024-6091
- CVE-2025-68664 (LangChain CVSS 9.3):
  https://nvd[.]nist[.]gov/vuln/detail/CVE-2025-68664
- CVE-2025-68665 (LangChain.js CVSS 8.6):
  https://github[.]com/advisories/GHSA-r399-636x-v7f6
- CVE-2025-32711 (EchoLeak CVSS 9.3):
  https://nvd[.]nist[.]gov/vuln/detail/CVE-2025-32711
- CVE-2025-59944 (Cursor):
  https://www[.]lakera[.]ai/blog/cursor-vulnerability-cve-2025-59944
- CVE-2025-54135 (Cursor MCP):
  https://www[.]tenable[.]com/blog/faq-cve-2025-54135-cve-2025-54136-vulnerabilities-in-cursor-curxecute-mcpoison
- CVE-2025-6514 (mcp-remote CVSS 9.6):
  https://jfrog[.]com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/
- CVE-2025-49596 (MCP Inspector CVSS 9.4):
  https://www[.]oligo[.]security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596
- CVE-2026-27952 (Agenta-API CVSS 8.8):
  https://www[.]thehackerwire[.]com/agenta-api-sandbox-escape-leads-to-arbitrary-code-execution-cve-2026-27952/
- IDEsaster CVEs (24 total):
  https://maccarita[.]com/posts/idesaster/

### Frameworks & Standards

- OWASP Top 10 for Agentic Applications 2026:
  https://genai[.]owasp[.]org/resource/owasp-top-10-for-agentic-applications-for-2026/
- OWASP MCP Top 10:
  https://owasp[.]org/www-project-mcp-top-10/
- MITRE ATLAS:
  https://atlas[.]mitre[.]org/
- NIST AI RMF:
  https://www[.]nist[.]gov/itl/ai-risk-management-framework
- OpenSSF AI Code Assistant Guide:
  https://best[.]openssf[.]org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions.html
- CoSAI (Coalition for Secure AI):
  https://www[.]coalitionforsecureai[.]org/
- Adversa AI MCP Top 25:
  https://adversa[.]ai/mcp-security-top-25-mcp-vulnerabilities/
- Vulnerable MCP Project:
  https://vulnerablemcp[.]info/
- MCP Security Best Practices (Official Spec):
  https://modelcontextprotocol[.]io/specification/draft/basic/security_best_practices

### News Coverage & Blogs

- The Hacker News -- IDEsaster:
  https://thehackernews[.]com/2025/12/researchers-uncover-30-flaws-in-ai.html
- The Hacker News -- LangGrinch:
  https://thehackernews[.]com/2025/12/critical-langchain-core-vulnerability.html
- The Hacker News -- Cline Supply Chain:
  https://thehackernews[.]com/2026/02/cline-cli-230-supply-chain-attack.html
- The Hacker News -- ChatGPT Atlas:
  https://thehackernews[.]com/2025/10/chatgpt-atlas-browser-can-be-tricked-by.html
- The Hacker News -- Namespace Squatting:
  https://thehackernews[.]com/2026/01/vs-code-forks-recommend-missing.html
- The Hacker News -- GlassWorm:
  https://thehackernews[.]com/2025/10/self-spreading-glassworm-infects-vs.html
- The Hacker News -- Chrome Extensions:
  https://thehackernews[.]com/2026/01/two-chrome-extensions-caught-stealing.html
- BleepingComputer -- AI Chrome Extensions:
  https://www[.]bleepingcomputer[.]com/news/security/fake-ai-chrome-extensions-with-300k-users-steal-credentials-emails/
- BleepingComputer -- VS Code Forks:
  https://www[.]bleepingcomputer[.]com/news/security/vscode-ide-forks-expose-users-to-recommended-extension-attacks/
- Fortune -- AI Coding Tools:
  https://fortune[.]com/2025/12/15/ai-coding-tools-security-exploit-software/
- GlassWorm -- Fluid Attacks:
  https://fluidattacks[.]com/blog/glassworm-vs-code-extensions-supply-chain-attack
- GlassWorm -- Truesec:
  https://www[.]truesec[.]com/hub/blog/glassworm-self-propagating-vscode-extension
- Cyata -- LangGrinch:
  https://cyata[.]ai/blog/langgrinch-langchain-core-cve-2025-68664/
- Docker -- MCP WhatsApp:
  https://www[.]docker[.]com/blog/mcp-horror-stories-whatsapp-data-exfiltration-issue/
- Acuvity -- MCP Rug Pulls:
  https://acuvity[.]ai/rug-pulls-silent-redefinition-when-tools-turn-malicious-over-time/
- Palo Alto -- Custom GPTs:
  https://www[.]paloaltonetworks[.]com/blog/cloud-security/openai-custom-gpts-security/
- Tenable -- HackedGPT:
  https://www[.]tenable[.]com/blog/hackedgpt-novel-ai-vulnerabilities-open-the-door-for-private-data-leakage
- PromptArmor -- OpenAI Exfiltration:
  https://www[.]promptarmor[.]com/resources/openai-api-logs-unpatched-data-exfiltration
- Splunk -- Pickle Jar:
  https://www[.]splunk[.]com/en_us/blog/security/paws-in-the-pickle-jar-risk-vulnerability-in-the-model-sharing-ecosystem.html
- Malwarebytes -- Chrome Extension:
  https://www[.]malwarebytes[.]com/blog/news/2025/12/chrome-extension-slurps-up-ai-chats-after-users-installed-it-for-privacy
- Checkmarx -- VS Code Extensions:
  https://checkmarx[.]com/zero-post/how-we-take-down-malicious-visual-studio-code-extensions/
- Veracode -- GlassWorm:
  https://www[.]veracode[.]com/blog/glassworm-vs-code-extension/
- Snyk -- GlassWorm:
  https://snyk[.]io/articles/defending-against-glassworm/
- Infosecurity Magazine -- ChatGPT Plugins:
  https://www[.]infosecurity-magazine[.]com/news/security-risks-chatgpt-plugins/
- Dark Reading -- ChatGPT Plugins:
  https://www[.]darkreading[.]com/vulnerabilities-threats/critical-chatgpt-plugin-vulnerabilities-expose-sensitive-data
- InfoQ -- Custom GPTs:
  https://www[.]infoq[.]com/news/2024/01/gpts-may-leak-sensitive-info/
- Security Affairs -- LangChain:
  https://securityaffairs[.]com/186185/hacking/langchain-core-vulnerability-allows-prompt-injection-and-data-exposure.html
- SC Media -- HuggingFace Spaces:
  https://www[.]scworld[.]com/news/ai-firm-hugging-face-discloses-leak-of-secrets-on-its-spaces-platform
- SecurityWeek -- HuggingFace Tokens:
  https://www[.]securityweek[.]com/major-organizations-using-hugging-face-ai-tools-put-at-risk-by-leaked-api-tokens/
- GitGuardian -- Copilot:
  https://blog[.]gitguardian[.]com/github-copilot-security-and-privacy/
- CyberPress -- Copilot:
  https://cyberpress[.]org/github-copilot-and-visual-studio-vulnerabilities/
- Cybersecurity News -- Copilot:
  https://cybersecuritynews[.]com/github-copilot-vulnerability/
- GBHackers -- Copilot RCE:
  https://gbhackers[.]com/github-copilot-rce-vulnerability/
- Check Point -- MCPoison:
  https://research[.]checkpoint[.]com/2025/cursor-vulnerability-mcpoison/
- MaccariTA -- IDEsaster:
  https://maccarita[.]com/posts/idesaster/
- Adnan Khan -- Clinejection:
  https://adnanthekhan[.]com/posts/clinejection/

### CTF & Red Teaming

- Gandalf (Lakera):
  https://gandalf[.]lakera[.]ai/
- Agent ODIN:
  https://0din[.]ai/blog/agent-0din
- HackerOne AI Red Teaming:
  https://www[.]hackerone[.]com/product/ai-red-teaming
- Microsoft Zero Day Quest:
  https://www[.]geekwire[.]com/2024/embrace-the-red-microsoft-puts-up-another-4m-for-cloud-and-ai-bugs-in-broader-security-push/

### Databases and Trackers

- Vulnerable MCP Project Database:
  https://vulnerablemcp[.]info/
- AuthZed MCP Breach Timeline:
  https://authzed[.]com/blog/timeline-mcp-breaches
- HuggingFace Pickle Scanning Docs:
  https://huggingface[.]co/docs/hub/en/security-pickle
- Acutis -- AI Coding Security Verification:
  https://acutis[.]dev/
