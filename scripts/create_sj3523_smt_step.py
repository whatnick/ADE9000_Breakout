from pathlib import Path
import re
import tempfile
import zipfile

import FreeCAD
import Import
import Part

OUT = Path(__file__).resolve().parents[1] / "models" / "step" / "Jack_3.5mm_CUI_SJ-3523-SMT_Horizontal.step"
SOURCE_ZIP = Path(__file__).resolve().parents[1] / "models" / "step" / "SJ_3523_SMT_TR.zip"
SOURCE_STEP = "SJ-3523-SMT-TR.STEP"
OUT.parent.mkdir(parents=True, exist_ok=True)


def add_step_presentation(path, face_colors):
    text = path.read_text(encoding="utf-8")
    face_ids = re.findall(r"#(\d+)\s*=\s*ADVANCED_FACE", text)
    entity_ids = [int(match) for match in re.findall(r"#(\d+)\s*=", text)]
    context_match = re.search(r"#(\d+)\s*=\s*\(\s*GEOMETRIC_REPRESENTATION_CONTEXT\(3\)", text)
    if not face_ids or not entity_ids or not context_match:
        raise RuntimeError("Could not locate STEP faces/context for color styling")

    next_id = max(entity_ids) + 1
    styled_ids = []
    lines = []
    style_ids = {}
    for face_id, color in zip(face_ids, face_colors):
        red, green, blue = color
        key = (red, green, blue)
        if key not in style_ids:
            style_id = next_id
            usage_id = next_id + 1
            side_id = next_id + 2
            fill_id = next_id + 3
            area_id = next_id + 4
            area_colour_id = next_id + 5
            colour_id = next_id + 6
            next_id += 7
            style_ids[key] = style_id
            lines.extend([
                f"#{style_id}=PRESENTATION_STYLE_ASSIGNMENT((#{usage_id}));",
                f"#{usage_id}=SURFACE_STYLE_USAGE(.BOTH.,#{side_id});",
                f"#{side_id}=SURFACE_SIDE_STYLE('',(#{fill_id}));",
                f"#{fill_id}=SURFACE_STYLE_FILL_AREA(#{area_id});",
                f"#{area_id}=FILL_AREA_STYLE('',(#{area_colour_id}));",
                f"#{area_colour_id}=FILL_AREA_STYLE_COLOUR('',#{colour_id});",
                f"#{colour_id}=COLOUR_RGB('',{red},{green},{blue});",
            ])

        styled_id = next_id
        next_id += 1
        styled_ids.append(styled_id)
        lines.append(f"#{styled_id}=STYLED_ITEM('color',(#{style_ids[key]}),#{face_id});")

    context_id = context_match.group(1)
    presentation_id = next_id
    styled_list = ",".join(f"#{styled_id}" for styled_id in styled_ids)
    lines.append(
        f"#{presentation_id}=MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({styled_list}),#{context_id});"
    )

    marker = "ENDSEC;\nEND-ISO-10303-21;"
    if marker not in text:
        raise RuntimeError("Could not locate STEP DATA section terminator")
    text = text.replace(marker, "\n".join(lines) + "\n" + marker, 1)
    path.write_text(text, encoding="utf-8")


def color_for_face(face):
    bb = face.BoundBox
    y_center = (bb.YMin + bb.YMax) / 2.0

    if y_center > 6.0 and bb.ZMin > 0.2:
        return (0.66, 0.66, 0.62)
    return (0.005, 0.005, 0.005)


if not SOURCE_ZIP.exists():
    raise FileNotFoundError(f"Missing manufacturer CAD ZIP: {SOURCE_ZIP}")

with tempfile.TemporaryDirectory() as tmpdir:
    with zipfile.ZipFile(SOURCE_ZIP) as archive:
        archive.extract(SOURCE_STEP, tmpdir)
    source_path = Path(tmpdir) / SOURCE_STEP

    doc = FreeCAD.newDocument("SJ3523SMT")
    Import.insert(str(source_path), doc.Name)
    doc.recompute()

    source = doc.Objects[0]
    # Native Same Sky CAD: X is across the jack, Y is vertical, Z is along insertion.
    # KiCad footprint frame: X across, Y along body, Z above PCB. This transform keeps
    # the front barrel on the footprint's +Y edge, which faces the ADE9000 board edge
    # when the jack footprints are placed at 90 degrees.
    transform = FreeCAD.Matrix(
        -1, 0, 0, 0,
        0, 0, 1, 6,
        0, 1, 0, 2.6,
        0, 0, 0, 1,
    )
    shape = source.Shape.transformGeometry(transform)
    doc.removeObject(source.Name)
    obj = doc.addObject("Part::Feature", "SJ-3523-SMT-TR_manufacturer_cad")
    obj.Shape = shape
    doc.recompute()

    face_colors = [color_for_face(face) for face in obj.Shape.Faces]
    Part.export([obj], str(OUT))

add_step_presentation(OUT, face_colors)
print(OUT)
