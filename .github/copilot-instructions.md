# Copilot Instructions

This repository is a KiCad 10 ADE9000 breakout board. Keep changes small, schematic-first, and validated with KiCad tools. For energy-monitor work, load the focused skills as applicable: circuit design, layout design, routing, PCB size/shape, and the ADE9000 project overlay.

Project constraints:
- Follow the ADE9000 datasheet Figure 55 test circuit.
- The current board is an ATM90E36-style ADE9000 bench breakout: stereo current-input jacks, voltage screw terminals, grouped SparkFun staggered/friction-fit 0.1 inch digital/debug header, 65 mm x 55 mm rounded board, four M2 holes, and F.Cu/B.Cu GND planes.
- The older compact revision used analog headers, a `J1` 6-pin JST-SH debug connector for `+3V3`, `GND`, `SS`, `MOSI`, `MISO`, and `SCLK`, and named bottom-side CF/IRQ/CLK/RESET test pads. Preserve this only when intentionally working on the compact topology.
- Preserve the existing custom symbol and project-local library setup.

Verified schematic-generation rules:
- Do not assume symbol pin order from visual intuition; read the actual symbol geometry or schematic pin locations first.
- For this project, bare net labels placed on passive pins are not sufficient for reliable ERC connectivity.
- Use `connect_to_net` when available. If scripting around the MCP server, emulate it exactly: pin endpoint -> short wire stub -> net label at the stub end.
- When connecting passives, headers, or test pads, use the exact pin endpoint rather than guessed body coordinates.
- Re-run ERC after each connectivity pass and treat zero ERC errors as the minimum acceptable result.

KiCad MCP notes:
- The workspace MCP configuration lives in `.vscode/mcp.json`.
- KiCad 10 Python is `C:/Program Files/KiCad/10.0/bin/python.exe`.
- KiCad CLI ERC command:
  `& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc --format json --output "c:\Users\tisha\dev\ADE9000_Breakout\erc.json" "c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_sch"`

Verified PCB routing rules:
- The compact QFN breakout routes cleanly with 0.15 mm tracks, 0.15 mm clearance, 0.45 mm vias, and 0.20 mm via drills.
- The ATM-style board uses a `Power` netclass for `+3V3`, `AVDDOUT`, and `DVDDOUT` with 0.25 mm tracks and 0.50/0.25 mm vias; route with this netclass before Freerouting instead of post-widening dense routes.
- Apply GND planes after routing with `scripts/apply_power_planes.py`; use planes for GND return rather than widening every GND trace.
- The JST-SH redesign needs the bottom-side TP5-TP13 pads placed along the lower board edge; the older mid-board test-pad cluster blocks the SPI/JST fanout and leaves KiCad-visible unconnected items after SES import.
- Keep the project `.kicad_pro` DRC rules aligned with the board routing rules; KiCad CLI validates the main board using project constraints, while temporary renamed boards can appear clean with only board-local settings.
- Export fresh DSN files with KiCad Python `pcbnew.ExportSpecctraDSN`; the MCP DSN exporter can use stale in-memory copper during this project.
- A fully routed board should report 0 unconnected items and 0 non-library DRC violations; the remaining `lib_footprint_mismatch` warnings are expected unless footprints are refreshed from libraries.

Known outcome from debugging this design:
- The rewired schematic reaches zero ERC errors.
- The PCB routes to zero unconnected items with J1 JST-SH and bottom-edge TP5-TP13 preserved.
- Final PCB DRC has only expected `lib_footprint_mismatch` warnings after silkscreen cleanup.
- Remaining ERC warnings are dominated by `endpoint_off_grid` plus one footprint-link warning; there are zero ERC errors.
- If reducing warnings, fix placement/grid alignment first instead of reverting to label-only connectivity.