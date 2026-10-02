# Signal Contract principles

This page collects six principles that the published Signal Contract profiles
already state. It is a reading guide. It is not normative, it adds no fields,
and it does not change `schema_version`. When this page and a profile differ,
the profile is correct.

| # | Principle | Stated in |
| --- | --- | --- |
| 1 | Observation is not understanding. | [Adapter Profile 0.1](profiles/adapter-profile/0.1/) |
| 2 | Understanding is not authorization to render. | [Adapter Profile 0.1](profiles/adapter-profile/0.1/) |
| 3 | Only ratified adapter rules may emit Signal Contract events. | [Adapter Profile 0.1](profiles/adapter-profile/0.1/) |
| 4 | Selection is not truth. | [Attention Projection 0.1](profiles/attention-projection/0.1/) |
| 5 | Unobserved is not nominal. | [Attention Projection 0.1](profiles/attention-projection/0.1/), [Adapter Profile 0.1](profiles/adapter-profile/0.1/), [Agent Lifecycle 0.1](profiles/agent-lifecycle/0.1/) |
| 6 | Projection must not rewrite what happened. | [Attention Projection 0.1](profiles/attention-projection/0.1/) |

## 1. Observation is not understanding

An adapter may receive, store, and count a source event without a rule that
maps it.

- **Adapter:** observing a source event does not oblige you to map it. A
  source event that does not become a Signal Contract event is rejected with
  exactly one named reason, such as `unmapped`.
- **Consumer:** the absence of a Signal Contract event does not mean the source
  was quiet. It can mean the source was observed and not mapped.

See: [Adapter Profile 0.1, Law](profiles/adapter-profile/0.1/README.md#law)
(rule 1), [Reject reasons](profiles/adapter-profile/0.1/README.md#reject-reasons),
and `notes.observed_vs_understood` in
[`profile.json`](profiles/adapter-profile/0.1/profile.json).

## 2. Understanding is not authorization to render

A matching `proposed` rule is understanding. It is not authorization to
emit.

- **Adapter:** a matching `proposed` rule may be inspected, compared, and
  rejected. It must not emit.
- **Consumer:** an unmapped observation stays silent. A renderer must not
  invent a channel, event name, or VET state to fill the gap.

See: [Adapter Profile 0.1, Law](profiles/adapter-profile/0.1/README.md#law)
(rules 2 and 6) and `notes.understood_vs_authorized` in
[`profile.json`](profiles/adapter-profile/0.1/profile.json).

## 3. Only ratified adapter rules may emit Signal Contract events

Only a rule with status `accepted` is eligible to emit. `proposed` and
`rejected` rules never emit. Browser assist may draft `proposed` rules only.

- **Adapter:** the first matching accepted rule wins. Ignored classes are
  trace-only. Every emitted object must validate against Signal Contract v1
  and must not carry a protected field.
- **Consumer:** the listening receipt names which accepted and proposed rules
  were loaded and which Signal Contract ids were actually emitted.

See: [Adapter Profile 0.1, Rule status](profiles/adapter-profile/0.1/README.md#rule-status),
[Law](profiles/adapter-profile/0.1/README.md#law) (rules 2 to 5),
[Conformance](profiles/adapter-profile/0.1/README.md#conformance),
[Listening receipt](profiles/adapter-profile/0.1/README.md#listening-receipt),
and `emit_policy`, `emit_statuses`, and `notes.assist_cannot_emit` in
[`profile.json`](profiles/adapter-profile/0.1/profile.json).

## 4. Selection is not truth

An attention projection chooses which valid events a human notices. It does
not decide what happened.

- **Projection:** foreground is not more true. Ambient is not less true.
  Suppressed events remain true, and their ids belong on the receipt. Channel
  rank is an attention heuristic, not a truth order.
- **Consumer:** the mixer may choose what you notice. It may never decide
  what happened. Read what happened from the source events, not from the mix.

See: [Attention Projection 0.1](profiles/attention-projection/0.1/README.md),
[Attention classes](profiles/attention-projection/0.1/README.md#attention-classes),
[Default policy](profiles/attention-projection/0.1/README.md#default-policy),
and `selection_is_not_truth` in
[`profile.json`](profiles/attention-projection/0.1/profile.json).

## 5. Unobserved is not nominal

No event is not the same fact as a healthy event.

- **Projection:** an expected entity with no event in the window is
  `unobserved`. Renderers must not sonify that gap as healthy progress.
  Conformance treats unobserved entities as a named absence, not as `nominal`.
- **Adapter:** `unmapped` is not `nominal`, not `idle`, and not a reason to
  sonify "everything is fine."
- **Lifecycle:** source disconnect, expiration, or `notLoaded` produces
  `unobserved`. Its typical public event uses the `advisory` channel.
  `notLoaded` is not `idle`.

See: [Attention Projection 0.1, Law](profiles/attention-projection/0.1/README.md#law)
(rule 6), [Conformance](profiles/attention-projection/0.1/README.md#conformance)
(item 5), `unobserved_is_not` in
[`profile.json`](profiles/attention-projection/0.1/profile.json);
[Adapter Profile 0.1, Reject reasons](profiles/adapter-profile/0.1/README.md#reject-reasons)
and `source_loss_is_not` in
[`profile.json`](profiles/adapter-profile/0.1/profile.json);
[Agent Lifecycle 0.1, Lifecycle states](profiles/agent-lifecycle/0.1/README.md#lifecycle-states)
and [Reducer rules](profiles/agent-lifecycle/0.1/README.md#reducer-rules).

## 6. Projection must not rewrite what happened

Source Signal Contract events are immutable inputs to a projection.

- **Projection:** copy ids. Do not rewrite channel, VET, producer, or event
  name. Compressed warning groups keep their underlying signal ids.
- **Consumer:** `audio_muted` and `reduced_motion` on an attention receipt are
  renderer constraints. They are not changes to the source events.

See: [Attention Projection 0.1, Law](profiles/attention-projection/0.1/README.md#law)
(rules 1 and 5) and [Receipt](profiles/attention-projection/0.1/README.md#receipt).
The same rule appears for receipts and paths elsewhere: the
[listening receipt](profiles/adapter-profile/0.1/README.md#listening-receipt)
does not rewrite the source stream or the emitted events, and a
[modulation path](profiles/modulation-profile/0.1/README.md) does not rewrite
producer values and leaves its waypoints unchanged.
