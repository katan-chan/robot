# /// script
# requires-python = ">=3.11"
# ///
"""Knowledge graph của dự án robot nhện.

  uv run tools/kb.py build              sinh docs/kb/graph.json
  uv run tools/kb.py check              kiểm schema + graph.json không cũ (hook dùng)
  uv run tools/kb.py show 12.7          một nút và các cạnh vào/ra
  uv run tools/kb.py impact 12.7        đổi X thì ảnh hưởng tới đâu (mặc định 3 bước)
  uv run tools/kb.py deps T1.6          các task phải xong trước T1.6
  uv run tools/kb.py path 12.7 T1.6     đường nối ngắn nhất giữa hai nút
  uv run tools/kb.py find servo         tìm theo từ khoá
  uv run tools/kb.py selftest           chạy các câu hỏi năng lực (CQ) trong ontology

Pipeline (graph-engineering): ontology.toml là schema → trích xuất bằng luật từ
docs/decisions → curated.toml (trích xuất tay) + harness.toml → gộp bí danh →
kiểm domain/range → graph.json.
"""
import json
import re
import sys
import tomllib
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEC = ROOT / "docs/decisions"
KB = ROOT / "docs/kb"
GRAPH = KB / "graph.json"

ID = r"\d{1,2}\.\d{1,2}[a-z]?"
ROW = re.compile(rf"^\|\s*({ID})\s*\|(.*)\|(.*)\|(.*)\|\s*$")
TASK = re.compile(r"^- (T\d+\.\d+) (.*)$")
PHASE = re.compile(r"^### Giai đoạn (\d+)\. (.*)$")
DATE = re.compile(r"^Ngày: (\d{4}-\d{2}-\d{2})", re.M)
SUPER = re.compile(rf"Đã thay → ({ID})(?![\w]|\.\d)")
CITE = re.compile(rf"(?<![\w.])({ID})(?![\w]|\.\d)")
RANGE = re.compile(r"(?<![\w.])(\d{1,2})\.(\d{1,2})–(\d{1,2})\.(\d{1,2})(?![\w]|\.\d)")
# Số đứng sau các từ này là phiên bản phần mềm, không phải mã quyết định ("Blender 5.2").
VERSION_WORDS = ("Blender", "Python", "MuJoCo", "mujoco", "≥")


def load(name):
    return tomllib.loads((ROOT / name).read_text(encoding="utf-8"))


def cites(text, known):
    """Mã quyết định được nhắc trong text, chỉ giữ mã có thật."""
    out = set()
    for m in RANGE.finditer(text):
        a, b, c, d = map(int, m.groups())
        if a == c and b < d:
            out |= {f"{a}.{i}" for i in range(b, d + 1)}
    for m in CITE.finditer(text):
        if not any(w in text[max(0, m.start() - 12):m.start()] for w in VERSION_WORDS):
            out.add(m.group(1))
    return out & known


def who(s):
    s = s.strip()
    if "tự quyết" in s:
        return "claude-decided"
    if "xác nhận" in s:
        return "user-confirmed"
    if s.startswith("[Người dùng]"):
        return "user"
    if "Claude đề xuất" in s:
        return "claude-proposed"
    return "unknown"


def status(s):
    s = s.strip()
    for prefix, v in (("Đang áp dụng", "active"), ("Chờ chốt", "pending"), ("Đã thay", "superseded")):
        if s.startswith(prefix):
            return v
    return "unknown"


def build():
    """Trả về (nodes, edges, errors). nodes: id → dict; edges: list of dict."""
    nodes, edges, errors = {}, [], []

    def add_node(n):
        old = nodes.get(n["id"])
        if old and old != n:
            errors.append(f"trùng id {n['id']}: {old.get('src')} và {n.get('src')}")
        nodes[n["id"]] = n

    def add_edge(frm, rel, to, src, by, conf=1.0):
        edges.append({"from": frm, "rel": rel, "to": to, "src": src, "by": by, "conf": conf})

    # 1. Trích xuất bằng luật: bảng quyết định trong docs/decisions/NN-*.md
    texts = {}
    for f in sorted(DEC.glob("[0-9][0-9]-*.md")):
        body = f.read_text(encoding="utf-8")
        since = (DATE.search(body) or [None, None])[1]
        rel = f.relative_to(ROOT).as_posix()
        for i, line in enumerate(body.splitlines(), 1):
            m = ROW.match(line)
            if not m:
                continue
            did, text, by, st = (g.strip() for g in m.groups())
            add_node({"id": did, "type": "Decision", "label": text[:100], "text": text,
                      "decided_by": who(by), "status": status(st), "status_raw": st,
                      "step": int(f.name[:2]), "src": f"{rel}#L{i}", "since": since, "by": "rule:decision-table"})
            texts[did] = text + " " + st
            if sup := SUPER.search(st):
                add_edge(sup.group(1), "SUPERSEDES", did, f"{rel}#L{i}", "rule:supersedes")

    # Task và giai đoạn trong Bước 7
    f = DEC / "07-trinh-tu-task.md"
    rel = f.relative_to(ROOT).as_posix()
    phase = None
    task_texts = {}
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if m := PHASE.match(line):
            phase = f"GD{m.group(1)}"
            add_node({"id": phase, "type": "Phase", "label": f"Giai đoạn {m.group(1)}. {m.group(2)}",
                      "src": f"{rel}#L{i}", "by": "rule:task-list"})
        elif (m := TASK.match(line)) and phase:
            tid, text = m.groups()
            add_node({"id": tid, "type": "Task", "label": text.replace("~~", "")[:100], "text": text,
                      "phase": phase, "src": f"{rel}#L{i}", "by": "rule:task-list"})
            add_edge(tid, "PART_OF", phase, f"{rel}#L{i}", "rule:task-list")
            task_texts[tid] = text

    known = {k for k, n in nodes.items() if n["type"] == "Decision"}
    superseded_by = {(e["to"], e["from"]) for e in edges if e["rel"] == "SUPERSEDES"}
    for frm, text in list(texts.items()) + list(task_texts.items()):
        for to in sorted(cites(text, known) - {frm}):
            if (frm, to) in superseded_by:
                continue
            add_edge(frm, "CITES", to, nodes[frm]["src"], "rule:cites")

    # 2. Harness (Harness²: 8 thành phần)
    h = load("harness.toml")
    for name, c in h["components"].items():
        hid = f"harness:{name}"
        add_node({"id": hid, "type": "HarnessComponent", "label": c["desc"], "mutability": c["mutability"],
                  "status": c.get("status", "active"), "src": "harness.toml", "by": "rule:harness"})
        for p in c["paths"]:
            add_edge(hid, "STORED_IN", f"file:{p}", "harness.toml", "rule:harness")

    # 3. Curated (trích xuất tay), có gộp bí danh
    cur = load("docs/kb/curated.toml")
    alias = cur.get("aliases", {})
    canon = lambda x: alias.get(x, x)
    conf = cur["meta"]["confidence"]
    for typ, items in cur.get("nodes", {}).items():
        for nid, a in items.items():
            nid = canon(nid)
            n = {"id": nid, "type": typ, "label": a["label"], "src": a["src"],
                 "since": cur["meta"]["since"], "by": "curated"}
            if "level" in a:
                n["level"] = a["level"]
            add_node(n)
            if "stored_in" in a:
                add_edge(nid, "STORED_IN", f"file:{a['stored_in']}", a["src"], "curated", conf)
    for did, tags in cur.get("decision_tags", {}).items():
        if did in nodes:
            nodes[did]["tags"] = tags
        else:
            errors.append(f"decision_tags: không có quyết định {did}")
    file_rels = {"STORED_IN", "WRITES"}
    for rel_name, table in cur.get("edges", {}).items():
        src_rule = cur["edge_src"].get(rel_name, "docs/kb/curated.toml")
        for frm, tos in table.items():
            frm = canon(frm)
            src = nodes.get(frm, {}).get("src", frm) if src_rule == "from" else src_rule
            for to in tos:
                to = f"file:{to}" if rel_name in file_rels else canon(to)
                add_edge(frm, rel_name, to, src, "curated", conf)

    # File: tự tạo nút cho mọi đường dẫn được nhắc tới
    for e in edges:
        if e["to"].startswith("file:") and e["to"] not in nodes:
            nodes[e["to"]] = {"id": e["to"], "type": "File", "label": e["to"][5:], "src": e["src"], "by": "rule:file-ref"}

    edges = [dict(t) for t in sorted({tuple(sorted(e.items())) for e in edges},
                                     key=lambda t: (dict(t)["from"], dict(t)["rel"], dict(t)["to"]))]
    errors += validate(nodes, edges)
    return nodes, edges, errors


def validate(nodes, edges):
    ont = load("docs/kb/ontology.toml")
    types, rels = set(ont["entities"]), ont["relations"]
    err = []
    for n in nodes.values():
        if n["type"] not in types:
            err.append(f"{n['id']}: loại {n['type']} không có trong ontology")
    for e in edges:
        tag = f"({e['from']})-[{e['rel']}]->({e['to']})"
        if e["rel"] not in rels:
            err.append(f"{tag}: quan hệ không có trong ontology")
            continue
        a, b = nodes.get(e["from"]), nodes.get(e["to"])
        if not a or not b:
            err.append(f"{tag}: đầu mút không tồn tại (src {e['src']})")
            continue
        if a["type"] not in rels[e["rel"]]["domain"] or b["type"] not in rels[e["rel"]]["range"]:
            err.append(f"{tag}: sai domain/range ({a['type']} → {b['type']})")
        if not e["src"]:
            err.append(f"{tag}: thiếu nguồn")
        if e["rel"] == "SUPERSEDES" and b.get("status") != "superseded":
            err.append(f"{tag}: {e['to']} bị thay nhưng trạng thái chưa là 'Đã thay'")
    has_phase = {e["from"] for e in edges if e["rel"] == "PART_OF"}
    err += [f"{t}: task không thuộc giai đoạn nào" for t, n in nodes.items() if n["type"] == "Task" and t not in has_phase]
    writers = {}
    for e in edges:
        if e["rel"] == "WRITES":
            writers.setdefault(e["to"], []).append(e["from"])
    err += [f"{f}: nhiều vai trò cùng ghi ({', '.join(w)}), vi phạm 'một người ghi mỗi file'" for f, w in writers.items() if len(w) > 1]
    seen = {}
    for n in nodes.values():
        if n["type"] in ("Component", "Check"):
            key = re.sub(r"\W+", "", n["label"].lower())
            if key in seen:
                err.append(f"{n['id']} và {seen[key]}: nhãn trùng, có thể là cùng một thứ (thêm vào [aliases])")
            seen[key] = n["id"]
    return err


def serialize(nodes, edges):
    return json.dumps({"nodes": [nodes[k] for k in sorted(nodes)], "edges": edges},
                      ensure_ascii=False, indent=1) + "\n"


def index(edges):
    out, inc = {}, {}
    for e in edges:
        out.setdefault(e["from"], []).append(e)
        inc.setdefault(e["to"], []).append(e)
    return out, inc


def triple(e):
    return f"({e['from']})-[{e['rel']}]->({e['to']})  # {e['src']}"


# Đi theo hướng "ảnh hưởng lan tới": ràng buộc đi xuôi; người phụ thuộc vào X thì đi ngược.
IMPACT_OUT = {"CONSTRAINS", "SUPERSEDES"}
IMPACT_IN = {"CITES", "VERIFIES", "IMPLEMENTS", "CHECKS", "DEPENDS_ON", "BLOCKS", "PERFORMS", "REVIEWS"}


def impact(nodes, edges, start, hops=3):
    out, inc = index(edges)
    seen, found, q = {start}, [], deque([(start, 0)])
    while q:
        cur, d = q.popleft()
        if d == hops:
            continue
        nxt = [(e, e["to"]) for e in out.get(cur, []) if e["rel"] in IMPACT_OUT]
        nxt += [(e, e["from"]) for e in inc.get(cur, []) if e["rel"] in IMPACT_IN]
        for e, n in nxt:
            if n not in seen:
                seen.add(n)
                found.append((d + 1, e, n))
                q.append((n, d + 1))
    return found


def path(nodes, edges, a, b):
    out, inc = index(edges)
    prev, q = {a: None}, deque([a])
    while q:
        cur = q.popleft()
        if cur == b:
            chain = []
            while prev[cur]:
                e, cur = prev[cur]
                chain.append(e)
            return chain[::-1]
        for e in out.get(cur, []) + inc.get(cur, []):
            n = e["to"] if e["from"] == cur else e["from"]
            if n not in prev:
                prev[n] = (e, cur)
                q.append(n)
    return None


def deps(edges, start):
    """Mọi task phải xong trước start (đi theo DEPENDS_ON, bắc cầu)."""
    out, _ = index(edges)
    seen, q = [], deque([start])
    while q:
        for e in out.get(q.popleft(), []):
            if e["rel"] == "DEPENDS_ON" and e["to"] not in seen:
                seen.append(e["to"])
                q.append(e["to"])
    return seen


def selftest():
    known = {"5.2", "8.5", "9.1", "9.3", "9.6"}
    assert cites("Blender 5.2 → MJCF, theo 8.5.", known) == {"8.5"}
    assert cites("phiên bản 3.5.0, ma sát 0.8–1.0, T1.6", known) == set()
    assert cites("xem 9.1–9.6 và (9.3)", known) == {"9.1", "9.3", "9.6"}
    nodes, edges, errors = build()
    assert not errors, errors
    has = lambda f, r, t: any(e["from"] == f and e["rel"] == r and e["to"] == t for e in edges)
    n = nodes
    assert n["12.7"]["status"] == "active" and n["12.7"]["decided_by"] == "user-confirmed"        # CQ1
    assert has("3.2", "SUPERSEDES", "3.1")                                                        # CQ2
    hit = {x for _, _, x in impact(nodes, edges, "12.7")}
    assert {"comp:servo-catalog", "check:static-torque", "T1.1"} <= hit, hit                      # CQ3
    comps = {e["to"] for e in edges if e["from"] == "T1.6" and e["rel"] == "IMPLEMENTS"}
    assert "8.3" in {e["from"] for e in edges if e["rel"] == "CONSTRAINS" and e["to"] in comps}  # CQ4
    assert {"T1.4", "T0.1"} <= set(deps(edges, "T1.6")) and "T1.7" not in deps(edges, "T1.6")   # CQ5
    assert len([e for e in edges if e["rel"] == "VERIFIES" and e["to"] == "8.5"]) >= 3            # CQ6
    sec = {d for d, x in n.items() if "security" in x.get("tags", [])}
    assert {"comp:key-store", "comp:web-server"} <= {e["to"] for e in edges if e["rel"] == "CONSTRAINS" and e["from"] in sec}  # CQ7
    assert has("q:wall-climb", "BLOCKS", "T5.2")                                                  # CQ8
    assert [e["from"] for e in edges if e["rel"] == "WRITES" and e["to"] == "file:spider/gait/"] == ["role:gait-worker"]  # CQ9
    assert len([x for x in n.values() if x["type"] == "HarnessComponent"]) == 8                  # CQ10
    ont = load("docs/kb/ontology.toml")
    assert {"Bug", "Lesson"} <= set(ont["entities"]) and "AFFECTS" in ont["relations"]          # CQ11, CQ12 (schema sẵn)
    print(f"selftest: OK ({len(nodes)} nút, {len(edges)} cạnh)")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "selftest":
        return selftest()
    nodes, edges, errors = build()
    if errors:
        print("KB LỖI — sửa nguồn (docs/decisions, docs/kb/curated.toml, harness.toml), không sửa graph.json:", file=sys.stderr)
        print("\n".join(f"  - {e}" for e in errors), file=sys.stderr)
        return 1
    text = serialize(nodes, edges)
    if cmd == "build":
        if not GRAPH.exists() or GRAPH.read_text(encoding="utf-8") != text:
            GRAPH.write_text(text, encoding="utf-8")
        print(f"{GRAPH.relative_to(ROOT)}: {len(nodes)} nút, {len(edges)} cạnh")
    elif cmd == "check":
        if not GRAPH.exists() or GRAPH.read_text(encoding="utf-8") != text:
            print("KB cũ: graph.json không khớp nguồn. Chạy: uv run tools/kb.py build", file=sys.stderr)
            return 1
        print(f"KB OK: {len(nodes)} nút, {len(edges)} cạnh")
    elif cmd == "show":
        nid = argv[2]
        if nid not in nodes:
            print(f"không có nút {nid}", file=sys.stderr)
            return 1
        print(json.dumps(nodes[nid], ensure_ascii=False, indent=1))
        out, inc = index(edges)
        for e in out.get(nid, []) + inc.get(nid, []):
            print(triple(e))
    elif cmd == "impact":
        hops = int(argv[3]) if len(argv) > 3 else 3
        for d, e, n in impact(nodes, edges, argv[2], hops):
            print(f"{d} {triple(e)}  — {nodes[n]['label'][:60]}")
    elif cmd == "deps":
        for t in deps(edges, argv[2]):
            print(f"{t:6} {nodes[t]['label'][:80]}")
    elif cmd == "path":
        chain = path(nodes, edges, argv[2], argv[3])
        print("\n".join(map(triple, chain)) if chain else "không có đường nối")
    elif cmd == "find":
        kw = " ".join(argv[2:]).lower()
        for k in sorted(nodes):
            x = nodes[k]
            if kw in (x["label"] + x.get("text", "")).lower() or kw in k.lower():
                print(f"{k:28} {x['type']:16} {x['label'][:70]}")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv) or 0)
