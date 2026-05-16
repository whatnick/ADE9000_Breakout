---
name: whatnick-energy-monitor-layout-design
description: "Use when: placing components, connectors, references, markings, or test pads on whatnick-style energy-monitor PCBs. Covers analog/digital partitioning, connector placement, decoupling placement, CT jack and screw terminal layout, silkscreen/reference rules, and deterministic KiCad Python placement workflows."
argument-hint: "target board or placement task"
---

# Whatnick Energy Monitor Layout Design

Use this skill after the circuit is defined and before routing. The goal is a board that is easy to wire, easy to probe, and friendly to the autorouter while keeping analog measurement paths short and readable.

Reference layouts:

- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/place_pcb.py`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/move_refs_to_silkscreen.py`
- `c:/Users/tisha/dev/ATM90E36_Breakout_KiCAD/ATM90E36_Breakout/ATM90E36_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/V93xx_Breakout/V9360_Breakout/V9360_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/V93xx_Breakout/V9381_Breakout/V9381_Breakout.kicad_pcb`

## Placement Intent

- Place the monitor IC first, usually near the center, with pin banks facing their related circuits.
- Keep analog conditioning between the field connector and the IC pin it serves.
- Put current inputs, voltage inputs, power/debug headers, and digital headers on board edges with readable pin order from the board edge.
- Keep high-touch connectors mechanically accessible; avoid burying screw terminals, jacks, or debug headers behind tall parts.
- Keep clock parts close to clock pins and away from noisy digital routing.
- Keep decoupling capacitors tight to the IC supply/reference pins with very short GND return paths.
- Use deterministic KiCad Python scripts for nontrivial board placement so the board can be regenerated.

## Analog And Digital Partitioning

- Put analog input connectors on one side or along the edge nearest the analog pin bank.
- Put digital/debug signals on the opposite side when board size allows.
- Keep SPI/UART/CF/IRQ/reset routing corridors away from current and voltage input filters.
- In compact boards, bottom-side test pads can reduce front-side crowding. In larger bench boards, prefer a grouped side header for digital signals.
- For ATM-style energy boards, stereo current jacks and voltage screw terminals should be grouped by channel and labeled so wiring order is obvious.

## Connector Placement Patterns

- Compact V93XX style: one 0.1 inch header and bottom-side test pads on a small rounded board.
- Compact ADE9000 JST style: `J1` JST-SH for power/SPI, `J2`/`J3` for analog pairs, bottom-edge test pads for CF/IRQ/clock/reset.
- ATM-style bench board: stereo jacks for current clamp inputs, screw terminals for voltage inputs, and a 0.1 inch digital/debug header along one side for breadboard or logic-analyzer access.
- Keep connector references visible on silkscreen and orient values on Fab only.

## Decoupling And Support Placement

- Place each decoupling capacitor adjacent to its associated IC pin; do not gather decouplers into a remote cluster.
- Pair AVDDOUT/DVDDOUT/REF capacitors with their pins and nearby GND access.
- Keep oscillator/crystal parts short, symmetric, and isolated from long digital traces.
- Place reset pull-ups/caps near reset pins unless a connector-driven reset path needs edge access.
- Place burden/multiplier resistors near the jack-side current pair before the anti-alias path enters the IC-side filter rows.

## Reference And Silkscreen Rules

- Reference designators live on the matching silkscreen layer: `F.SilkS` for front-side footprints and `B.SilkS` for back-side footprints.
- Values stay on Fab layers to keep silkscreen readable.
- Mounting-hole `H*` references and values are intentionally hidden.
- Keep every component, connector, and test-pad reference visible unless it is a mounting hole.
- Move or rotate references to avoid pads, copper, board edges, and other text.
- Use `scripts/move_refs_to_silkscreen.py` with KiCad 10 Python to bulk-migrate references from Fab to silkscreen.

Default silkscreen style:

- Compact labels: 0.8 mm text height and 0.2 mm stroke when DRC/project rules allow.
- Board identity on front when space allows.
- Attribution/version/OSHW logo on back after placement is stable.

## Deterministic KiCad Python Pattern

Run placement scripts with KiCad 10 Python:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\scripts\place_pcb.py
```

Script guidelines:

- Define board geometry and connector/channel constants near the top.
- Use helpers such as `place`, `place_bottom`, and `set_net` instead of repeating coordinate logic.
- Load exact footprints with `pcbnew.FootprintLoad` when library naming differs from schematic symbols.
- For ADE9000, KiCad 10 lacks the exact `EP4.27x4.27mm` QFN footprint; load the `EP4.6x4.6mm` footprint and resize/renumber the exposed pad to `EP`.
- Place refs before adding new Edge.Cuts or mounting-hole shapes if KiCad SWIG collections are fragile.
- If new footprint fields need to be hidden after insertion, post-process the serialized `.kicad_pcb` properties when SWIG field objects are unstable.

PowerShell note: do not use bash heredocs. Use checked-in scripts or `python -c` one-liners.

## Layout DRC Gate

Before routing, DRC should have no placement/mechanical blockers:

- no `courtyards_overlap`
- no `copper_edge_clearance`
- no `hole_clearance` or `hole_to_hole`
- no `pth_inside_courtyard` or `npth_inside_courtyard`
- no `silk_overlap`, `silk_over_copper`, or `silk_edge_clearance` caused by new placement

Unconnected items are expected before routing; all other DRC issues should be understood before exporting DSN.
