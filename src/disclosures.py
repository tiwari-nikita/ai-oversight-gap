"""
Step 2 - Companies are telling investors about AI. Are they telling them how it is governed?

Input: data/raw/sec_10k_hits.csv from fetch_sec.py - every 10-K filing (2019 - Sept 2026)
matching three EDGAR full-text searches, collapsed to one row per matching document:
  all_10k       "risk factors"            -> denominator (effectively every 10-K)
  ai_mention    "artificial intelligence"
  ai_governance explicit governance language: "AI governance", "responsible AI",
                "oversight of artificial intelligence", "AI oversight" and close variants

Everything is counted in unique FILINGS (accession numbers), not documents.

WHAT THIS MEASURES
Phrase matching finds explicit language. A company can govern AI without using these words,
and a company can use the words without governing anything. So this is a measure of what
companies *disclose*, which is exactly what investors and regulators can see.
"""
import pathlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "output"

hits = pd.read_csv(RAW / "sec_10k_hits.csv", dtype={"sic": str, "cik": str})
sets = {(q, y): set(g["adsh"]) for (q, y), g in hits.groupby(["query", "year"])}
years = sorted(hits["year"].unique())

rows = []
for y in years:
    base = sets.get(("all_10k", y), set())
    ai = sets.get(("ai_mention", y), set())
    gov = sets.get(("ai_governance", y), set())
    rows.append({
        "year": int(y),
        "filings": len(base),
        "ai_mention_filings": len(ai),
        "governance_filings": len(gov),
        "ai_mention_pct": len(ai) / len(base) * 100,
        "governance_pct": len(gov) / len(base) * 100,
        "governance_pct_of_ai_filers": len(gov & ai) / len(ai) * 100 if ai else np.nan,
        "ai_filings_in_denominator_pct": len(ai & base) / len(ai) * 100 if ai else np.nan,
    })
trend = pd.DataFrame(rows)
trend["mention_to_governance_ratio"] = trend["ai_mention_filings"] / trend["governance_filings"].replace(0, np.nan)
trend.round(3).to_csv(OUT / "disclosure_trend.csv", index=False)

# ---------------------------------------------------------------------------
# Where does governance language sit - in the 10-K itself, or only in an exhibit
# (codes of conduct, policies) attached to it?
# ---------------------------------------------------------------------------
g = hits[hits["query"] == "ai_governance"].copy()
g["in_body"] = g["file_type"].eq("10-K")
loc = g.groupby("adsh")["in_body"].any()
gov_rows = []
for y in years:
    ids = sets.get(("ai_governance", y), set())
    if not ids:
        continue
    body = int(loc.reindex(list(ids)).fillna(False).sum())
    gov_rows.append({"year": int(y), "governance_filings": len(ids), "in_10k_body": body,
                     "exhibit_only": len(ids) - body, "exhibit_only_pct": (len(ids) - body) / len(ids) * 100})
location = pd.DataFrame(gov_rows)
location.round(2).to_csv(OUT / "governance_location.csv", index=False)

# ---------------------------------------------------------------------------
# By sector (SIC division), pooled over the two most recent filing years
# ---------------------------------------------------------------------------
def division(sic):
    try:
        s = int(str(sic)[:2])
    except ValueError:
        return "Unknown"
    if 1 <= s <= 9:
        return "Agriculture"
    if 10 <= s <= 14:
        return "Mining & energy"
    if 15 <= s <= 17:
        return "Construction"
    if 20 <= s <= 39:
        return "Manufacturing"
    if 40 <= s <= 49:
        return "Transport, comms & utilities"
    if 50 <= s <= 59:
        return "Wholesale & retail"
    if 60 <= s <= 67:
        return "Finance, insurance & real estate"
    if 70 <= s <= 89:
        return "Services (incl. software)"
    return "Other"


recent = [y for y in years if y >= years[-1] - 1]
first = hits.drop_duplicates(["query", "year", "adsh"])
first = first[first["year"].isin(recent)].copy()
first["division"] = first["sic"].map(division)
by = first.groupby(["division", "query"])["adsh"].nunique().unstack(fill_value=0)
by = by[by["all_10k"] >= 200]
by["ai_mention_pct"] = by["ai_mention"] / by["all_10k"] * 100
by["governance_pct"] = by["ai_governance"] / by["all_10k"] * 100
by = by.sort_values("ai_mention_pct", ascending=False)
by.round(2).to_csv(OUT / "disclosure_by_sector.csv")

pd.set_option("display.width", 200)
print("DISCLOSURE TREND (unique 10-K filings by filing year; 2026 runs to 26 Sept)")
print(trend.round(1).to_string(index=False))
print()
print("WHERE GOVERNANCE LANGUAGE APPEARS")
print(location.round(1).to_string(index=False))
print()
print("BY SECTOR, filing years {}".format(recent))
print(by[["all_10k", "ai_mention_pct", "governance_pct"]].round(1).to_string())
