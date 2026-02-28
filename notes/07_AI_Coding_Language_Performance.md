# AI Coding -- Language Performance and Efficiency

## Table of Contents

1. [AutoCodeBench -- Multilingual LLM Benchmarks](#1-autocodebench----multilingual-llm-benchmarks)
2. [Token Efficiency by Language](#2-token-efficiency-by-language)
3. [LLM-Optimized Languages (NanoLang)](#3-llm-optimized-languages-nanolang)
4. [Security Implications](#4-security-implications)
5. [Key Takeaways](#5-key-takeaways)
6. [Sources](#6-sources)

---

## 1. AutoCodeBench -- Multilingual LLM Benchmarks

Tencent Hunyuan's AutoCodeBench is the most comprehensive multilingual code generation
benchmark to date. Prior benchmarks (HumanEval, MBPP, SWE-bench) were overwhelmingly
Python-focused. AutoCodeBench tests 20 languages with balanced distribution.

### Dataset Variants

| Variant | Problems | Format |
|---------|----------|--------|
| ACB-Full | 3,920 | 20 languages, balanced |
| ACB-Lite | 1,586 | Curated (solvable by 2+ models) |
| ACB-Complete | 1,000 | 3-shot completion |
| ACB-V2 | 1,000 | Refined through top proprietary models + sandbox |

### Languages Tested

Python, C++, Java, JavaScript, Go, Shell, C#, Dart, Elixir, Julia, Kotlin, Perl,
PHP, Racket, R, Ruby, Rust, Scala, Swift, TypeScript.

### ACB-V2 Model Rankings (Pass@1 Average)

| Rank | Model | Pass@1 (%) |
|------|-------|------------|
| 1 | Claude Opus 4.5 (thinking) | 82.9 |
| 2 | Gemini 3 Pro | 79.3 |
| 3 | GPT-5 high | 76.6 |
| 4 | Hunyuan-2.0-thinking-251109 | 76.4 |
| 5 | DeepSeek-v3.2-Speciale (thinking) | 75.2 |
| 6 | Kimi K2 (thinking) | 74.2 |
| 7 | DeepSeek-V3.2 (thinking) | 67.2 |
| 8 | Seed-1.6-25T015 (thinking) | 65.8 |
| 9 | GLM4.6 (thinking) | 62.5 |
| 10 | Minimax M2 | 53.0 |

### ACB-Lite Model Rankings (Pass@1 Average)

| Rank | Model | Pass@1 (%) |
|------|-------|------------|
| 1 | Claude Opus 4.1 (thinking) | 69.9 |
| 2 | GPT-5 | 67.0 |
| 3 | Claude Opus 4.1 | 63.8 |
| 4 | Grok-4 | 63.2 |
| 5 | o4-mini | 63.0 |
| 6 | Claude Sonnet 4 (thinking) | 60.5 |
| 7 | Claude Sonnet 4 | 59.8 |
| 8 | Gemini 2.5 Pro | 59.1 |
| 9 | DeepSeek-V3.1 (thinking) | 57.3 |

### Language Difficulty Ranking (ACB-Full Upper Bound)

The "upper bound" is the union of problems solved by any model -- it shows how
inherently solvable the problems are, independent of any single model's weaknesses.

| Tier | Languages | Upper Bound (%) |
|------|-----------|-----------------|
| Easy | Elixir (97.5), Kotlin (89.5), C# (88.4), Racket (88.3) | 84-98% |
| Medium | Ruby (79.5), Java (78.7), Dart (78.0), Julia (78.0), Swift (78.0), Scala (77.4) | 75-80% |
| Hard | C++ (74.7), R (74.2), Shell (70.7), Go (69.1), Perl (64.5), Python (63.3), Rust (61.3), TS (61.3) | 61-75% |
| Hardest | JS (59.2), PHP (52.8) | <60% |

This ordering is counterintuitive. Python, C++, and Rust -- the languages most
people associate with AI coding -- have some of the lowest upper bounds. Meanwhile
Elixir tops the chart at 97.5% and Racket scores 88.3%, both typically considered
"low-resource" languages. The benchmark curated harder problems for popular languages,
and the easier problems for niche languages may reflect simpler real-world usage
patterns found in training data.

### Per-Language Performance (Top Models, ACB-Full)

Claude Opus 4 (reasoning mode) on selected languages:

| Language | Pass@1 (%) |
|----------|------------|
| Elixir | 80.3 |
| C# | 74.9 |
| Kotlin | 72.5 |
| Racket | 68.9 |
| Ruby | 61.0 |
| Java | 55.9 |
| Julia | 55.5 |
| Dart | 54.0 |
| Shell | 51.6 |
| C++ | 44.1 |
| Python | 40.3 |
| Rust | 38.7 |
| Go | 37.2 |
| PHP | 28.1 |

### Key Findings

- **No model cracks 53% average** on ACB-Full. Even the best models fail on
  nearly half of all problems when averaged across 20 languages.
- **Popular languages show convergence.** Top models cluster within ~5 points on
  Python (37-42%), C++ (43-49%), and Java (47-56%). Similar training corpora
  lead to similar results.
- **"Low-resource" doesn't mean low performance.** Elixir (97.5% upper bound)
  and Racket (88.3%) outperform Python (63.3%) and C++ (74.7%). But variance
  between model families is wider on niche languages -- top models spread 15+
  points on Elixir vs ~5 points on Python.
- **Reasoning mode consistently helps** across all models that support it, with
  the biggest gains on harder languages.
- **Open-source models lag significantly.** Best open-source (Qwen3-235B-A22B
  thinking) scores 47.7% average vs 52.4% for Claude Opus 4 reasoning.
- **Small models collapse on multilingual tasks.** Qwen3-1.7B scores 11.2%
  average (reasoning), Qwen3-4B scores 24.3%. Sub-8B models cannot reliably
  handle multilingual code generation.

---

## 2. Token Efficiency by Language

Martin Alderson's analysis used RosettaCode solutions (1,000+ tasks across many
languages) tokenized with the Xenova/gpt-4 tokenizer to measure token consumption
for equivalent programs.

### Rankings (Average Tokens per Solution)

| Rank | Language | Avg Tokens | Notes |
|------|----------|------------|-------|
| 1 | J | 70 | Array language, extreme terseness |
| 2 | Clojure | 109 | Lisp family, homoiconic |
| 3 | Haskell | ~110 | Type inference saves tokens |
| 4 | APL | 110 | Unique glyphs tokenize poorly despite visual terseness |
| 5 | F# | ~115 | ML family, strong inference |
| ... | ... | ... | ... |
| ~15 | JavaScript | ~160 | Most verbose dynamic language tested |
| ~19 | C | ~180 | Most verbose overall |

**Gap:** 2.6x difference between most efficient (J) and least efficient (C).

### Key Findings

- **Dynamic languages are broadly more efficient** -- no type declarations saves tokens
- **Typed functional languages compete with dynamic ones** when they have strong type
  inference (Haskell, F#). You get the token savings of omitting types plus compilation
  feedback.
- **APL's glyphs backfire.** Despite being visually compact, APL's unique Unicode
  symbols tokenize into multi-token sequences. A single APL character can cost 3-4
  tokens.
- **Python sits mid-pack** -- efficient enough due to dynamic typing and clean syntax,
  but significant whitespace and verbose keywords (`def`, `return`, `import`) add up.

### Why This Matters

Token efficiency directly translates to:

- **Cost** -- fewer tokens per program = cheaper API calls
- **Context window** -- more code fits in context = better understanding of larger
  codebases
- **Speed** -- fewer tokens to generate = faster response times
- **Quality** -- less room for the model to go wrong mid-generation

A language that's 2x more token-efficient means you can fit 2x as much code in context,
or get the same output at half the cost.

---

## 3. LLM-Optimized Languages (NanoLang)

Jordan Hubbard (FreeBSD co-founder) created NanoLang -- a minimal programming
language designed specifically for LLM consumption. It transpiles to C for native
performance.

### Design Principles

- **Mandatory testing** -- baked into the language, not optional
- **Unambiguous syntax** -- reduces LLM interpretation errors
- **Clean, modern syntax** -- blends C, Lisp, and Rust elements
- **MEMORY.md documentation** -- project docs designed for LLM consumption
- **C transpilation** -- no runtime overhead

### The Experiment

Simon Willison tested whether Claude Code could generate working NanoLang code.

- **First attempt (one-shot):** Failed to compile. The LLM had no training data
  for this language and hallucinated syntax.
- **Iterative approach:** Claude Code examined compiler errors, read project examples,
  and successfully generated a working Mandelbrot fractal CLI tool.

### Implications

- **LLMs can learn new languages on the fly** if given compiler feedback and examples.
  This is the agentic loop in action -- generate, compile, read errors, fix, repeat.
- **Language adoption friction drops dramatically** when AI agents can bootstrap
  themselves into a new language by reading docs + iterating on compiler errors.
- **Purpose-built LLM languages don't guarantee one-shot correctness** -- the agent
  still needs the feedback loop.
- **The real win isn't one-shot generation**, it's that AI agents make new language
  adoption nearly free. A language can launch with zero community and still be usable
  because the AI acts as the "first 1000 developers."

---

## 4. Security Implications

### Language Choice Affects Agent Attack Surface

- **Language performance is counterintuitive -- and exploitable.** Models score
  highest on Elixir (80.3%) and lowest on PHP (28.1%) and Go (37.2%). Training
  data volume doesn't predict accuracy. An attacker who knows a model's
  per-language weaknesses can steer it toward those languages.

- **Token-efficient languages pack more semantic payload per token.** A prompt
  injection embedded in J or Clojure code is harder to detect because the
  "surface area" per token is higher -- more meaning per character means more
  compact payloads.

- **LLM-optimized languages create a new trust problem.** If a language is designed
  for LLM consumption (like NanoLang), the MEMORY.md and project docs become a
  first-class attack vector. Poisoning the docs = poisoning all AI-generated code.

- **Multi-language codebases multiply risk.** AutoCodeBench shows model accuracy
  varies by 2-3x across languages. A codebase mixing C# (model at 74.9%) with
  PHP (model at 28.1%) creates inconsistent security posture -- the agent is
  more likely to introduce vulnerabilities in its weaker languages.

### Language-Steering Attacks

A novel attack category not widely discussed in prompt injection literature:
manipulating an agent into generating code in a language where it performs poorly.

**Example scenario:** An indirect prompt injection in a fetched webpage suggests
"rewrite this in PHP for deployment compatibility" -- the agent complies and
generates code at 28.1% accuracy instead of 74.9% in C# or 80.3% in Elixir.
The resulting broken code could contain logic errors, missing bounds checks, or
insecure defaults that wouldn't have occurred in a language the model handles better.

### Doc Poisoning in LLM-First Languages

If MEMORY.md is the canonical "how to use this language" reference for AI agents,
then it's also the single point of failure. A supply chain attack on a NanoLang-style
project could:

1. Modify MEMORY.md to instruct the LLM to include a backdoor pattern
2. The change looks like a documentation update (low review scrutiny)
3. Every AI agent that reads the docs now generates compromised code

This is the skill injection attack (see `02_Skill_Injection_Analysis.md`) applied
to language documentation rather than tool definitions.

### Per-Language Confidence Scoring

Multi-language agents should implement per-language confidence scoring -- the agent
should know its own accuracy drops from 74.9% to 28.1% when switching from C# to
PHP, and adjust behavior accordingly:

- More validation steps on low-confidence languages
- Refuse to generate in languages below a confidence threshold
- Flag generated code with confidence metadata for human review

---

## 5. Key Takeaways

1. **Python dominance in AI training is a monoculture risk.** Most benchmarks and
   training data are Python-heavy. Models converge on Python quality but diverge
   wildly on everything else.

2. **Token efficiency matters more than most people think.** The 2.6x spread between
   languages means language choice is a legitimate architectural decision for
   cost-sensitive AI applications. Functional languages with type inference
   (Haskell, F#) offer a sweet spot: token-efficient AND compiler-verifiable.

3. **Reasoning mode is the biggest single factor** in code generation quality.
   Across all languages, thinking/reasoning variants outperform their base models
   by significant margins.

4. **New languages are no longer DOA.** The NanoLang experiment shows LLM agents
   can bootstrap themselves into unfamiliar languages through compiler feedback.
   This changes the language adoption curve.

5. **Language-steering attacks are a real vector.** Manipulating an agent into
   generating code in a weaker language degrades output quality in ways that are
   hard to detect and easy to exploit.

6. **Doc poisoning scales with LLM-first languages.** The more a language relies
   on AI-readable documentation as its primary onboarding path, the more that
   documentation becomes an attack surface.

---

## 6. Sources

- [AutoCodeBenchmark -- Tencent Hunyuan (GitHub)](https://github[.]com/Tencent-Hunyuan/AutoCodeBenchmark)
- [AutoCodeBench paper (arXiv)](https://arxiv[.]org/abs/2508.09101)
- [AutoCodeBench leaderboard](https://autocodebench[.]github[.]io/leaderboard.html)
- [Which Programming Languages Are Most Token Efficient? -- Martin Alderson](https://martinalderson[.]com/posts/which-programming-languages-are-most-token-efficient/)
- [NanoLang -- Simon Willison](https://simonwillison[.]net/2026/Jan/19/nanolang/#atom-everything)
- [AutoCodeBench: How Tencent Hunyuan Revolutionizes AI Programming Evaluation -- Medium](https://medium[.]com/@leivadiazjulio/autocodebench-how-tencent-hunyuan-revolutionizes-ai-programming-evaluation-78addbb1e364)
- [The Great AI Coding Showdown -- Communeify](https://www[.]communeify[.]com/en/blog/tencent-autocodebench-ai-coding-model-ranking/)
