# Adjacent profiles

These packages sit **next to** Signal Contract v1. They do not change
`schema_version`, do not add required fields to the flat event, and are not a
v2 object.

| Package | Object | Question |
| --- | --- | --- |
| [agent-lifecycle/0.1](agent-lifecycle/0.1/) | Profiled SC event | What should a renderer know about an agent without private content? |
| [adapter-profile/0.1](adapter-profile/0.1/) | Mapping rules + listening receipt | When may a foreign source event become a Signal Contract event? |
| [modulation-profile/0.1](modulation-profile/0.1/) | Arrival path + derivation receipt | How may renderer-facing state travel between two immutable waypoints? |
| [attention-projection/0.1](attention-projection/0.1/) | Mix + attention receipt | Which valid events may occupy limited attention without changing truth? |

Fixtures are synthetic. They are not production traces.
