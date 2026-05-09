"""
Place footprint reference designators on the matching silkscreen layer.
Mounting-hole references are intentionally hidden.
Values remain on their current Fab layers.
"""
import pcbnew

PCB_PATH = r"c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_pcb"

SILK_TEXT_SIZE_MM = 0.8
SILK_TEXT_THICKNESS_MM = 0.2

REFERENCE_PLACEMENTS = {
    "C1": (149.850, 101.600, 0),
    "C2": (143.000, 101.600, 0),
    "C3": (141.600, 107.000, 0),
    "C4": (143.200, 106.200, 0),
    "C5": (138.200, 86.350, 0),
    "C6": (140.500, 86.350, 0),
    "C7": (145.500, 107.000, 0),
    "C8": (147.100, 106.200, 0),
    "C9": (151.900, 91.250, 0),
    "C10": (151.900, 101.400, 0),
    "C11": (139.100, 105.000, 0),
    "C12": (136.550, 85.350, 0),
    "C13": (138.500, 89.600, 0),
    "C14": (136.550, 90.600, 0),
    "C15": (136.550, 92.500, 0),
    "C16": (128.850, 94.400, 90),
    "C17": (127.450, 96.300, 90),
    "C18": (128.850, 98.200, 90),
    "C19": (127.450, 100.100, 90),
    "C20": (142.650, 87.100, 0),
    "C21": (142.650, 89.000, 0),
    "C22": (142.650, 90.900, 0),
    "C23": (144.350, 92.000, 90),
    "C24": (144.350, 94.700, 90),
    "C25": (144.350, 97.400, 90),
    "D1": (153.000, 109.300, 0),
    "J1": (139.885, 109.200, 0),
    "J2": (126.000, 83.700, 0),
    "J3": (157.650, 90.500, 90),
    "R1": (134.900, 103.200, 0),
    "R2": (130.350, 86.800, 0),
    "R3": (130.350, 88.700, 0),
    "R4": (130.350, 90.600, 0),
    "R5": (130.350, 92.500, 0),
    "R6": (130.350, 94.400, 0),
    "R7": (130.350, 96.300, 0),
    "R8": (130.350, 98.200, 0),
    "R9": (130.350, 100.100, 0),
    "R10": (149.850, 87.100, 0),
    "R11": (149.850, 89.000, 0),
    "R12": (149.850, 90.900, 0),
    "R13": (149.850, 92.800, 0),
    "R14": (149.400, 94.900, 90),
    "R15": (149.400, 97.200, 90),
    "R16": (151.850, 104.700, 0),
    "TP5": (150.800, 116.950, 0),
    "TP6": (154.200, 116.950, 0),
    "TP7": (129.000, 119.950, 0),
    "TP8": (132.400, 119.950, 0),
    "TP9": (147.400, 119.950, 0),
    "TP10": (150.800, 119.950, 0),
    "TP11": (129.000, 116.950, 0),
    "TP12": (132.400, 116.950, 0),
    "TP13": (147.400, 116.950, 0),
    "U1": (139.885, 92.150, 0),
    "Y1": (153.800, 99.000, 90),
}


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

        if fp.GetReference() == "J1" or fp.GetReference().startswith("TP"):
            ref_field.SetVisible(False)
            continue

        if fp.GetReference().startswith("H") and "MountingHole" in fp.GetValue():
            ref_field.SetVisible(False)
            continue

        ref_field.SetVisible(True)

        placement = REFERENCE_PLACEMENTS.get(fp.GetReference())
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
