from __future__ import annotations

import argparse
import csv
import html
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMATIC = ROOT / "ADE9000_Breakout.kicad_sch"
DEFAULT_CSV = ROOT / "bom" / "ADE9000_Breakout_BOM.csv"
DEFAULT_XLSX = ROOT / "bom" / "ADE9000_Breakout_BOM.xlsx"

FIELDS = [
    "Line",
    "Quantity",
    "References",
    "Value",
    "Footprint",
    "Manufacturer",
    "MPN",
    "DigiKey",
    "Mouser",
    "Description",
]


def natural_ref_key(ref: str) -> tuple[str, int, str]:
    match = re.match(r"([A-Za-z]+)(\d+)(.*)", ref)
    if not match:
        return (ref, 0, "")
    return (match.group(1), int(match.group(2)), match.group(3))


def iter_symbol_blocks(text: str):
    position = 0
    while True:
        start = text.find("(symbol ", position)
        if start < 0:
            break
        depth = 0
        for end in range(start, len(text)):
            if text[end] == "(":
                depth += 1
            elif text[end] == ")":
                depth -= 1
                if depth == 0:
                    yield text[start : end + 1]
                    position = end + 1
                    break


def unescape(value: str) -> str:
    return value.replace('\\"', '"').replace('\\\\', '\\')


def properties(block: str) -> dict[str, str]:
    props: dict[str, str] = {}
    for match in re.finditer(r'\(property "([^"\\]*(?:\\.[^"\\]*)*)" "([^"\\]*(?:\\.[^"\\]*)*)"', block):
        props[unescape(match.group(1))] = unescape(match.group(2))
    return props


def load_rows(schematic: Path) -> list[dict[str, str]]:
    text = schematic.read_text()
    grouped: dict[tuple[str, str, str, str, str, str, str, str], list[str]] = defaultdict(list)

    for block in iter_symbol_blocks(text):
        if "(instances " not in block:
            continue
        props = properties(block)
        ref = props.get("Reference", "")
        if not ref or ref.startswith("#"):
            continue
        if props.get("Exclude from BOM", "").lower() in {"yes", "true", "1"}:
            continue
        key = (
            props.get("Value", ""),
            props.get("Footprint", ""),
            props.get("Manufacturer", ""),
            props.get("MPN", ""),
            props.get("DigiKey", ""),
            props.get("Mouser", ""),
            props.get("Description", ""),
            props.get("DNP", ""),
        )
        grouped[key].append(ref)

    rows: list[dict[str, str]] = []
    for line, (key, refs) in enumerate(sorted(grouped.items(), key=lambda item: natural_ref_key(sorted(item[1], key=natural_ref_key)[0])), start=1):
        value, footprint, manufacturer, mpn, digikey, mouser, description, dnp = key
        sorted_refs = sorted(refs, key=natural_ref_key)
        rows.append(
            {
                "Line": str(line),
                "Quantity": str(len(sorted_refs)),
                "References": ", ".join(sorted_refs),
                "Value": value,
                "Footprint": footprint,
                "Manufacturer": manufacturer,
                "MPN": mpn,
                "DigiKey": digikey,
                "Mouser": mouser,
                "Description": description,
            }
        )

    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as bom_file:
        writer = csv.DictWriter(bom_file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def cell_xml(row: int, column: int, value: str) -> str:
    ref = f"{column_name(column)}{row}"
    return f'<c r="{ref}" t="inlineStr"><is><t>{xml_escape(value)}</t></is></c>'


def sheet_xml(rows: list[dict[str, str]]) -> str:
    sheet_rows = []
    all_rows = [dict(zip(FIELDS, FIELDS, strict=True)), *rows]
    for row_index, row in enumerate(all_rows, start=1):
        cells = "".join(cell_xml(row_index, column_index, row.get(field, "")) for column_index, field in enumerate(FIELDS, start=1))
        sheet_rows.append(f'<row r="{row_index}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheetData>'
        + "".join(sheet_rows)
        + '</sheetData></worksheet>'
    )


def write_xlsx(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as xlsx:
        xlsx.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>',
        )
        xlsx.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>',
        )
        xlsx.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="BOM" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        xlsx.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>',
        )
        xlsx.writestr("xl/worksheets/sheet1.xml", sheet_xml(rows))


def write_html_preview(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "".join(f"<th>{html.escape(field)}</th>" for field in FIELDS)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(row.get(field, ''))}</td>" for field in FIELDS) + "</tr>"
        for row in rows
    )
    path.write_text(
        "<!doctype html><meta charset=\"utf-8\"><title>ADE9000 BOM</title>"
        "<style>body{font-family:sans-serif}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:0.35rem}th{background:#eee}</style>"
        f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export grouped ADE9000 BOM from schematic fields")
    parser.add_argument("--schematic", type=Path, default=DEFAULT_SCHEMATIC)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--html", type=Path, default=None)
    args = parser.parse_args()

    rows = load_rows(args.schematic)
    write_csv(rows, args.csv)
    write_xlsx(rows, args.xlsx)
    if args.html:
        write_html_preview(rows, args.html)
    print(f"Exported {len(rows)} BOM lines to {args.csv} and {args.xlsx}")


if __name__ == "__main__":
    main()