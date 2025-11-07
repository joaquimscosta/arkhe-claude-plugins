#!/usr/bin/env python3
"""
Validate microlearn outputs for basic structure and length.
Usage:
    python3 scripts/validate_microlesson.py [micro_blog.md] [video_script.md]
Checks:
    * micro_blog.md <= 250 words
    * Required sections in both files
    * video_script contains Hook/Takeaway/CTA
"""
import sys
import re
from pathlib import Path

REQ_HEADERS = [
    r"^##\s1\)\sHook",
    r"^##\s2\)\sCore Concept",
    r"^##\s3\)\sShow It",
    r"^##\s4\)\sTakeaway",
    r"^##\s5\)\sCTA",
]

def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))

def check_sections(text: str, fname: str):
    errs = []
    for pat in REQ_HEADERS:
        if not re.search(pat, text, flags=re.MULTILINE):
            errs.append(f"{fname}: missing section {pat}")
    return errs

def main():
    issues = []
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if p.exists():
            t = p.read_text(encoding="utf-8", errors="ignore")
            wc = word_count(t)
            if wc > 250:
                issues.append(f"{p.name}: {wc} words (limit 250)")
            issues += check_sections(t, p.name)
        else:
            issues.append(f"Missing file: {p}")
    if len(sys.argv) > 2:
        p2 = Path(sys.argv[2])
        if p2.exists():
            t2 = p2.read_text(encoding="utf-8", errors="ignore")
            for key in ["Hook", "Takeaway", "CTA"]:
                if key not in t2:
                    issues.append(f"{p2.name}: missing '{key}' cue")
            issues += check_sections(t2, p2.name)
        else:
            issues.append(f"Missing file: {p2}")
    if issues:
        print("Validation FAILED:")
        for e in issues:
            print("-", e)
        sys.exit(2)
    print("Validation PASSED ✅")

if __name__ == "__main__":
    main()
