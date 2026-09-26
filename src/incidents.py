"""
Step 1 - What actually goes wrong with deployed AI, and which safeguards would address it?

Source: AI Incident Database (AIID) export of 21 Sept 2026 - 1,689 incidents. 89% carry
expert classification under the MIT AI Risk Repository taxonomy (risk domain and subdomain,
who caused it, intent, and whether the harm arose before or after deployment). Those labels
are used as-is: this project does not re-classify incidents with its own model.

SAFEGUARD MAPPING
Each MIT risk subdomain is mapped to the control family that most directly prevents or
detects it, using the categories of the NIST AI Risk Management Framework (AI 100-1) and its
Generative AI Profile (AI 600-1). The mapping is a judgement call, published in full in
output/safeguard_mapping.csv so it can be challenged line by line.

CAVEAT THAT GOVERNS EVERY NUMBER
AIID records incidents that were reported publicly. It measures what surfaced in the press,
not the true rate of AI harm. Counts rise partly because reporting and attention rose.
"""
import pathlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "output"
SRC = RAW / "AIID_Excel_Export-20260921.xlsx"

df = pd.read_excel(SRC, sheet_name="Incidents", header=2)
lab = df[df["Risk Domain"].notna()].copy()

# (control family, where in the lifecycle it operates, NIST AI RMF reference)
MAP = {
    "Fraud, scams, and targeted manipulation": ("Misuse and abuse monitoring", "Post-deployment", "MANAGE 4.1; GenAI Profile misuse"),
    "Disinformation, surveillance, and influence at scale": ("Misuse and abuse monitoring", "Post-deployment", "MANAGE 4.1; GenAI Profile information integrity"),
    "Cyberattacks, weapon development or use, and mass harm": ("Misuse and abuse monitoring", "Post-deployment", "MANAGE 4.1; GenAI Profile CBRN / cyber"),
    "Lack of capability or robustness": ("Reliability testing and performance monitoring", "Both", "MEASURE 2.4, 2.5"),
    "False or misleading information": ("Output accuracy controls and human review", "Post-deployment", "MEASURE 2.5; GenAI Profile confabulation"),
    "Pollution of information ecosystem and loss of consensus reality": ("Output accuracy controls and human review", "Post-deployment", "GenAI Profile information integrity"),
    "Unfair discrimination and misrepresentation": ("Bias and fairness evaluation", "Both", "MEASURE 2.11"),
    "Unequal performance across groups": ("Bias and fairness evaluation", "Both", "MEASURE 2.11"),
    "Exposure to toxic content": ("Content safety filtering", "Post-deployment", "MEASURE 2.6; GenAI Profile harmful content"),
    "Compromise of privacy by obtaining, leaking or correctly inferring sensitive information": ("Privacy protection", "Both", "MEASURE 2.10; GenAI Profile data privacy"),
    "AI system security vulnerabilities and attacks": ("Security testing and red-teaming", "Both", "MEASURE 2.7"),
    "Overreliance and unsafe use": ("Human oversight and user guidance", "Post-deployment", "GOVERN 3.2; MAP 3.5"),
    "Loss of human agency and autonomy": ("Human oversight and user guidance", "Post-deployment", "GOVERN 3.2; MAP 3.5"),
    "Lack of transparency or interpretability": ("Transparency and documentation", "Pre-deployment", "MEASURE 2.8, 2.9"),
    "Governance failure": ("Accountability and governance structure", "Pre-deployment", "GOVERN 1, 2"),
    "AI pursuing its own goals in conflict with human goals or values": ("Security testing and red-teaming", "Pre-deployment", "MEASURE 2.6, 2.7"),
    "Increased inequality and decline in employment quality": ("Impact assessment", "Pre-deployment", "MAP 5.1"),
    "Power centralization and unfair distribution of benefits": ("Impact assessment", "Pre-deployment", "MAP 5.1"),
    "Economic and cultural devaluation of human effort": ("Impact assessment", "Pre-deployment", "MAP 5.1"),
    "Competitive dynamics": ("Impact assessment", "Pre-deployment", "MAP 5.1"),
    "Environmental harm": ("Impact assessment", "Pre-deployment", "MAP 5.1; MEASURE 2.12"),
}
mapping = pd.DataFrame([{"mit_subdomain": k, "control_family": v[0], "lifecycle": v[1], "nist_ai_rmf": v[2]}
                        for k, v in MAP.items()])
mapping.to_csv(OUT / "safeguard_mapping.csv", index=False)
unmapped = sorted(set(lab["Risk Subdomain"].dropna()) - set(MAP))

lab["control_family"] = lab["Risk Subdomain"].map({k: v[0] for k, v in MAP.items()})
lab["era"] = np.where(lab["year"] >= 2023, "2023-2026 (generative AI era)", "Before 2023")

# ---------------------------------------------------------------------------
# Headline shares
# ---------------------------------------------------------------------------
n_lab = len(lab)
timing = lab["Timing"].value_counts()
resp = lab["Responsible Entity"].value_counts()
intent = lab["Intent"].value_counts()
head = pd.DataFrame([{
    "incidents_total": len(df), "incidents_labeled": n_lab, "labeled_pct": n_lab / len(df) * 100,
    "post_deployment_pct": timing.get("Post-deployment", 0) / n_lab * 100,
    "pre_deployment_pct": timing.get("Pre-deployment", 0) / n_lab * 100,
    "post_deployment_n": int(timing.get("Post-deployment", 0)),
    "pre_deployment_n": int(timing.get("Pre-deployment", 0)),
    "caused_by_ai_pct": resp.get("AI", 0) / n_lab * 100,
    "caused_by_human_pct": resp.get("Human", 0) / n_lab * 100,
    "intentional_pct": intent.get("Intentional", 0) / n_lab * 100,
    "unintentional_pct": intent.get("Unintentional", 0) / n_lab * 100,
    "unmapped_subdomains": len(unmapped),
}])
head.round(2).to_csv(OUT / "incident_headline.csv", index=False)

# ---------------------------------------------------------------------------
# Growth (2026 is partial: the export runs to 21 Sept 2026)
# ---------------------------------------------------------------------------
per_year = df[df["year"].between(2015, 2026)].groupby("year").size().rename("incidents").reset_index()
per_year.to_csv(OUT / "incidents_per_year.csv", index=False)

# ---------------------------------------------------------------------------
# Domain mix by era
# ---------------------------------------------------------------------------
dom = (lab.groupby(["era", "Risk Domain"]).size().unstack(0).fillna(0))
dom_pct = dom / dom.sum() * 100
dom_pct = dom_pct.sort_values("2023-2026 (generative AI era)", ascending=False)
dom_pct.round(2).to_csv(OUT / "domain_mix_by_era.csv")
era_n = lab["era"].value_counts()
intent_era = lab.groupby("era")["Intent"].apply(lambda s: (s == "Intentional").mean() * 100)

# ---------------------------------------------------------------------------
# Safeguard ranking: share of labeled incidents each control family addresses
# ---------------------------------------------------------------------------
ctrl = (lab.groupby("control_family").size().sort_values(ascending=False) / n_lab * 100).rename("share_pct")
ctrl = ctrl.reset_index()
ctrl["cumulative_pct"] = ctrl["share_pct"].cumsum()
# lifecycle is a property of the control family, stated once (a per-row lookup would let
# the last subdomain listed overwrite the others)
FAMILY_LIFECYCLE = {
    "Misuse and abuse monitoring": "Post-deployment",
    "Reliability testing and performance monitoring": "Both",
    "Output accuracy controls and human review": "Post-deployment",
    "Bias and fairness evaluation": "Both",
    "Content safety filtering": "Post-deployment",
    "Privacy protection": "Both",
    "Human oversight and user guidance": "Post-deployment",
    "Security testing and red-teaming": "Both",
    "Impact assessment": "Pre-deployment",
    "Transparency and documentation": "Pre-deployment",
    "Accountability and governance structure": "Pre-deployment",
}
ctrl["lifecycle"] = ctrl["control_family"].map(FAMILY_LIFECYCLE)
ctrl["share_2023_2026_pct"] = ctrl["control_family"].map(
    lab[lab["era"].str.startswith("2023")].groupby("control_family").size() /
    (lab["era"].str.startswith("2023")).sum() * 100).fillna(0)
ctrl.round(2).to_csv(OUT / "safeguard_ranking.csv", index=False)

extra = pd.DataFrame([{
    "intentional_pct_before_2023": intent_era.get("Before 2023"),
    "intentional_pct_2023_2026": intent_era.get("2023-2026 (generative AI era)"),
    "top_subdomain": lab["Risk Subdomain"].value_counts().index[0],
    "top_subdomain_n": int(lab["Risk Subdomain"].value_counts().iloc[0]),
    "top_subdomain_2023_2026": lab[lab["era"].str.startswith("2023")]["Risk Subdomain"].value_counts().index[0],
    "pre_deployment_only_controls_pct": float(ctrl.loc[ctrl["lifecycle"] == "Pre-deployment", "share_pct"].sum()),
}])
extra.round(3).to_csv(OUT / "incident_extra.csv", index=False)
top3 = ctrl.head(3)

# ---------------------------------------------------------------------------
# Who deploys the systems involved (top deployers by incident count)
# ---------------------------------------------------------------------------
dep = (df["deployer"].fillna("").str.split(",").explode().str.strip())
dep = dep[(dep != "") & (dep.str.lower() != "unknown")]
top_dep = dep.value_counts().head(10).rename("incidents").reset_index()
top_dep.columns = ["deployer", "incidents"]
top_dep.to_csv(OUT / "top_deployers.csv", index=False)

pd.set_option("display.width", 200)
print("incidents {:,}; labeled under MIT taxonomy {:,} ({:.1f}%)".format(len(df), n_lab, n_lab / len(df) * 100))
print("unmapped subdomains:", unmapped or "none")
print()
print(head.T.round(1).to_string(header=False))
print()
print("INCIDENTS PER YEAR (2026 partial)")
print(per_year.tail(8).to_string(index=False))
print()
print("DOMAIN MIX BY ERA (% of labeled incidents)   n =", era_n.to_dict())
print(dom_pct.round(1).to_string())
print("intentional share by era:", intent_era.round(1).to_dict())
print()
print("SAFEGUARD RANKING")
print(ctrl.round(1).to_string(index=False))
print("\ntop 3 control families address {:.1f}% of labeled incidents".format(top3["cumulative_pct"].iloc[-1]))
print()
print(top_dep.to_string(index=False))
