# The AI Oversight Gap

**Analysis memo · September 2026**
**Sources:** SEC EDGAR full-text search, every 10-K filed 2019 – Sept 2026 · AI Incident Database, 1,689 incidents (export of 21 Sept 2026), classified under the MIT AI Risk Repository taxonomy

---

## Bottom line

**Companies talk about AI far more than they describe governing it.** In 2025, 49% of 10-K filings mentioned artificial intelligence, but only 1.7% used explicit AI-governance language: 28 mentions for every filing that described governance. By September 2026 the gap had narrowed to 11 to 1 (61% against 5.3%). It's closing fast, but it's still wide.

**And the harms governance needs to catch have changed.** Among publicly documented AI incidents, 98% arose after deployment. Since 2023, the most common problem is no longer AI systems failing on their own; it's people deliberately misusing them. Oversight built around pre-launch review is aimed at the wrong place and the wrong threat.

## What companies disclose

| Filing year | 10-Ks | Mention AI | Explicit governance language | Mentions per governance filing |
|---|---|---|---|---|
| 2019 | 6,854 | 6.3% | 0.0% | — |
| 2023 | 7,432 | 17.2% | 0.1% | 320 |
| 2024 | 6,924 | 34.8% | 0.7% | 52 |
| 2025 | 6,624 | 49.3% | 1.7% | 28 |
| 2026 (to 26 Sept) | 6,195 | 60.7% | 5.3% | 11 |

- **The language is in the report, not buried in attachments.** 96% of 2025 filings with governance language carry it in the 10-K body rather than only in an attached exhibit like a code of conduct.
- **By sector (2025–26):** software and services lead on governance language at 8.4% of filings. Finance, insurance and real estate mention AI in 38% of filings but describe governing it in only 2.1%. Mining and energy is lowest at 0.4%.

## What actually goes wrong

**Reported incidents roughly quadrupled** from 108 in 2022 to 452 in 2025. That reflects rising attention as well as rising harm, so treat it as a lower bound on the trend, not a prevalence rate.

**98% of classified harms arose after deployment:** 1,460 incidents, against 27 before deployment.

**The threat changed with generative AI.** Using the MIT taxonomy's expert labels:

| Risk domain | Before 2023 | 2023–2026 |
|---|---|---|
| Malicious actors & misuse | 11% | **52%** |
| Misinformation | 5% | 18% |
| AI system safety & failures | **39%** | 11% |
| Discrimination & toxicity | **30%** | 9% |

Intentional harm rose from 27% of incidents to 61%. The biggest single category is fraud, scams and targeted manipulation.

## The governance roadmap

Each MIT risk subdomain was mapped to the control family that most directly prevents or detects it, following the NIST AI Risk Management Framework and its Generative AI Profile. The full mapping is published in `output/safeguard_mapping.csv`. Ranked by share of incidents addressed:

1. **Misuse and abuse monitoring:** 38% of all incidents, 52% since 2023. Operates after deployment.
2. **Reliability testing and performance monitoring:** 20%. Operates before and after deployment.
3. **Output accuracy controls and human review:** 13%. Operates after deployment.

**These three cover 71% of documented AI harm.** Two of the three operate after launch, and the third spans both. A governance program that invests mainly in pre-launch review and documentation is aimed at under 2% of incidents.

## Why the method matters

1. **Filings, not documents.** EDGAR returns one hit per document, and a 10-K bundles many. Counting hits would double-count and silently mix in exhibits, so every hit is collapsed to its filing.
2. **The denominator is checked.** "Risk factors" stands in for all 10-Ks; 98% of AI-mentioning filings fall inside it every year.
3. **Expert labels, not homemade ones.** Incidents are classified with the MIT taxonomy's existing labels rather than a new model, and the one judgement call, the safeguard mapping, is published line by line.
4. **Phrase matching measures disclosure, not practice.** A company can govern AI without these words, or use them without governing anything. What's measured is what investors can see.

## So what

1. **For boards and risk officers:** disclosure is running far ahead of described oversight. Investors are hearing about AI risk without hearing who owns it, and that's the gap regulators will ask about first.
2. **For AI governance programs:** put the budget where the harm is. Misuse monitoring, performance monitoring and output review after launch address most documented incidents. Pre-launch paperwork alone doesn't.
3. **For financial services specifically:** a sector that mentions AI in over a third of filings but describes governance in 2% is the clearest near-term exposure.

## Limitations

- **The incident data covers what was publicly reported,** so it skews toward consumer-facing, newsworthy harm. Internal failures and near-misses are under-represented.
- **Governance language is identified by exact phrases.** Companies using other wording, such as describing a model risk committee without naming AI, are missed, so governance is likely undercounted somewhat.
- **2026 figures run only to 26 Sept 2026,** and filing year isn't fiscal year.
- **The safeguard mapping is a judgement call.** Reasonable reviewers could assign some subdomains differently; the mapping file exists so they can.

---

*Incident data: AI Incident Database (incidentdatabase.ai), CC BY-SA 4.0. Derived incident tables in `output/` are shared under the same license.*
