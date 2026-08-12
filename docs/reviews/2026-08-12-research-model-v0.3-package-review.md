# 연구모형 v0.3 패키지 최종 검토 원장

## 판정

- 검토 대상 제품 커밋: `6c068e99b711bbdff6536460e5cbb18ac44a44fa`
- 검토 대상 제품 트리: `d9d0ef30e91083cb9fc326c86035082400c35d3c`
- 검토 브랜치: `codex/complete-paper-artifacts-impl`
- 유효한 최신 전체 독립 검토: `Critical = 0`, `High = 0`, `Medium = 8`, `Low = 15`, `GATE = PASS`
- 현재 열린 `Critical`: **0**
- 현재 열린 `High`: **0**
- 패키지 상태: **READY_FOR_PREMERGE_REVIEW**
- 이 판정은 병합, push, PR, 배포 또는 현장조사 개시 승인이 아니다. 새 작업 세션의 전체 브랜치 pre-merge review가 별도로 필요하다.

## 고정 범위와 위협 모델

전체 검토는 catalog v3 계약, 공개 연구설계 문서 4개, 논문별 기여 카드 5개, PNG/XLSX/PPTX/PDF 생성·출처·Release 결합, protected companion 권리 경계, 암호화 뷰어, 데이터 보호 설계, 사이트 렌더링 및 자동 테스트를 포함했다. 기본·승인 구성에서의 우발적 운영자 실수, 악성·손상 입력, 계획과 적용 사이의 상태 변화, 외부 신뢰 기준을 지배하지 못하는 행위자의 로컬 변조를 위협 모델에 포함했다.

구현 코드, 저장소·Git·로컬 구성, 외부에서 검토된 해시·승인 기록, 최종 커밋·복제를 한 행위자가 모두 동시에 지배해야만 성립하는 시나리오는 제외했다. `Critical`/`High`는 지원 워크플로에서 재현 가능한 영속 데이터 손실, 자격증명 경계 침해, 권한 없는 상태 승격, 손상 복제본 승인 또는 핵심 무결성 게이트 우회에만 부여했다.

## 검토 실행과 유효성

- 실행: Windows Claude CLI, `--model claude-opus-5 --effort xhigh`, 읽기 전용 도구와 `dontAsk`, `safe-mode`, `no-chrome`
- 세션 ID: `bc92d637-20b3-4eb7-8672-d672a0aaa748`
- 요청 증거: `.superpowers/sdd/2026-08-12-research-model-v0.3-package/task-7-claude-request.md`
- 응답·도구 호출 전체 증거: `C:\Users\kimhy\.claude\projects\C--projects-paper--worktrees-complete-paper-artifacts-impl\bc92d637-20b3-4eb7-8672-d672a0aaa748.jsonl`
- 전송 디버그 증거: `.superpowers/sdd/2026-08-12-research-model-v0.3-package/task-7-claude-debug.log`
- 모델 검증: transcript의 assistant record 121개가 모두 `claude-opus-5`; debug의 first-party dispatch 120개가 모두 `claude-opus-5`; 다른 resolved model 또는 자동 fallback은 없었다.
- 읽기 전용 검증: 검토 전후 HEAD, tree, 네 핵심 입력 SHA-256과 Git 상태가 동일했다.
- 라운드 수: 전체 검토 1회. `Critical`/`High`가 없으므로 표적 종결 검토는 실행하지 않았다.

## 결정론적 게이트 증거

제품 트리에서 새로 실행한 결과는 다음과 같다.

| 게이트 | 결과 |
|---|---|
| `python -m unittest discover -s tests -v` | PASS — 84 tests, 0 failures/errors |
| `node --test` on all `tests/*.test.mjs` | PASS — 9 tests, 0 failures |
| `python tools/validate_catalog.py site/data/catalog.json site` | PASS — `valid catalog: 6 papers, 62 artifacts` |
| 금지된 추적 산출물 스캔 | PASS — `output/`, `tmp/`, private translations, PDF/PPTX/XLSX 추적 0건 |
| `site/` 비밀·NotebookLM ID·로컬 경로 스캔 | PASS — 0건 |
| `git diff --check`, `git diff --cached --check` | PASS |
| Git 기준선 | HEAD와 tree가 위 고정값과 일치, 기존 untracked `tmp/`만 존재 |

## Release 및 카탈로그 결합

Release `artifacts-2026-08-12-v3`은 공개·비초안·비프리릴리스이며 정확히 세 자산을 가진다. Release tag와 원격 feature branch는 `511dd65f405a93cbb286ec605b858f994b84c7c5`를 가리키고, catalog v3이 외부 자산의 이름·URL·크기·SHA-256을 고정한다. tag가 catalog-binding 커밋보다 앞선다는 사실은 L9로 별도 기록한다.

| 자산 | bytes | SHA-256 | API=다운로드=로컬=catalog |
|---|---:|---|---|
| `SW-AI-change-agent-research-model-v0.3-advisor-deck.pdf` | 560446 | `866089b52cfea9fbe3fc9c76b2be5a993352e384ebb86fa42f473ec89db5db59` | PASS |
| `SW-AI-change-agent-research-model-v0.3-advisor-deck.pptx` | 139036 | `35c9b6c875bd326689823893f1bba095ffc0dc090e7bb10a7020790c01fcd628` | PASS |
| `SW-AI-change-agent-research-model-v0.3-workbook.xlsx` | 32352 | `7fdbd00b3bc0702802fa6cb081e00d839bbc52374e86300f491461e8e266c8ae` | PASS |

## 독립 발견 처분

Phase A는 수용된 `Critical`/`High`만 수정하도록 제한됐다. 해당 등급이 0건이므로 아래 Medium/Low는 제품을 자동 수정하지 않고 재현 증거와 다음 경계를 기록한다.

### Medium

| ID | 독립 재현과 영향 | 처분 |
|---|---|---|
| M1 | 공개 핵심 행렬의 진행 순서가 3인 인지면접을 IRB·동의 준비보다 먼저 둔다. 실제 참가자 접촉 전에 승인·동의가 선행해야 한다. | **수용·현장조사 전 필수**. 연구방법 준비의 순서 결함이며 pre-merge `Critical`/`High`는 아니다. |
| M2 | alter별 관계자료를 수집하지만 비응답 alter 처리의 승인 근거, 녹음·전사·코딩자료 보존기간, cloud/AI 전사 제한, 인터뷰어 권력관계, 현장 위법·위험 사건 보고 규칙이 완결되지 않았다. 모든 alter에게 별도 동의가 항상 필수라는 주장은 관할·IRB별 판단이다. | **부분 수용·개인정보/연구윤리 gate**. 실제 모집 전에 IRB·법무·보안이 동의/waiver, 보존·폐기, 전사 경계, 독립 인터뷰, 즉시 보고 규칙을 확정한다. 방법론 타당도와 별도 gate로 유지한다. |
| M3 | `비공식 역할 변화`는 사전에 정의되고 인터뷰 종료 질문에는 등장하지만 사건코드, workbook 열, 전용 탐침·판정 규칙이 없다. | **수용·현장조사 전 필수**. 관찰·코딩 계약을 정한 뒤 파일럿한다. |
| M4 | 계약 테스트가 산출물의 의미보다 형태에 치우쳤다. 의미를 유지한 bullet 재서식으로 윤리행이 14→5로 줄어도 10개 asset test가 모두 통과했고, `_slide_5 = _slide_4`로 중복 슬라이드를 만들어도 두 media test가 통과했다. Kemell 직접근거에 허위 인과·수치 문장을 넣어도 카드 계약이 통과했다. `tests/`는 shipped `output/`을 참조하지 않고 viewer 행동 테스트도 없다. | **수용·pre-merge 품질 backlog**. 생성물-원문 의미 계약, shipped-byte 검증, renderer 행동 테스트를 보강한다. 현재 canonical identity/hash gate 자체의 우회는 재현되지 않았다. |
| M5 | clean venv에서 asset test import가 `ModuleNotFoundError: openpyxl`로 실패했고, 저장소에는 dependency manifest나 Pages 설치 단계가 없다. 배포는 fail-closed로 멈춘다. | **수용·배포 전 필수**. 새 pre-merge review가 runner dependency 계약과 Pages workflow를 점검해야 한다. 현재는 merge/deploy-ready가 아니다. |
| M6 | workbook을 1초 이상 간격으로 두 번 빌드하면 wall-clock modified timestamp 때문에 bytes/SHA가 달라진다. PNG/PPTX는 byte-stable이다. | **수용·재현성 backlog**. catalog의 현재 SHA 검증은 유지되지만 XLSX 재빌드 provenance는 불완전하다. |
| M7 | 공개 ciphertext가 4자 비밀번호로 보호된다. AES-GCM/PBKDF2 구현은 정상이고 기존 설계·viewer가 이 낮은 엔트로피를 명시했다. | **기존 승인 잔여위험으로 수용**. 이번 패키지의 새 결함이나 gate 우회가 아니며 크래킹을 시도하지 않았다. 권리자·법무 판단이 바뀌면 별도 재설계한다. |
| M8 | 사이트는 Release URL로 바로 연결하며 catalog의 size/SHA를 다운로드 시점에 검증·표시하지 않는다. 코드 부재는 확인했지만 외부 Release 변조는 수행하지 않았다. | **수용·방어심화 backlog**. 다음 validator run은 변조를 fail-closed로 탐지하지만 사용자 다운로드 즉시 검증은 없다. |

### Low

| ID | 독립 재현과 영향 | 처분 |
|---|---|---|
| L1 | 논문 카드가 주장하는 P 범위와 명제 추적표의 직접출처 연결이 일부 비대칭이다. | **수용** — 카드↔명제 양방향 추적성 정리. |
| L2 | v0.3의 P1-P7, 핵심 행렬의 P1-P6, 이론 bridge의 P1-P5가 명시적 supersession 없이 공존한다. | **수용** — 문서별 명제 집합과 버전 관계를 명시. |
| L3 | `looks_like_pdf`는 payload 어느 위치든 `%PDF-`가 있으면 거부한다. | **수용된 fail-closed 호환성 제한** — 정상 공개 문서 피해 사례는 없다. |
| L4 | PNG parser의 bounded `decompress` 뒤 `flush()`는 잔여 압축 스트림을 무제한 해제한다. 65,295-byte 입력이 거부되기 전에 약 148 MB Python heap을 사용했다(약 2,271배). | **수용** — 운영자 제공 입력에 대한 가용성 hardening backlog. |
| L5 | `protected-viewer.html`만 엄격한 CSP가 있고 `index.html`/`viewer.html`에는 없다. | **수용** — 정적 사이트 defense-in-depth. |
| L6 | `app.js`는 href scheme을 독립 검사하지 않는다. | **부분 수용** — canonical validator의 정확한 same-origin/Release href 계약이 현재 방어선이며 UI 독립검사는 backlog. |
| L7 | viewer는 Markdown 링크를 링크로 렌더링하지 않고 리터럴로 보인다. | **수용** — 사용성 backlog. |
| L8 | 계획의 `fieldwork-ready` 목표 표현과 같은 계획의 `fieldwork ready로 표시하지 말라`는 완료 경계가 충돌한다. | **수용** — 상태 용어 정리. 실제 산출물은 현장조사 미개시를 명시한다. |
| L9 | Release tag가 catalog-binding 커밋보다 앞서 있어 tag만으로는 최종 결합을 재구성할 수 없다. | **수용** — digest binding은 정상, provenance 설명 backlog. |
| L10 | PPTX에 `lastModifiedBy=Steve Canny`, Macintosh PowerPoint app 정보, printer settings, blank thumbnail 등 template residue가 있다. | **수용** — 공개 메타데이터 hygiene backlog; 비밀·로컬 경로는 발견되지 않았다. |
| L11 | PDF는 외부 LibreOffice 변환으로 생성되고 builder에 producer가 고정되지 않는다. 현재 파일은 LibreOffice `26.2.4.2`, +09:00 생성시각을 기록한다. | **수용** — build provenance·도구 pinning backlog. |
| L12 | speaker notes가 Pages에 배포되지 않는 `docs/`/`tools/` 내부 경로를 출처로 포함한다. | **수용** — 배포 후 출처 접근성 backlog. |
| L13 | deck 본문이 원문에서 파싱되지 않고 builder에 하드코딩되어 원문 변경 뒤 조용히 stale해질 수 있다. | **수용** — source-to-deck semantic contract backlog. |
| L14 | Neumann 카드가 세 조직 모두에 whitelist/approval governance가 있었던 것처럼 일반화하지만 직접 분석은 조직별 차이를 기록한다. | **수용** — 공개 직접근거 카드의 범위 표현을 pre-merge에서 재검토. |
| L15 | 마지막 슬라이드의 녹색 `설계 게이트 PASS`가 미충족 현장 gate 옆에 있어 승인 범위를 오해할 수 있다. | **수용** — 상태/색 의미 명료화 backlog. 제목과 본문은 현장조사 미개시를 함께 명시한다. |

## 이전 Task backlog의 최종 이관

- Task 3: 논문 카드의 `명제 추적표` 링크에 `기여 카드`라는 잘못된 label이 쓰인 항목은 **Low 사용성/추적성 backlog**로 유지한다.
- Task 5: 증거상태 색과 구성개념 색이 겹쳐 의미를 혼동할 수 있다는 항목은 L15와 함께 **Low 시각 의미 backlog**로 유지한다.
- 위 두 항목과 이번 Medium/Low는 `Critical`/`High`가 아니므로 이번 제한된 Phase A에서 자동 수정하거나 추가 전체 리뷰를 시작하지 않는다.

## 연구방법 준비와 개인정보·연구윤리 준비의 분리

### 연구방법 준비

문서·템플릿·명제·관계망 수집 계약은 pre-fieldwork 연구준비 산출물이다. M1, M3, M4, M6과 L1/L2/L7/L8/L12-L15는 측정·코딩·추적성·표현·재현성을 더 다듬어야 함을 뜻한다. 이 패키지는 P1-P7을 검증하거나 파일럿의 실현 가능성을 입증하지 않았다.

### 개인정보·연구윤리 준비

다음은 문서에 완료조건으로 적혀 있어도 실제 완료 증거가 없는 외부 gate다.

1. 실제 IRB 또는 동등한 연구윤리 승인
2. 기업 보안·법무·데이터 보호 승인과 조직별 자료접근 협약
3. 관할에 적합한 동의서와 비응답 alter의 동의·통지·waiver 판단
4. 독립 모집·동의회수·인터뷰 절차와 연구자 위치성/이해상충 공개
5. 익명화·연결코드·녹음·전사·코딩자료의 저장, cloud/AI 처리, 접근, 보존, 폐기 프로토콜
6. 현장 위법·안전·보안 사건의 중단·보고 절차
7. 조직 접근 확보와 실제 응답자 부담 검증

따라서 **현장조사는 시작할 수 없으며, 시작하지 않았다**. 위 gate는 방법론 문서 완성도나 패키지 검토 PASS로 대체되지 않는다.

## 다음 작업 경계

새 작업 세션에서 전체 브랜치 pre-merge review를 실행해야 한다. 그 검토는 최소한 M5의 clean-runner dependency/deploy 차단, M4의 의미·shipped-byte 테스트 공백, L14의 직접근거 범위, 그리고 모든 현장조사 전 외부 gate가 merge/deploy/fieldwork 승인과 혼동되지 않는지를 확인해야 한다. 이 원장의 commit 자체는 제품·인터페이스·테스트·배포 bytes를 변경하지 않아야 한다.
