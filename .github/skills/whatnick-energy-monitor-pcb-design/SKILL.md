---
name: whatnick-energy-monitor-pcb-design
description: "Use when: placing, routing, reviewing, or validating KiCad PCB layouts for whatnick-style energy monitor breakouts such as ADE9000, V9360, or V9381. Covers compact board outline, headers, bottom-side test pads, silkscreen rules, routing workflow, Freerouting, and DRC validation."
argument-hint: "target board or PCB task"
---

# Whatnick Energy Monitor PCB Design

Use this skill for PCB placement, routing, and DRC cleanup on compact whatnick-style energy monitor breakouts.

Reference boards:

- `c:/Users/tisha/dev/V93xx_Breakout/V9360_Breakout/V9360_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/V93xx_Breakout/V9381_Breakout/V9381_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/V9261F_Breakout/V9261F_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/MCP39xx_Breakout/MCP3909_Breakout/MCP3909_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/place_pcb.py`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/apply_mechanical.py`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/apply_board_markings.py`

## Layout Intent

Keep the board compact, breadboard-friendly, and manufacturable while preserving access to power, analog inputs, and debug pins.

- Use the V93XX breakout physical style as the default visual reference.
- Keep the main IC and support passives on the front side.
- Keep headers on the front side along board edges.
- Put test pads and optional logos on the bottom side to reduce front-side crowding.
- Prefer reproducible KiCad Python placement scripts for nontrivial placement changes.

## Board Outline Style

The V9360, V9381, and ADE9000 boards use a similar compact rounded/chamfered rectangle. MCP3909 is the rounded-corner reference.

- Board envelope is about `38.2 mm x 28.04 mm` including edge stroke.
- ADE9000 script constants use `38.100 mm x 27.940 mm` with `0.1 mm` Edge.Cuts width.
- Round/chamfer the corners by about `5.08 mm`; MCP3909 uses 5.08 mm radius corner arcs plus straight Edge.Cuts segments.
- Keep copper, holes, test pads, and silkscreen clear of rounded/chamfered edges before routing.

## Mounting Hole Pattern

For boards that need mounting holes, use standard M2 NPTH holes while preserving the compact breakout footprint.

- Use four `MountingHole:MountingHole_2.2mm_M2` holes when board space allows.
- Implement them as NPTH circular pads with `2.2 mm` drill and `2.2 mm` pad size, no net, excluded from BOM and position files.
- Place holes near corners but outside component courtyards and away from routed copper. On ADE9000, the validated positions are approximately:
  - `H1`: `(124.235, 85.000)`
  - `H2`: `(155.535, 85.000)`
  - `H3`: `(124.235, 108.650)`
  - `H4`: `(155.800, 108.550)`
- Hide mounting-hole reference and value fields; H* designators are intentionally omitted from silkscreen to keep NPTH corners clear.
- After adding holes, DRC must not introduce `npth_inside_courtyard`, `hole_clearance`, `copper_edge_clearance`, `silk_over_copper`, or `silk_overlap` violations.
- MCP3909 has the rounded-corner outline style but no M2 mounting-hole footprint precedent; use ADE9000's validated M2 setup as the local pattern.

## Placement Pattern

Use these placement rules before routing:

1. Place the monitor IC near the center with pin banks facing their support circuits.
2. Place analog anti-alias resistors/capacitors as short rows between IC pins and analog headers.
3. Place voltage/current input headers at the edges and keep their pin order readable from the board edge.
4. Place power header separately when the design has a dedicated power header.
5. Place crystals/oscillators close to clock pins; keep load capacitors tight and symmetric.
6. Place decoupling capacitors close to their supply/reference pins, with GND return kept short.
7. Put digital/debug test pads on B.Cu. V9381 uses bottom-side test pads along the left/right edges; ADE9000 uses a two-row bottom-side cluster.
8. Add bottom-side OSHW/logo marks only after electrical/mechanical placement is stable.

## Board Markings

Use V9261F as the marking style reference for project identity and attribution.

- Put the board title on front silkscreen when space allows. ADE9000 uses `ADE9000 Breakout` rotated vertically along the left front edge.
- Put attribution/version text on back silkscreen: `by Tisham Dhar`, `https://whatnick.com`, and `v0.1 <date>`.
- Use `0.8 mm` silkscreen text with `0.2 mm` thickness for marking text unless DRC/project rules require larger.
- Add the OSHW logo on the back side after placement is stable; use V9261F's B.Cu `Symbol:OSHW-Logo2_7.3x6mm_SilkScreen` footprint as the reference style.
- Keep logo and attribution text clear of bottom-side test pads, mounting holes, board edges, and routed copper; rerun DRC after adding markings.

## Style Details

- Default compact silkscreen text: `0.8 mm x 0.8 mm`, `0.2 mm` thickness.
- **Reference designators live on the silkscreen layer** — `F.SilkS` for front-side footprints, `B.SilkS` for back-side footprints. Never place references on Fab layers, except intentionally hidden mounting-hole references.
- **Values stay on the Fab layer** — `F.Fab` for front, `B.Fab` for back. This keeps the board readable while decluttering the silkscreen.
- Use `scripts/move_refs_to_silkscreen.py` (KiCad 10 Python) to bulk-migrate any board that has references on Fab layers.
- If the board is too dense, stagger, rotate, or move reference fields while keeping component, connector, and test-pad reference designators visible on silkscreen.
- Do not leave silkscreen over pads, copper, or board edges.
- Test pads should not overlap each other or through-hole header pads, even on opposite sides.
- Treat footprint courtyard overlap as a placement problem unless it is a deliberate, documented exception.

## KiCad Python Workflow

For scripted placement, use KiCad 10 Python:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\scripts\place_pcb.py
```

Script patterns to preserve:

- Define board geometry constants near the top.
- Use helper functions such as `place`, `place_bottom`, and `set_net`.
- Load exact footprints with `pcbnew.FootprintLoad` when KiCad library naming differs from the schematic symbol.
- For ADE9000, KiCad 10 lacks the exact `EP4.27x4.27mm` QFN footprint; load the `EP4.6x4.6mm` footprint and resize/renumber the exposed pad to `EP`.
- Keep placement deterministic so rerunning the script produces the same board.
- For mechanical edits, use `scripts/apply_mechanical.py` to add the rounded outline and M2 holes reproducibly.
- For board identity markings, use `scripts/apply_board_markings.py`; `scripts/apply_mechanical.py` also reapplies these markings after regenerating holes/outline.
- KiCad 10 Python can decay SWIG board collections after removals/additions. Collect existing footprints/drawings into lists before mutating the board, finish reference-field edits before adding new Edge.Cuts shapes, and save without re-querying mutated collections.
- If new board-local mounting-hole fields need to be hidden, post-process the serialized `.kicad_pcb` properties rather than touching new-footprint field SWIG objects after insertion.

PowerShell note: do not use bash heredocs. Use checked-in scripts or `python -c` one-liners.

## Routing Workflow

1. Start from a DRC-clean placement: no shorts, mask bridges, edge-clearance errors, silk/copper errors, or courtyard overlaps.
2. Route analog inputs first, keeping differential/pair geometry tidy and short.
3. Route decoupling and regulator/reference returns with short GND paths.
4. Route clock/crystal nets short and away from noisy digital lines.
5. Route digital/test-pad signals last; vias are acceptable to bottom-side test pads.
6. Use copper pours after critical routes are stable, then refill zones and rerun DRC.
7. If using Freerouting, export DSN, run router, import SES, then manually inspect and clean analog/clock routes.

Installed Freerouting context for this machine:

- Router jar: `C:/Users/tisha/AppData/Roaming/kicad/10.0/freerouting/freerouting.jar`
- JRE 25: `C:/Users/tisha/AppData/Roaming/kicad/10.0/freerouting/jre/jdk-25.0.3+9-jre/bin/java.exe`

## DRC Validation

Run KiCad 10 DRC from the project root:

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --format json --output drc.json .\ADE9000_Breakout.kicad_pcb
```

Before considering placement complete, DRC must have none of these classes:

- `shorting_items`
- `solder_mask_bridge`
- `copper_edge_clearance`
- `courtyards_overlap`
- `silk_overlap`
- `silk_over_copper`
- `silk_edge_clearance`
- `pth_inside_courtyard`
- `npth_inside_courtyard`
- `hole_clearance`
- `hole_to_hole`

Unconnected items are expected until routing is complete. After routing, require zero unconnected items and rerun schematic parity/DRC checks.

## Reference Facts

V93XX examples:

- `V9360_Breakout`: about `38.2 mm x 28.04 mm`, U1 on F.Cu near center, 1x10 header on F.Cu, two B.Cu test pads, OSHW logo on B.Cu.
- `V9381_Breakout`: about `38.2 mm x 28.04 mm`, U1 on F.Cu, 1x10 header on F.Cu, XO32 oscillator, ten B.Cu test pads, OSHW logo on B.Cu.

ADE9000 current pattern:

- U1 QFN centered around `(139.885, 96.393)`.
- J2 current header on the left, J3 voltage header on the right, J1 power header on the front side.
- Board uses MCP3909-style rounded corners with four M2 NPTH holes at `H1` through `H4`.
- Mounting-hole `H*` reference designators are hidden by design.
- Front silkscreen includes `ADE9000 Breakout`; back silkscreen includes `by Tisham Dhar`, `https://whatnick.com`, `v0.1 09/05/2026`, and a B.Cu OSHW logo.
- Digital pads `TP1` through `TP11` on B.Cu.
- Analog filter rows use 0402 passives near U1; bulk/reference caps use 0805/0402 as appropriate.