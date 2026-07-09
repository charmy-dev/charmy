"""Fix RST title underlines that are too short for CJK text."""
import glob

for f in sorted(glob.glob("**/*.rst", recursive=True)):
    content = open(f, "r", encoding="utf-8").read()
    lines = content.split("\n")
    changed = False
    for i in range(1, len(lines)):
        line = lines[i]
        if not line.strip():
            continue
        if not all(c in "-=~^" for c in line.strip()):
            continue
        if len(line.strip()) >= 30:
            continue
        prev = lines[i - 1].strip()
        if not prev or prev.startswith("..") or prev.startswith(" "):
            continue
        if ":" in prev[:3]:
            continue
        ch = line[0]
        # Use len() of the string (RST compares character count, not byte count)
        needed = max(len(prev), len(line), 30)
        new_line = ch * needed
        if line != new_line:
            lines[i] = new_line
            changed = True
            print(f"  line {i+1}: {repr(prev[:30])} -> {needed} chars")
    if changed:
        open(f, "w", encoding="utf-8").write("\n".join(lines))
        print(f"  [FIXED] {f}")

print("Done")
