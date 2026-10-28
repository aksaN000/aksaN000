"""Appends a content hash to every assets/*.svg link in README.md so GitHub's image cache never serves a stale plate."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


def stamp(match):
    attr, path = match.group(1), match.group(2)
    digest = hashlib.sha1((ROOT / path).read_bytes()).hexdigest()[:8]
    return f'{attr}="{path}?v={digest}"'


text = README.read_text(encoding="utf-8")
updated = re.sub(r'(src|srcset)="(assets/[^"?]+\.svg)(?:\?v=[0-9a-f]+)?"', stamp, text)
README.write_text(updated, encoding="utf-8", newline="\n")
print(f"stamped {len(re.findall(r'src(?:set)?=\"assets/', updated))} images")
