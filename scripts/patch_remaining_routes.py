from __future__ import annotations

from pathlib import Path

import pcbnew


BOARD = Path("ADE9000_Breakout.kicad_pcb")
TRACK_WIDTH_MM = 0.15
VIA_DIAMETER_MM = 0.45
VIA_DRILL_MM = 0.20


def vmm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    item = board.FindNet(name)
    if item is None:
        raise KeyError(name)
    return item


def track(board: pcbnew.BOARD, net_name: str, start: tuple[float, float], end: tuple[float, float], layer: int) -> None:
    if start == end:
        return
    item = pcbnew.PCB_TRACK(board)
    item.SetStart(vmm(*start))
    item.SetEnd(vmm(*end))
    item.SetWidth(pcbnew.FromMM(TRACK_WIDTH_MM))
    item.SetLayer(layer)
    item.SetNet(net(board, net_name))
    board.Add(item)


def via(board: pcbnew.BOARD, net_name: str, point: tuple[float, float]) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetPosition(vmm(*point))
    item.SetWidth(pcbnew.FromMM(VIA_DIAMETER_MM))
    item.SetDrill(pcbnew.FromMM(VIA_DRILL_MM))
    item.SetNet(net(board, net_name))
    board.Add(item)


def route(board: pcbnew.BOARD, net_name: str, points: list[tuple[float, float]], layer: int) -> None:
    for start, end in zip(points, points[1:]):
        track(board, net_name, start, end, layer)


def route_with_vias(board: pcbnew.BOARD, net_name: str, points: list[tuple[float, float]], via_points: list[tuple[float, float]]) -> None:
    for point in via_points:
        via(board, net_name, point)
    route(board, net_name, points, pcbnew.B_Cu)


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD))
    if board is None:
        raise RuntimeError(f"Could not load {BOARD}")

    # Freerouting leaves these six logical gaps on the otherwise DRC-clean import.
    route(board, "+3V3", [(136.9475, 94.143), (136.45, 94.143), (136.45, 103.2), (137.61, 103.2)], pcbnew.F_Cu)
    route(board, "IAP", [(134.55, 87.28), (135.48, 87.28), (135.48, 97.143), (136.9475, 97.143)], pcbnew.F_Cu)
    route(board, "CLKOUT", [(142.8225, 94.143), (150.487, 94.113)], pcbnew.F_Cu)
    route_with_vias(board, "CLKOUT", [(138.8, 104.0), (138.8, 101.2), (150.487, 98.583)], [(138.8, 104.0), (150.487, 98.583)])

    route_with_vias(board, "CF1", [(141.135, 93.4555), (135.4, 101.3), (135.4, 107.6)], [(141.135, 93.4555), (135.4, 107.6)])
    route_with_vias(board, "MOSI", [(138.135, 93.4555), (133.1, 100.8), (140.385, 110.475)], [(138.135, 93.4555), (140.385, 110.475)])
    route_with_vias(board, "MISO", [(138.635, 93.4555), (134.1, 101.8), (141.385, 110.475)], [(138.635, 93.4555), (141.385, 110.475)])

    pcbnew.SaveBoard(str(BOARD), board)
    print("patched remaining routes")


if __name__ == "__main__":
    main()