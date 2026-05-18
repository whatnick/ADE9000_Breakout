---
name: whatnick-energy-monitor-bom-sourcing
description: "Use when: choosing MPNs, creating BOMs, adding schematic sourcing fields, selecting DigiKey/Mouser parts, or standardizing passives/connectors across whatnick energy-monitor boards for bulk reel buying and reuse. Covers preferred common values, value normalization, substitution policy, distributor fields, and CSV/XLSX BOM export discipline."
argument-hint: "BOM, MPNs, DigiKey/Mouser sourcing, common passives, reel buying"
---

# Whatnick Energy Monitor BOM Sourcing

Use this skill when adding, reviewing, or regenerating BOM fields for whatnick energy-monitor boards. The sourcing goal is to reuse common values and manufacturers across boards so frequently used parts can be bought as reels and consumed across designs.

## Core Policy

- Put purchasing data on schematic symbols, not only in exported spreadsheets.
- Use the same preferred MPN for the same electrical value, package, dielectric, tolerance, and voltage rating wherever possible.
- Prefer reel-friendly commodity passives from stable high-volume families before optimizing for a one-off cheapest line item.
- Keep exact or mechanically constrained connectors as exact MPNs; do not substitute connectors just to share a line item if footprint, height, pitch, pinout, or 3D fit changes.
- Use distributor search URLs in `DigiKey` and `Mouser` fields unless a verified order-code field already exists in that project.
- Do not change precision, voltage rating, dielectric, power rating, package size, or temperature behavior to force reuse.
- Preserve measurement accuracy: burden, shunt, divider, reference, oscillator, and anti-alias parts may need tighter tolerance or lower tempco than generic passives.

## Preferred Common Parts

Use these as the first-choice values for new whatnick energy-monitor BOMs unless the circuit requires different electrical performance.

| Role | Value | Package | Preferred MPN | Manufacturer | Notes |
|------|-------|---------|---------------|--------------|-------|
| Logic/reset pull-up, LED limit, generic bias | 1 kOhm 1% | 0402 | `RC0402FR-071KL` | YAGEO | Reuse for non-precision 1 k resistors. Do not use for precision dividers when tighter specs are needed. |
| Generic pull-up/pull-down | 10 kOhm 1% | 0402 | `RC0402FR-0710KL` | YAGEO | Default digital/config strap resistor. |
| YHDC current-output clamp burden/multiplier | 2.4 Ohm 1% | 0402 | `RC0402FR-072R4L` | YAGEO | Use only where power dissipation and measurement error budget are acceptable. |
| Local high-frequency decoupling | 100 nF X7R | 0402 | `GRM155R71A104KA01D` | Murata | Default 0402 decoupler. Raise voltage rating when rail or derating requires it. |
| Reset/reference small bypass | 1 uF X5R | 0402 | `GRM155R61A105KE15D` | Murata | Default compact 1 uF. Check DC bias for analog reference use. |
| Anti-alias shunt capacitor | 22 nF X7R | 0402 | `GRM155R71H223KA12D` | Murata | ADE9000-style 1 k/22 nF first-order filters. |
| Crystal load capacitor | 16 pF C0G/NP0 | 0402 | `GRM1555C1H160JA01D` | Murata | Use C0G/NP0 for oscillator stability. Adjust value for crystal load capacitance and stray capacitance. |
| Bulk rail decoupling | 4.7 uF X5R | 0805 | `CL21A475KPFNNNE` | Samsung Electro-Mechanics | Default 0805 low-frequency local/bulk capacitor. |
| Bulk input decoupling | 10 uF X5R | 0805 | `CL21A106KPFNNNE` | Samsung Electro-Mechanics | Default 0805 10 uF. Check DC bias and voltage derating. |
| Green status LED | Green 0603 | 0603 | `LTST-C191KGKT` | Lite-On | Shared indicator LED where color is not functionally constrained. |

## Exact Mechanical Parts

These are shared where the matching footprint and mechanical envelope are intentionally used:

| Role | Preferred MPN | Manufacturer | Notes |
|------|---------------|--------------|-------|
| ADE9000 CT stereo SMT jack | `SJ-3523-SMT-TR` | Same Sky | Must match `Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal` and the project-local STEP model. |
| 3.5 mm 2-position voltage terminal | `1984617` | Phoenix Contact | Preferred 3.5 mm horizontal terminal substitute for ADE9000-style voltage terminals. Verify footprint against the target board. |
| 1x16 breakaway male header for SparkFun locking footprint | `PREC016SAAN-RC` | Sullins Connector Solutions | Header body used with SparkFun staggered/friction-fit PTH footprint. |

## Schematic Fields

For each sourced symbol, populate:

- `Manufacturer`
- `MPN`
- `Description`
- `DigiKey`
- `Mouser`

Use consistent field names across repositories so BOM exporters can group by MPN. If a board has legacy fields, preserve them only when required by its existing exporter and add the standard fields as well.

## Selection Workflow

1. Group parts by value, footprint, tolerance, voltage rating, dielectric, and role.
2. Match each group against the preferred common parts table.
3. Use the preferred MPN when the group is electrically equivalent or better for that role.
4. For special measurement or safety parts, choose the correct part first and document why it differs from the preferred list.
5. Add schematic fields, then export grouped CSV/XLSX BOM outputs from schematic data.
6. Review the grouped BOM for accidental fragmentation such as `100n`, `100nF`, and `0.1uF` exporting as separate lines.
7. Check live DigiKey/Mouser stock and packaging before ordering; distributor availability changes faster than the repository.

## When Not To Reuse

Choose a different MPN when any of these differ materially:

- ADC accuracy path needs tighter tolerance, tempco, voltage coefficient, or power rating.
- Capacitor dielectric or voltage rating affects filter frequency, reference noise, startup timing, or oscillator behavior.
- Connector must match an existing enclosure, mating cable, STEP model, board edge, or assembly process.
- The preferred part is end-of-life, unavailable in useful quantity, or no longer offered in reel-friendly packaging.

## Export Discipline

- Treat the schematic as BOM source of truth.
- Generated CSV/XLSX outputs are build artifacts derived from fields, but commit them when the repository uses BOM spreadsheets for ordering.
- Keep hand-edited iBOM output separate from sourced BOM commits unless the task is specifically to regenerate iBOM.
- Prefer exporter scripts over manual copy-paste from iBOM so the same preferred MPNs can be reused across boards.