from __future__ import annotations

from pathlib import Path

import pcbnew


BOARD = Path("ADE9000_Breakout.kicad_pcb")
TRACK_WIDTH_MM = 0.15
VIA_DIAMETER_MM = 0.45
VIA_DRILL_MM = 0.20


def vmm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def mm(point: pcbnew.VECTOR2I) -> tuple[float, float]:
    return pcbnew.ToMM(point.x), pcbnew.ToMM(point.y)


def net(board: pcbnew.BOARD, name: str) -> pcbnew.NETINFO_ITEM:
    item = board.FindNet(name)
    if item is None:
        raise KeyError(name)
    return item


def pad(board: pcbnew.BOARD, reference: str, number: str) -> tuple[float, float]:
    footprint = board.FindFootprintByReference(reference)
    if footprint is None:
        raise KeyError(reference)
    for item in footprint.Pads():
        if item.GetNumber() == number:
            return mm(item.GetPosition())
    raise KeyError(f"{reference}.{number}")


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


def via(board: pcbnew.BOARD, net_name: str, position: tuple[float, float]) -> None:
    item = pcbnew.PCB_VIA(board)
    item.SetPosition(vmm(*position))
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

    via(board, "IBP", (133.600, 91.080))
    via(board, "IBP", (135.850, 98.143))
    route(board, "IBP", [pad(board, "C14", "1"), (133.600, 91.080)], pcbnew.F_Cu)
    route(board, "IBP", [(133.600, 91.080), (132.400, 91.080), (132.400, 98.143), (135.850, 98.143)], pcbnew.B_Cu)
    route(board, "IBP", [(135.850, 98.143), pad(board, "U1", "9")], pcbnew.F_Cu)

    route(board, "IAN", [pad(board, "C13", "1"), (135.300, 89.180), (135.300, 97.643), pad(board, "U1", "8")], pcbnew.F_Cu)

    via(board, "ICP", (133.600, 94.880))
    via(board, "ICP", (137.000, 100.400))
    route(board, "ICP", [pad(board, "C16", "1"), (133.600, 94.880)], pcbnew.F_Cu)
    route(board, "ICP", [(133.600, 94.880), (137.000, 94.880), (137.000, 100.400)], pcbnew.B_Cu)
    route(board, "ICP", [(137.000, 100.400), pad(board, "U1", "11")], pcbnew.F_Cu)


    via(board, "GND", pad(board, "C14", "2"))
    via(board, "GND", pad(board, "C16", "2"))
    route(board, "GND", [pad(board, "C14", "2"), pad(board, "C16", "2")], pcbnew.B_Cu)

    via(board, "MOSI", (138.135, 92.650))
    via(board, "MOSI", (140.385, 109.500))
    route(board, "MOSI", [pad(board, "U1", "39"), (138.135, 92.650)], pcbnew.F_Cu)
    route(board, "MOSI", [(138.135, 92.650), (139.200, 92.650), (139.200, 109.500), (140.385, 109.500)], pcbnew.B_Cu)
    route(board, "MOSI", [(140.385, 109.500), pad(board, "J1", "4")], pcbnew.F_Cu)

    via(board, "CF3_ZX", (140.135, 92.650))
    route(board, "CF3_ZX", [pad(board, "U1", "35"), (140.135, 92.650)], pcbnew.F_Cu)
    route(
        board,
        "CF3_ZX",
        [(140.135, 92.650), (143.500, 92.650), (143.500, 116.800), (145.500, 118.300), pad(board, "TP9", "1")],
        pcbnew.B_Cu,
    )

    via(board, "CLKIN", (144.400, 94.643))
    via(board, "CLKIN", pad(board, "C9", "2"))
    route(board, "CLKIN", [pad(board, "U1", "29"), (144.400, 94.643)], pcbnew.F_Cu)
    route(board, "CLKIN", [(144.400, 94.643), (148.000, 94.643), (148.000, 92.900), pad(board, "C9", "2")], pcbnew.B_Cu)

    pcbnew.SaveBoard(str(BOARD), board)
    print("seeded critical ADE9000 routes")


if __name__ == "__main__":
    main()