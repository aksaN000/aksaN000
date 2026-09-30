"""Renders assets/ledger.svg: contribution calendar, streaks and language mix, from the GitHub GraphQL API."""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

from theme import BRASS, FAINT, HAIR, INK, IVORY, MUTED, measure, svg, text

USER = os.environ.get("GH_USER", "aksaN000")
TOKEN = os.environ["GH_TOKEN"]
OUT = Path(__file__).resolve().parent.parent / "assets" / "ledger.svg"
W = 900
IGNORED_LANGS = {"Jupyter Notebook", "TeX", "Perl", "Roff", "Hack", "PowerShell", "Shell",
                 "Batchfile", "Makefile", "Dockerfile", "Procfile"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
  }
}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    return payload["data"]["user"]


def streaks(days):
    today = dt.date.today().isoformat()
    counts = [d["contributionCount"] for d in days if d["date"] <= today]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def languages(repos):
    totals = {}
    for node in repos["nodes"]:
        for e in node["languages"]["edges"]:
            name = e["node"]["name"]
            if name not in IGNORED_LANGS:
                totals[name] = totals.get(name, 0) + e["size"]
    grand = sum(totals.values()) or 1
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:5]
    return [(n, s / grand) for n, s in top]


def render(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, longest = streaks(days)
    langs = languages(user["repositories"])

    pad = 48
    out = [f'<rect width="{W}" height="0" fill="{INK}"/>']

    figures = [
        (f"{cal['totalContributions']:,}", "CONTRIBUTIONS, 12 MO"),
        (f"{current}", "CURRENT RUN, DAYS"),
        (f"{longest}", "LONGEST RUN, DAYS"),
        (f"{user['repositories']['totalCount']}", "PUBLIC REPOSITORIES"),
    ]
    col = (W - 2 * pad) / 4
    for i, (num, label) in enumerate(figures):
        x = pad + i * col
        if i:
            out.append(f'<line x1="{x - 18:.1f}" y1="44" x2="{x - 18:.1f}" y2="98" stroke="{HAIR}"/>')
        out.append(text(x, 82, num, "serif", 46, IVORY))
        out.append(text(x + 2, 104, label, "mono", 8.5, MUTED, 0.22))

    top = 150
    step = (W - 2 * pad) / len(weeks)
    r = min(step * 0.34, 4.2)
    nonzero = sorted(d["contributionCount"] for d in days if d["contributionCount"])
    q = [nonzero[int(len(nonzero) * f)] if nonzero else 1 for f in (0.25, 0.5, 0.75)]

    def level(c):
        if not c:
            return None
        return 0.3 if c <= q[0] else 0.5 if c <= q[1] else 0.75 if c <= q[2] else 1.0

    last_month = None
    for wi, w in enumerate(weeks):
        x = pad + wi * step + step / 2
        month = w["contributionDays"][-1]["date"][5:7]
        starts = any(d["date"].endswith("-01") for d in w["contributionDays"])
        if starts and month != last_month and wi < len(weeks) - 2:
            name = dt.date(2000, int(month), 1).strftime("%b").upper()
            out.append(text(x - r, top - 12, name, "mono", 8, FAINT, 0.16))
            last_month = month
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).weekday()
            row = (wd + 1) % 7
            y = top + row * step + step / 2
            lv = level(d["contributionCount"])
            if lv is None:
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.45:.2f}" fill="{FAINT}" opacity="0.55"/>')
            else:
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{BRASS}" opacity="{lv}"/>')

    y = top + 7 * step + 34
    out.append(f'<line x1="{pad}" y1="{y:.1f}" x2="{W - pad}" y2="{y:.1f}" stroke="{HAIR}"/>')
    y += 34
    out.append(text(pad, y, "LANGUAGE MIX", "mono", 9.5, BRASS, 0.26))
    bar_x, bar_w = pad + 176, W - 2 * pad - 176
    shades = [1.0, 0.72, 0.5, 0.34, 0.22]
    x = bar_x
    for (name, share), op in zip(langs, shades):
        seg = bar_w * share / sum(s for _, s in langs)
        out.append(f'<rect x="{x:.1f}" y="{y - 8}" width="{max(seg - 2, 1):.1f}" height="3" fill="{BRASS}" opacity="{op}"/>')
        x += seg
    y += 26
    x = bar_x
    for (name, share), op in zip(langs, shades):
        label = f"{name.upper()} {share * 100:.0f}%"
        out.append(f'<circle cx="{x + 3}" cy="{y - 3}" r="2.6" fill="{BRASS}" opacity="{op}"/>')
        out.append(text(x + 12, y, label, "mono", 8.5, MUTED, 0.14))
        x += measure(label, "mono", 8.5, 0.14) + 34

    h = int(y + 38)
    out[0] = (f'<rect width="{W}" height="{h}" fill="{INK}"/>'
              f'<rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" fill="none" stroke="{HAIR}"/>')
    stamp = dt.datetime.now(dt.timezone.utc).strftime("UPDATED %d %b %Y").upper()
    out.append(text(W - pad, h - 16, stamp, "mono", 7.5, FAINT, 0.2, "end"))
    alt = (f"{cal['totalContributions']} contributions in the last year; current streak {current} days; "
           f"longest streak {longest} days; top languages: " + ", ".join(f"{n} {s:.0%}" for n, s in langs))
    OUT.write_text(svg(W, h, "\n".join(out), ["serif", "mono"], alt), encoding="utf-8")
    print(alt)


if __name__ == "__main__":
    render(fetch())
