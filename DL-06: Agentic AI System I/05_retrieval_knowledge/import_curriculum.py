### import_curriculum.py - convert the CPE RMUTT 2568 markdown files into knowledge base docs
### Source: https://github.com/thanasinb/CPE_RMUTT68 (clone to 05_retrieval_knowledge/data/raw/CPE_RMUTT68)
### Output: data/kb_curriculum.json, then run python ingest.py
### Run: python import_curriculum.py [repo folder]

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "09_backend"))
import setup_path  ### add folders 02-09 to sys.path (must come first)
import json
import re

import config

REPO_URL = "https://github.com/thanasinb/CPE_RMUTT68/blob/main/"
SNAPSHOT_DATE = "2026-11-12"   ### last commit date of the repo when imported
PROGRAM = "หลักสูตร วศ.บ. วิศวกรรมคอมพิวเตอร์ มทร.ธัญบุรี (ปรับปรุง 2568)"
PROGRAM_EN = "B.Eng. Computer Engineering, RMUTT (Revised 2025)"


def clean_md(line):
    ### strip markdown: links, anchors, bold, tables
    line = re.sub(r"<a id=[^>]*></a>", "", line)
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = line.replace("**", "").replace("`", "")
    line = line.lstrip("#>").strip()
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip("|").split("|")]
        line = " — ".join(c for c in cells if c)
    return line.strip()


def new_doc(doc_id, title_th, title_en, category, url, page, lines):
    return {
        "doc_id": doc_id, "title_th": title_th, "title_en": title_en,
        "category": category, "source_url": url, "page": page,
        "published_at": SNAPSHOT_DATE, "effective_date": "2025-06-01", "expired_date": None,
        "status": "active", "superseded_by": None, "access_level": "public", "faculty": "all",
        "text_mixed": [x for x in (clean_md(l) for l in lines) if x and x != "---"],
    }


def import_prospectus(repo):
    ### split by "## n." sections, and by "###" sub-sections (e.g. each semester plan)
    path = repo / "CPE_RMUTT68_Prospectus.md"
    docs, heading, sub, lines = [], None, None, []

    def flush():
        if heading and lines:
            name = heading + (" — " + sub if sub else "")
            th, _, en = name.partition(" | ")
            n = len(docs) + 1
            docs.append(new_doc(f"PROSP-{n:02d}", f"{PROGRAM} — {name}", f"{PROGRAM_EN} — {en or th}",
                                "handbook", REPO_URL + path.name, None, lines))

    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^## \d+\.", line):
            flush()
            heading, sub, lines = clean_md(line), None, []
        elif line.startswith("### ") and heading:
            flush()
            sub, lines = clean_md(line), []
            ### add the words students use, e.g. "ปี 3 เทอม 1" for "ชั้นปีที่ 3 / ภาคการศึกษาที่ 1"
            plan = re.search(r"ชั้นปีที่ (\d) / ภาคการศึกษาที่ (\d)", sub)
            if plan:
                lines.append(f"แผนการเรียน ปี {plan.group(1)} เทอม {plan.group(2)} ต้องเรียนวิชาต่อไปนี้")
        elif heading:
            lines.append(line)
    flush()
    return docs


def import_course(path, repo):
    text = path.read_text(encoding="utf-8")
    front = dict(re.findall(r"^(\w+):\s*(.*)$", text.split("---")[1], re.M))
    body = text.split("---", 2)[2]
    ### keep text up to the CLO table; the PLO mapping is long and not useful
    body = body.split("## ผลลัพธ์การเรียนรู้ระดับหลักสูตร (PLOs)")[0]
    prereq = re.search(r"\*\*วิชาบังคับก่อน \| Prerequisites:\*\*(.*)", body)

    lines = [
        f"รหัสวิชา {front['code']} {front['name_th']} ({front['name_en']}) หน่วยกิต {front['credits']}",
        f"ประเภท: {front['type']} | ชั้นปี: {front.get('year')} | ภาคการศึกษา: {front.get('semester')}",
        f"วิชาบังคับก่อน (Prerequisites): {clean_md(prereq.group(1)) if prereq else 'ไม่มี'}",
    ]
    keep = False
    for line in body.splitlines():
        if line.startswith("## "):
            keep = "Course Description" in line or "CLOs" in line
            continue
        if keep and not line.startswith("| CLO") and not line.startswith("| ---"):
            ### CLO table: keep CLO and outcome, drop the PLO column
            if line.startswith("|"):
                cells = [clean_md(c) for c in line.strip("|").split("|")]
                line = f"{cells[0]}: {cells[1]}" if len(cells) > 1 else line
            lines.append(line)

    rel = path.relative_to(repo).as_posix()
    return new_doc("COURSE-" + front["code"], f"รายวิชา {front['code']} {front['name_th']}",
                   f"Course {front['code']} {front['name_en']}", "course", REPO_URL + rel, None, lines)


if __name__ == "__main__":
    repo = Path(sys.argv[1]) if len(sys.argv) > 1 else config.KB_DIR / "raw" / "CPE_RMUTT68"
    docs = import_prospectus(repo)
    for path in sorted((repo / "courses").rglob("*.md")):
        docs.append(import_course(path, repo))
    out = config.KB_DIR / "kb_curriculum.json"
    out.write_text(json.dumps(docs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(docs)} documents -> {out}")
