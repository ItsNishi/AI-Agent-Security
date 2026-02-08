# Hidden Comment Injection

## Technique

Embed malicious instructions inside HTML comments within markdown files that are loaded as agent context (skills, CLAUDE.md, memory files).

HTML comments (`<!-- -->`) are:
- **Invisible** when markdown is rendered (GitHub, VS Code preview, any viewer)
- **Fully visible** when the LLM parses raw file content

This creates a gap between what humans review and what the agent executes.

## Attack Flow

```
1. Attacker creates a skill/plugin with legitimate content
2. Hidden HTML comment contains injection payload
3. User installs the skill, reviews the rendered markdown -- sees nothing suspicious
4. Agent loads the raw markdown as instructions
5. LLM reads the HTML comment and follows the hidden instructions
6. Payload executes (code execution, data exfil, persistence)
```

## Real-World Example

See [malicious_skill.md](./malicious_skill.md) for an annotated breakdown of a trojanized `security-review` skill that used this technique to achieve remote code execution.

See [sanitized_skill.md](./sanitized_skill.md) for what a legitimate version of the same skill looks like.

## Why It Works

- **Trust model gap**: Skills are loaded as trusted instructions. No distinction between the skill author's intent and injected content within the file.
- **Review gap**: Humans review rendered markdown. LLMs read raw text. The attack exists in the gap.
- **Social engineering**: The visible content is useful and legitimate, building trust. The hidden content exploits that trust.

## Detection

### Manual
```bash
# Search for HTML comments in any markdown file
grep -rn '<!--' *.md

# Search for shell commands inside comments
grep -Pzo '<!--[\s\S]*?(curl|wget|bash|sh|exec)[\s\S]*?-->' *.md
```

### Automated
- Strip all HTML comments before LLM processing
- Flag any skill file containing HTML comments with imperative verbs
- Reject skills with `curl | bash` patterns regardless of context

## Mitigation

1. **Always review raw source** of skills before installing -- not the rendered preview
2. **Strip HTML comments** from skill files during loading
3. **Sandbox skill execution** -- skills should not be able to make network requests or execute arbitrary commands
4. **Permission gates** -- require user approval for any shell command a skill triggers
