from __future__ import annotations

import argparse
from pathlib import Path

import pcbnew


BOARD_BBOX_MM = (123.501, 80.004, 188.501, 135.004)
POWER_NETS = {"+3V3", "AVDDOUT", "DVDDOUT"}
POWER_TRACK_WIDTH_MM = 0.25
POWER_VIA_DIAMETER_MM = 0.50
POWER_VIA_DRILL_MM = 0.25
ZONE_EDGE_INSET_MM = 0.60
ZONE_CLEARANCE_MM = 0.20
ZONE_MIN_THICKNESS_MM = 0.20
ZONE_THERMAL_GAP_MM = 0.25
ZONE_THERMAL_SPOKE_MM = 0.30


def vmm(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))


def net_name(track: pcbnew.BOARD_ITEM) -> str:
    if hasattr(track, "GetNetname"):
        return track.GetNetname()
    if hasattr(track, "GetNet") and track.GetNet() is not None:
        return track.GetNet().GetNetname()
    return ""


def widen_power_copper(board: pcbnew.BOARD) -> tuple[int, int]:
    widened_tracks = 0
    widened_vias = 0
    track_width = pcbnew.FromMM(POWER_TRACK_WIDTH_MM)
    via_diameter = pcbnew.FromMM(POWER_VIA_DIAMETER_MM)
    via_drill = pcbnew.FromMM(POWER_VIA_DRILL_MM)

    for track in board.GetTracks():
        if net_name(track) not in POWER_NETS:
            continue
        if type(track).__name__ == "PCB_VIA":
            if track.GetFrontWidth() < via_diameter:
                track.SetWidth(via_diameter)
            if hasattr(track, "SetDrill") and track.GetDrillValue() < via_drill:
                track.SetDrill(via_drill)
            widened_vias += 1
        elif hasattr(track, "SetWidth"):
            if track.GetWidth() < track_width:
                track.SetWidth(track_width)
            widened_tracks += 1

    return widened_tracks, widened_vias


def remove_existing_gnd_zones(board: pcbnew.BOARD) -> int:
    removed = 0
    for zone in list(board.Zones()):
        if zone.GetNetname() == "GND" and zone.GetLayer() in {pcbnew.F_Cu, pcbnew.B_Cu}:
            board.Remove(zone)
            removed += 1
    return removed


def add_gnd_zone(board: pcbnew.BOARD, layer: int, priority: int) -> pcbnew.ZONE:
    left, top, right, bottom = BOARD_BBOX_MM
    inset = ZONE_EDGE_INSET_MM
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(board.FindNet("GND"))
    zone.SetAssignedPriority(priority)
    zone.SetLocalClearance(pcbnew.FromMM(ZONE_CLEARANCE_MM))
    zone.SetMinThickness(pcbnew.FromMM(ZONE_MIN_THICKNESS_MM))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    zone.SetThermalReliefGap(pcbnew.FromMM(ZONE_THERMAL_GAP_MM))
    zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(ZONE_THERMAL_SPOKE_MM))
    zone.SetFillMode(pcbnew.ZONE_FILL_MODE_POLYGONS)
    zone.SetIsFilled(True)
    zone.AppendCorner(vmm(left + inset, top + inset), -1)
    zone.AppendCorner(vmm(right - inset, top + inset), -1)
    zone.AppendCorner(vmm(right - inset, bottom - inset), -1)
    zone.AppendCorner(vmm(left + inset, bottom - inset), -1)
    board.Add(zone)
    return zone


def fill_zones(board: pcbnew.BOARD) -> None:
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())


def main() -> None:
    parser = argparse.ArgumentParser(description="Add GND planes and widen ADE9000 power copper.")
    parser.add_argument("board", type=Path, help="Path to the .kicad_pcb file to update")
    args = parser.parse_args()

    board = pcbnew.LoadBoard(str(args.board))
    widened_tracks, widened_vias = widen_power_copper(board)
    removed_zones = remove_existing_gnd_zones(board)
    add_gnd_zone(board, pcbnew.F_Cu, 0)
    add_gnd_zone(board, pcbnew.B_Cu, 0)
    fill_zones(board)
    pcbnew.SaveBoard(str(args.board), board)
    print(
        f"Widened {widened_tracks} power tracks and {widened_vias} power vias; "
        f"replaced {removed_zones} old GND zone(s) with filled F.Cu/B.Cu planes."
    )


if __name__ == "__main__":
    main()
