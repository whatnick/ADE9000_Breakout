"""
Diagnose label positions vs actual pin positions in the schematic.
Compare label positions to where U1's pins actually are.
"""
import sys
sys.path.insert(0, 'C:/Program Files/KiCad/10.0/bin/Lib/site-packages')
sys.path.insert(0, 'C:/Users/tisha/OneDrive/Documents/KiCad/10.0/3rdparty/Python311/site-packages')

from skip import Schematic

sch = Schematic('c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_sch')

# Find U1 and its placement
u1 = None
for s in sch.symbol:
    ref = str(s.reference).strip('"')
    if ref == 'U1':
        u1 = s
        break

if u1 is None:
    print("ERROR: U1 not found!")
    sys.exit(1)

u1_at = u1.at
u1_x = float(u1_at[0])
u1_y = float(u1_at[1])
try:
    u1_angle = float(u1_at[2]) if len(u1_at) > 2 else 0
except:
    u1_angle = 0

print(f"U1 placement: at ({u1_x}, {u1_y}), angle={u1_angle}")
print(f"U1 mirror: {u1.mirror if hasattr(u1, 'mirror') else 'none'}")
print()

# Get all labels at x close to 117.3 (left side of U1)
labels_left = []
labels_right = []
for lb in sch.label:
    name = str(lb.value).strip('"')
    at = lb.at
    lx = round(float(at[0]), 2)
    ly = round(float(at[1]), 2)
    if abs(lx - 117.3) < 0.5:
        labels_left.append((ly, name))
    elif abs(lx - 142.7) < 0.5:
        labels_right.append((ly, name))

labels_left.sort()
labels_right.sort()

# Expected pin positions (from symbol def: pin at symbol (x_sym, y_sym), 
# schematic pos = U1_x + x_sym, U1_y + y_sym)
# LEFT pins (x_sym=-12.7, so schematic x=117.3)
left_pins = [
    ("PULL_HIGH", 1,  -29.21, "+3V3"),
    ("DGND",      2,  -26.67, "GND"),
    ("DVDDOUT",   3,  -24.13, "DVDDOUT"),
    ("PM0",       4,  -21.59, "GND"),
    ("PM1",       5,  -19.05, "GND"),
    ("RESET",     6,  -16.51, "RESET"),
    ("IAP",       7,  -13.97, "IAP"),
    ("IAN",       8,  -11.43, "IAN"),
    ("IBP",       9,   -8.89, "IBP"),
    ("IBN",      10,   -6.35, "IBN"),
    ("ICP",      11,   -3.81, "ICP"),
    ("ICN",      12,   -1.27, "ICN"),
    ("INP",      13,    1.27, "INP"),
    ("INN",      14,    3.81, "INN"),
    ("REFGND",   15,    6.35, "GND"),
    ("REF",      16,    8.89, "REF"),
    ("NC1",      17,   11.43, "no-connect"),
    ("NC2",      18,   13.97, "no-connect"),
    ("VAN",      19,   16.51, "VAN"),
    ("VAP",      20,   19.05, "VAP"),
    ("VBN",      21,   21.59, "VBN"),
    ("VBP",      22,   24.13, "VBP"),
    ("VCN",      23,   26.67, "VCN"),
    ("VCP",      24,   29.21, "VCP"),
]

print("LEFT SIDE PIN ANALYSIS (x=117.3)")
print(f"{'Pin':<5} {'Name':<12} {'Expected Y':<12} {'Net':<12} {'Label in File'}")
print("-" * 70)
for pin_name, pin_num, y_sym, expected_net in left_pins:
    expected_y = round(u1_y + y_sym, 2)
    # Find label closest to expected_y
    closest = min(labels_left, key=lambda t: abs(t[0] - expected_y)) if labels_left else None
    label_at = f"{closest[1]}@{closest[0]}" if closest and abs(closest[0] - expected_y) < 1.5 else "NONE"
    match = "✓" if closest and abs(closest[0] - expected_y) < 0.05 else ("~" if closest and abs(closest[0] - expected_y) < 1.5 else "✗")
    print(f"{pin_num:<5} {pin_name:<12} {expected_y:<12} {expected_net:<12} {label_at}  {match}")

print()
print("Labels actually in file at x≈117.3:")
for ly, name in labels_left:
    print(f"  y={ly}  {name}")
