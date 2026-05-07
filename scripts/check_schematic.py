import sys
sys.path.insert(0, 'C:/Program Files/KiCad/10.0/bin/Lib/site-packages')
sys.path.insert(0, 'C:/Users/tisha/OneDrive/Documents/KiCad/10.0/3rdparty/Python311/site-packages')

from skip import Schematic
from collections import Counter

sch = Schematic('c:/Users/tisha/dev/ADE9000_Breakout/ADE9000_Breakout.kicad_sch')

syms = list(sch.symbol)
labels = list(sch.label) if hasattr(sch, 'label') else []
no_connects = list(sch.no_connect) if hasattr(sch, 'no_connect') else []

print(f'Symbols: {len(syms)}')
print(f'Net labels: {len(labels)}')
print(f'No-connects: {len(no_connects)}')

# Show all label positions for debugging
print()
print('All labels (name, x, y):')
label_data = []
for lb in labels:
    name = str(lb.value).strip('"') if hasattr(lb, 'value') else '?'
    try:
        at = lb.at
        x = round(float(at[0]), 2)
        y = round(float(at[1]), 2)
    except Exception:
        x, y = '?', '?'
    label_data.append((name, x, y))

label_data.sort(key=lambda t: (t[0], t[1] if isinstance(t[1], float) else 0))
for name, x, y in label_data:
    print(f'  {name}  @  ({x}, {y})')

# Show all symbols with ref and position
print()
print('All symbols (ref, value, x, y):')
for s in syms:
    try:
        ref = str(s.reference).strip('"')
        val = str(s.value).strip('"')
        at = s.at
        x = round(float(at[0]), 2)
        y = round(float(at[1]), 2)
        print(f'  {ref}  {val}  @  ({x}, {y})')
    except Exception as e:
        print(f'  ERR: {e}')
