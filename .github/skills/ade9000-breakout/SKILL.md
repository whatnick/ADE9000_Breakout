---
name: ade9000-breakout
description: "Use when: making ADE9000_Breakout-specific schematic, PCB, routing, validation, or script changes. Layer this project overlay on top of the whatnick energy-monitor circuit-design, layout-design, routing, and pcb-size-shape skills. Covers ADE9000 Figure 55, KiCad 10 commands, local scripts, current ATM-style board facts, and known MCP/KiCad pitfalls."
argument-hint: "ADE9000 schematic, PCB, routing, or validation task"
---

# ADE9000 Breakout Project Overlay

Use this skill for ADE9000_Breakout-specific facts. For reusable design principles, also load the relevant topic skill:

- Circuit/schematic work: `whatnick-energy-monitor-circuit-design`
- Component placement and silkscreen: `whatnick-energy-monitor-layout-design`
- Routing, GND planes, netclasses, and DRC: `whatnick-energy-monitor-routing`
- Board envelope, mounting holes, and connector edge plan: `whatnick-energy-monitor-pcb-size-shape`
- 3D model placement and STEP export: `whatnick-energy-monitor-layout-design`

## Current Board Intent

The current board is an ATM90E36-style ADE9000 bench breakout, not the older tiny header-only board.

- Board envelope: 65 mm x 55 mm with rounded corners and four M2 NPTH mounting holes.
- Current inputs: stereo jack style connectors, with YHDC current-output clamp support.
- Voltage inputs: screw terminals.
- Digital/debug signals: aggregated on one side for breadboard/logical analyzer access.
- `J1` uses the project-local SparkFun `1x16_Locking` staggered/friction-fit footprint from `footprints/SparkFun-Connector.pretty`, placed at `(184.873, 86.1)` with -90 degree rotation so odd-numbered pads stay on the old `x=185.0` route centerline and pins 2-16 run downward.
- GND planes: filled on F.Cu and B.Cu.
- Power routing: `+3V3`, `AVDDOUT`, and `DVDDOUT` use the `Power` netclass with 0.25 mm tracks and 0.50/0.25 mm vias.
- 3D CAD: populated parts use project-local STEP models under `models/step/`; full assembly export lives at `exports/step/ADE9000_Breakout.step`.
- The CT jack STEP model must match the SMT `Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal` footprint; do not substitute the through-hole `SJ1-3523N` model.
- Strip CT jack footprint outlines from F.SilkS on this board; the jacks intentionally overhang the left board edge, and separate `CTA`/`CTB`/`CTC`/`CTN` labels carry the readable silkscreen marking.
- Voltage screw terminals use the Phoenix 1x02 P3.50 mm STEP as a 4Ucon substitute with model offset `(-1.75, -0.05, 0)`; keep pads at the continuous 3.5 mm row positions `J2=155`, `J3=162`, `J4=169`.

The previous compact/JST policy remains useful historical context:

- Compact `J1`: 6-pin JST-SH for `+3V3`, `GND`, `SS`, `MOSI`, `MISO`, and `SCLK`.
- Compact `J2`/`J3`: analog current/voltage inputs.
- Compact `TP5` through `TP13`: CF, IRQ, clock, and reset signals on the lower board edge.
- Do not recreate obsolete compact `TP1` through `TP4` unless intentionally reverting to the older topology.

## Circuit Facts

- Follow the ADE9000 datasheet Figure 55 support circuit unless the user explicitly changes topology.
- `ADE9000_Breakout.kicad_sym` is the authoritative source for custom symbol geometry.
- The ADE9000 exposed-pad pin number is `EP`.
- Anti-alias filters use 1 k series resistors and 22 nF shunt capacitors on analog input paths.
- VDD, AVDDOUT, DVDDOUT, and REF need local decoupling near U1.
- Clock uses a 24.576 MHz crystal with load capacitors unless using an external clock.
- PM0/PM1 are grounded for normal operating mode.
- YHDC current-output clamp support uses R17-R20, 2.4R 0402 burden/multiplier resistors across the jack-side current pairs.

## Schematic Generation Rules

- Inspect actual symbol pin locations before assigning nets.
- For U1 and all passives/connectors/test pads, connect by exact pin endpoint.
- Prefer MCP `connect_to_net` when it uses the exact pin endpoint.
- If scripting raw connectivity, use pin endpoint -> short wire stub -> net label at the stub end.
- Do not use label-only connectivity on passive pins; it looked connected but left pins ERC-open in this project.
- Add `no_connect` only to intentionally unused pins.
- Run KiCad ERC immediately after rewiring.

ERC interpretation:

- `pin_not_connected` means the generator failed electrically.
- `multiple_net_names` usually means two labeled stubs were accidentally merged.
- `endpoint_off_grid` is placement/grid hygiene; fix grid/placement before reworking proven connectivity.

## PCB Script Flow

Primary scripts:

- `scripts/rewire_schematic.py`: deterministic schematic regeneration.
- `scripts/apply_bom_fields.py`: deterministic schematic sourcing fields for Manufacturer, MPN, DigiKey, Mouser, and Description.
- `scripts/export_bom.py`: grouped CSV/XLSX/HTML BOM export from schematic fields.
- `scripts/place_pcb.py`: deterministic footprint/net assignment and placement.
- `scripts/apply_mechanical.py`: rounded outline, M2 holes, and board markings.
- `scripts/move_refs_to_silkscreen.py`: visible reference designators on matching silkscreen layers.
- `scripts/clear_routes_text.py`: remove old `(segment ...)` and `(via ...)` blocks before rerouting.
- `scripts/clear_zones_text.py`: remove old `(zone ...)` blocks before rerouting.
- `scripts/apply_power_planes.py`: add F.Cu/B.Cu GND planes and enforce thicker power copper.

Run scripts with KiCad 10 Python:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\scripts\place_pcb.py
```

PowerShell note: use semicolons for command chaining and avoid bash heredocs.

## Routing Facts

- Clear stale routes and zones before a fresh autoroute.
- Export fresh DSN with KiCad Python `pcbnew.ExportSpecctraDSN`; avoid stale MCP DSN export state.
- Route with the `Power` netclass already present in `.kicad_pro`; post-widening already-routed 0.15 mm power tracks caused clearance errors.
- Use GND planes instead of widening every GND trace.
- For KiCad 10 vias, avoid `PCB_VIA.GetWidth()` without layer context; use `GetFrontWidth()` or set width directly.
- `scripts/apply_power_planes.py` uses solid GND zone connections to avoid a starved thermal on U1 pad 28.

Installed Freerouting context:

- Router jar: `C:/Users/tisha/AppData/Roaming/kicad/10.0/freerouting/freerouting.jar`
- JRE 25: `C:/Users/tisha/AppData/Roaming/kicad/10.0/freerouting/jre/jdk-25.0.3+9-jre/bin/java.exe`

## Validation Commands

STEP export:

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb export step --force --subst-models --output exports\step\ADE9000_Breakout.step .\ADE9000_Breakout.kicad_pcb
```

ERC:

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc --format json --output erc.json .\ADE9000_Breakout.kicad_sch
```

DRC:

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --format json --output drc.json .\ADE9000_Breakout.kicad_pcb
```

Expected final PCB state:

- Zero DRC errors.
- Zero unconnected items.
- Remaining warnings are known library/text/silkscreen warnings unless the task is specifically to eliminate them.
