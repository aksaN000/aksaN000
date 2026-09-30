"""Builds the static SVG plates for the profile README into ../assets."""
import base64
import math
import re
from pathlib import Path

from theme import (BRASS, FAINT, HAIR, INK, IVORY, MUTED, esc, grain, measure,
                   svg, text, ticks, wrap)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
ICONS = Path(__file__).parent / "icons"
W = 900


def save(name, content):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name:28s} {len(content.encode()) / 1024:6.1f} KB")


def plate(h, inner=""):
    return (f'<rect width="{W}" height="{h}" fill="{INK}"/>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" fill="none" stroke="{HAIR}"/>'
            + inner)


# ───────────────────────────── banner ─────────────────────────────
def banner():
    h = 360
    cx, cy = 762, 186
    rings = [40, 66, 92]
    dial = "".join(
        f'<line x1="{cx + (rings[2] + 6) * math.cos(a):.1f}" y1="{cy + (rings[2] + 6) * math.sin(a):.1f}" '
        f'x2="{cx + (rings[2] + (13 if i % 6 == 0 else 9)) * math.cos(a):.1f}" '
        f'y2="{cy + (rings[2] + (13 if i % 6 == 0 else 9)) * math.sin(a):.1f}" '
        f'stroke="{BRASS if i % 6 == 0 else FAINT}" stroke-width="1"/>'
        for i, a in ((i, i * math.pi / 12) for i in range(24))
    )
    orbit = f"""
<g opacity="0.95">
  <line x1="{cx - 150}" y1="{cy}" x2="{cx + 130}" y2="{cy}" stroke="{HAIR}"/>
  <line x1="{cx}" y1="{cy - 130}" x2="{cx}" y2="{cy + 130}" stroke="{HAIR}"/>
  <circle cx="{cx}" cy="{cy}" r="{rings[0]}" fill="none" stroke="{FAINT}"/>
  <circle cx="{cx}" cy="{cy}" r="{rings[1]}" fill="none" stroke="{FAINT}" stroke-dasharray="2 5">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="120s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{cx}" cy="{cy}" r="{rings[2]}" fill="none" stroke="{HAIR}"/>
  {dial}
  <g><circle cx="{cx + rings[1]}" cy="{cy}" r="3.2" fill="{BRASS}"/>
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="22s" repeatCount="indefinite"/></g>
  <g><circle cx="{cx - rings[2]}" cy="{cy}" r="2.2" fill="{IVORY}" opacity="0.8"/>
    <animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="48s" repeatCount="indefinite"/></g>
  <g><circle cx="{cx}" cy="{cy - rings[0]}" r="1.8" fill="{MUTED}"/>
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="9s" repeatCount="indefinite"/></g>
  <circle cx="{cx}" cy="{cy}" r="3" fill="{BRASS}"/>
  <circle cx="{cx}" cy="{cy}" r="3" fill="none" stroke="{BRASS}">
    <animate attributeName="r" values="3;18" dur="3.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;0" dur="3.6s" repeatCount="indefinite"/>
  </circle>
</g>"""
    body = f"""
{grain()}
<defs>
  <radialGradient id="glow" cx="0.18" cy="0.1" r="0.75">
    <stop offset="0" stop-color="{BRASS}" stop-opacity="0.13"/>
    <stop offset="1" stop-color="{BRASS}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="fade" x1="0" x2="1">
    <stop offset="0" stop-color="{INK}" stop-opacity="0"/>
    <stop offset="0.55" stop-color="{INK}" stop-opacity="0.2"/>
    <stop offset="1" stop-color="{INK}" stop-opacity="1"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" fill="{INK}"/>
<rect width="{W}" height="{h}" fill="url(#grain)"/>
<rect width="{W}" height="{h}" fill="url(#glow)"/>
<rect x="16.5" y="16.5" width="{W - 33}" height="{h - 33}" fill="none" stroke="{HAIR}"/>
{ticks(16.5, 16.5, W - 33, h - 33, 12)}
{text(44, 52, "AKSAN000", "mono", 10.5, MUTED, 0.28)}
{text(W - 44, 52, "23.8103° N · 90.4125° E", "mono", 10.5, MUTED, 0.2, "end")}
{orbit}
{text(44, 118, "AI RESEARCH · SYSTEMS · WEB", "mono", 11, BRASS, 0.32)}
{text(40, 186, "Md. Aksan Gony Alif", "serif-lt", 62, IVORY)}
{text(44, 228, "Between the model and the metal.", "serif-it", 25, MUTED)}
<line x1="44" y1="258" x2="104" y2="258" stroke="{BRASS}"/>
{text(44, 292, "FINAL-YEAR CSE · BRAC UNIVERSITY · DHAKA", "mono", 10.5, MUTED, 0.24)}
{text(W - 44, 326, "FIG. 01 — ORBITS OF MEMORY", "mono", 10, FAINT, 0.24, "end")}
"""
    save("banner.svg", svg(W, h, body, ["serif-lt", "serif-it", "mono"],
                           "Md. Aksan Gony Alif — AI research, systems and web. Final-year CSE, BRAC University, Dhaka."))


# ─────────────────────────── chapter heads ───────────────────────────
CHAPTERS = [
    ("I", "Preface", "WHO I AM"),
    ("II", "Current work", "IN PROGRESS"),
    ("III", "Selected works", "SIX PROJECTS"),
    ("IV", "Instruments", "WHAT I BUILD WITH"),
    ("V", "Ledger", "BY THE NUMBERS"),
    ("VI", "Margins", "OFF THE CLOCK"),
    ("VII", "Correspondence", "WHERE TO FIND ME"),
]


def chapter(num, title, caption, idx):
    h = 78
    nx = 36
    nw = measure(num, "serif-it", 30)
    tx = nx + nw + 16
    tw = measure(title, "serif-lt", 32)
    cw = measure(caption, "mono", 10.5, 0.26)
    rule_start, rule_end = tx + tw + 22, W - 36 - cw - 20
    body = plate(h, f"""
{text(nx, 50, num, "serif-it", 30, BRASS)}
{text(tx, 50, title, "serif-lt", 32, IVORY)}
<line x1="{rule_start:.1f}" y1="42.5" x2="{rule_end:.1f}" y2="42.5" stroke="{HAIR}"/>
<circle cx="{rule_end:.1f}" cy="42.5" r="1.6" fill="{BRASS}"/>
{text(W - 36, 46, caption, "mono", 10.5, MUTED, 0.26, "end")}
""")
    save(f"ch-{idx}.svg", svg(W, h, body, ["serif-lt", "serif-it", "mono"], f"Chapter {num}: {title}"))


# ───────────────────────────── preface ─────────────────────────────
PREFACE = [
    "Hello, I'm Aksan: a final-year Computer Science & Engineering student at BRAC University "
    "in Dhaka, and someone who has to know how a thing works before I'm comfortable using it. "
    "That instinct is why, when I build something like a multithreaded process manager in C, I end up "
    "following its mutexes and spinlocks all the way down to the assembly. It's also why my thesis began "
    "with my own intuition about how memory and confidence should work inside a language model, rather "
    "than with a paper I was handed.",
    "I tend to think independently. More than once I've reached an idea on my own, like "
    "mixture of experts or task arithmetic, only to find it already in the literature. I read that as a signal: my work now is connecting instinct to "
    "research faster, so the original part lands on problems that are still open.",
]
DIRECTION = "Where I'm headed: a research-capable, systems-aware, full-stack AI engineer."


def preface():
    pad, size, lh, gap = 48, 22, 33, 18
    width = W - 2 * pad
    cap_size = 78
    cap, rest = PREFACE[0][0], PREFACE[0][1:]
    cap_w = measure(cap, "serif-md", cap_size) + 14
    first = wrap(rest, "serif", size, width - cap_w)[:2]
    remaining = rest[len(" ".join(first)):].strip()
    y = pad + 26
    out = [text(pad - 2, y + lh - 2, cap, "serif-md", cap_size, BRASS)]
    for i, ln in enumerate(first + wrap(remaining, "serif", size, width)):
        out.append(text(pad + (cap_w if i < 2 else 0), y, ln, "serif", size, IVORY))
        y += lh
    for para in PREFACE[1:]:
        y += gap
        for ln in wrap(para, "serif", size, width):
            out.append(text(pad, y, ln, "serif", size, IVORY))
            y += lh
    y += 20
    out.append(f'<line x1="{pad}" y1="{y - 8}" x2="{pad + 44}" y2="{y - 8}" stroke="{BRASS}"/>')
    y += 26
    out.append(text(pad, y, DIRECTION, "serif-it", 23, BRASS))
    h = int(y + pad - 8)
    save("preface.svg", svg(W, h, plate(h, "\n".join(out)), ["serif", "serif-md", "serif-it"],
                            " ".join(PREFACE) + " " + DIRECTION))


# ─────────────────────────── present tense ───────────────────────────
PRESENT = [
    ("THESIS", "CAEM, Confidence-Aware Episodic Memory: reducing hallucination in LLMs through episodic memory, "
               "confidence estimation and self-improvement."),
    ("NEXT", "An image-processing project, still on the drawing board."),
    ("EXPLORING", "AI engineering and research, and web development end to end."),
    ("PLANNED", "A hobby operating system in C, written from scratch."),
]


def present():
    pad, label_w, size, lh = 48, 172, 21, 29
    width = W - 2 * pad - label_w
    y = 22
    out = []
    for i, (label, line) in enumerate(PRESENT):
        lines = wrap(line, "serif", size, width)
        row_h = 30 + len(lines) * lh
        if i:
            out.append(f'<line x1="{pad}" y1="{y:.1f}" x2="{W - pad}" y2="{y:.1f}" stroke="{HAIR}"/>')
        out.append(text(pad, y + 36, f"{i + 1:02d}", "mono", 10, FAINT, 0.2))
        out.append(text(pad + 34, y + 36, label, "mono", 10, BRASS, 0.26))
        for j, ln in enumerate(lines):
            out.append(text(pad + label_w, y + 38 + j * lh, ln, "serif", size, IVORY))
        y += row_h
    h = int(y + 22)
    alt = " ".join(f"{a}: {b}" for a, b in PRESENT)
    save("present.svg", svg(W, h, plate(h, "\n".join(out)), ["serif", "mono"], alt))


# ─────────────────────────── selected works ───────────────────────────
WORKS = [
    ("caem-thesis", "THESIS · LLMS", "CAEM",
     "Confidence-aware episodic memory with a self-improvement loop. Cuts hallucination in open-domain QA: +20.3% exact match, −29.4% hallucination over the baseline.",
     "PYTHON · PYTORCH · QWEN-2.5 · FAISS · LORA"),
    ("Sam2-sar-Flood-mapping", "PAPER · COMPUTER VISION", "SAM 2 × Radar Floods",
     "Parameter-efficient adaptation of Segment Anything to Sentinel-1 SAR flood mapping. Four PEFT methods, five backbones, one public test set.",
     "PYTORCH LIGHTNING · TRANSFORMERS · PEFT"),
    ("memestack", "FULL STACK · LIVE", "MemeStack",
     "A meme studio and community: canvas editor, template library, collaborations, challenges, groups and moderation, deployed on Vercel.",
     "REACT · MUI · EXPRESS · MONGODB · CLOUDINARY"),
    ("vae-music-clustering", "RESEARCH · GENERATIVE", "VAE Music Clustering",
     "Seven variational autoencoders, from beta-VAE to a multimodal audio + lyrics model, clustering songs across four languages and three genres.",
     "PYTORCH · LIBROSA · SCIKIT-LEARN · UMAP"),
    ("Continual-Learning", "RESEARCH · NLP", "Continual Learning",
     "Elastic weight consolidation versus experience replay for a BERT intent classifier trained domain by domain. Sixteen configurations, twelve metrics.",
     "PYTORCH · TRANSFORMERS · BERT"),
    ("process-manager", "SYSTEMS · C", "Process Manager",
     "A simulated OS process table: concurrent fork, exit, wait and kill across POSIX threads, with zombie reaping, orphan adoption by init and a race-free monitor.",
     "C · PTHREADS · THREADSANITIZER"),
]


def work_card(i, repo, tag, title, desc, stack):
    cw, ch, pad = 440, 268, 30
    out = [
        f'<rect width="{cw}" height="{ch}" fill="{INK}"/>',
        f'<rect x="0.5" y="0.5" width="{cw - 1}" height="{ch - 1}" fill="none" stroke="{HAIR}"/>',
        ticks(0.5, 0.5, cw - 1, ch - 1, 8, BRASS, 7),
        text(pad, 46, f"{i:02d}", "mono", 11, BRASS, 0.2),
        text(pad + 32, 46, tag, "mono", 10.5, MUTED, 0.22),
        text(cw - pad, 48, "↗", "serif", 22, MUTED, anchor="end"),
        text(pad - 1, 98, title, "serif-lt", 34, IVORY),
    ]
    for j, ln in enumerate(wrap(desc, "serif-it", 18.5, cw - 2 * pad)[:4]):
        out.append(text(pad, 132 + j * 24, ln, "serif-it", 18.5, MUTED))
    out.append(f'<line x1="{pad}" y1="{ch - 50}" x2="{cw - pad}" y2="{ch - 50}" stroke="{HAIR}"/>')
    out.append(text(pad, ch - 26, stack, "mono", 10, MUTED, 0.14))
    save(f"work-{i}.svg", svg(cw, ch, "\n".join(out), ["serif", "serif-lt", "serif-it", "mono"],
                              f"{title} — {desc} Stack: {stack.title()}"))


# ─────────────────────────── instruments ───────────────────────────
INSTRUMENTS = [
    ("LANGUAGES", [("python", "Python"), ("c", "C"), ("javascript", "JavaScript"), ("typescript", "TypeScript"),
                   ("php", "PHP"), ("latex", "LaTeX"), ("gnubash", "Bash")]),
    ("MACHINE LEARNING", [("pytorch", "PyTorch"), ("huggingface", "Hugging Face"), ("lightning", "Lightning"),
                          ("scikitlearn", "scikit-learn"), ("pandas", "pandas"), ("numpy", "NumPy"),
                          ("weightsandbiases", "W&B"), ("jupyter", "Jupyter")]),
    ("WEB", [("react", "React"), ("nodedotjs", "Node.js"), ("express", "Express"), ("mongodb", "MongoDB"),
             ("mysql", "MySQL"), ("mui", "MUI"), ("bootstrap", "Bootstrap")]),
    ("TOOLING", [("git", "Git"), ("linux", "Linux"), ("vercel", "Vercel")]),
]


COLOR_ICONS = Path(__file__).parent / "icons-color"
DEVICON_NAMES = {"nodedotjs": "nodejs", "mui": "materialui"}
# Logos with no Devicon original, or whose brand colour vanishes on the dark plate.
FLAT_COLORS = {"huggingface": "#FFD21E", "weightsandbiases": "#FFBE00", "lightning": "#792EE5",
               "gnubash": "#4EAA25", "latex": "#3aa7a7", "express": IVORY, "vercel": IVORY, "pandas": IVORY,
               "mysql": "#4479A1", "linux": "#FCC624"}


def icon_path(name):
    raw = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', raw).group(1)


def icon(name, x, y, size):
    if name not in FLAT_COLORS:
        data = base64.b64encode((COLOR_ICONS / f"{DEVICON_NAMES.get(name, name)}.svg").read_bytes()).decode()
        return (f'<image x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" '
                f'href="data:image/svg+xml;base64,{data}"/>')
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({size / 24})">'
            f'<path d="{icon_path(name)}" fill="{FLAT_COLORS[name]}"/></g>')


def instruments():
    pad, label_w, step, size, row_h = 48, 176, 81, 28, 96
    out = []
    y = pad - 8
    for r, (label, items) in enumerate(INSTRUMENTS):
        if r:
            out.append(f'<line x1="{pad}" y1="{y:.1f}" x2="{W - pad}" y2="{y:.1f}" stroke="{HAIR}"/>')
        out.append(text(pad, y + 50, label, "mono", 10, BRASS, 0.26))
        for k, (slug, name) in enumerate(items):
            x = pad + label_w + k * step
            out.append(icon(slug, x + (step - size) / 2 - 12, y + 22, size))
            out.append(text(x + step / 2 - 12, y + 76, name.upper(), "mono", 9, MUTED, 0.06, "middle"))
        y += row_h
    h = int(y + 8)
    alt = "; ".join(f"{g}: " + ", ".join(n for _, n in items) for g, items in INSTRUMENTS)
    save("instruments.svg", svg(W, h, plate(h, "\n".join(out)), ["mono"], alt))


# ───────────────────────────── margins ─────────────────────────────
MARGINS = [
    ("PLAYING", "Clash Royale, competitively. Also Valorant, PUBG and CS:GO."),
    ("WRITING", "Personal journals, in LaTeX."),
    ("SOMEDAY", "A long list of places to see."),
]


def margins():
    pad = 48
    col = (W - 2 * pad) / len(MARGINS)
    rows = max(len(wrap(line, "serif-it", 21, col - 40)) for _, line in MARGINS)
    h = 86 + (rows - 1) * 26 + 42
    out = []
    for i, (label, line) in enumerate(MARGINS):
        x = pad + i * col
        if i:
            out.append(f'<line x1="{x - 20:.1f}" y1="36" x2="{x - 20:.1f}" y2="{h - 36}" stroke="{HAIR}"/>')
        out.append(text(x, 54, label, "mono", 10.5, BRASS, 0.26))
        for j, ln in enumerate(wrap(line, "serif-it", 21, col - 40)):
            out.append(text(x, 86 + j * 26, ln, "serif-it", 21, IVORY))
    alt = " ".join(f"{a}: {b}" for a, b in MARGINS)
    save("margins.svg", svg(W, h, plate(h, "\n".join(out)), ["serif-it", "mono"], alt))


# ─────────────────────────── correspondence ───────────────────────────
LINKS = [
    ("email", "EMAIL", "aksangoni.alif@gmail.com"),
    ("github", "GITHUB", "@aksaN000"),
    ("location", "BASED IN", "Dhaka, Bangladesh"),
]


def pill(slug, label, value):
    pw, ph = 292, 76
    body = f"""
<rect width="{pw}" height="{ph}" fill="{INK}"/>
<rect x="0.5" y="0.5" width="{pw - 1}" height="{ph - 1}" fill="none" stroke="{HAIR}"/>
<circle cx="24" cy="29" r="2.4" fill="{BRASS}"/>
{text(36, 33, label, "mono", 10.5, BRASS, 0.26)}
{text(22, 58, value, "serif", 21, IVORY)}
{text(pw - 20, 34, "↗" if slug != "location" else "", "serif", 18, MUTED, anchor="end")}
"""
    save(f"link-{slug}.svg", svg(pw, ph, body, ["serif", "mono"], f"{label.title()}: {value}"))


# ───────────────────────────── colophon ─────────────────────────────
def colophon():
    h = 132
    body = plate(h, f"""
<line x1="{W / 2 - 30}" y1="38" x2="{W / 2 + 30}" y2="38" stroke="{BRASS}"/>
{text(W / 2, 74, "Set in Cormorant Garamond and JetBrains Mono. Composed in Dhaka.", "serif-it", 19, MUTED, anchor="middle")}
{text(W / 2, 102, "MD. AKSAN GONY ALIF · MMXXVI", "mono", 10, FAINT, 0.3, "middle")}
""")
    save("colophon.svg", svg(W, h, body, ["serif-it", "mono"], "Colophon"))


if __name__ == "__main__":
    banner()
    for n, (num, title, cap) in enumerate(CHAPTERS, 1):
        chapter(num, title, cap, n)
    preface()
    present()
    for i, w in enumerate(WORKS, 1):
        work_card(i, *w)
    instruments()
    margins()
    for link in LINKS:
        pill(*link)
    colophon()
