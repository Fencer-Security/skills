# Report Template

This is the structure to follow when producing the final markdown report. It is intentionally fixed
so reports are consistent and easy to scan.

The template supports two review modes: **vendor diligence** and **self-review readiness**. Sections
marked with `<!-- MODE: vendor -->` or `<!-- MODE: self-review -->` are mode-specific — use only the
sections matching the active mode. Sections marked `<!-- MODE: both -->` apply in either mode.

Replace bracketed placeholders with actual content. Omit sections only if there's truly nothing to
put in them (e.g., no Strengths section if there are none — but think hard before omitting; most
companies do _something_ well for their stage).

---

## Template

<!-- MODE: vendor -->

```markdown
# SOC 2 Review: [Vendor Name]
```

<!-- MODE: self-review -->

```markdown
# SOC 2 Readiness Assessment: [Company Name]
```

<!-- MODE: both -->

```markdown
**Report type:** [Type 1 / Type 2] **Period covered:** [date range or "as of [date]"] **Auditor:**
[auditor firm] **Auditor opinion:** [Unqualified / Qualified / Adverse / Disclaimer] **Reviewed:**
[today's date]
```

<!-- MODE: vendor -->

```markdown
**Review mode:** Vendor diligence
```

<!-- MODE: self-review -->

```markdown
**Review mode:** Self-review readiness assessment **Reviewer perspective:** [e.g., Fortune 500
financial services procurement, state government, healthcare systems]
```

<!-- MODE: both -->

```markdown
---

## Executive summary

[3–5 bullets capturing the headline. What kind of company are we looking at, what kind of SOC 2 do
they have, what are the key takeaways.]

- [bullet]
- [bullet]
- [bullet]

**Findings tally:** [N] Critical · [N] High · [N] Medium · [N] Low/Observation · [N] Strengths
```

<!-- MODE: vendor -->

```markdown
**Recommendation:** [Proceed / Proceed with conditions / Hold pending follow-up / Do not proceed]
```

<!-- MODE: self-review -->

```markdown
**Readiness:** [Ready / Ready with caveats / Address before sharing / Significant gaps]
```

<!-- MODE: both -->

```markdown
---

## Company profile
```

<!-- MODE: vendor -->

```markdown
[1–2 paragraphs describing the vendor and the peer cohort being used as the comparison baseline.
Make the comparison explicit so the reader knows what bar is being applied. E.g., "We are evaluating
[Vendor] as a Series A SaaS vendor selling primarily to SMB customers in the restaurant industry.
Our comparison baseline is what's reasonable for a 30-person, post-Series-A B2B SaaS company with
SMB-focused distribution — not enterprise or regulated-industry standards."]
```

<!-- MODE: self-review -->

```markdown
[1–2 paragraphs describing the company and the reviewer perspective being applied. Make both the
baseline and the overlay explicit. E.g., "We are assessing [Company]'s SOC 2 as it would be reviewed
by a Fortune 500 financial services procurement team. [Company] is a Series B SaaS vendor with 80
employees, selling project management tools to mid-market customers. The peer cohort baseline is a
Series B B2B SaaS company with mid-market distribution. The financial services reviewer perspective
raises the bar on change management, processing integrity, vendor risk management, and segregation
of duties beyond what [Company]'s typical customer base would demand."]
```

<!-- MODE: both -->

```markdown
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
matters, and supporting evidence.

### Critical

#### [Finding title — e.g., "No MFA enforcement on production access"]

- **Finding:** [What the report shows or doesn't show.]
- **Peer expectation:** [What a reasonable peer at this stage/industry/customer-base would have.]
```

<!-- MODE: vendor -->

```markdown
- **Why it matters here:** [Tie to the user's intended use case if known.]
```

<!-- MODE: self-review -->

```markdown
- **Why a [reviewer type] reviewer would flag this:** [Explain what the target reviewer's
  procurement or security team would think and why this would be a concern in their framework.]
```

<!-- MODE: both -->

```markdown
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

[Things this company does notably well *for their cohort*. Be specific. "Has a SOC 2" is not a
strength on its own. "Performed quarterly access reviews with no exceptions across the audit period"
is a strength for a Series A. "Includes Privacy TSC despite not being privacy-regulated" shows
maturity.]

- [Strength]
- [Strength]
- [Strength]

---

## CUECs that matter
```

<!-- MODE: vendor -->

```markdown
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
```

<!-- MODE: self-review -->

```markdown
Your report lists these complementary user entity controls — obligations you're placing on your
customers. A [reviewer type] reviewer will scrutinize whether these are reasonable or whether they
shift more responsibility than the customer expects to carry.

**Note**: CUECs that materially shift responsibility are already rated as findings above. This
section is the reference list for your team — consider whether any of these would be objectionable
to [reviewer type] during procurement review.

- **[CUEC topic]:** [What you expect the customer to do, and commentary on whether a [reviewer type]
  reviewer would find this reasonable or would push back.]
- [Repeat]

[If no CUECs are surprising, write "Standard customer obligations — nothing that would raise
eyebrows with [reviewer type] procurement."]
```

<!-- MODE: both -->

```markdown
---
```

<!-- MODE: vendor -->

```markdown
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

<!-- MODE: self-review -->

```markdown
## Readiness assessment

**[Ready / Ready with caveats / Address before sharing / Significant gaps]**

[2–4 sentences explaining the assessment. Frame it from the reviewer's perspective — what would a
[reviewer type] procurement or security team conclude after reading this report? If "Ready with
caveats," name the items they'll ask about. If "Address before sharing," be specific about what
blocks readiness.]

---

## Remediation priorities

Ordered by impact on readiness for [reviewer type] review. Each item ties back to a finding above.

1. **[Gap title]** — [What to fix.] Effort: [quick win / quarter-level project / major initiative].
   Resolves: [finding reference]. Impact: [why fixing this matters for [reviewer type] review].
2. [Repeat]
3. [Repeat]

[If the report is clean, write "No material remediation needed before [reviewer type] review."]

---

## Likely reviewer questions

A [reviewer type] procurement or security team reviewing this report would likely ask the following.
Prepare answers or documentation for each.

1. [Specific question a reviewer would ask, tied to a finding or gap. E.g., "Your SOC 2 doesn't
   describe a formal incident response runbook. A bank's security team will ask: 'Can you share your
   IR plan and the date of the most recent tabletop exercise?' Prepare: your IR plan document and
   tabletop exercise summary."]
2. [Question + preparation guidance]
3. [Question + preparation guidance]
4. [Question + preparation guidance]
5. [Question + preparation guidance]

[Aim for 5–10. These should be specific and answerable, not generic questionnaire items.]
```

---

## Style notes

- **Markdown should render cleanly in GitHub and Notion.** Use standard markdown — tables, headers,
  bullets, bold/italic. Avoid HTML (except the `<!-- MODE -->` markers, which are template
  instructions and should not appear in the final output).
- **Severity uses plain bold text** (`**Critical**`, `**High**`, `**Medium**`,
  `**Low / Observation**`). No emojis — the marketplace's other plugins use plain text for severity,
  and a SOC 2 review often gets forwarded to procurement and legal where the formal register suits
  the audience.
- **Cite evidence specifically.** Reference section numbers, control IDs, or page numbers from the
  SOC 2 wherever possible. Vague claims undermine the report's credibility.
- **Be honest about uncertainty.** If you can't tell from the report whether a control exists, say
  so — don't assume the worst or the best. "The report does not describe this control" is a useful,
  honest finding.
- **Don't pad.** A short, sharp report is more valuable than a long one. If a company has a clean
  Type 2 with no real gaps for their stage, the report can be 1 page with a "Proceed" or "Ready"
  recommendation and three follow-up questions. That's success, not failure.
- **Filename**:
    - Vendor mode: `soc2-review-<vendor-slug>-<YYYY-MM-DD>-<HHMM>.md`
    - Self-review mode: `soc2-readiness-<company-slug>-<reviewer-slug>-<YYYY-MM-DD>-<HHMM>.md` —
      always include time so same-day re-reviews don't overwrite the original.

## Self-review recommendation rubric

Use this rubric as the default starting point for self-review mode. Deviate when the reviewer
perspective or use case demands it — state reasoning explicitly.

| Severity tally                               | Default readiness assessment                                                                                           |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Any Critical                                 | **Address before sharing** — or **Significant gaps** if structural (adverse opinion, scope mismatch, repeat criticals) |
| 0 Critical, 2+ High                          | **Address before sharing**                                                                                             |
| 0 Critical, 0–1 High, several Medium         | **Ready with caveats**                                                                                                 |
| 0 Critical, 0 High, mostly Low / Observation | **Ready**                                                                                                              |

**Readiness levels explained:**

- **Ready** — a [reviewer type] reviewer would likely have no material concerns. Share confidently.
- **Ready with caveats** — reviewable, but expect follow-up questions on specific items. Consider
  proactive disclosure of the Medium findings in a cover letter or trust page.
- **Address before sharing** — a [reviewer type] reviewer would likely hold or escalate. Fix the
  Critical/High items first; sharing now risks a negative procurement outcome.
- **Significant gaps** — the report has structural issues that would block procurement with
  [reviewer type]. The gaps go beyond individual findings to fundamental report problems.
