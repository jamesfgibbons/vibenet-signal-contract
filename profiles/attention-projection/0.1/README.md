# Attention Projection 0.1

`vibenet.attention-projection/0.1` is an adjacent Signal Contract profile. It
does not change Signal Contract v1 and does not add any required top-level
fields to the flat event object.

The profile answers one question: **given many valid Signal Contract events,
which may occupy a human's limited attention without changing what happened?**

The mixer may choose what you notice. It may never decide what happened.
**Selection is not truth.** Foreground is not more true. Ambient is not less
true. Unobserved is not idle and is not nominal.

## Law

1. Source Signal Contract events are immutable inputs. The projection copies
   ids; it MUST NOT rewrite channel, VET, producer, or event name.
2. A governed projection has a hard `max_foreground_slots` budget. The
   published default is **4**.
3. `critical` MUST bypass the budget. A valid critical event MUST NOT vanish
   because other voices are louder.
4. `handoff` MAY reserve a slot. It is a human transfer, not a numeric tie.
5. Related warnings MAY compress into one domain-level ambient group. The
   underlying signal ids stay on the group.
6. An expected entity with no event in the window is `unobserved`. Renderers
   MUST NOT sonify that gap as healthy progress.
7. `RAW` mode is a teaching contrast. It may exceed the slot budget. It is not
   a production default and MUST be labeled `mode: "raw"`.

## Attention classes

| Class | Meaning |
| --- | --- |
| `foreground` | Occupies a scarce human slot. |
| `ambient` | Valid, retained, not solo. |
| `suppressed` | Valid, named on a suppression note, not voiced. |
| `unobserved` | No event arrived for an expected entity. |

Suppressed events remain true. Their ids belong on the receipt.

## Default policy

These values are the published starting policy. Implementations MAY tighten
them. They MUST NOT silently drop critical bypass.

| Key | Default |
| --- | --- |
| `max_foreground_slots` | 4 |
| `critical_bypass` | true |
| `maximum_foreground_latency_ms` | 250 |
| `min_dwell_ms` | 800 |
| `hysteresis_ms` | 600 |
| `handoff_reserved_slot` | true |
| `recovery_hold_ms` | 2000 |

Channel rank is an attention heuristic, not a truth order:

`critical > handoff > warning > opportunity > recovery > advisory > nominal`

## Receipt

`vibenet.attention-receipt/0.1` records one mix: foreground ids, ambient group
ids, a digest of suppressed ids, unobserved entities, and whether critical
bypass fired. `audio_muted` and `reduced_motion` are renderer constraints, not
changes to the source events.

## Conformance

A projection conforms when it:

1. validates against `profile.schema.json`;
2. lists `source_signal_ids` that match the window it claims;
3. keeps `foreground_slots.length <= max_foreground_slots` in `governed` mode;
4. includes every critical source entity in foreground when `critical_bypass`
   is true;
5. treats unobserved entities as a named absence, not as `nominal`.

See `fixtures/` for a synthetic eight-agent window. All fixtures are labeled
synthetic. They are not a product fleet.
