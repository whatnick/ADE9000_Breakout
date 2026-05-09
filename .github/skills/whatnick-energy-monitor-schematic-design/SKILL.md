---
name: whatnick-energy-monitor-schematic-design
description: "Use when: creating, reviewing, or regenerating KiCad schematics for whatnick-style energy monitor breakouts such as ADE9000, V9360, or V9381. Covers compact header/test-pad policy, analog input filters, project-local symbols, exact pin connectivity, and ERC validation."
argument-hint: "target IC or schematic task"
---

# Whatnick Energy Monitor Schematic Design

Use this skill for KiCad schematic work on compact energy monitor breakouts in the whatnick style. Reference designs are:

- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_sch`
- `c:/Users/tisha/dev/V93xx_Breakout/V9360_Breakout/V9360_Breakout.kicad_sch`
- `c:/Users/tisha/dev/V93xx_Breakout/V9381_Breakout/V9381_Breakout.kicad_sch`
- `c:/Users/tisha/dev/V93xx_Breakout/V93xx_Breakout.kicad_sym`
- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_sym`

## Design Intent

Create small, breadboard-friendly energy monitor breakouts that expose the useful measurement and power pins while keeping digital/debug signals compact.

- Put power and analog measurement inputs on 0.1 inch headers.
- Put digital, clock, reset, IRQ, CF, UART, and SPI-style signals on test pads unless the reference board intentionally uses a compact debug connector.
- Preserve project-local symbols and footprints; do not replace custom libraries with guessed global library parts.
- Follow the IC datasheet reference or test circuit before optimizing the board.

## Reference Patterns

Use V93XX boards for style and compactness:

- `V9360_Breakout`: single `Conn_01x10_Pin` header, 2 bottom test pads, V9360 in project-local SOP footprint.
- `V9381_Breakout`: single `Conn_01x10` header, 10 bottom test pads, XO32 oscillator, V9381 in project-local symbol library.
- Both use onboard analog conditioning and local `V93xx_Breakout:V9360` / `V93xx_Breakout:V9381` symbols.

Use ADE9000 for the newer split-header compact policy:

- `J1`: 6-pin JST-SH for `+3V3`, `GND`, `SS`, `MOSI`, `MISO`, and `SCLK`.
- `J2`/`J3`: current and voltage analog pairs only.
- `TP5` through `TP13`: CF, IRQ, clock, and reset signals.
- `TP1` through `TP4` are obsolete in the JST-SH revision and should not be regenerated.
- Figure 55 support circuit is populated on board.

## Schematic Procedure

1. Identify the exact IC/package from datasheet and part lookup.
2. Inspect the actual KiCad symbol geometry and pin names before wiring. Never infer pin order from the package drawing or visual intuition.
3. Keep or create a project-local symbol library for the monitor IC when the global KiCad library does not contain an exact part.
4. Build the schematic around the datasheet application circuit:
   - supply decoupling on every supply and regulator-output/reference pin
   - analog anti-aliasing filters on voltage/current inputs
   - reset pull-up/RC where the datasheet requires it
   - crystal or oscillator network where required
   - optional CF/activity LED only when it is already in the design intent
5. Use clear net naming:
   - IC-side filtered analog nets use the IC signal name (`IAP`, `IAN`, `VAP`, `VAN`, etc.).
   - Header-side nets use a suffix (`_J`, `_IN`, or the existing project convention) when a series resistor separates header from IC pin.
   - Digital pads keep literal signal names (`SS`, `MOSI`, `MISO`, `SCLK`, `IRQ0`, `CF1`, `RESET`, etc.).
6. Add no-connect markers only to datasheet-confirmed unused pins.
7. Add `PWR_FLAG` symbols when KiCad ERC needs proof that a net is driven (`+3V3`, sometimes `GND`).

## Connectivity Rules

For generated or MCP-edited schematics, connectivity must be physical, not label-only.

- Prefer MCP `connect_to_net` when it uses the exact pin endpoint.
- If scripting manually, emulate `connect_to_net`: pin endpoint -> short wire stub -> net label at the stub end.
- Use exact pin endpoints for passives, headers, and test pads.
- Avoid placing a bare label on a passive pin body or guessed component coordinate; this caused false-looking but ERC-open nets in the ADE9000 work.
- After every bulk wiring pass, run ERC before changing layout aesthetics.

## Energy Monitor Circuit Conventions

Common V93XX-style conditioning:

- Current/voltage inputs use small series resistors and shunt capacitors to ground.
- V9360/V9381 references include values such as `1k`, `2R2`, `33n`, `100p`, `100n`, and `4.7u`; preserve datasheet-specific values for the target IC.
- External measurement nets are distinct from filtered IC pins when the resistor is in series.

ADE9000-specific conditioning:

- Anti-alias filters: 1 k + 22 nF on each analog input path.
- Supply/reference decoupling: VDD, AVDDOUT, DVDDOUT, and REF are decoupled per Figure 55.
- Clock: 24.576 MHz crystal with 16 pF caps unless using an external clock.
- PM0/PM1 are grounded for normal operating mode.

## Validation

Use KiCad 10 validation commands from the project root.

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc --format json --output erc.json .\ADE9000_Breakout.kicad_sch
```

Acceptable schematic state:

- Zero ERC errors.
- Any warnings are understood and documented.
- No floating labels.
- No unintended `multiple_net_names` or unconnected monitor pins.

When ERC fails, fix root connectivity first, not visual placement. Re-run ERC after each connectivity pass.