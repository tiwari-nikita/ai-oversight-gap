"""
Step 0b - Count 10-K filings that mention AI, and that use explicit AI-governance language,
via SEC EDGAR full-text search (efts.sec.gov), 2019 - 2026.

WHY FILINGS, NOT HITS
EDGAR full-text search returns one hit per matching *document*, and a 10-K filing bundles
many documents (the report plus exhibits such as codes of conduct). Counting hits would
double-count filings and mix exhibits in silently. Every hit is therefore collapsed to its
filing (accession number, "adsh"), and the document type is kept so governance language in
the report body can be told apart from language that only appears in an exhibit.

DENOMINATOR
All 10-K filings containing the phrase "risk factors" - effectively every 10-K, since the
form requires an Item 1A heading even when the answer is "not applicable".

SEC fair-access policy requires a declared User-Agent with contact details and at most 10
requests per second; this script identifies itself and stays well under that rate.
"""
import csv
import json
import os
import pathlib
import time
import urllib.parse
import urllib.request

RAW = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"
OUT = RAW / "sec_10k_hits.csv"
# SEC fair-access policy requires a User-Agent naming a person and a contact address.
# Supply your own, e.g.  SEC_USER_AGENT="Jane Doe jane@example.com"  (only needed to
# re-query EDGAR; the extract used here is already in data/raw/).
UA = os.environ.get("SEC_USER_AGENT", "")
YEARS = range(2019, 2027)
END_2026 = "2026-09-26"

QUERIES = {
    "all_10k": '"risk factors"',
    "ai_mention": '"artificial intelligence"',
    "ai_governance": ('"AI governance" OR "artificial intelligence governance" OR '
                      '"governance of artificial intelligence" OR "responsible AI" OR '
                      '"responsible artificial intelligence" OR "oversight of artificial intelligence" OR '
                      '"oversight of AI" OR "AI oversight"'),
}


def fetch(query, year):
    start, end = "{}-01-01".format(year), (END_2026 if year == 2026 else "{}-12-31".format(year))
    rows, offset, total = [], 0, None
    while True:
        qs = urllib.parse.urlencode({"q": query, "forms": "10-K", "dateRange": "custom",
                                     "startdt": start, "enddt": end, "from": offset})
        req = urllib.request.Request("https://efts.sec.gov/LATEST/search-index?" + qs,
                                     headers={"User-Agent": UA})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    d = json.load(r)
                break
            except Exception:
                time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError("SEC request failed: {} {} offset {}".format(query[:30], year, offset))
        hits = d["hits"]["hits"]
        total = d["hits"]["total"]["value"]
        for h in hits:
            s = h["_source"]
            rows.append({"year": year, "adsh": s.get("adsh"), "cik": (s.get("ciks") or [""])[0],
                         "file_type": s.get("file_type", ""), "sic": (s.get("sics") or [""])[0]})
        offset += len(hits)
        if not hits or offset >= total or offset >= 10000:
            break
        time.sleep(0.2)
    return rows, total


if OUT.exists():
    print("exists:", OUT.name)
elif not UA:
    raise SystemExit("Set SEC_USER_AGENT to 'Your Name your@email' to query SEC EDGAR "
                     "(required by the SEC's fair-access policy).")
else:
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["query", "year", "adsh", "cik", "file_type", "sic"])
        w.writeheader()
        for name, q in QUERIES.items():
            for y in YEARS:
                rows, total = fetch(q, y)
                for r in rows:
                    w.writerow(dict(r, query=name))
                print("  {:<14} {}  documents {:>6,}  filings {:>6,}".format(
                    name, y, total, len({r["adsh"] for r in rows})))
