"""Charts for the AI oversight gap analysis."""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": BASELINE,
                     "axes.labelcolor": INK2, "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.titlesize": 13, "axes.titleweight": "bold", "font.size": 10})


def style(ax, xgrid=False):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(axis="x" if xgrid else "y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def titles(ax, t, sub):
    ax.set_title(t, loc="left", pad=32)
    ax.text(0, 1.03, sub, transform=ax.transAxes, color=MUTED, fontsize=9, va="bottom")


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print("wrote", name)


# 1. The disclosure gap
tr = pd.read_csv(OUT / "disclosure_trend.csv")
fig, ax = plt.subplots(figsize=(9, 4.8))
x = tr["year"].astype(str).where(tr["year"] < 2026, "2026*")
ax.plot(x, tr["ai_mention_pct"], color=BLUE, marker="o", linewidth=2.4, markersize=7, label="Mentions AI")
ax.plot(x, tr["governance_pct"], color=ORANGE, marker="o", linewidth=2.4, markersize=7,
        label="Uses explicit AI-governance language")
for xi, a, g in zip(x, tr["ai_mention_pct"], tr["governance_pct"]):
    if xi in ("2019", "2025", "2026*"):
        ax.text(xi, a + 2.5, "{:.0f}%".format(a), ha="center", color=INK, fontweight="bold")
        ax.text(xi, g + 2.5, "{:.1f}%".format(g), ha="center", color=INK, fontweight="bold")
style(ax)
ax.set_ylim(0, 70)
ax.set_ylabel("Share of 10-K filings (%)")
r25 = tr.set_index("year").loc[2025]
titles(ax, "Half of annual reports now talk about AI. Few say how it is governed.",
       "10-K filings by filing year. 2025: {:.0f} mentions of AI for every filing with governance language. *2026 to 26 Sept.".format(
           r25["mention_to_governance_ratio"]))
ax.legend(frameon=False, loc="upper left", labelcolor=INK2)
ax.tick_params(axis="x", labelcolor=INK2)
save(fig, "01_disclosure_gap.png")

# 2. Incidents per year
py = pd.read_csv(OUT / "incidents_per_year.csv")
py = py[py["year"] >= 2015]
fig, ax = plt.subplots(figsize=(9, 4.4))
cols = [MUTED if y < 2023 else BLUE for y in py["year"]]
cols[-1] = "#86b6ef"
ax.bar(py["year"].astype(str), py["incidents"], color=cols, width=0.62, zorder=3)
style(ax)
ax.set_ylabel("Reported AI incidents")
titles(ax, "Reported AI incidents have quadrupled since 2022",
       "AI Incident Database, by year of harm. 2026 is partial (export of 21 Sept). Counts reflect reporting, not true prevalence.")
for i, v in enumerate(py["incidents"]):
    ax.text(i, v + 6, str(v), ha="center", color=INK, fontsize=9, fontweight="bold")
ax.tick_params(axis="x", labelcolor=INK2)
save(fig, "02_incidents_per_year.png")

# 3. What goes wrong, before vs after 2023
dom = pd.read_csv(OUT / "domain_mix_by_era.csv", index_col=0)
dom = dom.loc[dom.max(axis=1) >= 3]
order = dom.sort_values("2023-2026 (generative AI era)").index
fig, ax = plt.subplots(figsize=(9, 4.8))
y = np.arange(len(order))
before = dom.loc[order, "Before 2023"]
after = dom.loc[order, "2023-2026 (generative AI era)"]
ax.hlines(y, before, after, color=BASELINE, linewidth=2.5, zorder=2)
ax.scatter(before, y, s=80, color=MUTED, zorder=3, label="Before 2023")
ax.scatter(after, y, s=80, color=ORANGE, zorder=3, label="2023–2026")
for yi, b, a in zip(y, before, after):
    ax.text(a + (1.2 if a >= b else -1.2), yi, "{:.0f}%".format(a), va="center",
            ha="left" if a >= b else "right", color=INK, fontweight="bold", fontsize=9.5)
style(ax, xgrid=True)
ax.set_yticks(y)
ax.set_yticklabels(order, color=INK2)
ax.set_xlim(0, 62)
ax.set_xlabel("Share of classified incidents (%)")
titles(ax, "Since generative AI, the main problem is people misusing AI, not AI failing",
       "MIT AI Risk taxonomy domains. Intentional harm rose from 27% to 61% of incidents.")
ax.legend(frameon=False, loc="lower right", labelcolor=INK2)
save(fig, "03_domain_shift.png")

# 4. The safeguard roadmap
sg = pd.read_csv(OUT / "safeguard_ranking.csv").head(8).iloc[::-1]
fig, ax = plt.subplots(figsize=(9, 4.8))
cols = [ORANGE if i >= len(sg) - 3 else BLUE for i in range(len(sg))]
ax.barh(sg["control_family"], sg["share_pct"], color=cols, height=0.6, zorder=3)
style(ax, xgrid=True)
ax.set_xlim(0, 45)
ax.set_xlabel("Share of classified incidents each safeguard addresses (%)")
top3 = pd.read_csv(OUT / "safeguard_ranking.csv").head(3)["cumulative_pct"].iloc[-1]
titles(ax, "Three safeguards address {:.0f}% of documented AI harm".format(top3),
       "MIT risk subdomains mapped to NIST AI RMF control families (mapping published in full). Orange = top 3.")
for i, (v, lif) in enumerate(zip(sg["share_pct"], sg["lifecycle"])):
    ax.text(v + 0.5, i, "{:.0f}%  ·  {}".format(v, lif.lower()), va="center", color=INK, fontsize=9)
ax.tick_params(axis="y", labelcolor=INK2)
save(fig, "04_safeguard_roadmap.png")

# 5. Sector view
sec = pd.read_csv(OUT / "disclosure_by_sector.csv", index_col=0)
sec = sec.drop(index=[i for i in sec.index if i == "Unknown"]).sort_values("ai_mention_pct")
fig, ax = plt.subplots(figsize=(9, 4.6))
yy = np.arange(len(sec))
ax.barh(yy + 0.2, sec["ai_mention_pct"], height=0.38, color=BLUE, zorder=3, label="Mentions AI")
ax.barh(yy - 0.2, sec["governance_pct"], height=0.38, color=ORANGE, zorder=3, label="Governance language")
for yi, a, g in zip(yy, sec["ai_mention_pct"], sec["governance_pct"]):
    ax.text(a + 0.8, yi + 0.2, "{:.0f}%".format(a), va="center", color=INK, fontsize=9)
    ax.text(g + 0.8, yi - 0.2, "{:.1f}%".format(g), va="center", color=INK, fontsize=9)
style(ax, xgrid=True)
ax.set_yticks(yy)
ax.set_yticklabels(sec.index, color=INK2)
ax.set_xlim(0, 85)
ax.set_xlabel("Share of 10-K filings, 2025–2026 (%)")
titles(ax, "Finance mentions AI in 38% of filings but describes governing it in 2%",
       "10-K filings by SIC division, filing years 2025 and 2026 pooled")
ax.legend(frameon=False, loc="lower right", labelcolor=INK2)
save(fig, "05_sectors.png")
