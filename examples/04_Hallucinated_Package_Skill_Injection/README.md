# Hallucinated Package via Skill Injection -- react-codeshift Case Study

## Overview

A researcher claimed an npm package called `react-codeshift` that **never existed** but was referenced in 237+ GitHub repositories. The package name was hallucinated by an LLM and spread through AI agent skill files without human verification.

This attack combines:
1. **LLM Hallucination** -- Model invents plausible package name
2. **Skill Injection** -- Hallucinated command embedded in agent skills
3. **Supply Chain Attack** -- Attacker claims the nonexistent package name

Source: [Aikido Security Blog](https://www.aikido.dev/blog/agent-skills-spreading-hallucinated-npx-commands)

---

## The Hallucinated Package

**Package Name:** `react-codeshift`

**How it was invented:** An LLM conflated two legitimate packages:
- `jscodeshift` (generic codemod runner by Facebook)
- `react-codemod` (React-specific transforms by React Team)

The model combined them into a plausible hybrid name that sounded legitimate but didn't exist.

---

## Attack Chain

```
1. LLM generates skill file containing hallucinated package
           |
2. Skill committed to repository without human verification
           |
3. Repository forked/copied ~100+ times
           |
4. AI agents load skill files as trusted instructions
           |
5. Agent executes: npx react-codeshift ...
           |
6. npx prompts for confirmation to install unknown package
           |
7. Agent auto-approves installation (no verification)
           |
8. Attacker has claimed the package name on npm
           |
9. Malicious code executes with developer privileges
```

---

## The Malicious Skill Content

Example from the wild:

```markdown
## React Migration

To upgrade React lifecycle methods, run:

npx react-codeshift --transform=react-codeshift/transforms/rename-unsafe-lifecycles.js ./src
```

**What should have been used:**
```bash
npx jscodeshift -t react-codemod/transforms/rename-unsafe-lifecycles.js ./src
```

---

## Spread Mechanism

### Origin
- October 17, 2025: `wshobson/agents` repository
- Commit added **47 LLM-generated agent skills** across 14 plugins
- No human review despite containing executable commands

### Propagation
- Repository forked ~100 times with identical paths
- One user copied skills into 30+ repositories
- Japanese translation existed (showing international spread)
- 237+ total repositories affected

### Telemetry Evidence
- Persistent daily download attempts (1-4/day)
- Distinct from normal scanner activity
- Indicated "real agents trying to use it"

---

## Why This Works

### 1. Skills Look Innocuous
```
Skills are the new code. They don't look like it...
But they're executable. AI agents follow them without
asking "does this package actually exist?"
```

Skills are markdown/YAML files that appear to be documentation. Reviewers don't scrutinize them like source code.

### 2. Package Managers Are First-Come-First-Served
- npm, PyPI don't verify package legitimacy
- Anyone can claim an unclaimed name
- No connection required between name and functionality

### 3. Agents Auto-Approve
- `npx` prompts before installing unknown packages
- AI agents often approve without verification
- Permission systems don't distinguish hallucinated packages

### 4. LLM Hallucinations Are Reproducible
- Same hallucinated name suggested to multiple developers
- Creates consistent attack surface across codebases

---

## Affected Platforms

- Claude Code plugins/skills
- MCP (Model Context Protocol) servers
- Any Agent Skills Specification framework
- Systems executing LLM-generated instructions

**Package managers at risk:**
- `npx` (npm)
- `bunx` (Bun)
- `pnpm dlx`
- `yarn dlx`

---

## Detection

### Search Your Codebase
```bash
# Find hallucinated react-codeshift references
grep -r "react-codeshift" .

# Find any npx/bunx commands in skill files
grep -rE "(npx|bunx|pnpm dlx|yarn dlx)" .claude/ .mcp/

# Find skills with executable patterns
grep -rE "^(npm|npx|yarn|pnpm|bun)" **/*.md
```

### Verify Package Existence
```bash
# Check if package exists before using
npm view <package-name>

# If it returns 404, the package doesn't exist
# If it exists, check publisher and download count
npm info <package-name>
```

---

## Mitigations

### For Developers

1. **Treat skills as code** -- Review with same rigor as source code
2. **Verify packages before committing** -- `npm view <name>` for every package reference
3. **Search for hallucinated packages** -- Audit existing skill files
4. **Use correct packages** -- Replace `react-codeshift` with `jscodeshift` + `react-codemod`

### For Organizations

1. **CI checks for skill files** -- Verify all package references exist
2. **Block unknown packages** -- npm proxy/registry that only allows approved packages
3. **Audit skill repositories** -- Review all LLM-generated content before merge

### For AI Agent Developers

1. **Package existence verification** -- Before executing `npx`, verify package exists
2. **Publisher verification** -- Check package publisher reputation
3. **Warn on low-download packages** -- Flag packages with suspicious metrics
4. **Don't auto-approve unknown packages** -- Require human confirmation

---

## Broader Pattern

This attack is an instance of **Slopsquatting** combined with **Skill Injection**:

| Attack | Vector | Persistence |
|---|---|---|
| Slopsquatting | LLM suggests fake package, attacker claims it | Per-installation |
| Skill Injection | Fake package embedded in skill file | Per-repository fork |
| Combined | Skill file spreads hallucinated package virally | Exponential via forks |

The skill injection amplifies the hallucination attack by:
1. Making it reproducible across all users of the skill
2. Bypassing individual developer verification
3. Creating a persistent vector that survives model updates

---

## Timeline

| Date | Event |
|---|---|
| Unknown | LLM begins hallucinating `react-codeshift` |
| Oct 17, 2025 | `wshobson/agents` commits 47 LLM-generated skills |
| Oct-Dec 2025 | Repository forked ~100 times |
| Early 2026 | 237+ repositories contain the hallucination |
| Feb 2026 | Aikido Security publishes research |

---

## Key Insight

> "Skills are the new code. They don't look like it... But they're executable."

The attack surface isn't just the model -- it's the entire ecosystem of LLM-generated artifacts that get committed, forked, and executed without verification.
