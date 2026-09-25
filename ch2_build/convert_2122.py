import json
import re
from pathlib import Path

base = Path(__file__).parent
lines = (base / "part_2122.md").read_text(encoding="utf-8").splitlines()
blocks = []
pending_caption = None
idx = 0

while idx < len(lines):
    line = lines[idx].strip()
    if not line:
        idx += 1
        continue
    if line.startswith("#### "):
        blocks.append({"type": "heading", "level": 3, "text": line[5:]})
    elif line.startswith("### "):
        blocks.append({"type": "heading", "level": 2, "text": line[4:]})
    elif line.startswith("## "):
        blocks.append({"type": "heading", "level": 1, "text": line[3:]})
    elif line.startswith("[FIGURE:"):
        blocks.append({"type": "figure", "source_paragraph": 196, "caption": "Hình 2.1. Kiến trúc xử lý tổng quát của mô hình YOLO"})
    elif line.startswith("[CAPTION:"):
        pending_caption = line[len("[CAPTION:"):-1].strip()
    elif line.startswith("$$"):
        blocks.append({"type": "equation", "text": line[2:-2]})
    elif line.startswith("|"):
        rows = []
        while idx < len(lines) and lines[idx].strip().startswith("|"):
            cells = [cell.strip() for cell in lines[idx].strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                rows.append(cells)
            idx += 1
        block = {"type": "table", "rows": rows}
        if pending_caption:
            block["caption"] = pending_caption
            pending_caption = None
        blocks.append(block)
        continue
    else:
        blocks.append({"type": "paragraph", "text": line})
    idx += 1

assert len([b for b in blocks if b["type"] == "figure"]) == 1
assert len([b for b in blocks if b["type"] == "table"]) == 2
assert len([b for b in blocks if b["type"] == "equation"]) == 10
assert len([b for b in blocks if b["type"] == "heading"]) == 28

out = base / "part_2122.json"
out.write_text(json.dumps({"blocks": blocks}, ensure_ascii=False, indent=2), encoding="utf-8")
text_content = " ".join(b.get("text", "") for b in blocks if b["type"] in {"paragraph", "heading"})
print(out)
print("blocks:", len(blocks))
print("words:", len(text_content.split()))
print("tables:", len([b for b in blocks if b["type"] == "table"]))
print("equations:", len([b for b in blocks if b["type"] == "equation"]))
