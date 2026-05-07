# Copilot Instructions

This repository is a KiCad 10 ADE9000 breakout board. Keep changes small, schematic-first, and validated with KiCad tools.

Project constraints:
- Follow the ADE9000 datasheet Figure 55 test circuit.
- Break out only `+3V3`, `GND`, and the analog input pairs on 0.1 inch headers.
- Keep SPI, CF, IRQ, CLK, and RESET on test pads to minimize board size.
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

Known outcome from debugging this design:
- The rewired schematic reaches zero ERC errors.
- Remaining ERC warnings are dominated by `endpoint_off_grid` from symbol placement and inherited wire endpoints.
- If reducing warnings, fix placement/grid alignment first instead of reverting to label-only connectivity.