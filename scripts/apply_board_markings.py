from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PCB_PATH = ROOT / "ADE9000_Breakout.kicad_pcb"
V9261F_BOARD_PATH = Path(r"C:\Users\tisha\dev\V9261F_Breakout\V9261F_Breakout.kicad_pcb")

FRONT_TITLE = "ADE9000 Breakout"
BACK_ATTRIBUTION = "by Tisham Dhar\nhttps://whatnick.com\nv0.1 09/05/2026\nTAPR OHL"
LEGACY_BACK_ATTRIBUTIONS = [
    "by Tisham Dhar\nhttps://whatnick.com\nv0.1 09/05/2026",
]
LOGO_REF = "LOGO1"
CURRENT_JACK_REFS = {"CTA1", "CTB1", "CTC1", "CTN1"}
FOOTPRINT_GRAPHIC_BLOCKS = ("fp_line", "fp_arc", "fp_circle", "fp_poly", "fp_rect")
SIGNAL_TEXTS = [
    ("3V3", 180.700, 86.100, 0, "F.SilkS", 0.8, 0.2, "pin1"),
    ("GND", 180.700, 88.640, 0, "F.SilkS", 0.8, 0.2, "pin2"),
    ("SS", 180.700, 91.180, 0, "F.SilkS", 0.8, 0.2, "pin3"),
    ("MOSI", 180.700, 93.720, 0, "F.SilkS", 0.8, 0.2, "pin4"),
    ("MISO", 180.700, 96.260, 0, "F.SilkS", 0.8, 0.2, "pin5"),
    ("SCLK", 180.700, 98.800, 0, "F.SilkS", 0.8, 0.2, "pin6"),
    ("IRQ0", 180.700, 101.340, 0, "F.SilkS", 0.8, 0.2, "pin7"),
    ("IRQ1", 180.700, 103.880, 0, "F.SilkS", 0.8, 0.2, "pin8"),
    ("CF1", 180.700, 106.420, 0, "F.SilkS", 0.8, 0.2, "pin9"),
    ("CF2", 180.700, 108.960, 0, "F.SilkS", 0.8, 0.2, "pin10"),
    ("CF3", 180.700, 111.500, 0, "F.SilkS", 0.8, 0.2, "pin11"),
    ("DRDY", 180.700, 114.040, 0, "F.SilkS", 0.8, 0.2, "pin12"),
    ("RST", 180.700, 116.580, 0, "F.SilkS", 0.8, 0.2, "pin13"),
    ("CLKI", 180.700, 119.120, 0, "F.SilkS", 0.8, 0.2, "pin14"),
    ("CLKO", 180.700, 121.660, 0, "F.SilkS", 0.8, 0.2, "pin15"),
    ("GND", 180.700, 124.200, 0, "F.SilkS", 0.8, 0.2, "pin16"),
    ("CTA", 130.700, 88.000, 90, "F.SilkS", 0.8, 0.2, "cta"),
    ("CTB", 130.700, 101.000, 90, "F.SilkS", 0.8, 0.2, "ctb"),
    ("CTC", 130.700, 114.000, 90, "F.SilkS", 0.8, 0.2, "ctc"),
    ("CTN", 130.700, 127.000, 90, "F.SilkS", 0.8, 0.2, "ctn"),
    ("VA", 154.000, 127.700, 0, "F.SilkS", 0.8, 0.2, "va"),
    ("VB", 162.000, 127.700, 0, "F.SilkS", 0.8, 0.2, "vb"),
    ("VC", 170.000, 127.700, 0, "F.SilkS", 0.8, 0.2, "vc"),
    ("VIN 12VAC MAX", 145.500, 133.400, 0, "F.SilkS", 0.8, 0.2, "vinmax"),
    ("CT 0.5Vpk MAX", 144.000, 86.000, 0, "F.SilkS", 0.8, 0.2, "ctmax"),
    ("DIGITAL", 175.000, 82.600, 0, "F.SilkS", 0.8, 0.2, "digital"),
]
LEGACY_SIGNAL_TEXTS = ["DREADY", "SPI", "RESET", "CLKIN", "CLKOUT", "CF3/ZX"]


def escape_gr_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def find_block_end(text: str, start: int) -> int:
    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1

    raise ValueError("unterminated S-expression block")


def remove_blocks(text: str, block_start: str, match_text: str) -> str:
    cursor = 0
    output: list[str] = []

    while True:
        start = text.find(block_start, cursor)
        if start == -1:
            output.append(text[cursor:])
            return "".join(output)

        end = find_block_end(text, start)
        block = text[start:end]
        output.append(text[cursor:start])
        if match_text not in block:
            output.append(block)
        cursor = end


def remove_footprint_silk_graphics(block: str) -> str:
    cursor = 0
    output: list[str] = []

    while True:
        starts = [
            block.find(f"\t\t({block_name}", cursor)
            for block_name in FOOTPRINT_GRAPHIC_BLOCKS
        ]
        starts = [start for start in starts if start != -1]
        if not starts:
            output.append(block[cursor:])
            return "".join(output)

        start = min(starts)
        end = find_block_end(block, start)
        child = block[start:end]
        output.append(block[cursor:start])
        if '(layer "F.SilkS")' not in child:
            output.append(child)
        cursor = end


def strip_current_jack_silkscreen_text(board_text: str) -> str:
    cursor = 0
    output: list[str] = []

    while True:
        start = board_text.find("\t(footprint", cursor)
        if start == -1:
            output.append(board_text[cursor:])
            return "".join(output)

        end = find_block_end(board_text, start)
        block = board_text[start:end]
        output.append(board_text[cursor:start])
        if any(f'(property "Reference" "{ref}"' in block for ref in CURRENT_JACK_REFS):
            block = remove_footprint_silk_graphics(block)
        output.append(block)
        cursor = end


def gr_text_block(
    value: str,
    x: float,
    y: float,
    angle: float,
    layer: str,
    size: float,
    thickness: float,
    uuid: str,
    justify: str = "",
    bold: bool = False,
) -> str:
    value = escape_gr_text(value)
    bold_text = "\n\t\t\t\t(bold yes)" if bold else ""
    justify_text = f'\n\t\t\t(justify {justify})' if justify else ""
    return f'''\t(gr_text "{value}"
\t\t(at {x:.3f} {y:.3f} {angle:g})
\t\t(layer "{layer}")
\t\t(uuid "{uuid}")
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size:g} {size:g})
				(thickness {thickness:g}){bold_text}
			){justify_text}
\t\t)
\t)
'''


def oshw_logo_block() -> str:
    source = V9261F_BOARD_PATH.read_text(encoding="utf-8")
    start = source.find('(footprint "Symbol:OSHW-Logo2_7.3x6mm_SilkScreen"')
    if start == -1:
        raise ValueError("could not find V9261F OSHW logo footprint")
    end = find_block_end(source, start)
    text = source[start:end]
    text = text.replace('(at 150.495 87.376 180)', '(at 136.000 108.000 180)', 1)
    return "\t" + text.strip().replace("\n  ", "\n\t").rstrip() + "\n"


def apply_markings_text(board_text: str) -> str:
    board_text = strip_current_jack_silkscreen_text(board_text)
    board_text = remove_blocks(board_text, "\t(gr_text", FRONT_TITLE)
    board_text = remove_blocks(board_text, "\t(gr_text", BACK_ATTRIBUTION)
    board_text = remove_blocks(board_text, "\t(gr_text", escape_gr_text(FRONT_TITLE))
    board_text = remove_blocks(board_text, "\t(gr_text", escape_gr_text(BACK_ATTRIBUTION))
    for legacy_attribution in LEGACY_BACK_ATTRIBUTIONS:
        board_text = remove_blocks(board_text, "\t(gr_text", legacy_attribution)
        board_text = remove_blocks(board_text, "\t(gr_text", escape_gr_text(legacy_attribution))
    board_text = remove_blocks(board_text, "\t(footprint", LOGO_REF)
    board_text = remove_blocks(board_text, "\t(footprint", "OSHW-LOGO")
    for value in [entry[0] for entry in SIGNAL_TEXTS] + LEGACY_SIGNAL_TEXTS:
        board_text = remove_blocks(board_text, "\t(gr_text", value)
        board_text = remove_blocks(board_text, "\t(gr_text", escape_gr_text(value))

    blocks = [
        gr_text_block(FRONT_TITLE, 156.000, 82.100, 0, "F.SilkS", 0.8, 0.2, "26f5e411-5570-4436-91db-a9e900010002"),
        gr_text_block(BACK_ATTRIBUTION, 156.000, 88.000, 0, "B.SilkS", 0.8, 0.2, "a7fc7aca-9271-4c6a-98dc-a9e900010003", justify="bottom mirror", bold=True),
        oshw_logo_block(),
    ]
    for value, x, y, angle, layer, size, thickness, name in SIGNAL_TEXTS:
        justify = "mirror" if layer == "B.SilkS" else ""
        blocks.append(
            gr_text_block(
                value,
                x,
                y,
                angle,
                layer,
                size,
                thickness,
                f"a9e90002-0000-4000-8000-{name.encode('ascii').hex()[:12].ljust(12, '0')}",
                justify=justify,
            )
        )

    insertion = board_text.find("\n\t(gr_")
    if insertion == -1:
        insertion = board_text.rfind("\n)")
    if insertion == -1:
        raise ValueError("could not find insertion point for board markings")

    return board_text[: insertion + 1] + "".join(blocks) + board_text[insertion + 1 :]


def main() -> None:
    board_text = PCB_PATH.read_text(encoding="utf-8")
    PCB_PATH.write_text(apply_markings_text(board_text), encoding="utf-8", newline="")
    print("Applied ADE9000 front/back silkscreen markings and OSHW logo")


if __name__ == "__main__":
    main()
