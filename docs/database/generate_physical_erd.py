"""Export the current SQLite schema as a report-ready SVG and PNG (read-only DB)."""
from __future__ import annotations

import html
import json
import math
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
DATABASE = ROOT / "backend" / "helmet_detection.db"
ORDER = ["users", "projects", "locations", "analysis_sessions", "media_files", "violations"]
POSITIONS = {
    "users": (100, 210), "projects": (1000, 210), "locations": (1900, 210),
    "violations": (100, 800), "media_files": (1000, 800), "analysis_sessions": (1900, 800),
}
TITLES = {
    "users": "Người dùng", "projects": "Dự án", "locations": "Địa điểm",
    "analysis_sessions": "Phiên phân tích", "media_files": "Tệp ảnh / video", "violations": "Vi phạm",
}
W, H, SCALE = 2660, 1880, 2
BOX_W, HEADER, COL_HEADER, ROW, FOOTER = 660, 52, 38, 34, 64
INK, MUTED, BORDER = "#172638", "#526170", "#a6b1bc"
BLUE, AMBER = "#285d89", "#936126"
FONT_DIR = Path("C:/Windows/Fonts")


def quote(identifier):
    return '"' + identifier.replace('"', '""') + '"'


with sqlite3.connect(DATABASE.as_uri() + "?mode=ro", uri=True) as connection:
    connection.row_factory = sqlite3.Row
    actual_tables = {r[0] for r in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )}
    assert actual_tables == set(ORDER), actual_tables
    schema = {}
    for name in ORDER:
        indexes = [dict(r) for r in connection.execute(f"PRAGMA index_list({quote(name)})")]
        for index in indexes:
            index["columns"] = [r["name"] for r in connection.execute(
                f"PRAGMA index_info({quote(index['name'])})"
            )]
        schema[name] = {
            "columns": [dict(r) for r in connection.execute(f"PRAGMA table_info({quote(name)})")],
            "foreign_keys": [dict(r) for r in connection.execute(f"PRAGMA foreign_key_list({quote(name)})")],
            "indexes": indexes,
        }

expected_fks = {
    ("locations", "project_id", "projects", "id"),
    ("analysis_sessions", "location_id", "locations", "id"),
    ("media_files", "session_id", "analysis_sessions", "id"),
    ("violations", "session_id", "analysis_sessions", "id"),
    ("violations", "media_id", "media_files", "id"),
}
actual_fks = {(t, fk["from"], fk["table"], fk["to"])
              for t, table in schema.items() for fk in table["foreign_keys"]}
assert actual_fks == expected_fks, "Schema changed: review diagram routes."
assert sum(len(t["columns"]) for t in schema.values()) == 62

canvas = Image.new("RGB", (W * SCALE, H * SCALE), "white")
draw = ImageDraw.Draw(canvas)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<title>Sơ đồ cơ sở dữ liệu mức vật lý — SQLite hiện tại</title>',
       '<desc>6 bảng, 62 cột, 6 khóa chính, 5 khóa ngoại. Liên kết users tới projects chỉ có trong ORM, được vẽ nét đứt.</desc>',
       '<rect width="100%" height="100%" fill="white"/>']
font_cache = {}


def text(x, baseline, value, size=23, color=INK, bold=False, mono=False, anchor="start"):
    filename = "consolab.ttf" if mono and bold else "consola.ttf" if mono else "arialbd.ttf" if bold else "arial.ttf"
    key = (filename, size)
    if key not in font_cache:
        font_cache[key] = ImageFont.truetype(str(FONT_DIR / filename), size * SCALE)
    family = "Consolas, monospace" if mono else "Arial, sans-serif"
    svg.append(f'<text x="{x}" y="{baseline}" fill="{color}" font-family="{family}" font-size="{size}" '
               f'font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}">{html.escape(str(value))}</text>')
    draw.text((x * SCALE, baseline * SCALE), str(value), font=font_cache[key], fill=color,
              anchor={"start": "ls", "middle": "ms", "end": "rs"}[anchor])


def rect(x, y, width, height, fill="white", stroke=None, stroke_width=1):
    svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" '
               f'stroke="{stroke or "none"}" stroke-width="{stroke_width}"/>')
    draw.rectangle((x*SCALE, y*SCALE, (x+width)*SCALE, (y+height)*SCALE),
                   fill=fill, outline=stroke, width=stroke_width*SCALE)


def line(points, color=BORDER, width=2, dashed=False):
    coordinates = " ".join(f"{x},{y}" for x, y in points)
    svg.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="{width}" '
               f'stroke-linejoin="round"' + (' stroke-dasharray="10 7"' if dashed else '') + '/>')
    if not dashed:
        draw.line([(x*SCALE, y*SCALE) for x, y in points], fill=color, width=width*SCALE, joint="curve")
        return
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        distance = math.hypot(x2-x1, y2-y1)
        for start in range(0, math.ceil(distance), 17):
            end = min(start+10, distance)
            draw.line(((x1+(x2-x1)*start/distance)*SCALE, (y1+(y2-y1)*start/distance)*SCALE,
                       (x1+(x2-x1)*end/distance)*SCALE, (y1+(y2-y1)*end/distance)*SCALE),
                      fill=color, width=width*SCALE)


def point(x, y, color):
    svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
    draw.ellipse(((x-4)*SCALE, (y-4)*SCALE, (x+4)*SCALE, (y+4)*SCALE), fill=color)


def port(table, column, side):
    x, y = POSITIONS[table]
    i = next(i for i, col in enumerate(schema[table]["columns"]) if col["name"] == column)
    return (x if side == "left" else x + BOX_W, y + HEADER + COL_HEADER + i*ROW + ROW/2)


text(100, 87, "SƠ ĐỒ CƠ SỞ DỮ LIỆU MỨC VẬT LÝ", 46, bold=True)
text(100, 132, "Hệ thống phát hiện không đội mũ bảo hiểm", 28)
text(100, 169, "Nguồn: backend/helmet_detection.db  •  SQLite hiện tại  •  6 bảng / 62 cột / 5 khóa ngoại", 23, MUTED)

# Edges connect the exact referenced PK and FK rows; numbers express cardinality.
u = port("users", "id", "right")
p_owner = port("projects", "owner_id", "left")
line([u, (870, u[1]), (870, p_owner[1]), p_owner], AMBER, 3, True)
text(783, u[1]-12, "0..1", 22, AMBER, bold=True)
text(920, p_owner[1]-12, "0..N", 22, AMBER, bold=True)
rect(832, 398, 76, 28)
text(870, 418, "ORM*", 21, AMBER, anchor="middle")

p = port("projects", "id", "right")
l_fk = port("locations", "project_id", "left")
line([p, (1770, p[1]), (1770, l_fk[1]), l_fk], BLUE, 3)
text(1678, p[1]-12, "1", 22, BLUE, bold=True)
text(1820, l_fk[1]-12, "0..N", 22, BLUE, bold=True)

l = port("locations", "id", "right")
a_fk = port("analysis_sessions", "location_id", "right")
line([l, (2615, l[1]), (2615, a_fk[1]), a_fk], BLUE, 3)
text(2574, l[1]-12, "1", 22, BLUE, bold=True)
text(2570, a_fk[1]-12, "0..N", 20, BLUE, bold=True)

a = port("analysis_sessions", "id", "left")
m_fk = port("media_files", "session_id", "right")
line([a, (1780, a[1]), (1780, m_fk[1]), m_fk], BLUE, 3)
text(1871, a[1]-12, "1", 22, BLUE, bold=True)
text(1676, m_fk[1]-12, "0..N", 22, BLUE, bold=True)

v_session = port("violations", "session_id", "left")
line([a, (1840, a[1]), (1840, 715), (30, 715), (30, v_session[1]), v_session], BLUE, 3)
text(980, 698, "analysis_sessions.id → violations.session_id", 22, BLUE, mono=True, anchor="middle")
text(38, v_session[1]-12, "0..N", 20, BLUE, bold=True)

m = port("media_files", "id", "left")
v_media = port("violations", "media_id", "right")
line([m, (880, m[1]), (880, v_media[1]), v_media], BLUE, 3)
text(969, m[1]-12, "1", 22, BLUE, bold=True)
text(778, v_media[1]-12, "0..N", 22, BLUE, bold=True)

for name in ORDER:
    table = schema[name]
    x, y = POSITIONS[name]
    height = HEADER + COL_HEADER + ROW*len(table["columns"]) + FOOTER
    rect(x, y, BOX_W, height, "white", BORDER, 2)
    rect(x, y, BOX_W, HEADER, INK)
    text(x+18, y+35, name, 29, "white", bold=True)
    text(x+BOX_W-16, y+34, TITLES[name], 20, "#d9e2ea", anchor="end")
    rect(x+1, y+HEADER, BOX_W-2, COL_HEADER, "#eef1f4")
    columns = [(x+12, "Khóa"), (x+94, "Tên cột"), (x+404, "Kiểu dữ liệu"), (x+588, "NULL")]
    for tx, label in columns:
        text(tx, y+HEADER+26, label, 21, MUTED, bold=True)
    uniques = [index for index in table["indexes"] if index["unique"]]
    fk_columns = {fk["from"] for fk in table["foreign_keys"]}
    for i, column in enumerate(table["columns"]):
        cy = y + HEADER + COL_HEADER + i*ROW
        cname = column["name"]
        is_pk = bool(column["pk"])
        is_fk = cname in fk_columns
        single_unique = any(idx["columns"] == [cname] for idx in uniques)
        flags = "PK" if is_pk else "FK" if is_fk else "UQ" if single_unique else "REF*" if name == "projects" and cname == "owner_id" else ""
        fill = "#eaf2f8" if is_pk else "#f4f8fc" if is_fk else "#fff7ea" if flags == "REF*" else "white" if i%2 == 0 else "#fafbfc"
        rect(x+1, cy, BOX_W-2, ROW, fill)
        line([(x+1, cy+ROW), (x+BOX_W-1, cy+ROW)], "#e1e6eb", 1)
        text(x+12, cy+24, flags, 20, AMBER if flags == "REF*" else BLUE, bold=True)
        text(x+94, cy+24, cname, 22, bold=is_pk, mono=True)
        text(x+404, cy+24, column["type"], 22, mono=True)
        text(x+612, cy+24, "—" if column["notnull"] else "Có", 21, MUTED, anchor="middle")
    footer_y = y+HEADER+COL_HEADER+len(table["columns"])*ROW
    line([(x, footer_y), (x+BOX_W, footer_y)], BORDER, 1)
    if uniques:
        constraints = " • ".join("UNIQUE ("+", ".join(idx["columns"])+")" for idx in uniques)
        text(x+14, footer_y+25, constraints, 20, BLUE, mono=True)
    elif name == "analysis_sessions":
        text(x+14, footer_y+25, "FK: location_id → locations.id", 20, BLUE, mono=True)
    elif name == "media_files":
        text(x+14, footer_y+25, "FK: session_id → analysis_sessions.id", 20, BLUE, mono=True)
    elif name == "violations":
        text(x+14, footer_y+25, "FK: session_id, media_id", 20, BLUE, mono=True)
    text(x+14, footer_y+49,
         "* owner_id: tham chiếu theo ORM, chưa có FK" if name == "projects" else
         "ON DELETE CASCADE" if table["foreign_keys"] else "PK: id",
         20, AMBER if name == "projects" else MUTED)

for t1, c1, side1, t2, c2, side2 in [
    ("users", "id", "right", "projects", "owner_id", "left"),
    ("projects", "id", "right", "locations", "project_id", "left"),
    ("locations", "id", "right", "analysis_sessions", "location_id", "right"),
    ("analysis_sessions", "id", "left", "media_files", "session_id", "right"),
    ("analysis_sessions", "id", "left", "violations", "session_id", "left"),
    ("media_files", "id", "left", "violations", "media_id", "right"),
]:
    color = AMBER if t1 == "users" else BLUE
    point(*port(t1,c1,side1),color)
    point(*port(t2,c2,side2),color)

line([(100, 1645), (2560, 1645)], BORDER, 2)
text(100, 1691, "CHÚ GIẢI", 25, bold=True)
text(100, 1730, "PK: khóa chính  •  FK: khóa ngoại  •  UQ: duy nhất  •  NULL: Có = cho phép NULL; — = NOT NULL  •  0..N: không có hoặc nhiều bản ghi", 24)
line([(100, 1768), (174, 1768)], BLUE, 3)
text(193, 1776, "Khóa ngoại thực tế: ON DELETE CASCADE; ON UPDATE NO ACTION.", 23)
line([(100, 1810), (174, 1810)], AMBER, 3, True)
text(193, 1818, "REF* / ORM*: liên kết chỉ có trong model. SQLite chưa ràng buộc projects.owner_id → users.id.", 23, AMBER)

svg.append("</svg>")
(OUT / "physical_erd.svg").write_text("\n".join(svg), encoding="utf-8")
canvas.save(OUT / "physical_erd.png", dpi=(300, 300))
(OUT / "schema_snapshot.json").write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

readme = [
    "# Sơ đồ cơ sở dữ liệu mức vật lý", "",
    "Nguồn: `backend/helmet_detection.db`, đọc qua kết nối SQLite `mode=ro`.", "",
    "- `physical_erd.png`: ảnh 5320 × 3760 px, gắn metadata 300 DPI, dùng để chèn vào báo cáo.",
    "- `physical_erd.svg`: bản vector, có thể phóng to mà không vỡ hình.",
    "- `physical_erd.drawio`: bản chỉnh sửa trong diagrams.net; các bảng, từng ô dữ liệu và đường nối đều là đối tượng gốc. Mở bằng File → Open from → Device. Bấm đúp ô để sửa nội dung; đường nối được gắn vào hàng PK/FK và đi theo khi di chuyển bảng.",
    "- `generate_drawio.py`: tạo lại tệp `.drawio` từ `schema_snapshot.json` bằng thư viện chuẩn Python.",
    "- `schema_snapshot.json`: cấu trúc bảng, cột, khóa ngoại và chỉ mục đã đối chiếu.",
    "- `generate_physical_erd.py`: mã tạo lại sơ đồ từ CSDL hiện tại (cần Python + Pillow và font Arial/Consolas trên Windows).", "",
    "Sơ đồ giữ nguyên tên bảng và thứ tự cột trong SQLite: 6 bảng, 62 cột, 6 PK, 5 FK, 14 cột nullable.", "",
    "## Khác biệt giữa SQLite hiện tại và model SQLAlchemy", "",
    "1. `projects.owner_id` cho phép NULL nhưng chưa có FK hoặc chỉ mục. Đường nét đứt chỉ mô tả tham chiếu theo model, không phải FK vật lý.",
    "2. SQLite hiện có UNIQUE trên `projects.name` toàn bảng. Model lại khai báo UNIQUE trên `(owner_id, name)`.",
    "3. Cả 5 FK thực tế đều ON DELETE CASCADE, ON UPDATE NO ACTION. Ứng dụng bật `PRAGMA foreign_keys=ON` khi kết nối.",
    "4. Không cột nào có DEFAULT ở tầng CSDL; các default trong model được SQLAlchemy cung cấp.",
    "5. Kiểu dữ liệu trên sơ đồ là kiểu khai báo thực tế trong SQLite. TEXT được dùng cho các trường JSON.", "",
    "## Chỉ mục thực tế", "",
    "| Bảng | Chỉ mục | Cột | Duy nhất |", "|---|---|---|---|",
]
for name in ORDER:
    for index in schema[name]["indexes"]:
        readme.append(f'| `{name}` | `{index["name"]}` | `{", ".join(index["columns"])}` | {"Có" if index["unique"] else "Không"} |')
readme.extend(["", "## Chú thích đề xuất dưới hình trong báo cáo", "",
               "Hình: Sơ đồ cơ sở dữ liệu mức vật lý của hệ thống phát hiện không đội mũ bảo hiểm, theo SQLite hiện tại. Đường nét đứt thể hiện liên kết trong model chưa được áp dụng thành ràng buộc khóa ngoại trong CSDL.", ""])
(OUT / "README.md").write_text("\n".join(readme), encoding="utf-8")
print(json.dumps({"outputs": [str(OUT / n) for n in ["physical_erd.png", "physical_erd.svg", "schema_snapshot.json", "README.md"]],
                  "tables": len(schema), "columns": sum(len(t["columns"]) for t in schema.values()),
                  "foreign_keys": len(actual_fks), "png_size": canvas.size}, ensure_ascii=False))
