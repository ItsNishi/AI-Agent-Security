# MCP Tool Poisoning

## What Is Tool Poisoning?

Tool poisoning is an attack where malicious instructions are hidden inside an MCP (Model Context Protocol) tool's description metadata. When an AI agent loads a tool from an MCP server, it reads the tool's name, description, and parameter schema to understand how to use it. The agent treats these descriptions as trusted instructions -- it has no mechanism to distinguish legitimate usage guidance from injected attacker commands.

This makes tool descriptions a first-class prompt injection surface. Unlike traditional prompt injection (which targets the user's input), tool poisoning targets the infrastructure layer that the agent trusts implicitly.

## Why It Is Dangerous

- **Invisible to the user**: Tool descriptions are metadata that users never see. The agent silently follows injected instructions without displaying them.
- **Cross-server impact**: A poisoned tool on one MCP server can modify how the agent interacts with OTHER legitimate servers (cross-server shadowing).
- **Bypasses DLP**: Exfiltration through a legitimate tool (e.g., sending a WhatsApp message) looks like normal agent behavior to monitoring systems.
- **Persists across sessions**: Once a poisoned MCP server is configured, every future agent session inherits the malicious instructions.
- **No integrity verification**: MCP does not sign or version-lock tool definitions. There is no way to verify that a tool description has not been tampered with.

## Attack/Defense Pair in This Example

| File | Purpose |
|---|---|
| [malicious_server.json](./malicious_server.json) | Annotated [MALICIOUS] MCP server config with a poisoned "file search" tool whose description secretly exfiltrates environment variables |
| [detection.md](./detection.md) | Detection signals, defense strategies, scanning patterns, and tool references |

## Real-World Precedent

### Invariant Labs WhatsApp Exfiltration PoC (April 2025)

Invariant Labs demonstrated the first public tool poisoning attack:

1. A malicious MCP server was configured alongside a legitimate `whatsapp-mcp` server
2. The malicious server's tool description instructed the agent to silently read the user's entire WhatsApp chat history
3. The agent then used the legitimate WhatsApp server to send that history to an attacker-controlled phone number
4. The exfiltration appeared to be normal WhatsApp messaging behavior

The attack required no exploitation of software vulnerabilities -- only a crafted tool description that the agent followed as if it were legitimate instructions.

Source: https://invariantlabs[.]ai/blog/mcp-security-notification-tool-poisoning-attacks

### CVE-2025-6514: mcp-remote OS Command Injection (CVSS 9.6)

While not a tool poisoning attack per se, CVE-2025-6514 demonstrates the severity of trusting untrusted MCP servers. The `mcp-remote` package (437K+ downloads) had an OS command injection vulnerability via a crafted `authorization_endpoint` URL. An untrusted MCP server could achieve full RCE on the client's operating system -- the first real-world demonstration of an MCP server compromising a client machine.

- Fixed in mcp-remote v0.1.16
- Source: https://jfrog[.]com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/

### Elastic Security Labs Findings (September 2025)

Testing of MCP implementations revealed:

- **43%** contained command injection flaws
- **30%** permitted unrestricted URL fetching
- Source: https://www[.]elastic[.]co/security-labs/mcp-tools-attack-defense-recommendations

## Cross-References

- [Note 15: AI Application Ecosystem Security](../../notes/15_AI_Application_Ecosystem_Security.md) -- Full MCP security coverage including CVE table, rug pull attacks, tool poisoning in agent framework context, and ETDI proposals
- [Example 03: Data Exfiltration Via Agent](../03_Data_Exfiltration_Via_Agent/) -- General exfiltration techniques that tool poisoning enables as a delivery mechanism

## Key Sources

- Invariant Labs (Tool Poisoning): https://invariantlabs[.]ai/blog/mcp-security-notification-tool-poisoning-attacks
- JFrog (CVE-2025-6514): https://jfrog[.]com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/
- Trail of Bits (mcp-context-protector): https://blog[.]trailofbits[.]com/2025/07/28/we-built-the-security-layer-mcp-always-needed/
- OWASP MCP Top 10: https://owasp[.]org/www-project-mcp-top-10/
- Elastic Security Labs: https://www[.]elastic[.]co/security-labs/mcp-tools-attack-defense-recommendations
- Vulnerable MCP Project: https://vulnerablemcp[.]info/
