from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = ROOT / "ADE9000_Breakout.kicad_sch"


BOM_FIELDS = {
    "U1": {
        "Manufacturer": "Analog Devices",
        "MPN": "ADE9000ACPZ",
        "Description": "ADE9000 polyphase energy and power quality monitoring IC, CP-40-7 LFCSP",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=ADE9000ACPZ",
        "Mouser": "https://www.mouser.com/c/?q=ADE9000ACPZ",
    },
    "Y1": {
        "Manufacturer": "ECS Inc.",
        "MPN": "ECS-245.7-12-33Q-JES-TR",
        "Description": "24.576 MHz 3.2 x 2.5 mm SMD crystal",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=ECS-245.7-12-33Q-JES-TR",
        "Mouser": "https://www.mouser.com/c/?q=ECS-245.7-12-33Q-JES-TR",
    },
    "D1": {
        "Manufacturer": "Lite-On",
        "MPN": "LTST-C191KGKT",
        "Description": "Green 0603 SMD LED",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=LTST-C191KGKT",
        "Mouser": "https://www.mouser.com/c/?q=LTST-C191KGKT",
    },
    "J1": {
        "Manufacturer": "Sullins Connector Solutions",
        "MPN": "PREC016SAAN-RC",
        "Description": "1x16 2.54 mm vertical breakaway male header for SparkFun locking footprint",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=PREC016SAAN-RC",
        "Mouser": "https://www.mouser.com/c/?q=PREC016SAAN-RC",
    },
    "J2": {
        "Manufacturer": "Phoenix Contact",
        "MPN": "1984617",
        "Description": "2-position 3.5 mm horizontal screw terminal block",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=1984617",
        "Mouser": "https://www.mouser.com/c/?q=1984617",
    },
    "J3": {
        "Manufacturer": "Phoenix Contact",
        "MPN": "1984617",
        "Description": "2-position 3.5 mm horizontal screw terminal block",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=1984617",
        "Mouser": "https://www.mouser.com/c/?q=1984617",
    },
    "J4": {
        "Manufacturer": "Phoenix Contact",
        "MPN": "1984617",
        "Description": "2-position 3.5 mm horizontal screw terminal block",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=1984617",
        "Mouser": "https://www.mouser.com/c/?q=1984617",
    },
}


for ref in ("CTA1", "CTB1", "CTC1", "CTN1"):
    BOM_FIELDS[ref] = {
        "Manufacturer": "Same Sky",
        "MPN": "SJ-3523-SMT-TR",
        "Description": "3.5 mm stereo SMT audio jack for current-transformer inputs",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=SJ-3523-SMT-TR",
        "Mouser": "https://www.mouser.com/c/?q=SJ-3523-SMT-TR",
    }

for ref in ("C2", "C4", "C6", "C8"):
    BOM_FIELDS[ref] = {
        "Manufacturer": "Murata",
        "MPN": "GRM155R71A104KA01D",
        "Description": "100 nF 10 V X7R 0402 ceramic capacitor",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=GRM155R71A104KA01D",
        "Mouser": "https://www.mouser.com/c/?q=GRM155R71A104KA01D",
    }

for ref in ("C9", "C10"):
    BOM_FIELDS[ref] = {
        "Manufacturer": "Murata",
        "MPN": "GRM1555C1H160JA01D",
        "Description": "16 pF 50 V C0G/NP0 0402 ceramic capacitor",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=GRM1555C1H160JA01D",
        "Mouser": "https://www.mouser.com/c/?q=GRM1555C1H160JA01D",
    }

BOM_FIELDS["C11"] = {
    "Manufacturer": "Murata",
    "MPN": "GRM155R61A105KE15D",
    "Description": "1 uF 10 V X5R 0402 ceramic capacitor",
    "DigiKey": "https://www.digikey.com/en/products/result?keywords=GRM155R61A105KE15D",
    "Mouser": "https://www.mouser.com/c/?q=GRM155R61A105KE15D",
}

for index in range(12, 26):
    BOM_FIELDS[f"C{index}"] = {
        "Manufacturer": "Murata",
        "MPN": "GRM155R71H223KA12D",
        "Description": "22 nF 50 V X7R 0402 ceramic capacitor",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=GRM155R71H223KA12D",
        "Mouser": "https://www.mouser.com/c/?q=GRM155R71H223KA12D",
    }

BOM_FIELDS["C1"] = {
    "Manufacturer": "Samsung Electro-Mechanics",
    "MPN": "CL21A106KPFNNNE",
    "Description": "10 uF 10 V X5R 0805 ceramic capacitor",
    "DigiKey": "https://www.digikey.com/en/products/result?keywords=CL21A106KPFNNNE",
    "Mouser": "https://www.mouser.com/c/?q=CL21A106KPFNNNE",
}

for ref in ("C3", "C5", "C7"):
    BOM_FIELDS[ref] = {
        "Manufacturer": "Samsung Electro-Mechanics",
        "MPN": "CL21A475KPFNNNE",
        "Description": "4.7 uF 10 V X5R 0805 ceramic capacitor",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=CL21A475KPFNNNE",
        "Mouser": "https://www.mouser.com/c/?q=CL21A475KPFNNNE",
    }

BOM_FIELDS["R1"] = {
    "Manufacturer": "YAGEO",
    "MPN": "RC0402FR-0710KL",
    "Description": "10 kOhm 1% 0402 thick-film resistor",
    "DigiKey": "https://www.digikey.com/en/products/result?keywords=RC0402FR-0710KL",
    "Mouser": "https://www.mouser.com/c/?q=RC0402FR-0710KL",
}

for index in range(2, 17):
    BOM_FIELDS[f"R{index}"] = {
        "Manufacturer": "YAGEO",
        "MPN": "RC0402FR-071KL",
        "Description": "1 kOhm 1% 0402 thick-film resistor",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=RC0402FR-071KL",
        "Mouser": "https://www.mouser.com/c/?q=RC0402FR-071KL",
    }

for index in range(17, 21):
    BOM_FIELDS[f"R{index}"] = {
        "Manufacturer": "YAGEO",
        "MPN": "RC0402FR-072R4L",
        "Description": "2.4 Ohm 1% 0402 thick-film burden resistor",
        "DigiKey": "https://www.digikey.com/en/products/result?keywords=RC0402FR-072R4L",
        "Mouser": "https://www.mouser.com/c/?q=RC0402FR-072R4L",
    }


def escape(value: str) -> str:
    return value.replace('\\', '\\\\').replace('"', '\\"')


def iter_symbol_blocks(text: str):
    position = 0
    while True:
        start = text.find("(symbol ", position)
        if start < 0:
            break
        depth = 0
        for end in range(start, len(text)):
            if text[end] == "(":
                depth += 1
            elif text[end] == ")":
                depth -= 1
                if depth == 0:
                    yield start, end + 1, text[start : end + 1]
                    position = end + 1
                    break


def property_value(block: str, name: str) -> str | None:
    match = re.search(r'\(property "' + re.escape(name) + r'" "((?:[^"\\]|\\.)*)"', block)
    return match.group(1) if match else None


def property_span(block: str, name: str) -> tuple[int, int, str] | None:
    start = block.find(f'(property "{name}" ')
    if start < 0:
        return None

    depth = 0
    for end in range(start, len(block)):
        if block[end] == "(":
            depth += 1
        elif block[end] == ")":
            depth -= 1
            if depth == 0:
                return start, end + 1, block[start : end + 1]

    raise ValueError(f"Unterminated property {name}")


def property_rest(property_text: str) -> str:
    match = re.match(r'\(property "(?:[^"\\]|\\.)*" "(?:[^"\\]|\\.)*"(?P<rest>.*)\)$', property_text)
    if not match:
        raise ValueError(f"Unable to parse property text: {property_text}")
    return match.group("rest")


def upsert_property(block: str, name: str, value: str, template_rest: str) -> str:
    replacement = f'(property "{escape(name)}" "{escape(value)}"{template_rest})'
    span = property_span(block, name)
    if span:
        start, end, _property_text = span
        return block[:start] + replacement + block[end:]
    return block.replace("(instances ", replacement + " (instances ", 1)


def main() -> None:
    text = SCHEMATIC.read_text()
    updated_parts: list[str] = []
    cursor = 0

    for start, end, block in iter_symbol_blocks(text):
        ref = property_value(block, "Reference")
        if not ref or ref not in BOM_FIELDS:
            continue

        footprint_property = property_span(block, "Footprint")
        template_rest = property_rest(footprint_property[2]) if footprint_property else ' (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes))'

        new_block = block
        for field, value in BOM_FIELDS[ref].items():
            new_block = upsert_property(new_block, field, value, template_rest)

        updated_parts.append(text[cursor:start])
        updated_parts.append(new_block)
        cursor = end

    if not updated_parts:
        raise SystemExit("No matching schematic symbols were updated")

    updated_parts.append(text[cursor:])
    SCHEMATIC.write_text("".join(updated_parts))
    print(f"Updated BOM fields for {len(BOM_FIELDS)} schematic symbols")


if __name__ == "__main__":
    main()