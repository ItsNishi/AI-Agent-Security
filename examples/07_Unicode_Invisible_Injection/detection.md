# Detection and Defense: Unicode Invisible Injection

## Why Standard Defenses Fail

### Unicode Normalization Does NOT Help

```python
import unicodedata

Malicious = "Hello\U000E0100\U000E0101\U000E0102 world"

# None of these remove variation selectors:
unicodedata.normalize("NFC", Malicious)   # unchanged
unicodedata.normalize("NFD", Malicious)   # unchanged
unicodedata.normalize("NFKC", Malicious)  # unchanged
unicodedata.normalize("NFKD", Malicious)  # unchanged
```

Variation selectors and tags block characters are valid Unicode. Normalization transforms equivalent representations -- it doesn't strip valid characters.

### Regex `\w` and `\s` Miss Them

```python
import re

# Standard text matching skips invisible characters entirely
re.findall(r"\w+", Malicious)  # Returns ["Hello", "world"] -- hides injection
re.sub(r"\s+", " ", Malicious)  # Doesn't touch variation selectors
```

### Diff Tools Are Blind

`git diff`, GitHub PR reviews, and standard code review tools don't display invisible characters. A commit that adds zero visible changes can contain arbitrary hidden instructions.

---

## Detection Methods

### 1. Explicit Character Range Scanning (Most Reliable)

```python
import re

# Detect variation selectors, tags block, and zero-width characters
Invisible_Pattern = re.compile(
	r"[\U000E0100-\U000E01EF]"  # Variation Selectors Supplement
	r"|[\uFE00-\uFE0F]"          # Variation Selectors
	r"|[\U000E0001-\U000E007F]"  # Tags block
	r"|[\u200B\u200C\u200D\uFEFF\u2060]"  # Zero-width chars
)

def Has_Invisible_Content(Text: str) -> bool:
	return bool(Invisible_Pattern.search(Text))
```

### 2. Byte Length vs Character Length Comparison

Invisible Unicode characters are multi-byte in UTF-8 (4 bytes each for supplementary plane characters). A string where byte length significantly exceeds expected character-to-byte ratio likely contains hidden content.

```python
def Check_Byte_Ratio(Text: str) -> bool:
	"""Flag text where UTF-8 byte length exceeds 2x visible character count."""
	Visible_Chars = len(Text.encode("ascii", errors="ignore"))
	Total_Bytes = len(Text.encode("utf-8"))
	if Visible_Chars == 0:
		return Total_Bytes > 0  # All invisible
	return (Total_Bytes / Visible_Chars) > 3.0
```

### 3. Hex Dump Inspection (Manual)

```bash
# Show hex representation -- invisible characters become visible as byte sequences
xxd suspicious_file.md | grep -E "e0 (01|81|82|83)"

# Python one-liner to show all non-ASCII codepoints
python3 -c "
import sys
for i, c in enumerate(open(sys.argv[1]).read()):
    if ord(c) > 127:
        print(f'pos {i}: U+{ord(c):05X} ({c!r})')
" suspicious_file.md
```

---

## Defense: Stripping (The Only Reliable Mitigation)

Normalization doesn't work. Detection alone is insufficient (you still need to handle the finding). The defense is **explicit stripping** of all invisible character ranges from untrusted input before passing to an LLM.

```python
def Strip_Invisible(Text: str) -> str:
	"""Remove all invisible Unicode characters that can carry hidden content."""
	import re
	return re.sub(
		r"[\U000E0100-\U000E01EF"  # Variation Selectors Supplement
		r"\uFE00-\uFE0F"           # Variation Selectors
		r"\U000E0001-\U000E007F"   # Tags block
		r"\u200B\u200C\u200D"      # Zero-width space, joiners
		r"\uFEFF\u2060"            # BOM, word joiner
		r"]+",
		"",
		Text,
	)
```

**Apply this to**:
- All user input before LLM processing
- All fetched document content before injection into context
- All skill/plugin files before loading
- All inter-agent messages in multi-agent systems
- All RAG/retrieval results before context injection

**Do NOT apply to**:
- Internal system prompts you control
- Model output (stripping output hides evidence of compromise)

---

## Tool References

| Tool | Purpose | Source |
|---|---|---|
| ASCII Smuggler | Encode/decode hidden text via Tags block and variation selectors | [embracethered.com](https://embracethered.com/blog/posts/2025/sneaky-bits-and-ascii-smuggler/) |
| noseeum | Offensive framework for Unicode steganography and VS-based jailbreaking | [GitHub](https://github.com/umpolungfish/noseeum) |
| Promptfoo | Includes invisible character injection probes in red-team suite | [promptfoo.dev](https://www.promptfoo.dev) |
| Garak | NVIDIA's LLM security scanner; includes Unicode attack probes | [GitHub](https://github.com/NVIDIA/garak) |

See [payload_demo.py](./payload_demo.py) for a working Python implementation of encoding, decoding, detection, and stripping.
