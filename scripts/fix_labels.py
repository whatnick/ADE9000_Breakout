"""
ADE9000 Breakout - Label Fixer
Clears ALL labels from the schematic and re-adds with CORRECT positions.

Root cause of issues discovered via PinLocator:
1. ADE9000 symbol has pins in REVERSED y-order from what was assumed.
   - pin24 (VCP) is at the TOP of U1's left side (y=70.79)
   - pin1 (PULL_HIGH) is at the BOTTOM (y=129.21)
   - Same for right side: EPAD at top (y=79.68), AVDDOUT at bottom (y=120.32)
2. KiCad symbol y-axis in schematic is INVERTED from symbol file y-axis.
   - Correct formula: schematic_y = component_y - symbol_pin_y
   - My original script incorrectly used: component_y + symbol_pin_y
3. Test pad labels were at x=162.46 but pins are at x=159.92 (Conn_01x01 pin at -5.08, not -2.54)
4. J2/J3 connector net assignments were scrambled due to #2 above
5. D1 (LED) has horizontal pins at y=106 but labels were placed vertically

All positions verified by PinLocator.get_pin_location() from KiCad MCP Server.
"""
import sys
import json
import re
import subprocess
from pathlib import Path

SCH_PATH = r"c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_sch"
KI_IFACE = r"c:\Users\tisha\dev\KiCAD-MCP-Server\python\kicad_interface.py"
KI_PYTHON = r"C:\Program Files\KiCad\10.0\bin\python.exe"


# ─── STEP 1: CLEAR ALL LABELS FROM SCHEMATIC FILE ────────────────────────────

def remove_sexp_blocks(content: str, keyword: str) -> str:
    """Remove all top-level S-expression blocks starting with (keyword ...)."""
    result = []
    i = 0
    search_term = f'({keyword} '
    while i < len(content):
        idx = content.find(search_term, i)
        if idx == -1:
            result.append(content[i:])
            break
        # Add everything before this block
        result.append(content[i:idx])
        # Count parentheses to find the end of this S-expression block
        depth = 0
        j = idx
        while j < len(content):
            if content[j] == '(':
                depth += 1
            elif content[j] == ')':
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        # Skip (don't include) this block; also skip trailing whitespace/newline
        while j < len(content) and content[j] in ' \t\r\n':
            j += 1
        i = j
    return ''.join(result)


print("=== Step 1: Clear existing labels and no-connects ===")
sch = Path(SCH_PATH)
content = sch.read_text(encoding='utf-8')

label_count = content.count('(label ')
nc_count = content.count('(no_connect ')
print(f"  Found {label_count} labels and {nc_count} no-connects")

content = remove_sexp_blocks(content, 'label')
content = remove_sexp_blocks(content, 'no_connect')

sch.write_text(content, encoding='utf-8')
print(f"  Cleared {label_count} labels and {nc_count} no-connects ✓")


# ─── STEP 2: RE-ADD ALL LABELS WITH CORRECT POSITIONS ────────────────────────

def call_iface(command: str, params: dict):
    payload = json.dumps({"command": command, "params": params})
    result = subprocess.run(
        [KI_PYTHON, KI_IFACE],
        input=payload, capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(result.stdout)
    except Exception:
        data = {"success": False, "message": result.stderr[:120]}
    return data


def label(net: str, x: float, y: float, angle: int = 0):
    return call_iface("add_schematic_net_label", {
        "schematicPath": SCH_PATH,
        "netName": net,
        "position": [x, y],
        "orientation": angle,
    })


def no_connect(x: float, y: float):
    return call_iface("add_no_connect", {
        "schematicPath": SCH_PATH,
        "position": [x, y],
    })


ok = lambda r: "✓" if r.get("success") else f"✗({r.get('message','?')[:40]})"

errors = 0


def lbl(net, x, y, angle=0):
    global errors
    r = label(net, x, y, angle)
    status = ok(r)
    if not r.get("success"):
        errors += 1
        print(f"  ✗ label '{net}' @ ({x:.2f},{y:.2f}): {r.get('message','?')[:60]}")
    return r


def nc(x, y):
    global errors
    r = no_connect(x, y)
    if not r.get("success"):
        errors += 1
        print(f"  ✗ no_connect @ ({x:.2f},{y:.2f}): {r.get('message','?')[:60]}")
    return r


print()
print("=== Step 2: Add corrected U1 labels ===")
print()

# U1 LEFT SIDE (x=117.3, angle=0 — labels face right, stub on left)
# Pins verified by PinLocator. ADE9000 symbol has REVERSED pin order:
# physical pin 24 (VCP) at y=70.79 (TOP), physical pin 1 (PULL_HIGH) at y=129.21 (BOTTOM)
U1_LX = 117.3
U1_RX = 142.7

print("--- U1 Left Side (pins at x=117.3) ---")
# Format: (net_name, y_position, comment)
u1_left = [
    ("VCP",     70.79,  "pin24 VCP"),
    ("VCN",     73.33,  "pin23 VCN"),
    ("VBP",     75.87,  "pin22 VBP"),
    ("VBN",     78.41,  "pin21 VBN"),
    ("VAP",     80.95,  "pin20 VAP"),
    ("VAN",     83.49,  "pin19 VAN"),
    # pin18 NC at 86.03 → no_connect
    # pin17 NC at 88.57 → no_connect
    ("REF",     91.11,  "pin16 REF"),
    ("GND",     93.65,  "pin15 REFGND→GND"),
    ("INN",     96.19,  "pin14 INN"),
    ("INP",     98.73,  "pin13 INP"),
    ("ICN",     101.27, "pin12 ICN"),
    ("ICP",     103.81, "pin11 ICP"),
    ("IBN",     106.35, "pin10 IBN"),
    ("IBP",     108.89, "pin9 IBP"),
    ("IAN",     111.43, "pin8 IAN"),
    ("IAP",     113.97, "pin7 IAP"),
    ("RESET",   116.51, "pin6 ~RESET~"),
    ("GND",     119.05, "pin5 PM1→GND"),
    ("GND",     121.59, "pin4 PM0→GND"),
    ("DVDDOUT", 124.13, "pin3 DVDDOUT"),
    ("GND",     126.67, "pin2 DGND→GND"),
    ("+3V3",    129.21, "pin1 PULL_HIGH→+3V3"),
]
for net, y, comment in u1_left:
    r = lbl(net, U1_LX, y, angle=0)
    print(f"  {ok(r)} {net:14s} y={y:.2f}  [{comment}]")

# No-connects for NC pins (pin17 at y=88.57, pin18 at y=86.03)
r = nc(U1_LX, 86.03)
print(f"  {ok(r)} no-connect pin18 (NC) @ y=86.03")
r = nc(U1_LX, 88.57)
print(f"  {ok(r)} no-connect pin17 (NC) @ y=88.57")

print()
print("--- U1 Right Side (pins at x=142.7) ---")
# EPAD at y=79.68 (TOP), AVDDOUT at y=120.32 (BOTTOM)
u1_right = [
    ("GND",          79.68,  "EPAD→GND"),
    ("SS",           82.22,  "pin40 ~SS~"),
    ("MOSI",         84.76,  "pin39 MOSI"),
    ("MISO",         87.30,  "pin38 MISO"),
    ("SCLK",         89.84,  "pin37 SCLK"),
    ("CF4_DREADY",   92.38,  "pin36 CF4/DREADY"),
    ("CF3_ZX",       94.92,  "pin35 CF3/ZX"),
    ("CF2",          97.46,  "pin34 CF2"),
    ("CF1",          100.00, "pin33 CF1"),
    ("IRQ1",         102.54, "pin32 ~IRQ1~"),
    ("IRQ0",         105.08, "pin31 ~IRQ0~"),
    ("CLKOUT",       107.62, "pin30 CLKOUT"),
    ("CLKIN",        110.16, "pin29 CLKIN"),
    ("GND",          112.70, "pin28 GND"),
    ("+3V3",         115.24, "pin27 VDD→+3V3"),
    ("GND",          117.78, "pin26 AGND→GND"),
    ("AVDDOUT",      120.32, "pin25 AVDDOUT"),
]
for net, y, comment in u1_right:
    r = lbl(net, U1_RX, y, angle=180)
    print(f"  {ok(r)} {net:14s} y={y:.2f}  [{comment}]")

print()
print("--- J1 Power Connector (Conn_01x02 at (35,72)) ---")
# PinLocator: pin1=(29.92,72.0), pin2=(29.92,74.54)
r = lbl("+3V3", 29.92, 72.00, angle=180)
print(f"  {ok(r)} +3V3 @ pin1")
r = lbl("GND",  29.92, 74.54, angle=180)
print(f"  {ok(r)} GND  @ pin2")

print()
print("--- J2 Current Connector (Conn_01x08 at (35,96.19)) ---")
# PinLocator: pin1=(29.92,88.57) to pin8=(29.92,106.35)
j2_nets = ["IAP_J", "IAN_J", "IBP_J", "IBN_J", "ICP_J", "ICN_J", "INP_J", "INN_J"]
j2_ys   = [88.57,   91.11,   93.65,   96.19,   98.73,   101.27,  103.81,  106.35]
for net, y in zip(j2_nets, j2_ys):
    r = lbl(net, 29.92, y, angle=180)
    print(f"  {ok(r)} {net} @ pin y={y:.2f}")

print()
print("--- J3 Voltage Connector (Conn_01x06 at (35,124.13)) ---")
# PinLocator: pin1=(29.92,119.05) to pin6=(29.92,131.75)
j3_nets = ["VAN_J", "VAP_J", "VBN_J", "VBP_J", "VCN_J", "VCP_J"]
j3_ys   = [119.05,  121.59,  124.13,  126.67,  129.21,  131.75]
for net, y in zip(j3_nets, j3_ys):
    r = lbl(net, 29.92, y, angle=180)
    print(f"  {ok(r)} {net} @ pin y={y:.2f}")

print()
print("--- Test Pads TP1-TP11 (Conn_01x01 at x=165) ---")
# PinLocator: all pin1 at x=159.92 (not 162.46!)
# TP order matches U1 right-side SPI/CF/RESET signals
tp_nets = ["SS",   "MOSI",  "MISO",  "SCLK",  "IRQ0",
           "IRQ1", "CF1",   "CF2",   "CF3_ZX","CF4_DREADY","RESET"]
tp_ys   = [84.76,  87.30,   89.84,   92.38,   94.92,
           97.46,  100.00,  102.54,  105.08,  107.62,      110.16]
for net, y in zip(tp_nets, tp_ys):
    r = lbl(net, 159.92, y, angle=0)
    print(f"  {ok(r)} TP '{net}' @ (159.92,{y:.2f})")

print()
print("--- AA Filter Resistor Labels (R2-R15) ---")
# Device:R at (75, ry): p1 at (75, ry-3.81) [above], p2 at (75, ry+3.81) [below]
# p1 = IC side (IAP/IAN etc.), p2 = connector side (IAP_J/IAN_J etc.)
aa_r = [
    # (ref, ry, ic_net, j_net)
    ("R2",  86.03,  "IAP", "IAP_J"),
    ("R3",  88.57,  "IAN", "IAN_J"),
    ("R4",  91.11,  "IBP", "IBP_J"),
    ("R5",  93.65,  "IBN", "IBN_J"),
    ("R6",  96.19,  "ICP", "ICP_J"),
    ("R7",  98.73,  "ICN", "ICN_J"),
    ("R8",  101.27, "INP", "INP_J"),
    ("R9",  103.81, "INN", "INN_J"),
    ("R10", 116.51, "VAN", "VAN_J"),
    ("R11", 119.05, "VAP", "VAP_J"),
    ("R12", 121.59, "VBN", "VBN_J"),
    ("R13", 124.13, "VBP", "VBP_J"),
    ("R14", 126.67, "VCN", "VCN_J"),
    ("R15", 129.21, "VCP", "VCP_J"),
]
for ref, ry, ic_net, j_net in aa_r:
    r1 = lbl(ic_net, 75, ry - 3.81, angle=0)   # p1 = upper = IC side
    r2 = lbl(j_net,  75, ry + 3.81, angle=180)  # p2 = lower = connector side
    print(f"  {ok(r1)}{ok(r2)} {ref}: p1={ic_net}, p2={j_net}")

print()
print("--- AA Filter Cap Labels (C12-C25) ---")
# Device:C at (90, cy): p1 at (90, cy-3.81) [above], p2 at (90, cy+3.81) [below]
# cap placed at ic_y + 3.81, so cy = ic_y + 3.81
# p1 (upper) = GND, p2 (lower) = IC net (IAP etc.)
# Wait: cap shunts IC net to GND.
# From PinLocator for C12: p1=(90,86.03), p2=(90,93.65)
# cy = 86.03 + 3.81 = 89.84, so p1 = 89.84 - 3.81 = 86.03, p2 = 89.84 + 3.81 = 93.65
aa_c = [
    # (ref, ic_y, ic_net)  → cy = ic_y + 3.81
    ("C12", 86.03,  "IAP"),
    ("C13", 88.57,  "IAN"),
    ("C14", 91.11,  "IBP"),
    ("C15", 93.65,  "IBN"),
    ("C16", 96.19,  "ICP"),
    ("C17", 98.73,  "ICN"),
    ("C18", 101.27, "INP"),
    ("C19", 103.81, "INN"),
    ("C20", 116.51, "VAN"),
    ("C21", 119.05, "VAP"),
    ("C22", 121.59, "VBN"),
    ("C23", 124.13, "VBP"),
    ("C24", 126.67, "VCN"),
    ("C25", 129.21, "VCP"),
]
for ref, ic_y, ic_net in aa_c:
    cy = ic_y + 3.81
    r1 = lbl(ic_net, 90, cy + 3.81, angle=0)  # p2 (lower) = IC net
    r2 = lbl("GND",  90, cy - 3.81, angle=0)  # p1 (upper) = GND
    print(f"  {ok(r1)}{ok(r2)} {ref}: p2={ic_net}, p1=GND")

print()
print("--- Power Decoupling Caps (C1-C8) ---")
# Device:C: p1=(x,y-3.81) [above], p2=(x,y+3.81) [below]
decoup = [
    # (ref, x,   y,   p1_net, p2_net)
    ("C1",  157, 83,  "GND",     "+3V3"),
    ("C2",  163, 83,  "GND",     "+3V3"),
    ("C3",  157, 78,  "GND",     "AVDDOUT"),
    ("C4",  163, 78,  "GND",     "AVDDOUT"),
    ("C5",  105, 72,  "GND",     "DVDDOUT"),
    ("C6",  111, 72,  "GND",     "DVDDOUT"),
    ("C7",  105, 110, "GND",     "REF"),
    ("C8",  111, 110, "GND",     "REF"),
]
for ref, x, y, p1, p2 in decoup:
    r1 = lbl(p1, x, y - 3.81, angle=0)  # p1 upper
    r2 = lbl(p2, x, y + 3.81, angle=0)  # p2 lower
    print(f"  {ok(r1)}{ok(r2)} {ref}: p1={p1}, p2={p2}")

print()
print("--- Crystal Y1 (at (157,91)) + Load Caps C9, C10 ---")
# Y1: p1=(153.19,91.0)=CLKIN, p2=(160.81,91.0)=CLKOUT
r = lbl("CLKIN",  153.19, 91.0, angle=180)
print(f"  {ok(r)} Y1 p1=CLKIN")
r = lbl("CLKOUT", 160.81, 91.0, angle=0)
print(f"  {ok(r)} Y1 p2=CLKOUT")
# C9 @ (163, 89): p1=(163,85.19)=GND, p2=(163,92.81)=CLKIN
r1 = lbl("GND",   163, 89 - 3.81, angle=0)
r2 = lbl("CLKIN", 163, 89 + 3.81, angle=0)
print(f"  {ok(r1)}{ok(r2)} C9: p1=GND, p2=CLKIN")
# C10 @ (163, 93): p1=(163,89.19)=GND, p2=(163,96.81)=CLKOUT
r1 = lbl("GND",    163, 93 - 3.81, angle=0)
r2 = lbl("CLKOUT", 163, 93 + 3.81, angle=0)
print(f"  {ok(r1)}{ok(r2)} C10: p1=GND, p2=CLKOUT")

print()
print("--- Reset RC: R1 @ (100,80), C11 @ (106,80) ---")
# R1: p1=(100,76.19)=RESET, p2=(100,83.81)=+3V3
# (pullup: +3V3 → R1 → RESET node; lower pin = +3V3 side for pullup to supply)
r1 = lbl("RESET", 100, 80 - 3.81, angle=0)   # p1 upper = RESET net
r2 = lbl("+3V3",  100, 80 + 3.81, angle=0)   # p2 lower = +3V3
print(f"  {ok(r1)}{ok(r2)} R1: p1=RESET, p2=+3V3")
# C11: p1=(106,76.19)=GND, p2=(106,83.81)=RESET
r1 = lbl("GND",   106, 80 - 3.81, angle=0)
r2 = lbl("RESET", 106, 80 + 3.81, angle=0)
print(f"  {ok(r1)}{ok(r2)} C11: p1=GND, p2=RESET")

print()
print("--- LED Indicator: R16 @ (157,102), D1 @ (157,106) ---")
# R16: p1=(157,98.19), p2=(157,105.81)
# Circuit: CF2(from U1) → R16 → D1(anode) → D1(cathode) → GND
# R16 p1 (upper, y=98.19) = CF2_LED (to D1 anode)
# R16 p2 (lower, y=105.81) = CF2 (from U1 CF2 output)
r1 = lbl("CF2_LED", 157, 102 - 3.81, angle=0)  # p1 upper
r2 = lbl("CF2",     157, 102 + 3.81, angle=0)  # p2 lower
print(f"  {ok(r1)}{ok(r2)} R16: p1=CF2_LED, p2=CF2")
# D1 Device:LED: pA(anode)=(160.81,106.0), pK(cathode)=(153.19,106.0)
# Anode=CF2_LED, Cathode=GND
r1 = lbl("CF2_LED", 160.81, 106.0, angle=0)   # anode (right side)
r2 = lbl("GND",     153.19, 106.0, angle=180)  # cathode (left side)
print(f"  {ok(r1)}{ok(r2)} D1: anode=CF2_LED, cathode=GND")

print()
print("=== Summary ===")
if errors == 0:
    print(f"✓ All labels added successfully! No errors.")
else:
    print(f"✗ {errors} label(s) failed. Check messages above.")
print("Next: run ERC to validate")
