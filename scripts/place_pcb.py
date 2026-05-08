from __future__ import annotations

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "ADE9000_Breakout.kicad_pcb"
QFN_LIB = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Package_DFN_QFN.pretty")
QFN_NAME = "QFN-40-1EP_6x6mm_P0.5mm_EP4.6x4.6mm"

BOARD_LEFT = 120.835
BOARD_TOP = 82.423
BOARD_WIDTH = 38.100
BOARD_HEIGHT = 27.940
BOARD_RIGHT = BOARD_LEFT + BOARD_WIDTH
BOARD_BOTTOM = BOARD_TOP + BOARD_HEIGHT

SILK_TEXT_SIZE = 0.8
SILK_TEXT_THICKNESS = 0.2

U1_NETS = {
    "1": "+3V3",
    "2": "GND",
    "3": "DVDDOUT",
    "4": "GND",
    "5": "GND",
    "6": "RESET",
    "7": "IAP",
    "8": "IAN",
    "9": "IBP",
    "10": "IBN",
    "11": "ICP",
    "12": "ICN",
    "13": "INP",
    "14": "INN",
    "15": "GND",
    "16": "REF",
    "19": "VAN",
    "20": "VAP",
    "21": "VBN",
    "22": "VBP",
    "23": "VCN",
    "24": "VCP",
    "25": "AVDDOUT",
    "26": "GND",
    "27": "+3V3",
    "28": "GND",
    "29": "CLKIN",
    "30": "CLKOUT",
    "31": "IRQ0",
    "32": "IRQ1",
    "33": "CF1",
    "34": "CF2",
    "35": "CF3_ZX",
    "36": "CF4_DREADY",
    "37": "SCLK",
    "38": "MISO",
    "39": "MOSI",
    "40": "SS",
    "EP": "GND",
}


def vmm(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def footprint_by_ref(board: pcbnew.BOARD, ref: str) -> pcbnew.FOOTPRINT | None:
    for fp in board.GetFootprints():
        if fp.GetReference() == ref:
            return fp
    return None


def place(board: pcbnew.BOARD, ref: str, x: float, y: float, angle: float = 0.0) -> None:
    fp = footprint_by_ref(board, ref)
    if fp is None:
        return
    fp.SetPosition(vmm(x, y))
    fp.SetOrientationDegrees(angle)


def place_bottom(board: pcbnew.BOARD, ref: str, x: float, y: float, angle: float = 0.0) -> None:
    fp = footprint_by_ref(board, ref)
    if fp is None:
        return
    if fp.GetLayer() != pcbnew.B_Cu:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetPosition(vmm(x, y))
    fp.SetOrientationDegrees(angle)


def set_field_style(field: pcbnew.PCB_FIELD) -> None:
    field.SetTextSize(vmm(SILK_TEXT_SIZE, SILK_TEXT_SIZE))
    field.SetTextThickness(pcbnew.FromMM(SILK_TEXT_THICKNESS))


def place_ref(board: pcbnew.BOARD, ref: str, x: float, y: float, angle: float = 0.0) -> None:
    fp = footprint_by_ref(board, ref)
    if fp is None:
        return
    field = fp.Reference()
    set_field_style(field)
    field.SetTextPos(vmm(x, y))
    field.SetTextAngleDegrees(angle)


def normalize_silkscreen(board: pcbnew.BOARD) -> None:
    for fp in board.GetFootprints():
        for field in fp.GetFields():
            set_field_style(field)
        fp.Reference().SetLayer(pcbnew.B_Fab if fp.GetLayer() == pcbnew.B_Cu else pcbnew.F_Fab)
        for item in fp.GraphicalItems():
            if item.GetLayer() == pcbnew.F_SilkS:
                item.SetLayer(pcbnew.F_Fab)
            elif item.GetLayer() == pcbnew.B_SilkS:
                item.SetLayer(pcbnew.B_Fab)


def set_net(board: pcbnew.BOARD, pad: pcbnew.PAD, net_name: str) -> None:
    net = board.FindNet(net_name)
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
    pad.SetNet(net)


def add_u1_if_missing(board: pcbnew.BOARD) -> None:
    if footprint_by_ref(board, "U1") is not None:
        return

    fp = pcbnew.FootprintLoad(str(QFN_LIB), QFN_NAME)
    if fp is None:
        raise RuntimeError(f"Could not load {QFN_LIB / (QFN_NAME + '.kicad_mod')}")

    fp.SetReference("U1")
    fp.SetValue("ADE9000")
    fp.SetPosition(vmm(139.885, 96.393))
    fp.SetOrientationDegrees(0)

    for pad in fp.Pads():
        if pad.GetNumber() == "41":
            pad.SetNumber("EP")
            pad.SetSize(vmm(4.27, 4.27))
        net_name = U1_NETS.get(pad.GetNumber())
        if net_name:
            set_net(board, pad, net_name)

    board.Add(fp)


# Corner radius for the board outline (replaces the old 45-degree chamfer segments).
CORNER_RADIUS = 5.08
# Inset from each straight board edge for M2 mounting hole centres.
MH_INSET = 3.5
# Mounting hole library.
MH_LIB = r"C:\Program Files\KiCad\10.0\share\kicad\footprints\MountingHole.pretty"
MH_NAME = "MountingHole_2.2mm_M2"


def draw_outline(board: pcbnew.BOARD) -> None:
    """Replace any existing Edge.Cuts with a single rounded-rectangle."""
    for drawing in list(board.GetDrawings()):
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(drawing)

    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_RECTANGLE)
    shape.SetStart(vmm(BOARD_LEFT, BOARD_TOP))
    shape.SetEnd(vmm(BOARD_RIGHT, BOARD_BOTTOM))
    shape.SetCornerRadius(pcbnew.FromMM(CORNER_RADIUS))
    shape.SetLayer(pcbnew.Edge_Cuts)
    shape.SetWidth(pcbnew.FromMM(0.1))
    board.Add(shape)


def add_mounting_holes(board: pcbnew.BOARD) -> None:
    """Add four M2 NPTH mounting holes inset from each board corner."""
    # Remove existing mounting hole footprints so the function is idempotent.
    for ref in ("H1", "H2", "H3", "H4"):
        existing = board.FindFootprintByReference(ref)
        if existing:
            board.Remove(existing)

    corners = [
        ("H1", BOARD_LEFT  + MH_INSET, BOARD_TOP    + MH_INSET),
        ("H2", BOARD_RIGHT - MH_INSET, BOARD_TOP    + MH_INSET),
        ("H3", BOARD_RIGHT - MH_INSET, BOARD_BOTTOM - MH_INSET),
        ("H4", BOARD_LEFT  + MH_INSET, BOARD_BOTTOM - MH_INSET),
    ]
    for ref, x, y in corners:
        fp = pcbnew.FootprintLoad(MH_LIB, MH_NAME)
        if fp is None:
            raise RuntimeError(f"Could not load {MH_LIB}/{MH_NAME}.kicad_mod")
        fp.SetReference(ref)
        fp.SetValue("M2")
        fp.SetPosition(vmm(x, y))
        board.Add(fp)


def place_all(board: pcbnew.BOARD) -> None:
    add_u1_if_missing(board)

    place(board, "U1", 139.885, 96.393, 0)

    place(board, "J2", 126.000, 87.900, 0)
    place(board, "J3", 155.600, 88.500, 0)
    place(board, "J1", 145.000, 105.000, 0)

    current_rows = ["IAP", "IAN", "IBP", "IBN", "ICP", "ICN", "INP", "INN"]
    for index, _name in enumerate(current_rows):
        y = 86.800 + index * 1.900
        place(board, f"R{2 + index}", 132.250, y, 0)
        place(board, f"C{12 + index}", 134.550, y, 90)

    voltage_refs = [(10, 20), (11, 21), (12, 22), (13, 23), (14, 24), (15, 25)]
    for index, (resistor, cap) in enumerate(voltage_refs):
        y = 87.100 + index * 1.900
        place(board, f"R{resistor}", 147.600, y, 180)
        place(board, f"C{cap}", 145.250, y, 90)

    for ref, x, y, angle in [
        ("C1", 148.600, 101.600, 90),
        ("C2", 146.000, 101.600, 90),
        ("C3", 139.400, 106.400, 90),
        ("C4", 142.000, 106.400, 90),
        ("C5", 136.000, 84.700, 90),
        ("C6", 138.600, 84.700, 90),
        ("C7", 150.000, 84.700, 90),
        ("C8", 152.600, 84.700, 90),
        ("R1", 137.100, 103.200, 0),
        ("C11", 139.100, 103.200, 90),
        ("Y1", 151.900, 96.300, 90),
        ("C9", 151.900, 92.900, 0),
        ("C10", 151.900, 99.700, 0),
        ("R16", 149.500, 104.700, 0),
        ("D1", 153.000, 107.000, 0),
    ]:
        place(board, ref, x, y, angle)

    testpads = {
        "TP11": (132.000, 104.000),
        "TP1": (135.400, 104.000),
        "TP2": (138.800, 104.000),
        "TP3": (142.200, 104.000),
        "TP4": (148.500, 104.000),
        "TP5": (151.900, 104.000),
        "TP6": (132.000, 107.600),
        "TP7": (135.400, 107.600),
        "TP8": (138.800, 107.600),
        "TP9": (148.500, 107.600),
        "TP10": (151.900, 107.600),
    }
    for ref, (x, y) in testpads.items():
        place_bottom(board, ref, x, y, 0)

    normalize_silkscreen(board)

    for index in range(8):
        y = 86.800 + index * 1.900
        place_ref(board, f"R{2 + index}", 130.350, y, 0)
        place_ref(board, f"C{12 + index}", 136.550, y, 0)

    for index in range(6):
        y = 87.100 + index * 1.900
        place_ref(board, f"R{10 + index}", 149.850, y, 0)
        place_ref(board, f"C{20 + index}", 142.650, y, 0)

    for ref, x, y, angle in [
        ("U1", 139.885, 92.150, 0),
        ("J2", 126.000, 83.700, 0),
        ("J3", 155.600, 85.750, 0),
        ("J1", 145.000, 101.600, 0),
        ("R1", 134.900, 103.200, 0),
        ("C11", 141.400, 103.200, 0),
        ("Y1", 149.050, 96.300, 90),
        ("R16", 151.850, 104.700, 0),
        ("D1", 153.000, 109.300, 0),
        ("C1", 149.850, 101.600, 0),
        ("C2", 145.000, 101.600, 0),
        ("C3", 139.400, 108.100, 0),
        ("C4", 142.000, 108.100, 0),
        ("C5", 136.000, 82.950, 0),
        ("C6", 138.600, 82.950, 0),
        ("C7", 150.000, 82.950, 0),
        ("C8", 152.600, 82.950, 0),
        ("C9", 151.900, 91.250, 0),
        ("C10", 151.900, 101.400, 0),
    ]:
        place_ref(board, ref, x, y, angle)

    for index, ref in enumerate(testpads):
        x, y = testpads[ref]
        place_ref(board, ref, x, y + 1.650, 0)

    draw_outline(board)
    add_mounting_holes(board)


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    place_all(board)
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Placed ADE9000 breakout PCB: {BOARD_WIDTH:.2f} mm x {BOARD_HEIGHT:.2f} mm, rounded corners r={CORNER_RADIUS} mm, 4x M2 mounting holes")


if __name__ == "__main__":
    main()
