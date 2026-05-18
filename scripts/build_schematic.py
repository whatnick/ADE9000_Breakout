"""
ADE9000 Breakout Board - Schematic Builder
Adds all components to the KiCad schematic via the kicad_interface.py backend.
Calls the interface's add_schematic_component command for each component.
"""
import sys
import json
import subprocess
import uuid
import re
from pathlib import Path

SCH_PATH = r"c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_sch"
KI_IFACE = r"c:\Users\tisha\dev\KiCAD-MCP-Server\python\kicad_interface.py"
KI_PYTHON = r"C:\Program Files\KiCad\10.0\bin\python.exe"

def call_iface(command: str, args: dict):
    payload = json.dumps({"command": command, "params": args})
    result = subprocess.run(
        [KI_PYTHON, KI_IFACE],
        input=payload, capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(result.stdout)
    except Exception:
        data = {"success": False, "stdout": result.stdout, "stderr": result.stderr}
    if not data.get("success"):
        print(f"  WARN: {command} failed: {data.get('message', data)}", file=sys.stderr)
    return data

def add_component(symbol: str, ref: str, value: str, x: float, y: float,
                  footprint: str = "", unit: int = 1):
    lib, sym = symbol.split(":", 1)
    args = {
        "schematicPath": SCH_PATH,
        "component": {
            "library": lib,
            "type": sym,
            "reference": ref,
            "value": value,
            "footprint": footprint,
            "x": x,
            "y": y,
            "unit": unit,
        }
    }
    r = call_iface("add_schematic_component", args)
    ok = "✓" if r.get("success") else "✗"
    print(f"  {ok} {ref} ({symbol}) @ ({x:.2f}, {y:.2f})")
    return r

def add_label(net: str, x: float, y: float, angle: int = 0):
    args = {
        "schematicPath": SCH_PATH,
        "label": net,
        "x": x,
        "y": y,
        "angle": angle,
    }
    r = call_iface("add_schematic_net_label", args)
    return r

def add_no_connect(x: float, y: float):
    args = {"schematicPath": SCH_PATH, "x": x, "y": y}
    r = call_iface("add_no_connect", args)
    return r

def add_wire(x1, y1, x2, y2):
    args = {"schematicPath": SCH_PATH, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
    r = call_iface("add_schematic_wire", args)
    return r

print("=== ADE9000 Breakout Schematic Builder ===")
print()

# ── U1 already placed at (130, 100) ──────────────────────────────────────────
# U1 left pin wire ends: x=117.3, y from 70.79 to 129.21 in 2.54 steps
# U1 right pin wire ends: x=142.7, y from 79.68 to 120.32 in 2.54 steps

# U1 left pin y-positions (absolute)
U1_LX = 117.3  # left pin wire end x
U1_RX = 142.7  # right pin wire end x

left_pins = {
    "PULL_HIGH": (U1_LX, 70.79),
    "DGND":      (U1_LX, 73.33),
    "DVDDOUT":   (U1_LX, 75.87),
    "PM0":       (U1_LX, 78.41),
    "PM1":       (U1_LX, 80.95),
    "RESET":     (U1_LX, 83.49),
    "IAP":       (U1_LX, 86.03),
    "IAN":       (U1_LX, 88.57),
    "IBP":       (U1_LX, 91.11),
    "IBN":       (U1_LX, 93.65),
    "ICP":       (U1_LX, 96.19),
    "ICN":       (U1_LX, 98.73),
    "INP":       (U1_LX, 101.27),
    "INN":       (U1_LX, 103.81),
    "REFGND":    (U1_LX, 106.35),
    "REF":       (U1_LX, 108.89),
    "NC1":       (U1_LX, 111.43),
    "NC2":       (U1_LX, 113.97),
    "VAN":       (U1_LX, 116.51),
    "VAP":       (U1_LX, 119.05),
    "VBN":       (U1_LX, 121.59),
    "VBP":       (U1_LX, 124.13),
    "VCN":       (U1_LX, 126.67),
    "VCP":       (U1_LX, 129.21),
}

right_pins = {
    "AVDDOUT":   (U1_RX, 79.68),
    "AGND":      (U1_RX, 82.22),
    "VDD":       (U1_RX, 84.76),
    "GND":       (U1_RX, 87.30),
    "CLKIN":     (U1_RX, 89.84),
    "CLKOUT":    (U1_RX, 92.38),
    "IRQ0":      (U1_RX, 94.92),
    "IRQ1":      (U1_RX, 97.46),
    "CF1":       (U1_RX, 100.00),
    "CF2":       (U1_RX, 102.54),
    "CF3_ZX":    (U1_RX, 105.08),
    "CF4_DREADY":(U1_RX, 107.62),
    "SCLK":      (U1_RX, 110.16),
    "MISO":      (U1_RX, 112.70),
    "MOSI":      (U1_RX, 115.24),
    "SS":        (U1_RX, 117.78),
    "EPAD":      (U1_RX, 120.32),
}

# ─────────────────────────────────────────────────────────────────────────────
print("--- Connectors ---")

# J1: 2-pin power connector (Conn_01x02)
# Symbol pin positions relative to 'at': pin1=(−5.08,0), pin2=(−5.08,−2.54)
# Place at (35, 72) → pin1 at (29.92, 72.00), pin2 at (29.92, 69.46)
add_component("Connector_Generic:Conn_01x02", "J1", "PWR", 35, 72,
              footprint="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical")

# J2: 8-pin current inputs (Conn_01x08)
# Pin layout: pin1=(−5.08,7.62)..pin8=(−5.08,−10.16) in symbol space
# Place at (35, 96.19): pin1→(29.92, 103.81)=INN_J, pin8→(29.92, 86.03)=IAP_J
# Pin y order (visual bottom to top): IAP, IAN, IBP, IBN, ICP, ICN, INP, INN
# Since pin1 is at bottom and pin8 at top in this connector:
#   pin8 = IAP_J (y=86.03), pin7 = IAN_J (y=88.57) ... pin1 = INN_J (y=103.81)
add_component("Connector_Generic:Conn_01x08", "J2", "Current In", 35, 96.19,
              footprint="Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical")

# J3: 6-pin voltage inputs (Conn_01x06)
# Pin layout: pin1=(−5.08,5.08)..pin6=(−5.08,−7.62) in symbol space
# Place at (35, 116.13): pin1→(29.92, 121.21), pin6→(29.92, 108.51)
# Actually align with voltage input y range: VAN=116.51..VCP=129.21
# pin1 at top (smallest y in KiCad → higher on screen)
# Conn_01x06: pin1 at y+5.08, pin6 at y-7.62
# I want pin1 (top) at y=116.51 → connector y = 116.51-5.08 = 111.43
# Then pin6 at 111.43-7.62 = 103.81... that's wrong direction
# KiCad Y: larger Y = lower on screen
# pin1 at y+5.08 → pin1 is LOWER on screen (larger y)
# pin6 at y-7.62 → pin6 is HIGHER on screen (smaller y)
# Set: pin1 y = 129.21 (VCP), pin6 y = 116.51 (VAN)
# y+5.08 = 129.21 → y = 124.13
add_component("Connector_Generic:Conn_01x06", "J3", "Voltage In", 35, 124.13,
              footprint="Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical")

# ─────────────────────────────────────────────────────────────────────────────
print()
print("--- Test Pads (digital signals) ---")

# Test pads at x=165, y staggered
# Conn_01x01: pin1 at (−2.54, 0) in symbol space
# Placed at (165, y): pin at (162.46, y)
tp_data = [
    ("TP1",  "SS",          165, 84.76),
    ("TP2",  "MOSI",        165, 87.30),
    ("TP3",  "MISO",        165, 89.84),
    ("TP4",  "SCLK",        165, 92.38),
    ("TP5",  "IRQ0",        165, 94.92),
    ("TP6",  "IRQ1",        165, 97.46),
    ("TP7",  "CF1",         165, 100.00),
    ("TP8",  "CF2",         165, 102.54),
    ("TP9",  "CF3_ZX",      165, 105.08),
    ("TP10", "CF4_DREADY",  165, 107.62),
    ("TP11", "RESET",       165, 110.16),
]
for ref, val, x, y in tp_data:
    add_component("Connector_Generic:Conn_01x01", ref, val, x, y,
                  footprint="TestPoint:TestPoint_Pad_D1.5mm")

# ─────────────────────────────────────────────────────────────────────────────
print()
print("--- Power Decoupling ---")

# Decoupling capacitors for VDD (pin 27, right side y=84.76)
# C1: 10µF bulk bypass - place right of U1 at x=157, y=84.76
# Device:C pin1 at (0,3.81), pin2 at (0,-3.81) → vertical, pin1 is +, pin2 is -
add_component("Device:C_Polarized", "C1", "10uF", 157, 83,
              footprint="Capacitor_SMD:C_0805_2012Metric")
add_component("Device:C", "C2", "100nF", 163, 83,
              footprint="Capacitor_SMD:C_0603_1608Metric")

# AVDDOUT (pin 25, right side y=79.68)
add_component("Device:C_Polarized", "C3", "4.7uF", 157, 78,
              footprint="Capacitor_SMD:C_0805_2012Metric")
add_component("Device:C", "C4", "100nF", 163, 78,
              footprint="Capacitor_SMD:C_0603_1608Metric")

# DVDDOUT (pin 3, left side y=75.87)
add_component("Device:C_Polarized", "C5", "4.7uF", 105, 72,
              footprint="Capacitor_SMD:C_0805_2012Metric")
add_component("Device:C", "C6", "100nF", 111, 72,
              footprint="Capacitor_SMD:C_0603_1608Metric")

# REF (pin 16, left side y=108.89)
add_component("Device:C_Polarized", "C7", "4.7uF", 105, 110,
              footprint="Capacitor_SMD:C_0805_2012Metric")
add_component("Device:C", "C8", "100nF", 111, 110,
              footprint="Capacitor_SMD:C_0603_1608Metric")

# ─────────────────────────────────────────────────────────────────────────────
print()
print("--- Crystal ---")

# Y1: 24.576 MHz crystal
# Device:Crystal horizontal: pin1 at (-3.81,0), pin2 at (3.81,0)
# CLKIN=pin29 at (142.7, 89.84), CLKOUT=pin30 at (142.7, 92.38)
# Place crystal between them vertically → rotate 90° or place off to side
# Place at (157, 91) with vertical orientation
add_component("Device:Crystal", "Y1", "24.576MHz", 157, 91,
              footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")

# C9, C10: 16pF crystal load capacitors
add_component("Device:C", "C9",  "16pF", 163, 89,
              footprint="Capacitor_SMD:C_0603_1608Metric")
add_component("Device:C", "C10", "16pF", 163, 93,
              footprint="Capacitor_SMD:C_0603_1608Metric")

# ─────────────────────────────────────────────────────────────────────────────
print()
print("--- Reset RC ---")

# RESET (pin 6, left side y=83.49)
# R1: 10kΩ pullup, C11: 1µF filter cap
add_component("Device:R", "R1", "10k", 100, 80,
              footprint="Resistor_SMD:R_0603_1608Metric")
add_component("Device:C", "C11", "1uF", 106, 80,
              footprint="Capacitor_SMD:C_0603_1608Metric")

# ─────────────────────────────────────────────────────────────────────────────
print()
print("--- Anti-Aliasing RC Filters ---")
# 14 resistors R2-R15 (1kΩ) and 14 caps C12-C25 (22nF)
# Placed between connectors (x~35) and U1 (x~117)
# Using x=75 for resistors, x=84 for caps
# Each R is at a y matching the IC pin, each C goes to GND from same node

# Current channels - y aligns with IAP..INN on U1 left side
# AA filter: J_pin --wire--> R --wire--> IC pin (+ cap to GND)
r_idx = 2
c_idx = 12

aa_current = [
    ("IAP", 86.03), ("IAN", 88.57),
    ("IBP", 91.11), ("IBN", 93.65),
    ("ICP", 96.19), ("ICN", 98.73),
    ("INP", 101.27),("INN", 103.81),
]
for net, y in aa_current:
    add_component("Device:R", f"R{r_idx}", "1k", 75, y,
                  footprint="Resistor_SMD:R_0603_1608Metric")
    add_component("Device:C", f"C{c_idx}", "22nF", 90, y+3.81,
                  footprint="Capacitor_SMD:C_0603_1608Metric")
    r_idx += 1
    c_idx += 1

# Voltage channels - y aligns with VAN..VCP on U1 left side
aa_voltage = [
    ("VAN", 116.51), ("VAP", 119.05),
    ("VBN", 121.59), ("VBP", 124.13),
    ("VCN", 126.67), ("VCP", 129.21),
]
for net, y in aa_voltage:
    add_component("Device:R", f"R{r_idx}", "1k", 75, y,
                  footprint="Resistor_SMD:R_0603_1608Metric")
    add_component("Device:C", f"C{c_idx}", "22nF", 90, y+3.81,
                  footprint="Capacitor_SMD:C_0603_1608Metric")
    r_idx += 1
    c_idx += 1

# ─────────────────────────────────────────────────────────────────────────────
print()
print("--- CF2 LED indicator ---")

# CF2 = pin 34 at (142.7, 102.54)
# LED + 1kΩ resistor from +3V3 to CF2
add_component("Device:R",   "R16", "1k",  157, 102,
              footprint="Resistor_SMD:R_0603_1608Metric")
add_component("Device:LED", "D1",  "GREEN_LED", 157, 106,
              footprint="LED_SMD:LED_0603_1608Metric")

print()
print("=== All components placed ===")
print()
print("Note: Run add_net_labels.py next to connect all nets via labels.")
