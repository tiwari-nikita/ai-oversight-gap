"""Every figure published in MEMO.md / README.md, asserted against the generated outputs.
Run: python -m pytest tests/ -v   or   python tests/test_claims.py"""
import hashlib
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT, RAW = ROOT / "output", ROOT / "data" / "raw"
HASHES = {
    "AIID_Excel_Export-20260921.xlsx": "d8c26069f47363eb4adad00c381f8f80877f06e784050cd4bff900ee2159413c",
    "sec_10k_hits.csv": "21d2db13423cda905ac359b5fd38802ff561e3d480d97abfcb0c8020881e4f2c",
}


def near(a, b, tol, label):
    assert abs(a - b) <= tol, "{}: expected {} +/- {}, got {}".format(label, b, tol, a)


def head():
    return pd.read_csv(OUT / "incident_headline.csv").iloc[0]


def trend():
    return pd.read_csv(OUT / "disclosure_trend.csv").set_index("year")


def test_raw_data_unmodified():
    """AIID export and SEC extract match the SHA-256 recorded at download."""
    for name, h in HASHES.items():
        assert hashlib.sha256((RAW / name).read_bytes()).hexdigest() == h, name + " changed"


def test_incident_counts():
    """CLAIM: 1,689 incidents; 1,496 (89%) carry MIT AI Risk classification."""
    h = head()
    assert int(h["incidents_total"]) == 1689 and int(h["incidents_labeled"]) == 1496


def test_post_deployment():
    """CLAIM: 98% of classified harms arose after deployment (1,460 vs 27 before)."""
    h = head()
    near(h["post_deployment_pct"], 97.6, 0.1, "post")
    assert int(h["post_deployment_n"]) == 1460 and int(h["pre_deployment_n"]) == 27


def test_growth():
    """CLAIM: reported incidents roughly quadrupled from 2022 (108) to 2025 (452)."""
    p = pd.read_csv(OUT / "incidents_per_year.csv").set_index("year")["incidents"]
    assert p[2022] == 108 and p[2025] == 452
    near(p[2025] / p[2022], 4.2, 0.1, "growth multiple")


def test_domain_shift():
    """CLAIM: misuse rose from 11% to 52% of incidents; AI failures fell from 39% to 11%."""
    d = pd.read_csv(OUT / "domain_mix_by_era.csv", index_col=0)
    near(d.loc["Malicious Actors & Misuse", "Before 2023"], 11.4, 0.1, "misuse before")
    near(d.loc["Malicious Actors & Misuse", "2023-2026 (generative AI era)"], 52.1, 0.1, "misuse after")
    near(d.loc["AI system safety, failures, and limitations", "Before 2023"], 38.9, 0.1, "failures before")
    near(d.loc["AI system safety, failures, and limitations", "2023-2026 (generative AI era)"], 11.2, 0.1, "failures after")


def test_intent_and_fraud():
    """CLAIM: intentional harm rose from 27% to 61%; fraud & scams is the top category overall and since 2023."""
    e = pd.read_csv(OUT / "incident_extra.csv").iloc[0]
    near(e["intentional_pct_before_2023"], 27.0, 0.1, "intent before")
    near(e["intentional_pct_2023_2026"], 61.1, 0.1, "intent after")
    assert e["top_subdomain"] == "Fraud, scams, and targeted manipulation"
    assert e["top_subdomain_2023_2026"] == "Fraud, scams, and targeted manipulation"


def test_pre_launch_controls_small():
    """CLAIM: safeguards that operate only before launch address under 2% of incidents."""
    assert pd.read_csv(OUT / "incident_extra.csv").iloc[0]["pre_deployment_only_controls_pct"] < 2.0


def test_top_three_safeguards():
    """CLAIM: misuse monitoring (38%), reliability testing (20%) and output review (13%) cover 71%."""
    s = pd.read_csv(OUT / "safeguard_ranking.csv")
    assert list(s["control_family"][:3]) == ["Misuse and abuse monitoring",
                                             "Reliability testing and performance monitoring",
                                             "Output accuracy controls and human review"]
    near(s["cumulative_pct"].iloc[2], 71.3, 0.1, "top 3")
    near(s["share_2023_2026_pct"].iloc[0], 52.0, 0.1, "misuse monitoring, genAI era")


def test_every_subdomain_mapped():
    """Integrity: every MIT subdomain in the data maps to a safeguard (none silently dropped)."""
    assert int(head()["unmapped_subdomains"]) == 0


def test_disclosure_gap():
    """CLAIM: 2025 - 49% of 10-Ks mention AI, 1.7% use governance language (28 to 1)."""
    t = trend().loc[2025]
    near(t["ai_mention_pct"], 49.3, 0.1, "mention")
    near(t["governance_pct"], 1.7, 0.05, "governance")
    near(t["mention_to_governance_ratio"], 28.4, 0.2, "ratio")


def test_gap_closing():
    """CLAIM: 2026 to date - 61% mention AI, 5.3% governance (11 to 1); 6% mentioned AI in 2019."""
    t = trend()
    near(t.loc[2026, "ai_mention_pct"], 60.7, 0.1, "2026 mention")
    near(t.loc[2026, "governance_pct"], 5.3, 0.05, "2026 governance")
    near(t.loc[2026, "mention_to_governance_ratio"], 11.4, 0.2, "2026 ratio")
    near(t.loc[2019, "ai_mention_pct"], 6.3, 0.1, "2019 mention")


def test_denominator_sound():
    """Integrity: 98% of AI-mentioning filings fall inside the 'risk factors' denominator."""
    assert (trend()["ai_filings_in_denominator_pct"] > 97).all()


def test_governance_in_body():
    """CLAIM: 96% of 2025 governance language sits in the 10-K body, not only in exhibits."""
    loc = pd.read_csv(OUT / "governance_location.csv").set_index("year")
    near(100 - loc.loc[2025, "exhibit_only_pct"], 95.7, 0.1, "body share")


def test_sectors():
    """CLAIM: finance mentions AI in 38% of filings, governance language in 2%; services 8%."""
    s = pd.read_csv(OUT / "disclosure_by_sector.csv", index_col=0)
    near(s.loc["Finance, insurance & real estate", "ai_mention_pct"], 37.6, 0.1, "finance mention")
    near(s.loc["Finance, insurance & real estate", "governance_pct"], 2.1, 0.1, "finance gov")
    near(s.loc["Services (incl. software)", "governance_pct"], 8.4, 0.1, "services gov")


def _main():
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    bad = 0
    for n, f in tests:
        try:
            f()
            print("  PASS  {:<30} {}".format(n, (f.__doc__ or "").strip().splitlines()[0]))
        except AssertionError as e:
            bad += 1
            print("  FAIL  {:<30} {}".format(n, e))
    print("\n{} passed, {} failed".format(len(tests) - bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(_main())
