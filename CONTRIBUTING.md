# Contributing

Thanks for helping improve Signal Contract.

## Ground rules

- Keep the protocol small and renderer-facing.
- Do not introduce private channel taxonomy.
- Do not add VET formulas.
- Do not add backend lock-in or vendor-specific transport assumptions.
- Treat examples as adapters, not product surfaces.

## Local validation

```bash
python3 -m pip install jsonschema
python3 -m unittest tests.test_schema -v
```

## Change types

- Docs clarification
- Schema refinement
- Fixture expansion
- Example improvement
- Site copy cleanup

If a change alters the public schema or canonical example, update:

- `spec/v1/schema.json`
- `spec/v1/SPEC.md`
- `README.md`
- `tests/*.json`
- `site/v1/schema.json`

## Pull requests

- Keep PRs narrow.
- Explain whether the change is additive, clarifying, or breaking.
- Include fixture updates for any schema change.
- Avoid product roadmap language in spec docs.

## Versioning

- Backward-compatible field additions belong in a minor release.
- Breaking field changes require a new major version directory.
