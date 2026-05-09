from __future__ import annotations

import argparse
import collections
from pathlib import Path

import pcbnew


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump PCB pads grouped by net.")
    parser.add_argument("board", type=Path)
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    nets: dict[str, list[tuple[str, str, float, float]]] = collections.defaultdict(list)
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            net = pad.GetNetname()
            if not net:
                continue
            position = pad.GetPosition()
            nets[net].append(
                (
                    footprint.GetReference(),
                    pad.GetNumber(),
                    round(pcbnew.ToMM(position.x), 3),
                    round(pcbnew.ToMM(position.y), 3),
                )
            )

    for net in sorted(nets):
        if net in {"+3V3", "GND"} or len(nets[net]) > 1:
            print("NET", net, len(nets[net]))
            for row in sorted(nets[net], key=lambda item: (item[2], item[3], item[0])):
                print(" ", row)


if __name__ == "__main__":
    main()