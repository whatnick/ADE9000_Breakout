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


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD))
    if board is None:
        raise RuntimeError(f"Could not load {BOARD}")

    route(board, "IAN", [(134.55, 89.18), (135.85, 89.18), (135.85, 97.643), (136.9475, 97.643)], pcbnew.F_Cu)

    via(board, "CF1", (141.135, 93.4555))
    via(board, "CF1", (135.4, 107.6))
    route(board, "CF1", [(141.135, 93.4555), (134.1, 101.0), (134.1, 107.6), (135.4, 107.6)], pcbnew.B_Cu)

    pcbnew.SaveBoard(str(BOARD), board)
    print("seeded IAN and CF1")


if __name__ == "__main__":
    main()