from pathlib import Path
import re

TITLE_MAP = {
    9: ("夜里一点", "两点钟的楼梯"),
    11: ("804", "804门没锁"),
    14: ("永安里", "照片里的永安里"),
    15: ("十一年前", "十一年前的照片"),
    21: ("旧站台", "旧站台还在那里"),
    23: ("投诉还在", "那张投诉还在"),
    25: ("后台日志", "后台留下的日志"),
    26: ("六箱纸档", "库房里的六箱纸档"),
    27: ("维修记录", "十一年前的维修记录"),
    29: ("老陈", "老陈记得那栋楼"),
    31: ("旧回访单", "旧回访单上的地址"),
    32: ("夜班旧册", "夜班旧册里的记录"),
    33: ("旧地址表", "旧地址表里的永安里"),
    34: ("同步清单", "同步清单缺了一项"),
    35: ("三十分钟", "消失的三十分钟"),
    36: ("旧广播", "旧广播里的通知"),
    37: ("普通夜班", "那一晚的普通夜班"),
    38: ("接应点", "地图外的接应点"),
    40: ("失物登记", "失物登记里的名字"),
    41: ("人找到了", "人找到了以后"),
    42: ("回来以后", "回来以后少了什么"),
    44: ("拆牌清单", "拆牌清单上的地址"),
    45: ("库房编号", "库房编号对不上"),
    46: ("夜间报修", "夜间报修留下的地址"),
    47: ("指向哪里", "旧记录究竟指向哪里"),
    50: ("旧号新号", "旧号和新号之间"),
    51: ("图幅索引", "图幅索引缺了一页"),
    52: ("缺的一页", "档案里缺的那一页"),
    53: ("白班回函", "白班回函里的答案"),
}

ROOT = Path(__file__).resolve().parents[1]
READY = ROOT / "chapters" / "ready"
PLAN = ROOT / "plans" / "chapter_plan.csv"


def nonblank_len(s: str) -> int:
    return len(re.sub(r"\s+", "", s))


for chapter, (old_title, new_title) in TITLE_MAP.items():
    if nonblank_len(new_title) < 5:
        raise SystemExit(f"new title too short for chapter {chapter}: {new_title}")

    path = READY / f"{chapter:04d}.md"
    text = path.read_text(encoding="utf-8")
    pattern = rf"(?m)^title:\s*[\"']?{re.escape(old_title)}[\"']?\s*$"
    replacement = f'title: "{new_title}"'
    patched, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"chapter {chapter}: expected title {old_title!r} not found exactly once")
    path.write_text(patched, encoding="utf-8", newline="\n")

plan_text = PLAN.read_text(encoding="utf-8")
for chapter, (old_title, new_title) in TITLE_MAP.items():
    pattern = rf"(?m)^{chapter},{re.escape(old_title)},"
    replacement = f"{chapter},{new_title},"
    plan_text, count = re.subn(pattern, replacement, plan_text, count=1)
    if count != 1:
        raise SystemExit(f"chapter_plan row {chapter}: expected title {old_title!r} not found exactly once")
PLAN.write_text(plan_text, encoding="utf-8", newline="\n")

# Final gate: every publishable chapter title in ready/ must contain at least five non-whitespace chars.
violations = []
for path in sorted(READY.glob("[0-9][0-9][0-9][0-9].md")):
    parts = path.read_text(encoding="utf-8").split("---", 2)
    if len(parts) < 3:
        violations.append((path.name, "<missing frontmatter>"))
        continue
    head = parts[1]
    match = re.search(r"(?m)^title:\s*[\"']?(.*?)[\"']?\s*$", head)
    if not match:
        violations.append((path.name, "<missing title>"))
        continue
    title = match.group(1).strip().strip("\"'")
    if nonblank_len(title) < 5:
        violations.append((path.name, title))

if violations:
    raise SystemExit(f"ready title length gate failed: {violations}")

print(f"Patched {len(TITLE_MAP)} chapter titles and chapter_plan.csv; all ready titles pass >=5 nonblank chars.")
