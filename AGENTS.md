# AGENTS.md - AI Agent Security Research

Repository instructions for coding and writing agents working in this project. Keep this file aligned with the local `CLAUDE.md` guidance when rules change.

## Project Context

- **Purpose**: Educational security research on AI agent attack surfaces
- **Context**: Defensive security research documenting attacks so better defenses can be built
- **Authorization**: Offensive security content is for educational, CTF, and pentest learning purposes

## Safety Rules

- Defang URLs only in malicious code examples and attack payloads (`hxxps://`, `[.]` notation). Keep source citations and reference links live.
- Mark malicious content with `[MALICIOUS]` or `[INJECTED]` annotations.
- Every attack example must include a corresponding defense or mitigation.

## Writing Style

- **Concise and technical**: State facts. Skip filler.
- **Generalize, don't narrate**: Write about technique classes, not incident retellings. Use real-world cases briefly as examples with links.
- **Sources over storytelling**: Link to references instead of retelling them.
- **Banned slop words**: Do not use `landscape` in prose, `delve`, `comprehensive`, `robust`, `leverage`, `paradigm`, `holistic`, `utilize`, `in today's world`, `cutting-edge`, `game-changer`, `foster`, `moreover`, `furthermore`, `crucial`, `pivotal`, `streamline`, `harness`, `empower`, `seamless`, `innovative`, `transformative`, `underscores`, `multifaceted`, `ever-evolving`, or `navigate` in a non-literal sense. Use plain, direct language instead.
- **Banned slop patterns**: Do not start paragraphs with `In the realm of`, `When it comes to`, `In an era where`, or `As we stand on the brink of`. Do not hedge with `It is important to note that`. Do not pad with `Not only X, but also Y` when you just mean `X and Y`.
- **Structure**: Prefer headers, bullets, and tables over long prose. Lead with the concept, then examples if needed.
- **Voice**: Use active voice and second person or imperative where appropriate.

## Note Naming Convention

- New notes follow `{next_number:02d}_{Title_With_Underscores}.md`
- Check `ls notes/` first to determine the next number.
- Titles use `Title_Case` with underscores.

## Git Rules

- `CLAUDE.md` is gitignored. Never force-add it with `git add -f`.
- If `git add` warns that a file is ignored, respect `.gitignore`. Do not override it with `-f`.

## Repo Notes

- Each skill has its own `patterns.py` copy. They are self-contained, not shared.
- `patterns.py` files will trigger their own detection patterns. That is an expected false positive.
- All seven `examples/` directories are also used as test fixtures for the skills.
- Advisory hooks warn but do not block. Deterministic enforcement requires blocking hooks.
