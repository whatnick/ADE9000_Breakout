from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


def mm(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return round(pcbnew.ToMM(point.x), 3), round(pcbnew.ToMM(point.y), 3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare footprint placement between two boards.")
    parser.add_argument("old_board", type=Path)
    parser.add_argument("new_board", type=Path)
    args = parser.parse_args()

    old_board = pcbnew.LoadBoard(str(args.old_board))
    new_board = pcbnew.LoadBoard(str(args.new_board))
    if old_board is None or new_board is None:
        raise RuntimeError("could not load one of the boards")

    refs = sorted({fp.GetReference() for fp in old_board.GetFootprints()} | {fp.GetReference() for fp in new_board.GetFootprints()})
    for ref in refs:
        old_fp = old_board.FindFootprintByReference(ref)
        new_fp = new_board.FindFootprintByReference(ref)
        if old_fp is None or new_fp is None:
            print(ref, "old" if old_fp else "-", "new" if new_fp else "-")
            continue

        old_x, old_y = mm(old_fp.GetPosition())
        new_x, new_y = mm(new_fp.GetPosition())
        old_angle = round(old_fp.GetOrientationDegrees(), 1)
        new_angle = round(new_fp.GetOrientationDegrees(), 1)
        if abs(old_x - new_x) > 0.01 or abs(old_y - new_y) > 0.01 or abs(old_angle - new_angle) > 0.1:
            print(ref, "old", old_x, old_y, old_angle, "new", new_x, new_y, new_angle)


if __name__ == "__main__":
    main()