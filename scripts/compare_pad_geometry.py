from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


def pad_xy(pad: pcbnew.PAD) -> tuple[float, float]:
    position = pad.GetPosition()
    return round(pcbnew.ToMM(position.x), 3), round(pcbnew.ToMM(position.y), 3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare pad geometry between boards.")
    parser.add_argument("old_board", type=Path)
    parser.add_argument("new_board", type=Path)
    parser.add_argument("refs", nargs="*")
    args = parser.parse_args()

    old_board = pcbnew.LoadBoard(str(args.old_board))
    new_board = pcbnew.LoadBoard(str(args.new_board))
    refs = args.refs or sorted({fp.GetReference() for fp in old_board.GetFootprints()} & {fp.GetReference() for fp in new_board.GetFootprints()})
    for ref in refs:
        old_fp = old_board.FindFootprintByReference(ref)
        new_fp = new_board.FindFootprintByReference(ref)
        if old_fp is None or new_fp is None:
            continue
        old_pads = {pad.GetNumber(): pad for pad in old_fp.Pads()}
        for pad in new_fp.Pads():
            old_pad = old_pads.get(pad.GetNumber())
            if old_pad is None:
                continue
            old_xy = pad_xy(old_pad)
            new_xy = pad_xy(pad)
            if old_xy != new_xy or old_pad.GetNetname() != pad.GetNetname():
                print(ref, pad.GetNumber(), "old", old_xy, old_pad.GetNetname(), "new", new_xy, pad.GetNetname())


if __name__ == "__main__":
    main()