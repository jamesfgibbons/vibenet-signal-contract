# Releasing VIBEnet Signal Contract

Use this checklist for every public protocol release.

## Before tagging

1. Run schema tests:

   ```bash
   .venv/bin/python -m unittest tests.test_schema -v
   ```

2. Confirm the two published schema copies stay identical:

   ```bash
   diff -u spec/v1/schema.json site/v1/schema.json
   ```

3. Run a whitespace and patch sanity check:

   ```bash
   git diff --check
   ```

4. Confirm the canonical schema URL remains correct:

   - `spec/v1/schema.json` uses `https://vibenet.ai/protocol/v1/schema.json`
   - `site/v1/schema.json` uses `https://vibenet.ai/protocol/v1/schema.json`

5. Update `CHANGELOG.md` for the release.

## Tagging and publishing

1. Commit the release changes on `main`.
2. Create the release tag:

   ```bash
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```

3. Confirm the tag exposes the released schema at:

   `https://raw.githubusercontent.com/jamesfgibbons/vibenet-signal-contract/vX.Y.Z/spec/v1/schema.json`

## After release

If the new release should become the schema that `vibenet.ai` serves:

1. Open a separate `vibenet-frontend` PR.
2. Update:
   - `docs/ops/protocol_source.lock.json`
   - `public/protocol/v1/schema.json` only if the protocol intentionally changed
3. Let the frontend `protocol-integrity` workflow verify the adoption.

Do not treat an untagged `main` commit as the protocol source for `vibenet.ai`.
