"""Shared design system for the profile SVGs: palette, embedded fonts, text metrics."""
import base64
import html
from functools import lru_cache
from pathlib import Path

from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).parent / "fonts"

INK = "#0d1117"
PANEL = "#0e0e10"
HAIR = "#26252a"
IVORY = "#e9e3d5"
MUTED = "#b3ad9f"
FAINT = "#7d786d"
BRASS = "#c2a36b"

FONTS = {
    "serif": ("Cormorant", "cormorant-400.woff", 400, "normal"),
    "serif-lt": ("Cormorant", "cormorant-300.woff", 300, "normal"),
    "serif-md": ("Cormorant", "cormorant-500.woff", 500, "normal"),
    "serif-it": ("Cormorant", "cormorant-italic-400.woff", 400, "italic"),
    "mono": ("JetBrains Mono", "jetbrains-400.woff", 400, "normal"),
}


@lru_cache(maxsize=None)
def _font(key):
    return TTFont(FONT_DIR / FONTS[key][1])


def measure(text, key, size, spacing=0.0):
    """Rendered width of `text` in px, including CSS letter-spacing (em)."""
    f = _font(key)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    units = sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] for c in text)
    return units * size / upm + spacing * size * len(text)


def wrap(text, key, size, width, spacing=0.0):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if measure(trial, key, size, spacing) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def font_css(*keys):
    rules = []
    for key in dict.fromkeys(keys):
        family, file, weight, style = FONTS[key]
        data = base64.b64encode((FONT_DIR / file).read_bytes()).decode()
        rules.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff;base64,{data}) format('woff');}}"
        )
    classes = {
        "serif": "font-family:'Cormorant',Georgia,serif;font-weight:400;font-variant-numeric:lining-nums",
        "serif-lt": "font-family:'Cormorant',Georgia,serif;font-weight:300;font-variant-numeric:lining-nums",
        "serif-md": "font-family:'Cormorant',Georgia,serif;font-weight:500;font-variant-numeric:lining-nums",
        "serif-it": "font-family:'Cormorant',Georgia,serif;font-weight:400;font-style:italic;font-variant-numeric:lining-nums",
        "mono": "font-family:'JetBrains Mono',Consolas,monospace;font-weight:400",
    }
    rules += [f".{k}{{{v}}}" for k, v in classes.items() if k in keys]
    return "\n".join(rules)


def esc(s):
    return html.escape(s, quote=True)


def svg(width, height, body, fonts, title, extra_css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
{font_css(*fonts)}
{extra_css}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
{body}
</svg>
"""


def text(x, y, s, cls, size, fill=IVORY, spacing=0.0, anchor="start", opacity=None):
    ls = f' letter-spacing="{spacing}em"' if spacing else ""
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" fill="{fill}"'
            f' text-anchor="{anchor}"{ls}{op}>{esc(s)}</text>')


def ticks(x, y, w, h, length=10, color=BRASS, inset=0):
    """Brass corner ticks framing a rectangle."""
    x0, y0, x1, y1 = x + inset, y + inset, x + w - inset, y + h - inset
    L = length
    d = (f"M{x0},{y0 + L}V{y0}H{x0 + L} M{x1 - L},{y0}H{x1}V{y0 + L} "
         f"M{x1},{y1 - L}V{y1}H{x1 - L} M{x0 + L},{y1}H{x0}V{y1 - L}")
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1"/>'


def grain(pid="grain", opacity=0.05):
    """Fine dot lattice used as paper texture."""
    return (f'<defs><pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse">'
            f'<circle cx="1" cy="1" r="0.55" fill="{IVORY}" opacity="{opacity}"/></pattern></defs>')
