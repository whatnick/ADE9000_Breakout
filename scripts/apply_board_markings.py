from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PCB_PATH = ROOT / "ADE9000_Breakout.kicad_pcb"
V9261F_BOARD_PATH = Path(r"C:\Users\tisha\dev\V9261F_Breakout\V9261F_Breakout.kicad_pcb")

FRONT_TITLE = "ADE9000 Breakout"
BACK_ATTRIBUTION = "by Tisham Dhar\nhttps://whatnick.com\nv0.1 09/05/2026"
LOGO_REF = "LOGO1"


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
    text = text.replace('(at 150.495 87.376 180)', '(at 139.850 90.300 180)', 1)
    return "\t" + text.strip().replace("\n  ", "\n\t").rstrip() + "\n"


def apply_markings_text(board_text: str) -> str:
    board_text = remove_blocks(board_text, "\t(gr_text", FRONT_TITLE)
    board_text = remove_blocks(board_text, "\t(gr_text", BACK_ATTRIBUTION)
    board_text = remove_blocks(board_text, "\t(gr_text", escape_gr_text(FRONT_TITLE))
    board_text = remove_blocks(board_text, "\t(gr_text", escape_gr_text(BACK_ATTRIBUTION))
    board_text = remove_blocks(board_text, "\t(footprint", LOGO_REF)
    board_text = remove_blocks(board_text, "\t(footprint", "OSHW-LOGO")

    blocks = [
        gr_text_block(FRONT_TITLE, 122.350, 96.400, 90, "F.SilkS", 0.8, 0.2, "26f5e411-5570-4436-91db-a9e900010002"),
        gr_text_block(BACK_ATTRIBUTION, 139.850, 86.500, 0, "B.SilkS", 0.8, 0.2, "a7fc7aca-9271-4c6a-98dc-a9e900010003", justify="bottom mirror", bold=True),
        oshw_logo_block(),
    ]

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
