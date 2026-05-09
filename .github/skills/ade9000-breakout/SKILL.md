# ADE9000 Breakout Schematic Skill

Use this skill when editing or regenerating the ADE9000 breakout schematic with the KiCad MCP server.

## Goal

Maintain a compact ADE9000 breakout that is electrically correct in KiCad 10:
- analog inputs on 0.1 inch headers
- `+3V3`, `GND`, `SS`, `MOSI`, `MISO`, and `SCLK` on `J1` 6-pin JST-SH
- CF, IRQ, CLK, and RESET debug signals on named test pads
- datasheet Figure 55 support circuitry populated

## Validated workflow

1. Inspect actual symbol pin locations before assigning nets.
2. For U1 and all passives/connectors/test pads, connect by exact pin endpoint.
3. Prefer the MCP `connect_to_net` flow.
4. If scripting raw MCP calls, create connectivity as:
   - short wire stub from the pin endpoint
   - net label at the stub end
5. Add `no_connect` only to intentionally unused pins.
6. Run KiCad ERC immediately after rewiring.

## Important project facts

- `ADE9000_Breakout.kicad_sym` is the authoritative source for custom symbol geometry.
- The ADE9000 exposed-pad pin number is `EP`.
- The earlier failure mode in this project was label-only connectivity: it looked connected but left passive pins electrically open in ERC.
- The corrected wiring pattern removed all ERC errors.

## ERC interpretation

- `pin_not_connected` means the generator failed electrically.
- `multiple_net_names` usually means two labeled stubs were accidentally merged.
- `endpoint_off_grid` is a placement/grid hygiene issue; fix component placement before reworking net connectivity.

## Compact breakout rules

- Keep `J1` as `Connector_JST:JST_SHL_SM06B-SHLS-TF_1x06-1MP_P1.00mm_Horizontal` with pinout `+3V3`, `GND`, `SS`, `MOSI`, `MISO`, `SCLK`.
- Keep `J2` and `J3` for analog current/voltage inputs.
- Keep `IRQ0`, `IRQ1`, `CF1`, `CF2`, `CF3_ZX`, `CF4_DREADY`, `RESET`, `CLKIN`, and `CLKOUT` on `TP5` through `TP13`.
- Do not recreate obsolete `TP1` through `TP4`; those SPI signals now live on `J1`.
- For the PCB, place `TP5` through `TP13` on the lower board edge before routing. The older mid-board TP cluster blocks JST/SPI fanout.

## Canonical validation command

`& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc --format json --output "c:\Users\tisha\dev\ADE9000_Breakout\erc.json" "c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_sch"`

Expected final schematic state: zero ERC errors. Existing warnings are placement/grid hygiene, not connectivity failures.