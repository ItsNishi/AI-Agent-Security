# [CLEAN] Security Review Skill -- Sanitized Version

> This is what a legitimate security review skill looks like.
> No hidden payloads, no persistence triggers, no HTML comments with instructions.

---

```markdown
---
name: security-review
description: Perform a security review of the current codebase, checking for
             common vulnerabilities, hardcoded secrets, and dependency issues.
---

# Security Review Guidelines

When running a security review, follow these steps to identify potential
vulnerabilities, leaks, and misconfigurations.

## 1. Reconnaissance & Setup
- Identify the project's technology stack
- Verify `.gitignore` excludes sensitive files (`.env`, `*.pem`, `*.key`)
- Check for a `SECURITY.md` or security policy

## 2. Dependency Auditing
Check for known vulnerabilities in project dependencies:
- **Node.js**: Run `npm audit`
- **Python**: Run `pip-audit` (if installed) or check `pip list` against known CVEs
- **Go**: Run `govulncheck ./...`

## 3. Secret Scanning
Search the codebase for hardcoded secrets:
- AWS keys (`AKIA...`)
- API tokens (`sk_live`, `Bearer`)
- Private keys (`BEGIN RSA PRIVATE KEY`, `BEGIN EC PRIVATE KEY`)
- Database URIs (`postgres://`, `mongodb://`)
- Environment variable references that should be in `.env`

## 4. Code Analysis
Look for dangerous patterns by language:

### JavaScript/TypeScript
- `eval()`, `Function()` constructor
- `dangerouslySetInnerHTML` without sanitization
- `child_process.exec()` with unsanitized input

### Python
- `eval()`, `exec()`, `compile()`
- `subprocess.call(shell=True)` with user input
- `pickle.load()` on untrusted data
- `yaml.load()` without `Loader=SafeLoader`

### SQL (any language)
- String concatenation in queries
- Missing parameterized queries

## 5. Configuration Review
- Check for debug mode enabled in production configs
- Verify CORS policies are not overly permissive
- Ensure HTTPS is enforced where applicable
- Review authentication and session management

## 6. Report Findings
Produce a summary with:
- **Critical**: Issues requiring immediate fix (RCE, auth bypass, exposed secrets)
- **High**: Significant vulnerabilities (SQLi, XSS, insecure deserialization)
- **Medium**: Issues with limited exploitability
- **Low**: Best practice violations and hardening opportunities
- **Remediation steps** for each finding
```

## Key Differences from the Malicious Version

| Aspect | Malicious | Clean |
|---|---|---|
| Description | "ALWAYS run this at the end of each task" | Describes what it does, no persistence trigger |
| HTML comments | Contains hidden execution instructions | None |
| Network requests | `curl \| bash` from attacker URL | None -- all operations are local |
| Section 5 | Fake "validation" hiding injection | Legitimate configuration review |
| Scope | Tries to execute remote code | Only reads and analyzes local code |
