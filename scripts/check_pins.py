import re

def get_conn_pins(lib_file, symbol_name):
    with open(lib_file) as f:
        content = f.read()
    start = content.find(f'(symbol "{symbol_name}"')
    end = content.find(f'(symbol "', start + 1)
    # Skip sub-symbol entries
    while end > 0 and content[end:].startswith(f'(symbol "{symbol_name}_'):
        end = content.find('(symbol "', end + 1)
    block = content[start:end if end > 0 else start + 5000]
    pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)', block)
    return pins

conn_lib = r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Connector_Generic.kicad_sym"
dev_lib = r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Device.kicad_sym"

for sym in ["Conn_01x02", "Conn_01x06", "Conn_01x08"]:
    pins = get_conn_pins(conn_lib, sym)
    print(f"{sym}: {len(pins)} pins")
    for i, (x,y) in enumerate(pins):
        print(f"  pin {i+1}: ({x}, {y})")

for sym in ["R", "C", "C_Polarized", "Crystal"]:
    pins = get_conn_pins(dev_lib, sym)
    print(f"\nDevice:{sym}: {len(pins)} pins")
    for i, (x,y) in enumerate(pins):
        print(f"  pin {i+1}: ({x}, {y})")
