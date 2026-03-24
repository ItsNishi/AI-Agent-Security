# Unicode Variation Selector Attacks on LLMs

Variation selectors are invisible Unicode characters that LLM tokenizers encode as distinct tokens. Attackers append them to malicious prompts to alter tokenization without changing visible text -- producing adversarial suffixes that bypass safety alignment, guardrails, and human review.

This differs from homoglyph substitution ([note 06, section 2.4](./06_LLM_Jailbreaking_Deep_Dive.md)). Homoglyphs replace visible characters with lookalikes. Variation selectors add invisible characters that change how tokenizers parse the input while the display stays identical.

---

## Variation Selectors: The Unicode Primitives

### Codepoint Ranges

| Block | Range | Count | Intended Purpose |
|-------|-------|-------|-----------------|
| Variation Selectors | U+FE00 -- U+FE0F | 16 (VS1--VS16) | Glyph variant selection (e.g., emoji vs text presentation) |
| Variation Selectors Supplement | U+E0100 -- U+E01EF | 240 (VS17--VS256) | Extended glyph variants for CJK ideographs |

Combined: **256 invisible characters** that attach to a preceding base character without rendering. Most text editors, terminals, and web UIs do not display them.

### Why They Differ from Other Invisible Characters

| Character Class | Examples | Limitation |
|----------------|----------|------------|
| Zero-width chars | U+200B (ZWSP), U+200C (ZWNJ), U+200D (ZWJ), U+FEFF (BOM) | ~5 characters total; small perturbation space |
| Bidi markers | U+202A--U+202E | 5 characters; often stripped by renderers |
| Tags block | U+E0001--U+E007F | 128 characters; deprecated; increasingly filtered |
| **Variation selectors** | **U+FE00--U+FE0F, U+E0100--U+E01EF** | **256 characters; legitimate use cases make blanket filtering harder** |

Variation selectors have the largest invisible character space and attach to *any* base character at *any* position, unlike homoglyphs which can only substitute at fixed positions.

---

## How Tokenizers Handle Variation Selectors

Tokenizers don't discard variation selectors -- they encode them as multi-token blocks:

| Tokenizer (Model) | Tokens per VS | Example |
|-------------------|---------------|---------|
| GPT-4 / GPT-3.5 | ~4 tokens (92% of VS chars) | VS-50 (U+E0121) -> `[175, 254, 226, 94]` |
| Llama-2 / Vicuna | ~4 tokens (94% of VS chars) | Same VS -> different token IDs |
| Llama-3.1 | ~3 tokens (91% of VS chars) | Fewer tokens per selector |

The same variation selector produces **different token sequences across models**, which is why attacks must be optimized per target.

Source: [Imperceptible Jailbreaking against Large Language Models](https://arxiv.org/abs/2510.05025) (Gong et al., October 2025), Table 1

---

## Attack 1: Imperceptible Jailbreaking

### Technique

Append a suffix of L variation selectors to a harmful prompt. The visible text stays identical, but the token sequence changes enough to redirect the model past its safety alignment.

**Optimization pipeline (Chain-of-Search):**

1. Append L variation selectors to the malicious question (L=800 for most models, L=1200 for Llama-3.1)
2. Each iteration: modify M=10 contiguous selectors
3. Maximize log-likelihood of target-start tokens ("Sure", "To", "Here")
4. Run T=10,000 iterations per round across R=5 rounds
5. Reuse successful suffix-token pairs as initialization for new questions

### Attack Success Rates

| Model | ASR | Baseline (random VS) |
|-------|-----|---------------------|
| Vicuna-13B | 100% | 28% |
| Mistral-7B-Instruct | 100% | 12% |
| Llama-2-Chat-7B | 98% | 0% |
| Llama-3.1-Instruct-8B | 80% | 4% |

Attention visualization shows the invisible suffixes redirect model attention away from the malicious question's safety-triggering tokens, shifting the distribution toward compliance.

Source: [Gong et al., 2025](https://arxiv.org/abs/2510.05025)

---

## Attack 2: Guardrail Evasion

Safety guardrails (input classifiers that detect jailbreaks/injections before the LLM sees the prompt) are even more vulnerable than the LLMs themselves.

### Tested Guardrails and Results

Mindgard (2025) tested six production guardrail systems using character injection techniques including variation selectors, zero-width characters, emoji smuggling, homoglyphs, and diacritics:

| Guardrail | Fully Bypassed By |
|-----------|-------------------|
| Azure Prompt Shield | Emoji smuggling (100% evasion) |
| Protect AI v2 | Emoji smuggling (100% evasion) |
| Meta Prompt Guard | Character injection variants |
| Nvidia NeMo Guard | Character injection variants |
| Protect AI v1 | Character injection variants |
| Vijil Prompt Injection | Character injection variants |

No single guardrail consistently detected all character injection techniques. Emoji smuggling (which uses variation selectors U+FE0E/U+FE0F to encode hidden data within emoji sequences) achieved **100% evasion** against multiple commercial systems.

Source: [Mindgard -- Outsmarting AI Guardrails](https://mindgard.ai/blog/outsmarting-ai-guardrails-with-invisible-characters-and-adversarial-prompts) (April 2025)

---

## Attack 3: Data Smuggling and Encoding

### Sneaky Bits (Rehberger, 2025)

Pick two invisible Unicode characters to represent binary 0 and 1. Encode any data as a sequence of these invisible characters appended to visible text.

Default mapping:
- U+2062 (invisible times) = `0`
- U+2064 (invisible plus) = `1`

Example: the letter "A" (binary `01000001`) becomes 8 invisible characters.

LLMs interpret these hidden sequences as instructions. The visible prompt looks clean to humans, but the model sees and follows the hidden payload.

Source: [Rehberger -- Sneaky Bits and ASCII Smuggler Updates](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/)

### VS-to-Byte Mapping

Map VS1--VS256 directly to byte values 0x00--0xFF, enabling Extended ASCII encoding without a base character. Each variation selector carries one byte of payload.

This enables:
- Hidden prompt injection in documents, emails, or web pages
- Data exfiltration through invisible URL parameters
- Steganographic C2 channels in seemingly benign text

---

## Attack 4: Supply Chain (GlassWorm)

The GlassWorm malware (discovered October 2025) used variation selectors for real-world payload delivery in malicious npm packages and VS Code extensions.

### Encoding Scheme

Used VS17--VS256 (U+E0100--U+E01EF) with a simple formula:

```
byte_value = codepoint - 0xE0100 + 16
```

Example: U+E0154 decodes to byte value 100 (ASCII `d`).

A 6,492-character invisible string decoded to Base64, which decoded to JavaScript executed via `eval()`.

### Evasion

- Invisible characters don't render in VS Code or most editors
- Rate-limited activation (~2-day cooldown) prevented continuous execution
- Native binary decoders had **zero VirusTotal detections** at upload (2025-03-23)
- In-memory decryption using dynamic AES-128-CBC keys from HTTP headers
- Google Calendar events used as fallback C2 channel (event titles contained Base64-encoded URLs)

Impact: 35,000+ downloads across multiple malicious VS Code extensions.

Source: [Endor Labs -- GlassWorm](https://www.endorlabs.com/reports/invisible-threats-glassworm-unicode-vscode)

---

## Attack 5: Token Expansion DoS

Some tokenizers expand a single variation selector into multiple tokens (3--4 tokens per VS character). An attacker can craft input that appears short in character count but expands to thousands of tokens after tokenization.

This enables:
- **Context window exhaustion**: Fill the model's context with invisible tokens, displacing legitimate content
- **Cost amplification**: A short-looking prompt consumes disproportionate compute/billing
- **Rate limit bypass**: Character-count-based rate limits undercount the true token cost

Source: [Prompt Security -- Unicode Exploits](https://prompt.security/blog/unicode-exploits-are-compromising-application-security)

---

## Why Standard Defenses Fail

### Unicode Normalization Does Not Help

All four Unicode normalization forms (NFC, NFD, NFKC, NFKD) **preserve variation selectors**. They are not compatibility equivalents of anything -- they are combining marks with no decomposition mapping.

```
Input:  "Hello" + VS1 + VS2 + VS3
NFC:    "Hello" + VS1 + VS2 + VS3   (unchanged)
NFKD:   "Hello" + VS1 + VS2 + VS3   (unchanged)
```

This is a critical gap: many input sanitization pipelines rely on NFKC normalization to collapse Unicode tricks, but variation selectors survive it.

### Keyword Filters Operate on Visible Text

Safety classifiers trained on visible text miss invisible perturbations entirely. The visible portion of a variation-selector-injected prompt is identical to the original harmful prompt -- but the classifier sees different tokens than the LLM does if they use different processing pipelines.

### CVE-2025-12758: Library-Level Blindness

The JavaScript `validator` library's `isLength()` function miscounts strings containing VS15 (U+FE0E) and VS16 (U+FE0F), treating variation selectors as zero-length. Any length validation built on this library is bypassable.

Source: [Full Disclosure](https://seclists.org/fulldisclosure/2026/Jan/27)

---

## Defenses

### Input Sanitization (Pre-Tokenizer)

Strip or reject variation selectors before the tokenizer sees the input:

```python
import re

# Strip all variation selectors (both blocks)
Variation_Selector_Pattern = re.compile(
	"[\uFE00-\uFE0F\U000E0100-\U000E01EF]"
)

def Strip_Variation_Selectors(Text: str) -> str:
	return Variation_Selector_Pattern.sub("", Text)
```

Extend to cover the full invisible character surface:

```python
# Broader invisible character stripping
Invisible_Pattern = re.compile(
	"["
	"\uFE00-\uFE0F"       # Variation Selectors
	"\U000E0100-\U000E01EF"  # Variation Selectors Supplement
	"\U000E0001-\U000E007F"  # Tags block
	"\u200B-\u200F"        # Zero-width and direction chars
	"\u202A-\u202E"        # Bidi embedding
	"\u2060-\u2064"        # Invisible operators (Sneaky Bits)
	"\uFEFF"               # BOM / ZWNBSP
	"]"
)

def Strip_Invisible(Text: str) -> str:
	return Invisible_Pattern.sub("", Text)
```

### Token-Level Anomaly Detection

Flag inputs where the token count is disproportionate to the visible character count:

```python
def Detect_Token_Inflation(Text: str, Tokenizer, Threshold: float = 2.0) -> bool:
	"""Flag if token/visible-char ratio exceeds threshold."""
	Visible_Len = len(Strip_Invisible(Text))
	Token_Count = len(Tokenizer.encode(Text))
	if Visible_Len == 0:
		return Token_Count > 0
	return (Token_Count / Visible_Len) > Threshold
```

### Guardrail Architecture

- **Process sanitized text** through safety classifiers, not raw input
- **Ensure tokenizer parity**: the guardrail classifier and the target LLM must see the same token sequence (or the guardrail should operate on the post-sanitization output)
- **Layer defenses**: no single guardrail catches all encoding tricks (Mindgard's finding)

### Pre-Commit and CI Hooks

Detect invisible characters in agent configuration files, prompts, and code:

```bash
# Detect variation selectors and other invisible chars in staged files
# Uses grep with PCRE for Unicode property matching
git diff --cached --name-only | xargs grep -Pn '[\x{FE00}-\x{FE0F}\x{E0100}-\x{E01EF}\x{E0001}-\x{E007F}\x{200B}-\x{200F}\x{2060}-\x{2064}]'
```

See [note 10](./10_Agent_MD_Configuration_Files.md) for broader Unicode scanning in agent config files.

---

## Related Techniques

| Technique | Difference from VS Attacks | Note |
|-----------|---------------------------|------|
| Homoglyph substitution | Replaces visible characters; detectable by visual inspection | [06](./06_LLM_Jailbreaking_Deep_Dive.md) |
| Rules File Backdoor (Unicode) | Uses Tags block / zero-width chars in config files specifically | [10](./10_Agent_MD_Configuration_Files.md) |
| ASCII smuggling (Tags block) | Uses U+E0001--U+E007F (128 chars); increasingly filtered | [13](./13_AI_Application_Ecosystem_Security.md) |
| Token-level adversarial suffixes (GCG) | Visible garbage suffixes; detectable by perplexity filters | [06](./06_LLM_Jailbreaking_Deep_Dive.md) |

---

## Tools

| Tool | Purpose | Source |
|------|---------|--------|
| ASCII Smuggler | Encode/decode hidden text using Tags block and VS characters | [embracethered.com](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/) |
| noseeum | Offensive framework for Unicode-based attacks; VS steganography + jailbreaking | [GitHub](https://github.com/umpolungfish/noseeum) |
| Garak (ascii_smuggling probe) | Red-team testing for invisible character attacks on LLMs | [Garak docs](https://reference.garak.ai/en/latest/ascii_smuggling.html) |
| Promptfoo | LLM red-teaming with Unicode evasion test cases | [promptfoo.dev](https://www.promptfoo.dev) |

---

## Sources

- [Gong et al. -- Imperceptible Jailbreaking against LLMs (arXiv:2510.05025)](https://arxiv.org/abs/2510.05025)
- [Rehberger -- Sneaky Bits, Variant Selectors and ASCII Smuggler Updates](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/)
- [Mindgard -- Outsmarting AI Guardrails with Invisible Characters](https://mindgard.ai/blog/outsmarting-ai-guardrails-with-invisible-characters-and-adversarial-prompts)
- [Endor Labs -- GlassWorm: Invisible Threats and Blind Spots](https://www.endorlabs.com/reports/invisible-threats-glassworm-unicode-vscode)
- [Prompt Security -- Unicode Exploits Compromising Application Security](https://prompt.security/blog/unicode-exploits-are-compromising-application-security)
- [Promptfoo -- Invisible Unicode Threats in AI-Generated Code](https://www.promptfoo.dev/blog/invisible-unicode-threats/)
- [AWS -- Defending LLM Applications Against Unicode Character Smuggling](https://aws.amazon.com/blogs/security/defending-llm-applications-against-unicode-character-smuggling/)
- [CVE-2025-12758 -- Variation Selector Bypass in validator library](https://seclists.org/fulldisclosure/2026/Jan/27)
