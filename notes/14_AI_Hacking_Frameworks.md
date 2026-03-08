# AI Hacking Frameworks and Autonomous Offensive Security

> **Related notes**: [15 -- Bullshit Benchmark & LLM Honesty](15_Bullshit_Benchmark_And_LLM_Honesty.md) (reliability failures that create attack surfaces), [16 -- AI Blue Teaming & Defensive AI](16_AI_Blue_Teaming_And_Defensive_AI.md) (the defensive counterpart), [13 -- AI Application Ecosystem Security](13_AI_Application_Ecosystem_Security.md) (broader ecosystem context)

## Overview

AI-powered offensive security has evolved from simple ML classification (pre-2024) through LLM chat wrappers (2024) to fully autonomous multi-agent exploitation systems (2025-2026). The field splits into two categories: **hacking WITH AI** (using LLMs as the attacker) and **hacking OF AI** (red-teaming LLM systems themselves). Both are converging as AI agents become both attacker and target.

---

## Autonomous Offensive Platforms

Commercial and commercial-tier open-source platforms that autonomously discover and exploit vulnerabilities.

### XBOW

- **Source**: https://xbow.com (closed source)
- **Funding**: $117M total ($75M Series B from Sequoia, Altimeter)
- **Founded by**: Oege de Moor (GitHub veteran)

The most well-funded and highest-impact platform in this space. Thousands of independent agents run real attacks simultaneously against web applications.

**Key achievement**: #1 on the global HackerOne leaderboard, outperforming thousands of human hackers. Discovered 1,400+ zero-day vulnerabilities (54 critical, 242 high, 524 medium) in a single reporting period (April-June 2025). 80x faster than manual teams -- "Pentest On-Demand" delivers results within 5 business days vs traditional 35-100 day timelines.

Presented at Black Hat 2025. Ran live against real HackerOne targets on stage. Nat Friedman called it "somewhat terrifying." Also maintains the XBOW Benchmark used to evaluate other tools.

### Shannon (KeygraphHQ)

- **Source**: https://github.com/KeygraphHQ/shannon
- **Stars**: ~27,800 | **Language**: TypeScript | **License**: AGPL-3.0

Fully autonomous white-box web application pentester built on Anthropic's Claude Agent SDK. Takes a target URL and source code repository, autonomously discovers and **exploits** vulnerabilities, produces a pentester-grade report with reproducible PoCs.

**Architecture**: 11 specialized agents across 5 sequential phases (Pre-Recon, Recon via Playwright, parallel Vulnerability Analysis per OWASP category, parallel Exploitation, Reporting). Strict **"No Exploit, No Report"** policy -- unconfirmed hypotheses are discarded.

**Key innovations**: White-box + black-box hybrid (reads source to guide attack strategy, validates dynamically). Multi-model cost optimization (Haiku for summarization, Sonnet for analysis, Opus for deep reasoning). 96.15% success rate on the hint-free, source-aware XBOW Benchmark. ~$50/run, ~1-1.5 hours.

Shannon Lite (AGPL-3.0) is open-source; Shannon Pro adds LLM-powered data flow analysis (inspired by the LLMDFA paper, https://arxiv.org/abs/2402.10754).

### PentestGPT (Commercial)

- **Source**: https://pentestgpt.com

Evolved from the original academic PentestGPT project into a commercial autonomous penetration testing platform. Three self-interacting modules -- reasoning, generation, and parsing -- that maintain testing context and execute complex attack chains.

**Privacy concern**: Prompts go to external API servers. Local model support available to mitigate.

---

## Tier 2: Active Open-Source Projects

### Strix

- **Source**: https://github.com/usestrix/strix
- **Stars**: ~20,700 | **Language**: Python | **License**: Apache-2.0

Open-source AI agents that behave like hackers. Multi-agent system where agents work together and adjust tasks dynamically.

**Key capabilities**:
- HTTP proxy for request/response manipulation
- Browser automation for client-side testing (XSS, CSRF)
- Terminal sessions for command injection
- Python environment for custom exploit development

Solved HackTheBox easy machines fully autonomously. All processing happens locally in Docker -- no data leaves the machine. Recommended models: GPT-5 and Claude Sonnet 4.5.

### CAI (Cybersecurity AI) by Alias Robotics

- **Source**: https://github.com/aliasrobotics/cai
- **Stars**: ~7,300 | **Language**: Python

Framework for building and deploying AI-powered automation in offensive and defensive security. Pioneered LLM-powered AI security with the original PentestGPT research.

**Key capabilities**:
- 300+ AI model support (OpenAI, Anthropic, DeepSeek, Ollama)
- Built-in tools for recon, exploitation, privilege escalation
- Tools grouped in 6 categories inspired by the security kill chain
- Human-In-The-Loop (HITL) module as a core design principle

**Achievement**: 3,600x performance improvement over human pentesters in standardized CTF benchmarks. First place among AI teams in "AI vs Human" CTF challenge. Solved medium and 80-90% of hard HackTheBox challenges.

**Commercial tier**: CAI PRO with `alias1` model (500B parameters, zero refusals for authorized security testing, European hosting with GDPR/NIS2 compliance).

**Research output**: 8 academic papers. arXiv: https://arxiv.org/abs/2504.06017

### PentAGI

- **Source**: https://github.com/vxcontrol/pentagi
- **Stars**: ~9,000 | **Language**: Go | **License**: MIT

Fully autonomous AI agent system with microservices architecture and sandboxed Docker execution.

**Architecture**: Multi-agent system with specialized sub-agents (Searcher, Coder, Installer, Pentester). LLM planner orchestrates sequencing. Each sub-agent has access only to tools required for its role. React/TypeScript frontend, Go backend with REST/GraphQL API.

**Key capabilities**:
- 20+ professional security tools (Nmap, Metasploit, SQLmap)
- Knowledge graph via Graphiti/Neo4j for persistent memory across sessions
- Full observability stack (OpenTelemetry, Jaeger, Loki, VictoriaMetrics, Langfuse)
- Each sub-agent permission-scoped, all offensive operations in isolated Docker containers

### Reaper (Ghost Security)

- **Source**: https://github.com/ghostsecurity/reaper
- **Stars**: ~830 | **Language**: Go | **License**: Apache-2.0

Unified application security testing framework designed to work alongside AI agents. Bridges manual pentesting with AI-agent-driven workflows. Intercepts in-scope traffic, logs to local database, provides CLI for searching/inspecting captured data.

**Design philosophy**: "Reaper doesn't replace the pentester -- it enhances their work." More of an AI-augmented toolkit than a fully autonomous agent.

### Nebula (Beryllium Security)

- **Source**: https://github.com/berylliumsec/nebula
- **Language**: Python | **License**: BSD-2-Clause

AI-powered penetration testing assistant automating recon, note-taking, and vulnerability analysis. Middle ground between chat advisors and fully autonomous agents. "Like having a junior pentester in your terminal."

Features Deep Application Profiler (DAP) for zero-day malware detection via neural network behavioral analysis. Commercial tier (Nebula Pro) adds autonomous mode and code analysis.

---

## Tier 3: Older / RL-Based Tools

### AutoPentest-DRL

- **Source**: https://github.com/crond-jaist/AutoPentest-DRL

Pre-LLM era automated penetration testing using Deep Reinforcement Learning. Uses RL engine to select optimal attack sequences from MulVAL attack graphs. Integrates Nmap and Metasploit.

Important historically but less capable than LLM-based successors. Research project from JAIST (Japan).

### GyoiThon

ML-based intelligence gathering tool for web servers. Identifies products (CMS, web server, frameworks) via machine learning, then runs Metasploit modules. Narrower scope than newer LLM frameworks.

---

## Academic / Research Frameworks

### CHECKMATE (December 2025)

- **Paper**: https://arxiv.org/abs/2512.11143

Integrates LLM agents with classical AI planning using a Planner-Executor-Perceptor (PEP) design paradigm. Predefined attack actions encode Metasploit modules, NSE scripts, and Nuclei templates as structured command templates with parameter placeholders.

**Key innovation**: Neuro-symbolic hybrid -- classical planner provides built-in logical reasoning that offloads complex multi-step reasoning from the LLM.

**Results**: Outperforms Claude Code by 20%+ on benchmarks while cutting time and monetary costs by 50%+. In one demonstration, selected a Metasploit module for CVE-2023-46604 and obtained a root shell.

**Significance**: Shows that pure LLM approaches are suboptimal. Hybrid neuro-symbolic is the cutting edge.

### xOffense (September 2025)

- **Paper**: https://arxiv.org/abs/2509.13021

Multi-agent pentesting framework using a fine-tuned Qwen3-32B model. Shifts pentesting from expert-driven manual work to fully automated machine-executable workflows.

**Key innovation**: Mid-scale open-source LLM rather than massive commercial models. Fine-tuned on Chain-of-Thought penetration testing data. Supports local deployment, fine-tuning, and quantization (AWQ/INT4) -- suitable for air-gapped environments.

**Results**: 79.17% sub-task completion rate on AutoPenBench, surpassing VulnBot and PentestGPT. Fine-tuning improved base model performance from 52.36% to 79.17%.

### HackSynth (December 2024)

- **Source**: https://github.com/aielte-research/HackSynth
- **Paper**: https://arxiv.org/abs/2412.01778
- **Stars**: ~293 | **License**: AGPL-3.0

LLM agent and evaluation framework for autonomous penetration testing. Dual-module architecture: Planner (generates commands) and Summarizer (parses state).

**Key contribution**: Proposed two new CTF-based benchmark sets (PicoCTF and OverTheWire) with 200 challenges. Best results with GPT-4o, outperforming what GPT-4o's own system card suggested.

### HackingBuddyGPT

Interactive AI pentesting guide with educational focus. Logs interactions to a database. Supports local models. Educational angle: for teams where pentesters are new to some areas, the interactive guidance is as valuable as pure automation.

---

## Red-Teaming AI Systems (Hacking OF AI)

### Garak (NVIDIA)

Generative AI Red-teaming and Assessment Kit. 37+ probe modules covering prompt injection, jailbreaks, data leakage, hallucination, toxicity, encoding-based attacks. 23 generator backends (OpenAI, Anthropic, HuggingFace, local models). Active and well-maintained with NVIDIA backing.

### Promptfoo

- **Source**: https://www.promptfoo.dev

LLM evaluation and red teaming CLI with 300,000+ developers. 50+ vulnerability types including prompt injection, jailbreaking, PII leakage, hallucination. YAML-based test configurations for CI/CD integration. Compliance mapping to OWASP, NIST, MITRE ATLAS, EU AI Act. Open-source core with commercial tier.

### PyRIT (Microsoft)

Python Risk Identification Tool for generative AI. Specializes in multi-turn and multi-modal attack techniques. Key techniques: Crescendo attacks (gradual escalation over 5-20 turns), TAP (Tree of Attacks with Pruning). Enterprise-grade, backed by Microsoft's AI security team.

### FuzzyAI (CyberArk)

Automated LLM fuzzing. Generates adversarial prompts to test AI systems for jailbreaks and security vulnerabilities. Open-source from an established security vendor.

### DeepTeam / DeepEval (November 2025)

Applies jailbreaking and prompt injection techniques to probe LLM systems before deployment.

### Giskard

Automates adversarial testing probing ML models for model extraction, evasion, data poisoning, and unintended bias. Test orchestration engine deploys thousands of attack variations.

---

## Benchmarks and Competitions

### XBOW Benchmark
Shannon Lite achieved 96.15% success rate on the hint-free, source-aware version. XBOW itself solved 75%+ of industry-standard web security benchmarks.

### AutoPenBench
33 penetration testing tasks (22 in-vitro, 11 real-world CVEs). Used by xOffense and CHECKMATE for evaluation.

### Wiz Research: AI Agents vs. Humans (2026)
- **Source**: https://www.wiz.io/blog/ai-agents-vs-humans-who-wins-at-web-hacking-in-2026
- Tested Claude Sonnet 4.5, GPT-5, Gemini 2.5 Pro on 10 lab challenges modeled after real prevented breaches
- **Result**: AI won 9/10 challenges, all for less than $10 per exploit
- **Caveat**: When given broad scope with no guidance, performance decreased and cost increased 2-2.5x. AI agents "spread efforts haphazardly" while human testers prioritize promising leads
- Claude cracked a multi-step auth bypass in 23 moves

### DARPA AIxCC
Autonomous AI systems securing open-source software at DEF CON 2025. Teams discovered 86% of synthetic vulnerabilities and patched 68% across 54M lines of code. See [note 16](16_AI_Blue_Teaming_And_Defensive_AI.md#darpa-ai-cyber-challenge-aixcc) for full analysis.

### UK AISI / Gray Swan Challenge
1.8 million attacks across 22 models. **Every model broke.** No current frontier system resists determined, well-resourced attacks.

### Anthropic at Competitions
Anthropic entered Claude into 7 major cybersecurity competitions. Claude often landed in the top quarter, matched elite human teams on simple challenges, but lagged on the hardest problems. Got derailed by ASCII art.

---

## Architecture Patterns

Nearly every serious framework converges on the same design:

1. **Multi-agent orchestration**: Specialized agents for recon, analysis, exploitation, reporting
2. **Tool integration**: Nmap, Metasploit, SQLmap, Subfinder wrapped as callable tools
3. **Sandboxed execution**: Docker containers as the primary containment boundary
4. **Proof-by-exploitation**: Findings require actual exploit execution, not just static detection
5. **Iterative feedback loops**: Agent observes results, adjusts strategy, retries

### Attack Surfaces Covered

| Surface | Tools |
|---------|-------|
| Web applications (OWASP Top 10) | Shannon, XBOW, Strix, CAI, PentAGI |
| API security | Shannon, XBOW, Strix |
| Network infrastructure | PentAGI, CAI, AutoPentest-DRL, CHECKMATE |
| Active Directory | CAI (Kerberos, Golden/Silver tickets) |
| CTF challenges | HackSynth, CAI, Strix |
| LLM/AI systems | Garak, Promptfoo, PyRIT, FuzzyAI |

---

## Evolution Timeline

1. **Pre-2024**: RL-based approaches (AutoPentest-DRL), ML classification (GyoiThon), simple recon automation
2. **2024**: LLM wrappers and chat assistants (PentestGPT original, HackingBuddyGPT). Proof-of-concept phase. HackSynth establishes evaluation methodology
3. **2025**: Multi-agent architectures with tool integration. Shannon, Strix, PentAGI, CAI emerge. XBOW hits #1 on HackerOne. Architecture matures from "LLM advice" to executable pipelines
4. **2026**: Consolidation and commercialization. Benchmark-driven evaluation standard. Neuro-symbolic hybrids (CHECKMATE) emerge. Open-source core + commercial pro becomes dominant model

---

## Key Technical Debates

- **LLM-only vs. neuro-symbolic**: CHECKMATE demonstrates classical planning + LLM outperforms pure LLM by 20%+. Neural networks prune the search space; symbolic engines solve constraints.
- **Commercial APIs vs. local models**: xOffense shows fine-tuned Qwen3-32B (local, quantized) can match larger commercial models. Critical for air-gapped/regulated environments.
- **Full autonomy vs. HITL**: CAI explicitly builds Human-In-The-Loop as a core design principle. Nebula provides interactive mode. Most experts still recommend human oversight.
- **Open-source vs. commercial**: Shannon (AGPL), CAI (custom), Nebula (BSD) all follow open core + commercial pro. XBOW remains fully closed.

---

## Defense Implications

What these offensive frameworks tell defenders:

- **The annual pentest is dead.** Continuous AI-powered testing means defenders need continuous AI-powered defense. CI/CD-integrated security testing becomes mandatory.
- **AI attackers are fast and cheap.** Wiz Research: 9/10 challenges solved for under $10. XBOW: 80x faster than manual teams. Volume-based attacks at near-zero marginal cost.
- **Source code exposure dramatically increases risk.** Shannon's white-box approach shows source access enables vastly more effective attacks. Defense-in-depth must assume the attacker has read the code.
- **AI struggles with strategic prioritization.** The Wiz study showed agents "spread efforts haphazardly." Defenders can exploit this with deception (honeypots, canary tokens) to waste AI cycles.
- **Complex auth and business logic remain harder for AI.** Pattern matching (SQLi, XSS) is easy; business logic flaws requiring domain understanding are still hard.
- **The swarm model is coming.** PentAGI and XBOW move toward parallel multi-agent swarms. Defenders must prepare for coordinated, multi-vector attacks at machine speed.

For the full defensive AI landscape, tools, and strategies, see [note 16](16_AI_Blue_Teaming_And_Defensive_AI.md). For regulatory frameworks (EU AI Act, NIST, OWASP), see [note 08](08_AI_GRC_And_Policy_Landscape.md).

---

## Summary Table

| Tool | Type | Maturity | License | Stars | Key Innovation |
|------|------|----------|---------|-------|----------------|
| Shannon | Autonomous web pentester | Commercial + OSS | AGPL-3.0 | ~27,800 | Proof-by-exploitation, Claude Agent SDK |
| XBOW | Autonomous offensive platform | Commercial | Closed | N/A | #1 HackerOne, $117M funded |
| Strix | Autonomous AI hackers | Active OSS | Apache-2.0 | ~20,700 | Multi-agent, HackTheBox solver |
| PentAGI | Autonomous pentest system | Active OSS | MIT | ~9,000 | Knowledge graph, sandboxed Docker |
| CAI | Cybersecurity AI framework | Commercial + OSS | Custom | ~7,300 | 3,600x human performance, 8 papers |
| Reaper | AI-augmented pentest toolkit | Active OSS | Apache-2.0 | ~830 | Unified workflow, agent-friendly |
| Nebula | AI pentest assistant | Active OSS | BSD-2 | N/A | Interactive HITL, local models |
| CHECKMATE | Neuro-symbolic pentest | Research paper | N/A | N/A | Classical planning + LLM hybrid |
| xOffense | Local-model pentesting | Research paper | N/A | N/A | Fine-tuned Qwen3-32B, air-gap capable |
| HackSynth | LLM agent + eval framework | Research | AGPL-3.0 | ~293 | CTF benchmarks, dual-module arch |
| Garak | LLM vulnerability scanner | Active OSS (NVIDIA) | OSS | N/A | 37+ probe modules, 23 backends |
| Promptfoo | LLM red teaming CLI | Commercial + OSS | OSS | N/A | 50+ vuln types, compliance mapping |
| PyRIT | AI risk identification | Active OSS (Microsoft) | OSS | N/A | Multi-turn/multi-modal attacks |
| FuzzyAI | LLM fuzzing | Active OSS (CyberArk) | OSS | N/A | Automated adversarial prompt generation |
