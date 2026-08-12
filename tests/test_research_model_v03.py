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
