---
name: whatnick-energy-monitor-pcb-size-shape
description: "Use when: choosing board size, outline shape, connector edge allocation, mounting holes, rounded corners, or compact versus ATM-style mechanical form for whatnick energy-monitor PCBs. Covers V93XX compact boards, MCP3909 rounded corners, ADE9000 compact/JST and ATM-style board envelopes, M2 holes, and mechanical DRC constraints."
argument-hint: "target board, enclosure, or mechanical format"
---

# Whatnick Energy Monitor PCB Size And Shape

Use this skill when deciding the board envelope, rounded corners, mounting holes, connector edge plan, or compact-versus-bench-board form factor.

Reference boards:

- `c:/Users/tisha/dev/V93xx_Breakout/V9360_Breakout/V9360_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/V93xx_Breakout/V9381_Breakout/V9381_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/MCP39xx_Breakout/MCP3909_Breakout/MCP3909_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ATM90E36_Breakout_KiCAD/ATM90E36_Breakout/ATM90E36_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_pcb`
- `c:/Users/tisha/dev/ADE9000_Breakout/scripts/apply_mechanical.py`

## Form Factor Choice

Choose the board size from how the user will connect to it:

- Compact breakout: use when the goal is a small module exposing IC power and measurement pins with minimal debug access.
- Compact JST debug board: use when SPI/debug needs a reliable cable connector but the board should remain small.
- ATM-style bench board: use when the board needs stereo CT jacks, screw terminals, grouped digital header access, and more comfortable probing.
- Do not force a compact outline when connectors or analog filters cause bad routing, inaccessible labels, or fragile probing.

## Compact Board Style

V9360, V9381, MCP3909, and the compact ADE9000 revisions are the small-board references.

- V93XX envelope is about 38.2 mm x 28.04 mm including edge stroke.
- Compact ADE9000 JST revision used about 38.1 mm x 38.0 mm.
- Keep headers on edges and test pads on the bottom side when front-side space is tight.
- Put optional logos and attribution on B.SilkS after routing space is known.
- Keep copper, test pads, mounting holes, and silkscreen clear of rounded or chamfered edges.

## ATM-Style Bench Board

Use the ATM90E36-style layout when the energy monitor board is a wiring/probing platform rather than a tiny module.

- Allocate one edge or side region for digital/debug signals on a 0.1 inch breadboard-friendly header.
- Group current inputs by channel using stereo jacks or similarly robust connectors.
- Group voltage inputs on screw terminals with readable phase/neutral order.
- Leave room for burden/multiplier resistors near current jacks and filter rows near the IC.
- Use the larger board area to reduce routing congestion and improve silkscreen readability, not to scatter circuit blocks.
- The current ADE9000 ATM-style board uses a 65 mm x 55 mm envelope with current jacks, voltage screw terminals, digital header, M2 holes, and GND planes.

## Rounded Corners And Mounting Holes

Use MCP3909 as the rounded-corner style reference and ADE9000 as the local M2 implementation reference.

- Use rounded corners when the board will be handled as a bench module.
- 5.08 mm corner radius is the established rounded-corner visual pattern.
- Use four M2 NPTH holes when board space allows.
- M2 holes should be NPTH circular pads with 2.2 mm drill and 2.2 mm pad size, no net, excluded from BOM and position files.
- Hide mounting-hole references and values by design.
- Keep mounting holes outside component courtyards and away from copper, zones, silkscreen, and connector keepouts.

## Edge Allocation

- Put field wiring connectors where cables naturally leave the board.
- Keep analog connector edges away from digital headers when board size allows.
- Reserve a clean routing corridor between each connector group and its IC pin bank.
- Put bottom-side test pads along a board edge rather than mid-board when they need routing access.
- For the ADE9000 compact JST revision, bottom-edge `TP5` through `TP13` preserve the SPI/JST fanout corridor; the older mid-board cluster blocks routing.

## Mechanical Scripts

For ADE9000 mechanical finishing:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" .\scripts\apply_mechanical.py .\ADE9000_Breakout.kicad_pcb
```

Script principles:

- Keep board bbox constants explicit.
- Rebuild Edge.Cuts deterministically.
- Add mounting holes reproducibly.
- Reapply board markings after outline/hole regeneration when the local script owns those markings.
- Avoid re-querying fragile KiCad SWIG collections after adding/removing board drawings; collect what is needed before mutation.

## Mechanical DRC Gate

After changing size, shape, holes, or connector placement, DRC must not introduce:

- `copper_edge_clearance`
- `hole_clearance`
- `hole_to_hole`
- `npth_inside_courtyard`
- `pth_inside_courtyard`
- `courtyards_overlap`
- `silk_edge_clearance`
- `silk_overlap`
- `silk_over_copper`

If board size changes cause new routing congestion, revisit connector edge allocation before relaxing clearances.
