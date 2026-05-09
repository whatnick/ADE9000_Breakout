from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


TRACK_WIDTH_MM = 0.15
VIA_DIAMETER_MM = 0.45
VIA_DRILL_MM = 0.20


def vmm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def xy(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return round(pcbnew.ToMM(point.x), 3), round(pcbnew.ToMM(point.y), 3)


def net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    item = board.FindNet(name)
    if item is None:
        raise KeyError(name)
    return item


def pad(board: pcbnew.BOARD, ref: str, number: str) -> tuple[float, float]:
    footprint = board.FindFootprintByReference(ref)
    if footprint is None:
        raise KeyError(ref)
    for item in footprint.Pads():
        if item.GetNumber() == number:
            return xy(item.GetPosition())
    raise KeyError(f"{ref}.{number}")


def top_only_pad_positions(board: pcbnew.BOARD) -> set[tuple[float, float]]:
    positions: set[tuple[float, float]] = set()
    for footprint in board.GetFootprints():
        for item in footprint.Pads():
            if item.GetNetname() and item.IsOnLayer(pcbnew.F_Cu) and not item.IsOnLayer(pcbnew.B_Cu):
                positions.add(xy(item.GetPosition()))
    return positions


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


def route(board: pcbnew.BOARD, net_name: str, points: list[tuple[float, float]], layer: int) -> None:
    for start, end in zip(points, points[1:]):
        add_track(board, net_name, start, end, layer)


def route_bottom(board: pcbnew.BOARD, net_name: str, points: list[tuple[float, float]]) -> None:
    top_only = top_only_pad_positions(board)
    for point in sorted(set(points)):
        if point not in top_only:
            continue
        add_via(board, net_name, point)
    route(board, net_name, points, pcbnew.B_Cu)


def analog_left(board: pcbnew.BOARD) -> None:
    specs = [
        ("IAP_J", "J2", "1", "R2", "1"),
        ("IAN_J", "J2", "2", "R3", "1"),
        ("IBP_J", "J2", "3", "R4", "1"),
        ("IBN_J", "J2", "4", "R5", "1"),
        ("ICP_J", "J2", "5", "R6", "1"),
        ("ICN_J", "J2", "6", "R7", "1"),
        ("INP_J", "J2", "7", "R8", "1"),
        ("INN_J", "J2", "8", "R9", "1"),
    ]
    for net_name, j_ref, j_pad, r_ref, r_pad in specs:
        route(board, net_name, [pad(board, j_ref, j_pad), pad(board, r_ref, r_pad)], pcbnew.F_Cu)

    specs2 = [
        ("IAP", "R2", "C12", "7", 135.00),
        ("IAN", "R3", "C13", "8", 135.32),
        ("IBP", "R4", "C14", "9", 135.64),
        ("IBN", "R5", "C15", "10", 135.96),
        ("ICP", "R6", "C16", "11", 136.28),
        ("ICN", "R7", "C17", "12", 136.60),
        ("INP", "R8", "C18", "13", 136.92),
        ("INN", "R9", "C19", "14", 137.24),
    ]
    for net_name, r_ref, c_ref, u_pad, lane_x in specs2:
        r2 = pad(board, r_ref, "2")
        c1 = pad(board, c_ref, "1")
        u1 = pad(board, "U1", u_pad)
        route(board, net_name, [r2, c1, (lane_x, c1[1]), (lane_x, u1[1]), u1], pcbnew.F_Cu)


def analog_right(board: pcbnew.BOARD) -> None:
    specs = [
        ("VAP_J", "J3", "1", "R11", "1", 153.0),
        ("VAN_J", "J3", "2", "R10", "1", 152.7),
        ("VBP_J", "J3", "3", "R13", "1", 152.4),
        ("VBN_J", "J3", "4", "R12", "1", 152.1),
        ("VCP_J", "J3", "5", "R15", "1", 151.8),
        ("VCN_J", "J3", "6", "R14", "1", 151.5),
    ]
    for net_name, j_ref, j_pad, r_ref, r_pad, lane_x in specs:
        j = pad(board, j_ref, j_pad)
        r1 = pad(board, r_ref, r_pad)
        route(board, net_name, [j, (lane_x, j[1]), (lane_x, r1[1]), r1], pcbnew.F_Cu)

    specs2 = [
        ("VAN", "R10", "C20", "19", 144.90),
        ("VAP", "R11", "C21", "20", 144.58),
        ("VBN", "R12", "C22", "21", 144.26),
        ("VBP", "R13", "C23", "22", 143.94),
        ("VCN", "R14", "C24", "23", 143.62),
        ("VCP", "R15", "C25", "24", 143.30),
    ]
    for net_name, r_ref, c_ref, u_pad, lane_x in specs2:
        r2 = pad(board, r_ref, "2")
        c1 = pad(board, c_ref, "1")
        u1 = pad(board, "U1", u_pad)
        route(board, net_name, [r2, c1, (lane_x, c1[1]), (lane_x, u1[1]), u1], pcbnew.F_Cu)


def power_and_ground(board: pcbnew.BOARD) -> None:
    route(board, "+3V3", [pad(board, "J1", "1"), (137.385, 103.2), pad(board, "R1", "2"), pad(board, "U1", "1")], pcbnew.F_Cu)
    route(board, "+3V3", [pad(board, "U1", "27"), (146.0, 100.65), pad(board, "C2", "2"), pad(board, "C1", "2")], pcbnew.F_Cu)

    route(board, "DVDDOUT", [pad(board, "C5", "2"), pad(board, "U1", "3"), pad(board, "C6", "2")], pcbnew.F_Cu)
    route(board, "AVDDOUT", [pad(board, "U1", "25"), (142.0, 105.45), pad(board, "C3", "2"), pad(board, "C4", "2")], pcbnew.F_Cu)
    route(board, "REF", [pad(board, "U1", "16"), (145.0, 99.331), (145.0, 84.0), pad(board, "C7", "2"), pad(board, "C8", "2")], pcbnew.F_Cu)

    route_bottom(board, "GND", [pad(board, "J1", "2"), (138.385, 107.0), pad(board, "C3", "1"), pad(board, "C4", "1")])
    route_bottom(board, "GND", [pad(board, "C1", "1"), pad(board, "C2", "1"), (142.822, 96.143), pad(board, "U1", "26"), pad(board, "U1", "28")])
    route_bottom(board, "GND", [pad(board, "C5", "1"), pad(board, "C6", "1"), pad(board, "U1", "2"), pad(board, "U1", "4"), pad(board, "U1", "5")])
    route_bottom(board, "GND", [pad(board, "C7", "1"), pad(board, "C8", "1"), (145.0, 85.18), pad(board, "C20", "2"), pad(board, "C21", "2"), pad(board, "C22", "2"), pad(board, "C23", "2"), pad(board, "C24", "2"), pad(board, "C25", "2")])
    route_bottom(board, "GND", [pad(board, "C12", "2"), pad(board, "C13", "2"), pad(board, "C14", "2"), pad(board, "C15", "2"), pad(board, "C16", "2"), pad(board, "C17", "2"), pad(board, "C18", "2"), pad(board, "C19", "2"), (136.3, 99.62), pad(board, "U1", "15")])
    add_via(board, "GND", pad(board, "U1", "EP"))
    route_bottom(board, "GND", [pad(board, "U1", "EP"), pad(board, "U1", "15")])


def digital_and_clock(board: pcbnew.BOARD) -> None:
    route_bottom(board, "SS", [pad(board, "U1", "40"), (137.635, 101.0), (139.385, 101.0), pad(board, "J1", "3")])
    route_bottom(board, "MOSI", [pad(board, "U1", "39"), (138.135, 100.4), (140.385, 100.4), pad(board, "J1", "4")])
    route_bottom(board, "MISO", [pad(board, "U1", "38"), (138.635, 99.8), (141.385, 99.8), pad(board, "J1", "5")])
    route_bottom(board, "SCLK", [pad(board, "U1", "37"), (139.135, 99.2), (142.385, 99.2), pad(board, "J1", "6")])

    route_bottom(board, "RESET", [pad(board, "U1", "6"), (136.947, 102.0), pad(board, "R1", "1"), pad(board, "C11", "2"), pad(board, "TP11", "1")])
    route_bottom(board, "GND", [pad(board, "C11", "1"), (139.1, 107.0)])

    route_bottom(board, "IRQ0", [pad(board, "U1", "31"), (149.0, 93.456), (149.0, 104.0), pad(board, "TP5", "1")])
    route_bottom(board, "IRQ1", [pad(board, "U1", "32"), (132.0, 101.5), pad(board, "TP6", "1")])
    route_bottom(board, "CF1", [pad(board, "U1", "33"), (135.4, 101.0), pad(board, "TP7", "1")])
    route_bottom(board, "CF2", [pad(board, "U1", "34"), (138.8, 101.0), pad(board, "TP8", "1"), (145.0, 104.7), pad(board, "R16", "2")])
    route_bottom(board, "CF2_LED", [pad(board, "R16", "1"), pad(board, "D1", "2")])
    route_bottom(board, "GND", [pad(board, "D1", "1"), (152.213, 107.6), pad(board, "C4", "1")])
    route_bottom(board, "CF3_ZX", [pad(board, "U1", "35"), (148.5, 101.0), pad(board, "TP9", "1")])
    route_bottom(board, "CF4_DREADY", [pad(board, "U1", "36"), (151.9, 101.0), pad(board, "TP10", "1")])

    route_bottom(board, "CLKIN", [pad(board, "U1", "29"), (146.5, 94.643), pad(board, "C9", "2"), pad(board, "Y1", "1"), (135.4, 102.0), pad(board, "TP12", "1")])
    route_bottom(board, "CLKOUT", [pad(board, "U1", "30"), (145.8, 94.143), pad(board, "Y1", "2"), pad(board, "C10", "2"), (138.8, 102.0), pad(board, "TP13", "1")])
    route_bottom(board, "GND", [pad(board, "C9", "1"), (151.42, 96.3), pad(board, "C10", "1")])


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministically route the ADE9000 breakout PCB.")
    parser.add_argument("board", type=Path)
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    if board is None:
        raise RuntimeError(f"Could not load {args.board}")

    analog_left(board)
    analog_right(board)
    power_and_ground(board)
    digital_and_clock(board)
    pcbnew.SaveBoard(str(args.board), board)
    print("Added deterministic route pass")


if __name__ == "__main__":
    main()