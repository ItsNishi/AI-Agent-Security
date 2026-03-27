# Token Optimization and LLM Efficiency

> **Related notes**: [05 -- AI Coding Language Performance](05_AI_Coding_Language_Performance.md) (per-language token efficiency, language-steering attacks), [13 -- AI Application Ecosystem Security](13_AI_Application_Ecosystem_Security.md) (plugin/agent attack surfaces), [19 -- Token-Based Attacks](19_Token_Based_Attacks_And_Resource_Exploitation.md) (adversarial resource exploitation)

Every token is a unit of cost, latency, and context budget. Optimization is not about cutting corners -- it is about fitting the right information into finite attention, at the right price, using the right model. Anthropic now frames this discipline as **context engineering**: "finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."

---

## Table of Contents

1. [Current Pricing Landscape](#1-current-pricing-landscape)
2. [Context Engineering](#2-context-engineering)
3. [Prompt Structure](#3-prompt-structure)
4. [Few-Shot vs Zero-Shot vs Chain-of-Thought](#4-few-shot-vs-zero-shot-vs-chain-of-thought)
5. [Extended Thinking](#5-extended-thinking)
6. [Structured Output](#6-structured-output)
7. [Prompt Compression](#7-prompt-compression)
8. [Model Routing](#8-model-routing)
9. [Prompt Caching](#9-prompt-caching)
10. [Context Window Management](#10-context-window-management)
11. [Batching and Application Caching](#11-batching-and-application-caching)
12. [Agent Loop Optimization](#12-agent-loop-optimization)
13. [Claude Code Cost Management](#13-claude-code-cost-management)
14. [Security Implications](#14-security-implications)
15. [Sources](#15-sources)

---

## 1. Current Pricing Landscape

LLM API prices dropped ~80% from early 2025 to early 2026. The gap between budget and premium models exceeds 1,000x.

### Anthropic Claude (March 2026)

| Model | Input $/MTok | Output $/MTok | Context |
|-------|-------------|--------------|---------|
| Opus 4.6 | $5.00 | $25.00 | 200K |
| Sonnet 4.6 | $3.00 | $15.00 | 200K |
| Haiku 4.5 | $1.00 | $5.00 | 200K |

Opus 4.5/4.6 at $5/$25 is **67% cheaper** than Opus 4/4.1 at $15/$75. Extended thinking tokens bill as output tokens at standard rates. The 1M-token context surcharge is removed for 4.6 models.

### OpenAI (March 2026)

| Model | Input $/MTok | Output $/MTok | Context |
|-------|-------------|--------------|---------|
| GPT-5 | $1.25 | $10.00 | 400K |
| GPT-4.1 | $2.00 | $8.00 | 1M |
| GPT-4.1 mini | $0.40 | $1.60 | 1M |
| GPT-4o mini | $0.15 | $0.60 | 128K |
| o3 | $2.00 | $8.00 | 200K |
| o4-mini | $1.10 | $4.40 | 200K |

### Google Gemini (March 2026)

| Model | Input $/MTok | Output $/MTok | Context |
|-------|-------------|--------------|---------|
| Gemini 2.5 Pro | $1.25 | $10.00 | 1M |
| Gemini 2.5 Flash | $0.30 | $2.50 | 1M |

### Budget Providers

| Provider | Model | Input $/MTok | Output $/MTok |
|----------|-------|-------------|--------------|
| DeepSeek | V3.2 | $0.14-0.28 | $0.28-0.42 |
| Mistral | Large 3 | $0.06 | $0.18 |
| Mistral | Nemo | $0.02 | $0.04 |

DeepSeek V3.2 is ~36x cheaper than GPT-5 on output. Self-hosting open models at >10B tokens/month drops costs below $0.10/MTok.

### Key Ratio

Output tokens cost **3-5x more** than input tokens across all providers. Output length control is the single highest-leverage optimization.

---

## 2. Context Engineering

### From Prompts to Context

Anthropic's [context engineering framework](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) treats prompt crafting as one part of a larger discipline: curating the optimal token set for each inference call.

Core problem: **context rot**. As token count increases, the model's ability to recall specific information decreases. Transformer attention is O(n^2) -- every token dilutes attention to every other token. Treat context as a finite resource with diminishing returns.

Research from Levy, Jacoby, and Goldberg (2024): LLM reasoning performance degrades around **3,000 tokens**. Practical sweet spot for instruction content: **150-300 words**.

### Just-in-Time Loading

Instead of stuffing everything into the system prompt, load context only when needed:

- **Static reference**: system prompt (cached)
- **Per-request context**: user message or tool results (loaded on demand)
- **Agent memory**: external files read selectively, not dumped wholesale

Anthropic's own evaluation: context editing (removing stale content mid-conversation) reduced token consumption by **84%** in a 100-turn web search task while enabling workflows that would otherwise fail.

---

## 3. Prompt Structure

### Claude Processing Order

Tools -> System -> Messages. This hierarchy affects both caching and instruction priority.

### Placement Rules

| Content | Where | Why |
|---------|-------|-----|
| Stable instructions, reference material | System prompt (beginning) | Cached; high attention position |
| Long documents, inputs | User message (top) | Before the query for better comprehension |
| Task-specific query | User message (end) | Queries at end improve quality by up to 30% on complex inputs |
| Dynamic per-request data | User message (after cache break) | Does not invalidate system cache |

### XML Tags for Claude

Claude was trained with XML tags in its data. Tags like `<instructions>`, `<context>`, `<example>`, `<document>` genuinely outperform Markdown or numbered lists for structuring Claude prompts.

### Prompt Length

Keep system prompts under ~1,000 tokens for most applications. Push reference material into user messages or tool results for just-in-time loading. Long system prompts hurt prefill latency and bloat the KV cache.

### Assistant Prefill

Deprecated on Claude 4.6 models. On older models, prefilling (`{"role": "assistant", "content": "{"}`) forces output format. Claude 4.6's improved instruction-following makes this unnecessary.

---

## 4. Few-Shot vs Zero-Shot vs Chain-of-Thought

### The 2025 Reversal

[Cheng et al. (EMNLP 2025)](https://arxiv.org/abs/2506.14641) found that for strong modern models, **adding CoT exemplars does not improve reasoning performance** over zero-shot CoT. Few-shot examples primarily serve as **output format alignment**, not reasoning aids. DeepSeek's own reports confirm few-shot prompting can degrade R1 performance.

### Decision Matrix

| Strategy | Best For | Token Cost | Quality Trade-off |
|----------|----------|-----------|-------------------|
| Zero-shot | Simple tasks, frontier models | Lowest | Good on 2025+ models |
| Few-shot (2-3 examples) | Format enforcement, classification | Medium | Controls output structure |
| Zero-shot CoT ("think step by step") | Math, logic, multi-step reasoning | Medium (more output) | Often best on modern models |
| Few-shot CoT | Legacy models, niche domains | Highest | Diminishing returns on strong models |

### The Big-O_tok Framework

[Sypherd et al. (May 2025)](https://arxiv.org/abs/2505.14880) directly measures token cost per unit of performance. Key finding: **increased token usage produces drastically diminishing performance returns**. Each additional example costs more tokens but yields less improvement.

Practical guidance:
- Start zero-shot. Add examples only if output format or domain accuracy is wrong.
- 2-3 diverse examples usually match 5-10 in quality.
- For reasoning on frontier models, zero-shot CoT beats few-shot CoT while using fewer input tokens.

---

## 5. Extended Thinking

### Mechanics

Extended thinking allocates a separate token budget for internal reasoning before producing the final answer. Thinking tokens bill as **output tokens** at standard rates. The API returns a summary; you're charged for the full thinking tokens generated.

### Cost Math

A 10K thinking budget on Opus 4.6 costs up to $0.25 in output tokens per request. Accuracy on math questions improves **logarithmically** with thinking tokens -- 10x the budget does not produce 10x better results.

### Budget Sizing

| Task | Budget | Notes |
|------|--------|-------|
| Small problems | 4,000-8,000 | Minimum meaningful budget |
| Complex analysis | 10,000-16,000 | Good starting point |
| Very complex tasks | 16,000-32,000+ | Claude rarely uses full budgets above 32K |

### Adaptive Thinking (Claude 4.6)

On Opus 4.6 and Sonnet 4.6, use `thinking={"type": "adaptive"}`. Manual budgets (`type: "enabled"` with `budget_tokens`) still work but are deprecated. Claude evaluates each request's complexity and decides whether and how much to think.

Effort levels control the threshold: "high" (default) almost always thinks; lower levels skip thinking on simple problems.

### When to Use

**Use**: math, complex reasoning, code analysis, multi-step planning, research synthesis.

**Skip**: factual lookups, simple Q&A, generation tasks with minimal reasoning, latency-critical paths.

### Caching Interaction

- Thinking blocks from previous turns are removed from context but count as input tokens when cached
- Changing `budget_tokens` invalidates message cache (system prompt cache preserved)
- Use 1-hour cache TTL for extended thinking workflows that exceed 5 minutes

---

## 6. Structured Output

### Three Levels (2026)

1. **Prompt engineering** ("return JSON") -- 80-95% validity, fails silently
2. **Tool use / function calling** -- schema as hint, 95-99% validity
3. **Native constrained decoding** -- 100% schema validity via FSM token masking

Claude's structured output (GA on 4.5+ models): `output_config.format` with JSON Schema. Grammar compiled, cached 24 hours. The model literally cannot produce tokens violating the schema.

### Token Overhead

Structured output generates more tokens than free text. `{"sentiment": "positive"}` (~7 tokens) vs "The sentiment is positive" (5 tokens) -- **40% more**. Full structured responses run 2-3x the tokens of free text.

At scale, expect ~2-3% cost increase. Eliminating retry logic from parsing failures usually compensates.

### Reasoning Degradation

ACL 2025 research: constrained models drop **17.1% in accuracy** on structured tasks. Forcing JSON during reasoning degrades quality by 10-15%.

**Two-step workaround**: Let the model reason freely first, then convert to structured format. Improved aggregation accuracy from 48% to 61%, with only 12% token cost increase.

### Alternative Formats

For high-volume tabular input, the TOON format uses **40% fewer tokens** than JSON. For output, JSON with constrained decoding remains standard.

---

## 7. Prompt Compression

Compression reduces the token count of prompts while preserving semantic content. Two families:

### Hard Prompt (Token Selection)

Remove or rephrase tokens without changing the prompt modality. The model sees natural language.

| Method | Approach | Speed |
|--------|----------|-------|
| LLMLingua | Perplexity-based token filtering | Baseline |
| LLMLingua-2 | BERT-level token classification (distilled from GPT-4) | 3-6x faster |
| SelectiveContext | Bottom-up filtering via small LM | Fast |

### Soft Prompt (Embedding Compression)

Encode prompts into continuous embeddings or KV pairs. Higher compression ratios but requires model-specific training.

| Method | Compression | Notes |
|--------|------------|-------|
| Gist Tokens | Up to 26x | Zero-shot generalization via attention masking; 40% FLOPs reduction |
| AutoCompressor | Handles up to 30K tokens | Recursive sub-prompt compression |
| Soft prompt methods (general) | Up to 480x | Creates synthetic "language" for the LLM |

### Practical Trade-offs

Hard methods work out-of-the-box with any API (compress the text, send it). Soft methods require model modification or special inference setups -- not usable with hosted APIs.

For API users: LLMLingua-2 for general compression; manual pruning and summarization for most production use cases. Gist tokens are a research direction, not a production tool (yet).

Source: [Prompt Compression Survey (NAACL 2025)](https://arxiv.org/abs/2410.12388)

---

## 8. Model Routing

The single most impactful cost optimization. A typical distribution:

- **70%** of queries -> budget model (Haiku 4.5, GPT-4o mini, Gemini 2.5 Flash)
- **20%** of queries -> mid-tier (Sonnet 4.6, GPT-4o, Gemini 2.5 Pro)
- **10%** of queries -> premium (Opus 4.6, GPT-5, o3)

Saves **60-80%** vs routing everything through a premium model.

### Routing Techniques

| Technique | Savings | How It Works |
|-----------|---------|-------------|
| Classifier routing | 60-80% | Lightweight model predicts complexity, routes to cheapest adequate model |
| Cascade (FrugalGPT) | 50-98% | Start cheap, escalate only if confidence is low |
| Hybrid cascade | +14% over either alone | Combines classifier routing with cascading (ETH Zurich, PMLR 2025) |
| Answer consistency | ~60% | Use cheap model's consistency as difficulty signal |

### Plan-and-Execute

Use an expensive model to plan, cheap models to execute. One Opus planning call + 10 Haiku execution calls costs far less than 11 Opus calls.

```
Opus plans (1 call, ~$0.05) -> Haiku executes (10 calls, ~$0.05 total)
vs Opus does everything (11 calls, ~$0.55)
```

### Services

[Requesty](https://www.requesty.ai), [Portkey](https://portkey.ai), [OpenRouter](https://openrouter.ai) -- all offer routing infrastructure.

---

## 9. Prompt Caching

### Anthropic

Explicitly opt-in via `cache_control` markers. Processing order: Tools -> System -> Messages.

| Operation | Cost Multiplier | Break-even |
|-----------|----------------|------------|
| Cache write (5-min TTL) | 1.25x input | 2 reads |
| Cache write (1-hour TTL) | 2.00x input | 3 reads |
| Cache read | 0.10x input | -- |

A 100K-token system prompt on Opus 4.6: $0.50/request uncached, $0.05/request cached. **90% savings** after break-even.

Latency: up to **85% reduction** on long prompts (100K prompt dropped from 11.5s to 2.4s).

Workspace isolation since February 2026 -- caches are per-workspace, not per-org.

### OpenAI

Automatic for prompts >1,024 tokens. Free writes, 50% read discount, 5-10 minute TTL. Simpler but less aggressive savings (50% vs Anthropic's 90%).

### Design for Cache-Friendliness

1. Static content first (tools, system instructions, reference material)
2. Dynamic content after the cache breakpoint (user messages, timestamps)
3. Do not inject per-request data into the system prompt
4. Use up to 4 explicit breakpoints for content with different change frequencies
5. Pad short prompts above the minimum cacheable threshold if close

### Minimum Cacheable Tokens

| Model | Minimum |
|-------|---------|
| Opus 4.6 / Haiku 4.5 | 4,096 |
| Sonnet 4.6 | 2,048 |
| Sonnet 4.5/4, Opus 4.1/4 | 1,024 |

---

## 10. Context Window Management

### Lost-in-the-Middle

LLMs show a U-shaped performance curve on long contexts. Performance degrades **>30%** when critical information sits in the middle vs beginning or end (Stanford/UW).

Root causes (MIT 2025): causal masking gives early tokens more accumulated attention weight; RoPE positional embeddings introduce long-term decay. This is an architectural artifact, not a training gap.

### RAG vs Context Stuffing

RAG retrieves only relevant chunks. Research shows RAG preserves **95% of accuracy** using **25% of tokens** -- a **75% cost reduction**.

Context stuffing (dumping everything) degrades quality, increases hallucination risk, and costs linearly with context length.

### Best Practices

- **Document ordering**: most relevant information at beginning and end; avoid burying critical facts in the middle
- **Aggressive filtering**: retrieve generously, rerank, keep top 3-5 documents
- **Conversation summarization**: summarize old turns instead of carrying full history (10K tokens -> 1K summary)
- **Semantic chunking**: split by paragraph/section boundaries with 10-20% overlap
- **Effective length < advertised**: many models regress past tens of thousands of tokens on complex reasoning. 1M context does not mean you should use 1M tokens.

---

## 11. Batching and Application Caching

### Batch APIs

All major providers offer **50% discounts** for async batch processing:

| Provider | Max Requests | Completion Time | Discount |
|----------|-------------|-----------------|----------|
| Anthropic | 10,000/batch | <24h (most <1h) | 50% |
| OpenAI | 50,000/batch | <24h | 50% |
| Google | -- | <24h | 50% |

Combined with prompt caching: up to **95% savings** on input tokens.

Use for: evaluations, content moderation, data generation, document summarization.
Avoid for: real-time interactions, low-volume requests, iterative feedback loops.

### Semantic Caching

Application-level caching that matches queries by **vector similarity** rather than exact text. A query about "password reset" matches cached "how to reset my password."

Reported results: >80% cache hit rates, 40-90% cost reduction, up to 65x latency improvement.

Tools: [GPTCache](https://github.com/zilliztech/GPTCache), Bifrost (Maxim AI), Upstash Semantic Cache, Redis + LangChain.

**Warning**: Semantic caching is vulnerable to cache poisoning -- an attacker crafts a query that caches a malicious response, then legitimate similar queries return the poisoned answer. See [note 19](19_Token_Based_Attacks_And_Resource_Exploitation.md).

### Streaming

Token costs are identical for streaming vs non-streaming. Streaming is a UX optimization (time-to-first-token), not a cost optimization. Use when a human is watching; skip for automated pipelines.

---

## 12. Agent Loop Optimization

### Fewer Tools = Better

Vercel removed 80% of their agent's tools and got better results: fewer steps, fewer tokens, higher success rates. Tool descriptions and selection logic compound with every tool in the toolkit.

### Framework Token Efficiency

| Framework | Overhead | Notes |
|-----------|---------|-------|
| LangChain/LangGraph | ~900 tokens (simple task) | Lowest overhead |
| AutoGen | Medium | Strong for code execution |
| CrewAI | ~3x LangChain | Hierarchical process adds extra LLM calls per delegation |

Framework overhead is typically $5-20/month -- LLM API calls dominate total cost. Common pattern: prototype in CrewAI, ship in LangGraph.

### Parallel Execution

Run independent sub-tasks simultaneously. Saves wall-clock time without increasing token cost. Avoid for small tasks -- sub-agent overhead (system prompts, tool descriptions) can exceed the task itself.

### Sub-Agent Architecture

- **Planner** (expensive model, few calls)
- **Executors** (cheap model, many calls)
- **Reviewer** (mid-tier model, few calls)

Keep sub-agent summaries to 1K-2K tokens when reporting results back to the orchestrator.

---

## 13. Claude Code Cost Management

Average cost: **$6/developer/day** (90th percentile: $12/day).

### High-Impact Optimizations

| Technique | Savings | How |
|-----------|---------|-----|
| `.claudeignore` | ~50% of token budget | Exclude build artifacts, lock files, vendored deps |
| Concise CLAUDE.md (<200 lines) | Reduces per-session overhead | 500-2,000 tokens loaded every session |
| `/clear` between tasks | Eliminates stale context | Prevents irrelevant history from inflating tokens |
| `/compact` for exploration | Reduces output tokens | Shorter responses during codebase exploration |
| Delegate to subagents | Keeps main context clean | Verbose test/log output stays in subagent context |
| Reduce extended thinking | Output token savings | `/effort` command or `MAX_THINKING_TOKENS=8000` |

### Context Composition

80% of Claude Code's context is file reads and tool results. Only 20% is messages and responses. Optimizing what gets read has far more impact than shortening your prompts.

### Subagent Model Selection

`CLAUDE_CODE_SUBAGENT_MODEL` controls research subagents and the planning agent. Setting it to a weak model causes compounding errors. Sonnet is the safe default: ~40% cheaper than Opus with minimal quality loss on exploration tasks.

### Agent Teams Warning

Agent teams use ~**7x more tokens** than standard sessions. Each teammate maintains its own context window.

### Subscription vs API

Claude Max ($100-200/month flat rate) breaks even at roughly $100/month in API usage.

---

## 14. Security Implications

Full treatment in [note 19](19_Token_Based_Attacks_And_Resource_Exploitation.md). Key overlaps with optimization:

- **Denial of wallet**: Attackers exploit per-token pricing to drain budgets. All cost optimizations (budgets, routing, rate limiting) double as DoW defenses.
- **Reasoning exhaustion**: Extended thinking creates a new attack surface. ReasoningBomb achieves 286x amplification (60 input tokens -> 17K output tokens). Adaptive thinking partially mitigates by letting the model skip unnecessary reasoning.
- **Context window poisoning**: Long-context exploitation of the "lost in the middle" blind spot. RAG pre-filtering and structured prompt layouts defend against this.
- **Semantic cache poisoning**: Application-level semantic caching can be poisoned to serve malicious cached responses.
- **Prompt leaking**: Cached prompts create timing side channels (cached responses are faster). Logprob access enables model fingerprinting and prompt extraction.
- **System prompt extraction**: System prompts are not secret. Do not store credentials, internal URLs, or sensitive configuration in them. Cross-architecture extraction templates achieve 100% ASR.

---

## 15. Sources

### Pricing
- [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Google Gemini Pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [CostGoat LLM API Comparison](https://costgoat.com/compare/llm-api) -- 305+ models compared
- [MetaCTO -- Claude API Pricing Breakdown](https://www.metacto.com/blogs/anthropic-api-pricing-a-full-breakdown-of-costs-and-integration)

### Context Engineering and Prompt Design
- [Anthropic -- Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic -- Managing Context on the Claude Developer Platform](https://www.anthropic.com/news/context-management)
- [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Claude XML Tag Structuring](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags)
- [Lakera -- Prompt Engineering Guide 2026](https://www.lakera.ai/blog/prompt-engineering-guide)

### Few-Shot, CoT, and Prompt Strategy
- [Cheng et al. -- Revisiting Chain-of-Thought Prompting (EMNLP 2025)](https://arxiv.org/abs/2506.14641)
- [Sypherd et al. -- Big-O_tok (May 2025)](https://arxiv.org/abs/2505.14880)
- [Prompt Compression Survey (NAACL 2025)](https://arxiv.org/abs/2410.12388)
- [Mu et al. -- Learning to Compress Prompts with Gist Tokens](https://arxiv.org/abs/2304.08467)

### Extended Thinking
- [Claude Extended Thinking Docs](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
- [Claude Adaptive Thinking Docs](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
- [Anthropic -- Visible Extended Thinking](https://www.anthropic.com/news/visible-extended-thinking)

### Structured Output
- [Claude Structured Outputs Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Towards Data Science -- Anthropic Structured Output Capabilities](https://towardsdatascience.com/hands-on-with-anthropics-new-structured-output-capabilities/)
- [Let's Data Science -- Structured Outputs and Constrained Decoding](https://www.letsdatascience.com/blog/structured-outputs-making-llms-return-reliable-json)
- [Hannecke -- Beyond JSON: Picking the Right Format](https://medium.com/@michael.hannecke/beyond-json-picking-the-right-format-for-llm-pipelines-b65f15f77f7d)

### Model Routing
- [FrugalGPT (Stanford)](https://arxiv.org/abs/2305.05176)
- [Unified Cascade Routing (ETH Zurich, PMLR 2025)](https://files.sri.inf.ethz.ch/website/papers/dekoninck2024cascaderouting.pdf)
- [Portkey -- FrugalGPT Implementation](https://portkey.ai/blog/implementing-frugalgpt-smarter-llm-usage-for-lower-costs/)

### Caching
- [Anthropic Prompt Caching Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [OpenAI Prompt Caching Guide](https://developers.openai.com/api/docs/guides/prompt-caching)
- [PromptHub -- Caching Comparison (OpenAI, Anthropic, Google)](https://www.prompthub.us/blog/prompt-caching-with-openai-anthropic-and-google-models)
- [GPTCache (Zilliz)](https://github.com/zilliztech/GPTCache)

### Context Window and RAG
- [Liu et al. -- Lost in the Middle (Stanford/UW)](https://arxiv.org/abs/2307.03172)
- [Pinecone -- Why Use Retrieval Instead of Larger Context](https://www.pinecone.io/blog/why-use-retrieval-instead-of-larger-context/)
- [Redis -- Context Window Management](https://redis.io/blog/context-window-management-llm-apps-developer-guide/)

### Token Budgeting
- [TALE: Token-Budget-Aware LLM Reasoning (ACL 2025)](https://aclanthology.org/2025.findings-acl.1274.pdf)
- [BudgetThinker (OpenReview)](https://openreview.net/forum?id=ahatk5qrmB)

### Batching
- [Anthropic Batch Processing Docs](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- [OpenAI Batch API Guide](https://developers.openai.com/api/docs/guides/batch)

### Agent Loop Optimization
- [AgentFlow (Stanford, ICLR 2026 Oral)](https://agentflow.stanford.edu/)
- [LangGraph vs CrewAI Comparison](https://markaicode.com/vs/langgraph-vs-crewai-multi-agent-production/)
- [Armin Ronacher -- Agentic Coding Recommendations](https://lucumr.pocoo.org/2025/6/12/agentic-coding/)

### Claude Code Cost Management
- [Claude Code -- Manage Costs Effectively](https://code.claude.com/docs/en/costs)
- [SystemPrompt -- Claude Code Cost Optimisation](https://systemprompt.io/guides/claude-code-cost-optimisation)
- [ClaudeFast -- Token Usage Optimization Guide](https://claudefa.st/blog/guide/development/usage-optimization)

### General Cost Optimization
- [Prem AI -- 8 Strategies That Cut API Spend by 80%](https://blog.premai.io/llm-cost-optimization-8-strategies-that-cut-api-spend-by-80-2026-guide/)
- [Maxim AI -- Reduce LLM Cost and Latency](https://www.getmaxim.ai/articles/how-to-reduce-llm-cost-and-latency-a-practical-guide-for-production-ai/)
- [IBM -- Token Optimization](https://developer.ibm.com/articles/awb-token-optimization-backbone-of-effective-prompt-engineering/)
