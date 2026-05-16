from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


BOARD_BBOX_MM = (123.501, 80.004, 188.501, 135.004)
DIMENSION_OFFSET_MM = 4.0
DIMENSION_TEXT_SIZE_MM = 1.2
DIMENSION_TEXT_THICKNESS_MM = 0.15
DIMENSION_LINE_THICKNESS_MM = 0.10
DIMENSION_LAYER = pcbnew.Dwgs_User


def vmm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def remove_existing_dimensions(board: pcbnew.BOARD) -> int:
    removed = 0
    for drawing in list(board.GetDrawings()):
        if type(drawing).__name__.startswith("PCB_DIM_"):
            board.Remove(drawing)
            removed += 1
    return removed


def add_dimension(
    board: pcbnew.BOARD,
    start: tuple[float, float],
    end: tuple[float, float],
    height_mm: float,
    text: str,
    text_pos: tuple[float, float],
    text_angle_degrees: float = 0.0,
) -> None:
    dimension = pcbnew.PCB_DIM_ALIGNED(board)
    dimension.SetLayer(DIMENSION_LAYER)
    dimension.SetStart(vmm(*start))
    dimension.SetEnd(vmm(*end))
    dimension.SetHeight(pcbnew.FromMM(height_mm))
    dimension.SetUnits(pcbnew.EDA_UNITS_MM)
    dimension.SetUnitsMode(pcbnew.DIM_UNITS_MODE_MM)
    dimension.SetUnitsFormat(pcbnew.DIM_UNITS_FORMAT_BARE_SUFFIX)
    dimension.SetPrecision(pcbnew.DIM_PRECISION_X_XXX)
    dimension.SetText(text)
    dimension.SetTextPos(vmm(*text_pos))
    dimension.SetTextAngleDegrees(text_angle_degrees)
    dimension.SetTextSize(vmm(DIMENSION_TEXT_SIZE_MM, DIMENSION_TEXT_SIZE_MM))
    dimension.SetTextThickness(pcbnew.FromMM(DIMENSION_TEXT_THICKNESS_MM))
    dimension.SetLineThickness(pcbnew.FromMM(DIMENSION_LINE_THICKNESS_MM))
    dimension.SetArrowDirection(pcbnew.DIM_ARROW_DIRECTION_OUTWARD)
    board.Add(dimension)


def add_board_edge_dimensions(board: pcbnew.BOARD) -> None:
    left, top, right, bottom = BOARD_BBOX_MM
    width = right - left
    height = bottom - top
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2

    add_dimension(
        board,
        (left, top),
        (right, top),
        -DIMENSION_OFFSET_MM,
        f"{width:.3f} mm",
        (center_x, top - DIMENSION_OFFSET_MM - 1.35),
    )
    add_dimension(
        board,
        (right, top),
        (right, bottom),
        -DIMENSION_OFFSET_MM,
        f"{height:.3f} mm",
        (right + DIMENSION_OFFSET_MM + 1.35, center_y),
        90.0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Add visible board-edge measurements to the ADE9000 PCB.")
    parser.add_argument("board", type=Path, help="Path to the .kicad_pcb file to update")
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    removed = remove_existing_dimensions(board)
    add_board_edge_dimensions(board)
    pcbnew.SaveBoard(str(args.board), board)
    print(f"Replaced {removed} dimension item(s) with 65.000 mm x 55.000 mm edge measurements.")


if __name__ == "__main__":
    main()
