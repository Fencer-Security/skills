# Report Template

This is the structure to follow when producing the final markdown report. It is intentionally fixed
so reports are consistent across vendors and easy to scan.

Replace bracketed placeholders with actual content. Omit sections only if there's truly nothing to
put in them (e.g., no Strengths section if there are none — but think hard before omitting; most
vendors do _something_ well for their stage).

---

```markdown
# SOC 2 Review: [Vendor Name]

**Report type:** [Type 1 / Type 2] **Period covered:** [date range or "as of [date]"] **Auditor:**
[auditor firm] **Auditor opinion:** [Unqualified / Qualified / Adverse / Disclaimer] **Reviewed:**
[today's date]

---

## Executive summary

[3–5 bullets capturing the headline. What kind of vendor are we looking at, what kind of SOC 2 do
they have, what are the key takeaways.]

- [bullet]
- [bullet]
- [bullet]

**Findings tally:** [N] Critical · [N] High · [N] Medium · [N] Low/Observation · [N] Strengths

**Recommendation:** [Proceed / Proceed with conditions / Hold pending follow-up / Do not proceed]

---

## Vendor profile

[1–2 paragraphs describing the vendor and the peer cohort being used as the comparison baseline.
Make the comparison explicit so the reader knows what bar is being applied. E.g., "We are evaluating
[Vendor] as a Series A SaaS vendor selling primarily to SMB customers in the restaurant industry.
Our comparison baseline is what's reasonable for a 30-person, post-Series-A B2B SaaS company with
SMB-focused distribution — not enterprise or regulated-industry standards."]

---

## SOC 2 report at a glance

| Item                           | Value                                                                                           |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| Report type                    | [Type 1 / Type 2]                                                                               |
| Period                         | [date range]                                                                                    |
| Auditor opinion                | [Unqualified / etc.]                                                                            |
| Trust Service Criteria         | [Security; Availability; Confidentiality; Processing Integrity; Privacy — list what's in scope] |
| Additional frameworks attested | [ISO 27001 / HIPAA / HITRUST / NIST CSF mappings / PCI DSS additional criteria — or "None"]     |
| System scope                   | [the audited system in 1 sentence]                                                              |
| Subservice organizations       | [list, e.g., AWS (carve-out), Stripe (carve-out)]                                               |
| Total exceptions               | [N]                                                                                             |
| Coverage gap from prior period | [Yes / No / N/A — first-year audit]                                                             |
| Documents reviewed             | [e.g., 2026 Type 2 + bridge letter through 2026-04-30 + 2025 Type 2 (prior year)]               |

---

## Findings

Findings are grouped by severity. Each finding includes the gap, the peer expectation, why it
matters here, and supporting evidence.

### Critical

#### [Finding title — e.g., "No MFA enforcement on production access"]

- **Finding:** [What the report shows or doesn't show.]
- **Peer expectation:** [What a reasonable peer at this stage/industry/customer-base would have.]
- **Why it matters here:** [Tie to the user's intended use case if known.]
- **Evidence:** [Section/page reference, exception language, or "control not described in report."]

[Repeat for each Critical finding. If none, write "None." — and that's a strength worth noting.]

### High

[Same structure. If none, write "None."]

### Medium

[Same structure. If none, write "None."]

### Low / Observation

[Same structure, often briefer. If none, write "None."]

---

## Strengths for stage

[Things this vendor does notably well *for their cohort*. Be specific. "Has a SOC 2" is not a
strength on its own. "Performed quarterly access reviews with no exceptions across the audit period"
is a strength for a Series A. "Includes Privacy TSC despite not being privacy-regulated" shows
maturity.]

- [Strength]
- [Strength]
- [Strength]

---

## CUECs that matter

The vendor's report lists complementary user entity controls — things the vendor expects the
customer to do. This section is a curated reference for whoever owns the vendor relationship.

**Note**: CUECs that materially shift responsibility (and that the user is unlikely to operate) are
already rated as findings under Findings above — don't re-litigate severity here. This section is
the boundary list, not a duplicate.

- **[CUEC topic]:** [What the vendor expects the customer to do, and any commentary on whether
  that's a normal customer obligation or a notable shift of responsibility.]
- [Repeat]

[If no CUECs are surprising, write "Nothing unusual — standard customer obligations around user
access management and configuration."]

---

## Recommendation

**[Proceed / Proceed with conditions / Hold pending follow-up / Do not proceed]**

[2–4 sentences explaining the recommendation. Tie it back to the use case if known. If "Proceed with
conditions," list the conditions. If "Hold pending follow-up," make clear what answers from the
vendor would unblock the decision.]

---

## Follow-up questions for the vendor

Send these to the vendor's security team. They're calibrated to address the gaps and observations
above — not a generic security questionnaire.

1. [Specific question tied to a finding. E.g., "Your SOC 2 doesn't describe a formal incident
   response runbook. Can you share your IR plan and the date and outcome of the most recent tabletop
   exercise?"]
2. [Question]
3. [Question]
4. [Question]
5. [Question]

[Aim for 5–10 questions. More than that and the vendor will treat it as a questionnaire rather than
a focused diligence conversation.]
```

---

## Style notes

- **Markdown should render cleanly in GitHub and Notion.** Use standard markdown — tables, headers,
  bullets, bold/italic. Avoid HTML.
- **Severity uses plain bold text** (`**Critical**`, `**High**`, `**Medium**`,
  `**Low / Observation**`). No emojis — the marketplace's other plugins use plain text for severity,
  and a SOC 2 review often gets forwarded to procurement and legal where the formal register suits
  the audience.
- **Cite evidence specifically.** Reference section numbers, control IDs, or page numbers from the
  SOC 2 wherever possible. Vague claims undermine the report's credibility.
- **Be honest about uncertainty.** If you can't tell from the report whether a control exists, say
  so — don't assume the worst or the best. "The report does not describe this control" is a useful,
  honest finding.
- **Don't pad.** A short, sharp report is more valuable than a long one. If a vendor has a clean
  Type 2 with no real gaps for their stage, the report can be 1 page with a "Proceed" recommendation
  and three follow-up questions. That's success, not failure.
- **Filename**: save as `soc2-review-<vendor-slug>-<YYYY-MM-DD>-<HHMM>.md` — always include time so
  same-day re-reviews after vendor remediation don't overwrite the original.
