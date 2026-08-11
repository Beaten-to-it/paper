# Task 2 encrypted viewer review ledger

## Review target

- Full-review commit: `bda1ff374428533f6db8c32567cd53d2844893bc`
- Full-review tree: `d0762464fe1bb900b7f707a71e83bad1d01766b3`
- Reviewer: isolated Codex `gpt-5.6-sol`, reasoning `xhigh`, read-only
- Substitution reason: Claude Opus 5 service calls previously timed out at 60, 180, and 300 seconds; the user explicitly approved an isolated Codex alternative review.
- Gate: `Critical = 0`, `High = 0`

## Full-review result

- Critical: 0
- High: 1
- Gate: failed pending correction

### H1 — valid encrypted companion substitution

- Status: accepted and fixed
- Entry point: `site/assets/protected-viewer.js`
- Reproduction: keep artifact A's catalog metadata unchanged but serve a different valid same-password container B from A's path. The original viewer decrypted B and displayed it under A's title because it checked only PDF magic.
- Impact: silent protected-artifact integrity substitution.
- Correction: fetch ciphertext as raw bytes; enforce catalog-declared size and SHA-256; compare container version, algorithm, KDF, and iteration count before decryption.
- Regression: `tests/protected_viewer.test.mjs` swaps equal-length valid containers encrypted with the same password and requires an integrity rejection.

## Hardening observations

### M1 — pagehide unlock race

- Status: fixed
- Correction: relock now aborts the current fetch, clears the password field, increments an unlock generation, and rejects any late completion before creating a Blob URL.

### M2 — unbounded PBKDF2 work and container size

- Status: fixed
- Correction: browser parser and catalog validator now cap PBKDF2 iterations at 2,000,000 and encrypted Pages payloads at 50 MiB.
- Regression: Node rejects 2,000,001 iterations; Python rejects a matching catalog/container with 2,000,001 iterations.

## Verification before closure review

- `python -m unittest discover -s tests -v`: 43 passed.
- `node --test tests\\*.test.mjs`: 9 passed.
- `python tools\\validate_catalog.py site\\data\\catalog.json site`: valid catalog, 6 papers, 39 artifacts.
- `git diff --check`: passed.

## Targeted closure review

- Status: pending
