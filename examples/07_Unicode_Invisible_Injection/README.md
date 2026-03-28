# Unicode Invisible Injection

## Technique

Embed malicious instructions using Unicode characters that are invisible to humans but processed by LLM tokenizers. The text looks clean in any editor or terminal. The LLM reads and follows hidden instructions.

Three main encoding methods:
- **Variation Selectors** (U+FE00-U+FE0F, U+E0100-U+E01EF): 256 selectors intended to modify glyph rendering. When applied to ASCII characters, they render invisibly but tokenize as separate tokens.
- **Tags Block** (U+E0001-U+E007F): Unicode block originally for language tagging. Each tag character maps to an ASCII character (U+E0041 = 'A'). Invisible in all renderers.
- **Zero-Width Characters** (U+200B, U+200C, U+200D, U+FEFF): Zero-width space, joiners, and BOM. Invisible but tokenized.

## Attack Flow

```
1. Attacker encodes malicious instructions using invisible Unicode characters
2. Instructions are embedded in a seemingly benign document, comment, or skill file
3. Human reviews the file -- sees nothing (characters are zero-width or invisible)
4. Standard text editors, diff tools, and code review tools don't display the hidden text
5. LLM tokenizer processes invisible characters as valid tokens
6. Model reads and follows the hidden instructions
```

## Attack/Defense Pair

| File | Purpose |
|---|---|
| [payload_demo.py](./payload_demo.py) | Python script demonstrating Sneaky Bits encoding/decoding -- encode arbitrary text into invisible variation selector sequences |
| [detection.md](./detection.md) | Detection methods, stripping techniques, and why Unicode normalization alone doesn't work |

## Why It Works

- **Rendering gap**: Unicode renderers skip variation selectors and tags block characters. They're designed to be invisible. No editor bug needed -- this is the spec working as designed.
- **Tokenizer gap**: LLM tokenizers process these characters as valid input. They occupy token slots and carry semantic meaning to the model.
- **Normalization doesn't help**: NFC/NFD/NFKC/NFKD Unicode normalization does NOT strip variation selectors or tags block characters. These are "valid" Unicode, not malformed sequences.
- **Diff blindness**: `git diff`, GitHub PR reviews, and code review tools don't display invisible characters. A PR that looks like it changes nothing could contain injected instructions.

## Cross-References

- [Note 17: Unicode Variation Selector Attacks](../../notes/17_Unicode_Variation_Selector_Attacks.md) -- Full coverage of Sneaky Bits encoding, GlassWorm malware, token expansion DoS, and defense strategies
- [Example 01: Hidden Comment Injection](../01_Hidden_Comment_Injection/) -- Related technique using visible-in-source HTML comments (this example uses truly invisible characters)
