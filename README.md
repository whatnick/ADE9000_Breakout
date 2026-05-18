# ADE9000 Breakout Board

Breadboard-compatible breakout for the Analog Devices [ADE9000](https://www.analog.com/en/products/ade9000.html) — a high-performance, multiphase energy and power quality monitoring IC.

The board follows the **test circuit from Figure 55 of the ADE9000 datasheet** (Rev. B, p. 28): all onboard passives (decoupling, RC anti-aliasing filters, crystal load caps, reset RC) are populated, power plus the analog channels are broken out to 0.1" headers, and the remaining digital signals are exposed on test pads to keep the board compact.

---

## Features

- **ADE9000** in 40-lead LFCSP (CP-40-7) package
- 3.3 V single-supply operation
- Onboard **24.576 MHz crystal** with 16 pF load caps (CLKIN/CLKOUT)
- Onboard **RC anti-aliasing filters** on all 7 analog input pairs (1 kΩ + 22 nF)
- Onboard **reset RC** (10 kΩ pull-up + 1 µF)
- Onboard **decoupling** on VDD, AVDDOUT, DVDDOUT, and REF per datasheet
- **CF2 activity LED** with 1 kΩ current-limit resistor
- **Power plus analog inputs** broken out to 0.1" headers
- **SPI, CF, IRQ, CLK, and RESET** exposed on test pads
- PM0/PM1 grounded for normal operating mode

---

## Pin Headers

### J1 — Power

| Pin | Signal | ADE9000 Pin | Description |
|-----|--------|-------------|-------------|
| 1 | 3.3V | — | Power in |
| 2 | GND | — | Ground |

### J2 — Current Inputs (left side, top)

| Pin | Signal | ADE9000 Pin | Description |
|-----|--------|-------------|-------------|
| 1 | IAP | 7 | Phase A current, positive |
| 2 | IAN | 8 | Phase A current, negative |
| 3 | IBP | 9 | Phase B current, positive |
| 4 | IBN | 10 | Phase B current, negative |
| 5 | ICP | 11 | Phase C current, positive |
| 6 | ICN | 12 | Phase C current, negative |
| 7 | INP | 13 | Neutral current, positive |
| 8 | INN | 14 | Neutral current, negative |

> Each input pair has a 1 kΩ series resistor and 22 nF cap to GND already fitted on board. Max differential input ±1 V / PGA gain.

### J3 — Voltage Inputs (left side, bottom)

| Pin | Signal | ADE9000 Pin | Description |
|-----|--------|-------------|-------------|
| 1 | VAP | 20 | Phase A voltage, positive |
| 2 | VAN | 19 | Phase A voltage, negative |
| 3 | VBP | 22 | Phase B voltage, positive |
| 4 | VBN | 21 | Phase B voltage, negative |
| 5 | VCP | 24 | Phase C voltage, positive |
| 6 | VCN | 23 | Phase C voltage, negative |

> Each input pair has the same 1 kΩ + 22 nF RC filter as the current inputs.

### Test Pads — Digital I/O

| Pad | Signal | ADE9000 Pin | Description |
|-----|--------|-------------|-------------|
| TP1 | SS | 40 | SPI slave select (active low) |
| TP2 | MOSI | 39 | SPI data in |
| TP3 | MISO | 38 | SPI data out |
| TP4 | SCLK | 37 | SPI clock (up to 20 MHz) |
| TP5 | IRQ0 | 31 | Interrupt output 0 (active low) |
| TP6 | IRQ1 | 32 | Interrupt output 1 (active low) |
| TP7 | CF1 | 33 | Calibration frequency output 1 |
| TP8 | CF2 | 34 | Calibration frequency output 2 / LED drive |
| TP9 | CF3_ZX | 35 | Zero-cross / CF3 output |
| TP10 | CF4_DREADY | 36 | Data-ready / event / CF4 output |
| TP11 | RESET | 6 | Reset (active low, RC-held high) |

---

## Power

- Supply **3.3 V** into the J1 3.3V pin (or the dedicated 3V3 pad).
- Current draw: ~15–17 mA in normal mode (PSM0).
- Onboard decoupling (per datasheet §Test Circuit):
  - **VDD** (pin 27): 10 µF + 0.1 µF ceramic to GND
  - **AVDDOUT** (pin 25): 4.7 µF + 0.1 µF ceramic to GND — **do not drive externally**
  - **DVDDOUT** (pin 3): 4.7 µF + 0.1 µF ceramic to GND — **do not drive externally**
  - **REF** (pin 16): 4.7 µF + 0.1 µF ceramic to REFGND (internal 1.25 V reference)

---

## Clock

A 24.576 MHz crystal is fitted between CLKIN (pin 29) and CLKOUT (pin 30) with 16 pF load capacitors to GND. This matches the ADE9000's required ±30 ppm clock.

To use an external clock instead, remove the crystal, leave the load caps unpopulated, and drive CLKIN directly (3.3 V logic, 24.330–24.822 MHz, 45:55–55:45 duty cycle).

---

## SPI Interface

The ADE9000 uses **SPI mode 0** (CPOL=0, CPHA=0), MSB first, up to **20 MHz**.

| Signal | Direction (from MCU) | Notes |
|--------|---------------------|-------|
| SCLK | Output | Max 20 MHz |
| MOSI | Output | 16-bit or 32-bit transfers |
| MISO | Input | |
| SS | Output | Assert low before each transfer |

All SPI pins are 3.3 V logic. Use a level shifter if connecting to a 5 V MCU.

---

## Analog Input Signal Conditioning

The onboard RC filter on each analog input pin:

```
Signal ──[ 1 kΩ ]──┬── IxP / VxP (ADE9000 pin)
                   │
                 [22 nF]
                   │
                  GND
```

This provides a first-order anti-aliasing LPF with fc ≈ 7.2 kHz, matching the ADC's −3 dB bandwidth. For CT or Rogowski coil inputs, drive the differential pair through an additional burden resistor or signal conditioning stage before these onboard filters.

---

## BOM Summary

| Ref | Value | Package | Notes |
|-----|-------|---------|-------|
| U1 | ADE9000 | CP-40-7 LFCSP | Main IC |
| Y1 | 24.576 MHz | 3225 (3.2×2.5 mm) | ±30 ppm |
| C_CLKIN, C_CLKOUT | 16 pF | 0402 | Crystal load caps |
| C_VDD1 | 10 µF | 0805 | VDD bulk decoupling |
| C_VDD2, C_AVDD2, C_DVDD2, C_REF2 | 0.1 µF | 0402 | HF decoupling |
| C_AVDD1, C_DVDD1, C_REF1 | 4.7 µF | 0805 | LF decoupling |
| C_RST | 1 µF | 0402 | Reset RC |
| C_PM | 1 µF | 0402 | PM0 bypass |
| R_RST | 10 kΩ | 0402 | Reset pull-up |
| R_IAP…R_VCN (×14) | 1 kΩ | 0402 | Anti-aliasing series R |
| C_IAP…C_VCN (×7) | 22 nF | 0402 | Anti-aliasing cap (differential) |
| R_LED | 1 kΩ | 0402 | CF2 LED current limit |
| D_LED | Green LED | 0402 | CF2 activity indicator |

---

## Schematic

The KiCad schematic (`ADE9000_Breakout.kicad_sch`) implements Figure 55 of the datasheet with compact breakout constraints: only power and analog channels go to headers, while digital signals stay on test pads. Reference images and the datasheet are in [`docs/`](docs/).

---

## 3D CAD

Project-local STEP models for all populated ADE9000 board parts are stored in [`models/step/`](models/step/). The PCB references these files through `${KIPRJMOD}` so the 3D view and CAD export do not depend on a particular KiCad library installation.

The stereo CT jacks use a black AP214-colored STEP model at [`models/step/Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal.step`](models/step/Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal.step), generated from the manufacturer `SJ-3523-SMT-TR` CAD ZIP in [`models/step/SJ_3523_SMT_TR.zip`](models/step/SJ_3523_SMT_TR.zip) with [`scripts/create_sj3523_smt_step.py`](scripts/create_sj3523_smt_step.py). The script bakes the DigiKey/Same Sky CAD into the KiCad footprint frame with the front barrel on the footprint's board-edge side, without adding artificial pad overlays. Do not substitute the through-hole `SJ1-3523N` model for this SMT footprint.

The voltage screw-terminal footprints use KiCad's 1x02 3.50 mm horizontal Phoenix STEP model as the closest installed mechanical equivalent for the 4Ucon footprint, with a small model-only Y offset to align the substitute body to the 4Ucon footprint outline.

A full board assembly STEP export is available at [`exports/step/ADE9000_Breakout.step`](exports/step/ADE9000_Breakout.step). Regenerate it with:

```powershell
& "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" pcb export step --force --subst-models --output "exports\step\ADE9000_Breakout.step" "ADE9000_Breakout.kicad_pcb"
```

---

## Resources

| Document | Path |
|----------|------|
| ADE9000 Datasheet (Rev. B) | [`docs/ADE9000.pdf`](docs/ADE9000.pdf) |
| Test Circuit Reference | [`docs/images/test_ade9000.png`](docs/images/test_ade9000.png) |
| ADE9000 Product Page | https://www.analog.com/en/products/ade9000.html |
| ADE9000 Technical Reference Manual (UG-1098) | https://www.analog.com/media/en/technical-documentation/user-guides/ADE9000-UG-1098.pdf |
| Arduino Shield Eval (UG-1170) | https://www.analog.com/media/en/technical-documentation/user-guides/ev-ade9000shieldz-ug-1170.pdf |
| no-OS Driver | https://github.com/analogdevicesinc/no-OS/tree/main/drivers/meter/ade9000 |

---

## License

This hardware design is released under the [TAPR Open Hardware License v1.0](LICENSE). The PCB artwork includes a `TAPR OHL` notice on the back silkscreen.
