"""Regression coverage for signed task XP and negative daily totals."""
import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import openpyxl
import pytest

from ma_log_pdf_parser.course_parser import CourseProgressParser


@pytest.fixture
def parser(tmp_path):
    pdf = tmp_path / "synthetic.pdf"
    pdf.touch()
    return CourseProgressParser(str(pdf))


@pytest.mark.parametrize("cell, expected", [
    ("-4/4 XP", (-4, 4, "-4/4")),
    ("-1/4 XP", (-1, 4, "-1/4")),
    ("0/4 XP", (0, 4, "0/4")),
    ("6/4 XP", (6, 4, "6/4")),
    ("35/ XP", (35, 35, "35/")),
    ("-3/ XP", (-3, -3, "-3/")),
])
def test_signed_xp_cells(parser, cell, expected):
    assert parser._parse_xp_cell(cell) == expected


def test_fallback_keeps_negative_daily_total_and_clean_description(parser):
    rows = parser._parse_text_block("\n".join([
        "Mon, Oct 26th, 2026 (-4 XP)",
        "Algebra Review Synthetic review -4/4 XP",
        "Tue, Oct 27th, 2026 (6 XP)",
        "Algebra Review Synthetic bonus 6/4 XP",
    ]))
    assert [(r["Date"], r["XP Earned"], r["Daily Total XP"])
            for r in rows] == [("2026-10-26", -4, -4),
                               ("2026-10-27", 6, 6)]
    assert rows[0]["Description"] == "Synthetic review"
    assert rows[0]["XP Detail"] == "-4/4"


def test_fallback_negative_placement(parser):
    rows = parser._parse_text_block(
        "Mon, Oct 26th, 2026 (-3 XP)\nAlgebra Placement -3/ XP")
    assert len(rows) == 1
    assert rows[0]["XP Earned"] == -3
    assert rows[0]["XP Detail"] == "-3/"
    assert rows[0]["Daily Total XP"] == -3


def table_page(header, description, xp):
    page = MagicMock()
    page.extract_words.return_value = [
        {"text": word, "top": 10, "x0": i * 60}
        for i, word in enumerate(header.split())
    ]
    page.find_tables.return_value = [SimpleNamespace(
        rows=[SimpleNamespace(bbox=(0, 50, 500, 70))])]
    page.extract_tables.return_value = [
        [["Algebra", "Review", description, xp]]]
    return page


def test_table_pdf_to_exports_preserves_signed_totals(parser, tmp_path):
    document = MagicMock()
    document.__enter__.return_value.pages = [
        table_page("Mon, Oct 26th, 2026 (-4 XP)", "Synthetic penalty", "-4/4 XP"),
        table_page("Tue, Oct 27th, 2026 (6 XP)", "Synthetic bonus", "6/4 XP"),
    ]
    with patch("ma_log_pdf_parser.course_parser.pdfplumber.open",
               return_value=document):
        rows = parser.parse_course_data()
    assert [r["XP Earned"] for r in rows] == [-4, 6]
    assert [r["Date"] for r in rows] == ["2026-10-26", "2026-10-27"]
    assert [r["Daily Total XP"] for r in rows] == [-4, 6]

    json_path = tmp_path / "result.json"
    excel_path = tmp_path / "result.xlsx"
    parser.export_to_json(str(json_path), rows)
    parser.export_to_excel(str(excel_path), rows)
    exported = json.loads(json_path.read_text())
    assert exported["statistics"]["total_xp"] == 2
    assert exported["statistics"]["daily_breakdown"]["2026-10-26"]["total_xp"] == -4
    assert exported["statistics"]["course_breakdown"]["Algebra"]["xp"] == 2
    assert exported["statistics"]["task_type_breakdown"]["Review"]["xp"] == 2
    assert exported["activities"][0]["XP Detail"] == "-4/4"

    workbook = openpyxl.load_workbook(excel_path, read_only=True)
    try:
        sheet = workbook["Course Progress"]
        values = list(sheet.values)
        headers = list(values[0])
        earned_index = headers.index("XP Earned")
        detail_index = headers.index("XP Detail")
        assert [r[earned_index] for r in values[1:]] == [-4, 6]
        assert values[1][detail_index] == "-4/4"
    finally:
        workbook.close()
