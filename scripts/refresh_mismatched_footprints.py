from __future__ import annotations

import json
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "ADE9000_Breakout.kicad_pcb"
DRC_PATH = ROOT / "drc.json"
KICAD_FOOTPRINTS = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
EXCLUDE_REFS = {"J2", "J3", "J4"}


def mismatch_refs() -> list[str]:
    report = json.loads(DRC_PATH.read_text())
    refs: list[str] = []
    for violation in report.get("violations", []):
        if violation.get("type") != "lib_footprint_mismatch":
            continue
        items = violation.get("items", [])
        if not items:
            continue
        description = items[0].get("description", "")
        prefix = "Footprint "
        if description.startswith(prefix):
            refs.append(description[len(prefix) :])
    return sorted(set(refs) - EXCLUDE_REFS)


def copy_text_state(source: pcbnew.PCB_TEXT, target: pcbnew.PCB_TEXT) -> None:
    target.SetText(source.GetText())
    target.SetPosition(source.GetPosition())
    target.SetTextAngle(source.GetTextAngle())
    target.SetLayer(source.GetLayer())
    target.SetVisible(source.IsVisible())
    target.SetTextSize(source.GetTextSize())
    target.SetTextThickness(source.GetTextThickness())


def find_footprint(board: pcbnew.BOARD, ref: str) -> pcbnew.FOOTPRINT | None:
    for footprint in board.Footprints():
        footprint = pcbnew.Cast_to_FOOTPRINT(footprint)
        if footprint.GetReference() == ref:
            return footprint
    return None


def refreshed_footprint(board: pcbnew.BOARD, ref: str) -> tuple[pcbnew.FOOTPRINT, pcbnew.FOOTPRINT]:
    old = find_footprint(board, ref)
    if old is None:
        raise RuntimeError(f"Footprint {ref} not found on board")

    fpid = old.GetFPID()
    library = str(fpid.GetLibNickname())
    footprint_name = str(fpid.GetLibItemName())
    library_path = KICAD_FOOTPRINTS / f"{library}.pretty"
    if not library_path.exists():
        raise RuntimeError(f"Library path not found for {ref}: {library_path}")

    new = pcbnew.FootprintLoad(str(library_path), footprint_name)
    if new is None:
        raise RuntimeError(f"Unable to load {library}:{footprint_name} for {ref}")

    new.SetReference(old.GetReference())
    new.SetValue(old.GetValue())
    new.SetPosition(old.GetPosition())
    new.SetOrientation(old.GetOrientation())
    new.SetLayer(old.GetLayer())
    new.SetPath(old.GetPath())
    new.SetAttributes(old.GetAttributes())
    new.SetFPID(old.GetFPID())
    copy_text_state(old.Reference(), new.Reference())
    copy_text_state(old.Value(), new.Value())

    for new_pad in new.Pads():
        old_pad = old.FindPadByNumber(new_pad.GetNumber())
        if old_pad is not None:
            new_pad.SetNet(old_pad.GetNet())

    return old, new


def main() -> None:
    refs = mismatch_refs()
    if not refs:
        print("No lib_footprint_mismatch warnings found in drc.json")
        return

    board = pcbnew.LoadBoard(str(BOARD_PATH))
    replacements = []
    for ref in refs:
        replacements.append(refreshed_footprint(board, ref))

    for old, new in replacements:
        board.Remove(old)
        board.Add(new)

    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Refreshed {len(refs)} footprints from KiCad 10 libraries")


if __name__ == "__main__":
    main()
