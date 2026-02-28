# AI GRC and Policy Landscape

## Table of Contents

1. [AI Governance Frameworks](#1-ai-governance-frameworks)
2. [AI Risk Management](#2-ai-risk-management)
3. [AI Compliance -- Regulatory Landscape](#3-ai-compliance----regulatory-landscape)
4. [AI Security in GRC](#4-ai-security-in-grc)
5. [Enterprise AI Governance](#5-enterprise-ai-governance)
6. [Policy Debates](#6-policy-debates)
7. [Emerging Trends -- Agentic AI Governance](#7-emerging-trends----agentic-ai-governance)
8. [Key Organizations and Standards Bodies](#8-key-organizations-and-standards-bodies)
9. [Sources](#9-sources)

---

## 1. AI Governance Frameworks

### NIST AI Risk Management Framework (AI RMF)

The foundational US standard for AI risk management, built around four core functions: **Govern, Map, Measure, Manage**.

- **AI RMF 1.0** released January 2023
- **March 2025 update** expanded to address generative AI, supply chain vulnerabilities, and new attack models -- emphasizes model provenance, data integrity, and third-party model assessment
- **AI 600-1 GenAI Profile** provides 200+ suggested risk management actions specific to generative AI
- **December 2025**: NIST published preliminary draft of the **Cybersecurity Framework Profile for Artificial Intelligence** (Cyber AI Profile), organizing technical guidance around three focus areas:
	1. Securing AI systems
	2. Using AI for cyber defense
	3. Thwarting AI-enabled attacks
- **SP 800-53 "Control Overlays for Securing AI Systems" (COSAiS)** under development -- provides implementation-level guidance complementing the Cyber AI Profile's outcome-oriented approach
- **RMF 1.1** guidance addenda and expanded profiles expected through 2026

The 2025 updates signal organizations must move from planning to **operationalizing** AI risk management. The AI RMF now aligns more closely with cybersecurity and privacy frameworks, simplifying cross-framework compliance.

### ISO/IEC 42001:2023

The first certifiable international AI Management System (AIMS) standard, using a plan-do-check-act (PDCA) structure.

- Published December 2023, remains the current version
- Specifies requirements for establishing, implementing, maintaining, and improving an AIMS
- **76% of organizations** plan to pursue ISO 42001 or similar frameworks (CSA 2025 compliance benchmark)
- Maps well to EU AI Act requirements -- operationalizes legal requirements into governance programs
- Companion standards in the 42000 series under development

### EU AI Code of Practice

Voluntary, near-term route for GPAI providers to meet transparency and related duties under the EU AI Act. ISO 42001 + Code of Practice together describe how to run, evidence, and continuously improve an AI governance program.

### OECD AI Principles

Adopted by 46+ countries. Five principles: inclusive growth, human-centered values, transparency, robustness/security, accountability. Updated periodically with member country adoption tracking.

---

## 2. AI Risk Management

### Risk Categories

AI-specific risk categories span multiple domains:

- **Bias and fairness** -- algorithmic discrimination, training data representation
- **Hallucination and accuracy** -- confabulation, factual errors, citation fabrication
- **Security** -- prompt injection, adversarial attacks, model theft, supply chain compromise
- **Privacy** -- training data leakage, inference attacks, memorization of PII
- **Transparency** -- explainability, auditability, decision traceability
- **Reliability** -- model degradation, distribution shift, edge-case failures
- **Environmental** -- compute costs, energy consumption, sustainability
- **Societal** -- misinformation, deepfakes, job displacement, concentration of power

### Tooling and Processes

- **AI risk assessments** aligned to NIST AI RMF's Govern/Map/Measure/Manage functions
- **Model cards and datasheets** for documentation and transparency
- **Bias testing frameworks** -- IBM AI Fairness 360, Google What-If Tool
- **Red teaming** -- adversarial testing of model safety and security boundaries
- **Continuous monitoring** -- model drift detection, performance metrics tracking
- **Impact assessments** -- required by Colorado AI Act, EU AI Act for high-risk systems

Gartner forecasts **50% growth in GRC tool investment by 2026** as regulatory complexity outpaces manual compliance capabilities.

### Data Quality as Foundation

High-quality data foundation is critical for AI-ready GRC. If risk data is fragmented, siloed, or outdated, AI models produce flawed or biased outcomes. Fixing data architecture is a prerequisite for AI governance programs.

---

## 3. AI Compliance -- Regulatory Landscape

### EU AI Act

The world's first comprehensive AI regulation, adopted June 2024.

**Implementation Timeline:**

| Date | Milestone |
|------|-----------|
| **Feb 2, 2025** | Unacceptable-risk AI systems banned; AI literacy requirements take effect |
| **Aug 2, 2025** | GPAI model rules apply; national authorities designated; EU governance (AI Board, Scientific Panel, Advisory Forum) operational |
| **Aug 2, 2026** | High-risk AI system rules (Annex III) take effect; transparency rules (Art. 50) apply; full enforcement begins |
| **Aug 2, 2027** | GPAI models placed on market before Aug 2025 must be fully compliant |

**Penalties:**
- Up to EUR 35M or 7% global annual turnover for prohibited AI practices
- Up to EUR 15M or 3% global annual turnover for other obligation violations

### United States -- Federal

- **Biden EO 14110** (Oct 2023): Established AI safety and security requirements, later partially rescinded
- **Trump EO** (Dec 11, 2025): Proposes uniform federal AI policy framework that would **preempt state AI laws** deemed inconsistent -- specifically names Colorado AI Act as an example of "excessive State regulation"
- No comprehensive federal AI legislation enacted as of Feb 2026 -- regulation remains fragmented across agencies (FTC, FDA, SEC, etc.)

### United States -- State Level

Explosive state-level activity:

- **2025**: 1,208 AI-related bills introduced across all 50 states; 145 enacted into law; 38 states adopted or enacted ~100 AI-related measures
- **California** (7 new AI laws in 2025):
	- **SB 53** (Frontier AI Transparency Act): Developers of models trained >10^26 FLOPS must publish risk frameworks, report safety incidents within 15 days, implement whistleblower protections. Penalties up to $1M/violation. Effective Jan 1, 2026
	- **SB 942** (AI Transparency Act): Generative AI providers must offer watermarks, latent disclosures, detection tools. Effective Aug 2, 2026
	- Additional laws: Health Care Professions Deceptive Terms Act, Companion Chatbots Act, Preventing Algorithmic Price Fixing Act
	- **AB 316**: Precludes defendants from using AI system autonomous operation as a defense to liability claims. Effective Jan 1, 2026
- **Colorado AI Act** (SB 24-205): Requirements for high-risk AI system deployers -- risk management, disclosures, algorithmic discrimination mitigation. **Delayed to June 2026** (SB 25B-004 signed Aug 28, 2025)
- **Illinois**: AI disclosure law taking effect
- Other active states: New York, Rhode Island, Massachusetts, Vermont

### China

China is building the most prescriptive AI regulatory regime globally:

- **Oct 28, 2025**: Top legislature passed cybersecurity law amendments adding AI provisions -- first time AI enters national law. Effective Jan 1, 2026
- **Jul 26, 2025**: AI Action Plan issued at World AI Conference 2025 -- innovation, infrastructure, open ecosystems, data quality, green AI, standards
- **Aug 22, 2025**: Draft Measures from 10 central regulators on responsible AI innovation, ethical oversight, public interest protection
- **Sep 1, 2025**: AI content labelling measures took effect (Cyberspace Administration)
- Existing: Algorithm Recommendation Regulations (2022), Deep Synthesis Regulations (2023), Generative AI Measures (2023)
- Proposing **World Artificial Intelligence Cooperation Organization (WAICO)** -- a global body to coordinate AI regulation

### United Kingdom

- **No AI-specific legislation** currently in place
- Sector-by-sector approach -- existing regulators interpret and enforce AI principles within their domains
- **AI Safety Institute (AISI)** -- government-backed institute researching AI capabilities, impacts, and risk mitigation
- Principles-first approach with regulatory flexibility

### International Soft Law

- **OECD AI Principles** -- 46+ country adoption
- **UNESCO AI Ethics Recommendation** -- 193 member states
- **G7 Hiroshima AI Process** -- voluntary code of conduct for frontier AI developers
- **Council of Europe AI Convention** -- first legally binding international AI treaty (opened for signature Sep 2024)

---

## 4. AI Security in GRC

### Framework Integration

AI security is increasingly integrated into GRC through complementary frameworks:

| Framework | Focus | AI Security Coverage |
|-----------|-------|---------------------|
| **OWASP Top 10 for LLMs 2025** | Risk taxonomy | Prompt injection (LLM01), insecure output handling, training data poisoning, etc. |
| **OWASP Top 10 for Agentic Applications 2026** | Agent-specific risks | Goal hijacking, tool misuse, memory poisoning, rogue agents (see [Note 11](./11_AI_Memory_And_Corruption.md)) |
| **MITRE ATLAS** | Adversary tactics/techniques | 15 tactics, 66 techniques, 46 sub-techniques, 26 mitigations, 33 case studies (Oct 2025). Added 14 new techniques in 2025 for AI agents |
| **NIST AI RMF + GenAI Profile** | Risk management | 200+ risk actions, supply chain assessment, model provenance |
| **NIST Cyber AI Profile** | Cybersecurity | Securing AI systems, AI for defense, thwarting AI attacks |
| **ISO 42001** | Management system | Certifiable AIMS with controls for AI lifecycle |

### Prompt Injection in GRC Context

Prompt injection (OWASP LLM01 / ATLAS AML.T0051) remains the #1 ranked LLM risk. ATLAS distinguishes:
- **Direct prompt injection** -- malicious content in user input
- **Indirect prompt injection** -- malicious content in external data sources the LLM processes

Both map to GRC controls around input validation, output filtering, privilege separation, and monitoring.

### AI Supply Chain Security

The March 2025 NIST AI RMF update recognizes that most organizations rely on external or open-source AI components. Supply chain risks include:
- Poisoned training data
- Backdoored models
- Compromised fine-tuning pipelines
- Malicious tools and plugins (MCP servers, skills)
- Tampered model weights

---

## 5. Enterprise AI Governance

### Program Components

**77% of organizations** are actively developing AI governance programs (IAPP 2025 AI Governance Profession Report), with 47% ranking it among their top five strategic priorities.

Core components of enterprise AI governance:

1. **AI Use Case Inventory** -- comprehensive registry of all AI applications including shadow AI (unapproved employee tools)
2. **Model Registry** -- track versions, evaluation summaries, lineage across datasets and pipelines (e.g., Databricks Unity Catalog + MLflow)
3. **Risk Assessment** -- classify AI systems by risk level aligned to regulatory categories
4. **Policy Framework** -- living documents reviewed quarterly as capabilities and regulations evolve
5. **Ethics Board / AI Governance Committee** -- cross-functional oversight with authority to approve/reject AI deployments
6. **Audit Trail** -- who performed each action, when, and with what parameters (required by HIPAA, GDPR, SOX, EU AI Act)
7. **Continuous Monitoring** -- model performance, drift detection, bias metrics, incident tracking
8. **Incident Response** -- AI-specific incident procedures (California SB 53 requires 15-day reporting)

### Shadow AI

A growing concern: employees using unapproved AI tools (ChatGPT, Claude, Copilot) without organizational governance. Enterprise programs must inventory and address shadow AI usage through acceptable use policies and approved tool catalogs.

### Shift from Reactive to Proactive

GRC functions (internal audit, compliance, risk management) must shift from backward-looking compliance to forward-thinking intelligence engines. AI governance is no longer a secondary concern -- boards expect AI governed like any other enterprise risk with clear ownership, defined risk tolerance, and visibility.

---

## 6. Policy Debates

### Frontier Model Regulation

- **Compute thresholds** (e.g., California SB 53's 10^26 FLOPS) create bright-line rules but may be arbitrary as efficiency improvements enable dangerous capabilities at lower compute
- Multiple US states (California, New York, Rhode Island, Massachusetts, Vermont) seeking to codify frontier developer liability
- No consensus on what "reasonable protections" or "unreasonable risk" standards should apply
- Federal preemption debate: Trump administration pushing uniform federal framework over state patchwork

### Open Source AI Policy

Current regulatory frameworks disadvantage open models:
- Regulations with carve-outs for low-cost models create "regulatory cliffs" with uncertain liability for open models exceeding thresholds
- Tension between democratizing access to powerful AI and enabling capabilities without safeguards
- EU AI Act's GPAI rules apply regardless of open/closed release
- Debate: should open-source AI be treated differently from proprietary AI for liability purposes?

### AI Liability

Central unresolved question: who is liable when AI causes harm?
- **California AB 316** (effective Jan 1, 2026): cannot use AI autonomy as a defense
- Developer vs. deployer vs. user liability distribution remains contested
- Product liability frameworks struggle with AI's probabilistic nature
- No settled legal standards for AI negligence

### Deepfake Regulation

- Content labelling mandates (California SB 942, China AI labelling rules)
- Watermarking requirements for AI-generated content
- Election integrity concerns driving urgency
- Technical feasibility debates around reliable detection

### AI in Critical Infrastructure

- Healthcare AI regulation (FDA guidance, state health AI laws)
- Financial services AI oversight (SEC, state algorithmic pricing laws)
- Autonomous vehicles (federal vs. state regulatory authority)
- Defense and national security applications

---

## 7. Emerging Trends -- Agentic AI Governance

### The Agentic Governance Gap

The most critical evolution in 2026 is the shift from governing **content** (what AI says) to governing **behavior** (what AI does). The concern moves from chatbot tone to financial agents executing trades or approving loans autonomously.

- **Non-human and agentic identities** expected to exceed 45 billion by end of 2026 -- more than 12x the human global workforce
- Only **10% of organizations** report having a strategy for managing autonomous AI systems
- Professor Noam Kolt's forthcoming Notre Dame Law Review article offers the first comprehensive legal framework for AI agent governance

### OWASP Top 10 for Agentic Applications (2026)

Released December 2025, developed by 100+ experts. Ten agent-specific risks:

1. **ASI01**: Agent Goal Hijack
2. **ASI02**: Tool Misuse and Exploitation
3. **ASI03**: Identity and Privilege Abuse
4. **ASI04**: Agentic Supply Chain Vulnerabilities
5. **ASI05**: Unexpected Code Execution (RCE)
6. **ASI06**: Memory and Context Poisoning
7. **ASI07**: Insecure Inter-Agent Communication
8. **ASI08**: Cascading Failures
9. **ASI09**: Human-Agent Trust Exploitation
10. **ASI10**: Rogue Agents

Key design principle: **least agency** -- do not give agents more autonomy than the business problem justifies.

### Bounded Autonomy

Most organizations deploying agentic AI in 2026 will use:
- Checkpoints and escalation paths
- Human-in-the-loop for high-severity actions
- Defined scope boundaries per agent
- Explainable decision traces for compliance

### AI-Generated Code Governance

Emerging concern as AI coding agents (Copilot, Claude Code, Cursor) generate increasing amounts of production code:
- Code provenance and attribution
- License compliance for AI-generated code
- Security review of AI-generated code
- Liability for vulnerabilities introduced by AI

### AIGOV @ AAAI 2026

Academic conference dedicated to AI governance -- indicates the field is maturing into a distinct research discipline.

---

## 8. Key Organizations and Standards Bodies

| Organization | Role | Key Deliverables |
|-------------|------|-----------------|
| **NIST** | US standards body | AI RMF, Cyber AI Profile, SP 800-53 COSAiS |
| **ISO/IEC JTC 1/SC 42** | International standards | ISO 42001, 42000 series |
| **OWASP** | Application security | LLM Top 10, Agentic Top 10 |
| **MITRE** | Adversary knowledge base | ATLAS framework |
| **OECD** | International policy | AI Principles, AI Policy Observatory |
| **EU AI Office** | EU governance | AI Act enforcement, Code of Practice |
| **UK AISI** | AI safety research | Capability evaluation, risk mitigation |
| **IEEE** | Engineering standards | IEEE 7000 series (ethical AI) |
| **Partnership on AI** | Multi-stakeholder | Best practices, research coordination |
| **IAPP** | Privacy professionals | AI Governance Profession Report |
| **UNESCO** | UN cultural/scientific | AI Ethics Recommendation |
| **CAC (China)** | Cyberspace administration | Algorithm, deep synthesis, GenAI regulations |

---

## 9. Sources

### Frameworks and Standards
- [NIST AI Risk Management Framework](https://www[.]nist[.]gov/itl/ai-risk-management-framework)
- [NIST AI RMF 2025 Updates](https://www[.]ispartnersllc[.]com/blog/nist-ai-rmf-2025-updates-what-you-need-to-know-about-the-latest-framework-changes/)
- [Draft NIST Cyber AI Profile (Dec 2025)](https://www[.]nist[.]gov/news-events/news/2025/12/draft-nist-guidelines-rethink-cybersecurity-ai-era)
- [NIST Cyber AI Profile -- Preliminary Draft (Jan 2026)](https://www[.]globalpolicywatch[.]com/2026/01/nist-publishes-preliminary-draft-of-cybersecurity-framework-profile-for-artificial-intelligence-for-public-comment/)
- [ISO/IEC 42001 and EU AI Act Pairing (ISACA)](https://www[.]isaca[.]org/resources/news-and-trends/industry-news/2025/isoiec-42001-and-eu-ai-act-a-practical-pairing-for-ai-governance)
- [ISO 42001 -- Deloitte](https://www[.]deloitte[.]com/us/en/services/consulting/articles/iso-42001-standard-ai-governance-risk-management.html)

### EU AI Act
- [EU AI Act Implementation Timeline](https://artificialintelligenceact[.]eu/implementation-timeline/)
- [EU AI Act Service Desk Timeline](https://ai-act-service-desk[.]ec[.]europa[.]eu/en/ai-act/timeline/timeline-implementation-eu-ai-act)
- [EU AI Act Summary (Jan 2026)](https://www[.]softwareimprovementgroup[.]com/blog/eu-ai-act-summary/)
- [DLA Piper -- Aug 2025 Obligations](https://www[.]dlapiper[.]com/en-us/insights/publications/2025/08/latest-wave-of-obligations-under-the-eu-ai-act-take-effect)

### US Regulation
- [State AI Laws Effective Jan 2026 -- King & Spalding](https://www[.]kslaw[.]com/news-and-insights/new-state-ai-laws-are-effective-on-january-1-2026-but-a-new-executive-order-signals-disruption)
- [Colorado AI Act Delay -- Seyfarth](https://www[.]seyfarth[.]com/news-insights/artificial-intelligence-legal-roundup-colorado-postpones-implementation-of-ai-law-as-california-finalizes-new-employment-discrimination-regulations-and-illinois-disclosure-law-set-to-take-effect.html)
- [State AI Law Tracker -- White & Case](https://www[.]whitecase[.]com/insight-alert/california-kentucky-tracking-rise-state-ai-laws-2025)
- [US AI Law Update -- Baker Botts](https://www[.]bakerbotts[.]com/thought-leadership/publications/2026/january/us-ai-law-update)
- [State AI Laws Under Federal Scrutiny -- White & Case](https://www[.]whitecase[.]com/insight-alert/state-ai-laws-under-federal-scrutiny-key-takeaways-executive-order-establishing)

### International
- [China AI Global Governance Action Plan](https://www[.]fmprc[.]gov[.]cn/mfa_eng/xw/zyxw/202507/t20250729_11679232.html)
- [China Cybersecurity Law AI Amendments](http://english[.]scio[.]gov[.]cn/m/in-depth/2025-10/29/content_118147780.html)
- [China AI Governance -- Mayer Brown](https://www[.]mayerbrown[.]com/en/insights/publications/2025/10/artificial-intelligence-a-brave-new-world-china-formulates-new-ai-global--governance-action-plan-and-issues-draft-ethics-rules-and-ai-labelling-rules)
- [China Leading AI Governance -- Nature](https://www[.]nature[.]com/articles/d41586-025-03972-y)
- [Global AI Governance Overview](https://sumsub[.]com/blog/comprehensive-guide-to-ai-laws-and-regulations-worldwide/)

### AI Security Frameworks
- [OWASP Top 10 for Agentic Applications 2026](https://genai[.]owasp[.]org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP LLM01 Prompt Injection](https://genai[.]owasp[.]org/llmrisk/llm01-prompt-injection/)
- [MITRE ATLAS Framework](https://atlas[.]mitre[.]org/)
- [MITRE ATLAS Overview -- NIST Presentation](https://csrc[.]nist[.]gov/csrc/media/Presentations/2025/mitre-atlas/TuePM2.1-MITRE%20ATLAS%20Overview%20Sept%202025.pdf)
- [AI Security Standards -- SentinelOne](https://www[.]sentinelone[.]com/cybersecurity-101/data-and-ai/ai-security-standards/)

### Enterprise Governance
- [Enterprise AI Governance Guide -- Liminal](https://www[.]liminal[.]ai/blog/enterprise-ai-governance-guide)
- [Model Registry Governance -- Introl](https://introl[.]com/blog/model-registry-governance-mlops-production-ai-2025)
- [Databricks AI Governance Framework](https://www[.]databricks[.]com/blog/introducing-databricks-ai-governance-framework)
- [AI Governance Best Practices -- Glean](https://www[.]glean[.]com/perspectives/ai-governance-best-practices)

### GRC Trends
- [AI Redefining GRC 2026 -- Governance Intelligence](https://www[.]governance-intelligence[.]com/regulatory-compliance/how-ai-will-redefine-compliance-risk-and-governance-2026)
- [GRC Trends 2026 -- MetricStream](https://www[.]metricstream[.]com/blog/top-grc-trends-agentic-ai-enterprise-cyber-grc-2026.html)
- [Top 20 AI GRC Software -- AIMultiple](https://research[.]aimultiple[.]com/ai-grc/)

### Policy Debates
- [Frontier AI Open Source -- AI Frontiers](https://ai-frontiers[.]org/articles/frontier-ai-should-be-open-source)
- [Case for AI Liability -- AI Frontiers](https://ai-frontiers[.]org/articles/case-for-ai-liability)
- [2026 AI Regulatory Preview -- Wilson Sonsini](https://www[.]wsgr[.]com/en/insights/2026-year-in-preview-ai-regulatory-developments-for-companies-to-watch-out-for.html)
- [2026 and AI -- CFR](https://www[.]cfr[.]org/articles/how-2026-could-decide-future-artificial-intelligence)

### Agentic AI Governance
- [AI Agents Misbehave -- Baker Botts](https://ourtake[.]bakerbotts[.]com/post/102me2l/when-ai-agents-misbehave-governance-and-security-for-autonomous-ai)
- [Agentic AI Governance Wake-Up Call -- NACD](https://www[.]nacdonline[.]org/all-governance/governance-resources/directorship-magazine/online-exclusives/2025/q3-2025/autonomous-artificial-intelligence-oversight/)
- [AWS Agentic AI Security Scoping Matrix](https://aws[.]amazon[.]com/blogs/security/the-agentic-ai-security-scoping-matrix-a-framework-for-securing-autonomous-ai-systems/)
