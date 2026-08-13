# 연구모형 v0.3 패키지 최종 검토 원장

## 현재 판정

- 검토 대상 제품 커밋: `b5ae278b005f20fd79a7967057c6a61e2242eeb9`
- 검토 대상 제품 트리: `8d0bb77105503c0adeb8ca8104428778310aa84c`
- 검토 브랜치: `codex/complete-paper-artifacts-impl`
- 전체 패키지 merge base: `b12870a801100e53d2d0a8211f07753c884b0986`
- 유효한 최신 전체 독립 검토: `Critical = 0`, `High = 0`, `Medium = 3`, `Low = 5`, `GATE = PASS`
- 현재 열린 `Critical`: **0**
- 현재 열린 `High`: **0**
- 로컬 상태: **LOCAL_GATE_PASS — 사용자 승인 전 Phase B 대기**
- 이 판정은 push, PR, 병합, 배포 또는 현장조사 개시 승인이 아니다.

## 고정 범위와 위협 모델

전체 검토는 catalog v3와 62개 canonical binding, 공개 연구설계 문서, 논문별 기여 카드 5개와 원 논문 분석, PNG/XLSX/PPTX/PDF 생성·결정성·의미 계약·Release 결합, protected companion 권리 경계와 암호화 뷰어, 데이터 보호 설계, Pages clean-runner workflow와 테스트를 포함했다.

기본·승인 구성에서의 우발적 운영자 실수, 악성·손상 입력, 계획과 적용 사이의 상태 변화, 외부 신뢰 기준을 지배하지 못하는 행위자의 로컬 변조를 위협 모델에 포함했다. 구현 코드, 저장소·Git·로컬 구성, 외부에서 검토된 해시·승인 기록, 최종 커밋·복제를 한 행위자가 동시에 모두 지배해야만 성립하는 시나리오는 제외했다.

`Critical`은 지원 워크플로의 비가역적 영속 데이터 손실, 실제 자격증명의 신뢰 경계 밖 저장·전송, 권한 없는 상태 승격 또는 손상 복제본의 정상 승인을 뜻한다. `High`는 지원 워크플로의 핵심 무결성 gate 우회 또는 조용한 데이터 손실·보안 침해가 재현된 경우다. 실패 폐쇄형 가용성, 비지원 입력, 문서·품질·사용성·provenance·defense-in-depth 문제는 재현 영향이 위 기준을 충족하지 않는 한 `Medium` 이하로 처분했다.

## 최신 Claude 전체 검토

- 요청 모델·effort: `claude-opus-5`, `xhigh`
- 실행 계약: Windows Claude CLI `2.1.211`, safe mode, no Chrome, `dontAsk`, 읽기 전용 `Read`·`Glob`·`Grep`·`Bash`; mutation 도구와 `Agent` 금지
- 세션 ID: `a3d9fca4-bde4-4571-a504-4c856a088c8e`
- 실행시간: `513.9`초
- 요청: `.superpowers/sdd/2026-08-12-research-model-v0.3-package/task-7-latest-claude-request.md`
- 응답·도구 호출 transcript: `C:\Users\kimhy\.claude\projects\C--projects-paper--worktrees-complete-paper-artifacts-impl\a3d9fca4-bde4-4571-a504-4c856a088c8e.jsonl`
- debug·transport: `.superpowers/sdd/2026-08-12-research-model-v0.3-package/task-7-latest-claude-debug.log`
- 모델 검증: transcript assistant turn `101/101`이 `claude-opus-5`; debug first-party dispatch `35/35`가 `claude-opus-5`; wrapper `modelUsage`의 유일한 key도 `claude-opus-5`
- transport 검증: `apiProvider=firstParty`; 다른 resolved model 또는 model fallback 없음. debug의 `Config fallback` 한 줄은 CA certificate 설정 fallback이며 model fallback이 아니다.
- permission denial: 허용 목록 밖 PowerShell로 `dot -V`를 한 번 중복 탐침하려던 읽기 전용 호출 1건이 거부됐다. Graphviz는 허용된 경로와 실제 media test에서 검증됐고 검토 범위·결과에는 공백이 없다.
- 읽기 전용 검증: 검토 전후 HEAD, tree, `git status --short`와 핵심 파일 SHA-256 `14/14`가 동일했다. 상태는 기존 `?? tmp/`만 유지됐다.
- 결과: `Critical = 0`, `High = 0`, `Medium = 3`, `Low = 5`, `GATE = PASS`
- 라운드 수: 최신 제품 tree 전체 검토 1회. `Critical`/`High`가 0이므로 즉시 종료했으며 표적 재검토나 Medium/Low 자동 수정은 수행하지 않았다.

### 검토 이력

이 원장의 이전 제품 기준은 `6c068e99b711bbdff6536460e5cbb18ac44a44fa` / `d9d0ef30e91083cb9fc326c86035082400c35d3c`였고, 세션 `bc92d637-20b3-4eb7-8672-d672a0aaa748`이 `Critical 0 / High 0 / Medium 8 / Low 15`를 보고했다. 후속 whole-branch review가 I1-I6을 열었고, 각 수정·표적 재검토와 Release workbook refresh 뒤 현재 제품 tree를 새 전체 검토했다. 이전 counts와 workbook metadata는 현재 판정으로 대체한다.

## 현재 결정론적 gate

| Gate | 최신 결과 |
|---|---|
| Python 3.13.13 developer environment | PASS — `94/94`, failures 0, errors 0, skips 0 |
| 새 빈 Python 3.13.13 venv + `requirements-ci.txt` | PASS — install, `pip check`, Graphviz `dot 15.1.1`, Python `94/94` |
| Node 24.16.0, 모든 `tests/*.test.mjs` | PASS — `9/9` |
| `python tools/validate_catalog.py site/data/catalog.json site` | PASS — `valid catalog: 6 papers, 62 artifacts` |
| 금지된 추적 산출물 스캔 | PASS — `output/`, `tmp/`, private translations, PDF/PPTX/XLSX 추적 0건 |
| `site/` NotebookLM ID·password·로컬 경로 스캔 | PASS — 0건 |
| `git diff --check`, `git diff --cached --check` | PASS |
| Git 기준선 | 제품 HEAD/tree exact match, 기존 untracked `tmp/`만 존재 |

## Release v3 및 catalog 결합

Release `artifacts-2026-08-12-v3`은 public, non-draft, non-prerelease이며 정확히 3개 자산을 가진다. Release tag와 원격 feature branch는 `511dd65f405a93cbb286ec605b858f994b84c7c5`를 가리킨다. GitHub API metadata, fresh in-memory download, 로컬 staged asset, catalog v3의 URL·크기·SHA-256이 모두 일치했다.

| 자산 | bytes | SHA-256 | API=download=local=catalog |
|---|---:|---|---|
| `SW-AI-change-agent-research-model-v0.3-advisor-deck.pdf` | 560446 | `866089b52cfea9fbe3fc9c76b2be5a993352e384ebb86fa42f473ec89db5db59` | PASS |
| `SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx` | 139036 | `35c9b6c875bd326689823893f1bba095ffc0dc090e7bb10a7020790c01fcd628` | PASS |
| `SW-AI-change-agent-research-model-v0.3-workbook.xlsx` | 33513 | `ebe7d6047a5283580e284e622b7e214bd288648addc0fdb8249ead0d3909bee0` | PASS |

## Whole-branch I1-I6 최종 처분

| ID | 원래 blocker | 최종 근거와 follow-up | 처분 |
|---|---|---|---|
| I1 | Pages clean runner에 Python dependency와 Graphviz 설치 계약이 없어 `openpyxl` import에서 중단 | `requirements-ci.txt`가 네 direct dependency를 고정하고 Pages validate가 이를 설치한 뒤 Graphviz를 설치·탐침한다. 새 빈 venv에서 `94/94`, `pip check` clean. 회귀 검사는 manifest와 install→probe→test 순서를 고정한다. Follow-up은 최신 M2 Node `6/9` 선택과 M3 unauthenticated GitHub API다. | **CLOSED** |
| I2 | 모형의 유일한 조절변수 `변화 발산성`에 사건 측정과 P6/P7 처분 경로가 없음. 이전 원장 M3가 이를 `비공식 역할 변화`로 잘못 옮김 | **M3 정정:** 문제 구성개념은 `비공식 역할 변화`가 아니라 `변화 발산성`이다. 파일럿 `§변화 발산성의 사건 수준 측정`과 `§P6/P7 사건 판정 경로`는 DV1-DV4 탐침·주 자료원·교차확인, 최소 2개 독립 자료원, 차원 벡터 비합산, 네 사건 판정, P6 NC-B/NC-I와 P7 RP/RD/CE의 입력·선후·지지·반증·부족/충돌·처분을 둔다. workbook builder의 32개 `EVENT_COLUMNS`는 `dv1..dv4_{decision,primary_source,corroboration}`, vector/event/aggregation/uncertainty, `p6_use_decision`, `p7_use_decision`과 stop validation을 가진다. `test_change_divergence_has_a_complete_event_measurement_path`와 `test_event_sheet_binds_divergence_dimensions_and_p6_p7_decisions`가 삭제·약화·교환·역전·오분류를 거부한다. | **CLOSED — 오기 정정 완료** |
| I3 | 윤리 safeguards, 논문 카드 직접근거, duplicate deck/PDF의 의미 손상이 테스트를 통과 | workbook은 canonical `ETH01-ETH14`를 문단/불릿에 동일하게 추출하고 누락 시 실패한다. 다섯 카드의 직접근거는 slug별 exact ordered facts에 결합되어 fabricated 37% causal claim과 추가 bullet/prose를 거부한다. `SLIDE_SEMANTIC_CONTRACT`는 12개 순서·고유 제목, slide별 facts/sources와 PDF page facts를 묶어 slide 5→4 중복을 두 형식에서 거부한다. Live PDF도 12개 고유 page와 0 mismatch를 확인했다. Follow-up은 최신 M1의 Ubuntu CI PDF test skip이다. | **CLOSED** |
| I4 | Neumann 카드가 조직별 governance·Shadow AI 차이를 세 조직 전체로 일반화 | 카드는 GMT의 formal whitelist/승인, Dinoco의 risk-averse vendor 선택, Insight Inc.의 비교 가능한 governance 부재를 분리하고, unapproved Shadow IT을 Dinoco/GMT에만 귀속한다. 분석 Markdown과 exact card contract에 일치한다. | **CLOSED** |
| I5 | XLSX가 wall-clock ZIP metadata 때문에 byte-deterministic하지 않음 | `_normalize_xlsx`가 ZIP name order, timestamps, compression과 modified metadata를 고정한다. 2.1초 지연 double-build test가 byte equality를 요구한다. 독립 rebuild 2회가 동일하고 현재 published/catalog XLSX `33513` / `ebe7d604…09bee0`을 정확히 재현했다. Follow-up은 최신 L1의 tag provenance다. | **CLOSED** |
| I6 | 실제 참여자 인지면접이 승인·동의보다 먼저 배치 | matrix H2는 G0·G1 승인과 H1 동의 회수 뒤에만 인지면접을 허용하고, H3는 필요한 재승인 뒤 승인된 protocol로만 pilot을 허용한다. 테스트는 단계 교환, `동의 회수 전에`, 부정된 중단문 우회를 거부하고 canonical 사전 gate 금지문만 허용한다. | **CLOSED** |

모든 I1-I6 scoped rereview는 최종 `ADDRESSED`, `Critical 0`, `Important 0 open`을 보고했다. 관련 구현 commits는 I1 `b1ed068`, I2/I6 최종 `f866c34`, I3/I4 cards `3229175`, I2/I3/I5 workbook `217b413`, I3 media `7b6e39f`, Release/catalog refresh `b5ae278`이다.

## 최신 전체 검토의 비차단 발견

### Medium

| ID | 독립 재현과 영향 | 처분 |
|---|---|---|
| M1 | `build_media()`는 PNG/PPTX만 만들며 PDF builder가 없다. PDF test는 Windows LibreOffice 절대경로가 없으면 skip하므로 `ubuntu-latest`에서는 항상 skip한다. 현재 published PDF는 12쪽 semantic contract와 digest에 일치하지만 CI가 그 의미를 실행 검증하지 않는다. | **수용·pre-merge provenance/coverage backlog**. pinned PDF build/verify 또는 manual conversion+digest provenance를 명시한다. 현재 byte-integrity 우회는 없다. |
| M2 | Pages workflow는 `protected_crypto.test.mjs` 6개만 실행하고 `protected_viewer.test.mjs` 3개를 실행하지 않는다. 후자는 path traversal, public/duplicate ID, ciphertext size/hash/KDF binding을 다룬다. 모든 9개는 로컬 통과했다. | **수용·CI hardening backlog**. workflow를 all-Node로 확장하고 좁은 assertion을 갱신한다. 현재 live regression은 재현되지 않았다. |
| M3 | catalog validator의 GitHub Release API 요청은 `Authorization` header 없이 실행된다. 공유 runner rate limit/API 장애면 validate와 deploy가 fail-closed로 중단된다. 이번 실행의 live 요청은 성공해 실제 throttle은 재현되지 않았다. | **수용·가용성 backlog**. `${{ github.token }}`을 전달하도록 후속 hardening한다. 데이터 손실·무결성 우회가 아닌 실패 폐쇄형 가용성이다. |

### Low

| ID | 독립 재현과 영향 | 처분 |
|---|---|---|
| L1 | Release tag `511dd65`의 workbook builder SHA-256은 `b30ee593…`; 현재 published workbook을 재현하는 HEAD builder는 `ae84988c…`다. workbook 자산은 후속 refresh 시각에 바뀌었지만 tag는 이동하지 않았다. | **수용·provenance backlog**. catalog/Release byte binding은 정상이다. |
| L2 | 이전 원장이 구 제품 commit/tree와 old XLSX `32352` / `7fdbd00b…`을 기록했다. | **이번 원장에서 정정·종결**. 현재 값은 위 제품 기준과 `33513` / `ebe7d604…`이다. |
| L3 | 이전 원장 M3가 sole moderator를 `비공식 역할 변화`라고 오기했다. 그 문구는 제품에서 이전 원장 한 곳에만 있었고 실제 구성개념은 `변화 발산성`이다. | **이번 원장에서 정확히 정정·종결**. I2 표에 실제 end-to-end 경로와 tests를 기록했다. |
| L4 | deck slide 12 builder가 녹색 `설계 게이트 PASS / Critical 0 · High 0`을 hardcode해 이후 검토 결과를 추적하지 못하고, 미완료 fieldwork gate와 승인 범위를 혼동할 수 있다. 인접 panel은 현장조사 미개시를 밝힌다. | **수용·표현 backlog**. 현장조사 승인으로 해석하지 않는다. |
| L5 | speaker notes의 `tools/…`, `docs/reviews/…`, `docs/superpowers/specs/…` 네 경로는 Pages가 `site/`만 배포하므로 deck 수신자가 열 수 없다. | **수용·출처 접근성 backlog**. |

`Medium`/`Low`는 현재 severity 계약에서 새 review round나 자동 수정을 유발하지 않는다. 이번 단계에서는 수정하지 않았다.

## 이전 비차단 잔여위험

- 공개 ciphertext의 4자 password는 기존 설계와 viewer에 명시된 승인 잔여위험이다. AES-GCM/PBKDF2와 memory-only 처리의 우회는 재현되지 않았으며 password cracking은 수행하지 않았다.
- 사용자 다운로드 시 브라우저가 catalog size/SHA-256을 직접 검증·표시하지 않는다. publish/validation-time digest gate는 유지되지만 end-user download-time integrity는 방어심화 backlog다.
- internal Markdown preview의 literal link 표시, 일반 page의 CSP 부재, PDF/PPTX metadata hygiene, deck hardcoding, 이전 Task 3 link-label과 Task 5 color-semantics ambiguity는 비차단 backlog로 유지한다.
- `looks_like_pdf`의 fail-closed 호환성 제한과 PNG decompression `flush()`의 operator-input availability amplification은 기존 비차단 잔여위험이다.

## 연구방법 준비와 개인정보·연구윤리 준비의 분리

### 연구방법 준비

DV1-DV4, P6/P7 사건 판정, 32-field workbook, 14 ethics safeguards와 semantic regression contracts는 pre-fieldwork coding design을 구현한다. 이는 측정·코딩 계약의 존재와 내부 일관성을 검증한 것이며, P1-P7이나 분류 규칙의 실증 타당도, 응답자 부담 또는 파일럿 실현 가능성을 입증한 것이 아니다. P1-P7은 모두 검증 전이다.

### 완료되지 않은 실제 fieldwork/privacy/ethics gate

다음은 문서에 요구사항으로 존재할 뿐 완료 증거가 없다.

1. 실제 IRB 또는 동등한 연구윤리 승인
2. 기업 보안·법무·데이터 보호 승인과 조직별 자료접근 협약
3. 관할에 적합한 동의서 및 비응답 alter의 동의·통지·waiver 판단
4. 독립 모집·동의회수·인터뷰 절차와 실제 담당자 지정
5. 내부자 연구자의 위치성·이해상충 공개문
6. 익명화·연결코드 custody, 녹음·전사·코딩자료 저장 위치, 보존기간과 폐기 증거
7. participant audio/transcript의 cloud·AI 처리 허용·금지 경계
8. 위법·안전·보안 incident의 보고 대상·기한·escalation chain
9. 실제 조직·팀·gatekeeper 접근 확보
10. 60분 일정, alter 8명, alter-alter pair 10개의 실제 응답자 부담 검증

따라서 **모집, 접촉, 동의 회수, 인지면접, 파일럿, 인터뷰, 이름 생성, 조직 자료 수집은 시작할 수 없으며 시작하지 않았다**. 패키지 `PASS`는 위 gate를 대체하지 않는다.

## 다음 작업 경계

현재 제품 tree는 로컬 package-integrity gate의 `Critical 0 / High 0`을 충족한다. 다음 단계는 별도 사용자 승인 아래 push/PR/checks/merge/Pages/live desktop·mobile QA를 수행하는 Task 7 Phase B다. 이 원장 commit은 제품·인터페이스·테스트·배포 bytes를 변경하지 않아야 하며, Phase B 전까지 외부 branch/site 상태는 현재대로 유지한다.
