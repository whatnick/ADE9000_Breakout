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
- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/place_pcb.py`

## Layout Intent

Keep the board compact, breadboard-friendly, and manufacturable while preserving access to power, analog inputs, and debug pins.

- Use the V93XX breakout physical style as the default visual reference.
- Keep the main IC and support passives on the front side.
- Keep headers on the front side along board edges.
- Put test pads and optional logos on the bottom side to reduce front-side crowding.
- Prefer reproducible KiCad Python placement scripts for nontrivial placement changes.

## Board Outline Style

The V9360, V9381, and ADE9000 boards use a similar compact chamfered rectangle.

- Board envelope is about `38.2 mm x 28.04 mm` including edge stroke.
- ADE9000 script constants use `38.100 mm x 27.940 mm` with `0.1 mm` Edge.Cuts width.
- Chamfer the corners by about `5.08 mm`.
- Keep copper, holes, test pads, and silkscreen clear of chamfered edges before routing.

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

## Style Details

- Default compact silkscreen text: `0.8 mm x 0.8 mm`, `0.2 mm` thickness.
- If the board is too dense, move reference fields and footprint artwork to Fab rather than forcing unreadable silkscreen over copper.
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

Unconnected items are expected until routing is complete. After routing, require zero unconnected items and rerun schematic parity/DRC checks.

## Reference Facts

V93XX examples:

- `V9360_Breakout`: about `38.2 mm x 28.04 mm`, U1 on F.Cu near center, 1x10 header on F.Cu, two B.Cu test pads, OSHW logo on B.Cu.
- `V9381_Breakout`: about `38.2 mm x 28.04 mm`, U1 on F.Cu, 1x10 header on F.Cu, XO32 oscillator, ten B.Cu test pads, OSHW logo on B.Cu.

ADE9000 current pattern:

- U1 QFN centered around `(139.885, 96.393)`.
- J2 current header on the left, J3 voltage header on the right, J1 power header on the front side.
- Digital pads `TP1` through `TP11` on B.Cu.
- Analog filter rows use 0402 passives near U1; bulk/reference caps use 0805/0402 as appropriate.