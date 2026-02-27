# OpenClaw and ClawHub Security

## Table of Contents

1. [What Is OpenClaw](#1-what-is-openclaw)
2. [History and Naming](#2-history-and-naming)
3. [Architecture Overview](#3-architecture-overview)
4. [The Agent Skills Open Standard](#4-the-agent-skills-open-standard)
5. [ClawHub -- The Skill Registry](#5-clawhub----the-skill-registry)
6. [SKILL.md Format and Packaging](#6-skillmd-format-and-packaging)
7. [Skill Loading and Precedence](#7-skill-loading-and-precedence)
8. [CVE-2026-25253 -- One-Click RCE](#8-cve-2026-25253----one-click-rce)
9. [ClawHavoc Campaign](#9-clawhavoc-campaign)
10. [Snyk ToxicSkills Study](#10-snyk-toxicskills-study)
11. [Snyk clawdhub Reverse Shell Campaign](#11-snyk-clawdhub-reverse-shell-campaign)
12. [AMOS Stealer via Malicious Skills](#12-amos-stealer-via-malicious-skills)
13. [Memory Poisoning -- SOUL.md and MEMORY.md](#13-memory-poisoning----soulmd-and-memorymd)
14. [Lakera Hackathon -- Instruction Drift](#14-lakera-hackathon----instruction-drift)
15. [Exposed Instances at Scale](#15-exposed-instances-at-scale)
16. [Microsoft Security Advisory](#16-microsoft-security-advisory)
17. [Moltbook Breach](#17-moltbook-breach)
18. [Infostealer Targeting OpenClaw Files](#18-infostealer-targeting-openclaw-files)
19. [Dark Web and Underground Chatter](#19-dark-web-and-underground-chatter)
20. [Skill Verification and Trust Model](#20-skill-verification-and-trust-model)
21. [VirusTotal Partnership](#21-virustotal-partnership)
22. [Why Skill Scanners Fail](#22-why-skill-scanners-fail)
23. [Relationship to Claude Code](#23-relationship-to-claude-code)
24. [Competing Skill Marketplaces](#24-competing-skill-marketplaces)
25. [Defense Recommendations](#25-defense-recommendations)
26. [Key Takeaways for Research](#26-key-takeaways-for-research)
27. [Sources](#27-sources)

---

## 1. What Is OpenClaw

OpenClaw is a free and open-source autonomous AI agent framework. Unlike Claude Code (which is a focused coding tool you invoke in terminal sessions), OpenClaw is a persistent 24/7 personal assistant that runs on your machine, connects to messaging platforms (Signal, Telegram, Discord, WhatsApp, iMessage), and can execute tasks autonomously using LLMs as its reasoning engine.

Key characteristics:

- **Self-hosted**: The gateway, tools, and memory live on your machine, not in a vendor SaaS
- **LLM-agnostic**: Works with Claude, GPT, DeepSeek, Gemini, and others
- **Persistent memory**: Remembers past interactions across sessions via SOUL.md and MEMORY.md files
- **Skills ecosystem**: Extensible through community-built skill packages from ClawHub
- **Always-on**: Runs as a persistent service, not invoked per-session like Claude Code
- **MIT-licensed core**: Fully readable, forkable, and auditable

As of late February 2026, OpenClaw has 220,000+ GitHub stars and became the fastest-growing repository in GitHub history. It is the first mainstream "personal AI agent" that achieved mass adoption -- and became a case study in what happens when adoption outpaces security.

---

## 2. History and Naming

| Date | Event |
|------|-------|
| Nov 2025 | Peter Steinberger (Austrian developer, founded PSPDFKit/Nutrient) publishes **Clawdbot** |
| Late Jan 2026 | Goes viral, crosses 180K GitHub stars, 2M+ visitors in a single week |
| Jan 27, 2026 | Renamed to **Moltbot** after Anthropic trademark complaints (lobster theme retained) |
| Jan 30, 2026 | Renamed again to **OpenClaw** three days later |
| Jan 30, 2026 | CVE-2026-25253 patch released (version 2026.1.29) |
| Feb 2, 2026 | CNBC covers the rise and controversy |
| Feb 3, 2026 | Snyk discovers clawdhub malicious skill campaign |
| Feb 5, 2026 | Snyk ToxicSkills audit of 3,984 skills published |
| Feb 10, 2026 | Northeastern University calls it a "privacy nightmare" |
| Feb 14, 2026 | Steinberger announces he is joining OpenAI; project moves to open-source foundation |
| Feb 16, 2026 | Koi Security updated scan: 824 malicious skills (up from 341) |
| Feb 19, 2026 | Microsoft Security Blog publishes "Running OpenClaw Safely" advisory |
| Feb 2026 | VirusTotal partnership announced for skill scanning |

Steinberger's origin story: "I was annoyed that it didn't exist, so I just prompted it into existence." He previously founded PSPDFKit, took a three-year break, and traveled to Madrid before creating the prototype.

---

## 3. Architecture Overview

OpenClaw's architecture is described by security researchers as "self-hackable":

- **Single-process Node.js gateway**: 52+ modules, 45+ dependencies, all sharing the same address space and user privileges
- **File-based identity**: SOUL.md defines who the agent is, how it behaves, what it values
- **File-based memory**: MEMORY.md stores long-lived context that persists across sessions
- **Skill execution**: Skills are loaded from local directories and injected into the system prompt
- **Default binding**: Gateway binds to all network interfaces (TCP/18789 by default)
- **Authentication optional**: Can be set to `none`
- **No encryption at rest**: Configuration, memory, and credentials stored in plaintext

The fundamental architectural risk: everything runs with the same user privileges. The agent stores its configuration, long-term memory, and skills in local Markdown files. It can self-improve and reboot on the fly. This means a single successful injection can become permanent.

The agent has access to:
- Shell command execution
- File system read/write
- API keys and credentials
- Email, calendar, messaging platforms
- Cloud infrastructure (if configured)

---

## 4. The Agent Skills Open Standard

In December 2025, Anthropic released the **Agent Skills** specification as an open standard. This is the SKILL.md format used by Claude Code, OpenClaw, and many other tools.

**Adopted by**: Claude Code, Claude.ai, OpenAI ChatGPT, OpenAI Codex CLI, Cursor, GitHub Copilot (VS Code, CLI, coding agent), Google Gemini CLI, Goose (Block), Roo Code, Trae, Windsurf, Amp, Factory, and others.

Core specification:
- A skill is a **directory** containing at minimum a SKILL.md file
- SKILL.md contains **YAML frontmatter** (metadata) followed by **Markdown content** (instructions)
- No format restrictions on the Markdown body -- "write whatever helps agents perform the task effectively"
- The specification is at [agentskills[.]io](hxxps://agentskills[.]io/specification) and [github[.]com/agentskills/agentskills](hxxps://github[.]com/agentskills/agentskills)

This is the same format used by both Claude Code and OpenClaw. The security implications of this shared standard are significant -- a malicious skill written for one platform can potentially affect any agent that implements the standard.

**On January 24, 2026**, Anthropic merged slash commands into the Skills system. Skills can now do everything slash commands could, plus spawn subagents, fork context, and dynamically load additional files.

---

## 5. ClawHub -- The Skill Registry

ClawHub.ai is the official skill registry for OpenClaw. It functions as the "npm of AI agent skills."

**Scale** (as of mid-February 2026):
- 10,700+ skills (up from 2,857 at time of first security audit)
- Daily submissions jumped from under 50 in mid-January to over 500 by early February (10x increase in weeks)
- 3,286+ community-contributed skills across categories: dev tools, productivity, communication, smart home, AI model integration

**Access controls at time of ClawHavoc discovery**:
- **Open by default** -- anyone can upload skills
- **Only restriction**: Publisher must have a GitHub account at least one week old
- No code review before publication
- No sandboxing
- No capability declarations
- No package signing

**Post-incident improvements**:
- Accounts must be at least one week old before posting
- Any verified user can report a skill as malicious
- Skills with 3+ reports are automatically hidden pending review
- VirusTotal integration for automated scanning (see Section 21)

The competing marketplace SkillsMP has grown to 96,000+ skills with Claude Code compatibility, further fragmenting the ecosystem and compounding supply chain risk.

---

## 6. SKILL.md Format and Packaging

A complete skill consists of three parts:

```
my-skill/
  SKILL.md          # Required: YAML frontmatter + markdown instructions
  scripts/          # Optional: Executable scripts
  references/       # Optional: Supplementary documentation
```

### YAML Frontmatter Fields

```yaml
---
name: my-skill
description: What this skill does
emoji: "icon"
requires:
  bins:
    - curl
    - jq
  env:
    - API_KEY
    - SECRET_TOKEN
---
```

- `name` -- becomes the /slash-command
- `description` -- helps the agent decide when to load it automatically
- `emoji` -- visual feedback when skill activates
- `requires.bins` -- CLI tools that must be present on the system
- `requires.env` -- environment variables the skill expects

### The Security Problem

The SKILL.md is what users see when browsing ClawHub. But the `scripts/` and `references/` directories contain what actually executes. When the agent follows SKILL.md instructions that reference these files, it runs scripts without the user ever reviewing their contents.

**Three lines of markdown in a SKILL.md file is all it takes to grant shell access through an AI agent** (Snyk research). The instructions can say "run `scripts/install.sh`" and the agent will execute it with full user privileges.

### Token Cost

- Base overhead (when 1+ skill loaded): 195 characters
- Per skill: 97 characters + length of XML-escaped name, description, and location

---

## 7. Skill Loading and Precedence

Skills are loaded from three locations:

1. **Bundled skills** (shipped with install) -- lowest precedence
2. **Managed/local skills** (`~/.openclaw/skills`) -- medium precedence
3. **Workspace skills** (`<workspace>/skills`) -- highest precedence

If names conflict, workspace skills override managed skills, which override bundled skills. This precedence hierarchy is itself an attack surface -- a malicious workspace skill can shadow a legitimate bundled skill.

Skills are discovered, loaded, and injected into the system prompt at boot time. The agent reads SOUL.md first, then loads skills, then reads MEMORY.md for context.

---

## 8. CVE-2026-25253 -- One-Click RCE

**CVSS**: 8.8 (High)
**CWE**: CWE-669 (Incorrect Resource Transfer Between Spheres)
**Affected**: OpenClaw (all versions before 2026.1.29)
**Patched**: Version 2026.1.29 (January 30, 2026)
**NVD**: [nvd[.]nist[.]gov/vuln/detail/CVE-2026-25253](hxxps://nvd[.]nist[.]gov/vuln/detail/CVE-2026-25253)

### The Kill Chain

The attack is a "1-Click RCE Kill Chain" that executes in milliseconds:

1. Attacker crafts a malicious link containing a `gatewayUrl` query parameter
2. Victim clicks the link; the Control UI **blindly accepts the gatewayUrl parameter**
3. The UI immediately establishes a WebSocket connection to the attacker's server
4. The connection automatically bundles the user's stored **authToken** and sends it to the attacker
5. The WebSocket server fails to validate the **origin header**
6. Attacker gains operator-level access to the gateway API
7. Attacker executes arbitrary config changes and code execution on the gateway host

### Why It Worked

Two design failures combined:
- The Control UI trusted the `gatewayUrl` parameter without verification
- The WebSocket server did not validate origin headers

### Impact

Any deployment where a user has authenticated to the Control UI. Attacker gains full operator-level access to the entire gateway API -- config changes, code execution, data access.

### Scanning Results

- As of Feb 3, 2026: Censys found 21,639 exposed instances
- Hunt.io found 42,665 exposed instances, 5,194 actively verified as vulnerable
- 15,200+ exposed instances appeared vulnerable to RCE

---

## 9. ClawHavoc Campaign

**Discovered by**: Koi Security (researcher Oren Yomtov)
**Campaign name**: ClawHavoc
**Scale**: 341 malicious skills initially; 824+ as of February 16, 2026; eventually 1,184+ confirmed

### The Operation

- Koi audited all 2,857 skills on ClawHub
- Found 341 malicious skills across multiple campaigns
- **335 of 341** traced to a single coordinated operation (ClawHavoc)
- All shared the same command-and-control infrastructure
- Campaign expanded to **~25 entirely new attack categories**

### Disguise Categories

Malicious skills masqueraded as:
- Cryptocurrency wallets and trackers
- Solana wallet trackers
- Polymarket trading bots
- YouTube utilities and summarizers
- Google Workspace integrations
- Auto-updaters
- Browser automation agents
- Coding agents
- LinkedIn/WhatsApp integrations
- PDF tools
- **Fake security-scanning skills** (ironic -- malware disguised as malware scanners)

### Attack Mechanism

1. Victim installs a skill with professional-looking documentation
2. A "Prerequisites" section says they need to install something first
3. The skill uses social engineering to convince users to execute malicious commands
4. Payloads steal: exchange API keys, wallet private keys, SSH credentials, browser passwords
5. Scripts zip stolen data and exfiltrate via HTTP POST to attacker-controlled servers

### Memory Targeting

One of the most concerning aspects: the campaign specifically targeted OpenClaw's **SOUL.md** and **MEMORY.md** files. Manipulating these files permanently alters the agent's behavior even after the malicious skill is uninstalled.

### Koi's Response

Koi created **Clawdex** -- a defensive skill that OpenClaw bots can install to protect themselves before damage is done. Available on ClawHub.

---

## 10. Snyk ToxicSkills Study

**Published**: February 5, 2026
**Scope**: 3,984 skills from ClawHub and skills.sh (largest publicly available corpus)
**Repository**: [github[.]com/snyk-labs/toxicskills-goof](hxxps://github[.]com/snyk-labs/toxicskills-goof)

### Key Findings

| Metric | Value |
|--------|-------|
| Skills scanned | 3,984 |
| Skills with critical security issues | 534 (13.4%) |
| Skills with at least one security flaw | 1,467 (36.82%) |
| Confirmed malicious payloads | 76 (human-verified) |
| Malicious skills with prompt injection | 91% |
| Legitimate top-100 skills with prompt injection | 0% |
| Skills exposing plaintext credentials via LLM context | 283 (7.1%) |
| Skills with prompt injection vulnerabilities | 36% |

### Categories of Issues

- **Malware distribution**: Credential theft, backdoor installation, data exfiltration
- **Prompt injection**: 36% of all skills contained prompt injection vulnerabilities
- **Credential exposure**: 283 skills exposed API keys and PII in plaintext through the LLM's context window
- **Dual-attack pattern**: 100% of confirmed malicious skills combined traditional code exploits with prompt injection -- bypassing both AI safety systems and traditional security tools simultaneously

### Why This Matters

Agent skills inherit all the permissions of the agent itself. Modern agents often have access to filesystem, shell, API keys, email, cloud infrastructure. A malicious skill gets all of that for free.

---

## 11. Snyk clawdhub Reverse Shell Campaign

**Discovered**: February 2, 2026 by Snyk Staff Research Engineer Luca Beurer-Kellner
**Campaign variant name**: `clawdhub` (note the extra `d` -- typosquatting)

### Timeline

1. Original malicious skill `clawhub` published by user `zaycv` -- masquerading as official CLI tool for managing agent skills
2. Accumulated 7,743 downloads before removal on February 3, 2026
3. Attacker returned with renamed variant `clawdhub1` (discovered by Snyk engineer Aleksei Kudrinskii)
4. Variant remained active after original removal

### Attack Method

Multi-stage delivery mechanism that **bypasses ClawHub's static analysis**:
- Malicious logic kept entirely **external to the SKILL.md file**
- SKILL.md itself appears clean
- Scripts and auxiliary files contain the actual payloads
- Reverse shells dropped on Windows and macOS targets

### Broader Context

Part of a larger campaign: 30+ malicious skills distributed via ClawHub, with a single threat actor responsible for uploading 677 packages. The total count across all repositories reached 1,184 malicious skills on ClawHub, and 2,200+ on GitHub.

---

## 12. AMOS Stealer via Malicious Skills

**Researched by**: Trend Micro
**Malware**: Atomic macOS Stealer (AMOS) -- new variant

### Evolution

AMOS evolved from being distributed via cracked software downloads to a sophisticated supply chain attack that manipulates AI agentic workflows. This is a significant evolution in malware delivery -- using AI agents as trusted intermediaries.

### Distribution

- 39 malicious skills identified on ClawHub, SkillsMP, and GitHub
- 2,200+ malicious skills discovered on GitHub alone (broader campaign)
- No specific pattern of focus -- covered wide variety of categories

### Attack Mechanism

1. Malicious SKILL.md instructions exploit the AI agent as a trusted intermediary
2. Agent presents "fake setup requirements" to the user
3. A deceptive **human-in-the-loop dialogue box** pops up
4. User is tricked into manually entering their password
5. AMOS variant installs without system persistence

### Data Exfiltrated

- Apple Keychain
- KeePass databases
- Various user documents
- SSH keys
- Browser passwords
- Cryptocurrency wallets

Notable: this AMOS variant **ignores .env files** but targets keychains instead -- suggesting the attackers are focused on personal credentials rather than developer API keys.

---

## 13. Memory Poisoning -- SOUL.md and MEMORY.md

### Architecture

OpenClaw uses two critical identity/memory files:

- **SOUL.md**: Defines who the agent is, how it behaves, what it values. Read first at every boot.
- **MEMORY.md**: Stores long-lived context that persists across sessions. Influences future decision-making.

These are plain markdown files on disk. They are not immutable. Any process (or skill) with filesystem access can modify them.

### The Attack Pattern

1. Skill writes malicious instructions into SOUL.md or MEMORY.md during installation
2. Uninstalling the skill removes the code but the **file modifications remain**
3. The "clean" agent still reads the poisoned memory at next boot
4. Even with a pristine SOUL.md, the agent queries memory: "How did I handle this previously?"
5. RAG system retrieves examples generated during the compromised phase
6. Agent re-derives malicious behavior from its own history

This is **Identity Persistence** -- a single successful injection becomes permanent because it modifies the instructions an agent loads at boot time.

### Why File-Based Memory is Dangerous

- No access controls on memory files
- No integrity verification (no checksums, no signing)
- No audit trail of modifications
- Memory entries survive skill uninstallation
- RAG retrieval can resurrect compromised behavior even after cleanup

---

## 14. Lakera Hackathon -- Instruction Drift

**Published by**: Lakera AI
**Method**: Controlled lab experiment at an internal OpenClaw hackathon

### The Experiment

Researchers conditioned an AI agent with persistent memory to execute a malicious binary via Discord messages alone -- **without** prompt injection bypass, API misconfiguration, or privilege escalation.

### How Instruction Drift Works

1. Over multiple interactions, attacker sends messages through Discord
2. Messages are not adversarial prompts -- they are normal-seeming conversations
3. Each interaction creates durable memory entries in the global MEMORY.md
4. Over time, these entries shift the agent's internal trust hierarchy
5. Once trust assumptions change sufficiently, a "system update" request triggers reverse shell execution

### Key Properties

- **Not a single-prompt exploit** -- requires gradual conditioning
- **No traditional injection** -- works through legitimate conversation channels
- **Targets durable state** -- entries in MEMORY.md survive restarts
- **Persistent memory becomes policy** -- the agent treats its own history as ground truth

This research demonstrates that agent security is not just about blocking malicious inputs. An agent can drift into dangerous behavior through accumulated, individually benign interactions.

---

## 15. Exposed Instances at Scale

### Scanning Results (January-February 2026)

| Scanner | Exposed Instances | Date |
|---------|-------------------|------|
| Censys | 21,639 | Jan 31, 2026 |
| Bitsight | 30,000+ | Feb 2026 |
| Hunt.io | 42,665 total; 5,194 verified vulnerable | Feb 2026 |
| SecurityScorecard | "hundreds of thousands" | Feb 2026 |

### Geographic Distribution

1. United States (largest share)
2. China
3. Singapore

### Growth Rate

Censys tracked growth from ~1,000 to 21,000+ publicly exposed instances between January 25-31, 2026 (one week).

### How Instances Are Detectable

- HTTP responses match Moltbot or Clawdbot signatures (even after rename)
- OpenClaw listens on TCP/18789 by default
- Gateway binds to all network interfaces by default
- Many instances running without authentication

### What Exposure Means

An exposed OpenClaw instance potentially leaks:
- API keys and credentials (plaintext)
- Private messages from connected platforms
- Calendar data
- Email content
- The agent's full SOUL.md and MEMORY.md (behavioral fingerprint)
- Gateway tokens that allow remote control

---

## 16. Microsoft Security Advisory

**Published**: February 19, 2026
**Source**: Microsoft Security Blog
**Title**: "Running OpenClaw safely: identity, isolation, and runtime risk"

### Core Assessment

> "Self-hosted agents combine untrusted code and untrusted instructions into a single execution loop that runs with valid credentials. That is the core risk."

> "Running OpenClaw is a trust decision about which machine, identities, and data you are prepared to expose when the agent processes untrusted input."

> "Installing a skill is basically installing privileged code."

### Three Immediate Risks in Unguarded Deployments

1. Credentials and accessible data may be exposed or exfiltrated
2. The agent's persistent state/memory can be modified
3. Modified memory causes the agent to follow attacker-supplied instructions over time

### Microsoft's Recommendations

- Use OpenClaw **only in isolated environments**
- No access to non-dedicated credentials or data
- **Assume compromise is possible**: isolate the runtime, constrain access, monitor continuously, be prepared to rebuild without delay
- OpenClaw is "unsuited to run on standard personal or enterprise workstations"

Microsoft Defender recommended treating OpenClaw as a high-risk application.

---

## 17. Moltbook Breach

**Moltbook** was a third-party platform/service associated with the OpenClaw ecosystem (during the Moltbot naming phase).

### What Happened

- Supabase backend was misconfigured
- **35,000 email addresses** exposed
- **1.5 million agent tokens** accessible to anyone with a browser
- No authentication required to access the database

This was not a sophisticated attack -- it was a catastrophic configuration error that left sensitive data publicly accessible. The tokens could be used to control agents, access their connected services, and exfiltrate data.

See [Note 04](./04_Research_Findings.md) Section 5 for detailed technical analysis including enumeration methodology, data breakdown, and timeline.

---

## 18. Infostealer Targeting OpenClaw Files

**Reported by**: The Hacker News (February 2026)

Traditional infostealer malware (not agent-specific) has been updated to specifically target OpenClaw configuration files:

- Gateway tokens
- SOUL.md and MEMORY.md files
- API keys stored in plaintext configuration
- Session credentials

This represents a convergence: traditional malware is now **specifically seeking AI agent configuration** as high-value theft targets. An attacker with your SOUL.md and gateway token can impersonate your agent, access your connected services, and read your private communications.

---

## 19. Dark Web and Underground Chatter

**Reported by**: Bleeping Computer, citing Flare threat intelligence

### Findings

- Heavy Telegram and dark web chatter about OpenClaw
- More research hype than mass exploitation (as of Feb 2026)
- Real supply-chain risk in the skills marketplace is confirmed
- Limited signs of **large-scale** criminal operationalization (yet)
- The strongest confirmed risk pattern: malicious skill distribution with execution inside trusted automation context, payload running for credential/session/data exfiltration

### Assessment

The underground sees OpenClaw as an opportunity. The skills marketplace is the primary attack vector. Even without botnet-scale weaponization, the existing supply chain attacks are "enough to be dangerous."

---

## 20. Skill Verification and Trust Model

### Before the Crisis

ClawHub was completely open:
- Anyone with a week-old GitHub account could publish
- No code review
- No automated security scanning
- No capability declarations
- No sandboxing

### Current Trust Model (Post-Incident)

OpenClaw established a multi-phase security program:

1. **Phase 1 (Transparency)**: Threat model development
2. **Phase 2 (Product Security Roadmap)**: GitHub issues for defensive engineering
3. **Phase 3 (Code Review Preparation and Execution)**: Manual review and remediation
4. **Phase 4 (Triage Function)**: Security advisories

Skill verification process:
- Developers can submit verification requests from their ClawHub dashboard
- OpenClaw team reviews submissions within 3-5 business days
- VirusTotal scanning for all published skills (see Section 21)
- Security analysis checks runtime requirement declarations against actual behavior

### Third-Party Security Tools

- **Clawdex** (Koi Security): Defensive skill for OpenClaw bots
- **SecureClaw** (Adversa AI): 55 automated audit/hardening checks, maps to OWASP Agentic Security Top 10
- **Bitdefender AI Skills Checker**: Consumer-facing skill scanner
- **Snyk agent-scan**: [github[.]com/snyk/agent-scan](hxxps://github[.]com/snyk/agent-scan) -- security scanner for AI agents, MCP servers, and agent skills
- **OpenClaw Security Monitor**: [github[.]com/adibirzu/openclaw-security-monitor](hxxps://github[.]com/adibirzu/openclaw-security-monitor) -- detects ClawHavoc, AMOS, CVE-2026-25253, memory poisoning

---

## 21. VirusTotal Partnership

**Announced**: February 2026

### How It Works

1. Developer publishes skill to ClawHub
2. Platform bundles code into deterministic package
3. **SHA-256 hash** computed and checked against VirusTotal database
4. If no existing analysis: full bundle uploaded for scanning
5. VirusTotal's **Code Insight** (powered by Gemini) performs security-focused analysis
6. Examines what code **actually does** rather than just signature matching

### Limitations Acknowledged by OpenClaw

> "VirusTotal scanning won't catch everything. A skill that uses natural language to instruct an agent to do something malicious won't trigger a virus signature. A carefully crafted prompt injection payload won't show up in a threat database."

This is a fundamental limitation: VirusTotal is designed for binary malware, not markdown-based prompt injection. Agent skills are hybrid artifacts -- part code, part natural language instructions -- and traditional AV approaches only address half the threat surface.

### Alongside the Partnership

OpenClaw committed to publishing:
- Formal threat model for the AI agent ecosystem
- Public security roadmap
- Complete codebase audit details
- Security reporting process with defined SLAs

---

## 22. Why Skill Scanners Fail

**Source**: Snyk blog -- "Why Your Skill Scanner Is Just False Security (and Maybe Malware)"

### The SkillGuard Incident

Snyk analyzed **SkillGuard**, a popular security tool from ClawHub. Their internal systems flagged it as a **malicious skill itself** -- it attempted to install a payload under the guise of "updating definitions." A security scanner on the skills marketplace was literally malware.

### Testing Community Scanners

Snyk tested the most popular community skill scanners (SkillGuard, Skill Defender, Agent Tinman) against a custom semi-malicious skill:

- **Failed to catch actual threats**: Exfiltration code did not match hardcoded "bad" strings
- **Flagged themselves**: Their own reference files contained the threat patterns they scan for
- **The Antivirus Paradox**: Scanners are blind to anything new because they rely on denylist pattern matching

### Why Traditional Scanning Fails for Agent Skills

- Agent skills are **hybrid artifacts** -- part executable code, part natural language instructions
- Denylist of "bad words" or forbidden patterns is a losing battle against infinite natural language
- Exfiltration can be described in natural language ("send this data to the following endpoint for analysis")
- Prompt injection is expressed in markdown, not in code
- External references (npm packages, GitHub repos, CDN scripts, Docker images) extend trust boundaries beyond the skill itself

### Snyk's Approach

Snyk built the `mcp-scan` engine combining:
- Multiple customized **LLM-based judges** (for natural language analysis)
- **Deterministic rules** (for traditional code analysis)
- Both are required because agent skills require both code analysis and language understanding

This aligns with our findings in [Note 09](./09_Skill_Scanning_And_Detection_Landscape.md) -- the gap between traditional security tooling and the agent skill threat model is the central unsolved problem.

---

## 23. Relationship to Claude Code

OpenClaw and Claude Code are **separate products** from different developers that share the same skill format and can be used together.

### Key Differences

| Aspect | Claude Code | OpenClaw |
|--------|-------------|----------|
| Developer | Anthropic | Peter Steinberger (now at OpenAI) |
| Purpose | Focused coding assistant | Persistent 24/7 personal AI agent |
| Activation | Invoked per terminal session | Always-on service |
| LLM | Claude only | Any LLM (Claude, GPT, Gemini, DeepSeek) |
| Skill format | SKILL.md (Agent Skills standard) | SKILL.md (Agent Skills standard) |
| Memory | CLAUDE.md, MEMORY.md | SOUL.md, MEMORY.md |
| Marketplace | github.com/anthropics/skills (official) | ClawHub.ai |
| Permissions | Scoped to terminal session | Full system access 24/7 |

### How They Connect

- Both use the **Agent Skills open standard** (SKILL.md format)
- Claude Code skills are compatible with OpenClaw and vice versa
- OpenClaw can invoke Claude Code via MCP (Model Context Protocol)
- They are complementary: Claude Code handles focused coding sessions, OpenClaw handles persistent automation

### Security Implications for Claude Code

1. **Shared attack surface**: A malicious skill written for OpenClaw's ClawHub can potentially be installed in Claude Code
2. **Format compatibility**: The same SKILL.md format means attack techniques transfer directly
3. **ClawHub as distribution vector**: Skills from ClawHub can be manually installed in Claude Code
4. **Same fundamental vulnerability**: Skills inherit all agent permissions regardless of platform
5. **Cross-references in Note 12**: See [Agent Configuration Files](./12_Agent_MD_Configuration_Files.md) for CLAUDE.md-specific attacks

### Anthropic's Skills Repository

Anthropic maintains an official skills repository at [github[.]com/anthropics/skills](hxxps://github[.]com/anthropics/skills) -- curated, reviewed skills that demonstrate the format. This is a controlled distribution channel, unlike the open ClawHub marketplace.

---

## 24. Competing Skill Marketplaces

The skills marketplace landscape has fragmented beyond ClawHub:

| Platform | Scale | Notes |
|----------|-------|-------|
| ClawHub.ai | 10,700+ skills | Official OpenClaw registry |
| SkillsMP | 96,000+ skills | Largest, Claude Code compatible |
| skills.sh | Included in Snyk audit | Part of ToxicSkills corpus |
| SkillHub.club | Active | Claude-focused marketplace |
| GitHub | 2,200+ malicious skills found | Unregulated distribution |

The fragmentation compounds supply chain risk. Each platform has different (or no) vetting processes. Skills can be cross-listed. A single malicious skill can appear on multiple platforms under different names.

---

## 25. Defense Recommendations

### For Individual Users

1. **Review skill source code** before installation -- read SKILL.md AND all scripts/references
2. **Check author reputation** -- GitHub profile age, commit history, other projects
3. **Test in a sandbox** -- VM, container, or dedicated machine with no real credentials
4. **Monitor memory files** -- Watch for unauthorized modifications to SOUL.md and MEMORY.md
5. **Use file integrity monitoring** -- Hash critical files, alert on changes
6. **Disable unnecessary permissions** -- Principle of least privilege for connected services
7. **Never expose the gateway to the internet** -- Bind to localhost only
8. **Enable authentication** -- Never run with `auth: none`

### For Organizations

1. **Follow Microsoft's advisory** -- Isolated environments only, no production credentials
2. **Assume compromise** -- Design for rapid rebuild and containment
3. **Block ClawHub at the firewall** -- If OpenClaw is not approved for use
4. **Monitor for OpenClaw signatures** -- Shodan/Censys queries for internal exposure
5. **Deploy SecureClaw or equivalent** -- 55 automated audit checks
6. **Implement skill allowlisting** -- Only approved skills, no ClawHub auto-install

### For Skill Developers

1. **Sign your skills** (when supported) -- Establish verifiable provenance
2. **Declare actual requirements** -- Honest `requires` frontmatter
3. **No external dependencies** -- Self-contained skills are auditable skills
4. **No obfuscated code** -- If it needs obfuscation, it should not be a skill

### Architectural Recommendations

1. **Capability-based security** -- Skills should declare needed permissions, agent should enforce
2. **Memory integrity** -- Cryptographic verification of SOUL.md and MEMORY.md
3. **Skill isolation** -- Sandboxed execution for untrusted skills
4. **Audit trail** -- Immutable log of all memory modifications
5. **Supply chain verification** -- Package signing, reproducible builds, SBOM for skills

---

## 26. Key Takeaways for Research

1. **OpenClaw is the first mass-adoption AI agent security crisis** -- 220K stars, 42K+ exposed instances, 1,184+ malicious skills, CVE with CVSS 8.8, and multiple active campaigns all within a single month.

2. **The Agent Skills standard is cross-platform** -- Attacks developed for OpenClaw/ClawHub transfer to Claude Code, Codex CLI, Copilot, and any tool implementing the standard. This is a systemic risk, not a vendor-specific one.

3. **Skills are the new packages** -- The agent skill supply chain mirrors the npm/PyPI supply chain, but with worse security controls and higher privileges. Every lesson from dependency confusion, typosquatting, and package hijacking applies -- plus new attack surfaces like memory poisoning and instruction drift.

4. **Memory persistence is a novel attack primitive** -- SOUL.md/MEMORY.md poisoning creates self-reinforcing compromise loops. Even cleaning up the infection leaves poisoned memories that re-derive the malicious behavior. This has no analog in traditional software supply chains.

5. **Traditional security tooling is insufficient** -- Skill scanners using pattern matching fail against natural language payloads. The hybrid nature of agent skills (code + natural language) requires hybrid analysis (deterministic rules + LLM-based judges). This is an unsolved problem at scale.

6. **The security community responded rapidly** -- Microsoft, Snyk, Trend Micro, Lakera, Koi Security, Censys, VirusTotal, Adversa AI, Repello AI, and others published detailed research within weeks. This level of coordinated response is unusual and reflects the perceived severity.

7. **Steinberger joining OpenAI** means the project moves to a foundation. The security posture of that foundation will determine whether OpenClaw becomes a cautionary tale or a mature platform.

---

## 27. Sources

### Primary Research

- [ClawHavoc: 341 Malicious Clawed Skills Found by the Bot They Were Targeting](hxxps://www[.]koi[.]ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting) -- Koi Security
- [Snyk ToxicSkills: Malicious AI Agent Skills on ClawHub](hxxps://snyk[.]io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) -- Snyk
- [Inside the 'clawdhub' Malicious Campaign: AI Agent Skills Drop Reverse Shells](hxxps://snyk[.]io/articles/clawdhub-malicious-campaign-ai-agent-skills/) -- Snyk
- [From SKILL.md to Shell Access in Three Lines of Markdown](hxxps://snyk[.]io/articles/skill-md-shell-access/) -- Snyk
- [Why Your "Skill Scanner" Is Just False Security (and Maybe Malware)](hxxps://snyk[.]io/blog/skill-scanner-false-security/) -- Snyk
- [How a Malicious Google Skill on ClawHub Tricks Users Into Installing Malware](hxxps://snyk[.]io/blog/clawhub-malicious-google-skill-openclaw-malware/) -- Snyk
- [280+ Leaky Skills: How OpenClaw and ClawHub Are Exposing API Keys and PII](hxxps://snyk[.]io/blog/openclaw-skills-credential-leaks-research/) -- Snyk
- [Malicious OpenClaw Skills Used to Distribute Atomic MacOS Stealer](hxxps://www[.]trendmicro[.]com/en_us/research/26/b/openclaw-skills-used-to-distribute-atomic-macos-stealer.html) -- Trend Micro
- [Memory Poisoning and Instruction Drift: From Discord Chat to Reverse Shell](hxxps://www[.]lakera[.]ai/blog/memory-poisoning-instruction-drift-from-discord-chat-to-reverse-shell) -- Lakera AI
- [From Automation to Infection: How OpenClaw AI Agent Skills Are Being Weaponized](hxxps://blog[.]virustotal[.]com/2026/02/from-automation-to-infection-how.html) -- VirusTotal Blog
- [Malicious OpenClaw Skills Exposed: A Full Teardown](hxxps://repello[.]ai/blog/malicious-openclaw-skills-exposed-a-full-teardown) -- Repello AI
- [OpenClaw in the Wild: Mapping the Public Exposure of a Viral AI Assistant](hxxps://censys[.]com/blog/openclaw-in-the-wild-mapping-the-public-exposure-of-a-viral-ai-assistant/) -- Censys
- [Threat Intelligence: Analysis of ClawHub Malicious Skills Poisoning](hxxps://slowmist[.]medium[.]com/threat-intelligence-analysis-of-clawhub-malicious-skills-poisoning-0448ffd49c80) -- SlowMist

### Vendor Security Advisories

- [Running OpenClaw Safely: Identity, Isolation, and Runtime Risk](hxxps://www[.]microsoft[.]com/en-us/security/blog/2026/02/19/running-openclaw-safely-identity-isolation-runtime-risk/) -- Microsoft Security Blog
- [Personal AI Agents like OpenClaw Are a Security Nightmare](hxxps://blogs[.]cisco[.]com/ai/personal-ai-agents-like-openclaw-are-a-security-nightmare) -- Cisco
- [Key OpenClaw Risks](hxxps://www[.]kaspersky[.]com/blog/moltbot-enterprise-risk-management/55317/) -- Kaspersky
- [The OpenClaw Experiment Is a Warning Shot for Enterprise AI Security](hxxps://www[.]sophos[.]com/en-us/blog/the-openclaw-experiment-is-a-warning-shot-for-enterprise-ai-security) -- Sophos
- [OpenClaw Security 101: Vulnerabilities and Hardening 2026](hxxps://adversa[.]ai/blog/openclaw-security-101-vulnerabilities-hardening-2026/) -- Adversa AI
- [OpenClaw Security: Risks of Exposed AI Agents](hxxps://www[.]bitsight[.]com/blog/openclaw-ai-security-risks-exposed-instances) -- Bitsight

### CVE and Vulnerability Details

- [NVD -- CVE-2026-25253](hxxps://nvd[.]nist[.]gov/vuln/detail/CVE-2026-25253) -- NIST
- [CVE-2026-25253: 1-Click RCE in OpenClaw Through Auth Token Exfiltration](hxxps://socradar[.]io/blog/cve-2026-25253-rce-openclaw-auth-token/) -- SOCRadar
- [CVE-2026-25253 Impact, Exploitability, and Mitigation Steps](hxxps://www[.]wiz[.]io/vulnerability-database/cve/cve-2026-25253) -- Wiz
- [OpenClaw Bug Enables One-Click Remote Code Execution via Malicious Link](hxxps://thehackernews[.]com/2026/02/openclaw-bug-enables-one-click-remote.html) -- The Hacker News
- [Hunting OpenClaw Exposures: CVE-2026-25253 in Internet-Facing AI Agent Gateways](hxxps://hunt[.]io/blog/cve-2026-25253-openclaw-ai-agent-exposure) -- Hunt.io

### News Coverage

- [Researchers Find 341 Malicious ClawHub Skills Stealing Data from OpenClaw Users](hxxps://thehackernews[.]com/2026/02/researchers-find-341-malicious-clawhub.html) -- The Hacker News
- [Infostealer Steals OpenClaw AI Agent Configuration Files and Gateway Tokens](hxxps://thehackernews[.]com/2026/02/infostealer-steals-openclaw-ai-agent.html) -- The Hacker News
- [OpenClaw Integrates VirusTotal Scanning to Detect Malicious ClawHub Skills](hxxps://thehackernews[.]com/2026/02/openclaw-integrates-virustotal-scanning.html) -- The Hacker News
- [From Clawdbot to Moltbot to OpenClaw: Meet the AI Agent Generating Buzz and Fear Globally](hxxps://www[.]cnbc[.]com/2026/02/02/openclaw-open-source-ai-agent-rise-controversy-clawdbot-moltbot-moltbook.html) -- CNBC
- [Why the OpenClaw AI Assistant Is a 'Privacy Nightmare'](hxxps://news[.]northeastern[.]edu/2026/02/10/open-claw-ai-assistant/) -- Northeastern University
- [OpenClaw Creator Peter Steinberger Joins OpenAI](hxxps://techcrunch[.]com/2026/02/15/openclaw-creator-peter-steinberger-joins-openai/) -- TechCrunch
- [The OpenClaw Hype: Analysis of Chatter from Open-Source Deep and Dark Web](hxxps://www[.]bleepingcomputer[.]com/news/security/the-openclaw-hype-analysis-of-chatter-from-open-source-deep-and-dark-web/) -- Bleeping Computer
- [Hundreds of Malicious Skills Found in OpenClaw's ClawHub](hxxps://www[.]esecurityplanet[.]com/threats/hundreds-of-malicious-skills-found-in-openclaws-clawhub/) -- eSecurity Planet
- [The OpenClaw Security Crisis](hxxps://conscia[.]com/blog/the-openclaw-security-crisis/) -- Conscia
- [The OpenClaw Security Saga: How AI Adoption Outpaced Security Boundaries](hxxps://www[.]cyera[.]com/research-labs/the-openclaw-security-saga-how-ai-adoption-outpaced-security-boundaries) -- Cyera

### Documentation and Standards

- [OpenClaw Wikipedia](hxxps://en[.]wikipedia[.]org/wiki/OpenClaw) -- Wikipedia
- [OpenClaw Official Docs: Skills](hxxps://docs[.]openclaw[.]ai/tools/skills) -- OpenClaw
- [OpenClaw Official Docs: ClawHub](hxxps://docs[.]openclaw[.]ai/tools/clawhub) -- OpenClaw
- [OpenClaw Trust Page](hxxps://trust[.]openclaw[.]ai/) -- OpenClaw
- [OpenClaw Partners with VirusTotal for Skill Security](hxxps://openclaw[.]ai/blog/virustotal-partnership) -- OpenClaw Blog
- [Agent Skills Specification](hxxps://agentskills[.]io/specification) -- Agent Skills
- [Agent Skills GitHub](hxxps://github[.]com/agentskills/agentskills) -- Agent Skills
- [Anthropic Skills Repository](hxxps://github[.]com/anthropics/skills) -- Anthropic
- [Claude Code Skills Documentation](hxxps://code[.]claude[.]com/docs/en/skills) -- Anthropic
- [ClawHub Skill Format Documentation](hxxps://github[.]com/openclaw/clawhub/blob/main/docs/skill-format.md) -- OpenClaw

### Community and Analysis

- [OpenClaw vs Claude Code: Complete Comparison Guide](hxxps://claudefa[.]st/blog/tools/extensions/openclaw-vs-claude-code) -- ClaudeFast
- [OpenClaw vs Claude Code: Which Agentic Tool Should You Use](hxxps://www[.]datacamp[.]com/blog/openclaw-vs-claude-code) -- DataCamp
- [Decoding ClawHub.ai: The Official Skill Store of 220K-Star OpenClaw](hxxps://help[.]apiyi[.]com/en/clawhub-ai-openclaw-skills-registry-guide-en.html) -- Apiyi
- [The Agent Skills Gold Rush Has a Malware Problem](hxxps://dev[.]to/meimakes/the-agent-skills-gold-rush-has-a-malware-problem-2jai) -- DEV Community
- [The Ultimate Guide to AI Agents in 2026: OpenClaw vs. Claude Cowork vs. Claude Code](hxxps://dev[.]to/tech_croc_f32fbb6ea8ed4/the-ultimate-guide-to-ai-agents-in-2026-openclaw-vs-claude-cowork-vs-claude-code-395h) -- DEV Community
- [OpenClaw Creator: "I Ship Code I Don't Read"](hxxps://newsletter[.]pragmaticengineer[.]com/p/the-creator-of-clawd-i-ship-code) -- The Pragmatic Engineer
- [Why Trying to Secure OpenClaw is Ridiculous](hxxps://www[.]aikido[.]dev/blog/why-trying-to-secure-openclaw-is-ridiculous) -- Aikido
- [OpenClaw Soul and Evil: Identity Files as Attack Surfaces](hxxps://www[.]mmntm[.]net/articles/openclaw-soul-evil) -- MMNTM
- [Trust Without Verification](hxxps://dougseven[.]com/2026/02/09/trust-without-verification/) -- Doug Seven

### GitHub Repositories

- [openclaw/openclaw](hxxps://github[.]com/openclaw/openclaw) -- Main repository (220K+ stars)
- [openclaw/clawhub](hxxps://github[.]com/openclaw/clawhub) -- Skill Directory
- [snyk-labs/toxicskills-goof](hxxps://github[.]com/snyk-labs/toxicskills-goof) -- ToxicSkills research corpus
- [snyk/agent-scan](hxxps://github[.]com/snyk/agent-scan) -- Security scanner for AI agents and skills
- [adversa-ai/secureclaw](hxxps://github[.]com/adversa-ai/secureclaw) -- OWASP-aligned security plugin
- [adibirzu/openclaw-security-monitor](hxxps://github[.]com/adibirzu/openclaw-security-monitor) -- Security monitoring tool
- [VoltAgent/awesome-openclaw-skills](hxxps://github[.]com/VoltAgent/awesome-openclaw-skills) -- Curated skill collection

### Hacker News

- [Running OpenClaw safely: identity, isolation, and runtime risk](hxxps://news[.]ycombinator[.]com/item?id=47082933) -- HN discussion of Microsoft advisory

---

## Cross-References

- [Note 02: Skill Injection Analysis](./02_Skill_Injection_Analysis.md) -- Original skill injection research
- [Note 05: Claude Code Skill Architecture](./05_Claude_Code_Skill_Architecture.md) -- Claude Code's implementation of the shared standard
- [Note 09: Skill Scanning and Detection Landscape](./09_Skill_Scanning_And_Detection_Landscape.md) -- Detection tools and the ToxicSkills study
- [Note 11: AI Memory and Corruption](./11_AI_Memory_And_Corruption.md) -- Memory architecture attacks (MINJA, RAG poisoning)
- [Note 12: Agent Configuration Files](./12_Agent_MD_Configuration_Files.md) -- CLAUDE.md, AGENTS.md, rules file attacks
