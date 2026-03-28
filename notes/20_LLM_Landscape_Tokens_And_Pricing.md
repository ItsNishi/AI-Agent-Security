# Note 20: LLM Landscape and Token Economics

Understanding the LLM landscape is prerequisite to attacking or defending AI systems. Token economics determine attack costs, model selection shapes capability, and the provider you choose defines your data sovereignty posture. This note is a security-oriented reference -- model specs and pricing serve as inputs to threat modeling, not as a buying guide.

Cross-references: [Note 05](05_AI_Coding_Language_Performance.md) (language-level token efficiency), [Note 18](18_Token_Optimization_And_LLM_Efficiency.md) (optimization techniques), [Note 19](19_Token_Based_Attacks_And_Resource_Exploitation.md) (token-based attacks and resource exploitation).

---

## Tokens and Tokenization

Tokens are the atomic units LLMs process -- subword chunks determined by the model's tokenizer. A token is typically 3-4 English characters, roughly 0.75 words.

**Concrete examples** (GPT-4o tokenizer):
- `"Hello world"` = 2 tokens (`Hello`, ` world`)
- `"tokenization"` = 2 tokens (`token`, `ization`)
- `"antidisestablishmentarianism"` = 4 tokens
- `"こんにちは"` (Japanese) = 3-5 tokens (CJK is ~2-3x denser than English)

**Why tokens matter for security:**
- **Billing unit** -- every API charges per million tokens (MTok), separately for input and output. This is the cost surface attackers target in Denial of Wallet (see [Note 19 Section 1](19_Token_Based_Attacks_And_Resource_Exploitation.md#1-denial-of-wallet-attacks)).
- **Context window** -- the max tokens a model can process (input + output combined). Context window poisoning fills this with attacker-controlled content ([Note 19 Section 4](19_Token_Based_Attacks_And_Resource_Exploitation.md#4-context-window-poisoning)).
- **Latency** -- output tokens are generated sequentially (autoregressive), making sponge examples effective at degrading service ([Note 19 Section 2](19_Token_Based_Attacks_And_Resource_Exploitation.md#2-sponge-examples-and-energy-latency-attacks)).
- **Cost asymmetry** -- output tokens cost 3-5x more than input because each requires a full forward pass. Attackers exploit this by triggering verbose responses.

**Rules of thumb:**
- 1 MTok ~= 750K English words ~= 3,000 pages of text
- 1 page of code ~= 200-400 tokens
- A typical API call (500-word prompt + 200-word response) ~= 1,000 tokens total

### Tokenization Algorithms

All modern LLMs use **subword tokenization** -- breaking text into pieces smaller than words but larger than characters. The tokenizer is trained on a corpus before model training and never changes after.

| Algorithm | Used By | Mechanism |
|---|---|---|
| **BPE** (Byte Pair Encoding) | GPT-4/5, Claude, Llama 3/4, Mistral | Iteratively merge most frequent adjacent pairs |
| **WordPiece** | BERT, DistilBERT | Likelihood-maximized merges, `##` continuation prefix |
| **SentencePiece** (Unigram) | T5, Llama (wraps BPE), multilingual models | Language-agnostic raw byte stream, no pre-tokenization |

SentencePiece handles languages without whitespace (Chinese, Japanese, Thai) better than BPE -- relevant for multilingual attack surface analysis.

### Vocabulary Sizes (March 2026)

| Model Family | Vocab Size | Notes |
|---|---|---|
| GPT-4o / GPT-5 | 200,768 | Largest commercial vocab, ~15% more efficient than GPT-4 |
| Claude (Opus/Sonnet 4.6) | ~65,536 | Smaller vocab, compensated by architecture |
| Llama 3/4 | 128,256 | Doubled from Llama 2 (32K), major multilingual improvement |
| Gemini 3.x | 256,000 | Largest vocab, best multilingual coverage |
| Qwen 3 | 151,936 | Strong CJK optimization |
| DeepSeek V3 | 128,000 | Matches Llama 3 |
| Mistral | 32,768 | Smallest major vocab |

Larger vocabularies improve efficiency but increase the embedding table attack surface. Vocab size differences also affect adversarial tokenization -- the same input tokenizes differently across models, which matters for transfer attacks and token smuggling ([Note 19 Section 6](19_Token_Based_Attacks_And_Resource_Exploitation.md#6-tokenizer-security)).

### Token Efficiency by Language

| Language | Avg Chars/Token | Relative Cost (vs English) |
|---|---|---|
| English | 3.5-4.0 | 1.0x |
| Spanish/French | 3.0-3.5 | 1.1-1.2x |
| German | 2.5-3.0 | 1.2-1.4x (compounds) |
| Chinese/Japanese | 1.5-2.0 | 2.0-3.0x |
| Korean | 1.5-2.5 | 2.0-2.5x |
| Arabic/Hindi | 2.0-2.5 | 1.5-2.0x |
| Code (Python) | 4.0-5.0 | 0.8-0.9x |

The cost multiplier for CJK languages means DoW attacks using CJK input are 2-3x more effective per character. Code is often more efficient than prose because common keywords compress into single tokens.

---

## Token Economics

### Input vs Output Pricing

Every API provider charges output tokens at 3-5x the input rate:

- **Input**: Processed in parallel (one forward pass for the entire prompt)
- **Output**: Generated one token at a time (autoregressive), each requiring a full forward pass
- **KV cache**: Each output token grows the key-value cache, consuming GPU memory

This asymmetry is the core reason reasoning exhaustion attacks work -- forcing thinking tokens at output rates costs 3-5x more than stuffing the same token count into the prompt. A well-structured 500-token prompt that gets a 50-token answer is far cheaper than a vague 100-token prompt that triggers a 1,000-token response.

### Discount Mechanisms

| Mechanism | Typical Savings | How It Works |
|---|---|---|
| **Prompt caching** | 90% on cached input | Reuse KV cache from identical prompt prefixes. Anthropic: 0.1x read rate. OpenAI: 0.5x. |
| **Batch API** | 50% | Submit jobs asynchronously, provider runs during off-peak. Anthropic, OpenAI, Google. |
| **Model routing** | 60-80% | Route simple queries to cheap models, complex ones to expensive. OpenRouter, RouteLLM, Martian. |
| **Quantization** | 70-80% VRAM | Run open models at INT4/INT8 instead of FP16. Quality loss: 2-8%. |
| **Stacking** | Up to 95% | Batch (50%) + caching (90%) = 95% reduction for non-real-time workloads. |

**Security angle**: Model routing is an attack surface. If an adversary can influence the routing decision (e.g., by crafting inputs that appear complex), they force expensive model paths -- a targeted DoW vector. See [Note 18 Section 8](18_Token_Optimization_And_LLM_Efficiency.md#8-model-routing) for routing architectures and [Note 19](19_Token_Based_Attacks_And_Resource_Exploitation.md#1-denial-of-wallet-attacks) for exploitation techniques.

### Extended Thinking / Reasoning Tokens

Models with chain-of-thought reasoning (Claude extended thinking, OpenAI o-series, DeepSeek R1) generate "thinking tokens" before the visible response. These are billed as output tokens.

Budget 2-5x the visible output for thinking overhead. A 200-token visible response may cost 600-1,000 tokens total with reasoning enabled.

Reasoning tokens are the primary target of ThinkTrap and ReasoningBomb attacks ([Note 19 Section 3](19_Token_Based_Attacks_And_Resource_Exploitation.md#3-reasoning-exhaustion-attacks)) -- adversarial prompts that maximize thinking token generation while producing minimal visible output.

---

## Model Landscape (March 2026)

### Frontier Closed Models

| Model | Provider | Context | Input $/MTok | Output $/MTok | Key Strength |
|---|---|---|---|---|---|
| Opus 4.6 | Anthropic | 1M | $5.00 | $25.00 | Coding (80.8% SWE-bench), writing |
| Sonnet 4.6 | Anthropic | 1M | $3.00 | $15.00 | Best value frontier model |
| Haiku 4.5 | Anthropic | 200K | $1.00 | $5.00 | Fastest, lowest cost |
| GPT-5 | OpenAI | 1M | $1.25 | $10.00 | Math (94.6% AIME) |
| GPT-4.1 | OpenAI | 1M | $2.00 | $8.00 | Instruction-following |
| GPT-4o | OpenAI | 128K | $2.50 | $10.00 | Multimodal workhorse |
| o3 | OpenAI | 200K | $2.00 | $8.00 | Reasoning |
| o4-mini | OpenAI | 200K | $1.10 | $4.40 | Budget reasoning |
| Gemini 3.1 Pro | Google | 1M | $2.00 | $12.00 | Reasoning leader (94.3% GPQA) |
| Gemini 3 Flash | Google | 1M | ~$0.30 | ~$2.50 | Balanced |
| Gemini 3.1 Flash-Lite | Google | 1M | $0.25 | $1.50 | Cheapest 1M-context |
| Grok 4.1 Fast | xAI | 200K | $0.20 | $0.50 | Vision, speed |
| Nova Premier | Amazon | -- | $2.50 | $12.50 | Bedrock integration |
| Nova Lite | Amazon | -- | $0.06 | $0.24 | Cheapest major provider |

All major providers offer 50% batch discounts and prompt caching (90% Anthropic, 50% OpenAI/Google).

Sources: [Anthropic](https://docs.anthropic.com/en/docs/about-claude/pricing), [OpenAI](https://openai.com/api/pricing/), [Google](https://ai.google.dev/gemini-api/docs/pricing), [xAI](https://docs.x.ai/docs/api-pricing), [Amazon](https://aws.amazon.com/nova/pricing/)

### Open Weight Models

"Open source" in LLM context usually means **open weight** -- weights are downloadable, but training data and code may not be. Licenses vary from fully permissive (Apache 2.0) to restrictive (Meta custom with branding requirement).

| Model | Provider | Active / Total Params | Context | License | Key Strength |
|---|---|---|---|---|---|
| Llama 4 Scout | Meta | 17B / 109B MoE | 10M | Meta custom | Longest context, self-hostable |
| Llama 4 Maverick | Meta | 17B / 400B MoE | 1M | Meta custom | Multimodal, 128 experts |
| DeepSeek V3.2 | DeepSeek | 37B / 685B MoE | 164K | MIT-style | 37x cheaper than GPT-5, 72-74% SWE-bench |
| DeepSeek V3.2-Speciale | DeepSeek | 37B / 685B MoE | 164K | MIT-style | 96.0% AIME, IMO gold |
| Qwen3.5-Plus | Alibaba | 17B / 397B MoE | 1M | Apache 2.0 | 201 languages, most permissive |
| Mistral Large 3 | Mistral | 41B / 675B MoE | 256K | Proprietary | European, configurable reasoning |
| Mistral Small 4 | Mistral | 6B / 119B MoE | 256K | Apache 2.0 | Unified model, open |
| Gemma 3 (1-27B) | Google | Dense | 128K | Open weights | Edge/mobile deployment |
| Phi-4 | Microsoft | 14B | -- | Open | STEM reasoning |
| Nemotron-Cascade 2 | NVIDIA | 3B / 30B MoE | -- | NVIDIA Open | IMO gold, 20x param efficiency |
| Kimi K2.5 | Moonshot | 32B / 1.04T MoE | 256K | Modified MIT | 76.8% SWE-bench, agent swarm |
| GLM-5 | Zhipu | 44B / 745B MoE | 200K | MIT | Lowest hallucination, Ascend-trained |
| Falcon H1R | TII (UAE) | 7B | -- | Open | Claims 7x size-efficiency |

API pricing for hosted open models (via provider APIs or Groq/Together):
- DeepSeek V3.2: $0.27/$1.10
- Qwen3.5-Plus: $0.26/$1.56
- Kimi K2.5: $0.60/$2.50
- GLM-5: $1.00/$3.20
- Llama 4 Scout on Groq: $0.11/$0.34

### Chinese Models (Proprietary)

| Model | Provider | Key Specs | Input $/MTok | Output $/MTok |
|---|---|---|---|---|
| Doubao Seed 2.0 Pro | ByteDance | 98.3% AIME, 155M weekly users | $0.47 | $2.37 |
| ERNIE 4.5 | Baidu | Multimodal generalist | $0.55 | $2.20 |
| ERNIE X1 | Baidu | Reasoning (competes w/ R1/o3-mini) | $0.28 | $1.10 |
| Hunyuan 2.0 | Tencent | 406B MoE, 32B active, 256K context | ~$0.65 | ~$1.60 |
| SenseNova V6 | SenseTime | Real-time video analysis, Cantonese | ~$3.86 | -- |

### Global / Sovereign Models

| Model | Country | Params | License | API |
|---|---|---|---|---|
| Solar Pro 2/3 | South Korea | -- | Open weights | $0.15/$0.60 |
| HyperCLOVA X | South Korea | -- | Partial open | Regional |
| Rakuten AI 3.0 | Japan | ~700B MoE | Apache 2.0 | Self-host |
| Sarvam 105B | India | 10.3B active MoE | Apache 2.0 | Yes |
| BharatGen Param 2 | India | 17B MoE | Open | No |
| AI21 Jamba 1.7 | Israel | Hybrid SSM-MoE | Open | $2/$8 |
| EuroLLM-22B | EU | 22B | Apache 2.0 | No |
| Viking 33B | Finland | 33B | Apache 2.0 | No |
| InkubaLM | South Africa | 0.4B | CC BY-NC | No |

The sovereign AI movement is a direct response to dependency risk on US/Chinese providers -- governments treat LLM independence as strategic infrastructure.

---

## Security Implications of Model Selection

### Chinese Model Censorship and Data Sovereignty

Chinese LLMs exhibit **systematic content filtering** documented in peer-reviewed research:

- **Input blocking**: Consistent across DeepSeek, Qwen, Kimi, Doubao on politically sensitive queries
- **Output filtering**: Sensitive content appears in internal reasoning but is removed from final output ([NDSS 2026](https://www.ndss-symposium.org/ndss-paper/characterizing-the-implementation-of-censorship-policies-in-chinese-llm-services/))
- **Documented suppressions**: Government accountability, civic mobilization, positive framing of Western democratic processes ([Citizen Lab](https://citizenlab.ca/research/an-analysis-of-chinese-censorship-bias-in-llm/))
- **Data residency**: DeepSeek privacy policy states data is stored in PRC. Multiple US federal/state agencies have banned DeepSeek on government devices.

**Threat model**: Safe for coding, math, and general knowledge tasks. Unreliable for politically sensitive research or any task where censored output leads to wrong decisions. Data transmitted is subject to Chinese surveillance laws.

For security work specifically: censorship doesn't affect vulnerability analysis, exploit development, or defensive tooling. It does affect threat intelligence, geopolitical analysis, and any task involving Chinese government or military topics.

### Open Model Supply Chain Risks

Downloading a 70B-parameter model from Hugging Face is a trust decision. The open weight ecosystem has no equivalent of code signing or reproducible builds for model weights.

**Threat vectors**:
- **Poisoned weights**: Trojan models that behave normally on benchmarks but contain backdoors activated by specific inputs. Detection is an open research problem -- no reliable scanner exists for weight-level trojans.
- **Quantization integrity**: Converting FP16 to INT4 changes model behavior. Malicious quantization could introduce targeted degradation. Most users download pre-quantized models from anonymous uploaders.
- **Fine-tuning attacks**: LoRA adapters and merged models inherit trust from the base model, but the adapter itself can introduce arbitrary behavior. A "helpful coding assistant" LoRA could exfiltrate code to hardcoded endpoints.
- **Model identity**: No cryptographic binding between a model's claimed identity and its actual weights. A file named `llama-4-scout-q4.gguf` could contain anything.

**Mitigations**: Verify SHA256 checksums against official releases. Prefer downloads from verified organizations on Hugging Face. Run inference in network-isolated containers. Monitor outbound traffic from inference processes.

### Model Routing as Attack Surface

Cost-optimized deployments route queries to different models based on complexity. If an adversary can influence the routing decision -- by crafting inputs that appear complex to the router but are simple to the expensive model -- they force expensive execution paths.

**Attack pattern**: Inject complexity signals (long context, technical jargon, multi-step formatting) into otherwise simple queries. The router selects the frontier model; the actual computation is trivial. Net effect: 10-50x cost amplification per request.

**Defense**: Route on output cost (set token budgets per tier), not input complexity. Cap per-request spend regardless of which model is selected.

### Vendor Lock-In as Risk

Single-provider dependency creates concentrated blast radius:

- **API key compromise**: One leaked key exposes all workloads on that provider. Rate limits and billing alerts are the only defense -- there's no per-key scope restriction on most platforms.
- **Provider outage**: Anthropic, OpenAI, and Google have each had multi-hour outages in the past 12 months. If your security tooling depends on a single provider, it goes down with them.
- **Pricing changes**: Providers can change pricing with 30 days notice. A 2x price increase doubles your DoW attack surface overnight.
- **Policy changes**: Content policies change. A model that worked for your red team tooling yesterday may refuse tomorrow.

**Mitigation**: Abstract the provider behind an interface. Test failover to at least two providers. Store API keys in secrets managers with rotation policies, not environment variables.

### Model Selection for Security Work

| Security Task | Recommended Models | Why |
|---|---|---|
| Exploit development | Opus 4.6, GPT-5, DeepSeek V3.2-S | High SWE-bench scores correlate with code generation quality |
| Vulnerability analysis | Gemini 3.1 Pro, Opus 4.6 | Reasoning benchmarks (GPQA) correlate with complex analysis |
| Threat intelligence | Claude, GPT (avoid Chinese models) | No censorship filtering on geopolitical content |
| Bulk scanning/triage | Haiku 4.5, Flash-Lite, Nova Lite | Cost efficiency for high-volume, low-complexity tasks |
| Red team content | Open models (self-hosted) | No content policy restrictions, no API logging |
| Multilingual analysis | Qwen 3.5, Gemini 3.1 Pro | Broadest language coverage (201 and 100+ languages) |
| Air-gapped environments | Llama 4 Scout/Maverick, Qwen 3.5 | Open weights, run fully offline |

For offensive security: self-hosted open models avoid API-level content filtering and leave no query logs with third parties. The tradeoff is lower capability than frontier closed models on complex reasoning tasks.

---

## Writing Quality and Evaluation Benchmarks

Writing quality matters for security: phishing, social engineering, and report generation all depend on output quality.

**EQ-Bench Creative Writing Elo** (top models):

| Model | Elo |
|---|---|
| Claude Sonnet 4.6 | 1,936 |
| Claude Opus 4.6 | 1,932 |
| Grok 4.1 Thinking | ~1,720 |

**Chatbot Arena Creative Writing Elo** (top models):

| Model | Elo | Votes |
|---|---|---|
| Claude Opus 4.6 Thinking | 1,495 | 1,954 |
| Grok 4.20-beta1 | 1,485 | 1,015 |
| Gemini 3.1 Pro | 1,485 | 6,359 |

**Long-form gap**: LongGenBench shows all models degrade on 16K+ token generation despite strong context understanding benchmarks. Claimed context windows exceed usable generation windows -- relevant for long report generation and document analysis tasks.

Sources: [EQ-Bench](https://eqbench.com/creative_writing_longform.html), [Chatbot Arena](https://lmarena.ai/), [WritingBench](https://arxiv.org/abs/2503.05244), [LongGenBench](https://arxiv.org/abs/2409.02076)

---

## Inference Infrastructure

### Self-Hosting Economics

**GPU Requirements** (rule of thumb: ~2 GB VRAM per billion parameters at FP16):

| Model Size | FP16 VRAM | INT4 VRAM | GPU Examples |
|---|---|---|---|
| 7B | 14 GB | 5-6 GB | RTX 4060 (8GB, quantized) |
| 14B | 28 GB | 7-11 GB | RTX 4090 (24GB) |
| 70B | 140 GB | ~18 GB | H100 (80GB) or 2x A100 |
| 120B+ | 240 GB+ | 30+ GB | Multi-GPU H100/H200 |

**Cloud GPU Pricing (March 2026)**:

| GPU | RunPod | Lambda Labs | AWS | Vast.ai |
|---|---|---|---|---|
| H100 (80GB) | $2.69/hr | $2.99/hr | $3-4/hr | $0.29-0.60/hr |
| A100 (80GB) | $1.39/hr | $2.49/hr | $3.67/hr | $0.15-0.40/hr |

Specialist providers (Vast.ai, RunPod spot) are 60-85% cheaper than hyperscalers. Hyperscalers bundle SLAs and compliance.

**Break-even**: <100M tokens/month = APIs cheaper. >500M tokens/month = self-hosting saves 40-60%.

### Self-Hosting Security Considerations

Self-hosting trades API-level risks for infrastructure-level risks:

- **GPU cloud trust**: Spot/preemptible instances on budget providers (Vast.ai) run on shared hardware. Your model weights and inference data may be extractable by the host or co-tenants. For sensitive workloads, use dedicated instances or on-premise hardware.
- **Data residency**: Self-hosting is the only way to guarantee data never leaves your network. Required for classified environments, HIPAA workloads, and air-gapped deployments.
- **Model integrity**: You control the exact model binary. No risk of provider-side model updates changing behavior mid-deployment. But you're responsible for verifying what you downloaded (see supply chain risks above).
- **Attack surface**: Every self-hosted inference server (vLLM, llama.cpp, Ollama) is network-accessible software. Treat it like any other server: patch, firewall, authenticate. Ollama in particular has had multiple remote code execution vulnerabilities.

---

## Key Trends (March 2026)

1. **MoE dominance** -- Nearly every frontier model uses Mixture-of-Experts. Active parameters (17-44B) deliver frontier performance while total parameters (100B-2T) store knowledge. This decouples quality from inference cost -- and makes per-token attack cost calculations less intuitive.

2. **Price compression** -- Sub-$1/MTok input is standard. Sub-$0.30/MTok available. Race to zero on commodity tasks. Lower prices reduce DoW impact per request but lower the barrier for attacker-funded operations.

3. **Chinese model parity** -- Kimi K2.5, GLM-5, DeepSeek V3.2, and Doubao Seed 2.0 match or exceed Western models on coding and math at 4-37x lower cost. The gap is closed on specialized tasks; frontier reasoning breadth (GPQA) is the remaining differentiator.

4. **Hardware independence** -- GLM-5 trained entirely on Huawei Ascend chips. US export controls are accelerating Chinese chip development, not preventing frontier model training. Assumes adversaries will have frontier capability regardless of sanctions.

5. **Context window inflation** -- 1M tokens is table stakes. Llama 4 Scout claims 10M. Real-world long-context accuracy often degrades significantly -- claimed windows exceed usable windows. Larger windows mean larger context poisoning attack surfaces.

6. **Reasoning tokens as cost center** -- Extended thinking, o-series, R1 reasoning. All billed at output rates. Makes reasoning exhaustion attacks ([Note 19 Section 3](19_Token_Based_Attacks_And_Resource_Exploitation.md#3-reasoning-exhaustion-attacks)) increasingly expensive for defenders to absorb.

7. **Open weight eating the market** -- Apache 2.0 / MIT releases from Alibaba, Zhipu, DeepSeek, Mistral, Meta. 70-80% of enterprise workloads can run on open models. More open models = more self-hosting = more infrastructure attack surface and supply chain risk.

---

## Sources

### Pricing Documentation
- [Anthropic Pricing](https://docs.anthropic.com/en/docs/about-claude/pricing)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Google AI Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Amazon Nova Pricing](https://aws.amazon.com/nova/pricing/)
- [DeepSeek API Pricing](https://api-docs.deepseek.com/quick_start/pricing)
- [Mistral Pricing](https://mistral.ai/pricing)
- [Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [OpenRouter](https://openrouter.ai) (aggregated pricing comparison)
- [PricePerToken](https://pricepertoken.com) (cross-provider comparison)

### Model Documentation
- [Gemini 3.1 Pro](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-pro/)
- [Gemini 3.1 Flash-Lite](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-1-flash-lite/)
- [Llama 4 Official](https://www.llama.com/models/llama-4/)
- [Kimi K2.5 on Hugging Face](https://huggingface.co/moonshotai/Kimi-K2.5)
- [GLM-5 on Hugging Face](https://huggingface.co/zai-org/GLM-5)
- [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388)
- [DeepSeek V3 Technical Report](https://arxiv.org/html/2512.02556v1)
- [Gemma 3 Overview](https://ai.google.dev/gemma/docs/core)
- [Phi-4 Announcement](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-phi-4-microsoft-s-newest-small-language-model-specializing-in-comple/4357090)
- [Nemotron 3 Super](https://developer.nvidia.com/blog/introducing-nemotron-3-super-an-open-hybrid-mamba-transformer-moe-for-agentic-reasoning/)

### Benchmarks
- [EQ-Bench Creative Writing](https://eqbench.com/creative_writing_longform.html)
- [Chatbot Arena](https://lmarena.ai/)
- [WritingBench](https://arxiv.org/abs/2503.05244)
- [LongGenBench](https://arxiv.org/abs/2409.02076)

### Infrastructure
- [Self-Hosted LLM Guide 2026](https://blog.premai.io/self-hosted-llm-guide-setup-tools-cost-comparison-2026/)
- [LLM Hosting Cost 2026](https://aisuperior.com/llm-hosting-cost/)
- [GPU VRAM Requirements](https://www.spheron.network/blog/gpu-requirements-cheat-sheet-2026/)
- [Cloud GPU Pricing Comparison](https://www.spheron.network/blog/gpu-cloud-pricing-comparison-2026/)

### Censorship and Policy
- [NDSS 2026 - Chinese LLM Censorship](https://www.ndss-symposium.org/ndss-paper/characterizing-the-implementation-of-censorship-policies-in-chinese-llm-services/)
- [Citizen Lab - Chinese Censorship Bias](https://citizenlab.ca/research/an-analysis-of-chinese-censorship-bias-in-llm/)
- [PNAS Nexus - Political Censorship in LLMs](https://academic.oup.com/pnasnexus/article/5/2/pgag013/8487339)

### Global / Sovereign Models
- [Upstage Solar Pro Pricing](https://www.upstage.ai/pricing/api)
- [Rakuten AI 3.0 Release](https://global.rakuten.com/corp/news/press/2026/0317_01.html)
- [Sarvam AI 105B](https://huggingface.co/sarvamai/sarvam-105b)
- [AI21 Jamba](https://www.ai21.com/jamba/)
- [EuroLLM-22B](https://huggingface.co/utter-project/EuroLLM-22B-Instruct-2512)
- [OpenEuroLLM](https://openeurollm.eu/)
- [Viking 33B](https://huggingface.co/LumiOpen/Viking-33B)
- [Lelapa AI InkubaLM](https://huggingface.co/lelapa/InkubaLM-0.4B)
