# Task 6-7 integration, Release and browser QA

## Integrated scope

- Catalog schema: version 2
- Paper slots: five papers × nine standard artifact types
- Research-design slots: four
- Final state: 49 complete, 0 missing
- Protected inventory: exactly the source and private full Korean translation for Battilana & Casciaro (2012) and (2013)

## Local gates

- Python: 45 tests passed.
- Node: 9 encryption and protected-viewer tests passed.
- Rights-aware catalog validation: `valid catalog: 6 papers, 49 artifacts`.
- Release staging: 15 files, split into three sources, three public Korean translations, three audios, three PPTX files and three slide PDFs.
- Audio: all three staged M4A files decoded end-to-end without ffmpeg errors.
- Leakage scans: no missing status, private NotebookLM URL, local Windows path, plaintext PDF marker in ciphertext, tracked restricted plaintext or tracked password value.

## Published Release

- Tag: `artifacts-2026-08-11-v2`
- URL: https://github.com/Beaten-to-it/paper/releases/tag/artifacts-2026-08-11-v2
- GitHub asset count: 15
- All GitHub-reported sizes and SHA-256 digests matched the local staging files.
- Independent download check: one audio, one PPTX and one Korean translation PDF were downloaded again and matched the staged SHA-256 values.

## Local browser QA

- Desktop 1440 × 1000 and mobile 390 × 844 layouts rendered without visible clipping.
- Summary displayed six paper/research groups and 49 complete artifacts.
- Search for `Battilana` returned the two expected papers.
- Clearing search and selecting the source-paper filter returned the five expected papers.
- The internal Markdown viewer rendered the Golgeci NotebookLM run record and its table.
- The protected viewer rejected an incorrect password without exposing a PDF.
- The approved password opened the catalog-bound encrypted 2012 source in a memory Blob iframe.
- Reloading the protected viewer removed the iframe and returned to the locked state.
- Browser console reported zero errors and zero warnings.

QA screenshots remain ignored under `output/playwright/`; they contain no password or restricted PDF body.
