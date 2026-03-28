# Tools, Frameworks, and Benchmarks Index

Quick reference for every tool, framework, benchmark, and standard mentioned across this research project. Organized by category, not by the note that introduced it.

---

## Offensive Security Tools (Hacking WITH AI)

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| XBOW | Autonomous offensive platform; #1 HackerOne; $117M funded; 80x faster than manual teams | https://xbow.com | [14](14_AI_Hacking_Frameworks.md) |
| Shannon | White-box autonomous web pentester; 11 agents, 5 phases; Claude Agent SDK; proof-by-exploitation | https://github.com/KeygraphHQ/shannon | [14](14_AI_Hacking_Frameworks.md) |
| PentestGPT | Commercial autonomous pentest platform; 3 self-interacting modules | https://pentestgpt.com | [14](14_AI_Hacking_Frameworks.md) |
| Strix | Open-source AI hacker agents; solves HackTheBox; local Docker execution | https://github.com/usestrix/strix | [14](14_AI_Hacking_Frameworks.md) |
| CAI | Cybersecurity AI framework; 300+ models; 8 papers; 3,600x human perf claim | https://github.com/aliasrobotics/cai | [14](14_AI_Hacking_Frameworks.md), [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| PentAGI | Multi-agent pentest system; knowledge graph; sandboxed Docker; Go backend | https://github.com/vxcontrol/pentagi | [14](14_AI_Hacking_Frameworks.md) |
| Reaper | AI-augmented pentest toolkit; traffic interception; agent-friendly | https://github.com/ghostsecurity/reaper | [14](14_AI_Hacking_Frameworks.md) |
| Nebula | AI pentest assistant; interactive HITL; Deep Application Profiler | https://github.com/berylliumsec/nebula | [14](14_AI_Hacking_Frameworks.md) |
| AutoPentest-DRL | Pre-LLM; Deep RL-based automated pentesting; MulVAL attack graphs | https://github.com/crond-jaist/AutoPentest-DRL | [14](14_AI_Hacking_Frameworks.md) |
| GyoiThon | ML-based web server recon; product identification via ML | GitHub | [14](14_AI_Hacking_Frameworks.md) |
| CHECKMATE | Neuro-symbolic; classical planning + LLM; beats pure LLM by 20%+ | https://arxiv.org/abs/2512.11143 | [14](14_AI_Hacking_Frameworks.md) |
| xOffense | Fine-tuned Qwen3-32B; air-gap capable; 79.17% on AutoPenBench | https://arxiv.org/abs/2509.13021 | [14](14_AI_Hacking_Frameworks.md) |
| HackSynth | LLM agent + eval framework; PicoCTF/OverTheWire benchmarks | https://github.com/aielte-research/HackSynth | [14](14_AI_Hacking_Frameworks.md) |
| HackingBuddyGPT | Interactive AI pentest guide; educational focus | GitHub | [14](14_AI_Hacking_Frameworks.md) |

## AI Red-Teaming Tools (Hacking OF AI)

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| Garak | NVIDIA; 37+ probe modules; 23 backends; prompt injection/jailbreak/data leakage testing | Open-source (NVIDIA) | [14](14_AI_Hacking_Frameworks.md), [17](17_Unicode_Variation_Selector_Attacks.md) |
| Promptfoo | 300K+ devs; 50+ vuln types; YAML CI/CD; OWASP/NIST/MITRE compliance mapping | https://www.promptfoo.dev | [14](14_AI_Hacking_Frameworks.md), [17](17_Unicode_Variation_Selector_Attacks.md) |
| ASCII Smuggler | Encode/decode hidden text via Tags block and variation selectors | [embracethered.com](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/) | [17](17_Unicode_Variation_Selector_Attacks.md) |
| noseeum | Offensive framework for Unicode steganography and VS-based jailbreaking | [GitHub](https://github.com/umpolungfish/noseeum) | [17](17_Unicode_Variation_Selector_Attacks.md) |
| PyRIT | Microsoft; multi-turn/multi-modal; Crescendo attacks; TAP | Open-source (Microsoft) | [14](14_AI_Hacking_Frameworks.md) |
| FuzzyAI | CyberArk; automated LLM fuzzing; adversarial prompt generation | Open-source (CyberArk) | [14](14_AI_Hacking_Frameworks.md) |
| DeepTeam / DeepEval | Jailbreaking + prompt injection probing before deployment | Open-source | [14](14_AI_Hacking_Frameworks.md) |
| Giskard | Adversarial ML testing; model extraction/evasion/poisoning/bias | Open-source | [14](14_AI_Hacking_Frameworks.md) |
| Augustus | LLM security testing; 190+ probes; 28 providers | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Cisco MCP Scanner | Finding exposed or weak MCP servers | Open-source (Cisco) | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |

## Defensive AI Platforms (Commercial)

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| CrowdStrike Charlotte AI | Multi-model; "governed autonomy"; policy-gated agentic response | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Microsoft Security Copilot | Defender/Sentinel/Azure integration; 65T+ daily signals | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| SentinelOne Purple AI | NL queries over Singularity Data Lake; adaptive reasoning | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Palo Alto Cortex XSIAM | AI-driven SecOps; MTTR under 10 min; Google Cloud/Gemini partnership | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Vectra AI | Supervised + unsupervised ML NDR; 85%+ noise reduction; 35 AI patents | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Darktrace | Unsupervised "Self-Learning AI" anomaly detection; encrypted flow monitoring | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Stellar Cyber | Open XDR; broadest coverage (network, endpoint, identity, apps) | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Dropzone AI | AI SOC analyst; analyzes every alert in <10 min; 85+ tool integrations | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Prophet Security | Agentic AI SOC analyst; <3 min investigation; shows reasoning chain | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |

## AI Malware Analysis / Vulnerability Discovery

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| Microsoft Project Ire | Autonomous malware reverse engineering; angr + Ghidra; 0.98 precision | Microsoft Research | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| OpenAI Aardvark | GPT-5 autonomous vuln scanner + patcher; 92% recall; 10 CVEs found | https://openai.com/index/introducing-aardvark/ | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Booz Allen Vellox Reverser | Peer-to-peer AI agent malware analysis network | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| CodeHunter | Static + dynamic + AI malware analysis; MITRE-mapped reporting | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Google CodeMender | Detecting, patching, rewriting vulnerable code | Google | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |

## AI-Powered SAST / Code Security

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| Semgrep | AI-learned code context; 95% reviewer validation rate | https://semgrep.dev | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Snyk DeepCode AI | 25M+ data flow cases; 19+ languages; risk scoring | https://snyk.io | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Checkmarx AI Query Builder | Up to 90% FP reduction; 90% faster scans | https://checkmarx.com | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Mend SAST | +38% precision, +48% recall vs benchmarks | https://mend.io | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Veracode | <1.1% FP rate; reachability analysis | https://veracode.com | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Fortify Aviator | LLM-powered classification and code fix proposals | Commercial | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |

## LLM Guardrails / Input Protection

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| LLM Guard | Comprehensive security toolkit for LLM interactions | Protect AI | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Vigil-LLM | Prompt injection and jailbreak detector | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Rebuff | Self-hardening prompt injection detector | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| PurpleLlama | LLM security assessment and improvement | Meta | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| PromptGuard | Direct jailbreak and indirect injection detection | Meta | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Guardrail.ai | Structure, type, and quality guarantees for LLM outputs | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Lakera Guard | LLM protection middleware; instruction drift detection | Commercial | [07](07_Skill_Scanning_And_Detection_Landscape.md), [12](12_OpenClaw_And_ClawHub_Security.md) |

## Open-Source SIEM / SOAR / Threat Intel

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| Wazuh | Unified XDR and SIEM; Suricata/VirusTotal/YARA integration | https://wazuh.com | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Shuffle | SOAR platform; 2,500+ app integrations; Wazuh partnership | https://github.com/Shuffle/Shuffle | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| TheHive | Incident response and case management | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| IntelOwl | Threat intelligence automation; indicator enrichment | Open-source (Honeynet) | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| DIANA | LLM-powered detection engineering; threat intel to detection logic | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| DarkHuntAI | Multi-agent AI threat hunting; executable SIEM queries | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| Splunk DECEIVE | AI-powered honeypot; contextually appropriate deception | Open-source (Splunk) | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |

## Adversarial ML Defense

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| IBM ART | Adversarial Robustness Toolbox; evasion/poisoning/extraction/inference defense | Linux Foundation | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| AIDEFEND Framework | Defensive countermeasure knowledge base; MITRE ATLAS/MAESTRO/OWASP mapped | Open-source | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| A2AS Framework | Runtime agent protection; source verification, sandboxing, defensive prompts | Open-source | [21](21_Multi_Agent_Security.md) |

## Specialized Security LLMs

| Model | Description | Notes |
|-------|-------------|-------|
| Foundation-Sec-8B-Reasoning | Open-weight 8B instruction-tuned security LLM | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| VulnLLM-R-7B | 7B reasoning LLM; outperforms Claude-3.7-Sonnet on vuln detection | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |

## Token Abuse Defense / Cost Management

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| LiteLLM | Cost-aware rate limiting proxy; token budgeting; per-key spend caps | https://docs.litellm.ai | [19](19_Token_Based_Attacks_And_Resource_Exploitation.md) |
| RouteLLM | Model routing framework; cost optimization via complexity classification | https://github.com/lm-sys/RouteLLM | [18](18_Token_Optimization_And_LLM_Efficiency.md), [20](20_LLM_Landscape_Tokens_And_Pricing.md) |
| LLMLingua-2 | Prompt compression via BERT token classification; 3-6x faster; reduces DoW attack surface | https://github.com/microsoft/LLMLingua | [18](18_Token_Optimization_And_LLM_Efficiency.md) |

## Skill / Agent Config Scanning

| Tool | Description | Source | Notes |
|------|-------------|--------|-------|
| vet-repo (this project) | Scans repository agent configs for malicious patterns | [skills/vet-repo](../.claude/skills/vet-repo/) | [07](07_Skill_Scanning_And_Detection_Landscape.md) |
| scan-skill (this project) | Deep security analysis of individual skills | [skills/scan-skill](../.claude/skills/scan-skill/) | [07](07_Skill_Scanning_And_Detection_Landscape.md) |
| audit-code (this project) | Code security review; secrets, dangerous calls, OWASP | [skills/audit-code](../.claude/skills/audit-code/) | [07](07_Skill_Scanning_And_Detection_Landscape.md) |
| Cisco AI Defense Scanner | Skill security scanner from Cisco | Open-source (Cisco) | [07](07_Skill_Scanning_And_Detection_Landscape.md) |
| Invariant Labs MCP Scan | MCP server security scanner | Open-source | [13](13_AI_Application_Ecosystem_Security.md) |
| Membranes | Policy enforcement layer for AI tool access | Open-source | [07](07_Skill_Scanning_And_Detection_Landscape.md) |

---

## Benchmarks and Competitions

### Offensive / Cybersecurity Benchmarks

| Benchmark | What It Measures | Notes |
|-----------|-----------------|-------|
| XBOW Benchmark | Web application vulnerability discovery rate | [14](14_AI_Hacking_Frameworks.md) |
| AutoPenBench | 33 pentest tasks (22 in-vitro, 11 real CVEs) | [14](14_AI_Hacking_Frameworks.md) |
| Wiz AI vs Humans | AI agent performance on 10 real-world-modeled web challenges | [14](14_AI_Hacking_Frameworks.md) |
| DARPA AIxCC | Autonomous vulnerability discovery + patching at scale | [14](14_AI_Hacking_Frameworks.md), [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| UK AISI / Gray Swan | 1.8M attacks across 22 models (every model broke) | [14](14_AI_Hacking_Frameworks.md) |
| Agent Security Bench (ASB) | 27 attack types across 13 LLM backbones; multi-agent security; 84.30% max ASR | [21](21_Multi_Agent_Security.md) |
| BAD-ACTS | 188 scenarios in 4 agentic environments; communication-based attacks; 80% ASR | [21](21_Multi_Agent_Security.md) |

### LLM Honesty / Reliability Benchmarks

| Benchmark | What It Measures | Notes |
|-----------|-----------------|-------|
| BullshitBench v2 | Nonsense premise detection and pushback (100 prompts, 13 techniques) | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| TruthfulQA | Human misconception reproduction (817 questions, 38 topics) | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| SimpleQA / SimpleQA Verified | Short-form factual accuracy + confidence calibration | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| FELM | Segment-level factuality across 5 domains | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| FACTS Grounding | Response grounding in provided source documents | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| Vectara Hallucination Leaderboard | Hallucination rate during document summarization | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| FaithBench | Human-annotated hallucination in summarization | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| HaluEval | LLM ability to recognize hallucinated content | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| HalluLens | Extrinsic + intrinsic hallucinations; dynamic test sets | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| Bullshit Index (Machine Bullshit) | LLM truth-indifference quantification (Princeton) | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| AbstentionBench | LLM ability to refuse unanswerable queries | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| Confabulation Leaderboard | Non-existent answers to misleading RAG questions | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| Semantic Entropy | Meaning-level uncertainty detection (Nature 2024) | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |

### Sycophancy Benchmarks

| Benchmark | What It Measures | Notes |
|-----------|-----------------|-------|
| SycEval | Sycophancy in math/medical domains (Stanford) | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| ELEPHANT | Social sycophancy / "face" preservation | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| BrokenMath | Sycophancy in theorem proving with perturbed problems | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| Syco-Bench | Four-part sycophancy benchmark (Picking Sides, Mirroring, etc.) | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |
| Spiral-Bench | Sycophancy and delusion reinforcement in 20-turn conversations | [15](15_Bullshit_Benchmark_And_LLM_Honesty.md) |

### Writing Quality Benchmarks

| Benchmark | What It Measures | Notes |
|-----------|-----------------|-------|
| EQ-Bench Creative Writing | Narrative quality, emotional depth, prose style; Elo ranking | [20](20_LLM_Landscape_Tokens_And_Pricing.md) |
| WritingBench | 6 domains (academic, finance, law, literature, education, advertising); 1,239 queries | [20](20_LLM_Landscape_Tokens_And_Pricing.md) |
| LongGenBench | Long-form generation quality at 16K-32K tokens; coherence + instruction adherence | [20](20_LLM_Landscape_Tokens_And_Pricing.md) |

### Code Performance Benchmarks

| Benchmark | What It Measures | Notes |
|-----------|-----------------|-------|
| AutoCodeBench | LLM code generation across 20 languages | [05](05_AI_Coding_Language_Performance.md) |

---

## Standards and Frameworks

| Framework | Description | Notes |
|-----------|-------------|-------|
| OWASP LLM Top 10 | Top 10 LLM security risks | [08](08_AI_GRC_And_Policy_Landscape.md), [13](13_AI_Application_Ecosystem_Security.md) |
| OWASP Agentic Top 10 | Top 10 agentic AI security risks | [08](08_AI_GRC_And_Policy_Landscape.md), [13](13_AI_Application_Ecosystem_Security.md) |
| MITRE ATLAS | Adversarial threat landscape for AI systems | [08](08_AI_GRC_And_Policy_Landscape.md), [13](13_AI_Application_Ecosystem_Security.md) |
| NIST AI RMF | AI Risk Management Framework | [08](08_AI_GRC_And_Policy_Landscape.md) |
| NIST AI 100-2 E2025 | Adversarial Machine Learning taxonomy (updated March 2025) | [16](16_AI_Blue_Teaming_And_Defensive_AI.md) |
| EU AI Act | European AI regulation; adversarial testing requirements | [08](08_AI_GRC_And_Policy_Landscape.md) |
| ISO 42001 | AI Management System standard | [08](08_AI_GRC_And_Policy_Landscape.md) |

---

## Curated Resource Lists

| Repository | Description |
|-----------|-------------|
| awesome-ai-security | https://github.com/ottosulin/awesome-ai-security |
| awesome-llm-security | https://github.com/corca-ai/awesome-llm-security |
| awesome-ai-cybersecurity | https://github.com/ElNiak/awesome-ai-cybersecurity |
| Awesome-LLM4Cybersecurity | https://github.com/tmylla/Awesome-LLM4Cybersecurity |
| oss-llm-security | https://github.com/kaplanlior/oss-llm-security |
| awesome-hallucination-detection | https://github.com/EdinburghNLP/awesome-hallucination-detection |
| LLM-Honesty-Survey | https://github.com/SihengLi99/LLM-Honesty-Survey |
