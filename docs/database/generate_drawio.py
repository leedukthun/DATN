"""Create an editable diagrams.net document from the verified schema snapshot."""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path


OUT = Path(__file__).resolve().parent
SCHEMA = json.loads((OUT / "schema_snapshot.json").read_text(encoding="utf-8"))
ORDER = ["users", "projects", "locations", "analysis_sessions", "media_files", "violations"]
POSITIONS = {
    "users": (100, 210), "projects": (1000, 210), "locations": (1900, 210),
    "violations": (100, 800), "media_files": (1000, 800), "analysis_sessions": (1900, 800),
}
TITLES = {
    "users": "Người dùng", "projects": "Dự án", "locations": "Địa điểm",
    "analysis_sessions": "Phiên phân tích", "media_files": "Tệp ảnh / video", "violations": "Vi phạm",
}
INK, MUTED, BORDER = "#172638", "#526170", "#a6b1bc"
BLUE, AMBER = "#285d89", "#936126"

document = ET.Element("mxfile", host="app.diagrams.net", type="device", compressed="false")
page = ET.SubElement(document, "diagram", id="physical-erd", name="CSDL mức vật lý")
model = ET.SubElement(page, "mxGraphModel", dx="2660", dy="1880", grid="1", gridSize="10",
                      guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                      pageScale="1", pageWidth="2660", pageHeight="1880", math="0", shadow="0",
                      background="#ffffff")
root = ET.SubElement(model, "root")
ET.SubElement(root, "mxCell", id="0")
ET.SubElement(root, "mxCell", id="1", parent="0")


def vertex(cell_id, value, x, y, width, height, style, parent="1", **extra):
    cell = ET.SubElement(root, "mxCell", id=cell_id, value=value, style=style,
                         vertex="1", parent=parent, **extra)
    ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(width), height=str(height), **{"as": "geometry"})
    return cell


def text(cell_id, value, x, y, width, height, size=23, color=INK, bold=False,
         mono=False, align="left", parent="1", extra_style=""):
    return vertex(cell_id, value, x, y, width, height,
                  "text;html=0;strokeColor=none;fillColor=none;whiteSpace=nowrap;overflow=visible;"
                  f"fontFamily={'Consolas' if mono else 'Arial'};fontSize={size};fontColor={color};"
                  f"fontStyle={1 if bold else 0};align={align};verticalAlign=middle;spacing=0;"
                  "connectable=0;" + extra_style, parent, connectable="0")


def row_id(table, column):
    return f"row_{table}_{column}"


text("title", "SƠ ĐỒ CƠ SỞ DỮ LIỆU MỨC VẬT LÝ", 100, 44, 2400, 54, 46, bold=True)
text("subtitle", "Hệ thống phát hiện không đội mũ bảo hiểm", 100, 105, 2300, 37, 28)
text("source_note", "Nguồn: backend/helmet_detection.db  •  SQLite hiện tại  •  6 bảng / 62 cột / 5 khóa ngoại",
     100, 145, 2400, 32, 23, MUTED)

for name in ORDER:
    table = SCHEMA[name]
    x, y = POSITIONS[name]
    table_id = f"table_{name}"
    table_h = 90 + len(table["columns"]) * 34 + 64
    vertex(table_id, "", x, y, 660, table_h,
           f"rounded=0;whiteSpace=wrap;html=0;fillColor=#ffffff;strokeColor={BORDER};strokeWidth=2;"
           "container=1;collapsible=0;recursiveResize=1;", table_name=name)
    vertex(f"header_{name}", "", 0, 0, 660, 52,
           f"rounded=0;fillColor={INK};strokeColor=none;", table_id, connectable="0")
    text(f"name_{name}", name, 18, 8, 440, 36, 29, "#ffffff", True, parent=table_id)
    text(f"meaning_{name}", TITLES[name], 425, 11, 217, 30, 20, "#d9e2ea", align="right", parent=table_id)
    vertex(f"column_header_{name}", "", 1, 52, 658, 38,
           "rounded=0;fillColor=#eef1f4;strokeColor=none;", table_id, connectable="0")
    for suffix, label, cx, cw in [("key", "Khóa", 12, 72), ("column", "Tên cột", 94, 302),
                                  ("type", "Kiểu dữ liệu", 404, 177), ("null", "NULL", 588, 64)]:
        text(f"column_header_{name}_{suffix}", label, cx, 55, cw, 32, 21, MUTED, True, parent=table_id)
    uniques = [idx for idx in table["indexes"] if idx["unique"]]
    foreign_columns = {fk["from"] for fk in table["foreign_keys"]}
    for index, column in enumerate(table["columns"]):
        cname = column["name"]
        rid = row_id(name, cname)
        primary = bool(column["pk"])
        foreign = cname in foreign_columns
        unique = any(idx["columns"] == [cname] for idx in uniques)
        flag = "PK" if primary else "FK" if foreign else "UQ" if unique else "REF*" if name == "projects" and cname == "owner_id" else ""
        fill = "#eaf2f8" if primary else "#f4f8fc" if foreign else "#fff7ea" if flag == "REF*" else "#ffffff" if index % 2 == 0 else "#fafbfc"
        vertex(rid, "", 1, 90 + 34*index, 658, 34,
               f"rounded=0;fillColor={fill};strokeColor=#e1e6eb;strokeWidth=0.5;"
               "container=1;collapsible=0;recursiveResize=1;", table_id,
               column_name=cname, data_type=column["type"], nullable=str(not bool(column["notnull"])).lower(),
               key_kind=flag)
        text(rid+"_key", flag, 11, 1, 72, 32, 20, AMBER if flag == "REF*" else BLUE, True, parent=rid)
        text(rid+"_name", cname, 93, 1, 305, 32, 22, bold=primary, mono=True, parent=rid)
        text(rid+"_type", column["type"], 403, 1, 178, 32, 22, mono=True, parent=rid)
        text(rid+"_null", "—" if column["notnull"] else "Có", 584, 1, 62, 32, 21, MUTED, align="center", parent=rid)
    foot = 90 + 34*len(table["columns"])
    if uniques:
        first_line = " • ".join("UNIQUE (" + ", ".join(idx["columns"]) + ")" for idx in uniques)
    elif name == "analysis_sessions":
        first_line = "FK: location_id → locations.id"
    elif name == "media_files":
        first_line = "FK: session_id → analysis_sessions.id"
    else:
        first_line = "FK: session_id, media_id"
    second_line = "* owner_id: tham chiếu theo ORM, chưa có FK" if name == "projects" else "ON DELETE CASCADE" if table["foreign_keys"] else "PK: id"
    text(f"constraints_{name}", first_line, 14, foot+4, 634, 28, 20, BLUE, mono=True, parent=table_id)
    text(f"note_{name}", second_line, 14, foot+30, 634, 27, 20, AMBER if name == "projects" else MUTED, parent=table_id)


def edge_label(edge_id, suffix, value, at_start, side, color):
    label = ET.SubElement(root, "mxCell", id=f"{edge_id}_{suffix}", value=value,
                          style=f"edgeLabel;html=0;align=center;verticalAlign=middle;resizable=0;"
                                f"fontFamily=Arial;fontSize=22;fontColor={color};fontStyle=1;"
                                "labelBackgroundColor=#ffffff;", vertex="1", connectable="0", parent=edge_id)
    geometry = ET.SubElement(label, "mxGeometry", x="-1" if at_start else "1", y="0", relative="1", **{"as": "geometry"})
    offset = 27 if value == "1" else 46
    ET.SubElement(geometry, "mxPoint", x=str(offset if side == "right" else -offset), y="-19", **{"as": "offset"})


def relationship(edge_id, source_table, source_col, source_side, target_table, target_col,
                 target_side, waypoints, reference=False, label=""):
    color = AMBER if reference else BLUE
    edge = ET.SubElement(root, "mxCell", id=edge_id, value=label,
                         style="edgeStyle=segmentEdgeStyle;rounded=0;html=0;endArrow=none;startArrow=none;"
                               f"strokeColor={color};strokeWidth=3;fontFamily=Arial;fontSize=21;fontColor={color};"
                               f"dashed={1 if reference else 0};dashPattern=10 7;labelBackgroundColor=#ffffff;"
                               f"exitX={1 if source_side == 'right' else 0};exitY=0.5;exitDx=0;exitDy=0;exitPerimeter=0;"
                               f"entryX={1 if target_side == 'right' else 0};entryY=0.5;entryDx=0;entryDy=0;entryPerimeter=0;",
                         parent="1", edge="1", source=row_id(source_table, source_col),
                         target=row_id(target_table, target_col), relation_kind="ORM_REFERENCE" if reference else "FOREIGN_KEY")
    geometry = ET.SubElement(edge, "mxGeometry", relative="1", **{"as": "geometry"})
    points = ET.SubElement(geometry, "Array", **{"as": "points"})
    for px, py in waypoints:
        ET.SubElement(points, "mxPoint", x=str(px), y=str(py))
    edge_label(edge_id, "one", "0..1" if reference else "1", True, source_side, color)
    edge_label(edge_id, "many", "0..N", False, target_side, color)


relationship("orm_users_projects", "users", "id", "right", "projects", "owner_id", "left",
             [(870, 317), (870, 487)], reference=True, label="ORM*")
relationship("fk_projects_locations", "projects", "id", "right", "locations", "project_id", "left",
             [(1770, 317), (1770, 351)])
relationship("fk_locations_sessions", "locations", "id", "right", "analysis_sessions", "location_id", "right",
             [(2615, 317), (2615, 941)])
relationship("fk_sessions_media", "analysis_sessions", "id", "left", "media_files", "session_id", "right",
             [(1780, 907), (1780, 941)])
relationship("fk_sessions_violations", "analysis_sessions", "id", "left", "violations", "session_id", "left",
             [(1840, 907), (1840, 715), (30, 715), (30, 941)], label="analysis_sessions.id → violations.session_id")
relationship("fk_media_violations", "media_files", "id", "left", "violations", "media_id", "right",
             [(880, 907), (880, 975)])

vertex("legend_separator", "", 100, 1645, 2460, 1, f"fillColor={BORDER};strokeColor=none;")
text("legend_heading", "CHÚ GIẢI", 100, 1665, 2300, 35, 25, bold=True)
text("legend_keys", "PK: khóa chính  •  FK: khóa ngoại  •  UQ: duy nhất  •  NULL: Có = cho phép NULL; — = NOT NULL  •  0..N: không có hoặc nhiều bản ghi",
     100, 1705, 2460, 36, 24)
text("legend_fk", "Đường liền: khóa ngoại thực tế — ON DELETE CASCADE; ON UPDATE NO ACTION.",
     100, 1752, 2460, 33, 23, BLUE)
text("legend_orm", "Đường nét đứt / REF* / ORM*: liên kết chỉ có trong model; SQLite chưa ràng buộc projects.owner_id → users.id.",
     100, 1794, 2460, 33, 23, AMBER)

cells = root.findall("mxCell")
ids = [cell.get("id") for cell in cells]
assert len(ids) == len(set(ids)), "Duplicate cell IDs"
for cell in cells:
    for attr in ("parent", "source", "target"):
        if cell.get(attr):
            assert cell.get(attr) in ids, (cell.get("id"), attr)
assert len([cell for cell in cells if cell.get("column_name")]) == 62
assert len([cell for cell in cells if cell.get("table_name")]) == 6
assert len([cell for cell in cells if cell.get("relation_kind") == "FOREIGN_KEY"]) == 5
ET.indent(document, space="  ")
destination = OUT / "physical_erd.drawio"
ET.ElementTree(document).write(destination, encoding="utf-8", xml_declaration=True)
ET.parse(destination)
print(json.dumps({"file": str(destination), "cells": len(cells), "editable_columns": 62,
                  "foreign_keys": 5, "orm_references": 1, "bytes": destination.stat().st_size}, ensure_ascii=False))
