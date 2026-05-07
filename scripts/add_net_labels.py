"""
ADE9000 Breakout Board - Net Label Adder
Adds all net labels to connect schematic components.

Net strategy:
- J1 pin1 → +3V3 label
- J1 pin2 → GND label
- J2/J3 connector pins → IAP_J, IAN_J ... nets (left side of resistors)
- Resistors R2..R15 connect IAP_J → IAP through 1kΩ
- Caps C12..C25 connect node IAP etc → GND
- U1 analog pins get IAP, IAN... labels
- U1 digital pins get test pad labels
- Test pads TP1..TP11 get matching labels
- Power ties: PULL_HIGH→+3V3, PM0→GND, PM1→GND, DGND→GND, AGND→GND, REFGND→GND, EPAD→GND

Label angle convention:
- angle=0   → label faces RIGHT (normal, wire extends to the left)
- angle=180 → label faces LEFT (wire extends to the right)
"""
import sys
import json
import subprocess

SCH_PATH = r"c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_sch"
KI_IFACE = r"c:\Users\tisha\dev\KiCAD-MCP-Server\python\kicad_interface.py"
KI_PYTHON = r"C:\Program Files\KiCad\10.0\bin\python.exe"

def call_iface(command: str, params: dict):
    payload = json.dumps({"command": command, "params": params})
    result = subprocess.run(
        [KI_PYTHON, KI_IFACE],
        input=payload, capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(result.stdout)
    except Exception:
        data = {"success": False, "stdout": result.stdout, "stderr": result.stderr}
    if not data.get("success"):
        print(f"  WARN: {command} '{params.get('label', params.get('x', ''))}' failed: {data.get('message', data)[:80]}", file=sys.stderr)
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
        "schematicPath": SCH_PATH, "position": [x, y]
    })

ok = lambda r: "✓" if r.get("success") else "✗"

print("=== ADE9000 Net Label Adder ===\n")

# ─── PIN POSITIONS ─────────────────────────────────────────────────────────────
# U1 left pins wire at x=117.3; U1 right pins wire at x=142.7
U1_LX = 117.3
U1_RX = 142.7

# For labels ON U1 left wires (facing left, so net comes from left):
# angle=0 means text faces right → the wire end attaches left of label
# We want a label pointing INTO the wire end at x=117.3
# Use angle=180 so the connection point is on the RIGHT side of the label,
# placed just past the wire end.
# KiCad net label: the connection stub is at the label origin (x,y).
# angle=0: connection stub on left, text extends right.
# angle=180: connection stub on right, text extends left.
# For U1 left pins, wire ends are at x=117.3 pointing LEFT (toward x<117.3).
# So we place label at x=117.3 with angle=0 (stub on left matches wire going left).
# For U1 right pins, wire ends at x=142.7 pointing RIGHT (toward x>142.7).
# Place label at x=142.7 with angle=180 (stub on right matches wire going right).

print("--- U1 Left Pin Labels (analog + control) ---")
left_pin_labels = [
    # (net_name, x, y)
    ("+3V3",   U1_LX, 70.79),   # PULL_HIGH  (pin1)  → +3V3
    ("GND",    U1_LX, 73.33),   # DGND       (pin2)  → GND
    # DVDDOUT (pin3) gets its own node: DVDDOUT net (power output)
    ("GND",    U1_LX, 78.41),   # PM0        (pin4)  → GND (SPI mode)
    ("GND",    U1_LX, 80.95),   # PM1        (pin5)  → GND (normal mode)
    ("RESET",  U1_LX, 83.49),   # ~RESET~    (pin6)
    # Analog current inputs
    ("IAP",    U1_LX, 86.03),
    ("IAN",    U1_LX, 88.57),
    ("IBP",    U1_LX, 91.11),
    ("IBN",    U1_LX, 93.65),
    ("ICP",    U1_LX, 96.19),
    ("ICN",    U1_LX, 98.73),
    ("INP",    U1_LX, 101.27),
    ("INN",    U1_LX, 103.81),
    ("GND",    U1_LX, 106.35),  # REFGND     (pin15) → GND
    ("REF",    U1_LX, 108.89),  # REF output (pin16)
    # NC1/NC2 → no-connect, handled separately
    # Analog voltage inputs
    ("VAN",    U1_LX, 116.51),
    ("VAP",    U1_LX, 119.05),
    ("VBN",    U1_LX, 121.59),
    ("VBP",    U1_LX, 124.13),
    ("VCN",    U1_LX, 126.67),
    ("VCP",    U1_LX, 129.21),
]

for net, x, y in left_pin_labels:
    r = label(net, x, y, angle=0)
    print(f"  {ok(r)} label '{net}' @ ({x}, {y:.2f})")

# DVDDOUT output node label
r = label("DVDDOUT", U1_LX, 75.87, angle=0)
print(f"  {ok(r)} label 'DVDDOUT' @ ({U1_LX}, 75.87)")

print()
print("--- U1 Right Pin Labels (power + SPI + CF) ---")
right_pin_labels = [
    # (net_name, x, y)
    ("AVDDOUT", U1_RX, 79.68),   # pin25
    ("GND",     U1_RX, 82.22),   # AGND (pin26) → GND
    ("+3V3",    U1_RX, 84.76),   # VDD  (pin27) → +3V3 in
    ("GND",     U1_RX, 87.30),   # GND  (pin28)
    ("CLKIN",   U1_RX, 89.84),   # CLKIN (pin29)
    ("CLKOUT",  U1_RX, 92.38),   # CLKOUT (pin30)
    ("IRQ0",    U1_RX, 94.92),   # ~IRQ0~ (pin31)
    ("IRQ1",    U1_RX, 97.46),   # ~IRQ1~ (pin32)
    ("CF1",     U1_RX, 100.00),  # CF1 (pin33)
    ("CF2",     U1_RX, 102.54),  # CF2 (pin34)
    ("CF3_ZX",  U1_RX, 105.08),  # CF3/ZX (pin35)
    ("CF4_DREADY", U1_RX, 107.62),  # CF4/DREADY (pin36)
    ("SCLK",    U1_RX, 110.16),  # SCLK (pin37)
    ("MISO",    U1_RX, 112.70),  # MISO (pin38)
    ("MOSI",    U1_RX, 115.24),  # MOSI (pin39)
    ("SS",      U1_RX, 117.78),  # ~SS~ (pin40)
    ("GND",     U1_RX, 120.32),  # EPAD → GND
]

for net, x, y in right_pin_labels:
    r = label(net, x, y, angle=180)
    print(f"  {ok(r)} label '{net}' @ ({x}, {y:.2f})")

# ─── NO-CONNECTS for NC1, NC2 ─────────────────────────────────────────────────
print()
print("--- No-Connects ---")
r = no_connect(U1_LX, 111.43)
print(f"  {ok(r)} no-connect NC1 @ ({U1_LX}, 111.43)")
r = no_connect(U1_LX, 113.97)
print(f"  {ok(r)} no-connect NC2 @ ({U1_LX}, 113.97)")

# ─── J1 POWER CONNECTOR ──────────────────────────────────────────────────────
# Conn_01x02 at (35, 72)
# Pin1 at (29.92, 72.00), Pin2 at (29.92, 69.46)
print()
print("--- J1 Power Connector ---")
# J1 connector pin ends are on the LEFT side of the connector (at x ≈ 29.92)
# Labels face right (angle=0) connecting to the stub
r = label("+3V3", 29.92, 72.00, angle=180)
print(f"  {ok(r)} label '+3V3' J1-pin1")
r = label("GND",  29.92, 69.46, angle=180)
print(f"  {ok(r)} label 'GND'  J1-pin2")

# ─── J2 CURRENT CONNECTOR ────────────────────────────────────────────────────
# Conn_01x08 at (35, 96.19) — pin ends at x=29.92
# Pin y-positions: pin1(bottom)=103.81, pin2=101.27, ..., pin8(top)=86.03
# Net assignment (bottom=pin1=INN, top=pin8=IAP):
print()
print("--- J2 Current Connector ---")
j2_pins = [
    (29.92, 103.81, "INN_J"),  # pin1
    (29.92, 101.27, "INP_J"),  # pin2
    (29.92,  98.73, "ICN_J"),  # pin3
    (29.92,  96.19, "ICP_J"),  # pin4
    (29.92,  93.65, "IBN_J"),  # pin5
    (29.92,  91.11, "IBP_J"),  # pin6
    (29.92,  88.57, "IAN_J"),  # pin7
    (29.92,  86.03, "IAP_J"),  # pin8
]
for x, y, net in j2_pins:
    r = label(net, x, y, angle=180)
    print(f"  {ok(r)} label '{net}' @ ({x}, {y:.2f})")

# ─── J3 VOLTAGE CONNECTOR ────────────────────────────────────────────────────
# Conn_01x06 at (35, 124.13) — pin ends at x=29.92
# Pin1=(y+5.08)=129.21(bottom), Pin6=(y-7.62)=116.51(top)
print()
print("--- J3 Voltage Connector ---")
j3_pins = [
    (29.92, 129.21, "VCP_J"),  # pin1
    (29.92, 126.67, "VCN_J"),  # pin2
    (29.92, 124.13, "VBP_J"),  # pin3
    (29.92, 121.59, "VBN_J"),  # pin4
    (29.92, 119.05, "VAP_J"),  # pin5
    (29.92, 116.51, "VAN_J"),  # pin6
]
for x, y, net in j3_pins:
    r = label(net, x, y, angle=180)
    print(f"  {ok(r)} label '{net}' @ ({x}, {y:.2f})")

# ─── ANTI-ALIASING RESISTORS R2–R15 ─────────────────────────────────────────
# Each resistor: pin1 at (75, y+3.81) = _J net; pin2 at (75, y-3.81) = IC net
# Device:R: pin1=(0,3.81), pin2=(0,-3.81) in symbol space
# At position (75, y_r): pin1 absolute y = y_r+3.81, pin2 = y_r-3.81
print()
print("--- AA Filter Resistor Labels ---")
aa_filters = [
    # (r_ref, r_y, j_net, ic_net)
    ("R2",  86.03,  "IAP_J", "IAP"),
    ("R3",  88.57,  "IAN_J", "IAN"),
    ("R4",  91.11,  "IBP_J", "IBP"),
    ("R5",  93.65,  "IBN_J", "IBN"),
    ("R6",  96.19,  "ICP_J", "ICP"),
    ("R7",  98.73,  "ICN_J", "ICN"),
    ("R8",  101.27, "INP_J", "INP"),
    ("R9",  103.81, "INN_J", "INN"),
    ("R10", 116.51, "VAN_J", "VAN"),
    ("R11", 119.05, "VAP_J", "VAP"),
    ("R12", 121.59, "VBN_J", "VBN"),
    ("R13", 124.13, "VBP_J", "VBP"),
    ("R14", 126.67, "VCN_J", "VCN"),
    ("R15", 129.21, "VCP_J", "VCP"),
]
for ref, ry, j_net, ic_net in aa_filters:
    # pin1 (top in symbol) = source side = _J net
    r1 = label(j_net,  75, ry + 3.81, angle=180)
    # pin2 (bottom) = IC side net
    r2 = label(ic_net, 75, ry - 3.81, angle=0)
    print(f"  {ok(r1)}{ok(r2)} {ref}: {j_net}→{ic_net}")

# ─── AA FILTER CAPS C12–C25 ──────────────────────────────────────────────────
# Each cap: pin1 at (90, y+3.81) = IC net; pin2 at (90, y-3.81) = GND
# Placed at (90, ic_pin_y + 3.81) → cap_y = ic_y + 3.81
# pin1 absolute y = cap_y + 3.81 = ic_y + 7.62
# pin2 absolute y = cap_y - 3.81 = ic_y
print()
print("--- AA Filter Cap Labels ---")
aa_caps = [
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
for ref, ic_y, ic_net in aa_caps:
    cy = ic_y + 3.81  # capacitor placement y
    # pin1 at cy+3.81 connects to the IC net; pin2 at cy-3.81 = GND
    r1 = label(ic_net, 90, cy + 3.81, angle=0)
    r2 = label("GND",  90, cy - 3.81, angle=0)
    print(f"  {ok(r1)}{ok(r2)} {ref}: pin1={ic_net}, pin2=GND")

# ─── POWER DECOUPLING CAPS C1–C8 ─────────────────────────────────────────────
# All caps: pin1 at (x, y+3.81), pin2 at (x, y-3.81)
# VDD decoupling (C1, C2) near VDD at (157/163, 83)
# pin1 → +3V3 or AVDDOUT/DVDDOUT/REF; pin2 → GND
print()
print("--- Decoupling Cap Labels ---")
decoup_caps = [
    # (ref, x,   y,   pin1_net, pin2_net)
    ("C1",  157, 83,  "+3V3",    "GND"),
    ("C2",  163, 83,  "+3V3",    "GND"),
    ("C3",  157, 78,  "AVDDOUT", "GND"),
    ("C4",  163, 78,  "AVDDOUT", "GND"),
    ("C5",  105, 72,  "DVDDOUT", "GND"),
    ("C6",  111, 72,  "DVDDOUT", "GND"),
    ("C7",  105, 110, "REF",     "GND"),
    ("C8",  111, 110, "REF",     "GND"),
]
for ref, x, y, p1, p2 in decoup_caps:
    r1 = label(p1, x, y + 3.81, angle=0)
    r2 = label(p2, x, y - 3.81, angle=0)
    print(f"  {ok(r1)}{ok(r2)} {ref}: pin1={p1}, pin2={p2}")

# ─── CRYSTAL Y1 + LOAD CAPS ──────────────────────────────────────────────────
# Crystal at (157, 91): pin1=(-3.81,0)→(153.19, 91), pin2=(3.81,0)→(160.81, 91)
# But at 0° rotation: pin1 connects LEFT, pin2 connects RIGHT
# CLKIN net on left, CLKOUT on right
print()
print("--- Crystal Labels ---")
r = label("CLKIN",  153.19, 91, angle=180)
print(f"  {ok(r)} Y1 pin1 → CLKIN")
r = label("CLKOUT", 160.81, 91, angle=0)
print(f"  {ok(r)} Y1 pin2 → CLKOUT")

# C9 @ (163, 89): pin1 top = CLKIN, pin2 bottom = GND
# C10 @ (163, 93): pin1 top = CLKOUT, pin2 bottom = GND
r = label("CLKIN",  163, 89 + 3.81, angle=0)
r = label("GND",    163, 89 - 3.81, angle=0)
print(f"  {ok(r)} C9: CLKIN / GND")
r = label("CLKOUT", 163, 93 + 3.81, angle=0)
r = label("GND",    163, 93 - 3.81, angle=0)
print(f"  {ok(r)} C10: CLKOUT / GND")

# ─── RESET RC ────────────────────────────────────────────────────────────────
# R1 @ (100, 80): pin1 top=(100, 83.81) = +3V3; pin2 bottom=(100, 76.19) = RESET
# C11 @ (106, 80): pin1 top=(106, 83.81) = RESET; pin2 bottom=(106, 76.19) = GND
print()
print("--- Reset RC Labels ---")
r = label("+3V3",  100, 80 + 3.81, angle=0)
print(f"  {ok(r)} R1 pin1 → +3V3")
r = label("RESET", 100, 80 - 3.81, angle=0)
print(f"  {ok(r)} R1 pin2 → RESET")
r = label("RESET", 106, 80 + 3.81, angle=0)
print(f"  {ok(r)} C11 pin1 → RESET")
r = label("GND",   106, 80 - 3.81, angle=0)
print(f"  {ok(r)} C11 pin2 → GND")

# ─── TEST PADS TP1–TP11 ───────────────────────────────────────────────────────
# Conn_01x01 at (165, y): pin1 at (162.46, y) approximately
# (pin1 = (-2.54, 0) from symbol origin)
print()
print("--- Test Pad Labels ---")
tp_labels = [
    (165, 84.76,  "SS"),
    (165, 87.30,  "MOSI"),
    (165, 89.84,  "MISO"),
    (165, 92.38,  "SCLK"),
    (165, 94.92,  "IRQ0"),
    (165, 97.46,  "IRQ1"),
    (165, 100.00, "CF1"),
    (165, 102.54, "CF2"),
    (165, 105.08, "CF3_ZX"),
    (165, 107.62, "CF4_DREADY"),
    (165, 110.16, "RESET"),
]
for x, y, net in tp_labels:
    pin_x = x - 2.54
    r = label(net, pin_x, y, angle=0)
    print(f"  {ok(r)} TP '{net}' @ ({pin_x:.2f}, {y:.2f})")

# ─── LED / CF2 INDICATOR ─────────────────────────────────────────────────────
# R16 @ (157, 102): pin1 top=(157, 105.81)=+3V3, pin2 bot=(157, 98.19)=CF2_LED
# D1  @ (157, 106): pin1 top=(157, 109.81)=CF2_LED, pin2 bot=(157, 102.19)→GND
# Wait - Device:LED has anode at pin1 and cathode at pin2
# Typical LED circuit: +3V3 → R16 → anode (LED) → cathode → GND
# But CF2 is an output pulse from IC — connect as: CF2 → R16 → anode → cathode → GND
print()
print("--- CF2 LED indicator labels ---")
r = label("CF2",  157, 102 + 3.81, angle=0)
print(f"  {ok(r)} R16 pin1 → CF2")
r = label("CF2_LED", 157, 102 - 3.81, angle=0)
print(f"  {ok(r)} R16 pin2 → CF2_LED")
r = label("CF2_LED", 157, 106 + 3.81, angle=0)
print(f"  {ok(r)} D1 pin1 → CF2_LED")
r = label("GND",  157, 106 - 3.81, angle=0)
print(f"  {ok(r)} D1 pin2 → GND")

print()
print("=== Net labels complete ===")
print("Next: run ERC to validate")
