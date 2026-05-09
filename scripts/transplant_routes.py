from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


TRACK_WIDTH_MM = 0.15
VIA_DIAMETER_MM = 0.45
VIA_DRILL_MM = 0.20
SKIP_OLD_NETS = {"SS", "MOSI", "MISO", "SCLK"}


def vmm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def to_mm(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)


def net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    item = board.FindNet(name)
    if item is None:
        item = pcbnew.NETINFO_ITEM(board, name)
        board.Add(item)
    return item


def clear_routes(board: pcbnew.BOARD) -> int:
    removed = 0
    for item in list(board.GetTracks()):
        board.Remove(item)
        removed += 1
    return removed


def add_track(board: pcbnew.BOARD, net_name: str, start: tuple[float, float], end: tuple[float, float], layer: int) -> None:
    if start == end:
        return
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(vmm(*start))
    track.SetEnd(vmm(*end))
    track.SetWidth(pcbnew.FromMM(TRACK_WIDTH_MM))
    track.SetLayer(layer)
    track.SetNet(net(board, net_name))
    board.Add(track)


def add_via(board: pcbnew.BOARD, net_name: str, position: tuple[float, float]) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(vmm(*position))
    via.SetWidth(pcbnew.FromMM(VIA_DIAMETER_MM))
    via.SetDrill(pcbnew.FromMM(VIA_DRILL_MM))
    via.SetNet(net(board, net_name))
    board.Add(via)


def route_polyline(board: pcbnew.BOARD, net_name: str, points: list[tuple[float, float]], layer: int) -> None:
    for start, end in zip(points, points[1:]):
        add_track(board, net_name, start, end, layer)


def route_with_via(
    board: pcbnew.BOARD,
    net_name: str,
    top_points: list[tuple[float, float]],
    via_position: tuple[float, float],
    bottom_points: list[tuple[float, float]],
) -> None:
    route_polyline(board, net_name, top_points + [via_position], pcbnew.F_Cu)
    add_via(board, net_name, via_position)
    route_polyline(board, net_name, [via_position] + bottom_points, pcbnew.B_Cu)


def transplant(old_board: pcbnew.BOARD, new_board: pcbnew.BOARD) -> int:
    copied = 0
    for item in old_board.GetTracks():
        net_name = item.GetNetname()
        if not net_name or net_name in SKIP_OLD_NETS:
            continue

        if "VIA" in item.GetClass():
            via = pcbnew.PCB_VIA(new_board)
            via.SetPosition(item.GetPosition())
            via.SetWidth(pcbnew.FromMM(VIA_DIAMETER_MM))
            via.SetDrill(pcbnew.FromMM(VIA_DRILL_MM))
            via.SetNet(net(new_board, net_name))
            new_board.Add(via)
            copied += 1
            continue

        track = pcbnew.PCB_TRACK(new_board)
        track.SetStart(item.GetStart())
        track.SetEnd(item.GetEnd())
        track.SetWidth(item.GetWidth())
        track.SetLayer(item.GetLayer())
        track.SetNet(net(new_board, net_name))
        new_board.Add(track)
        copied += 1
    return copied


def add_new_routes(board: pcbnew.BOARD) -> None:
    # New JST-SH SPI/debug connector fanout.
    route_polyline(board, "SS", [(137.635, 93.456), (137.635, 101.2), (139.385, 101.2), (139.385, 110.475)], pcbnew.F_Cu)
    route_polyline(board, "MOSI", [(138.135, 93.456), (138.135, 100.7), (140.385, 100.7), (140.385, 110.475)], pcbnew.F_Cu)
    route_polyline(board, "MISO", [(138.635, 93.456), (138.635, 100.2), (141.385, 100.2), (141.385, 110.475)], pcbnew.F_Cu)
    route_polyline(board, "SCLK", [(139.135, 93.456), (139.135, 99.7), (142.385, 99.7), (142.385, 110.475)], pcbnew.F_Cu)

    # Tie the new JST power pins into the existing transplanted power network.
    route_polyline(board, "+3V3", [(137.385, 110.475), (137.385, 103.2), (137.610, 103.2)], pcbnew.F_Cu)
    route_polyline(board, "GND", [(138.385, 110.475), (138.385, 107.35), (139.400, 107.35)], pcbnew.F_Cu)

    # New CLKIN/CLKOUT bottom test pads.
    route_with_via(
        board,
        "CLKIN",
        [(142.822, 94.643), (144.1, 94.643), (144.1, 102.9)],
        (135.4, 102.9),
        [(135.4, 104.0)],
    )
    route_with_via(
        board,
        "CLKOUT",
        [(142.822, 94.143), (143.5, 94.143), (143.5, 103.4)],
        (138.8, 103.4),
        [(138.8, 104.0)],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Transplant known-good ADE9000 routes and add JST debug routes.")
    parser.add_argument("board", type=Path)
    parser.add_argument("old_board", type=Path)
    parser.add_argument("--skip-new", action="store_true", help="Only copy old compatible routes")
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    old_board = pcbnew.LoadBoard(str(args.old_board))
    if board is None:
        raise RuntimeError(f"Could not load {args.board}")
    if old_board is None:
        raise RuntimeError(f"Could not load {args.old_board}")

    removed = clear_routes(board)
    copied = transplant(old_board, board)
    if not args.skip_new:
        add_new_routes(board)
    pcbnew.SaveBoard(str(args.board), board)
    suffix = "" if args.skip_new else ", added JST/CLK routes"
    print(f"Removed {removed} route item(s), copied {copied}{suffix}")


if __name__ == "__main__":
    main()