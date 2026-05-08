---
name: soc2-vendor-review
description: Review and assess a vendor's SOC 2 Type 1 or Type 2 report against the security and operational maturity that's reasonable for a company of their size, stage, industry, and customer base — not against Fortune 500 standards. Use whenever the user shares a SOC 2 report (PDF, attestation letter, bridge letter) along with any context about the vendor — even casually, like "can you look over this SOC 2 from a 40-person fintech startup we're evaluating" or "diligence this vendor's SOC 2 for me." Also trigger for related vendor security diligence requests where a SOC 2 is the primary artifact — gap analysis, peer-cohort comparison, drafting follow-up questions for the vendor's security team, or producing a write-up to share with stakeholders. Produces a structured markdown report with risk-rated findings, a recommendation, and follow-up questions to send to the vendor.
allowed-tools: Read Write Glob Grep
---

# SOC 2 Vendor Review

A skill for assessing a SOC 2 report in the context of who the vendor actually is — their stage, size, industry, and customer base — and surfacing gaps that matter for vendor diligence.

## Why this skill exists

Most SOC 2 reviews fail in one of two directions: either they rubber-stamp the report ("it has a SOC 2, ship it") or they hold a 30-person startup to the standards of a Fortune 500 enterprise and flag everything as a problem. Neither is useful.

A good SOC 2 review answers a different question: **given who this vendor actually is, does their security program look like what a reasonable peer would have — and where it doesn't, does that matter for our use case?**

That's what this skill produces.

**Confidentiality.** SOC 2 reports are typically NDA-protected. This skill operates on local files only and produces a local markdown report; it does not transmit report contents anywhere. Don't paste report contents into third-party tools or chat surfaces outside this session.

## Inputs

The user provides:

1. **One or more SOC 2 documents** — typically PDFs. The primary artifact is a Type 1 or Type 2 report. Vendors commonly share several documents together; handle them as follows:
    - **Most recent full Type 2** → the primary artifact; everything in Step 2 is extracted from this.
    - **Bridge letter / attestation letter** alongside a Type 2 → extends the coverage period; any qualifications it raises become findings.
    - **Bridge letter alone, no full Type 2** → ask once whether the full Type 2 is available, then **proceed with shallow analysis** — flag the limitation prominently in the report header, the Gaps section, and the Recommendation. Conclusions are necessarily provisional. Don't block on a missing full report; partial output beats none, as long as the limitation is honest.
    - **Prior year's report** → use it as the source of truth for repeat-exception detection; note any exception that recurs from the prior year as a stronger finding.

    Note all documents received in the report header.

2. **A vendor context blurb** — describes who the vendor is across four required dimensions: **company size/stage**, **industry/data sensitivity**, **customer base**, and **intended use case** (what data the vendor will hold, how critical they are to your operations).

### Collecting the vendor blurb when it's missing or sparse

If any of the four dimensions is missing, run a structured intake using `AskUserQuestion` rather than a free-form ask. Skip questions for dimensions the user already supplied. Keep the option labels short — the tool surfaces them as buttons.

- **Company size / stage:** 1–15 (pre-seed/seed) · 15–50 (Series A) · 50–200 (Series B) · 200–1000 (Series C+/late-stage) · 1000+ (public/Fortune-1000) · I'm not sure
- **Industry / data sensitivity:** B2B SaaS (no special sensitivity) · Healthcare / PHI · Financial services / PCI · Critical infra or security tooling · Government / public sector · B2C consumer
- **Customer base:** Primarily SMB · Mid-market · Enterprise · Regulated industries (banks, hospitals, gov)
- **Intended use case:** A free-text question — "What will this vendor hold or do for you, and how critical are they to your operations?"

After collecting answers, echo back the assembled profile in one sentence — e.g., "Treating this vendor as a Series B health-tech vendor selling to hospitals, calibrating against that bar." Then proceed.

A reasonable minimum to proceed: size/stage, industry, customer base, and intended use case. Without these the gap analysis becomes generic and loses most of its value — the whole point is calibrating expectations to peers.

## Workflow

### Step 0: Confirm the document is a reviewable SOC 2

Before reading deeply, confirm the document is what we can actually work with. Read the first 2–3 pages and check:

- **Is it a SOC 2 at all?** Look for telltale strings: "Independent service auditor's report," "SSAE-18" (or "SSAE No. 18"), "Trust Services Criteria," "AICPA," "Service Organization Control." If absent, the user has shared something else — most likely an ISO 27001 cert, a pen test report, a vendor security questionnaire, or a customer-trust whitepaper. Stop and tell the user what they appear to have shared and that this skill needs a SOC 2 specifically. (If it's an ISO 27001 cert, say so plainly — there isn't an ISO skill yet, but pretending the SOC 2 review will work is worse.)

- **Is it a SOC 2 Type 1, Type 2, or something else?** Type 3 reports and "executive summary" / prospect-facing condensed versions exist but lack the Section IV control listing and exceptions that this skill depends on. If the document is dramatically shorter than typical (under ~30 pages), labeled "executive summary" or "for prospects," or lacks Section IV, decline gracefully — explain the skill needs a full Type 1 or Type 2 to produce useful findings.

- **Is the PDF text-extractable?** Some scanned SOC 2 PDFs have no embedded text layer. If the first read returns empty or near-empty content for pages that visually contain text, the PDF is image-only. Stop and tell the user: "This PDF appears to be image-only with no text layer. Run it through OCR (e.g., `ocrmypdf input.pdf output.pdf`) and re-share." Don't try to produce a report from no content.

If the document passes all three checks, proceed to Step 1.

### Step 1: Read the report

Most SOC 2 reports run 50–150 pages and follow a predictable structure:

- **Section I**: Independent service auditor's report (the opinion — qualified, unqualified, adverse, disclaimer). **Read in full.**
- **Section II**: Management's assertion. Skim — boilerplate unless there's an unusual qualification.
- **Section III**: System description (the vendor's narrative description of services, infrastructure, people, data, processes, controls, subservice organizations, CUECs). **Read in full.**
- **Section IV**: Trust services criteria, related controls, and tests of operating effectiveness — this is where the actual control list and test results live, including any **exceptions**. **Read in full** — this is the highest-signal section.
- **Section V** (sometimes): Other information provided by management (unaudited). Useful context, but don't draw findings from it.

**Reading the PDF.** Claude Code's `Read` tool requires a `pages` parameter for PDFs over 10 pages. Read the table of contents first (`pages: "1-3"`), use it to locate Sections I, III, and IV, then read each in 10–20 page chunks. Don't try to read the whole PDF in one call — it'll fail. A typical pattern:

```
Read(file_path, pages: "1-3")     # ToC + opinion letter
Read(file_path, pages: "4-8")     # finish opinion + management assertion
Read(file_path, pages: "9-30")    # system description (Section III)
Read(file_path, pages: "31-50")   # controls + exceptions (Section IV)
... continue until Section IV is fully covered
```

The reference docs live alongside this SKILL.md; resolve their absolute path so reads work in both Claude Code and Codex:

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${SKILL_DIR}}"
# References to load on demand:
#   $SKILL_DIR/references/soc2-fundamentals.md
#   $SKILL_DIR/references/peer-cohort-heuristics.md
#   $SKILL_DIR/references/report-template.md
```

If unfamiliar with how to read these reports, read `$SKILL_DIR/references/soc2-fundamentals.md` for a primer on what to look for in each section, what trust service criteria mean, what counts as a real exception, the difference between Type 1 and Type 2, and common terms (CUEC, subservice organization, carve-out vs inclusive, etc.).

### Step 2: Extract structured findings

Pull the following from the report. Capture page references using the format `Section IV.5, p. 47` when the section is useful, or `p. 47` when section context isn't needed. Consistent format makes the report's evidence citations skimmable and lets the reader jump to the source quickly.

- **Auditor and opinion**: Who performed the audit. What kind of opinion (unqualified is the goal; qualified or adverse are red flags).
- **Report type and period**: Type 1 or Type 2. For Type 2, the period covered (a 3-month period for a first-year audit is normal; ongoing reports should cover ~12 months with no gaps from the previous report).
- **Freshness**: Today's date minus the period end. **If the period ended more than 12 months ago, this is a finding** — Medium for 12–18 months, High for >18 months. Ask the user whether a current report is available before going deep on the rest of the extraction; a stale report changes what's worth investigating.
- **Trust Service Criteria (TSC) in scope**: Security is mandatory; Availability, Confidentiality, Processing Integrity, and Privacy are optional. Which the vendor included signals what they care about and what their customers demanded.
- **Additional frameworks attested**: Some SOC 2 reports include or reference additional criteria — HIPAA, HITRUST, NIST CSF mappings, PCI DSS additional criteria, ISO 27001 cross-references. Capture these; they're candidate **Strengths for stage** (program-maturity signal beyond what SOC 2 alone provides).
- **System scope**: What products/services/environments are in scope. Watch for narrow scoping (e.g., only the marketing site, not the actual product).
- **Subservice organizations**: AWS, GCP, Azure, datacenters, payment processors, etc. — and whether they're carved-out (their controls are not tested here, you rely on their own SOC 2) or inclusive (tested as part of this audit). Carve-out is normal; the question is whether the vendor monitors those subservice orgs.
- **Complementary User Entity Controls (CUECs)**: What the vendor expects _you_ to do. Read these — they often shift real responsibility to the customer.
- **Exceptions / deviations**: The actual control failures the auditor found during testing. These are gold. Note severity, whether management responded, and whether remediation is described. **Cross-check against the prior year's report** if one was provided — repeat exceptions are a stronger finding than first-time ones.
- **Control inventory**: A high-level catalogue of what controls exist, organized by domain (access control, change management, incident response, vendor management, BCDR, HR/personnel, monitoring, encryption, vulnerability management, etc.).

### Step 3: Build the peer cohort profile

Using the vendor blurb, sketch what a reasonable peer at this stage looks like. The goal is to set the expectation bar fairly.

For detailed peer-cohort heuristics (what's reasonable at seed vs Series A vs Series B+ vs late-stage vs public; SaaS vs fintech vs healthtech vs infra; SMB vs mid-market vs enterprise customer base), read `$SKILL_DIR/references/peer-cohort-heuristics.md`. Use those heuristics — don't make up your own bar.

A few principles worth holding onto:

- **Stage governs the operational maturity bar more than size.** A 50-person Series B will typically have more formal processes than a 50-person bootstrapped company, because they've raised institutional money and signed enterprise contracts that demanded it.
- **Industry governs the regulatory floor.** A healthtech vendor needs HIPAA-aligned controls regardless of size. A fintech vendor handling card data needs PCI scope handled. A vendor selling into financial services needs to look defensible to bank security teams.
- **Customer base governs the maturity ceiling.** A vendor selling to Fortune 500 has been through enough security questionnaires that gaps are unusual; a vendor selling to small restaurants has probably never been pressed on these things and gaps are expected.

### Step 4: Compare and rate findings

Walk through the extracted findings against peer expectations. For each gap or notable item, classify:

- **Critical** — a control failure or absence that's unusual even for this peer cohort and creates real risk for the user's intended use case. Examples: production access without MFA at a vendor selling to enterprises; no encryption at rest for a vendor storing PII; an adverse or qualified auditor opinion; multiple repeat exceptions from prior years.
- **High** — a meaningful gap relative to peers, or a single significant exception with weak remediation. Examples: no formal incident response plan at a 100-person company; access reviews not performed; vendor management process is informal at a vendor that itself depends heavily on subprocessors.
- **Medium** — gap exists but is common at this stage, or is mitigated by other controls. Worth raising in follow-up but not a blocker. Examples: no formal threat modeling program at a 30-person startup; SOC monitoring is business-hours only at a non-24/7-SLA product.
- **Low / Observation** — worth noting for completeness but not a real concern at this stage. Examples: no dedicated CISO at a 25-person company; no formal red team exercises at Series A.
- **Strength** — call these out. Things the vendor does well _for their stage_ are signal too. A 40-person company with formal vendor risk management, working access reviews, and clean exception history is doing better than peers. Additional frameworks attested in the report (ISO 27001, HIPAA, HITRUST, NIST CSF, PCI DSS additional criteria) are program-maturity signal and belong here.

Avoid the trap of importing enterprise expectations wholesale. If you find yourself flagging "no 24/7 SOC" or "no dedicated security team of 10+" at a Series A, that's enterprise-grade reasoning misapplied. Fix it.

**CUECs deserve their own rating pass.** Walk through the CUECs from Step 2 with the same severity lens. A CUEC that shifts material responsibility — "customer is responsible for backing up exported data," "customer is responsible for monitoring authentication anomalies," "customer is responsible for retaining audit logs beyond 30 days" — should generate a Medium or High **finding**, not just a "CUECs that matter" bullet, when the user is not realistically going to operate that control. The CUEC list documents the boundary; the _finding_ is that the boundary lands somewhere the user wasn't expecting.

### Step 5: Generate the report

Use the template structure in `$SKILL_DIR/references/report-template.md`. The report is markdown, designed to be readable and skimmable — pasted into Notion or attached to a vendor risk ticket.

Do not include findings the vendor handled well unless they're notable strengths for their stage. The report should be honest, calibrated, and actionable — not a comprehensive control-by-control audit (that's what the SOC 2 itself is).

**CUECs in the report.** Material CUECs you rated as findings in Step 4 belong in **Findings** under their assigned severity. The separate **CUECs that matter** report section is the curated list of user-side controls verbatim from the report — reference for whoever owns the vendor relationship — not a duplicate of the findings.

**Recommendation rubric.** End the report with one of: Proceed / Proceed with conditions / Hold pending follow-up / Do not proceed. The recommendation is a judgment call, not a calculation, but the following is a reasonable default starting point — deviate when use case demands it:

| Severity tally                               | Default recommendation                                                                                                                                         |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Any Critical                                 | Hold pending follow-up — or **Do not proceed** if the Critical is structural (adverse opinion, scope mismatch, repeat criticals, RLS-equivalent base failures) |
| 0 Critical, 2+ High                          | Proceed with conditions                                                                                                                                        |
| 0 Critical, 0–1 High, several Medium         | Proceed with conditions or Proceed, depending on use case                                                                                                      |
| 0 Critical, 0 High, mostly Low / Observation | Proceed                                                                                                                                                        |

The use case can promote or demote the default by one level. A single Medium can warrant a Hold if the user is putting their entire customer database in this vendor's hands. A single Critical can warrant Conditions if the user's exposure is trivial. State the reasoning explicitly when deviating.

**Follow-up questions.** Phrase them specifically — not "tell us about your incident response process" but "your SOC 2 doesn't describe a formal incident response runbook; can you share your IR plan and details on the last tabletop exercise?" Aim for 5–10. More than that and the vendor will treat it as a questionnaire rather than a focused diligence conversation.

### Step 6: Save the file and hand off

**Vendor slug.** Lowercase ASCII alphanumerics + hyphens, derived from the vendor's primary name, max 40 chars. Examples: "Acme Corp." → `acme-corp`; "Datadog, Inc." → `datadog`; "Health-Stream Analytics LLC" → `health-stream-analytics`.

**Filename.** `soc2-review-<vendor-slug>-<YYYY-MM-DD>-<HHMM>.md`, saved to the working directory. Always include time, so same-day re-reviews (vendor sends an updated report, re-run after their remediation) don't overwrite the original.

**In-chat handoff.** Don't paste the entire report inline. Give the user the verdict at a glance, then point at the file. Use this format:

```
SOC 2 review for [Vendor] saved to: ./soc2-review-<slug>-<date>-<time>.md

- Critical: [N]  High: [N]  Medium: [N]  Low: [N]  Strengths: [N]
- **Recommendation: [Proceed / Conditions / Hold / Do not proceed]**
- [One-line headline — the single most important thing the user should know.]
```

Three lines plus the file path. The user gets the verdict instantly and reads the file for detail.

## Output structure

The report follows this fixed structure (full template in `references/report-template.md`):

1. **Header** — vendor name, report type/period, auditor, date of review
2. **Executive summary** — 3–5 bullets capturing the headline; recommendation; severity tally
3. **Vendor profile** — the peer cohort you're comparing against, in their own words
4. **SOC 2 report at a glance** — opinion, TSC in scope, scope of system, subservice orgs, exception count
5. **Findings** — grouped by severity, each with: finding, peer expectation, why it matters here, evidence/page reference
6. **Strengths for stage** — what's notably good
7. **CUECs that matter** — the user-side controls the vendor expects you to operate
8. **Recommendation** — one of the four standard recommendations, with reasoning
9. **Follow-up questions for the vendor** — specific, numbered, ready to paste

## A few things to remember

- **Don't invent control failures.** If the report doesn't describe a control, that's an absence to note — not a confirmed failure. Distinguish "the report doesn't address X" from "the auditor found X failed."
- **Read the exceptions carefully.** A single missed access review during the period with documented remediation is very different from "12 of 87 terminations did not have access removed within policy." The numbers and management response matter.
