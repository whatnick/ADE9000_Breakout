---
name: whatnick-energy-monitor-routing
description: "Use when: routing, autorouting, adding ground planes, configuring net classes, importing SES files, or validating DRC for whatnick-style energy-monitor PCBs. Covers analog routing priorities, power trace widths, GND planes, Freerouting workflow, KiCad 10 DSN/SES handling, and zero-error DRC expectations."
argument-hint: "target board or routing task"
---

# Whatnick Energy Monitor Routing

Use this skill once placement is DRC-clean. Route critical analog, clock, power, and return paths deliberately, and use autorouting only with rules that match the intended copper widths.

Reference scripts and boards:

- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_pro`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/clear_routes_text.py`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/clear_zones_text.py`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/apply_power_planes.py`

## Routing Priorities

1. Confirm placement DRC is clean except expected unconnected items.
2. Route current and voltage input pairs with short, tidy paths through their filters.
3. Route reference, regulator output, and decoupling connections with short return loops.
4. Route clock/crystal nets short and away from SPI/CF/IRQ runs.
5. Route digital/debug signals after analog and clock paths have stable corridors.
6. Add or refill GND planes after critical routes are stable.
7. Run DRC and inspect both clearance errors and unconnected items.

## Net Classes And Widths

Keep `.kicad_pro` rules aligned with the board being validated; KiCad CLI DRC uses project constraints.

Compact QFN breakout rules:

- Default: 0.15 mm track width, 0.15 mm clearance, 0.45 mm vias, 0.20 mm via drills.
- This routes dense ADE9000 compact/JST layouts cleanly when test pads are placed along the lower board edge.

ATM-style ADE9000 rules:

- Default signal routing can remain 0.15 mm/0.15 mm for dense IC fanout.
- Use a `Power` netclass for `+3V3`, `AVDDOUT`, and `DVDDOUT` before routing:
  - 0.25 mm tracks
  - 0.50 mm vias
  - 0.25 mm via drills
  - 0.15 mm clearance
- Do not post-widen dense 0.15 mm routes blindly; it creates avoidable clearance errors. Export DSN after the Power netclass is in the project.
- Treat `REF` as a precision/reference node, not a bulk power rail, unless the circuit specifically requires otherwise.
- Use GND planes for return copper; do not widen every `GND` segment in dense analog areas.

## Ground Planes

- Use filled GND zones on both copper layers when board area allows.
- Keep zones inset from board edges and mounting holes enough to avoid copper-edge and hole-clearance issues.
- Refill zones after every routing or mechanical change.
- For the ADE9000 ATM-style board, `scripts/apply_power_planes.py` adds F.Cu/B.Cu GND planes and enforces thicker power routing.
- Solid GND zone pad connections avoid the starved thermal on ADE9000 U1 pad 28; thermal relief can be used elsewhere only when DRC remains clean.

## Freerouting Workflow

Use fresh DSN/SES files. Avoid stale in-memory board state.

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\scripts\clear_routes_text.py .\ADE9000_Breakout.kicad_pcb
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\scripts\clear_zones_text.py .\ADE9000_Breakout.kicad_pcb
& "C:\Program Files\KiCad\10.0\bin\python.exe" -c "import pcbnew; board=pcbnew.LoadBoard(r'ADE9000_Breakout.kicad_pcb'); pcbnew.ExportSpecctraDSN(board, r'ADE9000_Breakout.dsn')"
& "C:\Users\tisha\AppData\Roaming\kicad\10.0\freerouting\jre\jdk-25.0.3+9-jre\bin\java.exe" -jar "C:\Users\tisha\AppData\Roaming\kicad\10.0\freerouting\freerouting.jar" -de .\ADE9000_Breakout.dsn -do .\ADE9000_Breakout.ses -mp 100
& "C:\Program Files\KiCad\10.0\bin\python.exe" -c "import pcbnew; path=r'ADE9000_Breakout.kicad_pcb'; board=pcbnew.LoadBoard(path); pcbnew.ImportSpecctraSES(board, r'ADE9000_Breakout.ses'); pcbnew.SaveBoard(path, board)"
```

After SES import, reapply mechanical/marking scripts if the board flow requires them, then add planes and run DRC.

Installed Freerouting context for this machine:

- Router jar: `C:/Users/tisha/AppData/Roaming/kicad/10.0/freerouting/freerouting.jar`
- JRE 25: `C:/Users/tisha/AppData/Roaming/kicad/10.0/freerouting/jre/jdk-25.0.3+9-jre/bin/java.exe`

## KiCad 10 API Notes

- Export DSN with KiCad Python `pcbnew.ExportSpecctraDSN`; the MCP DSN exporter can use stale copper.
- Import SES with `pcbnew.ImportSpecctraSES`.
- For KiCad 10 vias, do not call `PCB_VIA.GetWidth()` without a layer-aware context. Use `GetFrontWidth()` or set via width directly.
- Clear zones with `scripts/clear_zones_text.py` before rerouting if old filled zones interfere with DSN export or DRC diagnosis.

## DRC Validation

Run KiCad 10 DRC from the project root:

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb drc --format json --output drc.json .\ADE9000_Breakout.kicad_pcb
```

Final routed boards must have:

- Zero DRC errors.
- Zero unconnected items.
- No non-library violations introduced by routing, pours, holes, or silkscreen.
- Remaining warnings are understood, usually `lib_footprint_mismatch`, text size, or legacy silkscreen warnings unless the current task is to eliminate them.
