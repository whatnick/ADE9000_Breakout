"""
Place footprint reference designators on the matching silkscreen layer.
Mounting-hole references are intentionally hidden.
"""
import pcbnew

PCB_PATH = r"c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_pcb"

SILK_TEXT_SIZE_MM = 0.8
SILK_TEXT_THICKNESS_MM = 0.2

REFERENCE_PLACEMENTS = {
    "CTA1": (124.600, 88.000, 90),
    "CTB1": (124.600, 101.000, 90),
    "CTC1": (124.600, 114.000, 90),
    "CTN1": (124.600, 127.000, 90),
    "R17": (138.000, 90.000, 0),
    "R18": (138.000, 103.000, 0),
    "R19": (138.000, 116.000, 0),
    "R20": (138.000, 129.000, 0),
    "J1": (182.500, 104.500, 90),
    "J2": (154.000, 126.200, 0),
    "J3": (162.000, 126.200, 0),
    "J4": (170.000, 126.200, 0),
    "U1": (158.500, 99.600, 0),
    "C1": (167.900, 99.500, 0),
    "C2": (163.000, 99.500, 0),
    "C3": (160.600, 114.400, 0),
    "C4": (162.500, 113.600, 0),
    "C5": (155.800, 94.000, 0),
    "C6": (158.100, 94.000, 0),
    "C7": (164.500, 114.400, 0),
    "C8": (166.400, 113.600, 0),
    "C9": (170.000, 98.700, 0),
    "C10": (170.000, 109.300, 0),
    "C11": (157.000, 113.300, 0),
    "D1": (172.000, 118.300, 0),
    "R1": (152.800, 111.500, 0),
    "R16": (170.300, 113.800, 0),
    "Y1": (172.800, 104.000, 90),
}

for index in range(8):
    REFERENCE_PLACEMENTS[f"R{2 + index}"] = (141.300, 88.000 + index * 4.000, 0)
    REFERENCE_PLACEMENTS[f"C{12 + index}"] = (149.300, 88.000 + index * 4.000, 0)

for index in range(6):
    REFERENCE_PLACEMENTS[f"R{10 + index}"] = (157.800, 116.000 + index * 2.200, 0)
    REFERENCE_PLACEMENTS[f"C{20 + index}"] = (165.100, 116.000 + index * 2.200, 0)


def vmm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def place_references(board: pcbnew.BOARD) -> tuple[int, int]:
    moved = 0
    placed = 0

    for fp in board.GetFootprints():
        ref_field = fp.GetField(pcbnew.FIELD_T_REFERENCE)
        if ref_field is None:
            continue

        target_layer = pcbnew.B_SilkS if fp.GetLayer() == pcbnew.B_Cu else pcbnew.F_SilkS
        src = ref_field.GetLayer()
        if src != target_layer:
            ref_field.SetLayer(target_layer)
            moved += 1
            print(f"  {fp.GetReference()}: layer {board.GetLayerName(src)} -> {board.GetLayerName(target_layer)}")

        ref_field.SetTextSize(vmm(SILK_TEXT_SIZE_MM, SILK_TEXT_SIZE_MM))
        ref_field.SetTextThickness(pcbnew.FromMM(SILK_TEXT_THICKNESS_MM))

        if fp.GetReference().startswith("H") and "MountingHole" in fp.GetValue():
            ref_field.SetVisible(False)
            continue

        placement = REFERENCE_PLACEMENTS.get(fp.GetReference())
        ref_field.SetVisible(placement is not None)
        if placement is not None:
            x_mm, y_mm, angle = placement
            ref_field.SetTextPos(vmm(x_mm, y_mm))
            ref_field.SetTextAngleDegrees(angle)
            placed += 1

    return moved, placed


def main() -> None:
    board = pcbnew.LoadBoard(PCB_PATH)
    moved, placed = place_references(board)
    board.Save(PCB_PATH)
    print(f"\nDone. Moved {moved} reference layer(s), placed {placed} visible reference(s). Saved to {PCB_PATH}")


if __name__ == "__main__":
    main()