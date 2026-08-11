# Task 8 final integration review ledger

## Review substitution

- Default reviewer: Claude Opus 5 with xhigh effort.
- Substitution reason: the Claude review service timed out earlier in this task.
- Authorization: the user explicitly approved an isolated Codex substitute review.
- Substitute configuration: fresh agent with no forked conversation, `gpt-5.6-sol`, xhigh reasoning, read-only instructions and an exact commit/tree target.

## Initial latest-tree review

- Target commit: `d7248e068863bbe5c8591fe781cbbb9458347da5`
- Target tree: `8a42b4f61181c163cdbd97195f58f138feafec5a`
- Reviewer state: the agent delivered a reproduced High finding, then its final response was interrupted by a service safety filter. No reviewer writes occurred.

### H1 — catalog-wide identity and artifact-binding bypass

- Severity: High
- Reproduced supported entry points:
  1. Duplicating the Kemell group allowed seven groups and 58 artifacts to validate.
  2. Changing the restricted 2013 paper to `research-design`, poisoning its rights source and substituting an unrelated DOI allowed validation.
  3. Swapping the full source Release URL/size/SHA-256 triplets between Kemell and Neumann allowed validation and would silently serve each source under the other paper card.
- Root cause: the validator checked per-item shape, rights and published digests but did not bind the complete canonical group set, group identities, globally unique artifact IDs, or each group/slot to its approved storage and URL.
- Disposition: accepted and fixed in `6eb297a5700b1ba479ee1606e3ea79d1e11c1b67`.
- Correction: canonical version 2, six unique group identities, 49 unique artifact IDs and every artifact ID/type/storage/URL binding are now enforced before file validation. Version downgrade is rejected.
- Regression coverage: duplicate group, restricted-paper kind downgrade and rights poisoning, source swap, duplicate artifact ID and catalog-version downgrade.
- Local result after correction: Python 51/51, Node 9/9, live Release-backed validator `6 papers, 49 artifacts`.

## Closure target

- Corrected commit before this ledger: `6eb297a5700b1ba479ee1606e3ea79d1e11c1b67`
- Corrected tree before this ledger: `d81c4463500e0299844876e233b0599a0071bbfd`
- Latest-tree closure review: pending on the commit containing this ledger.
