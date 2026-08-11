# Complete Paper Artifacts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete all 49 Paper Lab artifact slots, publish rights-cleared materials openly, and make only four restricted PDFs available through browser-side password decryption.

**Architecture:** `site/data/catalog.json` remains the public source of truth. Public files use GitHub Pages or the `artifacts-2026-08-11-v2` Release; four restricted PDFs are encrypted locally into self-describing AES-256-GCM containers and decrypted only in browser memory. Content generation stays in the research workspace, while only reviewed public artifacts and ciphertext enter Git.

**Tech Stack:** Python 3.13, Node.js Web Crypto and Node test runner, static HTML/CSS/JavaScript, NotebookLM in the signed-in browser, bundled presentation/PDF tooling, GitHub Actions/Releases/Pages.

## Global Constraints

- Password-gate exactly four items: source and private full Korean translation for Battilana & Casciaro (2012) and (2013).
- Never store the real password in tracked files, tests, Actions, Release metadata, browser storage, or published logs.
- Use AES-256-GCM; PBKDF2-HMAC-SHA-256 with random 16-byte salt, random 12-byte IV, and at least 600,000 iterations per file.
- Restricted plaintext stays only in `C:\Users\kimhy\OneDrive\문서\ChatGPT\논문작성\output\private-translations\` or the existing local source directory.
- Publish the three CC BY 4.0 source PDFs and unofficial full Korean translations with attribution, license, adaptation, and “인용은 원문 기준” notices.
- Preserve section structure, hypotheses, sample/statistical values, table/figure numbering, and references; do not reproduce separately licensed third-party figures.
- Give each paper exactly nine types: `source_paper`, `korean_version`, `analysis`, `notebooklm_prompt`, `notebooklm_run`, `audio`, `slides`, `slide_pdf`, `infographic`.
- Final catalog: 49 slots, 49 `complete`, 0 `missing`.
- Each NotebookLM notebook contains exactly one source; public records never expose its private URL.
- Visually verify every PDF/PPT/infographic, fully decode each audio file, and validate every file size and SHA-256.
- Deploy only after a latest-tree Claude Opus 5 review reports `Critical = 0` and `High = 0`.

## File Map

- Create `tools/protected_crypto.mjs`: local container encryption/decryption CLI.
- Create `site/assets/protected-crypto.js`: browser-safe parser and AES-GCM decryption.
- Create `site/assets/protected-viewer.js` and `site/protected-viewer.html`: password UI and memory-only PDF viewer.
- Create `tests/protected_crypto.test.mjs`: success, wrong-password, and tamper tests.
- Modify `tools/validate_catalog.py`, `tests/test_validate_catalog.py`, and `tests/test_site_contract.py`: rights/access/secret/49-slot contract.
- Modify `site/data/catalog.json`, `site/assets/app.js`, `site/assets/styles.css`, and `site/index.html`: complete catalog, badges, links, and notices.
- Create two public Korean study guides, three NotebookLM run records, three infographics, and four `site/protected/*.enc` containers.
- Modify `.github/workflows/pages.yml`, `.gitignore`, and `README.md`.
- Create public/private translations, three audio files, three PPTX/PDF pairs, infographics, and local QA renders under `C:\Users\kimhy\OneDrive\문서\ChatGPT\논문작성\output\` and `tmp\qa\`.

---

### Task 1: Define the rights-aware catalog contract

**Files:**
- Modify: `tests/test_validate_catalog.py`
- Modify: `tests/test_site_contract.py`
- Modify: `tools/validate_catalog.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `validate(catalog: dict, public_root: Path) -> tuple[int, int]`.
- Produces: `validate_rights(paper: dict)`, `validate_external_url(artifact: dict)`, `validate_protected(artifact: dict, root: Path, declared: set[str])`, and exact nine-slot validation.

- [ ] **Step 1: Add failing schema tests**

```python
def test_rejects_restricted_paper_public_redistribution(self):
    catalog = self.complete_fixture()
    paper = catalog["papers"][3]
    paper["artifacts"][0]["storage"] = "release"
    result = self.run_validator(catalog, self.fixture_files())
    self.assertIn("rights do not allow public redistribution", result.stderr)

def test_rejects_wrong_paper_slot_set(self):
    catalog = self.complete_fixture()
    catalog["papers"][0]["artifacts"].pop()
    result = self.run_validator(catalog, self.fixture_files())
    self.assertIn("nine-slot contract", result.stderr)
```

- [ ] **Step 2: Confirm tests fail before implementation**

```powershell
python -m unittest tests.test_validate_catalog tests.test_site_contract -v
```

Expected: FAIL because rights, `external`, `protected`, and exact slots are unsupported.

- [ ] **Step 3: Implement the minimal contract**

```python
PAPER_SLOT_TYPES = {
    "source_paper", "korean_version", "analysis", "notebooklm_prompt",
    "notebooklm_run", "audio", "slides", "slide_pdf", "infographic",
}
ALLOWED_STORAGE = {"pages", "release", "external", "protected"}
ALLOWED_EXTERNAL_HOSTS = {"dash.harvard.edu", "doi.org", "pubsonline.informs.org"}

def validate_rights(paper: dict) -> None:
    required = {"license", "redistribution", "translation_publication", "source_url", "checked_at"}
    if set(paper["rights"]) != required:
        raise CatalogError("invalid rights metadata")
```

Enforce allowed HTTPS host/DOI pairs, access values `public`, `official_link_plus_password_encrypted`, and `public_plus_password_encrypted`, a declared protected inventory, exact paper slots, 49 total slots, and zero incomplete status in the final catalog.

Use these shapes consistently:

```json
{"type":"source_paper","storage":"release","access":"public","href":"https://github.com/Beaten-to-it/paper/releases/download/artifacts-2026-08-11-v2/file.pdf"}
{"type":"source_paper","storage":"external","access":"official_link_plus_password_encrypted","href":"https://doi.org/10.0000/example","protected":{"href":"protected/bc2012-source.enc","size_bytes":1,"sha256":"64-hex","container_version":1,"algorithm":"AES-256-GCM","kdf":"PBKDF2-HMAC-SHA-256","iterations":600000}}
{"type":"korean_version","storage":"pages","access":"public_plus_password_encrypted","translation_kind":"detailed_study_guide","href":"downloads/battilana-casciaro-2012/korean-study-guide.md","protected":{"href":"protected/bc2012-korean-full.enc","size_bytes":1,"sha256":"64-hex","container_version":1,"algorithm":"AES-256-GCM","kdf":"PBKDF2-HMAC-SHA-256","iterations":600000}}
```

- [ ] **Step 4: Exclude plaintext build areas**

```gitignore
output/private-translations/
output/translations/
output/release-assets/
output/rendered/
```

Do not ignore `site/protected/`.

- [ ] **Step 5: Run tests and commit**

```powershell
python -m unittest discover -s tests -v
git add .gitignore tools/validate_catalog.py tests/test_validate_catalog.py tests/test_site_contract.py
git commit -m "test: define rights-aware artifact contract"
```

---

### Task 2: Implement encrypted PDF containers and viewer

**Files:**
- Create: `tools/protected_crypto.mjs`
- Create: `site/assets/protected-crypto.js`
- Create: `site/assets/protected-viewer.js`
- Create: `site/protected-viewer.html`
- Create: `tests/protected_crypto.test.mjs`
- Modify: `site/assets/styles.css`
- Modify: `tests/test_site_contract.py`

**Interfaces:**
- Produces: `encryptBytes(plaintext, password, options)`, `parseContainer(text)`, `decryptContainer(container, password)`, and CLI `node tools/protected_crypto.mjs encrypt --input <pdf> --output <enc>` reading only `PAPER_PRIVATE_PASSWORD`.

- [ ] **Step 1: Write the failing Node round-trip test**

```javascript
test("round-trip, wrong password, and tamper", async () => {
  const password = "test-only-long-password";
  const pdf = new TextEncoder().encode("%PDF-1.7\nfixture\n%%EOF");
  const container = await encryptBytes(pdf, password, { iterations: 600000 });
  assert.deepEqual(await decryptContainer(container, password), pdf);
  await assert.rejects(decryptContainer(container, "wrong-password"));
  container.ciphertext = flipOneBase64Byte(container.ciphertext);
  await assert.rejects(decryptContainer(container, password));
});
```

- [ ] **Step 2: Confirm the module-not-found failure**

```powershell
node --test tests/protected_crypto.test.mjs
```

- [ ] **Step 3: Implement the container and atomic CLI**

```javascript
export async function encryptBytes(plaintext, password, options = {}) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const iterations = options.iterations ?? 600000;
  const key = await deriveAesKey(password, salt, iterations, ["encrypt"]);
  const ciphertext = new Uint8Array(await crypto.subtle.encrypt({name: "AES-GCM", iv}, key, plaintext));
  return {version: 1, algorithm: "AES-256-GCM", kdf: "PBKDF2-HMAC-SHA-256", iterations, salt: toBase64(salt), iv: toBase64(iv), ciphertext: toBase64(ciphertext)};
}
```

Abort if the environment variable is absent or shorter than four characters. Put no password, plaintext filename, MIME text, or plaintext hash in the container. Write atomically and verify decrypt-and-hash before replacing the destination.

- [ ] **Step 4: Implement the memory-only browser viewer**

```javascript
const bytes = await decryptContainer(container, passwordInput.value);
if (!startsWithPdfMagic(bytes)) throw new Error("PDF 형식 검증 실패");
activeUrl = URL.createObjectURL(new Blob([bytes], {type: "application/pdf"}));
pdfFrame.src = activeUrl;
passwordInput.value = "";
addEventListener("pagehide", () => activeUrl && URL.revokeObjectURL(activeUrl));
```

Read an artifact ID, look it up in `catalog.json`, allow only declared `protected/*.enc`, use `type="password"`, show a generic failure message, and never use storage, cookies, analytics, or a server endpoint.

- [ ] **Step 5: Add and run lock-boundary tests**

```python
def test_protected_viewer_does_not_persist_password(self):
    html = (SITE_ROOT / "protected-viewer.html").read_text(encoding="utf-8")
    script = (SITE_ROOT / "assets/protected-viewer.js").read_text(encoding="utf-8")
    self.assertIn('type="password"', html)
    self.assertNotIn("localStorage", script)
    self.assertNotIn("sessionStorage", script)
    self.assertIn("URL.revokeObjectURL", script)
```

```powershell
node --test tests/protected_crypto.test.mjs
python -m unittest discover -s tests -v
rg -n --hidden --glob '!.git/**' --glob '!docs/superpowers/**' 'PAPER_PRIVATE_PASSWORD\s*=' .
```

Expected: tests PASS and the secret scan has no tracked implementation match.

- [ ] **Step 6: Commit the crypto slice**

```powershell
git add tools/protected_crypto.mjs site/assets/protected-crypto.js site/assets/protected-viewer.js site/protected-viewer.html site/assets/styles.css tests/protected_crypto.test.mjs tests/test_site_contract.py
git commit -m "feat: add encrypted restricted-paper viewer"
```

---

### Task 3: Produce five Korean paper versions

**Files:**
- Create in research workspace: `output/translations/Kemell-2025-Korean-unofficial-translation.pdf`, `Neumann-2026-Korean-unofficial-translation.pdf`, `Golgeci-2025-Korean-unofficial-translation.pdf`.
- Create in research workspace: `output/private-translations/Battilana-Casciaro-2012-Korean-full-translation-private.pdf`, `Battilana-Casciaro-2013-Korean-full-translation-private.pdf`.
- Create: `site/downloads/battilana-casciaro-2012/korean-study-guide.md`.
- Create: `site/downloads/battilana-casciaro-2013/korean-study-guide.md`.

**Interfaces:**
- Consumes: five existing `output/pdf/*.pdf` sources.
- Produces: five Korean PDFs, two non-substitutive public study guides, and a local-only hash/page QA manifest.

- [ ] **Step 1: Extract page-addressable source text**

```powershell
pdftotext -layout "output\pdf\Kemell-et-al-2025-Still-just-personal-assistants.pdf" "tmp\translations\kemell-2025.txt"
pdftotext -layout "output\pdf\Neumann-et-al-2026-Between-policy-and-practice.pdf" "tmp\translations\neumann-2026.txt"
pdftotext -layout "output\pdf\Golgeci-et-al-2025-AI-resistance-process-framework.pdf" "tmp\translations\golgeci-2025.txt"
pdftotext -layout "output\pdf\Battilana-Casciaro-2012-Change-agents-networks-institutions.pdf" "tmp\translations\bc2012.txt"
pdftotext -layout "output\pdf\Battilana-Casciaro-2013-Strong-ties-affective-cooptation.pdf" "tmp\translations\bc2013.txt"
```

Run in the research workspace and verify titles, headings, tables, and references before translating.

- [ ] **Step 2: Translate under a fixed fidelity rule**

Use each extracted text as the sole source. Translate section-by-section into natural academic Korean; copy numbers/citations exactly; retain `〔원문 p. N〕`; mark unreadable content `[원문 판독 필요: 페이지 N]`; never invent values or reconstruct excluded third-party figures.

- [ ] **Step 3: Generate the five PDFs**

```python
PUBLIC_NOTICE = "AI 보조 비공식 한국어 번역입니다. 학술 인용은 반드시 원문을 기준으로 하십시오."
PRIVATE_NOTICE = "비공개 개인 학습용 · 재배포 금지"
CC_BY_NOTICE = "Creative Commons Attribution 4.0 — https://creativecommons.org/licenses/by/4.0/"
```

Use embedded Korean fonts, title/rights page, running title, page numbers, and repeating table headers. Add attribution and `CC_BY_NOTICE` to three public translations; watermark every restricted page with `PRIVATE_NOTICE`.

- [ ] **Step 4: Write two public study guides**

Each Markdown file starts with `전문 번역 아님`, official source and DOI, then research question, theory, hypotheses, method/sample, results, network interpretation, strengths, limitations, doctoral-study connection, and citation guidance. Paraphrase; do not reproduce a continuous translation.

- [ ] **Step 5: Render and inspect every page**

```powershell
pdftoppm -png -r 144 "output\translations\Kemell-2025-Korean-unofficial-translation.pdf" "tmp\qa\translations\kemell\page"
pdftoppm -png -r 144 "output\private-translations\Battilana-Casciaro-2012-Korean-full-translation-private.pdf" "tmp\qa\translations\bc2012\page"
```

Repeat for all five. Inspect every PNG for Korean font substitution, clipping, empty pages, broken tables, missing watermark, and incorrect source-page markers; regenerate until clean.

- [ ] **Step 6: Verify notices and commit only public guides**

```powershell
pdftotext "output\translations\Golgeci-2025-Korean-unofficial-translation.pdf" - | rg "AI 보조 비공식 한국어 번역|인용은.*원문"
pdftotext "output\private-translations\Battilana-Casciaro-2013-Korean-full-translation-private.pdf" - | rg "비공개 개인 학습용|재배포 금지"
Get-FileHash -Algorithm SHA256 output\translations\*.pdf,output\private-translations\*.pdf
git add site/downloads/battilana-casciaro-2012/korean-study-guide.md site/downloads/battilana-casciaro-2013/korean-study-guide.md
git commit -m "docs: add restricted-paper Korean study guides"
```

---

### Task 4: Generate three NotebookLM runs and audio files

**Files:**
- Create: `site/downloads/golgeci-2025/notebooklm-run.md`.
- Create: `site/downloads/battilana-casciaro-2012/notebooklm-run.md`.
- Create: `site/downloads/battilana-casciaro-2013/notebooklm-run.md`.
- Create in research workspace: `output/audio/Golgeci-2025-Korean-deep-dive.m4a`, `Battilana-Casciaro-2012-Korean-deep-dive.m4a`, `Battilana-Casciaro-2013-Korean-deep-dive.m4a`.

**Interfaces:**
- Consumes: one source PDF and its checked-in `notebooklm-prompts.md` per notebook.
- Produces: three real NotebookLM audio downloads and three public run records without notebook URLs.

- [ ] **Step 1: Create isolated notebooks**

In the signed-in browser, create one notebook per paper, upload exactly the matching PDF, and verify the source count is `1`. Do not combine papers or add web sources.

- [ ] **Step 2: Generate and download Korean deep-dive audio**

Paste only the audio instruction from the matching prompt, choose Korean, wait until generation finishes, and download to the exact filenames above. A failed or partial generation remains incomplete and is not replaced with synthetic filler.

- [ ] **Step 3: Write observed run metadata**

```markdown
# NotebookLM 실행·검증 기록

- 실행일: 2026-08-11
- 소스 수: 1
- 언어: 한국어
- 산출물: Audio Overview
- 파일: exact-filename.m4a
- 표시 길이: observed duration
- 크기(bytes): observed integer
- SHA-256: observed lowercase digest
- 검증: 단일 원문, 전체 디코딩 성공, 비공개 Notebook URL 제외
```

- [ ] **Step 4: Verify full audio decoding**

```powershell
ffprobe -v error -show_entries format=duration,format_name,size -of json "output\audio\Golgeci-2025-Korean-deep-dive.m4a"
ffmpeg -v error -i "output\audio\Golgeci-2025-Korean-deep-dive.m4a" -f null NUL
```

Repeat for all three; require positive duration and exit code 0.

- [ ] **Step 5: Commit the public run records**

```powershell
git add site/downloads/golgeci-2025/notebooklm-run.md site/downloads/battilana-casciaro-2012/notebooklm-run.md site/downloads/battilana-casciaro-2013/notebooklm-run.md
git commit -m "docs: record three NotebookLM paper runs"
```

---

### Task 5: Create three seminar media packages

**Files:**
- Create in research workspace: three `output/slides/*-seminar-deck.pptx` files.
- Create in research workspace: three matching `output/pdf/*-seminar-deck.pdf` files.
- Create in research workspace: three `output/infographics/*-infographic.png` files.
- Create: matching `site/downloads/<slug>/infographic.png` files.

**Interfaces:**
- Consumes: paper PDF, analysis card, NotebookLM record, and audio metadata.
- Produces: per paper an editable 12-slide deck, matching PDF, and 1600×2400 infographic.

- [ ] **Step 1: Fix the deck content map**

Use 12 slides: title/citation; doctoral relevance; problem/question; theory; constructs; model; propositions/hypotheses; method/evidence; results; strengths/limitations; leader/champion application; discussion/references. Label claims `원문 사실`, `저자 해석`, or `박사논문 확장`.

- [ ] **Step 2: Generate editable PPTX files**

Use the presentation design system and native editable elements: 16:9, minimum 18 pt body text, at most two font families, no paragraph-dense slides, and a `[Sources]` speaker-note block with exact source pages on every slide.

- [ ] **Step 3: Render and structurally inspect each deck**

```powershell
python "C:\Users\kimhy\.codex\plugins\cache\openai-primary-runtime\presentations\26.805.11740\skills\presentations\container_tools\render_slides.py" "output\slides\Golgeci-2025-seminar-deck.pptx"
python "C:\Users\kimhy\.codex\plugins\cache\openai-primary-runtime\presentations\26.805.11740\skills\presentations\container_tools\slides_test.py" "output\slides\Golgeci-2025-seminar-deck.pptx"
```

Repeat for all decks; inspect montage and full-resolution slides for overlap, cutoff, unreadable citations, inconsistent labels, and missing notes.

- [ ] **Step 4: Export and compare slide PDFs**

Export each PPTX to PDF, compare `pdfinfo` page count to PPTX slide count, render all PDF pages with `pdftoppm`, and confirm they match the approved deck.

- [ ] **Step 5: Generate and assemble infographics**

Use ImageGen for a clean conceptual background without embedded Korean text. Overlay deterministic typography with citation, research question, core model, 3–5 findings, official-leader implication, informal-champion implication, limitation, and doctoral-study connection.

- [ ] **Step 6: Inspect at original resolution and commit**

Verify every number, author/year, construct label, and Korean phrase against the source. Correct text in the overlay, copy the three approved PNGs to the site, then run:

```powershell
git add site/downloads/golgeci-2025/infographic.png site/downloads/battilana-casciaro-2012/infographic.png site/downloads/battilana-casciaro-2013/infographic.png
git commit -m "feat: add three paper infographics"
```

---

### Task 6: Encrypt four files and integrate 49 catalog slots

**Files:**
- Create: `site/protected/bc2012-source.enc`, `bc2012-korean-full.enc`, `bc2013-source.enc`, `bc2013-korean-full.enc`.
- Modify: `site/data/catalog.json`, `site/assets/app.js`, `site/assets/styles.css`, `site/index.html`.
- Modify: `.github/workflows/pages.yml`, `README.md`.

**Interfaces:**
- Consumes: verified Task 3–5 artifacts and four restricted plaintext PDFs.
- Produces: four ciphertext containers, 49 complete catalog entries, access/rights badges, and a 15-file v2 Release staging set.

- [ ] **Step 1: Encrypt using only the process environment**

```powershell
$secret = Read-Host "비공개 자료 암호" -AsSecureString
$secretPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
  $env:PAPER_PRIVATE_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPtr)
node tools/protected_crypto.mjs encrypt --input "C:\Users\kimhy\OneDrive\문서\ChatGPT\논문작성\output\pdf\Battilana-Casciaro-2012-Change-agents-networks-institutions.pdf" --output "site\protected\bc2012-source.enc"
node tools/protected_crypto.mjs encrypt --input "C:\Users\kimhy\OneDrive\문서\ChatGPT\논문작성\output\private-translations\Battilana-Casciaro-2012-Korean-full-translation-private.pdf" --output "site\protected\bc2012-korean-full.enc"
node tools/protected_crypto.mjs encrypt --input "C:\Users\kimhy\OneDrive\문서\ChatGPT\논문작성\output\pdf\Battilana-Casciaro-2013-Strong-ties-affective-cooptation.pdf" --output "site\protected\bc2013-source.enc"
node tools/protected_crypto.mjs encrypt --input "C:\Users\kimhy\OneDrive\문서\ChatGPT\논문작성\output\private-translations\Battilana-Casciaro-2013-Korean-full-translation-private.pdf" --output "site\protected\bc2013-korean-full.enc"
  git grep -n -F -- "$env:PAPER_PRIVATE_PASSWORD"
  if ($LASTEXITCODE -eq 0) { throw "비밀번호가 Git 추적 파일에 포함되었습니다." }
} finally {
  Remove-Item Env:PAPER_PRIVATE_PASSWORD -ErrorAction SilentlyContinue
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPtr)
}
```

The real value is entered interactively and never pasted into a script or tracked command file.

- [ ] **Step 2: Verify encrypted inventory and leakage**

```powershell
Get-ChildItem site\protected\*.enc | Select-Object Name,Length
rg -a -n '%PDF-|Battilana|Casciaro' site\protected
node --test tests/protected_crypto.test.mjs
```

Expected: exactly four nonempty files, no raw scan match, tests PASS. Run CLI verification with the session-only password and require plaintext/decrypted SHA-256 equality.

- [ ] **Step 3: Stage the 15 public Release assets locally**

Place three CC BY sources, three public translations, three audios, three PPTX files, and three slide PDFs in untracked `output/release-assets/` using exact catalog filenames for `artifacts-2026-08-11-v2`.

- [ ] **Step 4: Rewrite catalog metadata from observed files**

Compute every `size_bytes` and lowercase SHA-256. Add paper-level `rights`, artifact `access`/`translation_kind`, official URLs for restricted sources, protected metadata for four companions, and v2 Release URLs. Do not use invented values.

- [ ] **Step 5: Render badges and separate actions**

```javascript
const protectedAction = artifact.protected
  ? `<a href="protected-viewer.html?id=${encodeURIComponent(artifact.id)}">암호 입력 후 열기</a>`
  : "";
const rightsBadge = `<span class="rights-badge">${escapeHtml(artifact.rights_label)}</span>`;
```

Show official/public and locked actions separately, escape all catalog fields, and explain that the four-digit lock is not strong authentication.

- [ ] **Step 6: Strengthen CI and run local gates**

```yaml
- run: python -m unittest discover -s tests -v
- run: node --test tests/protected_crypto.test.mjs
- run: python tools/validate_catalog.py site/data/catalog.json site
```

```powershell
python -m unittest discover -s tests -v
node --test tests/protected_crypto.test.mjs
python tools/validate_catalog.py site/data/catalog.json site
rg -n '"status"\s*:\s*"missing"|notebook\.google\.com/notebook/' site
git ls-files | rg 'private-translations|output/pdf/Battilana|\.pptx$|\.m4a$'
git diff --check
```

Expected: tests PASS, validator reports `6 papers, 49 artifacts`, and scans reveal no missing status, private URL, or restricted plaintext.

- [ ] **Step 7: Commit the integrated slice**

```powershell
git add site .github/workflows/pages.yml README.md
git commit -m "feat: complete rights-aware paper artifact library"
```

---

### Task 7: Publish the v2 Release and perform local browser QA

**Files:**
- Modify catalog only if actual published asset metadata differs.
- Create local-only QA screenshots under `output/playwright/`.

**Interfaces:**
- Consumes: `output/release-assets/*` and final site.
- Produces: GitHub Release `artifacts-2026-08-11-v2` and a browser-tested local site.

- [ ] **Step 1: Reconcile the 15-file manifest**

```powershell
Get-ChildItem output\release-assets -File | ForEach-Object {
  [pscustomobject]@{Name=$_.Name; Size=$_.Length; SHA256=(Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLowerInvariant()}
} | Sort-Object Name | Format-Table -AutoSize
```

Require 3 sources, 3 translations, 3 audios, 3 PPTX, and 3 slide PDFs matching the catalog.

- [ ] **Step 2: Create and verify the Release**

```powershell
gh release create artifacts-2026-08-11-v2 output\release-assets\* --repo Beaten-to-it/paper --title "Paper Lab artifacts 2026-08-11 v2" --notes "Rights-cleared sources, Korean study materials, audio, and seminar media. Restricted plaintext papers are excluded."
gh release view artifacts-2026-08-11-v2 --repo Beaten-to-it/paper --json assets,url
```

If the tag exists, inspect it first and upload only missing/replaced assets; do not delete an existing Release without separate approval. Download one PDF, PPTX, and audio asset to a temporary directory and confirm hashes.

- [ ] **Step 3: Run local browser QA**

```powershell
python -m http.server 8765 --directory site
```

In the in-app browser, check desktop and 390 px mobile views, search/filter, all nine slots, public links, image previews, audio, Markdown viewer, correct/wrong password behavior, tamper rejection, and relock after refresh.

- [ ] **Step 4: Commit evidence-driven corrections**

```powershell
git add site tools tests .github README.md
git commit -m "fix: resolve artifact library QA findings"
```

Skip the commit if no tracked correction was needed. Never commit QA screenshots showing the restricted PDF body or password.

---

### Task 8: Adversarial review, merge, deploy, and live verification

**Files:**
- Create: `docs/reviews/2026-08-11-complete-paper-artifacts-review.md`.
- Modify implementation only for independently reproduced Critical/High findings.

**Interfaces:**
- Consumes: exact latest tree and clean status.
- Produces: valid Claude Opus 5 gate, merged `main`, successful Pages deployment, and verified live site.

- [ ] **Step 1: Freeze the review target**

```powershell
git status --short
git rev-parse HEAD
git rev-parse HEAD^{tree}
```

Scope accidental operator errors, corrupt/malicious catalog or containers, path traversal, plaintext leakage, stale metadata, and wrong-password/tamper behavior under the approved threat model.

- [ ] **Step 2: Run one full Windows Claude review**

```powershell
claude -p --model claude-opus-5 --effort xhigh "Review the exact current tree for the approved paper-artifact design. Report reproducible findings with severity, entry point, steps, observed impact, and disposition criteria. Completion gate: Critical=0 and High=0. Do not edit files."
```

Verify response metadata resolves to `claude-opus-5`; otherwise record the round invalid and stop.

- [ ] **Step 3: Reproduce and close Critical/High findings**

Record each item as accepted, rejected, deferred, or fixed with evidence. Fix only accepted Critical/High items and add regression tests. If needed, run at most two targeted closure reviews against only the fix diff, affected interfaces, and tests. Stop when a valid latest review has `Critical = 0`, `High = 0`; after two unresolved targeted reviews, mark `설계 재검토 필요` and ask the user.

- [ ] **Step 4: Run full pre-publish verification**

```powershell
python -m unittest discover -s tests -v
node --test tests/protected_crypto.test.mjs
python tools/validate_catalog.py site/data/catalog.json site
git diff --check
git status --short
```

- [ ] **Step 5: Push, open PR, and merge after green checks**

```powershell
git push -u origin codex/complete-paper-artifacts
gh pr create --repo Beaten-to-it/paper --base main --head codex/complete-paper-artifacts --title "Complete rights-aware paper artifact library" --body "Completes 49 artifact slots, adds encrypted access to exactly four restricted PDFs, and publishes verified paper media."
gh pr merge --repo Beaten-to-it/paper --merge --delete-branch
```

Do not bypass a failing required check.

- [ ] **Step 6: Verify Pages and live behavior**

```powershell
gh run list --repo Beaten-to-it/paper --workflow "Deploy GitHub Pages" --limit 3
gh api repos/Beaten-to-it/paper/pages
```

Open `https://beaten-to-it.github.io/paper/`; confirm 49 complete slots; test one public artifact of each type; test all four locked items with the session-only password, one wrong password, and refresh relock; confirm no plaintext restricted or private NotebookLM URL is reachable.

- [ ] **Step 7: Report the verified handoff**

Report Release and Pages URLs, merged commit, exact counts, public/restricted boundary, local plaintext locations, test/review results, and the remaining offline brute-force risk of a four-digit client-side password. Never repeat the password.
