"""
ADE9000 Breakout - connectivity rewriter

This script rebuilds the generated schematic connectivity for the ADE9000 breakout.
The ADE9000 pins, headers, and compact support circuits still use short wire
stubs plus labels, but the analog input conditioning is laid out as readable
series-R/shunt-C rows that follow the Figure 55 test-circuit structure.
"""

import copy
import json
import subprocess
import uuid
from pathlib import Path

import sexpdata

SCH_PATH = r"c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_sch"
KI_IFACE = r"c:\Users\tisha\dev\KiCAD-MCP-Server\python\kicad_interface.py"
KI_PYTHON = r"C:\Program Files\KiCad\10.0\bin\python.exe"
RESISTOR_FOOTPRINT = "Resistor_SMD:R_0603_1608Metric"
CAPACITOR_0603_FOOTPRINT = "Capacitor_SMD:C_0603_1608Metric"
CAPACITOR_0603_REFS = {"C2", "C4", "C6", "C8", "C9", "C10", "C11"} | {f"C{index}" for index in range(12, 26)}
IO_STUB = 2.54
PASSIVE_STUB = 1.27
FILTER_R_X = 82.0
FILTER_C_X = 102.0
FILTER_INPUT_LABEL_X = 62.0
FILTER_OUTPUT_LABEL_X = 98.0
BURDEN_R_X = 52.0
BURDEN_LABEL_X = 46.0
DIVIDER_R_X = 70.0
DIVIDER_SHUNT_R_X = 75.5
DIGITAL_HEADER_NETS = [
    "+3V3",
    "GND",
    "SS",
    "MOSI",
    "MISO",
    "SCLK",
    "IRQ0",
    "IRQ1",
    "CF1",
    "CF2",
    "CF3_ZX",
    "CF4_DREADY",
    "RESET",
    "CLKIN",
    "CLKOUT",
    "GND",
]
CURRENT_JACK_NETS = {
    "CTA1": ["IAP_J", "IAN_J", "GND"],
    "CTB1": ["IBP_J", "IBN_J", "GND"],
    "CTC1": ["ICP_J", "ICN_J", "GND"],
    "CTN1": ["INP_J", "INN_J", "GND"],
}
VOLTAGE_TERMINAL_NETS = {
    "J2": ["VAP_J", "VAN_J"],
    "J3": ["VBP_J", "VBN_J"],
    "J4": ["VCP_J", "VCN_J"],
}


FILTER_ROWS = [
    ("R2", "C12", "IAP_J", "IAP", 50.0),
    ("R3", "C13", "IAN_J", "IAN", 58.5),
    ("R4", "C14", "IBP_J", "IBP", 67.0),
    ("R5", "C15", "IBN_J", "IBN", 75.5),
    ("R6", "C16", "ICP_J", "ICP", 84.0),
    ("R7", "C17", "ICN_J", "ICN", 92.5),
    ("R8", "C18", "INP_J", "INP", 101.0),
    ("R9", "C19", "INN_J", "INN", 109.5),
    ("R11", "C21", "VAP_J", "VAP", 127.0),
    ("R10", "C20", "VAN_J", "VAN", 137.5),
    ("R13", "C23", "VBP_J", "VBP", 148.0),
    ("R12", "C22", "VBN_J", "VBN", 158.5),
    ("R15", "C25", "VCP_J", "VCP", 169.0),
    ("R14", "C24", "VCN_J", "VCN", 179.5),
]

VOLTAGE_DIVIDER_ROWS = [
    ("R21", "R27", "VAP_J", "VAP_DIV", "R11", "C21", "VAP", 127.0),
    ("R22", "R28", "VAN_J", "VAN_DIV", "R10", "C20", "VAN", 137.5),
    ("R23", "R29", "VBP_J", "VBP_DIV", "R13", "C23", "VBP", 148.0),
    ("R24", "R30", "VBN_J", "VBN_DIV", "R12", "C22", "VBN", 158.5),
    ("R25", "R31", "VCP_J", "VCP_DIV", "R15", "C25", "VCP", 169.0),
    ("R26", "R32", "VCN_J", "VCN_DIV", "R14", "C24", "VCN", 179.5),
]

VOLTAGE_FILTER_REFS = {row[4] for row in VOLTAGE_DIVIDER_ROWS}

YHDC_BURDEN_ROWS = [
    ("R17", "IAP_J", "IAN_J", 54.25),
    ("R18", "IBP_J", "IBN_J", 71.25),
    ("R19", "ICP_J", "ICN_J", 88.25),
    ("R20", "INP_J", "INN_J", 105.25),
]


COMPONENT_POSES = {
    "J1": (210.0, 110.0, 0.0),
    "CTA1": (35.0, 55.0, 0.0),
    "CTB1": (35.0, 70.0, 0.0),
    "CTC1": (35.0, 85.0, 0.0),
    "CTN1": (35.0, 100.0, 0.0),
    "J2": (35.0, 127.0, 0.0),
    "J3": (35.0, 140.0, 0.0),
    "J4": (35.0, 153.0, 0.0),
    "C7": (108.0, 53.0, 0.0),
    "C8": (114.0, 53.0, 0.0),
    "C5": (108.0, 145.0, 0.0),
    "C6": (114.0, 145.0, 0.0),
    "R1": (108.0, 134.0, 0.0),
    "C11": (114.0, 134.0, 0.0),
    "Y1": (168.0, 94.0, 0.0),
    "C9": (180.0, 90.0, 0.0),
    "C10": (180.0, 98.0, 0.0),
    "R16": (180.0, 128.0, 0.0),
    "D1": (180.0, 136.0, 0.0),
    "C3": (166.0, 145.0, 0.0),
    "C4": (172.0, 145.0, 0.0),
    "C1": (166.0, 158.0, 0.0),
    "C2": (172.0, 158.0, 0.0),
    "#FLG1": (20.0, 74.54, 0.0),
    "#FLG2": (20.0, 70.0, 0.0),
    "#FLG3": (195.0, 134.0, 0.0),
    "#FLG4": (195.0, 139.0, 0.0),
    "#FLG5": (195.0, 144.0, 0.0),
}


def atom_name(atom) -> str:
    if isinstance(atom, sexpdata.Symbol):
        return atom.value()
    return str(atom)


def component_ref(symbol_block: list) -> str | None:
    for item in symbol_block:
        if isinstance(item, list) and item and atom_name(item[0]) == "property" and len(item) > 2 and item[1] == "Reference":
            return item[2]
    return None


def component_property(symbol_block: list, name: str) -> list | None:
    for item in symbol_block:
        if isinstance(item, list) and item and atom_name(item[0]) == "property" and len(item) > 2 and item[1] == name:
            return item
    return None


def set_property(symbol_block: list, name: str, value: str) -> None:
    prop = component_property(symbol_block, name)
    if prop is not None:
        prop[2] = value


def set_lib_id(symbol_block: list, lib_id: str) -> None:
    for item in symbol_block:
        if isinstance(item, list) and item and atom_name(item[0]) == "lib_id":
            item[1] = lib_id
            return


def refresh_uuids(block) -> None:
    if not isinstance(block, list):
        return
    if block and atom_name(block[0]) == "uuid" and len(block) > 1:
        block[1] = str(uuid.uuid4())
        return
    for item in block:
        refresh_uuids(item)


def replace_string(block, old: str, new: str) -> None:
    if not isinstance(block, list):
        return
    for index, item in enumerate(block):
        if item == old:
            block[index] = new
        else:
            replace_string(item, old, new)


def ensure_connector_symbol(
    data: list,
    symbols: list,
    ref: str,
    value: str,
    lib_id: str,
    footprint: str,
    template_ref: str,
) -> None:
    existing = next((symbol for symbol in symbols if component_ref(symbol) == ref), None)
    if existing is None:
        template = next((symbol for symbol in symbols if component_ref(symbol) == template_ref), None)
        if template is None:
            template = next((symbol for symbol in symbols if component_ref(symbol) in {"J1", "J2", "J3"}), None)
        if template is None:
            return
        existing = copy.deepcopy(template)
        old_ref = component_ref(existing)
        if old_ref is not None:
            replace_string(existing, old_ref, ref)
        refresh_uuids(existing)
        data.insert(-2, existing)
        symbols.append(existing)

    set_lib_id(existing, lib_id)
    set_property(existing, "Reference", ref)
    set_property(existing, "Value", value)
    set_property(existing, "Footprint", footprint)


def ensure_resistor_symbol(data: list, symbols: list, ref: str, value: str, template_ref: str = "R2") -> None:
    existing = next((symbol for symbol in symbols if component_ref(symbol) == ref), None)
    if existing is None:
        template = next((symbol for symbol in symbols if component_ref(symbol) == template_ref), None)
        if template is None:
            return
        existing = copy.deepcopy(template)
        old_ref = component_ref(existing)
        if old_ref is not None:
            replace_string(existing, old_ref, ref)
        refresh_uuids(existing)
        data.insert(-2, existing)
        symbols.append(existing)

    set_lib_id(existing, "Device:R")
    set_property(existing, "Reference", ref)
    set_property(existing, "Value", value)
    set_property(existing, "Footprint", RESISTOR_FOOTPRINT)


def normalize_passive_footprints(symbol: list, ref: str) -> None:
    if ref.startswith("R") and ref[1:].isdigit():
        set_property(symbol, "Footprint", RESISTOR_FOOTPRINT)
    elif ref in CAPACITOR_0603_REFS:
        set_property(symbol, "Footprint", CAPACITOR_0603_FOOTPRINT)


def normalize_debug_symbols(data: list) -> None:
    symbols = [
        item
        for item in data
        if isinstance(item, list) and item and atom_name(item[0]) == "symbol"
    ]

    # The larger ATM-style board replaces compact debug pads with connectorized I/O.
    data[:] = [
        item
        for item in data
        if not (
            isinstance(item, list)
            and item
            and atom_name(item[0]) == "symbol"
            and component_ref(item) in {"TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7", "TP8", "TP9", "TP10", "TP11", "TP12", "TP13"}
        )
    ]

    symbols = [
        item
        for item in data
        if isinstance(item, list) and item and atom_name(item[0]) == "symbol"
    ]
    ensure_connector_symbol(
        data,
        symbols,
        "J1",
        "Digital breadboard",
        "Connector_Generic:Conn_01x16",
        "SparkFun-Connector:1x16_Locking",
        "J1",
    )
    for ref in CURRENT_JACK_NETS:
        ensure_connector_symbol(
            data,
            symbols,
            ref,
            "CT stereo jack",
            "Connector_Generic:Conn_01x03",
            "Connector_Audio:Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal",
            "J2",
        )
    for ref in VOLTAGE_TERMINAL_NETS:
        ensure_connector_symbol(
            data,
            symbols,
            ref,
            "Voltage terminal",
            "Connector_Generic:Conn_01x02",
            "ADE9000-Local:TerminalBlock_4Ucon_1x02_P3.50mm_Horizontal_ADE9000",
            "J3",
        )
    for ref, *_rest in YHDC_BURDEN_ROWS:
        ensure_resistor_symbol(data, symbols, ref, "2.4R")
    for high_ref, low_ref, *_rest in VOLTAGE_DIVIDER_ROWS:
        ensure_resistor_symbol(data, symbols, high_ref, "100k")
        ensure_resistor_symbol(data, symbols, low_ref, "2.49k")


def set_at(block: list, x: float, y: float, angle: float | None = None) -> None:
    for item in block:
        if isinstance(item, list) and item and atom_name(item[0]) == "at":
            item[1] = round(x, 2)
            item[2] = round(y, 2)
            if angle is not None:
                if len(item) > 3:
                    item[3] = float(angle)
                else:
                    item.append(float(angle))
            return


def layout_components() -> None:
    poses: dict[str, tuple[float, float, float]] = dict(COMPONENT_POSES)
    for ref, *_nets, row_y in YHDC_BURDEN_ROWS:
        poses[ref] = (BURDEN_R_X, row_y, 0.0)
    for ref_r, ref_c, *_rest, row_y in FILTER_ROWS:
        poses[ref_r] = (FILTER_R_X, row_y, 90.0)
        poses[ref_c] = (FILTER_C_X, row_y + 3.81, 0.0)
    for high_ref, low_ref, *_rest, row_y in VOLTAGE_DIVIDER_ROWS:
        poses[high_ref] = (DIVIDER_R_X, row_y, 90.0)
        poses[low_ref] = (DIVIDER_SHUNT_R_X, row_y + 3.81, 0.0)

    data = sexpdata.loads(Path(SCH_PATH).read_text())
    normalize_debug_symbols(data)
    for item in data:
        if not (isinstance(item, list) and item and atom_name(item[0]) == "symbol"):
            continue
        ref = component_ref(item)
        if ref:
            normalize_passive_footprints(item, ref)
        if ref not in poses:
            continue

        x, y, angle = poses[ref]
        set_at(item, x, y, angle)
        for child in item:
            if not (isinstance(child, list) and child and atom_name(child[0]) == "property"):
                continue
            prop_name = child[1]
            if prop_name == "Reference":
                set_at(child, x, y - 2.54, 0.0)
            elif prop_name == "Value":
                set_at(child, x, y + 2.54, 0.0)
            elif prop_name in {"Footprint", "Datasheet"}:
                set_at(child, x, y, 0.0)

    Path(SCH_PATH).write_text(sexpdata.dumps(data))


def remove_sexp_blocks(content: str, keyword: str) -> str:
    result = []
    index = 0
    search_term = f"({keyword} "
    while index < len(content):
        start = content.find(search_term, index)
        if start == -1:
            result.append(content[index:])
            break
        result.append(content[index:start])
        depth = 0
        cursor = start
        while cursor < len(content):
            if content[cursor] == '(':
                depth += 1
            elif content[cursor] == ')':
                depth -= 1
                if depth == 0:
                    cursor += 1
                    break
            cursor += 1
        while cursor < len(content) and content[cursor] in ' \t\r\n':
            cursor += 1
        index = cursor
    return ''.join(result)


def call_iface(command: str, params: dict) -> dict:
    payload = json.dumps({"command": command, "params": params})
    result = subprocess.run(
        [KI_PYTHON, KI_IFACE],
        input=payload,
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"success": False, "message": result.stderr[:200] or result.stdout[:200]}


def add_wire(start_x: float, start_y: float, end_x: float, end_y: float) -> dict:
    block = (
        f' (wire (pts (xy {start_x} {start_y}) (xy {end_x} {end_y})) '
        f'(stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))'
    )
    append_schematic_block(block)
    return {"success": True}


def add_label(net: str, x: float, y: float, angle: int = 0) -> dict:
    justify = "left bottom" if angle == 0 else "right bottom"
    block = (
        f' (label "{net}" (at {x} {y} {angle}) '
        f'(effects (font (size 1.27 1.27)) (justify {justify})) (uuid "{uuid.uuid4()}"))'
    )
    append_schematic_block(block)
    return {"success": True}


def add_no_connect(x: float, y: float) -> dict:
    append_schematic_block(f' (no_connect (at {x} {y}) (uuid "{uuid.uuid4()}"))')
    return {"success": True}


def append_schematic_block(block: str) -> None:
    schematic = Path(SCH_PATH)
    content = schematic.read_text(encoding="utf-8")
    marker = " (sheet_instances "
    index = content.find(marker)
    if index == -1:
        index = content.rfind("(sheet_instances ")
    if index == -1:
        raise RuntimeError("could not find schematic insertion point")
    schematic.write_text(content[:index] + block + content[index:], encoding="utf-8")


def add_component(library: str, comp_type: str, reference: str, value: str, x: float, y: float) -> dict:
    return call_iface(
        "add_schematic_component",
        {
            "schematicPath": SCH_PATH,
            "component": {
                "library": library,
                "type": comp_type,
                "reference": reference,
                "value": value,
                "x": x,
                "y": y,
            },
        },
    )


def connect_pin(ref: str, pin: str, net: str) -> dict:
    if ref == "#FLG1":
        wire, label = connect_with_stub(net, 20.0, 74.54, 20.0, 77.08, 0)
        return {"success": wire.get("success") and label.get("success")}
    if ref == "#FLG2":
        wire, label = connect_with_stub(net, 20.0, 70.0, 20.0, 72.54, 0)
        return {"success": wire.get("success") and label.get("success")}
    if ref in {"#FLG3", "#FLG4", "#FLG5"}:
        x, y, _angle = COMPONENT_POSES[ref]
        wire, label = connect_with_stub(net, x, y, x, y + 2.54, 0)
        return {"success": wire.get("success") and label.get("success")}
    if ref in COMPONENT_POSES:
        x, y, _angle = COMPONENT_POSES[ref]
        wire = add_wire(x - 5.08, y, x - 2.54, y)
        label = add_label(net, x - 2.54, y, 0)
        return {"success": wire.get("success") and label.get("success")}
    return {"success": False, "message": f"no direct pin mapping for {ref}"}


def rotate_component(ref: str, angle: int) -> dict:
    return {"success": True}


def move_component(ref: str, x: float, y: float) -> dict:
    return call_iface(
        "move_schematic_component",
        {
            "schematicPath": SCH_PATH,
            "reference": ref,
            "position": {"x": x, "y": y},
            "preserveWires": False,
        },
    )


def connect_with_stub(net: str, pin_x: float, pin_y: float, label_x: float, label_y: float, angle: int = 0) -> tuple[dict, dict]:
    wire = add_wire(pin_x, pin_y, label_x, label_y)
    label = add_label(net, label_x, label_y, angle)
    return wire, label


def add_filter_row(ref_r: str, ref_c: str, external_net: str, ade_net: str, y: float, x_label: float = 55.0) -> int:
    row_errors = 0
    r_center_x = FILTER_R_X
    c_x = FILTER_C_X
    r_left = r_center_x - 3.81
    r_right = r_center_x + 3.81
    c_top_y = y
    c_bottom_y = y + 7.62

    row_errors += report_pair(f"{external_net} into {ref_r}", *connect_with_stub(external_net, r_left, y, x_label, y, 180))
    row_errors += report_single(f"{ref_r} to {ref_c}", add_wire(r_right, y, c_x, c_top_y))
    row_errors += report_single(f"{ade_net} node label", add_label(ade_net, FILTER_OUTPUT_LABEL_X, y, 0))
    row_errors += report_single(f"{ade_net} node wire", add_wire(c_x, y, FILTER_OUTPUT_LABEL_X, y))
    row_errors += report_pair(f"{ref_c} to GND", *connect_with_stub("GND", c_x, c_bottom_y, c_x, c_bottom_y + PASSIVE_STUB, 0))
    return row_errors


def add_voltage_divider_row(
    high_ref: str,
    low_ref: str,
    external_net: str,
    divided_net: str,
    filter_ref: str,
    cap_ref: str,
    ade_net: str,
    y: float,
) -> int:
    row_errors = 0
    high_left = DIVIDER_R_X - 3.81
    high_right = DIVIDER_R_X + 3.81
    shunt_top = y
    shunt_bottom = y + 7.62
    filter_left = FILTER_R_X - 3.81
    filter_right = FILTER_R_X + 3.81
    cap_bottom = y + 7.62

    row_errors += report_pair(f"{external_net} into {high_ref}", *connect_with_stub(external_net, high_left, y, FILTER_INPUT_LABEL_X, y, 180))
    row_errors += report_single(f"{high_ref} to {low_ref}/{filter_ref}", add_wire(high_right, y, DIVIDER_SHUNT_R_X, shunt_top))
    row_errors += report_single(f"{divided_net} to {filter_ref}", add_wire(DIVIDER_SHUNT_R_X, shunt_top, filter_left, y))
    row_errors += report_single(f"{divided_net} node label", add_label(divided_net, DIVIDER_SHUNT_R_X, shunt_top, 0))
    row_errors += report_pair(f"{low_ref} to GND", *connect_with_stub("GND", DIVIDER_SHUNT_R_X, shunt_bottom, DIVIDER_SHUNT_R_X, shunt_bottom + PASSIVE_STUB, 0))
    row_errors += report_single(f"{filter_ref} to {cap_ref}", add_wire(filter_right, y, FILTER_C_X, y))
    row_errors += report_single(f"{ade_net} node label", add_label(ade_net, FILTER_OUTPUT_LABEL_X, y, 0))
    row_errors += report_single(f"{ade_net} node wire", add_wire(FILTER_C_X, y, FILTER_OUTPUT_LABEL_X, y))
    row_errors += report_pair(f"{cap_ref} to GND", *connect_with_stub("GND", FILTER_C_X, cap_bottom, FILTER_C_X, cap_bottom + PASSIVE_STUB, 0))
    return row_errors


def add_yhdc_burden_row(ref_r: str, positive_net: str, negative_net: str, y: float) -> int:
    row_errors = 0
    r_x = BURDEN_R_X
    r_top = y - 3.81
    r_bottom = y + 3.81

    row_errors += report_pair(
        f"{ref_r} top {positive_net}",
        *connect_with_stub(positive_net, r_x, r_top, BURDEN_LABEL_X, r_top, 180),
    )
    row_errors += report_pair(
        f"{ref_r} bottom {negative_net}",
        *connect_with_stub(negative_net, r_x, r_bottom, BURDEN_LABEL_X, r_bottom, 180),
    )
    return row_errors


def report_pair(name: str, wire: dict, label: dict) -> int:
    if wire.get("success") and label.get("success"):
        print(f"  ✓ {name}")
        return 0
    problems = []
    if not wire.get("success"):
        problems.append(f"wire={wire.get('message', '?')}")
    if not label.get("success"):
        problems.append(f"label={label.get('message', '?')}")
    print(f"  ✗ {name}: {'; '.join(problems)}")
    return 1


def report_single(name: str, result: dict) -> int:
    if result.get("success"):
        print(f"  ✓ {name}")
        return 0
    print(f"  ✗ {name}: {result.get('message', '?')}")
    return 1


print("=== Step 1: Clear generated wires, labels, and no-connects ===")
schematic = Path(SCH_PATH)
content = schematic.read_text(encoding="utf-8")
has_gnd_flag = '"#FLG1"' in content
has_3v3_flag = '"#FLG2"' in content
has_ss_flag = '"#FLG3"' in content
has_mosi_flag = '"#FLG4"' in content
has_sclk_flag = '"#FLG5"' in content
wire_count = content.count("(wire ")
label_count = content.count("(label ")
junction_count = content.count("(junction ")
no_connect_count = content.count("(no_connect ")
for keyword in ("wire", "label", "junction", "no_connect"):
    content = remove_sexp_blocks(content, keyword)
schematic.write_text(content, encoding="utf-8")
print(
    f"  Cleared {wire_count} wires, {label_count} labels, {junction_count} junctions, "
    f"{no_connect_count} no-connects"
)
layout_components()
print("  Laid out AA filters, support circuits, and test pads inside the drawing area")

errors = 0

print()
print("=== Step 2: Rebuild connectivity with wire stubs ===")

print()
print("--- Ensure Ground Power Flag ---")
if has_gnd_flag:
    print("  ✓ #FLG1 already present")
else:
    errors += report_single(
        "Add #FLG1",
        add_component("power", "PWR_FLAG", "#FLG1", "PWR_FLAG", 20.0, 74.54),
    )
if has_3v3_flag:
    print("  ✓ #FLG2 already present")
else:
    errors += report_single(
        "Add #FLG2",
        add_component("power", "PWR_FLAG", "#FLG2", "PWR_FLAG", 20.0, 70.0),
    )
for flag_ref, flag_net, flag_x, flag_y, is_present in [
    ("#FLG3", "SS", 195.0, 134.0, has_ss_flag),
    ("#FLG4", "MOSI", 195.0, 139.0, has_mosi_flag),
    ("#FLG5", "SCLK", 195.0, 144.0, has_sclk_flag),
]:
    if is_present:
        print(f"  ✓ {flag_ref} already present")
    else:
        errors += report_single(
            f"Add {flag_ref} external driver flag for {flag_net}",
            add_component("power", "PWR_FLAG", flag_ref, "PWR_FLAG", flag_x, flag_y),
        )

print()
print("--- Normalize Dense Passive Orientation ---")
for ref in [
    "R1",
    "R16",
    *(f"C{index}" for index in range(1, 12)),
]:
    errors += report_single(f"{ref} rotate 0", rotate_component(ref, 0))
for ref in [
    *(f"R{index}" for index in range(2, 16)),
]:
    errors += report_single(f"{ref} rotate 90", rotate_component(ref, 90))
for ref, *_rest in YHDC_BURDEN_ROWS:
    errors += report_single(f"{ref} rotate 0", rotate_component(ref, 0))

print()
print("--- U1 Left Side ---")
for net, pin_y in [
    ("VCP", 70.79),
    ("VCN", 73.33),
    ("VBP", 75.87),
    ("VBN", 78.41),
    ("VAP", 80.95),
    ("VAN", 83.49),
    ("REF", 91.11),
    ("GND", 93.65),
    ("INN", 96.19),
    ("INP", 98.73),
    ("ICN", 101.27),
    ("ICP", 103.81),
    ("IBN", 106.35),
    ("IBP", 108.89),
    ("IAN", 111.43),
    ("IAP", 113.97),
    ("RESET", 116.51),
    ("GND", 119.05),
    ("GND", 121.59),
    ("DVDDOUT", 124.13),
    ("GND", 126.67),
    ("+3V3", 129.21),
]:
    errors += report_pair(f"U1 left {net} @ {pin_y:.2f}", *connect_with_stub(net, 117.3, pin_y, 114.76, pin_y, 180))
errors += report_single("U1 NC pin18", add_no_connect(117.3, 86.03))
errors += report_single("U1 NC pin17", add_no_connect(117.3, 88.57))

print()
print("--- U1 Right Side ---")
for net, pin_y in [
    ("GND", 79.68),
    ("SS", 82.22),
    ("MOSI", 84.76),
    ("MISO", 87.30),
    ("SCLK", 89.84),
    ("CF4_DREADY", 92.38),
    ("CF3_ZX", 94.92),
    ("CF2", 97.46),
    ("CF1", 100.00),
    ("IRQ1", 102.54),
    ("IRQ0", 105.08),
    ("CLKOUT", 107.62),
    ("CLKIN", 110.16),
    ("GND", 112.70),
    ("+3V3", 115.24),
    ("GND", 117.78),
    ("AVDDOUT", 120.32),
]:
    errors += report_pair(f"U1 right {net} @ {pin_y:.2f}", *connect_with_stub(net, 142.7, pin_y, 145.24, pin_y, 0))

print()
print("--- External Connectors ---")
errors += report_single("#FLG1 pin 1 GND", connect_pin("#FLG1", "1", "GND"))
errors += report_single("#FLG2 pin 1 +3V3", connect_pin("#FLG2", "1", "+3V3"))

header_x, header_y, _header_angle = COMPONENT_POSES["J1"]
for index, net in enumerate(DIGITAL_HEADER_NETS):
    pin_y = header_y - 19.05 + index * 2.54
    errors += report_pair(f"J1 pin {index + 1} {net}", *connect_with_stub(net, header_x - 5.08, pin_y, header_x - 7.62, pin_y, 180))

for ref, nets in CURRENT_JACK_NETS.items():
    jack_x, jack_y, _angle = COMPONENT_POSES[ref]
    for index, net in enumerate(nets):
        pin_y = jack_y - 2.54 + index * 2.54
        errors += report_pair(f"{ref} pin {index + 1} {net}", *connect_with_stub(net, jack_x - 5.08, pin_y, jack_x - 7.62, pin_y, 180))

for ref, nets in VOLTAGE_TERMINAL_NETS.items():
    terminal_x, terminal_y, _angle = COMPONENT_POSES[ref]
    for index, net in enumerate(nets):
        pin_y = terminal_y + index * 2.54
        errors += report_pair(f"{ref} pin {index + 1} {net}", *connect_with_stub(net, terminal_x - 5.08, pin_y, terminal_x - 7.62, pin_y, 180))

for flag_ref, flag_net in [("#FLG3", "SS"), ("#FLG4", "MOSI"), ("#FLG5", "SCLK")]:
    errors += report_single(f"{flag_ref} {flag_net}", connect_pin(flag_ref, "1", flag_net))

print()
print("--- YHDC CT Burden/Multiplier Resistors ---")
for row in YHDC_BURDEN_ROWS:
    errors += add_yhdc_burden_row(*row)

print()
print("--- AA Input Filters ---")
for row in FILTER_ROWS:
    if row[0] not in VOLTAGE_FILTER_REFS:
        errors += add_filter_row(*row, x_label=FILTER_INPUT_LABEL_X)

print()
print("--- 12 VAC Voltage Divider Inputs ---")
for row in VOLTAGE_DIVIDER_ROWS:
    errors += add_voltage_divider_row(*row)

print()
print("--- Decoupling and Reference Caps ---")
for ref, top_net, bottom_net in [
    ("C7", "GND", "REF"),
    ("C8", "GND", "REF"),
    ("C5", "GND", "DVDDOUT"),
    ("C6", "GND", "DVDDOUT"),
    ("C3", "GND", "AVDDOUT"),
    ("C4", "GND", "AVDDOUT"),
    ("C1", "GND", "+3V3"),
    ("C2", "GND", "+3V3"),
]:
    x, y, _angle = COMPONENT_POSES[ref]
    errors += report_pair(f"{ref} top {top_net}", *connect_with_stub(top_net, x, y - 3.81, x, y - 3.81 - PASSIVE_STUB, 0))
    errors += report_pair(f"{ref} bottom {bottom_net}", *connect_with_stub(bottom_net, x, y + 3.81, x, y + 3.81 + PASSIVE_STUB, 0))

print()
print("--- Crystal, Reset, LED ---")
y1_x, y1_y, _angle = COMPONENT_POSES["Y1"]
c9_x, c9_y, _angle = COMPONENT_POSES["C9"]
c10_x, c10_y, _angle = COMPONENT_POSES["C10"]
r1_x, r1_y, _angle = COMPONENT_POSES["R1"]
c11_x, c11_y, _angle = COMPONENT_POSES["C11"]
r16_x, r16_y, _angle = COMPONENT_POSES["R16"]
d1_x, d1_y, _angle = COMPONENT_POSES["D1"]
errors += report_pair("Y1 CLKIN", *connect_with_stub("CLKIN", y1_x - 3.81, y1_y, y1_x - 3.81 - IO_STUB, y1_y, 180))
errors += report_pair("Y1 CLKOUT", *connect_with_stub("CLKOUT", y1_x + 3.81, y1_y, y1_x + 3.81 + IO_STUB, y1_y, 0))
errors += report_pair("C9 top GND", *connect_with_stub("GND", c9_x, c9_y - 3.81, c9_x, c9_y - 3.81 - PASSIVE_STUB, 0))
errors += report_pair("C9 bottom CLKIN", *connect_with_stub("CLKIN", c9_x, c9_y + 3.81, c9_x, c9_y + 3.81 + PASSIVE_STUB, 0))
errors += report_pair("C10 top GND", *connect_with_stub("GND", c10_x, c10_y - 3.81, c10_x, c10_y - 3.81 - PASSIVE_STUB, 0))
errors += report_pair("C10 bottom CLKOUT", *connect_with_stub("CLKOUT", c10_x, c10_y + 3.81, c10_x, c10_y + 3.81 + PASSIVE_STUB, 0))
errors += report_pair("R1 top RESET", *connect_with_stub("RESET", r1_x, r1_y - 3.81, r1_x, r1_y - 3.81 - PASSIVE_STUB, 0))
errors += report_pair("R1 bottom +3V3", *connect_with_stub("+3V3", r1_x, r1_y + 3.81, r1_x, r1_y + 3.81 + PASSIVE_STUB, 0))
errors += report_pair("C11 top GND", *connect_with_stub("GND", c11_x, c11_y - 3.81, c11_x, c11_y - 3.81 - PASSIVE_STUB, 0))
errors += report_pair("C11 bottom RESET", *connect_with_stub("RESET", c11_x, c11_y + 3.81, c11_x, c11_y + 3.81 + PASSIVE_STUB, 0))
errors += report_pair("R16 top CF2_LED", *connect_with_stub("CF2_LED", r16_x, r16_y - 3.81, r16_x, r16_y - 3.81 - PASSIVE_STUB, 0))
errors += report_pair("R16 bottom CF2", *connect_with_stub("CF2", r16_x, r16_y + 3.81, r16_x, r16_y + 3.81 + PASSIVE_STUB, 0))
errors += report_pair("D1 cathode GND", *connect_with_stub("GND", d1_x - 3.81, d1_y, d1_x - 3.81 - IO_STUB, d1_y, 180))
errors += report_pair("D1 anode CF2_LED", *connect_with_stub("CF2_LED", d1_x + 3.81, d1_y, d1_x + 3.81 + IO_STUB, d1_y, 0))

print()
print("=== Summary ===")
if errors:
    print(f"✗ {errors} operation(s) failed")
else:
    print("✓ Connectivity rebuild completed with no reported failures")
