# 🛡️ AI Agent Security Research

> *Documenting how AI coding agents get exploited -- so we can build better defenses.*

[![Educational](https://img.shields.io/badge/Purpose-Educational%20%26%20Defensive-blue)]()
[![AI Agents](https://img.shields.io/badge/Scope-AI%20Coding%20Agents-purple)]()
[![No Live Exploits](https://img.shields.io/badge/Exploits-None%20Executable-green)]()

---

## 🔍 What This Is

A growing collection of research, annotated attack examples, and defense strategies targeting the security of **AI coding agents** -- Claude Code, Cursor, Copilot, Windsurf, and the broader ecosystem of LLM-powered development tools.

Every attack has a defense. Every payload is annotated, defanged, and educational.

---

## 📝 Research Notes

| | Topic | What You'll Learn |
|---|-------|-------------------|
| 🎯 | [Prompt Injection Overview](notes/01_Prompt_Injection_Overview.md) | The foundational attack -- how untrusted input hijacks agent behavior |
| 💉 | [Skill Injection Analysis](notes/02_Skill_Injection_Analysis.md) | Real-world trojanized skill teardown (ZackKorman `security-review` case) |
| 🧱 | [Defense Patterns](notes/03_Defense_Patterns.md) | Sanitization, sandboxing, and mitigation strategies with working code |
| 🔬 | [Research Findings](notes/04_Research_Findings.md) | Cutting-edge attacks (2024-2026): MCP poisoning, memory corruption, vibe coding risks |
| ⚙️ | [Claude Code Skill Architecture](notes/05_Claude_Code_Skill_Architecture.md) | How Claude Code's extensibility (skills, hooks, MCP) creates attack surface |
| 👻 | [LLM Hallucination Prevention](notes/06_LLM_Hallucination_Prevention.md) | Why models invent things, how to detect it, and how to stop it |
| 🌐 | [AI Coding Language Performance](notes/07_AI_Coding_Language_Performance.md) | Multilingual benchmarks, token efficiency, and language-steering attacks |
| 🔓 | [LLM Jailbreaking Deep Dive](notes/08_LLM_Jailbreaking_Deep_Dive.md) | Full taxonomy: DAN to GCG to Crescendo, defenses, benchmarks, agent implications |
| 🔍 | [Skill Scanning & Detection Landscape](notes/09_Skill_Scanning_And_Detection_Landscape.md) | Cisco Skill Scanner, VirusTotal, ToxicSkills audit, gap analysis, what to build next |

---

## 🧪 Attack / Defense Examples

Hands-on annotated scenarios -- each one shows the attack **and** the fix.

| | Technique | TL;DR |
|---|-----------|-------|
| 🕵️ | [Hidden Comment Injection](examples/01_Hidden_Comment_Injection/) | HTML comments are invisible in markdown previews but the LLM reads every word |
| 🌊 | [Indirect Prompt Injection](examples/02_Indirect_Prompt_Injection/) | Poison the web page, API response, or file the agent fetches -- it obeys |
| 📤 | [Data Exfiltration Via Agent](examples/03_Data_Exfiltration_Via_Agent/) | The agent becomes an unwitting mule for your secrets, keys, and credentials |
| 📦 | [Hallucinated Package Injection](examples/04_Hallucinated_Package_Skill_Injection/) | LLM invents a package name, attacker registers it -- instant supply chain attack |

---

## 🗂️ Attack Taxonomy

```
┌─────────────────────────────────────────────────────┐
│                  AI Agent Attacks                    │
├──────────────┬──────────────┬───────────────────────┤
│ 🎯 Injection │ 🔗 Supply    │ 📤 Exfiltration       │
│              │    Chain     │                       │
│ Direct       │ Trojan       │ Secrets & keys        │
│ Indirect     │  skills      │ Source code           │
│ Hidden       │ Hallucinated │ Environment           │
│  comments    │  packages    │  variables            │
│ MCP tool     │ Poisoned     │ Credentials           │
│  poisoning   │  docs        │                       │
│ Language-    │              │                       │
│  steering    │              │                       │
└──────────────┴──────────────┴───────────────────────┘
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
