from __future__ import annotations

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "ADE9000_Breakout.kicad_pcb"

KICAD_FOOTPRINTS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
QFN_LIB = KICAD_FOOTPRINTS / "Package_DFN_QFN.pretty"
QFN_NAME = "QFN-40-1EP_6x6mm_P0.5mm_EP4.6x4.6mm"
AUDIO_LIB = KICAD_FOOTPRINTS / "Connector_Audio.pretty"
AUDIO_NAME = "Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal"
TERMINAL_LIB = KICAD_FOOTPRINTS / "TerminalBlock_4Ucon.pretty"
TERMINAL_NAME = "TerminalBlock_4Ucon_1x02_P3.50mm_Horizontal"
TERMINAL_MODEL = "${KIPRJMOD}/models/step/TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal.step"
TERMINAL_MODEL_OFFSET = (0.0, -0.6, 0.0)
HEADER_LIB = KICAD_FOOTPRINTS / "Connector_PinHeader_2.54mm.pretty"
HEADER_NAME = "PinHeader_1x16_P2.54mm_Vertical"
RESISTOR_LIB = KICAD_FOOTPRINTS / "Resistor_SMD.pretty"
RESISTOR_NAME = "R_0402_1005Metric"
FOOTPRINT_PLUGIN = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
FOOTPRINT_PROTOTYPES: dict[tuple[str, str], pcbnew.FOOTPRINT] = {}

BOARD_LEFT = 123.501
BOARD_TOP = 80.004
BOARD_WIDTH = 65.000
BOARD_HEIGHT = 55.000
BOARD_RIGHT = BOARD_LEFT + BOARD_WIDTH
BOARD_BOTTOM = BOARD_TOP + BOARD_HEIGHT

SILK_TEXT_SIZE = 0.8
SILK_TEXT_THICKNESS = 0.2

DIGITAL_HEADER_NETS = {
    "1": "+3V3",
    "2": "GND",
    "3": "SS",
    "4": "MOSI",
    "5": "MISO",
    "6": "SCLK",
    "7": "IRQ0",
    "8": "IRQ1",
    "9": "CF1",
    "10": "CF2",
    "11": "CF3_ZX",
    "12": "CF4_DREADY",
    "13": "RESET",
    "14": "CLKIN",
    "15": "CLKOUT",
    "16": "GND",
}

CURRENT_JACK_NETS = {
    "CTA1": {"T": "IAP_J", "S": "IAN_J", "R": "GND"},
    "CTB1": {"T": "IBP_J", "S": "IBN_J", "R": "GND"},
    "CTC1": {"T": "ICP_J", "S": "ICN_J", "R": "GND"},
    "CTN1": {"T": "INP_J", "S": "INN_J", "R": "GND"},
}

YHDC_BURDEN_RESISTOR_NETS = {
    "R17": {"1": "IAP_J", "2": "IAN_J"},
    "R18": {"1": "IBP_J", "2": "IBN_J"},
    "R19": {"1": "ICP_J", "2": "ICN_J"},
    "R20": {"1": "INP_J", "2": "INN_J"},
}

VOLTAGE_TERMINAL_NETS = {
    "J2": {"1": "VAP_J", "2": "VAN_J"},
    "J3": {"1": "VBP_J", "2": "VBN_J"},
    "J4": {"1": "VCP_J", "2": "VCN_J"},
}

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


def load_footprint(library_path: str | Path, footprint_name: str) -> pcbnew.FOOTPRINT | None:
    key = (str(library_path), footprint_name)
    prototype = FOOTPRINT_PROTOTYPES.get(key)
    if prototype is None:
        prototype = FOOTPRINT_PLUGIN.FootprintLoad(str(library_path), footprint_name)
        if not hasattr(prototype, "CopyFrom"):
            return None
        FOOTPRINT_PROTOTYPES[key] = prototype
    footprint = pcbnew.FOOTPRINT(None)
    footprint.CopyFrom(prototype)
    return footprint


for preload_lib, preload_name in [
    (QFN_LIB, QFN_NAME),
    (AUDIO_LIB, AUDIO_NAME),
    (TERMINAL_LIB, TERMINAL_NAME),
    (HEADER_LIB, HEADER_NAME),
    (RESISTOR_LIB, RESISTOR_NAME),
]:
    load_footprint(preload_lib, preload_name)

PREPARED_FOOTPRINTS: dict[str, pcbnew.FOOTPRINT] = {}
for prepared_ref, prepared_lib, prepared_name in [
    ("J1", HEADER_LIB, HEADER_NAME),
    ("CTA1", AUDIO_LIB, AUDIO_NAME),
    ("CTB1", AUDIO_LIB, AUDIO_NAME),
    ("CTC1", AUDIO_LIB, AUDIO_NAME),
    ("CTN1", AUDIO_LIB, AUDIO_NAME),
    ("J2", TERMINAL_LIB, TERMINAL_NAME),
    ("J3", TERMINAL_LIB, TERMINAL_NAME),
    ("J4", TERMINAL_LIB, TERMINAL_NAME),
]:
    prepared = load_footprint(prepared_lib, prepared_name)
    if prepared is not None:
        PREPARED_FOOTPRINTS[prepared_ref] = prepared


def footprint_by_ref(board: pcbnew.BOARD, ref: str) -> pcbnew.FOOTPRINT | None:
    for fp in board.GetFootprints():
        if hasattr(fp, "GetReference") and fp.GetReference() == ref:
            return fp
    return None


def copy_board_link(old_fp: pcbnew.FOOTPRINT | None, new_fp: pcbnew.FOOTPRINT) -> None:
    if old_fp is None:
        return
    for getter, setter in (("GetPath", "SetPath"), ("GetSheetname", "SetSheetname"), ("GetSheetfile", "SetSheetfile")):
        if hasattr(old_fp, getter) and hasattr(new_fp, setter):
            getattr(new_fp, setter)(getattr(old_fp, getter)())


def set_net(board: pcbnew.BOARD, pad: pcbnew.PAD, net_name: str) -> None:
    net = board.FindNet(net_name)
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
    pad.SetNet(net)


def make_terminal_footprint(ref: str, value: str) -> pcbnew.FOOTPRINT:
    fp = pcbnew.FOOTPRINT(None)
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetFPID(pcbnew.LIB_ID("TerminalBlock_4Ucon", TERMINAL_NAME))
    fp.SetLayer(pcbnew.F_Cu)

    for pad_number, x_offset in [("1", -1.75), ("2", 1.75)]:
        pad = pcbnew.PAD(fp)
        pad.SetNumber(pad_number)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
        pad.SetSize(vmm(2.2, 1.8))
        pad.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_CIRCLE)
        pad.SetDrillSize(vmm(1.1, 1.1))
        pad.SetLayerSet(pad.PTHMask())
        pad.SetPosition(vmm(x_offset, 0.0))
        fp.Add(pad)

    return fp


def ensure_footprint(
    board: pcbnew.BOARD,
    ref: str,
    value: str,
    library: Path,
    footprint_name: str,
    net_map: dict[str, str],
) -> pcbnew.FOOTPRINT:
    old_fp = footprint_by_ref(board, ref)
    needs_add = False
    if old_fp is None or footprint_name not in old_fp.GetFPIDAsString():
        if footprint_name == TERMINAL_NAME:
            fp = make_terminal_footprint(ref, value)
        else:
            fp = PREPARED_FOOTPRINTS.pop(ref, None) or load_footprint(library, footprint_name)
        if fp is None:
            raise RuntimeError(f"Could not load {library / (footprint_name + '.kicad_mod')}")
        fp.SetReference(ref)
        fp.SetValue(value)
        copy_board_link(old_fp, fp)
        if old_fp is not None:
            board.Remove(old_fp)
        needs_add = True
    else:
        fp = old_fp
        fp.SetValue(value)

    pads = fp.Pads()
    if hasattr(pads, "__iter__"):
        for pad in pads:
            net_name = net_map.get(pad.GetNumber())
            if net_name:
                set_net(board, pad, net_name)
    else:
        for pad_number, net_name in net_map.items():
            pad = fp.FindPadByNumber(pad_number)
            if pad is not None:
                set_net(board, pad, net_name)
    if needs_add:
        board.Add(fp)
    return fp


def place(board: pcbnew.BOARD, ref: str, x: float, y: float, angle: float = 0.0) -> None:
    fp = footprint_by_ref(board, ref)
    if fp is None:
        return
    if fp.GetLayer() != pcbnew.F_Cu:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetPosition(vmm(x, y))
    fp.SetOrientationDegrees(angle)


def set_field_style(field: pcbnew.PCB_FIELD) -> None:
    field.SetTextSize(vmm(SILK_TEXT_SIZE, SILK_TEXT_SIZE))
    field.SetTextThickness(pcbnew.FromMM(SILK_TEXT_THICKNESS))


def place_ref(board: pcbnew.BOARD, ref: str, x: float, y: float, angle: float = 0.0, visible: bool = True) -> None:
    fp = footprint_by_ref(board, ref)
    if fp is None:
        return
    field = fp.Reference()
    set_field_style(field)
    field.SetLayer(pcbnew.F_SilkS if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_SilkS)
    field.SetVisible(visible)
    field.SetTextPos(vmm(x, y))
    field.SetTextAngleDegrees(angle)


def set_terminal_model(fp: pcbnew.FOOTPRINT) -> None:
    models = fp.Models()
    if hasattr(models, "clear"):
        models.clear()
    model = pcbnew.FP_3DMODEL()
    model.m_Filename = TERMINAL_MODEL
    model.m_Offset.Set(*TERMINAL_MODEL_OFFSET)
    model.m_Scale.Set(1.0, 1.0, 1.0)
    model.m_Rotation.Set(0.0, 0.0, 0.0)
    fp.Models().append(model)


def normalize_silkscreen(board: pcbnew.BOARD) -> None:
    for fp in board.GetFootprints():
        if not hasattr(fp, "GetFields"):
            continue
        for field in fp.GetFields():
            set_field_style(field)
        fp.Reference().SetLayer(pcbnew.F_SilkS if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_SilkS)
        fp.Value().SetLayer(pcbnew.F_Fab if fp.GetLayer() == pcbnew.F_Cu else pcbnew.B_Fab)


def add_u1_if_missing(board: pcbnew.BOARD) -> None:
    if footprint_by_ref(board, "U1") is not None:
        return

    fp = load_footprint(QFN_LIB, QFN_NAME)
    if fp is None:
        raise RuntimeError(f"Could not load {QFN_LIB / (QFN_NAME + '.kicad_mod')}")

    fp.SetReference("U1")
    fp.SetValue("ADE9000")
    for pad in fp.Pads():
        if pad.GetNumber() == "41":
            pad.SetNumber("EP")
            pad.SetSize(vmm(4.27, 4.27))
        net_name = U1_NETS.get(pad.GetNumber())
        if net_name:
            set_net(board, pad, net_name)
    board.Add(fp)


def ensure_external_connectors(board: pcbnew.BOARD) -> None:
    for ref in ["TP5", "TP6", "TP7", "TP8", "TP9", "TP10", "TP11", "TP12", "TP13"]:
        fp = footprint_by_ref(board, ref)
        if fp is not None:
            board.Remove(fp)

    ensure_footprint(board, "J1", "DIGITAL", HEADER_LIB, HEADER_NAME, DIGITAL_HEADER_NETS)

    for ref, net_map in CURRENT_JACK_NETS.items():
        ensure_footprint(board, ref, "CT stereo", AUDIO_LIB, AUDIO_NAME, net_map)

    for ref, net_map in VOLTAGE_TERMINAL_NETS.items():
        fp = ensure_footprint(board, ref, "Voltage", TERMINAL_LIB, TERMINAL_NAME, net_map)
        set_terminal_model(fp)


def ensure_yhdc_burden_resistors(board: pcbnew.BOARD) -> None:
    for ref, net_map in YHDC_BURDEN_RESISTOR_NETS.items():
        ensure_footprint(board, ref, "2.4R", RESISTOR_LIB, RESISTOR_NAME, net_map)


def place_all(board: pcbnew.BOARD) -> None:
    add_u1_if_missing(board)
    ensure_external_connectors(board)
    ensure_yhdc_burden_resistors(board)

    place(board, "U1", 158.500, 104.000, 0)

    for ref, y in [("CTA1", 88.000), ("CTB1", 101.000), ("CTC1", 114.000), ("CTN1", 127.000)]:
        place(board, ref, 129.500, y, 90)

    for ref, y in [("R17", 90.000), ("R18", 103.000), ("R19", 116.000), ("R20", 129.000)]:
        place(board, ref, 140.000, y, 90)

    for ref, x in [("J2", 155.000), ("J3", 162.000), ("J4", 169.000)]:
        place(board, ref, x, 131.250, 0)

    place(board, "J1", 185.000, 86.100, 0)

    current_rows = ["IAP", "IAN", "IBP", "IBN", "ICP", "ICN", "INP", "INN"]
    for index, _name in enumerate(current_rows):
        y = 88.000 + index * 4.000
        place(board, f"R{2 + index}", 143.500, y, 0)
        place(board, f"C{12 + index}", 147.000, y, 90)

    voltage_refs = [(10, 20), (11, 21), (12, 22), (13, 23), (14, 24), (15, 25)]
    for index, (resistor, cap) in enumerate(voltage_refs):
        y = 116.000 + index * 2.200
        place(board, f"R{resistor}", 160.000, y, 0)
        place(board, f"C{cap}", 163.000, y, 90)

    for ref, x, y, angle in [
        ("C1", 166.500, 99.500, 90),
        ("C2", 164.500, 99.500, 90),
        ("C3", 160.600, 112.000, 90),
        ("C4", 162.500, 112.000, 90),
        ("C5", 154.600, 95.700, 0),
        ("C6", 158.100, 95.700, 0),
        ("C7", 164.500, 112.000, 90),
        ("C8", 166.400, 112.000, 90),
        ("R1", 155.000, 111.500, 0),
        ("C11", 157.000, 111.500, 90),
        ("Y1", 170.000, 104.000, 90),
        ("C9", 170.000, 100.400, 0),
        ("C10", 170.000, 107.600, 0),
        ("R16", 168.000, 113.800, 0),
        ("D1", 172.000, 116.000, 0),
    ]:
        place(board, ref, x, y, angle)

    normalize_silkscreen(board)

    for ref, x, y, angle in [
        ("U1", 158.500, 99.600, 0),
        ("J1", 182.500, 104.500, 90),
        ("J2", 155.000, 126.200, 0),
        ("J3", 162.000, 126.200, 0),
        ("J4", 169.000, 126.200, 0),
        ("CTA1", 124.600, 88.000, 90),
        ("CTB1", 124.600, 101.000, 90),
        ("CTC1", 124.600, 114.000, 90),
        ("CTN1", 124.600, 127.000, 90),
        ("R17", 138.000, 90.000, 0),
        ("R18", 138.000, 103.000, 0),
        ("R19", 138.000, 116.000, 0),
        ("R20", 138.000, 129.000, 0),
        ("R1", 152.800, 111.500, 0),
        ("C11", 157.000, 113.300, 0),
        ("Y1", 172.800, 104.000, 90),
        ("R16", 170.300, 113.800, 0),
        ("D1", 172.000, 118.300, 0),
        ("C1", 167.900, 99.500, 0),
        ("C2", 163.000, 99.500, 0),
        ("C3", 160.600, 114.400, 0),
        ("C4", 162.500, 113.600, 0),
        ("C5", 155.800, 94.000, 0),
        ("C6", 158.100, 94.000, 0),
        ("C7", 164.500, 114.400, 0),
        ("C8", 166.400, 113.600, 0),
        ("C9", 170.000, 98.700, 0),
        ("C10", 170.000, 109.300, 0),
    ]:
        place_ref(board, ref, x, y, angle)

    for index in range(8):
        y = 88.000 + index * 4.000
        place_ref(board, f"R{2 + index}", 141.300, y, 0)
        place_ref(board, f"C{12 + index}", 149.300, y, 0)

    for index in range(6):
        y = 116.000 + index * 2.200
        place_ref(board, f"R{10 + index}", 157.800, y, 0)
        place_ref(board, f"C{20 + index}", 165.100, y, 0)


def main() -> None:
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    place_all(board)
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Placed ADE9000 ATM-style PCB: {BOARD_WIDTH:.2f} mm x {BOARD_HEIGHT:.2f} mm")


if __name__ == "__main__":
    main()