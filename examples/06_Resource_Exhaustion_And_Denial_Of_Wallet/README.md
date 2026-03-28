# Resource Exhaustion & Denial of Wallet

## Technique

Force an AI agent into expensive execution paths -- maximizing token consumption, triggering reasoning loops, or saturating context windows -- to drain the victim's API budget without crashing the service.

Unlike traditional DoS (crash the service), Denial of Wallet (DoW) exploits consumption-based pricing. The system stays up. The bill explodes.

## Attack Flow

```
1. Attacker identifies an agent endpoint that accepts user-controlled input
2. Crafts input designed to maximize token consumption (see techniques below)
3. Agent processes the input, generating expensive output tokens
4. Reasoning models generate thousands of hidden "thinking" tokens (billed at output rates)
5. Single request costs $0.50-5.00+; automated at scale, budget drains in hours
6. Rate limiters count requests, not cost -- attacker stays under request limits
```

## Attack Techniques

### Reasoning Exhaustion

Target chain-of-thought models (Claude extended thinking, OpenAI o-series, DeepSeek R1) with prompts that trigger extended internal evaluation.

See [reasoning_bomb.md](./reasoning_bomb.md) for annotated examples of prompts that maximize thinking token generation while producing minimal visible output.

### Context Window Saturation

See [context_saturation.md](./context_saturation.md) for a crafted input that fills the context window with attacker-controlled content, displacing legitimate instructions.

## Cost Math

| Scenario | Tokens | Cost per Request | 1,000 Requests |
|---|---|---|---|
| Normal API call | ~1,000 total | ~$0.01 | $10 |
| Reasoning bomb (Claude Opus 4.6) | ~50,000 thinking tokens | ~$1.25 | $1,250 |
| Context saturation (128K input) | ~128,000 input tokens | ~$0.64 | $640 |
| Agentic loop (5 tool calls) | ~100,000 total | ~$2.50 | $2,500 |

Output tokens cost 3-5x more than input tokens. Attacks that force verbose output or extended reasoning are the most cost-effective for the attacker.

## Detection

### Signals
- Per-request token consumption exceeding baseline by 10x+
- Thinking token ratio exceeding 5:1 vs visible output
- Repeated requests near context window maximum
- Sudden billing spikes without corresponding user activity increase

### Monitoring
```python
# Pseudocode: flag requests exceeding cost threshold
Request_Cost = (Input_Tokens * Input_Rate) + (Output_Tokens * Output_Rate)
if Request_Cost > Max_Request_Budget:
	Alert("DoW: request cost ${Request_Cost:.2f} exceeds budget")
	Block_Request()
```

## Mitigation

1. **Per-request token budgets**: Cap total tokens (input + output + thinking) per request. LiteLLM and custom proxies support this.
2. **Per-user spend caps**: Track cumulative cost per API key, not just request count. Alert and throttle when budget thresholds are hit.
3. **Reasoning token limits**: Set `max_tokens` and thinking budget parameters to bound worst-case cost.
4. **Input length validation**: Reject inputs exceeding a reasonable length for the use case (don't accept 128K input if your use case needs 2K).
5. **Billing alerts**: Configure provider-level billing alerts at 50%, 80%, and 100% of monthly budget.
6. **Model routing**: Route simple queries to cheap models. Don't use Opus for tasks Haiku can handle.

## Cross-References

- [Note 19: Token-Based Attacks & Resource Exploitation](../../notes/19_Token_Based_Attacks_And_Resource_Exploitation.md) -- Full coverage of DoW, sponge examples, reasoning exhaustion, token smuggling, and defense patterns
- [Note 18: Token Optimization & LLM Efficiency](../../notes/18_Token_Optimization_And_LLM_Efficiency.md) -- Defensive optimization techniques
- [Note 20: LLM Landscape & Token Economics](../../notes/20_LLM_Landscape_Tokens_And_Pricing.md) -- Model pricing reference for cost calculations
