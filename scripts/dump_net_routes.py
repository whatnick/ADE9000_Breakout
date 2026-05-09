from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


def point_mm(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return round(pcbnew.ToMM(point.x), 3), round(pcbnew.ToMM(point.y), 3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump tracks/vias for selected nets.")
    parser.add_argument("board", type=Path)
    parser.add_argument("nets", nargs="+")
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    for item in board.GetTracks():
        net_name = item.GetNetname()
        if net_name not in args.nets:
            continue
        layer = item.GetLayerName()
        if "VIA" in item.GetClass():
            print(net_name, "via", point_mm(item.GetPosition()))
        else:
            print(net_name, layer, point_mm(item.GetStart()), point_mm(item.GetEnd()))


if __name__ == "__main__":
    main()