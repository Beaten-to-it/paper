import importlib
import importlib.util
import re
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urljoin, urlparse

from openpyxl import load_workbook
from PIL import Image, ImageChops
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pypdf import PdfReader

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
RELATION_TYPES = ["advice", "trust", "approval_exception", "risk_escalation"]
RELATION_EVIDENCE_SUFFIXES = [
    "sender_report_delivery",
    "receipt_confirmation_evidence",
    "recipient_stance",
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

    def test_relation_sheet_preserves_delivery_receipt_and_stance_per_relation(self):
        with TemporaryDirectory() as tmp:
            path, workbook = self.build(tmp)
            worksheet = workbook["관계망"]
            relation_headers = headers(worksheet)

            expected_evidence_columns = [
                f"{relation}_{suffix}"
                for relation in RELATION_TYPES
                for suffix in RELATION_EVIDENCE_SUFFIXES
            ]
            self.assertTrue(set(expected_evidence_columns).issubset(relation_headers))
            self.assertFalse(set(RELATION_EVIDENCE_SUFFIXES).intersection(relation_headers))
            self.assertEqual(len(set(expected_evidence_columns)), 12)

            values = {
                "event_code": "EV-TEST",
                "respondent_code": "R-TEST",
                "alter_code": "A-TEST",
                "advice_relation": True,
                "trust_relation": True,
                "advice_sender_report_delivery": "조언 전달 보고",
                "advice_receipt_confirmation_evidence": "조언 수신 확인",
                "advice_recipient_stance": "수용",
                "trust_sender_report_delivery": "신뢰 전달 보고",
                "trust_receipt_confirmation_evidence": "신뢰 수신 미확인",
                "trust_recipient_stance": "보류",
            }
            for column_name, value in values.items():
                worksheet.cell(row=2, column=relation_headers.index(column_name) + 1).value = value
            workbook.save(path)

            rebuilt = load_workbook(path, read_only=False, data_only=False)["관계망"]
            saved = dict(zip(headers(rebuilt), [cell.value for cell in rebuilt[2]]))
            for column_name, value in values.items():
                self.assertEqual(saved[column_name], value)
            self.assertNotEqual(
                saved["advice_receipt_confirmation_evidence"],
                saved["trust_receipt_confirmation_evidence"],
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

    def test_dense_research_sheets_use_readable_multi_page_print_layouts(self):
        with TemporaryDirectory() as tmp:
            _, workbook = self.build(tmp)

            title_columns = {
                "구성개념": "$A:$A",
                "명제추적": "$A:$A",
                "논문별기여": "$A:$A",
                "관계망": "$A:$D",
            }
            for sheet_name, expected_title_columns in title_columns.items():
                worksheet = workbook[sheet_name]
                self.assertFalse(worksheet.sheet_properties.pageSetUpPr.fitToPage, sheet_name)
                self.assertIsNone(worksheet.page_setup.fitToWidth, sheet_name)
                self.assertIsNone(worksheet.page_setup.fitToHeight, sheet_name)
                self.assertEqual(worksheet.page_setup.scale, 100, sheet_name)
                self.assertEqual(str(worksheet.page_setup.paperSize), str(worksheet.PAPERSIZE_A3), sheet_name)
                self.assertEqual(worksheet.page_setup.orientation, worksheet.ORIENTATION_LANDSCAPE, sheet_name)
                self.assertEqual(worksheet.print_title_rows, "$1:$1", sheet_name)
                self.assertEqual(worksheet.print_title_cols, expected_title_columns, sheet_name)

    def test_validations_and_paper_lab_links_are_operational(self):
        with TemporaryDirectory() as tmp:
            path, workbook = self.build(tmp)

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
                parsed = urlparse(target)
                self.assertEqual((parsed.scheme, parsed.netloc), ("https", "beaten-to-it.github.io"), target)
                self.assertTrue(parsed.path.startswith("/paper/downloads/"), target)
                self.assertEqual(urljoin(path.as_uri(), target), target, target)
                source = ROOT / "site" / unquote(parsed.path.removeprefix("/paper/"))
                self.assertTrue(source.is_file(), target)

    def test_boolean_relation_validation_uses_stop_error_alerts(self):
        with TemporaryDirectory() as tmp:
            _, workbook = self.build(tmp)
            validations = workbook["관계망"].data_validations.dataValidation

            self.assertEqual(len(validations), 1)
            validation = validations[0]
            self.assertEqual(validation.formula1, '"TRUE,FALSE"')
            self.assertEqual(
                {str(cell_range) for cell_range in validation.ranges.ranges},
                {"E2:E500", "F2:F500", "G2:G500", "H2:H500"},
            )
            self.assertTrue(validation.showErrorMessage)
            self.assertEqual(validation.errorStyle, "stop")
            self.assertEqual(validation.errorTitle, "허용되지 않은 관계 값")
            self.assertIn("TRUE 또는 FALSE", validation.error)

    def test_rebuild_has_stable_structural_values(self):
        with TemporaryDirectory() as tmp:
            _, first = self.build(tmp, "first.xlsx")
            _, second = self.build(tmp, "second.xlsx")

            self.assertEqual(workbook_snapshot(first), workbook_snapshot(second))

    def test_v03_visual_package_is_editable_sourced_and_claim_safe(self):
        module_name = "tools.build_research_model_v03_media"
        self.assertIsNotNone(
            importlib.util.find_spec(module_name),
            "The v0.3 media builder is not implemented.",
        )
        build_media = importlib.import_module(module_name).build_media

        with TemporaryDirectory() as tmp:
            diagram_path = Path(tmp) / "model.png"
            deck_path = Path(tmp) / "deck.pptx"
            build_media(diagram_path, deck_path)
            second_diagram_path = Path(tmp) / "model-second.png"
            second_deck_path = Path(tmp) / "deck-second.pptx"
            build_media(second_diagram_path, second_deck_path)

            with Image.open(diagram_path) as diagram:
                self.assertEqual(diagram.size, (2400, 1600))
                nonwhite = ImageChops.difference(diagram.convert("RGB"), Image.new("RGB", diagram.size, "white"))
                content_bounds = nonwhite.getbbox()
                self.assertIsNotNone(content_bounds)
                left, top, right, bottom = content_bounds
                self.assertGreaterEqual(min(left, top, 2400 - right, 1600 - bottom), 20)
            self.assertEqual(diagram_path.read_bytes(), second_diagram_path.read_bytes())
            self.assertEqual(deck_path.read_bytes(), second_deck_path.read_bytes())

            deck = Presentation(deck_path)
            self.assertEqual(len(deck.slides), 12)
            slide_texts = [
                "\n".join(
                    shape.text
                    for shape in slide.shapes
                    if getattr(shape, "has_text_frame", False)
                )
                for slide in deck.slides
            ]
            all_text = "\n".join(slide_texts)

            for phrase in (
                "역할 보완성",
                "네트워크 연결성",
                "발언 안전성",
                "발언 효능감",
                "변화 발산성",
                "검증 전 명제",
            ):
                self.assertIn(phrase, all_text)
            self.assertIn("NotebookLM 산출물은 근거가 아니다", all_text)
            self.assertIn("현장조사는 시작하지 않았다", all_text)
            self.assertIsNone(re.search(r"검증됐다|입증됐다", all_text))

            for index, slide in enumerate(deck.slides, start=1):
                source_notes = slide.notes_slide.notes_text_frame.text
                self.assertRegex(source_notes, r"(?s)\[Sources\]\s*\n\S+", f"slide {index}")
                for shape in slide.shapes:
                    self.assertGreaterEqual(shape.left, 0, f"slide {index}: {shape.name}")
                    self.assertGreaterEqual(shape.top, 0, f"slide {index}: {shape.name}")
                    self.assertGreaterEqual(
                        shape.left,
                        457200,
                        f"slide {index}: {shape.name} violates the 0.5-inch left safe area",
                    )
                    self.assertLessEqual(
                        shape.left + shape.width,
                        deck.slide_width,
                        f"slide {index}: {shape.name}",
                    )
                    self.assertLessEqual(
                        shape.left + shape.width,
                        deck.slide_width - 457200,
                        f"slide {index}: {shape.name} violates the 0.5-inch right safe area",
                    )
                    self.assertLessEqual(
                        shape.top + shape.height,
                        deck.slide_height,
                        f"slide {index}: {shape.name}",
                    )
                editable_shapes = [
                    shape
                    for shape in slide.shapes
                    if shape.shape_type in (MSO_SHAPE_TYPE.AUTO_SHAPE, MSO_SHAPE_TYPE.TEXT_BOX)
                    and getattr(shape, "has_text_frame", False)
                ]
                self.assertGreaterEqual(len(editable_shapes), 3, f"slide {index}")

            proposition_slide = slide_texts[9]
            for proposition in (f"P{number}" for number in range(1, 8)):
                self.assertIn(proposition, proposition_slide)
            self.assertIn("검증 전 명제", proposition_slide)

    def test_v03_pdf_export_has_twelve_pages_when_libreoffice_is_available(self):
        module_name = "tools.build_research_model_v03_media"
        self.assertIsNotNone(importlib.util.find_spec(module_name))
        build_media = importlib.import_module(module_name).build_media
        soffice = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
        if not soffice.is_file():
            self.skipTest("LibreOffice is not installed")

        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            deck_path = tmp_path / "deck.pptx"
            build_media(tmp_path / "model.png", deck_path)
            profile = tmp_path / "lo-profile"
            result = subprocess.run(
                [
                    str(soffice),
                    "--headless",
                    f"-env:UserInstallation={profile.resolve().as_uri()}",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(tmp_path),
                    str(deck_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            pdf_path = deck_path.with_suffix(".pdf")
            self.assertTrue(pdf_path.is_file(), result.stderr or result.stdout)
            self.assertEqual(len(PdfReader(pdf_path).pages), 12)


if __name__ == "__main__":
    unittest.main()
