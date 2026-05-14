# Peer Cohort Heuristics

The whole point of this skill is comparing a vendor against what's reasonable for a peer at their
stage and context — not against Fortune 500 standards. This document captures the heuristics for
setting that bar.

These are not rules. Treat them as defaults to apply unless the specific situation calls for
adjustment.

## How to think about a peer cohort

Three axes drive expectations:

1. **Stage** — primarily governs operational and process maturity. A pre-seed company genuinely
   cannot be expected to have a formal vendor risk program; a Series B company with enterprise
   customers should.
2. **Industry / data sensitivity** — primarily governs the regulatory and security floor.
   Healthcare, financial services, government-adjacent, and security tools all have higher floors
   regardless of stage.
3. **Customer base** — primarily governs how much pressure the vendor has had to mature. A vendor
   selling exclusively to small businesses has rarely been pressed on these things; a vendor with a
   few Fortune 500 customers has been through dozens of security questionnaires and gaps are
   unusual.

Combine these, then read the report against the resulting profile.

## Stage-based expectations

### Pre-seed / seed (typically 1–15 people)

**Reasonable to expect:**

- Basic AUP, code of conduct, and confidentiality agreements
- Cloud-native infrastructure with provider-default security (AWS/GCP IAM, encrypted storage)
- MFA on critical systems (cloud console, code repos, email)
- Some form of access provisioning/deprovisioning, even if manual
- Founder-led security responsibility (no dedicated security person)
- Basic background checks for employees
- SOC 2 Type 1 or first-year Type 2 with limited testing window

**Not reasonable to expect:**

- Dedicated security team or CISO
- Formal incident response runbook with tabletop exercises
- Vendor risk management program
- Threat modeling, red teaming, or formal pen testing program (one annual pen test is starting to be
  common)
- 24/7 monitoring or formal SOC
- Mature change management with separation of duties
- Privacy program beyond basic privacy policy

**Red flags at this stage:**

- No MFA anywhere
- Unencrypted storage of customer data
- No code review process
- Production access for everyone in the company without justification
- Auditor opinion that's qualified or worse

### Series A / early growth (typically 15–50 people)

**Reasonable to expect:**

- Everything from seed, plus:
- Documented security policies (acceptable use, access control, incident response, change
  management)
- SOC 2 Type 2 with at least 3–6 months of coverage
- MFA enforced broadly, including SSO for SaaS apps
- Quarterly or semi-annual access reviews
- Annual security awareness training
- Annual risk assessment (often light)
- Basic vendor inventory and review of critical subprocessors' SOC 2s
- One or two part-time security responsibilities (often a security-minded engineer or someone in
  IT/eng leadership)
- Annual third-party penetration test
- Vulnerability scanning on infrastructure and code

**Not reasonable to expect:**

- Dedicated security team beyond 1–2 people
- 24/7 SOC or formal SIEM operation
- Mature threat modeling for every feature
- Formal red team exercises
- Formal data classification and DLP
- Privacy program approaching ISO 27701 maturity

**Red flags at this stage:**

- Type 1 only, two+ years after raising Series A
- No formal IR plan
- No access reviews, or access reviews not being completed
- No annual pen test
- No subprocessor management
- Multiple exceptions clustered in one domain (e.g., access management)

### Series B / growth (typically 50–200 people)

**Reasonable to expect:**

- Everything from Series A, plus:
- SOC 2 Type 2 with full 12-month coverage; often ISO 27001 in progress or completed
- Dedicated security function (1–5 people, possibly a Head of Security or CISO)
- Formal IR plan with at least one tabletop exercise per year
- SIEM or centralized log aggregation with alerting
- Quarterly access reviews completed reliably
- Vendor risk management program with a documented process for new vendors
- Mature change management: code review enforcement, separation between dev/prod, deployment
  approvals
- Encryption at rest and in transit, with documented key management
- Annual or biannual pen test, with remediation tracking
- Vulnerability management with documented SLAs
- Defined RTO/RPO for critical systems, with at least annual DR testing
- Customer data deletion processes meeting GDPR/CCPA requirements where applicable

**Not reasonable to expect:**

- Massive security team (10+)
- 24/7 monitored SOC (unless industry demands it)
- Formal red team program with internal red teamers
- Bug bounty program (some have one, but not having one is fine)
- Formal threat intelligence function

**Red flags at this stage:**

- No dedicated security person at all
- Type 2 with significant exceptions in core domains and weak management responses
- No documented IR plan or tabletop history
- Subservice organizations not monitored
- Repeat exceptions from a prior-year SOC 2
- CUECs that shift major responsibility to customers in surprising ways

### Series C+ / late-stage (typically 200–1000 people)

**Reasonable to expect:**

- Everything from Series B, plus:
- ISO 27001 likely; possibly ISO 27017/27018 for cloud, or industry-specific (HIPAA, PCI DSS,
  FedRAMP)
- Security team of 5–20 across appsec, infra security, GRC, IR
- Multiple TSCs in scope (Security + Availability + Confidentiality at minimum; often Privacy)
- Formal SDLC with security checkpoints
- Bug bounty or VDP
- Mature vendor risk program with continuous monitoring of critical subprocessors
- Formal data classification and handling procedures
- DLP capabilities deployed
- Customer-facing security documentation, trust center, public security page
- Mature privacy program with DPO or equivalent

**Red flags at this stage:**

- Anything that would have been a red flag at Series B, plus:
- Material gaps that would block Fortune 500 procurement
- No public trust center or customer-facing security materials
- Recent breach with weak public response

### Public / Fortune-1000 size

At this scale, the bar is whatever their largest enterprise customers demand — typically multiple
compliance frameworks, mature programs across all domains, and a security team of 50+. This skill is
less useful at this scale; the standard frameworks (CSA STAR, ISO 27001, FedRAMP) are usually
present and the SOC 2 is a baseline document. Apply the Series C+ profile but raise the bar across
the board.

## Industry adjustments

Apply these on top of the stage profile.

### Healthcare / health-tech (PHI involved)

- **Floor raised regardless of stage**: HIPAA Security Rule controls are required. Expect BAA in
  place, encryption of PHI in transit and at rest, audit logging of PHI access, breach notification
  process.
- A SOC 2 _plus_ HIPAA attestation (often included as additional criteria in the SOC 2) is the norm.
- A 30-person health-tech vendor with no HIPAA mention in their SOC 2 is a serious gap — it's not a
  stage-appropriate omission.

### Financial services (banking, lending, payments, fintech with PCI scope)

- **Floor raised**: depending on what they touch, expect PCI DSS scope handled, possibly
  SOX-relevant controls, possibly NYDFS Part 500 (NY regulated entities), GLBA.
- Processing Integrity TSC should typically be in scope.
- Expect more mature change management and segregation of duties even at smaller sizes.

### Critical infrastructure / data security tools / identity providers

- **Floor raised**: customers depend on the vendor for _their own_ security. Expectations are higher
  than the stage would suggest.
- Expect 24/7 monitoring or strong on-call, mature IR, customer-facing trust documentation.
- A 50-person identity vendor without 24/7 monitoring is a real concern; a 50-person marketing
  analytics vendor without it is fine.

### Government / public sector

- FedRAMP is the most common requirement. SOC 2 alone usually isn't enough for federal customers.
- StateRAMP, CJIS, or specific state-level frameworks may apply.

### State and local government

- **Floor lower and more variable than federal.** Some states have formal frameworks (TX-RAMP,
  StateRAMP); many accept SOC 2 + a security questionnaire with no framework-specific requirements.
- Data residency and public records / FOIA considerations may apply — ask whether data will be stored
  in-state and whether any of it is subject to public records requests.
- CJIS Security Policy applies if the vendor touches criminal justice information — this is a hard
  requirement, not a maturity preference.
- Expect basic security hygiene but not FedRAMP-level rigor. A SOC 2 Type 2 with Security +
  Availability is typically sufficient. Additional frameworks beyond SOC 2 are unusual at this level.
- A vendor selling to municipal governments without MFA or encryption is still a real concern — the
  bar is lower than federal, not absent.

### Heavy industry / manufacturing / construction

- **Historically low security maturity in vendor procurement, but rising fast** — especially for
  vendors touching project data, safety-critical systems, supply chain logistics, or OT/ICS
  environments.
- Primary concerns: operational continuity (Availability TSC), data integrity, and basic
  confidentiality of project data, bid data, and proprietary designs.
- **Vendors touching OT/ICS environments face a raised floor**: expect network segmentation between
  IT and OT, disciplined change management, and controls aligned with IEC 62443 or NIST SP 800-82.
  A SOC 2 alone may not cover OT-specific risks — note this as a gap if OT is in scope.
- Vendors handling only IT/SaaS workloads (project management, ERP, document management) for these
  industries: bar is roughly equivalent to mid-market commercial with a slight raise on availability
  and business continuity.
- Don't expect deep control-by-control scrutiny from these reviewers — they care more about "will
  this vendor's failure disrupt our operations or expose our project data" than granular access review
  cadence or formal threat modeling.
- Safety-critical contexts (construction site systems, manufacturing floor monitoring) raise the bar
  on availability and integrity closer to critical-infrastructure levels.

### B2C / consumer

- Privacy floor is higher (GDPR, CCPA, age-appropriate design where applicable).
- Privacy TSC inclusion or a separate privacy attestation matters more.

### B2B SaaS, no special data sensitivity (e.g., productivity tools, marketing, internal ops)

- Default to the stage profile; no industry-specific raise.
- Most of the SaaS market lives here. The stage table above is calibrated to this baseline.

## Customer-base adjustments

### Selling primarily to SMBs / SMB-focused

- Apply the stage profile as-is. SMB customers rarely run rigorous security reviews, so the vendor's
  program is what their stage produces — nothing more.
- Mature programs at SMB-focused vendors are uncommon and worth noting as a strength.

### Selling to mid-market / commercial

- Slight raise. Commercial customers often run lightweight security reviews. Expect documented IR
  plan, vendor management, and encryption to be present even at smaller stages.

### Selling to enterprise / Fortune 500

- Significant raise. Enterprise procurement runs heavy security reviews. A vendor with multiple
  enterprise logos has been through many of these and gaps are unusual _for what they sell_. Apply
  the next stage up's expectations.

### Selling to regulated industries (banks, hospitals, government)

- Significant raise plus the relevant industry adjustment. Their customers literally cannot legally
  use them without certain controls.

## Putting it together

The way to use this in practice:

1. From the vendor blurb, identify the **stage** (default to size and revenue if stage isn't given —
   1–15 = pre-seed/seed, 15–50 = Series A, 50–200 = Series B, etc.)
2. Apply the **industry adjustment** (most are "no adjustment, default SaaS")
3. Apply the **customer-base adjustment**
4. The resulting profile is the bar to compare findings against.

Then when you encounter something in the report:

- **Present and adequate**: don't list it (unless it's a notable strength for stage)
- **Present but with exceptions**: severity scales with how clustered/repeat/material the exceptions
  are
- **Absent but stage-appropriate to be absent**: don't list it
- **Absent and stage-inappropriate to be absent**: that's a finding

## Worked example

Vendor: 30-person SaaS company, $4M ARR, 100+ customers, restaurant operations software, sells to
independent restaurants and small chains.

**Profile:**

- Stage: Series A (size and revenue)
- Industry: B2B SaaS, no special data sensitivity (PCI may be relevant if they handle payments —
  check)
- Customer base: SMB-focused

**Resulting bar (Series A SaaS to SMB):**

- Documented policies: yes
- SOC 2 Type 2 with 6+ months coverage: yes
- MFA broadly: yes
- Quarterly access reviews: yes
- Annual security training: yes
- Annual pen test: yes
- Vendor risk basics: yes
- One or two security-minded folks: yes
- Dedicated security team: not expected
- 24/7 SOC: not expected
- Formal threat modeling: not expected
- Privacy program at ISO 27701 level: not expected

If the vendor's SOC 2 shows MFA, access reviews completing, an IR plan with a tabletop, and no
clustered exceptions — that's a healthy Series A program for SMB-focused SaaS, even if a Fortune 500
standard would flag a dozen things missing.

If the vendor's SOC 2 shows missing access reviews, no IR plan, and exceptions clustered in change
management — that's underbuilt for stage and a real concern.

## Worked example — regulated industry, enterprise customers

Vendor: 60-person Series B health-tech company, $12M ARR, 80 hospital and clinic customers including
two academic medical centers, sells a clinical workflow platform that ingests EHR data.

**Profile:**

- Stage: Series B (size and revenue)
- Industry: Health-tech with PHI — **floor raised** (HIPAA Security Rule controls required)
- Customer base: Enterprise + regulated industry — **significant raise** (academic medical centers
  run heavy security reviews, plus HIPAA-aligned BAA expectations)

**Resulting bar (raised twice from default Series B):**

- Everything in the Series B baseline
- HIPAA Security Rule controls explicit in the SOC 2 (or a separate HIPAA attestation)
- BAA in place; encryption of PHI in transit and at rest
- Audit logging of PHI access with retention
- Documented breach notification process meeting HIPAA timelines
- Mature change management with separation of duties (enterprise-grade, not just Series B-grade)
- Vendor risk program with continuous monitoring of subprocessors that touch PHI
- Customer-facing trust documentation
- Pen test cadence at least annual, ideally with remediation tracking visible

**Findings calibration:**

- _No HIPAA mention in the SOC 2:_ Critical (regulatory floor not met).
- _Encryption at rest documented but no key management description:_ High at this stage; would be
  Medium for a generic Series B.
- _Quarterly access reviews completed reliably with one minor exception:_ Strength for stage; the
  bar is high here and they cleared it.
- _No 24/7 SOC:_ Low / Observation — even at this stage and customer base, 24/7 SOC isn't required
  for a workflow tool (it would be for an identity provider or EDR vendor). Don't import that
  expectation reflexively.

The point of stacking the adjustments: a 60-person company without HIPAA controls is fine if they
sell marketing tools to small businesses; the same company is a Critical-finding case when their
customers are hospitals.

## Applying a reviewer perspective overlay

When the user specifies a **reviewer perspective** — "how would a Fortune 500 bank evaluate this
report?" or "we're preparing for healthcare procurement reviews" — the peer cohort profile gets a
second pass.

### How it works

1. **Build the baseline** from the subject company's own context (stage + industry + customer base)
   using the sections above. This is the same process as a standard review.

2. **Apply the reviewer overlay** by mapping the reviewer type to the industry and customer-base
   adjustments above. The overlay raises the bar to match what that reviewer would expect — it never
   lowers it below what the subject's own profile produces.

3. **Use the higher of the two bars** for each control domain. If the subject's own profile already
   meets or exceeds the reviewer's expectations (e.g., a healthtech vendor selling to hospitals,
   reviewed by a hospital system), the overlay adds nothing.

### Reviewer-to-heuristic mapping

| Reviewer perspective                         | Industry adjustment applied          | Customer-base adjustment applied              |
| -------------------------------------------- | ------------------------------------ | --------------------------------------------- |
| Financial services (banks, insurance, etc.)  | Financial services                   | Selling to regulated industries               |
| Healthcare / hospital systems                | Healthcare / health-tech             | Selling to regulated industries               |
| Federal government / FedRAMP                 | Government / public sector           | Selling to regulated industries               |
| State or local government                    | State and local government           | Selling to mid-market or enterprise (varies)  |
| Heavy industry / manufacturing / construction| Heavy industry / manufacturing       | Selling to mid-market                         |
| Enterprise SaaS procurement (Fortune 500)    | None (no industry-specific raise)    | Selling to enterprise / Fortune 500           |
| Mid-market commercial buyers                 | None                                 | Selling to mid-market / commercial            |
| General enterprise — no specific vertical    | None                                 | Selling to enterprise / Fortune 500           |

### Principle: the overlay only raises

The reviewer perspective never lowers the bar. If a vendor already sells to enterprise healthcare
customers and the reviewer is a mid-market commercial buyer, the vendor's own profile produces a
higher bar — use that. The overlay catches the case where a vendor's actual customer base is less
demanding than the specific reviewer evaluating them.

### Worked example — self-review, bank reviewer

**Subject:** 80-person Series B SaaS company, project management tools, selling primarily to
mid-market.

**Reviewer perspective:** Fortune 500 financial services (JP Morgan-type procurement).

**Baseline (from subject's own profile):**

- Stage: Series B
- Industry: B2B SaaS, no special data sensitivity → no industry adjustment
- Customer base: mid-market → slight raise

**Reviewer overlay:**

- Financial services industry adjustment → expect PCI-adjacent rigor on change management,
  Processing Integrity TSC in scope, mature vendor risk program, segregation of duties
- "Selling to regulated industries" customer-base adjustment → significant raise

**Result:** The bar looks like Series B + financial-services floor + enterprise-regulated customer
expectations. This is a meaningful stretch for a mid-market project management tool company. The
report should acknowledge this honestly: "Your peer cohort doesn't require this level of maturity.
However, a Fortune 500 bank's procurement team will apply their standard bar regardless of your
typical customer profile."

### Worked example — vendor mode, redundant reviewer perspective

**Subject:** 30-person Series A healthtech vendor, selling to hospitals.

**Reviewer:** "We're a hospital system evaluating this vendor."

**Baseline:** Series A + healthcare industry adjustment + regulated customer-base adjustment.

**Reviewer overlay:** Healthcare + regulated industries — but the subject already has both applied.

**Result:** No additional raise. The reviewer's expectations are already embedded in the subject's
own profile. This is the common case when the reviewer is a natural customer of the vendor.

### Worked example — self-review, state government reviewer

**Subject:** 40-person Series A SaaS company, document management tools, selling to SMBs and small
government offices.

**Reviewer perspective:** State government procurement.

**Baseline:**

- Stage: Series A
- Industry: B2B SaaS, no special sensitivity → no industry adjustment
- Customer base: SMB-focused → no raise

**Reviewer overlay:**

- State and local government industry adjustment → modest raise on data residency, public records
  handling, and availability. CJIS only if criminal justice data is involved (ask).
- Customer-base adjustment: mid-market level (state agencies are larger and more process-heavy than
  SMBs, but don't run Fortune 500-grade security reviews)

**Result:** The bar rises modestly above the SMB-focused Series A baseline. Expect documented
security policies, SOC 2 Type 2 with Security + Availability, basic encryption, and access
controls. Don't expect FedRAMP, NIST 800-53 mapping, or a formal privacy program — state
procurement is less standardized and the floor is lower than federal. The report should note which
state-specific frameworks (TX-RAMP, StateRAMP) might apply if the user names the state.
