# Modulation Profile 0.1

`vibenet.modulation-profile/0.1` is an adjacent Signal Contract profile. It does
not change Signal Contract v1 and does not add any required top-level fields to
the flat event object.

The profile answers one question: **how may renderer-facing state travel
between two immutable Signal Contract waypoints?**

A Signal Contract event is a point. A modulation profile is the governed path
between two points. The waypoints MUST remain byte-identical after derivation
and after sampling. Intermediate contour samples are not Signal Contract events
and MUST NOT invent a channel.

## Law

1. `previous_signal_id` and `target_signal_id` name existing Signal Contract
   events. The profile does not own those events.
2. Curves interpolate `valence`, `energy`, `tension`, `intensity`, and `pulse`
   toward the **target** waypoint. They do not rewrite producer values.
3. Same terminal VET with a different `transition_class` is legal and
   meaningful. Arrival is not the same fact as destination.
4. Channel safety may **tighten** onset or hold. It MUST NOT loosen concealment
   of a critical or handoff.
5. `Contour Off` (state-only) is an instantaneous jump to the target waypoint.
   It is a renderer mode, not a new event.
6. A locked handoff MUST NOT release until a terminal decision exists.

## Transition classes

| Class | Typical story | Interruptibility | Attention |
| --- | --- | --- | --- |
| `nominal_step` | Healthy progress | soft | ambient |
| `gradual_degrade` | Retries, thinning evidence | soft | notice |
| `sudden_contradiction` | Source-of-truth snap | hard | interrupt |
| `escalation` | Pressure building | soft | notice or interrupt |
| `handoff` | Human transfer | locked | notice |
| `recovery` | Trusted return | soft | resolve |
| `completion` | Terminal success | soft | resolve |
| `opportunity_lift` | Consonant lift | soft | notice |

## Channel safety

These bounds are normative. A derivation that exceeds them MUST cap, not
ignore.

| Channel | max onset | min stabilization | resolve requires terminal |
| --- | --- | --- | --- |
| `nominal` | 2000 ms | 0 ms | no |
| `advisory` | 1200 ms | 0 ms | no |
| `opportunity` | 1000 ms | 0 ms | no |
| `warning` | 600 ms | 200 ms | no |
| `critical` | 180 ms | 400 ms | no |
| `handoff` | 500 ms | 800 ms | yes |
| `recovery` | 900 ms | 1200 ms | no |

`critical_onset_capped`, `handoff_resolve_blocked`, and
`recovery_fullness_gated` are receipt flags. They record that safety changed
the curve. They are not new channels.

## Same state, different arrival

A conforming pair of paths may share start and end Signal Contract waypoints
and still differ in `transition_class`, curve kind, and timing. Renderers that
drop the modulation object will hear nearly the same point-state. Renderers
that honor it will hear different operational stories.

## Conformance

A modulation profile conforms when it:

1. validates against `profile.schema.json`;
2. names two Signal Contract ids and does not embed replacement events;
3. respects the channel safety table in `profile.json`;
4. leaves the referenced waypoints unchanged.

The derivation receipt conforms when it validates against `receipt.schema.json`
and repeats the same ids, class, and safety flags.

See `fixtures/` for a synthetic same-state pair. All fixtures are labeled
synthetic.
