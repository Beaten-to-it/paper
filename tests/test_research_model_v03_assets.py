import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from openpyxl import load_workbook

from tools.build_research_model_v03_workbook import build_workbook


ROOT = Path(__file__).resolve().parents[1]
SHEET_ORDER = [
    "README",
    "구성개념",
    "명제추적",
    "논문별기여",
    "사건코딩",
    "관계망",
    "부정사례",
    "윤리체크",
]
EVENT_COLUMNS = [
    "event_code",
    "actor_role",
    "trigger",
    "threat",
    "role_complementarity",
    "activated_connectivity",
    "voice_safety",
    "voice_efficacy",
    "response_codes",
    "dominant_path",
    "substantive_handling",
    "problem_resolution",
    "rival_explanation",
    "negative_case",
]
RELATION_BOOLEAN_COLUMNS = [
    "advice_relation",
    "trust_relation",
    "approval_exception_relation",
    "risk_escalation_relation",
]


def headers(worksheet):
    return [cell.value for cell in worksheet[1]]


def workbook_snapshot(workbook):
    return tuple(
        (
            worksheet.title,
            worksheet.freeze_panes,
            worksheet.auto_filter.ref,
            tuple(tuple(cell.value for cell in row) for row in worksheet.iter_rows()),
            tuple(
                (cell.coordinate, cell.hyperlink.target)
                for row in worksheet.iter_rows()
                for cell in row
                if cell.hyperlink
            ),
            tuple(
                (validation.type, validation.formula1, str(validation.sqref))
                for validation in worksheet.data_validations.dataValidation
            ),
        )
        for worksheet in workbook.worksheets
    )


class ResearchModelV03AssetTests(unittest.TestCase):
    def build(self, directory, name="workbook.xlsx"):
        path = Path(directory) / name
        build_workbook(path)
        return path, load_workbook(path, read_only=False, data_only=False)

    def test_v03_workbook_structure(self):
        with TemporaryDirectory() as tmp:
            _, workbook = self.build(tmp)

            self.assertEqual(workbook.sheetnames, SHEET_ORDER)
            self.assertEqual(workbook["구성개념"].max_row, 13)
            self.assertEqual(workbook["명제추적"].max_row, 8)
            self.assertEqual(workbook["논문별기여"].max_row, 6)
            self.assertEqual(
                [workbook["명제추적"].cell(row=row, column=1).value for row in range(2, 9)],
                [f"P{number}" for number in range(1, 8)],
            )
            self.assertEqual(
                {workbook["명제추적"].cell(row=row, column=3).value for row in range(2, 9)},
                {"검증 전"},
            )
            self.assertIn("실행된 역할 보완성", {cell.value for cell in workbook["구성개념"]["A"]})
            self.assertIn("Kemell et al. (2025)", {cell.value for cell in workbook["논문별기여"]["A"]})

    def test_blank_templates_preserve_event_and_network_boundaries(self):
        with TemporaryDirectory() as tmp:
            _, workbook = self.build(tmp)

            self.assertEqual(headers(workbook["사건코딩"]), EVENT_COLUMNS)
            self.assertEqual(workbook["사건코딩"].max_row, 1)

            relation_headers = headers(workbook["관계망"])
            self.assertEqual(relation_headers[:4], ["event_code", "respondent_code", "alter_code", "alter_role_category"])
            self.assertEqual(
                [column for column in relation_headers if column in RELATION_BOOLEAN_COLUMNS],
                RELATION_BOOLEAN_COLUMNS,
            )
            self.assertEqual(workbook["관계망"].max_row, 1)
            self.assertNotIn("real_name", relation_headers)
            self.assertFalse(any("실명" in str(value) or "name" == str(value).lower() for value in relation_headers))

            self.assertEqual(workbook["부정사례"].max_row, 1)
            self.assertTrue(
                all(
                    cell.value in (None, "")
                    for row in workbook["윤리체크"].iter_rows(min_row=2)
                    for cell in row[2:5]
                )
            )

    def test_headers_filters_freeze_panes_and_layout_are_usable(self):
        with TemporaryDirectory() as tmp:
            _, workbook = self.build(tmp)

            for worksheet in workbook.worksheets:
                self.assertEqual(worksheet.freeze_panes, "A2", worksheet.title)
                self.assertEqual(
                    worksheet.auto_filter.ref,
                    f"A1:{worksheet.cell(row=worksheet.max_row, column=worksheet.max_column).coordinate}",
                    worksheet.title,
                )
                self.assertFalse(worksheet.sheet_view.showGridLines, worksheet.title)
                for cell in worksheet[1]:
                    self.assertEqual(cell.fill.fgColor.rgb, "FF17365D", f"{worksheet.title}!{cell.coordinate}")
                    self.assertEqual(cell.font.name, "Malgun Gothic", f"{worksheet.title}!{cell.coordinate}")
                    self.assertTrue(cell.alignment.wrap_text, f"{worksheet.title}!{cell.coordinate}")
                    width = worksheet.column_dimensions[cell.column_letter].width
                    self.assertGreaterEqual(width, 12, f"{worksheet.title}!{cell.column_letter}")
                    self.assertLessEqual(width, 60, f"{worksheet.title}!{cell.column_letter}")
            self.assertEqual(workbook["README"]["A2"].fill.fgColor.rgb, "FFEAF2F8")

    def test_validations_and_paper_lab_links_are_operational(self):
        with TemporaryDirectory() as tmp:
            _, workbook = self.build(tmp)

            proposition_validations = workbook["명제추적"].data_validations.dataValidation
            self.assertEqual(len(proposition_validations), 2)
            self.assertEqual(
                {validation.formula1 for validation in proposition_validations},
                {'"검증 전,수정,분기,기각"', '"미검토,유지,수정,분기,기각"'},
            )
            self.assertEqual(
                {validation.formula1 for validation in workbook["관계망"].data_validations.dataValidation},
                {'"TRUE,FALSE"'},
            )
            self.assertEqual(
                {validation.formula1 for validation in workbook["부정사례"].data_validations.dataValidation},
                {'"미검토,유지,수정,분기,기각"'},
            )

            links = [
                cell.hyperlink.target
                for sheet_name in ("README", "구성개념", "명제추적", "논문별기여", "윤리체크")
                for row in workbook[sheet_name].iter_rows()
                for cell in row
                if cell.hyperlink
            ]
            self.assertGreaterEqual(len(links), 29)
            for target in links:
                self.assertTrue(target.startswith("../../site/downloads/"), target)
                expected = ROOT / "output/release-assets" / target
                self.assertTrue(expected.resolve().is_file(), target)

    def test_rebuild_has_stable_structural_values(self):
        with TemporaryDirectory() as tmp:
            _, first = self.build(tmp, "first.xlsx")
            _, second = self.build(tmp, "second.xlsx")

            self.assertEqual(workbook_snapshot(first), workbook_snapshot(second))


if __name__ == "__main__":
    unittest.main()
