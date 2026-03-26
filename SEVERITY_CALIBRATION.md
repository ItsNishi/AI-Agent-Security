# Severity Calibration Guide

How severity levels are assigned to detection patterns in the skill suite.

## Severity Levels

### CRITICAL

**Meaning**: Immediate security impact. Exploitation achievable with no additional conditions or minimal effort.

**Assignment criteria** (any one qualifies):
- Arbitrary code execution on the user's machine
- Direct credential theft or exfiltration with active network send
- Permission system bypass that removes all safety gates
- Supply chain payload execution (eval/exec of decoded/decompressed content)
- Package does not exist on registry (hallucinated/typosquatted name)
- Complete context override (ignore all previous instructions)

| Pattern | Why CRITICAL |
|---|---|
| `pipe_to_shell` | `curl ... \| bash` = RCE in one step |
| `html_comment_with_commands` | Hidden shell commands execute with no user visibility |
| `hook_auto_approve` | `permissionDecision: allow` removes the last safety gate |
| `python_b64decode_exec` | `exec(b64decode(...))` -- encoded payload runs immediately |
| `ignore_previous_instructions` | Complete context override -- attacker controls agent behavior |
| `curl_post_sensitive_file` | Credential exfiltration with active network send |
| `reverse_shell_bash` | Full interactive access to the user's machine |
| `package_not_found` | Promoted from INFO by `Verify_Install_Findings` when package doesn't exist |

### HIGH

**Meaning**: Significant security risk. Exploitation requires some conditions but is realistic in agent environments.

**Assignment criteria** (any one qualifies):
- Code execution requiring user interaction or specific conditions
- Credential file access or environment variable harvesting (read, not yet sent)
- Persistence mechanisms (cron, shell profiles, git hooks, systemd)
- Output suppression (hiding malicious activity from user)
- Instruction replacement or system prompt injection markers
- Dangerous function calls with obvious abuse potential (eval, exec, subprocess shell=True)

| Pattern | Why HIGH |
|---|---|
| `persistence_trigger_always` | Forces repeated execution but requires skill to be loaded first |
| `sensitive_file_read` | Reads ~/.ssh/id_rsa -- data theft requires a separate exfil step |
| `bashrc_profile_append` | Shell persistence, but needs restart to activate |
| `eval_call` | Dangerous call with clear abuse potential, but may be legitimate in some contexts |
| `output_suppression` | Hides activity from user but doesn't execute code by itself |
| `generic_api_key_assignment` | Key exposure, but may be a false positive on config examples |

### MEDIUM

**Meaning**: Moderate risk. Represents a security concern that warrants review but may be legitimate in context.

**Assignment criteria** (any one qualifies):
- Configuration weaknesses (auto-invocation enabled, Bash pre-approved)
- Suspicious patterns with legitimate uses (Process.Start, strcpy, sprintf)
- Obfuscation indicators (hex strings, unicode escapes, bidi characters)
- Missing security controls (missing frontmatter field, some world bits)
- Credential path references without active access
- Probing or reconnaissance (capability probing, scope escalation attempts)
- Package verification failure due to network error (manual check needed)

| Pattern | Why MEDIUM |
|---|---|
| `frontmatter_bash_pre_approved` | Risk depends on skill content -- Bash alone is not malicious |
| `hex_encoded_string` | Could be payload or legitimate binary data |
| `c_strcpy` | Dangerous in C but standard usage exists |
| `credential_path_access` | References path but doesn't read or send the file |
| `package_unverified` | Network error during verification -- needs manual check |

### LOW

**Meaning**: Minor concern or informational finding. Rarely actionable on its own.

**Assignment criteria**:
- Best practice violations
- Patterns with high false-positive rates
- Informational context about build system features
- Hypothetical framing detection
- Missing but non-critical security configuration

| Pattern | Why LOW |
|---|---|
| `hypothetical_framing` | "for educational purposes" is often legitimate |
| `cargo_build_script` | build.rs is standard Rust -- just noting it exists |
| `base64_long_blob` | Long base64 strings are common in configs, images, certs |
| `gitignore_missing_pattern` | Missing .gitignore entry, not an active vulnerability |

### INFO

**Meaning**: Purely informational. Logged for awareness, not a security issue.

**Assignment criteria**:
- Standard package installation commands (before registry verification)
- Expected configuration patterns (env vars in auth headers)
- Baseline observations

| Pattern | Why INFO |
|---|---|
| `npm_install_unknown` | Placeholder until `Verify_Install_Findings` checks the registry |
| `pip_install_unknown` | Same -- may be promoted to CRITICAL if package doesn't exist |
| `mcp_env_var_in_auth` | Standard practice, just noting env var usage |
| `github_actions_secrets_in_run` | Common pattern, flagging for review |

## Calibration Principles

1. **RCE is always CRITICAL** -- if a pattern leads to arbitrary code execution with no additional conditions, it is CRITICAL.

2. **Credential read = HIGH, credential send = CRITICAL** -- reading `~/.ssh/id_rsa` is HIGH. Sending it via `curl POST` is CRITICAL. The distinction is between preparation and execution of the attack chain.

3. **Persistence = HIGH** -- persistence mechanisms (cron, shell profiles, git hooks) survive session boundaries, but they require an initial execution vector to install.

4. **Context-dependent = MEDIUM** -- patterns dangerous in some contexts but legitimate in others are MEDIUM. Bash pre-approval in a skill is suspicious but not inherently malicious.

5. **INFO is a staging level** -- `pip_install_unknown` starts at INFO and gets promoted to CRITICAL by `Verify_Install_Findings` if the package doesn't exist. INFO means "needs more context."

6. **Prefer higher severity on ambiguity** -- when a pattern could be HIGH or MEDIUM, lean HIGH. False positives are acceptable; false negatives are not. Users can triage down, but they can't detect what was never flagged.

## Dynamic Severity Promotion

### Package Verification (`Verify_Install_Findings`)

| Input Severity | Registry Result | Output |
|---|---|---|
| INFO (`pip_install_unknown`) | Package not found (404) | CRITICAL (`package_not_found`) |
| INFO (`pip_install_unknown`) | Network error | MEDIUM (`package_unverified`) |
| INFO (`pip_install_unknown`) | Package exists | Finding removed |

### Frontmatter Combination Escalation (`Analyze_Frontmatter`)

| Fields | Severity | Rationale |
|---|---|---|
| Bash pre-approved (alone) | MEDIUM | Pre-approval is a concern but not exploitable alone |
| Bash + auto-invocable | HIGH | Agent can trigger shell execution without user initiating the skill |
| Bash + auto-invocable + hidden | CRITICAL | Stealth shell execution -- user has no visibility or control |

## Adding New Patterns

When adding a new pattern, use these questions:

1. Does it achieve RCE or credential exfiltration with no extra steps? -> **CRITICAL**
2. Does it require a second step (e.g., exfil after read)? -> **HIGH**
3. Is it dangerous only in certain contexts? -> **MEDIUM**
4. Is it mainly a best-practice concern? -> **LOW**
5. Is it a placeholder for further verification? -> **INFO**

Document the rationale in the pattern's `description` field and keep this guide updated when new categories are added.
