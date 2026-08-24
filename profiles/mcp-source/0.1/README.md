# MCP Source Profile 0.1

`vibenet.mcp-source/0.1` is an additive Signal Contract profile. It does not
change Signal Contract v1. It answers one question:

**When does an MCP protocol event become a VIBEnet awareness event?**

MCP carries capability, identity, delegation, tasks, and tool traffic.
Constitutional CMS decides whether a publishing consequence is admissible.
VIBEnet translates only *consequential* transitions into portable perception.

## Law

MCP activity is observation. Only ratified mappings emit. Unknown methods stay
silent. Protected content is stripped before normalization.

Do not sonify every `tools/call`. Healthy tool traffic is not a Signal Contract
event.

## MCP spec pin

Every fixture and emitted event MUST set `metadata.mcp_spec_version` to
`2026-07-28` (stateless HTTP, Tasks as an official extension). Later identity
and event-channel work is tracked, not invented here.

## Mapping

| MCP condition | Profile event | Channel |
| --- | --- | --- |
| task accepted/active | `agent.running` | `nominal` |
| progress / healthy `tools/call` / resource read | silent | — |
| InputRequired / elicitation | `agent.input_requested` | `handoff` |
| approval boundary | `agent.approval_requested` | `handoff` |
| CMS `UNMEASURED` on a proposed publish | `agent.input_requested` | `handoff` |
| task completed | `agent.completed` | `nominal` |
| tool/action fails | `agent.failed` | `warning` or `critical` |
| transport/source disappears | `agent.unobserved` | `advisory` |
| trusted operation after failure / CMS `PASS` | `agent.recovered` | `recovery` |
| authority denied or revoked | `agent.authority_denied` | `warning` or `critical` |

`agent.recovered` requires a **fresh** mapped observation. Elapsed time MUST NOT
invent recovery.

## Privacy

`content_redacted` MUST be `true`. `task_ref` and `actor_ref` MUST be opaque
(`hmac-sha256:…` or `fixture:…`). Profile events MUST NOT contain prompts,
messages, tool arguments/results, tokens, paths, emails, OAuth subjects, or
account identifiers.

Public `entity` is a privacy-safe reference such as `agent.mcp.fixture_task`.
Real MCP identity, if present in the source, belongs only in a mapping receipt
as an opaque actor_ref.

## Conformance

A profile event conforms when it:

1. validates against Signal Contract v1;
2. validates against `profile.schema.json`;
3. matches the event semantics in `profile.json`;
4. contains no data outside the metadata allowlist;
5. pins `mcp_spec_version` to `2026-07-28`.

See `fixtures/valid.jsonl`, `fixtures/invalid.json`, and
`fixtures/authority-trace.jsonl`.
