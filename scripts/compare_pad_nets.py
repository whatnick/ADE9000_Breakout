from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare pad net assignments between boards.")
    parser.add_argument("old_board", type=Path)
    parser.add_argument("new_board", type=Path)
    parser.add_argument("refs", nargs="*")
    args = parser.parse_args()

    old_board = pcbnew.LoadBoard(str(args.old_board))
    new_board = pcbnew.LoadBoard(str(args.new_board))
    refs = args.refs or ["U1", "J1", "J2", "J3"]
    for ref in refs:
        old_fp = old_board.FindFootprintByReference(ref) if old_board else None
        new_fp = new_board.FindFootprintByReference(ref) if new_board else None
        print(ref)
        if old_fp is None or new_fp is None:
            print("  missing", "old" if old_fp is None else "", "new" if new_fp is None else "")
            continue
        old_pads = {pad.GetNumber(): pad.GetNetname() for pad in old_fp.Pads()}
        for pad in new_fp.Pads():
            number = pad.GetNumber()
            old_net = old_pads.get(number)
            new_net = pad.GetNetname()
            if old_net != new_net:
                print("  pad", number, "old", old_net, "new", new_net)


if __name__ == "__main__":
    main()