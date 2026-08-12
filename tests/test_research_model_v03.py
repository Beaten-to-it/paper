import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = (ROOT / "docs/superpowers/specs/2026-08-12-research-model-v0.3-design.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "site/downloads/research-design/core-paper-matrix-research-model-interview-guide.md").read_text(encoding="utf-8")
MATRIX = GUIDE
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

CARD_DIRECT_EVIDENCE_FACTS = {
    "kemell-2025": (
        "유럽 SW 기업 7곳의 다중 사례에서 회사가 정한 라이선스·도구, 현장 사용, 상향식 수요, 공식 제공 밖 도구의 자율 사용이 서로 다른 방식으로 병존했다.",
        "공식 조직 라이선스가 없는 Company E에서도 개발자 사용이 널리 나타났고, 공식 제공 도구 밖 사용과 개인 시간 실험은 잠재적 Shadow IT 문제로 연결됐다.",
        "저항의 직접 증거는 파일럿의 한 회의적 참여자처럼 얇았으며, 선택적 참여 때문에 저항이 관찰 표본 밖에 남았을 가능성을 저자들이 언급했다.",
    ),
    "neumann-2026": (
        "GMT는 EU AI Act 위험 분류, 공식 화이트리스트, 경영진 승인, 내부 전문가 그룹의 검증을 갖춘 공식형 거버넌스를 사용했다.",
        "Dinoco는 compliance와 최고경영진이 기존 대형 벤더 중심으로 도구를 정하는 위험회피형 방식을 사용했다.",
        "Insight Inc.에는 비교 가능한 거버넌스 구조가 없었다.",
        "ChatGPT는 세 조직 모두에서 가장 자주 사용됐지만, 비승인 Shadow IT 사용은 Dinoco와 GMT에서만 보고됐다.",
        "Dinoco에는 비승인 ChatGPT 사용을 개인 시간 사용으로 재분류하는 비공식 합의가 있었고, GMT에서는 공식 정책이 있어도 구성원들이 업무에 개인 계정을 사용했다.",
        "실용적 대안·학습·지원이 부족한 공식 규칙은 준수 책임을 개인에게 전가했고, 저자들은 기술 특성·조직 제약을 충분히 고려하지 않은 정책 번역이 정책-실무 간극과 Shadow IT를 낳는다고 해석했다.",
        "연구는 역할별 사용과 정책 우회를 보여 주지만, 공식 리더와 비공식 AI 챔피언의 관계망은 측정하지 않았다.",
    ),
    "golgeci-2025": (
        "이 통합적 문헌고찰과 개념적 과정 프레임워크는 AI 저항을 두려움, 비효능감, 반감의 비배타적 차원으로 설명한다.",
        "AI 불신, 실존적 질문, 기술 성찰과 AI 접근성, 인간-AI 증강, 기술 정당화의 조직적 완화 메커니즘을 개념적으로 연결한다.",
        "저자들의 세 연결은 이론적 명제이며, 효과나 시간 순서를 실증한 인과 결과가 아니다.",
    ),
    "battilana-casciaro-2012": (
        "영국 NHS의 변화 프로젝트 68개에서, 구조적 공백이 많은 변화주도자는 더 제도적으로 이탈한 변화를 발의하는 경향을 보였다.",
        "변화 채택에서는 구조적 공백의 주효과가 아니라 변화 괴리도와의 상호작용이 중요했다. 고괴리 변화에는 중개형 네트워크가, 기존 관행과 가까운 변화에는 응집형 네트워크가 더 유리했다.",
        "이는 단일 변화주도자의 자아중심 네트워크와 NHS 맥락의 결과다.",
    ),
    "battilana-casciaro-2013": (
        "영국 NHS의 68개 변화 프로젝트에서 영향력 있는 경계인과의 강한 관계는 변화 채택과 정(+)의 관계를 보였다.",
        "명확한 저항자와의 관계강도는 주효과가 유의하지 않았고, 변화 괴리도가 낮을 때의 이점은 고괴리 조건에서 약해지거나 부정적으로 바뀔 수 있었다.",
        "이 연구는 관계 상대의 태도와 변화 괴리도를 함께 고려해야 함을 보이지만, 고괴리 조건의 부정적 단순기울기는 모형에 따라 한계적 유의성을 포함해 과장할 수 없다.",
    ),
}

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

V03_PACKAGE_FILES = (
    "research-model-v0.3.md",
    "construct-dictionary-v0.3.md",
    "proposition-traceability-v0.3.md",
    "pilot-protocol-and-codingbook-v0.3.md",
)

V03_CONSTRUCTS = (
    "실행된 역할 보완성",
    "활성화된 네트워크 연결성",
    "발언 안전성",
    "발언 효능감",
    "구성원 반응",
    "사건 지배 경로",
    "변화 발산성",
    "기초 네트워크 구조",
    "정책-실무 정합성",
    "책임 있는 AI 채택",
    "공식 리더",
    "비공식 AI 챔피언",
)

CONSTRUCT_FIELDS = (
    "분석 수준",
    "정의",
    "포함",
    "제외",
    "관찰 가능한 근거",
    "시간적 위치",
    "가장 가까운 경쟁 구성개념",
    "귀속 규칙",
)

PROPOSITION_FIELDS = (
    "직접 근거 출처",
    "통합 해석",
    "분석 수준",
    "자료원",
    "지지 패턴",
    "반증 패턴",
    "경쟁 설명",
    "연구 2 처분",
)

PROPOSITION_CARDS = {
    "P1": ("kemell-2025", "golgeci-2025"),
    "P2": ("golgeci-2025",),
    "P3": ("golgeci-2025", "neumann-2026"),
    "P4": ("kemell-2025", "neumann-2026"),
    "P5": ("golgeci-2025", "neumann-2026"),
    "P6": ("battilana-casciaro-2012",),
    "P7": ("battilana-casciaro-2013",),
}

PACKAGE_EVIDENCE_LABELS = (
    "논문 직접 근거",
    "통합 해석",
    "후속 연구 명제 (검증 전)",
)

PILOT_FIXED_CLAUSES = (
    "한 초점 사건에는 하나의 명부만 사용하며, 고유 인물 최대 8명으로 제한한다.",
    "각 alter마다 조언, 신뢰, 승인·예외, 위험 에스컬레이션 관계를 표시하고, 접촉 빈도, 지각된 신뢰, 공식 역할 속성은 한 번만 수집한다.",
    "alter-alter 관계는 초점 사건에서 핵심 인물 최대 5명 사이에서만 묻고, 무방향 쌍 최대 10개로 제한한다.",
    GUIDE_TIE_PROTOCOL,
    P5_RULE,
    "인터뷰와 관계망 조사 전에 IRB와 기업 보안·법무 승인을 완료한다.",
    "비응답 지명자는 역할 범주로만 분석하며 규정위반 행동은 개인 코드가 아니라 사건에만 귀속한다.",
    "연결코드 명부는 전사·코딩자료와 분리 암호화하고 연구책임자만 접근하며 분석 종료 시 폐기한다.",
    "재직·협력 관계를 위치성·이해상충 진술에 공개한다.",
    "참여자와 지휘·평가 관계가 없는 독립 모집 담당자가 모집과 동의 회수를 수행한다.",
    "고용주에게 원자료를 제공하지 않는다. 법률 또는 IRB 승인 안전절차의 공개 한계는 동의서에 사전 명시한다.",
)

DIVERGENCE_DIMENSION_CONTRACT = {
    "DV1": {
        "name": "업무 발산성",
        "probe_terms": ("개발·검토·배포 절차", "사건 전", "사건 후"),
        "source_terms": ("구성원", "공식 리더"),
        "corroboration_terms": ("업무 절차", "검토 체크리스트"),
    },
    "DV2": {
        "name": "전문성 발산성",
        "probe_terms": ("필요 지식", "직무 정체성", "숙련 가치"),
        "source_terms": ("구성원", "비공식 AI 챔피언"),
        "corroboration_terms": ("직무기술", "교육"),
    },
    "DV3": {
        "name": "권한 발산성",
        "probe_terms": ("판단·승인·예외·중단 권한", "누구에게서", "누구에게로"),
        "source_terms": ("공식 리더", "권한을 행사한 구성원"),
        "corroboration_terms": ("승인", "예외 기록"),
    },
    "DV4": {
        "name": "책임 발산성",
        "probe_terms": ("오류·품질·보안 책임", "검증 방식", "사건 전후"),
        "source_terms": ("책임자", "실무자"),
        "corroboration_terms": ("품질·보안 정책", "사후검토"),
    },
}

DIVERGENCE_DECISION_CONTRACT = {
    "고발산 후보": "서로 다른 두 차원 이상이 `경계 재구성`이고 각 차원이 교차확인되면 고발산 후보로 둔다.",
    "저발산 후보": "세 차원 이상이 `유지` 또는 `국소 조정`이고 `경계 재구성`이 없으며 각 차원이 교차확인되면 저발산 후보로 둔다.",
    "혼합": "한 차원만 `경계 재구성`이거나 차원별 방향이 엇갈리면 혼합으로 두고 차원 벡터를 그대로 보고한다.",
    "판정 유보": "교차확인된 차원이 세 개 미만이거나 핵심 자료가 충돌하면 판정을 유보하고 P6/P7 비교에 넣지 않는다.",
}

DIVERGENCE_USE_CONTRACT = {
    "고발산 후보": "P6의 경계 연결 조건과 P7의 고발산 입력 조건을 평가한다.",
    "저발산 후보": "P6의 내부 응집·강한 관계 조건을 평가하고 P7은 입력 불충족으로 기록한다.",
    "혼합": "P6는 차원별로 분기해 비교하고 P7은 고발산 입력이 별도 확인될 때만 평가한다.",
    "판정 유보": "P6/P7 판정을 모두 유보하고 추가 자료 또는 연구 2의 측정 정제를 기다린다.",
}

P6_NETWORK_CONTRACT = {
    "NC-B": (
        "경계 연결",
        "기능·부서 경계를 넘는 유향 관계에서 전달과 수신이 확인되고 EV6 검토·조정 전에 활성화됐다.",
        "관계 유형, 발신·수신 근거, 양쪽 기능·부서와 활성화 시점을 기록한다.",
    ),
    "NC-I": (
        "내부 응집·강한 관계 후보",
        "같은 팀의 핵심 인물 사이에서 상호 이름지목 또는 양측 수신 확인이 있고 반복 접촉이나 높은 지각 신뢰가 교차확인됐다.",
        "파일럿의 제한 명부를 팀 전체 응집성 점수로 간주하지 않고 사건 맥락 후보로 기록한다.",
    ),
}

P7_OUTCOME_CONTRACT = {
    "RP": (
        "관계압력",
        "기존 관계 때문에 동의·수용해야 한다는 의무감, 죄책감 또는 회피가 반복 설득 뒤 보고됐다.",
        "저항자 당사자 진술과 설득자 또는 독립 관찰자 진술을 교차확인한다.",
    ),
    "RD": (
        "관계 손상",
        "반복 설득 뒤 신뢰, 접촉 또는 협업이 사건 전보다 악화됐다.",
        "관계 양측 진술이나 승인 범위 안의 비식별 협업·접촉 근거를 교차확인한다.",
    ),
    "CE": (
        "챔피언 소진",
        "반복 설득 뒤 챔피언이 정서적 고갈, 역할 과부하 또는 활동 축소를 보고했다.",
        "챔피언 진술과 업무부담·활동 변화 자료를 연결하되 임상 진단으로 해석하지 않는다.",
    ),
}

P6_P7_DECISION_CONTRACT = {
    "P6": {
        "입력 조건": "EV2-D의 발산성 후보, EV3의 경계 연결 또는 내부 응집·강한 관계 후보, EV6-EV7의 조정 경로·후행 결과를 함께 본다.",
        "시간 순서": "EV2-D 사건 특성 → EV3 관계 활성화 → EV4-EV6 반응·경로 → EV7 실제 조정 결과 순서를 요구한다.",
        "필요한 교차자료": "발산성 교차확인 자료, 전달·수신이 확인된 유향 관계, 기능·부서 경계 또는 팀 내부 관계 속성, 조정 결과의 복수 진술·승인 문서를 연결한다.",
        "지지 후보": "고발산 후보에서 경계 연결이 먼저 활성화되어 조정으로 이어지거나, 저발산 후보에서 내부 응집·강한 관계가 먼저 활성화되어 조정으로 이어지는 대비가 확인된다.",
        "반증 후보": "충분한 자료에서 위 조합이 반복적으로 뒤집히거나 관계 조건과 조정 결과 사이에 시간적 연결이 없다.",
        "자료 부족·충돌": "발산성 판정 유보, 관계 전달·수신 미확인, 관계 유형 또는 결과의 자료 충돌이 있으면 P6 판정을 유보하고 평균·다수결로 해소하지 않는다.",
        "연구 1 명제 처분": "두 분기가 모두 반복되면 유지 후보, 한 분기만 확인되면 분기·수정 후보, 반전이 반복되면 기각 후보로 기록한다. 단일 사건은 명제를 유지하지 못한다.",
    },
    "P7": {
        "입력 조건": "EV2-D 고발산 후보, 첫 관계 기반 설득 전 당사자의 명시적 부정적 반대 또는 거절과 독립 자료로 교차확인된 명확한 저항자 태도, EV3 이후 두 차례 이상의 관계 기반 설득, 그 뒤 관계압력·관계 손상·챔피언 소진을 함께 본다.",
        "시간 순서": "고발산 판정 → 설득 전 저항자 태도 → 반복 설득 → 과정결과 순서를 요구하며 사후 태도로 초기 저항을 소급하지 않는다.",
        "필요한 교차자료": "저항자 당사자의 설득 전 명시적 부정적 반대 또는 거절 진술, 그 태도를 독립적으로 확인하는 동시기 문서·제3자 진술, 설득자·챔피언 진술, 반복 접촉 기록, 관계 양측 또는 독립 관찰자의 관계 변화 근거, 소진의 업무부담 자료를 연결한다.",
        "지지 후보": "교차확인된 고발산 사건에서 설득 전 명시적 부정적 반대 또는 거절이 독립 자료로 확인된 명확한 저항자에게 두 차례 이상 관계 기반 설득한 뒤 관계압력·손상 또는 챔피언 소진이 나타난다.",
        "반증 후보": "같은 입력과 순서에서 관계·자율성이 유지된 채 조정되거나, 결과가 반복 설득보다 먼저 발생하거나 저발산 사건에서만 반복된다.",
        "자료 부족·충돌": "설득 전 명시적 부정적 반대 또는 거절, 이를 확인할 독립 자료, 반복 횟수, 관계 결과의 시간 순서가 부족·충돌하면 P7 판정을 유보하며 보류를 명확한 저항으로 대체하거나 수신자 회피만으로 소진을 추정하지 않는다.",
        "연구 1 명제 처분": "결과가 반복되면 유지 후보, 압력·손상·소진 중 일부만 반복되면 분기·수정 후보, 충분한 반증이 반복되면 기각 후보로 기록한다. 단일 사건은 명제를 유지하지 못한다.",
    },
}

PRE_GATE_ALLOWED_PROHIBITIONS = {
    "G0·G1 승인 전에는 후보자를 모집·접촉하지 않는다.",
    "H1 동의 회수 전에는 인지면접을 시작하지 않는다.",
    "필요한 재승인 전에는 파일럿을 진행하지 않는다.",
}

ETHICS_STAGE_CONTRACT = (
    ("D0", ("지도교수", "근거상태")),
    ("G0", ("연구동의서", "철회", "익명화·연결코드", "사건·관계망 코딩북", "중단·보고")),
    ("G1", ("IRB", "기업 보안·법무·데이터 보호", "자료접근 협약", "서면 승인")),
    ("H1", ("G0와 G1", "독립 모집 담당자", "모집·접촉")),
    ("H2", ("G0·G1 승인", "H1 동의 회수", "인지면접", "각 1명씩 총 3명")),
    ("H3", ("G0·G1 승인", "H1 동의 회수", "파일럿", "필요한 재승인", "승인된 프로토콜")),
    ("A0", ("순차 혼합방법", "다중 사례연구", "사회연결망 분석")),
)


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


def markdown_section(text, heading):
    match = re.search(rf"^(#{{1,6}}) {re.escape(heading)}(?:\s|$)", text, re.MULTILINE)
    if not match:
        raise AssertionError(f"missing section: {heading}")
    level = len(match.group(1))
    following = re.search(rf"^#{{1,{level}}} ", text[match.end():], re.MULTILINE)
    end = match.end() + following.start() if following else len(text)
    return text[match.end():end]


def markdown_table_rows(text):
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = tuple(cell.strip() for cell in stripped[1:-1].split("|"))
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return tuple(rows)


def markdown_links(text):
    return tuple(re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", text))


def prose_paragraphs(text):
    paragraphs = []
    current = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if current:
                paragraphs.append(tuple(current))
                current = []
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        is_structure = (
            not stripped
            or stripped.startswith("#")
            or stripped.startswith("|")
            or stripped.startswith("- ")
            or re.match(r"^\\d+\\. ", stripped)
            or stripped in {"---", "***"}
        )
        if is_structure:
            if current:
                paragraphs.append(tuple(current))
                current = []
        else:
            current.append(line)
    if current:
        paragraphs.append(tuple(current))
    return tuple(paragraphs)


def numbered_steps(text):
    return tuple(
        (int(number), body.strip())
        for number, body in re.findall(r"^(\d+)\.\s+(.+)$", text, re.MULTILINE)
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
        self.assertEqual(
            tuple(line.strip() for line in by_heading["직접 근거"].splitlines() if line.strip()),
            (
                "**논문 직접 근거**",
                *(f"- {fact}" for fact in CARD_DIRECT_EVIDENCE_FACTS[slug]),
            ),
            f"{slug}: direct-evidence section contains non-canonical content",
        )
        for heading, clause in CARD_V03_REQUIREMENTS[slug]:
            self.assertIn(clause, by_heading[heading], f"{slug}: missing role contract in {heading}")

    def assert_divergence_measurement_contract(self, protocol):
        measurement = markdown_section(protocol, "변화 발산성의 사건 수준 측정")
        rows = markdown_table_rows(measurement)
        dimension_header = ("코드", "차원", "직접 탐침", "주 자료원", "교차확인")
        decision_header = ("사건 판정", "판정 규칙", "P6/P7 사용")
        self.assertIn(dimension_header, rows)
        self.assertIn(decision_header, rows)

        dimension_start = rows.index(dimension_header) + 1
        decision_start = rows.index(decision_header)
        dimension_rows = rows[dimension_start:decision_start]
        self.assertEqual(len(dimension_rows), 4)
        self.assertEqual({row[0] for row in dimension_rows}, set(DIVERGENCE_DIMENSION_CONTRACT))
        for row in dimension_rows:
            self.assertEqual(len(row), 5)
            code, name, probe, sources, corroboration = row
            contract = DIVERGENCE_DIMENSION_CONTRACT[code]
            self.assertEqual(name, contract["name"])
            for term in contract["probe_terms"]:
                self.assertIn(term, probe, f"{code}: incomplete direct probe")
            for term in contract["source_terms"]:
                self.assertIn(term, sources, f"{code}: incomplete source plan")
            for term in contract["corroboration_terms"]:
                self.assertIn(term, corroboration, f"{code}: incomplete corroboration plan")

        decision_rows = rows[decision_start + 1:]
        self.assertEqual({row[0] for row in decision_rows}, set(DIVERGENCE_DECISION_CONTRACT))
        for row in decision_rows:
            self.assertEqual(len(row), 3)
            self.assertEqual(row[1], DIVERGENCE_DECISION_CONTRACT[row[0]])
            self.assertEqual(row[2], DIVERGENCE_USE_CONTRACT[row[0]])

        for clause in (
            "각 차원은 `유지`, `국소 조정`, `경계 재구성`, `자료 부족`, `자료 충돌` 중 하나로 사건별 판정한다.",
            "같은 사람의 반복 진술은 하나의 자료원으로 센다.",
            "연구 1에서는 DV1-DV4를 합산하거나 평균하지 않고 차원 벡터로 보존한다.",
            "고발산·저발산은 측정척도가 아니라 위 규칙에 따른 질적 사례비교용 잠정 분류다.",
        ):
            self.assert_once(measurement, clause)

        event_rows = markdown_table_rows(markdown_section(protocol, "사건 코드"))
        divergence_event = tuple(row for row in event_rows if row and row[0] == "EV2-D 변화 발산성")
        self.assertEqual(len(divergence_event), 1)
        self.assertIn("DV1-DV4", divergence_event[0][1])
        self.assertIn("관계 동원 전", divergence_event[0][2])

        network_rows = markdown_table_rows(markdown_section(protocol, "P6 네트워크 조건"))
        self.assertEqual(network_rows[0], ("코드", "조건", "판정 규칙", "기록 경계"))
        self.assertEqual({row[0] for row in network_rows[1:]}, set(P6_NETWORK_CONTRACT))
        for row in network_rows[1:]:
            self.assertEqual(tuple(row[1:]), P6_NETWORK_CONTRACT[row[0]])

        outcome_rows = markdown_table_rows(markdown_section(protocol, "P7 과정결과"))
        self.assertEqual(outcome_rows[0], ("코드", "결과", "판정 규칙", "필요한 교차자료"))
        self.assertEqual({row[0] for row in outcome_rows[1:]}, set(P7_OUTCOME_CONTRACT))
        for row in outcome_rows[1:]:
            self.assertEqual(tuple(row[1:]), P7_OUTCOME_CONTRACT[row[0]])

        for proposition, contract in P6_P7_DECISION_CONTRACT.items():
            proposition_rows = markdown_table_rows(
                markdown_section(protocol, f"{proposition} 사건 판정")
            )
            self.assertEqual(proposition_rows[0], ("판정 항목", "사건 수준 규칙"))
            actual = {row[0]: row[1] for row in proposition_rows[1:] if len(row) == 2}
            self.assertEqual(actual, contract, f"{proposition}: incomplete decision path")

        p7_section = markdown_section(protocol, "P7 사건 판정")
        for clause in (
            "명확한 저항자 태도는 첫 관계 기반 설득 전에 당사자가 명시한 부정적 반대 또는 거절과 이를 뒷받침하는 독립 자료가 모두 있을 때만 코딩하며, 설득 뒤 태도로 소급하지 않는다.",
            "보류는 양가적 또는 미결 태도로 별도 코딩하며 명확한 저항자 입력에 포함하지 않는다.",
            "반복 관계 설득은 서로 다른 시점의 두 차례 이상 접촉으로 코딩하며 한 대화 안의 반복 표현은 한 차례로 센다.",
        ):
            self.assert_once(p7_section, clause)

    def assert_ethics_stage_ordering(self, matrix):
        next_steps = markdown_section(matrix, "13. 바로 다음 작업")
        steps = numbered_steps(next_steps)
        self.assertEqual(tuple(number for number, _ in steps), tuple(range(1, 8)))
        stage_bodies = {}
        stages = []
        for _, body in steps:
            match = re.match(r"`([A-Z]\d)`\s+", body)
            self.assertIsNotNone(match, f"missing stage identifier: {body}")
            stage = match.group(1)
            stages.append(stage)
            stage_bodies[stage] = body
        expected_stages = tuple(stage for stage, _ in ETHICS_STAGE_CONTRACT)
        self.assertEqual(tuple(stages), expected_stages)
        for stage, terms in ETHICS_STAGE_CONTRACT:
            for term in terms:
                self.assertIn(term, stage_bodies[stage], f"{stage}: missing ordering safeguard {term}")

        for human_stage in ("H1", "H2", "H3"):
            self.assertLess(stages.index("G0"), stages.index(human_stage))
            self.assertLess(stages.index("G1"), stages.index(human_stage))

        violation_markers = (
            "동의 회수 전",
            "동의 전",
            "동의 없이",
            "승인 전",
            "승인 없이",
            "재승인 전",
            "재승인 없이",
        )
        human_actions = ("모집", "접촉", "인지면접", "파일럿")
        for line in next_steps.splitlines():
            if not any(marker in line for marker in violation_markers):
                continue
            if not any(action in line for action in human_actions):
                continue
            instruction = re.sub(r"^(?:[-*]\s+|\d+\.\s+)", "", line.strip())
            self.assertIn(
                instruction,
                PRE_GATE_ALLOWED_PROHIBITIONS,
                f"pre-gate human-subject instruction: {line}",
            )

        sampling = section(matrix, "### 4.2 예비 표집")
        self.assertIn("G0 프로토콜 확정과 G1 서면 승인이 끝나기 전에는 후보 팀이나 개인을 모집·접촉하지 않는다.", sampling)

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

    def test_v03_card_contract_rejects_the_fabricated_kemell_randomized_37_percent_claim(self):
        path = ROOT / "site/downloads/kemell-2025/model-v0.3-contribution.md"
        text = path.read_text(encoding="utf-8")
        fabricated = "- 무작위 대조실험에서 생성형 AI가 개발자 생산성을 37% 높이는 인과효과가 확인됐다."
        mutated = text.replace(
            "## 직접 근거\n\n**논문 직접 근거**",
            f"## 직접 근거\n\n**논문 직접 근거**\n\n{fabricated}",
            1,
        )

        with self.assertRaises(AssertionError):
            self.assert_v03_card_contract("kemell-2025", mutated)

    def test_v03_card_contract_rejects_extra_direct_evidence_for_every_paper(self):
        for slug in CARD_DIRECT_EVIDENCE_FACTS:
            with self.subTest(slug=slug):
                path = ROOT / "site/downloads" / slug / "model-v0.3-contribution.md"
                text = path.read_text(encoding="utf-8")
                mutated = text.replace(
                    "## 직접 근거\n\n**논문 직접 근거**",
                    "## 직접 근거\n\n**논문 직접 근거**\n\n- 원 분석에 없는 추가 직접근거다.",
                    1,
                )
                with self.assertRaises(AssertionError):
                    self.assert_v03_card_contract(slug, mutated)

    def test_v03_card_contract_rejects_extra_direct_evidence_prose_for_every_paper(self):
        for slug in CARD_DIRECT_EVIDENCE_FACTS:
            with self.subTest(slug=slug):
                path = ROOT / "site/downloads" / slug / "model-v0.3-contribution.md"
                text = path.read_text(encoding="utf-8")
                mutated = text.replace(
                    "## 직접 근거\n\n**논문 직접 근거**",
                    "## 직접 근거\n\n**논문 직접 근거**\n\n원 분석에 없는 추가 직접근거다.",
                    1,
                )
                with self.assertRaises(AssertionError):
                    self.assert_v03_card_contract(slug, mutated)

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

    def public_v03_documents(self):
        base = ROOT / "site/downloads/research-design"
        paths = {name: base / name for name in V03_PACKAGE_FILES}
        for name, path in paths.items():
            self.assertTrue(path.is_file(), f"missing public v0.3 document: {name}")
        return {name: path.read_text(encoding="utf-8") for name, path in paths.items()}

    def assert_mobile_document_contract(self, name, text):
        for paragraph in prose_paragraphs(text):
            self.assertLess(
                len(paragraph),
                6,
                f"{name}: prose paragraph exceeds five lines: {paragraph!r}",
            )
        for row in markdown_table_rows(text):
            self.assertLess(
                len(row),
                6,
                f"{name}: table exceeds five columns: {row!r}",
            )

    def assert_relative_links_resolve(self, path, text):
        for target in markdown_links(text):
            href = target.split("#", 1)[0]
            if not href or "://" in href or href.startswith("mailto:"):
                continue
            target_path = Path(href)
            self.assertFalse(target_path.is_absolute(), f"{path.name}: non-relative link {target}")
            self.assertTrue(
                (path.parent / target_path).is_file(),
                f"{path.name}: broken local link {target}",
            )

    def test_public_v03_package_is_complete_and_cross_linked(self):
        documents = self.public_v03_documents()
        paths = {
            name: ROOT / "site/downloads/research-design" / name
            for name in V03_PACKAGE_FILES
        }
        for name, text in documents.items():
            for label in PACKAGE_EVIDENCE_LABELS:
                self.assertIn(label, text, f"{name}: missing evidence-status label {label}")
            self.assertIn("P1-P7", text, f"{name}: missing P1-P7 boundary")
            self.assertIn("검증 전", text, f"{name}: missing verification boundary")
            self.assert_relative_links_resolve(paths[name], text)
            targets = {target.split("#", 1)[0] for target in markdown_links(text)}
            for peer in V03_PACKAGE_FILES:
                if peer != name:
                    self.assertIn(peer, targets, f"{name}: missing package link to {peer}")

        traceability = documents["proposition-traceability-v0.3.md"]
        trace_targets = set(markdown_links(traceability))
        for slugs in PROPOSITION_CARDS.values():
            for slug in slugs:
                expected = f"../{slug}/model-v0.3-contribution.md"
                self.assertIn(expected, trace_targets, f"traceability: missing contribution-card link {expected}")

    def test_public_v03_documents_are_mobile_readable_and_reject_a_wide_table(self):
        documents = self.public_v03_documents()
        for name, text in documents.items():
            self.assert_mobile_document_contract(name, text)

        mutated = documents["research-model-v0.3.md"] + "\n| A | B | C | D | E | F |\n| --- | --- | --- | --- | --- | --- |\n"
        with self.assertRaises(AssertionError):
            self.assert_mobile_document_contract("mutated", mutated)

    def test_construct_dictionary_has_a_complete_card_for_every_construct(self):
        dictionary = self.public_v03_documents()["construct-dictionary-v0.3.md"]
        for construct in V03_CONSTRUCTS:
            construct_section = markdown_section(dictionary, construct)
            labels = {row[0] for row in markdown_table_rows(construct_section) if len(row) == 2}
            self.assertTrue(
                set(CONSTRUCT_FIELDS).issubset(labels),
                f"{construct}: missing dictionary fields {set(CONSTRUCT_FIELDS) - labels}",
            )

        mutated = markdown_section(dictionary, "실행된 역할 보완성").replace(
            "| 귀속 규칙 |", "| 판정 규칙 |", 1
        )
        labels = {row[0] for row in markdown_table_rows(mutated) if len(row) == 2}
        self.assertFalse(set(CONSTRUCT_FIELDS).issubset(labels))

    def test_proposition_traceability_has_all_required_rows_and_card_links(self):
        traceability = self.public_v03_documents()["proposition-traceability-v0.3.md"]
        for proposition, slugs in PROPOSITION_CARDS.items():
            proposition_section = markdown_section(traceability, proposition)
            self.assertIn("**상태:** 후속 연구 명제 (검증 전)", proposition_section)
            labels = {row[0] for row in markdown_table_rows(proposition_section) if len(row) == 2}
            self.assertTrue(
                set(PROPOSITION_FIELDS).issubset(labels),
                f"{proposition}: missing traceability fields {set(PROPOSITION_FIELDS) - labels}",
            )
            for slug in slugs:
                self.assertIn(f"../{slug}/model-v0.3-contribution.md", proposition_section)

        mutated = markdown_section(traceability, "P1").replace("| 연구 2 처분 |", "| 연구 2 상태 |", 1)
        labels = {row[0] for row in markdown_table_rows(mutated) if len(row) == 2}
        self.assertFalse(set(PROPOSITION_FIELDS).issubset(labels))

    def test_pilot_protocol_preserves_operational_and_safety_contracts(self):
        protocol = self.public_v03_documents()["pilot-protocol-and-codingbook-v0.3.md"]
        agenda_section = markdown_section(protocol, "60분 진행 순서")
        agenda_match = re.search(r"```text\n(.*?)\n```", agenda_section, re.DOTALL)
        self.assertIsNotNone(agenda_match, "missing fixed 60-minute agenda block")
        agenda = tuple(
            (label.strip(), int(minutes))
            for label, minutes in re.findall(r"([^|\n]+?)\s+(\d+)분", agenda_match.group(1))
        )
        self.assertEqual(agenda, AGENDA)
        self.assertEqual(sum(minutes for _, minutes in agenda), 60)
        for clause in PILOT_FIXED_CLAUSES:
            self.assert_once(protocol, clause)
        for relation in ("조언", "신뢰", "승인·예외", "위험 에스컬레이션"):
            self.assertIn(relation, protocol)
        for heading in ("사건 코드", "부정 사례 로그", "동의·철회", "중단 조건"):
            self.assertIn(heading, protocol)
        self.assertIn("인터뷰, 모집, 이름 생성, 조직 자료 수집은 시작하지 않았다.", protocol)
        self.assertIn("NotebookLM 산출물은 근거로 사용하지 않는다.", protocol)

        mutated = protocol.replace("무방향 쌍 최대 10개", "무방향 쌍 최대 12개", 1)
        with self.assertRaises(AssertionError):
            for clause in PILOT_FIXED_CLAUSES:
                self.assert_once(mutated, clause)

    def test_change_divergence_has_a_complete_event_measurement_path(self):
        protocol = self.public_v03_documents()["pilot-protocol-and-codingbook-v0.3.md"]
        self.assert_divergence_measurement_contract(protocol)

        missing_dimension = protocol.replace(
            "| DV4 | 책임 발산성 |", "| DX4 | 책임 변화 |", 1
        )
        with self.assertRaises(AssertionError):
            self.assert_divergence_measurement_contract(missing_dimension)

        weakened_decision = protocol.replace(
            "서로 다른 두 차원 이상이 `경계 재구성`", "한 차원이 `경계 재구성`", 1
        )
        with self.assertRaises(AssertionError):
            self.assert_divergence_measurement_contract(weakened_decision)

        deleted_use_path = protocol
        for original in DIVERGENCE_USE_CONTRACT.values():
            deleted_use_path = deleted_use_path.replace(original, "P6/P7 사용 경로 삭제")
        with self.assertRaises(AssertionError):
            self.assert_divergence_measurement_contract(deleted_use_path)

        p6_support = P6_P7_DECISION_CONTRACT["P6"]["지지 후보"]
        p7_support = P6_P7_DECISION_CONTRACT["P7"]["지지 후보"]
        exchanged = protocol.replace(p6_support, "__P6_SUPPORT__", 1)
        exchanged = exchanged.replace(p7_support, p6_support, 1)
        exchanged = exchanged.replace("__P6_SUPPORT__", p7_support, 1)
        with self.assertRaises(AssertionError):
            self.assert_divergence_measurement_contract(exchanged)

        reversed_outcome = protocol.replace(
            "경계 연결이 먼저 활성화되어 조정으로 이어지거나",
            "경계 연결이 먼저 활성화되어 조정에 실패하거나",
            1,
        )
        with self.assertRaises(AssertionError):
            self.assert_divergence_measurement_contract(reversed_outcome)

        clear_resistor_including_hold = protocol.replace(
            "당사자가 명시한 부정적 반대 또는 거절과 이를 뒷받침하는 독립 자료",
            "당사자가 명시한 반대·거절·보류와 이를 뒷받침하는 독립 자료",
            1,
        )
        with self.assertRaises(AssertionError):
            self.assert_divergence_measurement_contract(clear_resistor_including_hold)

    def test_matrix_requires_ethics_gates_before_any_human_contact(self):
        self.assert_ethics_stage_ordering(MATRIX)

        next_steps = markdown_section(MATRIX, "13. 바로 다음 작업")
        lines = next_steps.splitlines()
        cognitive_index = next(index for index, line in enumerate(lines) if "`H2`" in line)
        approval_index = next(index for index, line in enumerate(lines) if "`G1`" in line)
        lines[cognitive_index], lines[approval_index] = lines[approval_index], lines[cognitive_index]
        mutated = MATRIX.replace(next_steps, "\n".join(lines), 1)
        with self.assertRaises(AssertionError):
            self.assert_ethics_stage_ordering(mutated)

        preconsent_interview = MATRIX.replace(
            "각 1명씩 총 3명에게 인지면접을 하고",
            "각 1명씩 총 3명에게 동의 회수 전에 인지면접을 하고",
            1,
        )
        with self.assertRaises(AssertionError):
            self.assert_ethics_stage_ordering(preconsent_interview)

        for contradiction in (
            "승인 전에 후보자를 모집·접촉한다.",
            "재승인 전에 파일럿을 진행한다.",
            "승인 전에 파일럿을 중단하지 않는다.",
        ):
            contradicted = MATRIX.replace(next_steps, next_steps + "\n" + contradiction, 1)
            with self.assertRaises(AssertionError):
                self.assert_ethics_stage_ordering(contradicted)

        for prohibition in PRE_GATE_ALLOWED_PROHIBITIONS:
            prohibited = MATRIX.replace(next_steps, next_steps + "\n" + prohibition, 1)
            self.assert_ethics_stage_ordering(prohibited)
