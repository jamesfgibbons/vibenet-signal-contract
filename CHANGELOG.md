# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows semantic versioning.

## [Unreleased]

## [1.1.0] - 2026-08-16

### Added

- Added the non-breaking `vibenet.agent-lifecycle/0.1` profile
- Added a closed metadata allowlist, machine-readable event semantics, and deterministic valid/invalid fixtures
- Added profile conformance tests without changing Signal Contract v1 schema fields
- Added adjacent `vibenet.adapter-profile/0.1` (observed ≠ understood ≠ authorized to render)
- Added adjacent `vibenet.modulation-profile/0.1` (same state, different arrival; waypoints immutable)
- Added adjacent `vibenet.attention-projection/0.1` (selection is not truth; unobserved ≠ nominal)
- Added listening, modulation, and attention receipts as companion schemas
- Added synthetic fixtures and tests for the three adjacent profiles

### Notes

- Signal Contract `schema_version` remains `"1.0"`. These profiles do not add required fields to the flat event.

## [1.0.1] - 2026-04-21

### Added

- Documented the optional `metadata.publishable`, `metadata.indexable`, and `metadata.fallback_reason` convention
- Added a canonical fallback-state example showing `publishable: false` and `indexable: true`

### Changed

- Annotated the v1 schema `metadata` description without adding required fields, top-level fields, or a `schema_version` bump

## [1.0.0] - 2026-04-20

### Changed

- Canonicalized the repo to the live flat Signal Contract v1 schema served by VIBEnet
- Replaced stale `timestamp` and nested `coordinates` examples with the published flat event object
- Reframed the package publicly as VIBEnet Signal Contract
- Updated the reference site, examples, fixtures, and tests to the flat v1 shape

### Added

- Seven top-level example events, one for each public semantic channel
- Manual dual-publish guidance for keeping the repo and live VIBEnet schema in sync

## [0.1.0] - 2026-04-19

### Added

- Initial public scaffold for Signal Contract v1
- JSON Schema Draft 2020-12 schema
- v1 protocol spec
- Canonical example and public semantic channel set
- Browser earcon example
- Python logger example
- Valid, invalid, and edge fixtures
- Schema validation test suite
- GitHub Actions validation workflow
- Minimal static site and schema route
