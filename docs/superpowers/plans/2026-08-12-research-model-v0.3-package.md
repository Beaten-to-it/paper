# Research Model v0.3 Paper Lab Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the approved research model v0.3 into a fieldwork-ready, cross-paper analysis package and publish all public artifacts through Paper Lab.

**Architecture:** Keep `site/data/catalog.json` as the public source of truth and advance it to version 3. Add the same v0.3 contribution-analysis slot to all five paper groups, then add a focused research-design package containing four mobile-readable Markdown artifacts, one model diagram, one workbook, one editable deck, and one matching PDF. Resolve all pre-fieldwork methodological and ethics findings before producing the pilot protocol; keep binaries in a new GitHub Release and public text/image artifacts in GitHub Pages.

**Tech Stack:** Python 3.13 and `unittest`, Node.js 24, static HTML/CSS/JavaScript, bundled spreadsheet/presentation/PDF runtimes, GitHub CLI/Releases/Pages, Playwright CLI.

## Global Constraints

- Official working title: `SW 개발조직의 AI 전환에서 공식 리더-비공식 AI 챔피언 네트워크의 역할 보완성: 구성원 우려의 표면화와 책임 있는 AI 채택 프레임워크 개발 및 검증`.
- Central path: `역할 보완성 × 네트워크 연결성 → 발언 안전성 + 발언 효능감 → 건설적 표면화 또는 은폐·이탈 → 정책-실무 정합성 + 책임 있는 AI 채택`.
- The moderator is event-level change divergence; P1-P7 remain unverified propositions until qualitative and measurement studies support conversion to hypotheses.
- Separate direct paper evidence, cross-theory synthesis, and propositions for later empirical testing in every artifact.
- Treat NotebookLM products as learning aids, never academic evidence.
- Do not start interviews, recruitment, name generation, or organizational data collection until the ethics, insider-researcher, level-of-analysis, measurement, and burden gates in Task 1 pass.
- Keep restricted source PDFs and translations exactly as currently protected; do not touch passwords, ciphertext, rights metadata, or private NotebookLM URLs.
- Catalog version 3 contains exactly six groups and 62 complete artifacts: five papers with ten slots each and one research-design group with twelve artifacts.
- Add `model_contribution` once to every paper; do not add a new analysis type to only selected papers.
- Store public Markdown and PNG files on Pages. Store the v0.3 XLSX, PPTX, and slide PDF in Release `artifacts-2026-08-12-v3`.
- Public text files use UTF-8 with LF endings. Every cataloged file has an observed byte size and lowercase SHA-256.
- The final latest-tree adversarial review must resolve to `claude-opus-5` with `xhigh` effort and report `Critical = 0`, `High = 0`.

## File Map

- Modify `docs/superpowers/specs/2026-08-12-research-model-v0.3-design.md`: close fieldwork-level construct and ethics gaps.
- Modify `site/downloads/research-design/core-paper-matrix-research-model-interview-guide.md`: bound the interview and name generator.
- Modify `docs/reviews/2026-08-12-research-model-v0.3-review.md`: record finding dispositions and validation evidence.
- Create `tests/test_research_model_v03.py`: enforce research-design, fieldwork, and content contracts.
- Create one `model-v0.3-contribution.md` under each of the five existing paper download directories.
- Create four public research-design Markdown files: model overview, construct dictionary, proposition traceability, and pilot protocol/codebook.
- Create `tools/build_research_model_v03_workbook.py` and `tools/build_research_model_v03_media.py`.
- Create `tests/test_research_model_v03_assets.py`.
- Create locally under ignored `output/release-assets/`: v0.3 XLSX, PPTX, and PDF.
- Create `site/downloads/research-design/research-model-v0.3.png` at 2400×1600.
- Modify `tests/test_validate_catalog.py`, `tests/test_site_contract.py`, `tools/validate_catalog.py`, `site/data/catalog.json`, `site/assets/app.js`, and `README.md` for version 3.

---

### Task 1: Close the pre-fieldwork research-design gates

**Files:**
- Create: `tests/test_research_model_v03.py`
- Modify: `docs/superpowers/specs/2026-08-12-research-model-v0.3-design.md`
- Modify: `site/downloads/research-design/core-paper-matrix-research-model-interview-guide.md`
- Modify: `docs/reviews/2026-08-12-research-model-v0.3-review.md`

**Interfaces:**
- Consumes: accepted v0.3 constructs, the independent review ledger, and the current 50-70 minute interview guide.
- Produces: an explicit level map, non-overlapping process codes, participant/alter protections, insider controls, a measurable moderator, and a feasible 60-minute pilot.

- [ ] **Step 1: Write the failing document-contract tests**

```python
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = (ROOT / "docs/superpowers/specs/2026-08-12-research-model-v0.3-design.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "site/downloads/research-design/core-paper-matrix-research-model-interview-guide.md").read_text(encoding="utf-8")

class ResearchModelV03Tests(unittest.TestCase):
    def test_construct_levels_are_explicit(self):
        for row in (
            "실행된 역할 보완성 | 사건", "활성화된 네트워크 연결성 | 사건",
            "발언 안전성 | 개인×사건", "발언 효능감 | 개인×사건", "변화 발산성 | 사건",
        ):
            self.assertIn(row, SPEC)

    def test_ethics_gate_protects_alters_and_insider_participants(self):
        for phrase in (
            "비응답 지명자", "연결코드 명부", "사건에만 귀속",
            "독립 모집 담당자", "고용주에게 원자료를 제공하지 않는다", "인터뷰와 관계망 조사 전에 IRB",
        ):
            self.assertIn(phrase, SPEC)

    def test_measurement_path_covers_new_constructs(self):
        for phrase in ("변화 발산성 문항", "반응경로 코딩", "내용타당도", "차원성 검토"):
            self.assertIn(phrase, SPEC)

    def test_pilot_network_burden_is_bounded(self):
        for phrase in ("고유 인물 최대 8명", "핵심 인물 최대 5명", "관계망 질문 12분"):
            self.assertIn(phrase, GUIDE)

    def test_path_and_process_outcome_are_not_double_counted(self):
        self.assertIn("검토 착수와 조정 여부는 지배 경로 판정에만 사용", SPEC)
        self.assertIn("실질적 처리 내용과 실제 문제해결 여부", SPEC)
```

- [ ] **Step 2: Run the tests and confirm the expected failures**

```powershell
python -m unittest tests.test_research_model_v03 -v
```

Expected: FAIL because the current spec lacks the level rows, alter/insider safeguards, complete measurement path, bounded roster, and path/outcome separation.

- [ ] **Step 3: Fix construct levels and outcome boundaries**

Add this level contract to §4:

```markdown
실행된 역할 보완성 | 사건
활성화된 네트워크 연결성 | 사건
발언 안전성 | 개인×사건
발언 효능감 | 개인×사건
구성원 반응 | 개인×사건; 사건 지배 경로는 파생값
변화 발산성 | 사건
기초 네트워크 구조 | 팀 맥락; P1의 주 예측변수와 분리
```

Define event scores from enacted role division and ties activated for the focal incident. Keep static team centrality, brokerage, and cohesion as contextual descriptors until Study 1 supports a team-level hypothesis. State that review initiation and adjustment determine the dominant path only, while substantive handling content and actual problem resolution are downstream outcomes; never include both as independent terms in the same P5 test.

- [ ] **Step 4: Add the ethics and insider-researcher gate**

Add these enforceable rules to §13 and §16:

```markdown
- 인터뷰와 관계망 조사 전에 IRB와 기업 보안·법무 승인을 완료한다.
- 비응답 지명자는 역할 범주로만 분석하며 규정위반 행동은 개인 코드가 아니라 사건에만 귀속한다.
- 연결코드 명부는 전사·코딩자료와 분리 암호화하고 연구책임자만 접근하며 분석 종료 시 폐기한다.
- 재직·협력 관계를 위치성·이해상충 진술에 공개한다.
- 참여자와 지휘·평가 관계가 없는 독립 모집 담당자가 모집과 동의 회수를 수행한다.
- 고용주에게 원자료를 제공하지 않는다. 법률 또는 IRB 승인 안전절차의 공개 한계는 동의서에 사전 명시한다.
```

Add the research consent form, anonymization/linkage-code protocol, positionality/conflict statement, and gatekeeper data-access agreement to §16 deliverables.

- [ ] **Step 5: Bound the name generator and session time**

Use one roster of at most eight unique people. For each alter, tick advice, trust, approval/exception, and risk-escalation relations; collect frequency, perceived trust, and formal-role attributes once. Ask alter-alter ties only among the five most central focal-incident alters, at most ten undirected pairs.

```text
동의·안전 5분 | 역할·AI 경험 5분 | 사건 타임라인 10분 | 결정적 사건 15분
관계망 질문 12분 | 역할별 질문 8분 | 정책 적합성·종료 5분
```

- [ ] **Step 6: Extend Study 2 measurement development**

Add change-divergence items and response-path coding to §11.3. Require content-validity review, cognitive interviews, dimensionality assessment, and an explicit reflective/formative/index decision before the moderation test. Map P6/P7 terms—brokerage, cohesion, tie strength, recipient stance, relational pressure, and champion exhaustion—to §6 constructs or exploratory outcomes.

- [ ] **Step 7: Run tests, record dispositions, and commit**

```powershell
python -m unittest tests.test_research_model_v03 -v
git diff --check
git add tests/test_research_model_v03.py docs/superpowers/specs/2026-08-12-research-model-v0.3-design.md site/downloads/research-design/core-paper-matrix-research-model-interview-guide.md docs/reviews/2026-08-12-research-model-v0.3-review.md
git commit -m "docs: harden v0.3 fieldwork design"
```

---

### Task 2: Add the same v0.3 contribution analysis to all five papers

**Files:**
- Create: `site/downloads/kemell-2025/model-v0.3-contribution.md`
- Create: `site/downloads/neumann-2026/model-v0.3-contribution.md`
- Create: `site/downloads/golgeci-2025/model-v0.3-contribution.md`
- Create: `site/downloads/battilana-casciaro-2012/model-v0.3-contribution.md`
- Create: `site/downloads/battilana-casciaro-2013/model-v0.3-contribution.md`
- Modify: `tests/test_research_model_v03.py`

**Interfaces:**
- Consumes: each paper's existing `analysis.md` and the approved v0.3 model.
- Produces: five comparable cards using identical headings and evidence labels.

- [ ] **Step 1: Add the failing five-card contract**

```python
def test_every_paper_has_one_v03_contribution_card(self):
    slugs = ["kemell-2025", "neumann-2026", "golgeci-2025", "battilana-casciaro-2012", "battilana-casciaro-2013"]
    required = ["## 직접 근거", "## v0.3에서의 역할", "## 연결되는 명제", "## 검증하지 않은 것", "## 현장자료 요구"]
    for slug in slugs:
        path = ROOT / "site/downloads" / slug / "model-v0.3-contribution.md"
        self.assertTrue(path.is_file(), slug)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(all(heading in text for heading in required), slug)
        self.assertIn("후속 연구 명제", text)
```

- [ ] **Step 2: Confirm the files are missing**

```powershell
python -m unittest tests.test_research_model_v03.ResearchModelV03Tests.test_every_paper_has_one_v03_contribution_card -v
```

- [ ] **Step 3: Write the five cards with fixed theoretical roles**

```text
Kemell 2025: official/informal adoption coexistence; phenomenon anchor; no direct network or resistance-effect test.
Neumann 2026: policy-practice gap and Shadow IT signal; informs P4-P5 context; no leader-champion network measurement.
Golgeci 2025: conceptual AI-resistance and alleviation mechanisms; informs P1-P5; not an empirical scale validation.
Battilana & Casciaro 2012: divergence-conditioned network structure; informs P6; do not generalize healthcare results directly.
Battilana & Casciaro 2013: recipient stance and tie-strength boundary; cautiously informs P7; do not overstate the marginal resistor result.
```

Each card must distinguish `논문 직접 근거`, `통합 해석`, and `후속 연구 명제`, then name the interview/network evidence required to test the extension.

- [ ] **Step 4: Run tests and commit**

```powershell
python -m unittest tests.test_research_model_v03 -v
git diff --check
git add tests/test_research_model_v03.py site/downloads/*/model-v0.3-contribution.md
git commit -m "docs: add v0.3 contribution cards"
```

---

### Task 3: Build the mobile-readable research-design package

**Files:**
- Create: `site/downloads/research-design/research-model-v0.3.md`
- Create: `site/downloads/research-design/construct-dictionary-v0.3.md`
- Create: `site/downloads/research-design/proposition-traceability-v0.3.md`
- Create: `site/downloads/research-design/pilot-protocol-and-codingbook-v0.3.md`
- Modify: `tests/test_research_model_v03.py`

**Interfaces:**
- Consumes: the corrected spec and five contribution cards.
- Produces: four standalone public documents that remain readable on a mobile screen and trace every claim to its evidence status.

- [ ] **Step 1: Add failing content and cross-link tests**

```python
def test_public_v03_package_is_complete_and_cross_linked(self):
    files = {
        "research-model-v0.3.md": ["## 한 문장 모형", "## 인과경로", "## 사건 과정", "## 검증 순서"],
        "construct-dictionary-v0.3.md": ["역할 보완성", "네트워크 연결성", "포함 기준", "제외 기준", "분석 수준"],
        "proposition-traceability-v0.3.md": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "반증 사례"],
        "pilot-protocol-and-codingbook-v0.3.md": ["60분", "고유 인물 최대 8명", "사건 코드", "부정 사례", "IRB"],
    }
    base = ROOT / "site/downloads/research-design"
    for name, phrases in files.items():
        text = (base / name).read_text(encoding="utf-8")
        self.assertTrue(all(phrase in text for phrase in phrases), name)
        self.assertIn("검증 전", text)
```

- [ ] **Step 2: Confirm the four-file test fails**

```powershell
python -m unittest tests.test_research_model_v03.ResearchModelV03Tests.test_public_v03_package_is_complete_and_cross_linked -v
```

- [ ] **Step 3: Write the model overview and construct dictionary**

Keep paragraphs under six lines and tables under six columns for mobile reading. The overview explains the central path, two response routes, event-process sequence, P1-P7 status, and three-study validation sequence. The dictionary gives each construct's level, definition, inclusion/exclusion criteria, observable evidence, temporal position, nearest competing construct, and attribution rule.

- [ ] **Step 4: Write proposition traceability and pilot protocol/codebook**

For every proposition record the direct source contribution, synthesis step, level, data source, supporting pattern, falsifying pattern, rival explanation, and Study 2 disposition. The pilot protocol contains the exact 60-minute agenda, one-roster name generator, event codes, path-versus-outcome rule, negative-case log, consent/withdrawal flow, linkage-code handling, insider safeguards, and stop conditions.

- [ ] **Step 5: Verify mobile structure, evidence labels, and commit**

```powershell
python -m unittest tests.test_research_model_v03 -v
rg -n "검증됐다|입증됐다" site/downloads/research-design/*v0.3.md site/downloads/*/model-v0.3-contribution.md
git diff --check
git add tests/test_research_model_v03.py site/downloads/research-design/*v0.3.md
git commit -m "docs: add v0.3 research package"
```

Review every search match and retain it only when it describes a source paper's direct evidence rather than P1-P7.

---

### Task 4: Generate and verify the v0.3 analysis workbook

**Files:**
- Create: `tools/build_research_model_v03_workbook.py`
- Create: `tests/test_research_model_v03_assets.py`
- Create locally: `output/release-assets/SW-AI-change-agent-research-model-v0.3-workbook.xlsx`

**Interfaces:**
- Consumes: the four public v0.3 Markdown documents and five contribution cards.
- Produces: `build_workbook(output_path: Path) -> None` and one deterministic XLSX with sheets `README`, `구성개념`, `명제추적`, `논문별기여`, `사건코딩`, `관계망`, `부정사례`, and `윤리체크`.

- [ ] **Step 1: Load bundled dependencies and write a failing workbook test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from openpyxl import load_workbook
from tools.build_research_model_v03_workbook import build_workbook

def test_v03_workbook_structure(self):
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "workbook.xlsx"
        build_workbook(path)
        wb = load_workbook(path, read_only=False, data_only=False)
        self.assertEqual(wb.sheetnames, ["README", "구성개념", "명제추적", "논문별기여", "사건코딩", "관계망", "부정사례", "윤리체크"])
        self.assertEqual(wb["명제추적"].max_row, 8)
        self.assertEqual(wb["논문별기여"].max_row, 6)
        self.assertTrue(wb["구성개념"].freeze_panes)
        self.assertTrue(wb["사건코딩"].auto_filter.ref)
```

- [ ] **Step 2: Confirm the workbook is absent**

```powershell
python -m unittest tests.test_research_model_v03_assets.ResearchModelV03AssetTests.test_v03_workbook_structure -v
```

- [ ] **Step 3: Implement the deterministic workbook builder**

Use `openpyxl`. Parse the approved Markdown artifacts or define each source row once inside the builder; do not maintain duplicate research-content blocks. Apply a Korean-capable font, dark-blue headers, alternating rows, wrapped text, filters, frozen headers, validation lists for evidence status/disposition, and hyperlinks to matching Paper Lab Markdown.

Use one row per respondent-alter pair in `관계망` with four Boolean relation columns and no real-name column. Use these `사건코딩` columns:

```text
event_code, actor_role, trigger, threat, role_complementarity,
activated_connectivity, voice_safety, voice_efficacy, response_codes,
dominant_path, substantive_handling, problem_resolution,
rival_explanation, negative_case
```

- [ ] **Step 4: Generate and verify the workbook**

```powershell
python tools/build_research_model_v03_workbook.py --output output/release-assets/SW-AI-change-agent-research-model-v0.3-workbook.xlsx
python -m unittest tests.test_research_model_v03_assets -v
```

Use the spreadsheet skill's render-and-inspect workflow on all eight sheets. Reject clipped Korean text, broken wrapping, unusable widths, invalid filters, and spreadsheet error values.

- [ ] **Step 5: Commit builder and tests**

```powershell
git add tools/build_research_model_v03_workbook.py tests/test_research_model_v03_assets.py
git commit -m "feat: build v0.3 analysis workbook"
```

The generated XLSX stays in the ignored release staging directory until Task 6.

---

### Task 5: Generate the model diagram and advisor seminar deck

**Files:**
- Create: `tools/build_research_model_v03_media.py`
- Create: `site/downloads/research-design/research-model-v0.3.png`
- Create locally: `output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx`
- Create locally: `output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pdf`
- Modify: `tests/test_research_model_v03_assets.py`

**Interfaces:**
- Consumes: v0.3 overview, dictionary, proposition map, and review ledger.
- Produces: `build_media(diagram_path: Path, deck_path: Path) -> None`, one 2400×1600 PNG, one editable 12-slide PPTX, and one matching 12-page PDF.

- [ ] **Step 1: Add failing image and deck tests**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
from pptx import Presentation
from tools.build_research_model_v03_media import build_media

def test_v03_visual_package(self):
    with TemporaryDirectory() as tmp:
        diagram = Path(tmp) / "model.png"
        deck_path = Path(tmp) / "deck.pptx"
        build_media(diagram, deck_path)
        self.assertEqual(Image.open(diagram).size, (2400, 1600))
        deck = Presentation(deck_path)
        self.assertEqual(len(deck.slides), 12)
        text = "\n".join(shape.text for slide in deck.slides for shape in slide.shapes if hasattr(shape, "text"))
        for phrase in ("역할 보완성", "네트워크 연결성", "발언 안전성", "발언 효능감", "변화 발산성", "검증 전 명제"):
            self.assertIn(phrase, text)
```

- [ ] **Step 2: Confirm the visual package is absent**

```powershell
python -m unittest tests.test_research_model_v03_assets.ResearchModelV03AssetTests.test_v03_visual_package -v
```

- [ ] **Step 3: Implement deterministic PNG/PPTX generation**

Use Pillow for the diagram and `python-pptx` for the editable deck. Use a bundled Korean font, color the predictor blue, dual mediators amber, constructive route green, concealment route red, distal outcomes teal, and moderator violet. Do not use AI-generated embedded text.

```text
1 title and one-sentence model
2 empirical phenomenon and research gap
3 five-paper evidence architecture
4 focal event and multilevel units
5 role complementarity
6 four multiplex network relations
7 dual voice mediators
8 response-path coding
9 change-divergence boundary condition
10 P1-P7 and rival explanations
11 exploratory sequential mixed-method design
12 ethics gates, review status, and next decision
```

Every slide contains a `[Sources]` notes block. Label source findings, synthesis, and unverified propositions distinctly.

- [ ] **Step 4: Render and inspect the PPTX**

```powershell
python tools/build_research_model_v03_media.py --diagram site/downloads/research-design/research-model-v0.3.png --deck output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx
python "C:\Users\kimhy\.codex\plugins\cache\openai-primary-runtime\presentations\26.805.11740\skills\presentations\container_tools\render_slides.py" output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx
python "C:\Users\kimhy\.codex\plugins\cache\openai-primary-runtime\presentations\26.805.11740\skills\presentations\container_tools\slides_test.py" output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx
```

First confirm the bundled path with the workspace dependency loader. Inspect the montage and all full-resolution slides for overlap, cutoff, font substitution, label ambiguity, and unreadable sources.

- [ ] **Step 5: Export and compare the PDF**

Export and render with explicit commands:

```powershell
$soffice = (Get-Command soffice -ErrorAction Stop).Source
& $soffice --headless --convert-to pdf --outdir output/release-assets output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx
if ((pdfinfo output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pdf | Select-String '^Pages:\s+12$').Count -ne 1) { throw "Expected a 12-page slide PDF." }
New-Item -ItemType Directory -Force output/rendered/research-model-v03 | Out-Null
pdftoppm -png -r 144 output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pdf output/rendered/research-model-v03/page
```

Use the PDF skill to inspect all 12 rendered pages. Reject a blank page, clipping, or a visual mismatch with the PPTX render.

- [ ] **Step 6: Run tests and commit tracked sources**

```powershell
python -m unittest tests.test_research_model_v03_assets -v
git diff --check
git add tools/build_research_model_v03_media.py tests/test_research_model_v03_assets.py site/downloads/research-design/research-model-v0.3.png
git commit -m "feat: add v0.3 model media"
```

---

### Task 6: Publish version 3 assets and enforce the 62-artifact catalog

**Files:**
- Modify: `tests/test_validate_catalog.py`
- Modify: `tests/test_site_contract.py`
- Modify: `tools/validate_catalog.py`
- Modify: `site/data/catalog.json`
- Modify: `site/assets/app.js`
- Modify: `README.md`

**Interfaces:**
- Consumes: five contribution cards, four design Markdown files, PNG, staged XLSX/PPTX/PDF, and live Release metadata.
- Produces: catalog version 3 with 62 exact bindings and UI labels/previews for all new types.

- [ ] **Step 1: Add failing version-3 catalog tests**

```python
def test_v3_catalog_has_five_ten_slot_papers_and_twelve_design_artifacts(self):
    catalog = json.loads((SITE_ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    papers = [p for p in catalog["papers"] if p["kind"] == "paper"]
    design = next(p for p in catalog["papers"] if p["kind"] == "research-design")
    self.assertEqual(catalog["version"], 3)
    self.assertTrue(all(len(p["artifacts"]) == 10 for p in papers))
    self.assertTrue(all(sum(a["type"] == "model_contribution" for a in p["artifacts"]) == 1 for p in papers))
    self.assertEqual(len(design["artifacts"]), 12)
    self.assertEqual(sum(len(p["artifacts"]) for p in catalog["papers"]), 62)
```

Add negative tests for a missing paper contribution card, a swapped card between papers, a missing research artifact, catalog downgrade to version 2, and a v3 Release URL with the wrong size or SHA-256.

- [ ] **Step 2: Confirm failure on version 2**

```powershell
python -m unittest tests.test_validate_catalog tests.test_site_contract -v
```

- [ ] **Step 3: Create and verify the v3 Release**

```powershell
$branch = git branch --show-current
git push -u origin $branch
if (gh release view artifacts-2026-08-12-v3 --repo Beaten-to-it/paper 2>$null) { throw "Release tag artifacts-2026-08-12-v3 already exists; inspect it before continuing." }
gh release create artifacts-2026-08-12-v3 `
  output/release-assets/SW-AI-change-agent-research-model-v0.3-workbook.xlsx `
  output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx `
  output/release-assets/SW-AI-change-agent-research-model-v0.3-advisor-deck.pdf `
  --repo Beaten-to-it/paper `
  --target codex/complete-paper-artifacts-impl `
  --title "Paper Lab research model v0.3 artifacts" `
  --notes "Research model v0.3 workbook and advisor seminar package."
```

Push the current branch before creating the Release so the target commit exists remotely. Fail closed if `gh release view artifacts-2026-08-12-v3` already succeeds; inspect the existing tag instead of overwriting it. Read the published asset list with `gh release view artifacts-2026-08-12-v3 --json assets,url`. Compare each live byte size and downloaded SHA-256 with the local staged file before cataloging it.

- [ ] **Step 4: Implement the version-3 validator contract**

Set `PAPER_SLOT_TYPES` to the current nine types plus `model_contribution`. Allow `.md` for `model_contribution`, `research_model`, `construct_dictionary`, `proposition_traceability`, and `pilot_protocol`; allow `.png` for `model_diagram`. Add `RELEASE_V3`, update the research-design identity date, bind all five card paths, bind eight new research-design artifacts, require 62 unique IDs, and reject any canonical catalog version other than 3.

```text
research-model-v03 → research_model → pages → downloads/research-design/research-model-v0.3.md
construct-dictionary-v03 → construct_dictionary → pages → downloads/research-design/construct-dictionary-v0.3.md
proposition-traceability-v03 → proposition_traceability → pages → downloads/research-design/proposition-traceability-v0.3.md
pilot-protocol-v03 → pilot_protocol → pages → downloads/research-design/pilot-protocol-and-codingbook-v0.3.md
research-model-v03-diagram → model_diagram → pages → downloads/research-design/research-model-v0.3.png
research-model-v03-workbook → spreadsheet → release v3 XLSX
research-model-v03-slides → slides → release v3 PPTX
research-model-v03-slide-pdf → slide_pdf → release v3 PDF
```

- [ ] **Step 5: Update catalog and UI**

Add observed size/hash metadata. Add Korean labels for `model_contribution`, `research_model`, `construct_dictionary`, `proposition_traceability`, `pilot_protocol`, and `model_diagram` in `app.js`. Render `model_diagram` with the same safe preview behavior as infographics. Update README counts to six groups and 62 complete artifacts.

- [ ] **Step 6: Run all local tests and commit**

```powershell
python -m unittest discover -s tests -v
$nodeTests = Get-ChildItem tests -Filter "*.test.mjs" | ForEach-Object FullName
node --test $nodeTests
python tools/validate_catalog.py site/data/catalog.json site
git diff --check
git add tools/validate_catalog.py tests/test_validate_catalog.py tests/test_site_contract.py site/data/catalog.json site/assets/app.js README.md
git commit -m "feat: publish research model v0.3 catalog"
```

Expected validator output: `valid catalog: 6 papers, 62 artifacts`.

---

### Task 7: Run final integrity, adversarial, deployment, and mobile QA gates

**Files:**
- Create: `docs/reviews/2026-08-12-research-model-v0.3-package-review.md`
- Modify only when a reproduced Critical/High requires correction: files named by that finding.

**Interfaces:**
- Consumes: the complete version-3 tree and live v3 Release.
- Produces: a reviewed commit, merged pull request, successful Pages deployment, and live desktop/mobile evidence.

- [ ] **Step 1: Run the complete deterministic gate**

```powershell
python -m unittest discover -s tests -v
$nodeTests = Get-ChildItem tests -Filter "*.test.mjs" | ForEach-Object FullName
node --test $nodeTests
python tools/validate_catalog.py site/data/catalog.json site
git ls-files | rg "(^|/)(output|tmp)/|private-translations|\.pdf$|\.pptx$|\.xlsx$"
rg -n --hidden --glob '!.git/**' "notebook\.google\.com/notebook/|PAPER_PRIVATE_PASSWORD\s*=|C:\\Users\\kimhy" site
```

The tracked-binary scan may list only deliberately tracked public PNG/encrypted containers; it must not list staged XLSX/PPTX/PDF or restricted plaintext. The URL/path/secret scan must return zero matches.

- [ ] **Step 2: Run the latest-tree Claude Opus 5 review**

Fix exact commit and tree hashes in the request. Require read-only inspection of the version-3 contract, all new research artifacts, five contribution cards, generated-asset provenance, Release metadata, rights boundaries, data-protection design, and test coverage. Validate `modelUsage` resolves to `claude-opus-5`. Apply the repository severity contract; independently reproduce every finding; fix accepted Critical/High only; stop when the valid latest review reports `Critical = 0`, `High = 0`.

- [ ] **Step 3: Record review evidence and rerun final checks**

Write target hashes, requested/resolved model, findings, dispositions, test counts, Release asset size/hash verification, and remaining Medium/Low fieldwork gates to the review ledger. Commit the ledger, then rerun the Python, Node, and catalog commands against the exact final tree.

- [ ] **Step 4: Push and open a new pull request**

```powershell
$branch = git branch --show-current
git push -u origin $branch
$body = @"
## Summary
- publish the research model v0.3 cross-paper package
- expand Paper Lab to 62 complete artifacts
- add fieldwork ethics and measurement gates

## Verification
- full Python and Node suites
- live Release size and SHA-256 checks
- catalog validator: 6 groups, 62 artifacts
- Claude Opus 5: Critical 0, High 0
"@
gh pr create --base main --head $branch --title "Publish research model v0.3 package" --body $body
```

Add the observed Release link, exact test counts, and known nonblocking backlog to `$body` before running the command. Merge only after GitHub checks pass.

- [ ] **Step 5: Verify GitHub Pages deployment**

```powershell
gh run list --workflow "Deploy GitHub Pages" --branch main --limit 3
$runId = gh run list --workflow "Deploy GitHub Pages" --branch main --limit 3 --json databaseId,conclusion --jq 'map(select(.conclusion=="success"))[0].databaseId'
gh run view $runId --json status,conclusion,url,jobs
```

Require `$runId` to be nonempty and the validate and deploy jobs to complete successfully. Confirm the live catalog returns version 3, six groups, 62 complete artifacts, and exactly four protected companions.

- [ ] **Step 6: Perform live desktop and mobile browser QA**

With Playwright, test 1440×1000 and 390×844 viewports. Verify:

```text
five paper cards each show the v0.3 contribution link
research-design group shows all twelve artifacts
Markdown opens in the internal viewer
the 2400×1600 diagram previews and opens
XLSX, PPTX, and PDF links return HTTP 200 from Release v3
type filtering finds every new artifact type
protected source/translation behavior is unchanged
console errors = 0 and warnings = 0
```

- [ ] **Step 7: Close the delivery record**

Record the merge commit, Pages run URL, live site URL, Release URL, final 62/62 count, test counts, browser evidence, and unfinished conditions. Do not mark fieldwork ready unless every Task 1 ethics and methods condition is present in the published pilot protocol.
