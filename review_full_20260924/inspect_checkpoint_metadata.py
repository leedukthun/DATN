"""Read checkpoint metadata without importing torch or executing pickle globals."""
import hashlib
import json
import pickletools
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
reports = []
for relative in ("backend/models/best.pt", "backend/models/best_3class.pt"):
    path = ROOT / relative
    with zipfile.ZipFile(path) as archive:
        name = next(n for n in archive.namelist() if n.endswith("data.pkl"))
        operations = list(pickletools.genops(archive.read(name)))
    # Recover only primitive values and explicit memo references. No pickle loads.
    memo = {}
    scalar_ops = {"BINUNICODE", "SHORT_BINUNICODE", "UNICODE", "BININT", "BININT1", "BININT2", "BINFLOAT", "INT", "FLOAT", "NEWTRUE", "NEWFALSE", "NONE"}
    resolved = []
    last = None
    for op, arg, position in operations:
        if op.name in scalar_ops:
            last = True if op.name == "NEWTRUE" else False if op.name == "NEWFALSE" else arg
            resolved.append((op.name, last))
        elif op.name in {"BINPUT", "LONG_BINPUT", "PUT"}:
            memo[arg] = last
            resolved.append((op.name, arg))
        elif op.name in {"BINGET", "LONG_BINGET", "GET"}:
            last = memo.get(arg)
            resolved.append((op.name, last))
        else:
            last = None
            resolved.append((op.name, arg))
    start = next((i for i, (op, arg) in enumerate(resolved) if arg == "train_results"), len(resolved))
    wanted = {"epoch", "metrics/precision(B)", "metrics/recall(B)", "metrics/mAP50(B)", "metrics/mAP50-95(B)"}
    history = {}
    for index in range(start + 1, len(resolved)):
        op, arg = resolved[index]
        if op == "BINUNICODE" and arg in wanted:
            stop = next((j for j in range(index + 1, len(resolved)) if resolved[j][0] == "APPENDS"), index)
            history[arg] = [v for kind, v in resolved[index + 1:stop] if kind in {"BININT", "BININT1", "BININT2", "BINFLOAT", "INT", "FLOAT"}]
    picks = []
    for index, (op, arg) in enumerate(resolved[:start]):
        if op == "BINUNICODE" and arg in {"model", "name", "lr0", "optimizer", "seed", "version", "date"}:
            following = resolved[index + 1:index + 5]
            value = next((v for kind, v in following if kind in scalar_ops or kind in {"BINGET", "LONG_BINGET", "GET"}), None)
            if isinstance(value, (str, float, int, bool)):
                picks.append({"key": arg, "value": value})
    row = {key: values[87] for key, values in history.items() if len(values) > 87}
    maps = history.get("metrics/mAP50-95(B)", [])
    reports.append({
        "file": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "method": "pickletools opcode inspection only; no deserialization or model execution",
        "selected_metadata": picks,
        "epoch_88": row,
        "highest_map5095_epoch": maps.index(max(maps)) + 1 if maps else None,
        "highest_map5095": max(maps) if maps else None,
    })
(ROOT / "review_full_20260924/checkpoint_metadata_review.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
