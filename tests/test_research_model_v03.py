import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = (ROOT / "docs/superpowers/specs/2026-08-12-research-model-v0.3-design.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "site/downloads/research-design/core-paper-matrix-research-model-interview-guide.md").read_text(encoding="utf-8")
LEDGER = (ROOT / "docs/reviews/2026-08-12-research-model-v0.3-review.md").read_text(encoding="utf-8")


LEVEL_BLOCK = """실행된 역할 보완성 | 사건
활성화된 네트워크 연결성 | 사건
발언 안전성 | 개인×사건
발언 효능감 | 개인×사건
구성원 반응 | 개인×사건; 사건 지배 경로는 파생값
변화 발산성 | 사건
기초 네트워크 구조 | 팀 맥락; P1의 주 예측변수와 분리"""

ETHICS_RULES = (
    "인터뷰와 관계망 조사 전에 IRB와 기업 보안·법무 승인을 완료한다.",
    "비응답 지명자는 역할 범주로만 분석하며 규정위반 행동은 개인 코드가 아니라 사건에만 귀속한다.",
    "연결코드 명부는 전사·코딩자료와 분리 암호화하고 연구책임자만 접근하며 분석 종료 시 폐기한다.",
    "재직·협력 관계를 위치성·이해상충 진술에 공개한다.",
    "참여자와 지휘·평가 관계가 없는 독립 모집 담당자가 모집과 동의 회수를 수행한다.",
    "고용주에게 원자료를 제공하지 않는다. 법률 또는 IRB 승인 안전절차의 공개 한계는 동의서에 사전 명시한다.",
)

DELIVERABLE_RULES = (
    "연구동의서와 익명화·연결코드 명부 프로토콜",
    "재직·협력 관계의 위치성·이해상충 진술",
    "독립 모집 담당자의 모집·동의 회수 절차",
    "고용주와의 원자료 비공유 및 접근 경계를 정한 gatekeeper 자료접근 협약",
)

AGENDA = (
    ("동의·안전", 5),
    ("역할·AI 경험", 5),
    ("사건 타임라인", 10),
    ("결정적 사건", 15),
    ("관계망 질문", 12),
    ("역할별 질문", 8),
    ("정책 적합성·종료", 5),
)

MEASUREMENT_RULES = (
    "역할 보완성, 네트워크 연결성, AI 사건 특화 발언 효능감과 변화 발산성 문항 풀을 질적 자료에서 개발하고, 구성원 반응은 반응경로 코딩으로 먼저 정제한다.",
    "내용타당도 검토, 응답자 인지면접과 소규모 파일럿으로 문항의 이해도와 변별성을 확인하고, 차원성 검토를 수행한다.",
    "조절효과 검정 전에 각 구성개념의 reflective, formative 또는 index 결정을 명시한다.",
    "P6/P7 용어는 다음처럼 §6 구성개념 또는 탐색적 결과에 연결한다: 브로커리지는 §6.2의 중개자 의존, 응집성은 §6.2 네트워크 연결성의 팀 맥락 기술값, 관계강도는 §6.2의 관계별 빈도와 지각된 신뢰, 수신자 태도는 §6.6의 구성원 반응, 관계압력과 챔피언 소진은 탐색적 과정결과다. 이 연결은 P6/P7을 가설로 전환하지 않는다.",
)

P5_RULE = "P5의 같은 검정에서는 지배 경로 판정과 후행 과정결과를 독립항으로 함께 넣지 않는다."
SPEC_TIE_PROTOCOL = "각 사건의 관계는 `발신자 코드 → 수신자 코드`로 기록하는 유향 연결이다. 관계마다 (a) `발신자 보고 전달`(발신자가 명명된 수신자에게 정보·요청·위험 신호를 보냈다고 진술한 사실), (b) `수신·확인 근거`(명명된 수신자가 받은 사실을 진술·문서·확인 기록으로 뒷받침한 근거), (c) `수신 뒤 수신자 태도`(수신 뒤 수용·보류·거절·회피 중 확인된 반응)를 분리해 기록한다. 발신자 보고만으로는 수신을 확정하지 않는다."
GUIDE_TIE_PROTOCOL = "각 표시된 관계는 초점 사건의 `발신자 코드 → 수신자 코드` 유향 기록이다. 관계마다 (a) `발신자 보고 전달`(발신자가 명명된 수신자에게 신호를 보냈다고 진술한 사실), (b) `수신·확인 근거`(명명된 수신자의 진술·문서·확인 기록), (c) `수신 뒤 수신자 태도`(수신 뒤 수용·보류·거절·회피 중 확인된 반응)를 같은 순서로 기록한다. 발신자 보고만으로는 수신을 확정하지 않는다."
DELIVERY_LEDGER_DISPOSITION = "| 전달·수신·수신자 태도 경계 | 수용·수정 | §6.2와 Q3이 사건별 유향 연결, 발신자 보고 전달, 명명된 수신자의 수신·확인 근거, 수신 뒤 수신자 태도를 분리하고 발신자 보고만으로 수신을 확정하지 못하게 한다. |"

CARD_H2_CONTRACT = (
    ("직접 근거", "**논문 직접 근거**"),
    ("v0.3에서의 역할", "**통합 해석**"),
    ("연결되는 명제", "**후속 연구 명제 (검증 전)**"),
    ("검증하지 않은 것", "**논문 직접 근거의 한계**"),
    ("현장자료 요구", "**후속 연구를 위한 자료 요구**"),
)

CARD_COMMON_BOUNDARIES = (
    "P1-P7은 모두 검증 전 후속 연구 명제다.",
    "이 카드는 현장조사 시작이나 실증 검증을 뜻하지 않으며",
    "NotebookLM 산출물은 근거로 사용하지 않는다.",
)

CARD_V03_REQUIREMENTS = {
    "kemell-2025": (
        ("v0.3에서의 역할", "공식 AI 도입과 비공식 실험이 함께 존재하는 SW 조직의 사건 맥락을 제공한다."),
        ("연결되는 명제", "P1-P5를 검토할 때, 공식 도입과 현장 실험이 공존하는 AI 사건을 표집할 이유를 제공한다."),
        ("검증하지 않은 것", "공식 리더와 비공식 AI 챔피언의 역할 분담이나 두 주체의 네트워크 연결을 측정하지 않았다."),
        ("검증하지 않은 것", "저항 관리의 효과, 책임 있는 AI 채택, 정책-실무 정합성을 인과적으로 검증하지 않았다."),
    ),
    "neumann-2026": (
        ("v0.3에서의 역할", "v0.3의 **정책-실무 간극과 Shadow AI 신호**를 보여 주는 현상 앵커다."),
        ("연결되는 명제", "P4의 은폐·이탈 경로와 P5의 정책-실무 정합성 맥락을 구체화한다."),
        ("검증하지 않은 것", "리더·보안·법무·챔피언이 누구와 어떻게 연결되어 정책을 번역하거나 우회를 표면화하는지 측정하지 않았다."),
    ),
    "golgeci-2025": (
        ("v0.3에서의 역할", "v0.3의 **개념적 AI 저항과 완화 메커니즘**을 제공한다."),
        ("연결되는 명제", "P1-P5의 구성원 반응과 발언 안전성·발언 효능감의 과정 해석에 기여한다."),
        ("검증하지 않은 것", "개념 논문이므로 과정의 실제 순서와 효과를 실증 검증하지 않았다."),
        ("검증하지 않은 것", "AI 저항의 경험적 척도 타당화 연구가 아니다."),
    ),
    "battilana-casciaro-2012": (
        ("v0.3에서의 역할", "v0.3의 **변화 발산성에 따른 네트워크 구조 조건**을 제공한다."),
        ("연결되는 명제", "P6의 조건부 논리, 즉 고발산 사건의 중개 연결과 저발산 사건의 팀 내부 응집·강한 관계를 탐색할 이론적 출발점이다."),
        ("검증하지 않은 것", "NHS 결과를 SW·AI 조직에 직접 일반화할 수 없다."),
    ),
    "battilana-casciaro-2013": (
        ("v0.3에서의 역할", "v0.3의 **수신자 태도와 관계강도 경계**를 제공한다."),
        ("연결되는 명제", "P7의 관계 기반 설득 경계조건을 검토하는 이론적 출발점이다."),
        ("직접 근거", "고괴리 조건의 부정적 단순기울기는 모형에 따라 한계적 유의성을 포함해 과장할 수 없다."),
    ),
}


def section(text, heading):
    start = text.index(heading)
    body_start = start + len(heading)
    level = len(heading.split(maxsplit=1)[0])
    following = re.search(rf"^#{{1,{level}}}\s", text[body_start:], re.MULTILINE)
    end = body_start + following.start() if following else len(text)
    return text[body_start:end]


def h2_sections(text):
    matches = list(re.finditer(r"^## ([^\n]+)$", text, re.MULTILINE))
    return tuple(
        (match.group(1), text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)])
        for index, match in enumerate(matches)
    )


class ResearchModelV03Tests(unittest.TestCase):
    def assert_once(self, text, clause):
        self.assertEqual(text.count(clause), 1, f"missing, duplicated, or mutated contract clause: {clause}")

    def assert_level_contract(self, level_section):
        self.assert_once(level_section, LEVEL_BLOCK)
        self.assert_once(
            level_section,
            "사건 점수는 초점 사건에서 실제로 실행된 역할분담과 활성화된 관계 연결로 산정한다.",
        )
        self.assert_once(
            level_section,
            "정적인 팀 중심성, 브로커리지, 응집성은 연구 1이 팀 수준 가설을 뒷받침할 때까지 팀 맥락의 기술값으로만 보관하며 P1의 주 예측변수에 포함하지 않는다.",
        )

    def assert_pilot_contract(self, agenda_section, name_generator_section):
        agenda_match = re.search(r"```text\n(.*?)\n```", agenda_section, re.DOTALL)
        self.assertIsNotNone(agenda_match, "missing fixed 60-minute agenda block")
        agenda = tuple((label.strip(), int(minutes)) for label, minutes in re.findall(r"([^|\n]+?)\s+(\d+)분", agenda_match.group(1)))
        self.assertEqual(agenda, AGENDA)
        self.assertEqual(sum(minutes for _, minutes in agenda), 60)
        for clause in (
            "한 초점 사건에는 하나의 명부만 사용하며, 고유 인물 최대 8명으로 제한한다.",
            "각 alter마다 조언, 신뢰, 승인·예외, 위험 에스컬레이션 관계를 표시하고, 접촉 빈도, 지각된 신뢰, 공식 역할 속성은 한 번만 수집한다.",
            "alter-alter 관계는 초점 사건에서 핵심 인물 최대 5명 사이에서만 묻고, 무방향 쌍 최대 10개로 제한한다.",
        ):
            self.assert_once(name_generator_section, clause)

    def assert_v03_card_contract(self, slug, text):
        sections = h2_sections(text)
        headings = tuple(heading for heading, _ in sections)
        expected_headings = tuple(heading for heading, _ in CARD_H2_CONTRACT)
        self.assertEqual(headings, expected_headings, slug)
        by_heading = dict(sections)

        for heading, label in CARD_H2_CONTRACT:
            self.assertIn(label, by_heading[heading], f"{slug}: missing {label} in {heading}")
        for boundary in CARD_COMMON_BOUNDARIES:
            self.assertIn(boundary, text, f"{slug}: missing common boundary")
        for heading, clause in CARD_V03_REQUIREMENTS[slug]:
            self.assertIn(clause, by_heading[heading], f"{slug}: missing role contract in {heading}")

    def test_level_contract_is_complete_and_rejects_a_missing_row(self):
        level_section = section(SPEC, "## 4. 분석단위와 다수준 구조")
        self.assert_level_contract(level_section)

        mutated = level_section.replace("구성원 반응 | 개인×사건; 사건 지배 경로는 파생값\n", "")
        with self.assertRaises(AssertionError):
            self.assert_level_contract(mutated)

    def test_ethics_and_deliverable_contract_rejects_a_removed_safeguard(self):
        ethics_section = section(SPEC, "## 13. 연구윤리와 조직 안전")
        deliverables_section = section(SPEC, "## 16. 다음 산출물의 완료 조건")
        for clause in ETHICS_RULES:
            self.assert_once(ethics_section, clause)
        for clause in DELIVERABLE_RULES:
            self.assert_once(deliverables_section, clause)

        mutated = ethics_section.replace(ETHICS_RULES[-1], "")
        with self.assertRaises(AssertionError):
            for clause in ETHICS_RULES:
                self.assert_once(mutated, clause)

    def test_pilot_contract_has_a_complete_agenda_and_rejects_a_pair_cap_mutation(self):
        agenda_section = section(GUIDE, "## 5. 인터뷰 공통 진행 순서")
        name_generator_section = section(GUIDE, "### Q3. 관계망 이름생성기")
        self.assert_pilot_contract(agenda_section, name_generator_section)

        mutated = name_generator_section.replace("무방향 쌍 최대 10개", "무방향 쌍 최대 12개")
        with self.assertRaises(AssertionError):
            self.assert_pilot_contract(agenda_section, mutated)

    def test_measurement_p6_p7_and_p5_contracts_reject_a_decision_mutation(self):
        measurement_section = section(SPEC, "### 11.3 연구 2: 측정모형 정제")
        process_section = section(SPEC, "### 6.6 구성원 반응과 지배 경로")
        for clause in MEASUREMENT_RULES:
            self.assert_once(measurement_section, clause)
        self.assert_once(process_section, P5_RULE)

        mutated = measurement_section.replace("reflective, formative 또는 index 결정", "검토 대상 결정")
        with self.assertRaises(AssertionError):
            for clause in MEASUREMENT_RULES:
                self.assert_once(mutated, clause)

    def test_directed_tie_protocol_requires_delivery_receipt_and_stance_evidence(self):
        network_section = section(SPEC, "### 6.2 네트워크 연결성")
        name_generator_section = section(GUIDE, "### Q3. 관계망 이름생성기")
        task_one_ledger = section(LEDGER, "## Task 1 — 현장조사 전 설계 게이트 처분")
        self.assert_once(network_section, SPEC_TIE_PROTOCOL)
        self.assert_once(name_generator_section, GUIDE_TIE_PROTOCOL)
        self.assert_once(task_one_ledger, DELIVERY_LEDGER_DISPOSITION)

        mutated = network_section.replace("발신자 보고만으로는 수신을 확정하지 않는다.", "")
        with self.assertRaises(AssertionError):
            self.assert_once(mutated, SPEC_TIE_PROTOCOL)

    def test_every_paper_has_one_v03_contribution_card(self):
        slugs = ["kemell-2025", "neumann-2026", "golgeci-2025", "battilana-casciaro-2012", "battilana-casciaro-2013"]
        for slug in slugs:
            path = ROOT / "site/downloads" / slug / "model-v0.3-contribution.md"
            self.assertTrue(path.is_file(), slug)
            text = path.read_text(encoding="utf-8")
            self.assert_v03_card_contract(slug, text)

    def test_v03_card_contract_rejects_a_downgraded_h2(self):
        path = ROOT / "site/downloads/kemell-2025/model-v0.3-contribution.md"
        mutated = path.read_text(encoding="utf-8").replace("## v0.3에서의 역할", "> ## v0.3에서의 역할", 1)

        with self.assertRaises(AssertionError):
            self.assert_v03_card_contract("kemell-2025", mutated)

    def test_v03_card_contract_rejects_a_missing_integrated_interpretation_label(self):
        path = ROOT / "site/downloads/kemell-2025/model-v0.3-contribution.md"
        mutated = path.read_text(encoding="utf-8").replace(
            "## v0.3에서의 역할\n\n**통합 해석**",
            "## v0.3에서의 역할",
            1,
        )

        with self.assertRaises(AssertionError):
            self.assert_v03_card_contract("kemell-2025", mutated)

    def test_epistemic_and_no_fieldwork_boundaries_reject_a_proposition_mutation(self):
        theory_section = section(SPEC, "## 3. 이론적 위치와 근거 경계")
        propositions_section = section(SPEC, "## 9. 잠정 이론적 명제")
        scope_section = section(SPEC, "## 15. v0.3 범위 밖")
        deliverables_section = section(SPEC, "## 16. 다음 산출물의 완료 조건")
        task_one_ledger = section(LEDGER, "## Task 1 — 현장조사 전 설계 게이트 처분")

        self.assert_once(theory_section, "v0.3은 기존 논문의 직접 검증 결과와 여러 이론을 연결해 도출한 후속 연구 명제를 구분한다. 아래 P1-P7은 검증된 사실이 아니다.")
        for proposition in range(1, 8):
            self.assertEqual(propositions_section.count(f"- **P{proposition}.**"), 1)
        self.assert_once(propositions_section, "P1-P7은 질적 연구에서 수정, 분기 또는 기각할 명제다. 자료가 지지한 경로와 측정 타당성이 확보된 구성개념만 후속 양적 연구의 H1-Hn으로 전환한다.")
        self.assert_once(scope_section, "NotebookLM 요약, 오디오, 슬라이드와 인포그래픽을 학술적 증거로 사용하지 않는다.")
        self.assert_once(deliverables_section, "각 산출물은 `논문이 직접 말한 것`, `여러 이론의 통합 해석`, `후속 실증에서 검증할 명제`를 시각적·문장 수준에서 구분해야 한다.")
        self.assert_once(task_one_ledger, "인터뷰, 모집, 이름 생성, 조직 자료 수집은 시작하지 않았다.")

        mutated = propositions_section.replace("P1-P7은 질적 연구에서 수정, 분기 또는 기각할 명제다.", "P1-P7은 검증된 가설이다.")
        with self.assertRaises(AssertionError):
            self.assert_once(mutated, "P1-P7은 질적 연구에서 수정, 분기 또는 기각할 명제다. 자료가 지지한 경로와 측정 타당성이 확보된 구성개념만 후속 양적 연구의 H1-Hn으로 전환한다.")
