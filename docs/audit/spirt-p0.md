# SPIRT P0 Hardening Plan

## Scope

P0 strengthens the stable 1.0 foundation without changing the public-only OSINT boundary.

### Workstreams

1. Evidence validation and provenance integrity.
2. Collection result invariants and deterministic serialization.
3. Safe HTTP input validation and bounded response reads.
4. Provider contract tests and regression coverage.
5. CI checks for formatting, linting, and tests.

## Design constraints

- Collect only legitimately public resources.
- Do not bypass authentication, anti-bot controls, rate limits, or access controls.
- Keep provider implementations behind the existing provider contract.
- Preserve backwards-compatible JSON fields unless a change is explicitly versioned.
- Prefer explicit, explainable failure states over silent fallbacks.

## Acceptance criteria

- Invalid evidence confidence and empty provenance fields fail early.
- HTTP collection rejects non-HTTPS and malformed URLs before network access.
- HTTP responses have a bounded body size.
- Existing collection/report JSON remains compatible.
- Tests cover the new invariants.
