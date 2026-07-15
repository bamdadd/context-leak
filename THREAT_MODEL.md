# Threat model & safety rationale

**This is a defensive evaluation harness.** It measures whether an agent respects
context-dependent information norms — need-to-know discipline — so that respect
can be measured and improved. It is not an attack toolkit.

- **Goal:** measure and improve contextual-integrity robustness. Scenarios exist
  only to score whether an agent discloses an attribute to a recipient the
  context forbids.
- **Synthetic only.** Every attribute value, recipient, and scenario is
  **invented**. There is **zero real customer or patient data**. Figures like
  `$47,318.22` and diagnosis codes are fabricated to be unique, not sourced.
- **Success criterion:** *verified* inappropriate disclosure — a deterministic,
  per-recipient check of whether the agent's own output to a forbidden recipient
  contains the attribute's value or a declared alias. **Never an LLM judge.**
- **Not shipped:** no exploit payloads, no jailbreaks, no real records. The
  benchmark scores information *flows*, not attacks.
- **Lower bound, by design.** Detection is verbatim/alias value match, so the
  reported disclosure rate under-counts paraphrase and confirm/deny. A
  deterministic match never fabricates a violation; missing paraphrase is the
  honest cost (see the README limitation and future work).
- **Disclosure:** if the harness is ever run against a live product and surfaces
  a real inappropriate-disclosure path, disclose privately to the affected vendor
  first. Never publish a working exploit against a named deployment.
