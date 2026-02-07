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

## 📁 Project Structure

```
AI-Agent-Security/
├── 📄 README.md
├── 📝 notes/            # Research writeups and analysis
├── 🧪 examples/         # Annotated attack/defense pairs
└── 🔧 tools/            # Detection & sanitization scripts (planned)
```

---

## ⚠️ Disclaimer

This research is for **educational and defensive purposes only**. All examples use defanged URLs (`hxxps://`, `[.]`), annotated payloads marked `[MALICIOUS]`, and non-executable demonstrations. Every attack technique includes corresponding defenses.

---

## 📜 License

MIT
