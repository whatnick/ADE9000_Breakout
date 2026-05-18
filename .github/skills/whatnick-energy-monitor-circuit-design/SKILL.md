---
name: whatnick-energy-monitor-circuit-design
description: "Use when: designing, reviewing, or regenerating energy-monitor schematics for ADE9000, ATM90E36, V9360, V9381, V9261F, MCP39xx, or similar metering breakouts. Covers datasheet circuits, analog input conditioning, current clamp burden/multiplier choices, power/reference/clock support circuits, connector policy, KiCad symbol connectivity, and ERC validation."
argument-hint: "target IC, schematic, or circuit block"
---

# Whatnick Energy Monitor Circuit Design

Use this skill for the electrical design of whatnick-style energy-monitor boards before PCB placement or routing. Start from the datasheet reference circuit, then adapt connector exposure and conditioning to the intended board format.

Reference designs:

- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_sch`
- `c:/Users/tisha/dev/ATM90E36_Breakout_KiCAD/ATM90E36_Breakout/ATM90E36_Breakout.kicad_sch`
- `c:/Users/tisha/dev/V93xx_Breakout/V9360_Breakout/V9360_Breakout.kicad_sch`
- `c:/Users/tisha/dev/V93xx_Breakout/V9381_Breakout/V9381_Breakout.kicad_sch`
- `c:/Users/tisha/dev/V9261F_Breakout/V9261F_Breakout.kicad_sch`
- `c:/Users/tisha/dev/MCP39xx_Breakout/MCP3909_Breakout/MCP3909_Breakout.kicad_sch`

## Circuit Intent

Build electrically correct monitor breakouts that are easy to instrument:

- Follow the target IC datasheet reference/test circuit first.
- Preserve project-local symbols and footprints for metering ICs; do not replace custom libraries with guessed global parts.
- Expose measurement inputs through connectors sized for the intended use: compact headers for small breakouts, stereo jacks and screw terminals for clamp/line-input bench boards.
- Keep debug/digital access compact and grouped, using a JST/debug connector or breadboard-friendly side header instead of scattering test pads across the board.
- Add onboard support circuits for supplies, reference outputs, reset, clock, and mode pins before optimizing the PCB.

## Datasheet-First Procedure

1. Identify the exact IC, package, and exposed-pad naming from the datasheet and part lookup.
2. Inspect the actual KiCad symbol geometry and pin names before wiring; never infer pin order from package drawings or symbol appearance.
3. Create or preserve a project-local symbol when the global KiCad library does not contain an exact part.
4. Implement the application circuit blocks:
   - supply input filtering and regulator/output decoupling
   - reference decoupling
   - analog anti-alias filters on voltage and current channels
   - reset pull-up/RC or supervisor connection where required
   - crystal, oscillator, or external clock network
   - mode straps and no-connects for datasheet-confirmed unused pins
5. Add `PWR_FLAG` symbols only where KiCad ERC needs proof that a net is driven.
6. Run ERC after every generated or bulk connectivity pass.

## Analog Input Conventions

Use explicit net names around every conditioning component:

- IC-side filtered nets use the IC signal name: `IAP`, `IAN`, `VAP`, `VAN`, and so on.
- Connector-side nets use a suffix such as `_J`, `_IN`, or the existing project convention when a series resistor separates the connector from the IC pin.
- Keep each differential or pseudo-differential pair easy to inspect in the schematic.
- Place shunt capacitors to `GND` only where the datasheet/filter design requires them.
- Keep voltage divider, burden, and multiplier resistor roles visually distinct from anti-alias series resistors.

Common patterns:

- ADE9000 Figure 55 style: 1 k series and 22 nF shunt anti-alias filters on analog inputs; decouple VDD, AVDDOUT, DVDDOUT, and REF.
- V93XX compact style: small series resistors and shunt capacitors near the monitor IC; preserve datasheet-specific values.
- ATM-style clamp boards: CT jack inputs feed conditioning networks, and voltage inputs use screw terminals and divider/filter networks sized for the measurement range.

## Current Clamp Support

When supporting YHDC or similar current-output clamps:

- Add a clearly labeled burden/multiplier resistor across each jack-side current pair.
- Keep burden resistors close to the input connector but before the IC-side anti-alias network.
- Use explicit pair nets such as `IAP_J`/`IAN_J`, `IBP_J`/`IBN_J`, `ICP_J`/`ICN_J`, and `INP_J`/`INN_J`.
- For the ADE9000 ATM-style board, R17-R20 are 2.4R 0603 burden/multiplier resistors across the four current jack pairs for hand assembly.

## Digital And Debug Policy

Choose the debug exposure based on board format:

- Compact breakouts: put power and analog measurement pins on 0.1 inch headers; place CF, IRQ, reset, clock, and other low-use digital signals on named bottom-side test pads.
- Compact ADE9000 JST policy: use `J1` as a 6-pin JST-SH connector for `+3V3`, `GND`, `SS`, `MOSI`, `MISO`, and `SCLK`; keep CF/IRQ/CLK/RESET on named test pads.
- Larger ATM-style boards: aggregate digital signals on one board side with a breadboard-friendly 0.1 inch header so logic-analyzer and MCU hookup is obvious.
- Keep signal names literal on debug connectors and test pads: `SS`, `MOSI`, `MISO`, `SCLK`, `IRQ0`, `CF1`, `RESET`, `CLKIN`, etc.

## KiCad Connectivity Rules

For generated or MCP-edited schematics, connectivity must be physical, not label-only:

- Prefer MCP `connect_to_net` when it uses the exact pin endpoint.
- If scripting manually, emulate `connect_to_net`: pin endpoint -> short wire stub -> net label at the stub end.
- Use exact pin endpoints for IC pins, passives, connectors, and test pads.
- Do not place bare labels on passive pin bodies or guessed component coordinates; this caused ERC-open nets in the ADE9000 work.
- Add no-connect markers only to datasheet-confirmed unused pins.

## ERC Validation

Run KiCad 10 ERC from the project root:

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc --format json --output erc.json .\ADE9000_Breakout.kicad_sch
```

Acceptable schematic state:

- Zero ERC errors.
- No floating labels or unintended `multiple_net_names` violations.
- No unconnected monitor IC pins unless they have datasheet-backed no-connect markers.
- Warnings are understood and documented. `endpoint_off_grid` is placement/grid hygiene; fix alignment before changing proven connectivity.
