# 🛡️ AI Agent Security Research

> *Documenting how AI coding agents get exploited -- so we can build better defenses.*

[![Educational](https://img.shields.io/badge/Purpose-Educational%20%26%20Defensive-blue)]()
[![AI Agents](https://img.shields.io/badge/Scope-AI%20Coding%20Agents-purple)]()
[![No Live Exploits](https://img.shields.io/badge/Exploits-None%20Executable-green)]()

---

## 🔍 What This Is

A growing collection of research, annotated attack examples, and defense strategies targeting the security of **AI coding agents** -- Claude Code, Cursor, Copilot, Windsurf, and the broader ecosystem of LLM-powered development tools.

Every attack has a defense. Every payload is annotated, defanged, and educational.

> **Note:** This project is actively maintained and frequently updated as new findings emerge, attack surfaces evolve, and AI-assisted research uncovers new patterns. Expect content to change regularly.

---

## 📝 Research Notes

| | Topic | What You'll Learn |
|---|-------|-------------------|
| 🗂️ | [Tools & Frameworks Index](notes/00_Tools_And_Frameworks_Index.md) | Quick reference for every tool, framework, benchmark, and standard mentioned across all notes |
| 💉 | [Prompt Injection & Skill Injection](notes/01_Skill_Injection_Analysis.md) | Foundational injection concepts, agent attack surface, trojanized skill teardown, supply chain comparison |
| 🧱 | [Defense Patterns](notes/02_Defense_Patterns.md) | Sanitization, sandboxing, and mitigation strategies with working code |
| ⚙️ | [Claude Code Skill Architecture](notes/03_Claude_Code_Skill_Architecture.md) | How Claude Code's extensibility (skills, hooks, MCP) creates attack surface |
| 👻 | [LLM Hallucination Prevention](notes/04_LLM_Hallucination_Prevention.md) | Why models invent things, how to detect it, and how to stop it |
| 🌐 | [AI Coding Language Performance](notes/05_AI_Coding_Language_Performance.md) | Multilingual benchmarks, token efficiency, and language-steering attacks |
| 🔓 | [LLM Jailbreaking Deep Dive](notes/06_LLM_Jailbreaking_Deep_Dive.md) | Full taxonomy: DAN to GCG to Crescendo, defenses, benchmarks, agent implications |
| 🔍 | [Skill Scanning & Detection Landscape](notes/07_Skill_Scanning_And_Detection_Landscape.md) | Cisco Skill Scanner, VirusTotal, ToxicSkills audit, gap analysis, what to build next |
| 📋 | [AI GRC & Policy Landscape](notes/08_AI_GRC_And_Policy_Landscape.md) | NIST AI RMF, EU AI Act, ISO 42001, state laws, agentic governance, OWASP Agentic Top 10 |
| 🧠 | [AI Memory & Corruption](notes/09_AI_Memory_And_Corruption.md) | Memory architectures, RAG poisoning, MINJA, persistence risks, real-world case studies, defenses |
| 📄 | [Agent Configuration Files](notes/10_Agent_MD_Configuration_Files.md) | CLAUDE.md/AGENTS.md attack surface, Rules File Backdoor, Unicode obfuscation, hardening recommendations |
| 🧠 | [Chatbot & AI Psychosis](notes/11_Chatbot_And_AI_Psychosis.md) | AI-induced psychosis, sycophancy mechanisms, documented deaths, folie a deux, weaponization, RAND national security analysis |
| 🦞 | [OpenClaw & ClawHub Security](notes/12_OpenClaw_And_ClawHub_Security.md) | OpenClaw architecture, ClawHub supply chain, CVE-2026-25253, ClawHavoc campaign, AMOS stealer, memory poisoning, 42K exposed instances |
| 🏪 | [AI Application Ecosystem Security](notes/13_AI_Application_Ecosystem_Security.md) | GPT Store, MCP tool poisoning, LangChain, HuggingFace, AutoGPT, CrewAI, Devin, IDEsaster, GlassWorm, OWASP Agentic Top 10, MITRE ATLAS |
| ⚔️ | [AI Hacking Frameworks](notes/14_AI_Hacking_Frameworks.md) | XBOW, Shannon, Strix, PentAGI, CAI, Reaper, Nebula, CHECKMATE, Garak, Promptfoo, PyRIT, benchmarks, architecture patterns |
| 💩 | [Bullshit Benchmark & LLM Honesty](notes/15_Bullshit_Benchmark_And_LLM_Honesty.md) | BullshitBench, TruthfulQA, SimpleQA, sycophancy benchmarks, Bullshit Index, abstention, slopsquatting, RLHF-security tension |
| 🛡️ | [AI Blue Teaming & Defensive AI](notes/16_AI_Blue_Teaming_And_Defensive_AI.md) | AI SOC agents, CrowdStrike Charlotte, Microsoft Security Copilot, malware RE, DARPA AIxCC, NIST AI 100-2, defender's advantage analysis |

---

## 🧪 Attack / Defense Examples

Hands-on annotated scenarios -- each one shows the attack **and** the fix.

| | Technique | TL;DR |
|---|-----------|-------|
| 🕵️ | [Hidden Comment Injection](examples/01_Hidden_Comment_Injection/) | HTML comments are invisible in markdown previews but the LLM reads every word |
| 🌊 | [Indirect Prompt Injection](examples/02_Indirect_Prompt_Injection/) | Poison the web page, API response, or file the agent fetches -- it obeys |
| 📤 | [Data Exfiltration Via Agent](examples/03_Data_Exfiltration_Via_Agent/) | The agent becomes an unwitting mule for your secrets, keys, and credentials |
| 📦 | [Hallucinated Package Injection](examples/04_Hallucinated_Package_Skill_Injection/) | LLM invents a package name, attacker registers it -- instant supply chain attack |
| 🔧 | [MCP Tool Poisoning](examples/05_MCP_Tool_Poisoning/) | Malicious instructions hidden in tool descriptions hijack agent behavior silently |

---

## 🗂️ Attack Taxonomy

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AI Agent Attacks                                       │
├──────────────┬──────────────────┬───────────────────┬───────────────────────────────┤
│ 🎯 Injection │ 🔗 Supply Chain  │ 📤 Exfiltration   │ 🧠 Memory & Persistence      │
│              │                  │                   │                               │
│ Direct       │ Trojan skills    │ Secrets & keys    │ RAG poisoning                │
│ Indirect     │ Hallucinated     │ Source code       │ Memory injection (MINJA)     │
│ Hidden       │  packages        │ Environment       │ Context window manipulation  │
│  comments    │ Poisoned docs    │  variables        │ Persistent backdoors         │
│ MCP tool     │ Rules file       │ Credentials       │ Config file persistence      │
│  poisoning   │  backdoor        │ Agent tokens      │ Instruction drift            │
│ Language-    │ Namespace        │ Chat history      │ SOUL.md/MEMORY.md poisoning  │
│  steering    │  squatting       │ IDE telemetry     │                               │
│ Sampling     │ GlassWorm        │                   │                               │
│  injection   │  extension worm  │                   │                               │
├──────────────┴──────────────────┴───────────────────┴───────────────────────────────┤
│ 🏗️ Framework & Platform                    │ 🛡️ Bypass & Escalation              │
│                                             │                                      │
│ MCP server compromise (CVE-2025-6514)      │ Sandbox escape (numpy allowlist)     │
│ OpenClaw gateway exposure (42K+ instances) │ Cross-agent privilege escalation     │
│ GPT Store plugin OAuth flaws               │ Tool confusion / confused deputy     │
│ HuggingFace pickle deserialization         │ Rug pull / bait-and-switch           │
│ IDE Chromium CVEs (94+ in Cursor/Windsurf) │ IDEsaster (30+ CVEs across AI IDEs) │
│ ClawHub malicious skills (1184+)           │ Agent-to-agent prompt injection      │
└─────────────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 🔧 Security Skill Suite

Working defensive tooling built on Claude Code's skill + hook architecture. These turn the research above into practical detection.

### Install from ClawHub

The fastest way to install -- each link goes to the ClawHub listing:

| Skill | ClawHub | What It Does |
|---|---|---|
| **vet-repo** | [clawhub.ai/ItsNishi/vet-repo](https://clawhub.ai/ItsNishi/vet-repo) | Scans `.claude/`, `.mcp.json`, `CLAUDE.md`, VS Code/Cursor configs for hook abuse, injection, MCP poisoning |
| **scan-skill** | [clawhub.ai/ItsNishi/scan-skill](https://clawhub.ai/ItsNishi/scan-skill) | Deep analysis of a single skill before installation -- frontmatter, HTML comments, persistence triggers, supporting scripts |
| **audit-code** | [clawhub.ai/ItsNishi/audit-code](https://clawhub.ai/ItsNishi/audit-code) | Code security review -- hardcoded secrets, dangerous calls, SQL injection, `.env` files, file permissions |

### Install from Source

If you prefer to install manually from this repo:

```bash
# Clone the repo
git clone git@github.com:ItsNishi/AI-Agent-Security.git

# Copy the skills you want into your project or personal skills directory
# Project-level (scoped to one repo):
cp -r AI-Agent-Security/.claude/skills/vet-repo /path/to/your/project/.claude/skills/
cp -r AI-Agent-Security/.claude/skills/scan-skill /path/to/your/project/.claude/skills/
cp -r AI-Agent-Security/.claude/skills/audit-code /path/to/your/project/.claude/skills/

# Personal-level (available in all projects):
cp -r AI-Agent-Security/.claude/skills/vet-repo ~/.claude/skills/
cp -r AI-Agent-Security/.claude/skills/scan-skill ~/.claude/skills/
cp -r AI-Agent-Security/.claude/skills/audit-code ~/.claude/skills/
```

### Usage

Once installed, invoke in any Claude Code session:

```
/vet-repo              # Scan current repo's agent configs
/scan-skill <dir>      # Analyze a skill before installing it
/audit-code [path]     # Security review of project code (defaults to project root)
```

### Prerequisites

- **Python 3.10+** -- scanner scripts use stdlib only, no third-party packages
- **Claude Code** -- skills are invoked via `/skill-name` in a Claude Code session

### Hooks

Advisory `PreToolUse` guards in `.claude/settings.json` that warn (not block) on:

- **Bash**: pipe-to-shell, `rm -rf /`, `chmod 777`, eval with variables, base64-to-execution
- **Write**: writes to `~/.ssh/`, `~/.aws/`, `.claude/settings.json`, shell profiles

To install the hooks, copy `.claude/settings.json` into your project's `.claude/` directory.

### Shared Pattern Database

70+ detection patterns across 10 categories. Each skill bundles its own copy of `patterns.py` so it works standalone:

```
skill_injection | hook_abuse | mcp_config | secrets | dangerous_calls
exfiltration | encoding_obfuscation | instruction_override | supply_chain | file_permissions
```

All patterns derived from the research notes and examples in this repo.

---

## 📁 Project Structure

```
AI-Agent-Security/
├── 📄 README.md
├── 📝 notes/                           # Research writeups and analysis
├── 🧪 examples/                        # Annotated attack/defense pairs
└── 🔧 .claude/
    ├── settings.json                    # Hook configurations
    └── skills/
        ├── vet-repo/                    # Repository agent config scanner
        │   ├── SKILL.md
        │   └── scripts/
        │       ├── patterns.py          # Pattern database
        │       └── vet_repo.py
        ├── scan-skill/                  # Individual skill analyzer
        │   ├── SKILL.md
        │   └── scripts/
        │       ├── patterns.py          # Pattern database
        │       └── scan_skill.py
        └── audit-code/                  # Code security auditor
            ├── SKILL.md
            └── scripts/
                ├── patterns.py          # Pattern database
                └── audit_code.py
```

---

## ⚠️ Disclaimer

This research is for **educational and defensive purposes only**. All examples use defanged URLs (`hxxps://`, `[.]`), annotated payloads marked `[MALICIOUS]`, and non-executable demonstrations. Every attack technique includes corresponding defenses.

---

## 📜 License

MIT
