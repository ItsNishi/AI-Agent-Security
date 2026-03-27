# LLM Tokenization Deep Dive

## What Are Tokens?

Tokens are **not words, not characters**—they are **subword units** of variable length that form the bridge between human text and neural networks. Each token is a unique integer assigned by a model's tokenizer, and the model processes sequences of these integers, not raw text.

### Concrete Example: Tokenization Differences

The same sentence tokenizes differently across models:

"Artificial intelligence is transforming industries."

- **GPT-4 (cl100k_base)**: 6 tokens
- **Llama 2**: 8 tokens
- **Llama 3**: ~6 tokens (128K vocabulary)

GPT-4 assigns a single token to "intelligence" because it's common; Llama 2 breaks it into multiple tokens. This 30% difference in token count directly impacts API costs and context window consumption.

### Token Granularity Examples

Tokens can be:
- Complete words: "hello" = 1 token
- Subwords: "tokenization" = ["token", "ization"] = 2 tokens
- Punctuation: "," or "." = 1 token each
- Whitespace: A leading space = 1 token (e.g., " hello")
- Multi-word phrases: "international" might be 1 token in GPT-4o but 2 in older tokenizers

The actual split depends on the model's vocabulary—high-frequency subwords get their own tokens, while rare combinations are broken smaller.

---

## Tokenization Algorithms

### 1. Byte Pair Encoding (BPE)

BPE is the foundation for GPT models and most modern LLMs. Originally published in 1994 as a compression algorithm, it was repurposed for tokenization.

**How BPE Works:**

1. **Pre-tokenization**: Split text by whitespace and punctuation, append `_` to mark word boundaries
   - "hello world" becomes ["hello_", "world_"]

2. **Initialize vocabulary** with all unique characters:
   - Vocabulary: {h, e, l, o, _, w, r, d}

3. **Iteratively merge the most frequent adjacent pair** until target vocabulary size:
   - Most common: "l" + "l" → "ll"
   - Next: "ll" + "o" → "llo"
   - Continue until 50K, 100K, or 200K tokens

4. **Apply learned merges to new text**:
   - "hello" → apply all merge rules in order → output tokens

**Key Properties:**
- Deterministic: same text always produces same tokens
- Greedy merging: only the most frequent pair is merged each step
- No merge rule history saved (only final vocabulary)

**Models using BPE:**
- GPT-2, GPT-3, GPT-4: OpenAI's tiktoken BPE
- Llama 3: SentencePiece BPE variant
- Mistral: SentencePiece BPE

---

### 2. WordPiece

Developed by Google for BERT. Similar to BPE but with different merge heuristics.

**How WordPiece Differs:**

- Uses **frequency weighted by information content**, not raw frequency
- Merges pairs that appear together far more often than by chance (using likelihood ratios)
- Stores only the final vocabulary, not merge rules
- Uses `##` prefix for non-initial subwords: `["hello", "##world"]`

**Tokenization Strategy:**
- Starts from word beginning, greedily finds longest subword in vocabulary
- Falls back to shorter subwords if needed
- Marks continuations with `##`

Example: "unbelievable"
1. Check: "unbelievable" → not in vocab
2. Check: "unbel" → not in vocab
3. Check: "un" → in vocab, output "un"
4. Check: "believable" → in vocab, output "##believable"
5. Result: ["un", "##believable"]

**Models using WordPiece:**
- BERT, RoBERTa (older encoder-only models)
- Typical vocabulary: ~30,000 tokens (BERT has 30,522)

**Key Difference from BPE:**
- WordPiece often produces **longer subwords** because it only merges high-value pairs
- More "complete" words = fewer tokens on average, but this is context-dependent

---

### 3. SentencePiece: BPE and Unigram Variants

Developed by Google (2018) for language-agnostic tokenization. Handles languages without explicit word boundaries (Chinese, Japanese).

#### **SentencePiece BPE**

Nearly identical to standard BPE, with one key difference:
- Operates on **Unicode codepoints directly**, not bytes or characters
- Encodes spaces as `▁` (U+2581)
- No explicit pre-tokenization needed

**Used by:**
- Llama 3, Llama 2: 128K and 32K vocabularies
- Mistral: SentencePiece BPE
- XLNet: Pre-training on raw Unicode streams

**Advantages for multilingual text:**
- Naturally handles CJK (Chinese, Japanese, Korean) without special preprocessing
- Treats all languages equally during merge operations

#### **SentencePiece Unigram**

Works **opposite to BPE**: starts with a huge vocabulary, prunes down.

**Algorithm:**
1. Initialize vocabulary with 500K+ candidate subwords (via BPE prepass or exhaustive enumeration)
2. Fit a unigram language model: assign probability to each token based on corpus frequency
3. Use **Expectation-Maximization** to compute loss for each token
4. **Remove lowest-loss tokens** (ones that hurt the model less if removed)
5. Repeat until reaching target vocabulary size (e.g., 256K)
6. During inference, use **Viterbi decoding** to find the most probable token sequence

**Key Insight:**
- Instead of greedy merges, it measures which tokens are *most valuable* to the model
- A rare but highly informative token is kept; a common but redundant token is pruned
- Probabilistic: can output multiple valid tokenizations for the same text

**Used by:**
- T5, BigBird, Pegasus: older encoder models
- Gemini, Gemma: large vocabulary (256K) with Unigram
- XLM-RoBERTa: multilingual

**Pros:** Optimal compression for the corpus; better for rare words
**Cons:** Slower inference (requires EM iterations during training); slightly non-deterministic behavior possible

---

## Vocabulary Sizes: How Many Tokens Each Model Knows

| Model/Tokenizer | Vocabulary Size | Notes |
|---|---|---|
| GPT-2 | ~50K | Original BPE |
| GPT-3 (0-shot) | ~50K | Same as GPT-2 |
| GPT-3.5 / GPT-4 (cl100k_base) | 100,257 | OpenAI's tiktoken |
| **GPT-4o (o200k_base)** | **200,000** | Doubled vocabulary; better multilingual |
| Claude 3 / 3.5 (Sonnet) | ~65,000 | Proprietary Anthropic tokenizer; closed-source |
| Llama 2 | 32,000 | SentencePiece BPE |
| **Llama 3** | **128,256** | 4x expansion; 15% fewer tokens than Llama 2 for English |
| Mistral 7B | ~32,000 | SentencePiece BPE (similar to Llama 2) |
| **Gemini / Gemma** | **256,000** | SentencePiece Unigram; largest publicly documented |

### Key Observations:

1. **Larger ≠ Better**: Gemini's 256K vocab doesn't always mean fewer tokens. Token efficiency depends on the training corpus quality and how well the vocabulary matches your use case.

2. **GPT-4o's expansion** (50K → 200K) focuses on:
   - Improved handling of languages with non-Latin scripts (Chinese, Arabic, Korean)
   - Better compression for structured text and code
   - Modest improvements in English (1-5% fewer tokens)

3. **Claude's closed vocabulary** (65K) is significantly smaller than GPT-4 (100K) but optimized for Anthropic's training data. Some sources report it fragments code more than GPT-4, leading to higher token counts for technical content.

---

## Token Costs in Practice

### Rule of Thumb (English)

- **1 token ≈ 4 characters**
- **1 token ≈ 0.75 words** (equivalently, 1 word ≈ 1.33 tokens)
- **100 tokens ≈ 75 words**
- **1–2 sentences ≈ 30 tokens**
- **1 paragraph ≈ 100 tokens**

### Real-World Examples

**Short texts:**
- "Hello, world!" = 4 tokens
- Wayne Gretzky quote: "You miss 100% of the shots you don't take" = 11 tokens

**Typical emails:**
- Brief response (2-3 sentences): 50–150 tokens
- Standard email (5-10 sentences): 200–500 tokens
- Long email with attachments or quotes: 1,000–2,000 tokens

**One page of prose** (500 words):
- ~667 tokens (1.33 tokens per word)
- Equivalent to ~2,000 characters

**Full-length novel:**
- "The Great Gatsby" (~47K words): ~63K tokens
- "War and Peace" (~560K words): ~750K tokens
- 1 million tokens ≈ 1.33 × "War and Peace"

### Source Code vs. Prose

Code is **15–40% more token-dense** than English prose:
- Symbols, operators, variable names with underscores/camelCase are often broken into multiple tokens
- Python/JavaScript: longer token counts per visual line than equivalent English
- Modern tokenizers (Qwen-2.5, DeepSeek-V3, Llama 3) include programming-specific tokens, improving efficiency by 15–40% vs. older tokenizers
- WordPiece (BERT) is worst for code: ~4.5 tokens per instruction; Unigram is best: ~2 tokens per instruction

**Example:**
```python
def calculate_fibonacci(n):
    return 42
```
GPT-4: ~15 tokens
Older BERT: ~25 tokens

### Non-English Languages (Multilingual Tax)

**CJK (Chinese, Japanese, Korean):**
- **Chinese**: ~2x more tokens than English for equivalent information
- **Japanese**: ~3x more tokens than English (each character often = 1 token)
- **Korean**: ~1.5–2x more tokens than English

**Root Cause:**
- Traditional BPE using UTF-8: CJK characters require 3–4 bytes, each processed separately
- CJK languages don't use spaces; each character is a semantic unit
- SentencePiece Unigram helps more than BPE for CJK

**Mitigation:**
- Gemini's 256K vocabulary includes more CJK tokens, reducing the penalty
- Llama 3's 128K vocabulary (vs. 32K Llama 2) improves multilingual efficiency by ~15%
- UTF-16-based BBPE16 reduces CJK tokens by up to 10.4% vs. standard UTF-8 BPE

**Example: Same meaning, different token costs**
- English: "Hello world" = 2 tokens
- Chinese: "你好世界" (hello world) = 4–5 tokens (typically 1 token per character)
- Japanese: "こんにちは世界" (hello world) = 8–9 tokens

---

## Context Windows Explained

A context window is the maximum number of **input + output tokens** a model can process in one request.

### What is a Context Window?

- **Input tokens**: All text you send (system prompt, user message, documents, images, tools)
- **Output tokens**: All text the model generates (response, reasoning, tool calls)
- **Total context**: Input + output must not exceed the window

### Context Window Sizes (2026)

| Model | Context Window | Notes |
|---|---|---|
| GPT-3.5 | 4K / 16K | Legacy; rarely used |
| GPT-4 / GPT-4 Turbo | 8K / 128K | Older, less widely deployed |
| **GPT-4o** | **128K** | Current OpenAI flagship |
| Claude Opus 4 | 200K | Anthropic flagship |
| Claude 3.5 Sonnet | 200K | Latest; claims best reasoning at scale |
| Llama 3.1 | 128K | Open-source; widely deployed |
| Gemini 2.0 Flash | 1M | Experimental; longest window |
| DeepSeek-V3 | 64K | Cost-optimized |

### Bigger Isn't Always Better

**The "Lost in the Middle" Problem:**
A 2023 Stanford study found that LLMs perform worse when relevant information is placed in the middle of the context window. Performance follows a **U-shaped curve**:

- **Beginning of context**: High performance (↑ 95% accuracy)
- **Middle of context**: Low performance (↓ 60–70% accuracy; -30% drop)
- **End of context**: High performance (↑ 95% accuracy)

**Why?**
- Tokens at the start get attended to by every subsequent token, accumulating attention weight
- Middle tokens have limited visibility: only tokens after them can attend to them
- Positional encodings (like RoPE) introduce distance-based decay, penalizing far-apart token pairs

**Practical Implication:**
With a 128K context, putting a critical document in the middle is often worse than using a 16K context with the document at the start or end. Many RAG systems compensate by:
1. Ranking retrieved documents by relevance
2. Placing highest-ranked at beginning and end
3. Placing lower-ranked in middle
4. Limiting document count rather than filling the entire window

**Emerging Solutions:**
- Positional interpolation: fine-tune models to handle longer contexts at their boundaries
- Multi-scale positional encoding (Ms-PoE): plug-and-play positional encoding that reduces "lost in middle" without fine-tuning
- Selective attention mechanisms: attend to entire context at once, not sequentially

---

## Input vs. Output Token Costs

Output tokens cost **3–5x more** than input tokens. This is not a pricing arbitrage; it reflects fundamental computational differences.

### Why Output is Expensive: Autoregressive Generation

**Input processing:**
- The model reads the entire input in one forward pass
- All input tokens are processed in **parallel** using transformer attention
- Computational cost scales linearly with input tokens (with quadratic attention, but still one pass)

**Output generation:**
- The model generates one token at a time, each conditioned on all previous tokens
- Process is **sequential** and cannot be parallelized
- For a 1,000-token output, the model runs 1,000 separate forward passes
- Each forward pass incurs full attention cost: O(context_length²)

**Example: Total compute for 1K input + 100 output**
- Input cost: O(1K²) = 1M operations (one pass)
- Output cost: 100 × O((1K + output_position)²) ≈ 100 × O(1M) = 100M operations
- Ratio: 100:1, justifying the 3–5x token multiplier (accounting for efficiency gains in batch processing)

### Pricing Hierarchy (2026)

OpenAI GPT-4o:
- Input: $2.50 / 1M tokens
- Output: $10.00 / 1M tokens
- Ratio: 4x

Anthropic Claude 3.5 Sonnet:
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens
- Ratio: 5x

### Hidden Cost: Context Window Creep

In long conversations, the cost of maintaining context can exceed the cost of generating the response.

**Example: 10-turn conversation**
- System prompt (always sent): 200 tokens
- Previous turns (accumulated): 2K tokens
- Current user message: 100 tokens
- Total input: 2.3K tokens
- Model output: 300 tokens

Cost breakdown:
- Input (2.3K × $0.0000025): $0.00575
- Output (300 × $0.0000100): $0.00300
- **Input is 65% of cost** even though output seems "active"

Over 100 turns, the 200-token system prompt costs as much as 80 output tokens, for minimal semantic value.

### Optimization Strategy

1. Compress system prompts (e.g., use brief templates instead of verbose instructions)
2. Summarize old conversation turns instead of appending full histories
3. Use smaller models for simple tasks (Claude Haiku, GPT-4o mini)
4. Cache system prompts if the API supports it (Claude's prompt caching: 10% input cost for cached tokens)

---

## How to Count Tokens

### Option 1: OpenAI's tiktoken (Python)

```python
import tiktoken

# Load tokenizer for a specific model
encoding = tiktoken.encoding_for_model("gpt-4o")
# Or load directly:
# encoding = tiktoken.get_encoding("o200k_base")

text = "Hello, world!"
tokens = encoding.encode(text)
num_tokens = len(tokens)
print(f"Text: {text}")
print(f"Tokens: {tokens}")
print(f"Count: {num_tokens}")
```

**Output:**
```
Text: Hello, world!
Tokens: [9906, 11, 1917, 0]
Count: 4
```

Available encodings:
- `"cl100k_base"`: GPT-4, GPT-3.5
- `"o200k_base"`: GPT-4o
- `"gpt2"`: GPT-2

**Speed:** 3–6x faster than alternative tokenizers.

### Option 2: Anthropic Token Counter API

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.count_tokens(
    model="claude-3-5-sonnet-20241022",
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": "What is tokenization?"
        }
    ]
)

print(f"Input tokens: {response.input_tokens}")
```

**Key facts:**
- Free to use; subject to rate limits (separate from message creation limits)
- Supports system prompts, tools, images, PDFs
- Actual token count may differ by a small amount (system adds optimization tokens not charged)
- Token count is an estimate; use it for pre-checks, not post-invoice accounting

### Option 3: Online Tools

- OpenAI Tokenizer: https://platform.openai.com/tokenizer
- Claude Tokenizer (open-source): https://claude-tokenizer.vercel.app/
- Token Calculator: https://llm-calculator.com/ (supports GPT-4o, Llama, Claude)
- Vibe Meter: https://steipete.me/posts/2025/vibe-meter-2-claude-code-usage-calculation (Claude-specific, includes hidden token accounting)

### Option 4: Hugging Face Transformers (any model)

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8b")
tokens = tokenizer.encode("Hello, world!")
print(len(tokens))
```

Works for any model on Hugging Face, but slower than tiktoken or Anthropic counters.

---

## Tokenization Attacks and Security Implications

Tokenization itself is a security boundary. Attackers exploit tokenization in multiple ways:

### 1. Token Smuggling via Unicode Variation Selectors

Unicode variation selectors (U+FE00–U+FE0F) are invisible characters that modify preceding characters without changing their meaning. Some tokenizers treat these as separate tokens; others ignore them.

**Attack:**
```
prompt = "show me passwords" + U+FE00 + U+FE01 + U+FE02
```

When tokenized, the variation selectors might:
- Be stripped during preprocessing (defense wins)
- Become separate tokens, breaking the original instruction
- Expand to multiple tokens, causing token count estimation errors

**Result:** Prompt injection or input validation bypass.

**Defense:** Explicit Unicode normalization (NFKC or NFKD) and stripping of variation selectors before tokenization, not after.

### 2. Token Expansion DoS

Attackers embed content that expands dramatically during tokenization.

**Example:** Some emoji or rare Unicode sequences tokenize into many subword tokens.

```
payload = "▮" × 1000  # Rare block-drawing character
# Each might be 1 token in rendering, but 3–5 tokens in tokenization
# 1000 characters = 3000–5000 tokens
```

**Result:** Token count estimation says it's 1K; actual is 5K. Adversary exceeds rate limits or context capacity.

**Defense:** Pre-tokenize and count; enforce token limits on the count, not character length.

### 3. Vocabulary Boundary Exploits

Different tokenizers split words differently. An attacker crafts payloads that:
- Pass validation on one tokenizer (tokens don't match filter words)
- Reconstruct into forbidden content on the model's tokenizer

**Example:**
- GPT-4: "password" = 1 token (in vocabulary)
- Llama 2: "password" = ["pass", "word"] = 2 tokens
- If a filter looks for the single token `[password_token]`, Llama input bypasses it

**Defense:** Tokenize with the exact model's tokenizer before filtering; don't assume vocabulary consistency.

### 4. Prompt Injection via Normalization

Unicode normalization (NFD, NFC, NFKD, NFKC) can decompose characters:

```
NFC("ﬁ") = "fi"       # Ligature decomposes to two chars
NFKC("ℌ") = "H"       # Mathematical Alphanumeric decomposes to ASCII
```

When a filter normalizes and a tokenizer doesn't (or vice versa), payloads slip through.

**Defense:** Normalize before tokenization, apply filters after, tokenize the normalized result.

---

## Summary and Key Takeaways

1. **Tokens ≠ words or characters**. They are vocabulary-dependent subword units, and the same text produces different token counts across models.

2. **Algorithm choice matters**:
   - **BPE** (GPT, Llama 3, Mistral): Fast, deterministic, greedy merges
   - **WordPiece** (BERT, older models): Smaller vocabularies, longer subwords
   - **Unigram** (Gemini, T5): Slower training, optimal compression, probabilistic

3. **Vocabulary size** ranges from 30K (BERT) to 256K (Gemini). Bigger isn't always better; depends on your use case.

4. **Token efficiency**:
   - English prose: 1 token ≈ 4 characters, 0.75 words
   - Code: 15–40% more tokens per visual line than prose
   - CJK languages: 2–3x more tokens per semantic unit than English

5. **Context windows** are input + output, and relevant information in the middle performs 30% worse than at the boundaries ("lost in the middle").

6. **Output tokens cost 3–5x more** than input because generation is sequential, not parallel.

7. **Count tokens before deployment** using tiktoken (GPT), Anthropic's API (Claude), or Hugging Face Transformers (other models).

8. **Tokenization is a security boundary**. Unicode attacks, expansion attacks, and normalization mismatches can all exploit tokenization differences. Normalize, tokenize, then filter.

---

## References

### Tokenization Algorithms
- [Byte-pair encoding - Wikipedia](https://en.wikipedia.org/wiki/Byte-pair_encoding)
- [Implementing A Byte Pair Encoding (BPE) Tokenizer From Scratch - Sebastian Raschka](https://sebastianraschka.com/blog/2025/bpe-from-scratch.html)
- [Byte-Pair Encoding tokenization - Hugging Face LLM Course](https://huggingface.co/learn/llm-course/en/chapter6/5)
- [WordPiece tokenization - Hugging Face LLM Course](https://huggingface.co/learn/llm-course/en/chapter6/6)
- [Unigram tokenization - Hugging Face LLM Course](https://huggingface.co/learn/llm-course/en/chapter6/7)
- [SentencePiece Tokenizer Demystified - Towards Data Science](https://towardsdatascience.com/sentencepiece-tokenizer-demystified-d0a3aac19b15)

### Model-Specific Tokenization
- [GitHub - kaisugi/gpt4_vocab_list - GPT-4o and GPT-4 tokenizer vocabulary lists](https://github.com/kaisugi/gpt4_vocab_list)
- [GitHub - openai/tiktoken - OpenAI's tokenizer library](https://github.com/openai/tiktoken)
- [How to count tokens with Tiktoken - OpenAI Cookbook](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken)
- [Reverse Engineering Claude's Token Counter - Rohan Gupta](https://grohan.co/2026/02/10/ctoc/)
- [The Mystery of the Claude 3 Tokenizer - Sander Land](https://tokencontributions.substack.com/p/the-mystery-of-the-claude-3-tokenizer)
- [Token counting - Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- [In-depth understanding of Llama Tokenizer - Medium](https://medium.com/@manyi.yim/in-depth-understanding-of-llama-tokenizer-d91777025dab)
- [Dissecting Gemini's Tokenizer and Token Scores](https://dejan.ai/blog/gemini-toknizer/)

### Token Efficiency and Costs
- [Tokenization Speed and Efficiency Benchmarks (July 2025) - LLM Calculator](https://llm-calculator.com/blog/tokenization-performance-benchmark/)
- [How Different Tokenization Algorithms Impact LLMs - arXiv](https://arxiv.org/html/2511.03825v1)
- [Multilingual token compression in GPT-o family models](https://www.njkumar.com/gpt-o-multilingual-token-compression/)
- [Why Output & Reasoning Tokens Inflate LLM Costs (2026 Guide) - Code Ant](https://www.codeant.ai/blogs/input-vs-output-vs-reasoning-tokens-cost)
- [How does LLM inference work? - BentoML LLM Inference Handbook](https://bentoml.com/llm/llm-inference-basics/how-does-llm-inference-work/)
- [Autoregressive Generation: How GPT Generates Text Token by Token - Michael Brenndoerfer](https://mbrenndoerfer.com/writing/autoregressive-generation-gpt-text-generation)

### Multilingual and Non-English Tokenization
- [Working with Chinese, Japanese, and Korean text in Generative AI pipelines](https://tonybaloney.github.io/posts/cjk-chinese-japanese-korean-llm-ai-best-practices.html)
- [Language Model Tokenizers Introduce Unfairness Between Languages - arXiv](https://arxiv.org/pdf/2305.15425)
- [BBPE16: UTF-16-based Byte-Level Byte-Pair Encoding for Improved Multilingual Speech Recognition - arXiv](https://arxiv.org/html/2602.01717)

### The "Lost in the Middle" Problem
- [Lost in the Middle: How Language Models Use Long Contexts - arXiv 2307.03172](https://arxiv.org/abs/2307.03172)
- [Lost in the Middle: How Language Models Use Long Contexts - Stanford PDF](https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.arxiv2023.pdf)
- [The 'Lost in the Middle' Problem — Why LLMs Ignore the Middle of Your Context Window - DEV Community](https://dev.to/thousand_miles_ai/the-lost-in-the-middle-problem-why-llms-ignore-the-middle-of-your-context-window-3al2)
- [Found in the Middle: How Language Models Use Long Contexts Better via Plug-and-Play Positional Encoding - arXiv](https://arxiv.org/html/2403.04797v1)

### Tokenization Security
- [Unicode Exploits Are Compromising Application Security - Prompt Security](https://prompt.security/blog/unicode-exploits-are-compromising-application-security)
- [Unicode Normalization Attacks: When "admin" ≠ "admin" - Medium](https://medium.com/@instatunnel/unicode-normalization-attacks-when-admin-admin-32477c36db7f)
- [Unicode Normalization Vulnerabilities & the Special K Polyglot - AppCheck](https://appcheck-ng.com/unicode-normalization-vulnerabilities-the-special-k-polyglot/)
- [Black Box Emoji Fix – A Unicode Sanitization Method for Mitigating Emoji-Based Injection Attacks in LLM Systems](https://www.tdcommons.org/dpubs_series/7836/)

### Token Counting Tools
- [Token Calculator & Cost Estimator (2026) - token-calculator.net](https://token-calculator.net/)
- [Vibe Meter 2.0: Calculating Claude Code Usage with Token Counting - Peter Steinberger](https://steipete.me/posts/2025/vibe-meter-2-claude-code-usage-calculation)
- [Tiktoken Tutorial: OpenAI's Python Library for Tokenizing Text - DataCamp](https://www.datacamp.com/tutorial/tiktoken-library-python)
