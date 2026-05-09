from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew

from apply_board_markings import apply_markings_text
from move_refs_to_silkscreen import place_references


CORNER_RADIUS_MM = 5.08
MOUNTING_HOLE_DRILL_MM = 2.2
MOUNTING_HOLE_INSET_MM = 3.4
EDGE_WIDTH_MM = 0.1
ADE9000_BOARD_BBOX = (120.835, 82.423, 158.935, 120.423)

def to_coord(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def edge_cuts_bbox(board: pcbnew.BOARD) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []

    for drawing in board.GetDrawings():
        if not hasattr(drawing, "GetLayer") or drawing.GetLayer() != pcbnew.Edge_Cuts:
            continue

        for point in (drawing.GetStart(), drawing.GetEnd()):
            xs.append(pcbnew.ToMM(point.x))
            ys.append(pcbnew.ToMM(point.y))

        if hasattr(drawing, "GetCenter"):
            center = drawing.GetCenter()
            xs.append(pcbnew.ToMM(center.x))
            ys.append(pcbnew.ToMM(center.y))

    if not xs or not ys:
        raise RuntimeError("board has no Edge.Cuts outline to update")

    return min(xs), min(ys), max(xs), max(ys)


def remove_edge_cuts(board: pcbnew.BOARD) -> None:
    for drawing in list(board.GetDrawings()):
        if hasattr(drawing, "GetLayer") and drawing.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(drawing)


def add_edge_segment(
    board: pcbnew.BOARD,
    start: tuple[float, float],
    end: tuple[float, float],
) -> None:
    segment = pcbnew.PCB_SHAPE(board)
    segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
    segment.SetLayer(pcbnew.Edge_Cuts)
    segment.SetWidth(pcbnew.FromMM(EDGE_WIDTH_MM))
    segment.SetStart(to_coord(*start))
    segment.SetEnd(to_coord(*end))
    board.Add(segment)


def add_edge_arc(
    board: pcbnew.BOARD,
    start: tuple[float, float],
    end: tuple[float, float],
    center: tuple[float, float],
) -> None:
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetLayer(pcbnew.Edge_Cuts)
    arc.SetWidth(pcbnew.FromMM(EDGE_WIDTH_MM))
    arc.SetStart(to_coord(*start))
    arc.SetEnd(to_coord(*end))
    arc.SetCenter(to_coord(*center))
    board.Add(arc)


def add_rounded_outline(board: pcbnew.BOARD, bbox: tuple[float, float, float, float]) -> None:
    left, top, right, bottom = bbox
    radius = min(CORNER_RADIUS_MM, (right - left) / 2 - 0.5, (bottom - top) / 2 - 0.5)

    add_edge_segment(board, (left + radius, top), (right - radius, top))
    add_edge_arc(board, (right - radius, top), (right, top + radius), (right - radius, top + radius))
    add_edge_segment(board, (right, top + radius), (right, bottom - radius))
    add_edge_arc(board, (right, bottom - radius), (right - radius, bottom), (right - radius, bottom - radius))
    add_edge_segment(board, (right - radius, bottom), (left + radius, bottom))
    add_edge_arc(board, (left + radius, bottom), (left, bottom - radius), (left + radius, bottom - radius))
    add_edge_segment(board, (left, bottom - radius), (left, top + radius))
    add_edge_arc(board, (left, top + radius), (left + radius, top), (left + radius, top + radius))


def remove_existing_mounting_holes(board: pcbnew.BOARD) -> None:
    for footprint in list(board.GetFootprints()):
        if footprint.GetReference().startswith("H") and "MountingHole" in footprint.GetValue():
            board.Remove(footprint)


def add_mounting_hole(board: pcbnew.BOARD, reference: str, x_mm: float, y_mm: float) -> None:
    footprint = pcbnew.FOOTPRINT(board)
    footprint.SetReference(reference)
    footprint.SetValue("MountingHole_2.2mm_M2")
    footprint.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_2.2mm_M2"))
    footprint.SetPosition(to_coord(x_mm, y_mm))
    footprint.SetLayer(pcbnew.F_Cu)

    try:
        footprint.SetExcludedFromBOM(True)
        footprint.SetExcludedFromPositionFiles(True)
    except AttributeError:
        pass

    pad = pcbnew.PAD(footprint)
    pad.SetNumber("")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_CIRCLE)
    pad.SetSize(to_coord(MOUNTING_HOLE_DRILL_MM, MOUNTING_HOLE_DRILL_MM))
    pad.SetDrillSize(to_coord(MOUNTING_HOLE_DRILL_MM, MOUNTING_HOLE_DRILL_MM))
    pad.SetLayerSet(pad.UnplatedHoleMask())
    pad.SetPosition(to_coord(x_mm, y_mm))
    footprint.Add(pad)
    board.Add(footprint)


def add_mounting_holes(board: pcbnew.BOARD, bbox: tuple[float, float, float, float]) -> None:
    left, top, right, bottom = bbox
    positions = [
        ("H1", left + MOUNTING_HOLE_INSET_MM, top + 2.577),
        ("H2", right - MOUNTING_HOLE_INSET_MM, top + 2.577),
        ("H3", left + MOUNTING_HOLE_INSET_MM, bottom - 1.713),
        ("H4", right - 3.135, bottom - 1.813),
    ]

    for reference, x_mm, y_mm in positions:
        add_mounting_hole(board, reference, x_mm, y_mm)


def hide_mounting_hole_values(board_path: Path) -> None:
    text = board_path.read_text(encoding="utf-8")

    visible_value = (
        '(property "Value" "MountingHole_2.2mm_M2"\n'
        '\t\t\t(at 0 0 0)\n'
        '\t\t\t(layer "F.Fab")'
    )
    hidden_value = visible_value + '\n\t\t\t(hide yes)'
    text = text.replace(visible_value, hidden_value)

    board_path.write_text(text, encoding="utf-8", newline="")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply ADE9000 breakout mechanical board features.")
    parser.add_argument("board", type=Path, help="Path to the .kicad_pcb file to update")
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    bbox = ADE9000_BOARD_BBOX
    edge_drawings = [
        drawing
        for drawing in list(board.GetDrawings())
        if hasattr(drawing, "GetLayer") and drawing.GetLayer() == pcbnew.Edge_Cuts
    ]
    footprints = list(board.GetFootprints())
    mounting_holes = [
        footprint
        for footprint in footprints
        if footprint.GetReference().startswith("H") and "MountingHole" in footprint.GetValue()
    ]

    for drawing in edge_drawings:
        board.Remove(drawing)

    for footprint in mounting_holes:
        board.Remove(footprint)

    add_rounded_outline(board, bbox)
    add_mounting_holes(board, bbox)
    place_references(board)

    pcbnew.SaveBoard(str(args.board), board)
    hide_mounting_hole_values(args.board)
    args.board.write_text(apply_markings_text(args.board.read_text(encoding="utf-8")), encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
