# SOC 2 Fundamentals

A primer on what SOC 2 reports actually are, so you can read them critically rather than as a
checklist.

## What a SOC 2 is — and isn't

A SOC 2 is an attestation report produced by a CPA firm under AICPA's SSAE-18 standard. The auditor
evaluates a service organization's controls against the **Trust Services Criteria (TSC)**. SOC 2 is
not a certification. There is no "pass/fail" — there's an auditor's opinion (ideally unqualified)
and a list of tested controls with exceptions.

Crucially: **a clean SOC 2 does not mean the vendor is secure.** It means an auditor tested specific
controls during a specific period and the controls operated as the vendor described them. The scope,
the controls, and the criteria are largely chosen by the vendor (with auditor pushback). A narrow
scope with an unqualified opinion can hide a great deal.

## Type 1 vs Type 2

- **Type 1**: Tests _design_ of controls at a single point in time. "These controls exist and are
  designed appropriately as of [date]." Cheaper, faster, common for first-year audits or for vendors
  that just stood up a security program. Relatively weak signal — controls existing on paper isn't
  the same as them working.
- **Type 2**: Tests _operating effectiveness_ over a period (usually 6–12 months). "These controls
  existed and operated effectively from [start] to [end]." This is what enterprise procurement
  actually wants. Type 2 reports include test results and exceptions, which is where the real signal
  is.

A first-year Type 2 covering only 3 months is normal and not a red flag on its own — many vendors do
a 3-month Type 2 the year after their Type 1, then move to 12-month coverage. Flag it as "limited
testing window" but don't penalize harshly.

## The Trust Services Criteria

There are five TSCs. **Security** (also called Common Criteria, or CC) is mandatory in every SOC 2.
The other four are optional:

| TSC                      | What it covers                                                                                    | Typical inclusion                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Security (CC)**        | Access control, change management, risk assessment, monitoring, incident response, communications | Always — required                                                                  |
| **Availability**         | Uptime commitments, capacity planning, environmental safeguards, BCDR                             | Common when vendor has SLAs                                                        |
| **Confidentiality**      | Protection of information designated as confidential (often customer data)                        | Common for B2B SaaS                                                                |
| **Processing Integrity** | Processing is complete, accurate, timely, authorized                                              | Common for fintech, payment processing, data pipelines                             |
| **Privacy**              | Notice, choice, collection, use, retention, disclosure, quality, monitoring                       | Less common; many vendors handle privacy via separate frameworks (GDPR, ISO 27701) |

What's included signals what the vendor's customers have demanded. A SaaS vendor selling to
enterprise without Confidentiality in scope is unusual. A payment processor without Processing
Integrity is unusual.

## How to read each section

The five sections aren't all equally load-bearing. Spend reading time accordingly:

- **Section I** (auditor's opinion letter) — read in full. The opinion type drives everything
  downstream.
- **Section II** (management's assertion) — skim. It's largely boilerplate where management formally
  asserts the description is fair and controls are designed appropriately. Look for unusual
  qualifications or carve-outs.
- **Section III** (system description) — read in full. This is where you learn what the audited
  system actually is, what's in scope, who the subservice orgs are, and what CUECs the vendor has
  shifted to customers.
- **Section IV** (controls and tests of operating effectiveness) — read in full. The highest-signal
  section — actual controls, test procedures, and exceptions live here.
- **Section V** (other information) — read for context, but **don't draw findings from it**. It's
  unaudited management-supplied content. Useful for understanding the vendor's narrative; not
  evidence.

## Auditor's opinion — the four flavors

This appears in Section I, the auditor's letter. Read it first.

- **Unqualified** — clean. The auditor concludes the description is fairly presented, controls are
  suitably designed, and (Type 2) operated effectively. This is the goal and the most common
  outcome.
- **Qualified** — mostly clean, but with a specific exception called out in the opinion itself. Read
  what's qualified — sometimes it's narrow (one control area), sometimes it's structural.
- **Adverse** — the controls don't operate effectively or the description is materially misleading.
  Rare. A serious red flag.
- **Disclaimer** — the auditor couldn't form an opinion (often due to scope limitations or lack of
  evidence). Also serious.

A qualified, adverse, or disclaimed opinion is not automatically disqualifying — but it requires
understanding _why_ and what management did about it.

## Scope: what to look for

The system description (Section III) defines what's actually covered. Watch for:

- **Product scope**: Is the audited system the actual product the user is buying, or some subset?
  "ABC Platform" is fine; "the marketing website and customer support portal" is not, if the user is
  buying ABC Platform.
- **Environment scope**: Production only, or also staging/dev? Production is what matters for
  security.
- **Geographic / entity scope**: Global org, or only the US entity? Could matter if data residency
  is relevant.
- **Time scope** (Type 2): The exam period. Look for gaps from prior reports — a vendor that had a
  12-month report ending Dec 31 last year and now has a 6-month report starting July 1 has a 6-month
  coverage gap.

## Subservice organizations

These are vendors-of-the-vendor: AWS, GCP, Azure, datacenters, managed services, payment processors,
etc. Almost every modern SOC 2 lists at least the cloud provider.

- **Carve-out** (most common): the subservice org's controls are _not_ tested in this audit. The
  vendor relies on the subservice org's own SOC 2. The vendor's responsibility here is to monitor
  the subservice org's SOC 2 and act on any exceptions. Look for whether the report describes how
  the vendor does this monitoring.
- **Inclusive** (rare): the subservice org's controls are tested as part of this audit. More
  thorough, but uncommon.

Carve-out is normal and fine. The question is whether the vendor has a process for reviewing the
subservice org's SOC 2 reports and tracking complementary subservice organization controls (CSOCs).

## CUECs — Complementary User Entity Controls

These are controls the vendor expects _the customer_ (you) to operate for the overall control
environment to work. They're listed in Section III. Read them carefully — they often contain things
like:

- "Customers are responsible for managing their own user access within the application."
- "Customers are responsible for configuring SSO and MFA settings."
- "Customers are responsible for reviewing audit logs."
- "Customers are responsible for backing up their data exported from the system."

That last one in particular — if the vendor disclaims responsibility for data backup, that's a real
customer obligation, not boilerplate.

Two questions to ask of CUECs:

1. Does the user actually do these things? (If not, the vendor's SOC 2 isn't covering the gap.)
2. Are any of them surprising — i.e., shifting responsibility the user assumed was the vendor's?

## Exceptions — what they are and how to read them

Exceptions are the actual control failures the auditor found during testing. They appear in Section
IV alongside the control description and test procedures. A typical exception entry looks like:

> _Control C5.2: Access reviews are performed quarterly for production systems._ _Test: Inspected
> access review documentation for a sample of 4 quarters._ _Exception: For 1 of 4 quarters tested,
> the access review was completed 23 days after the quarter end, outside the policy window._
> _Management response: Process has been updated to include automated reminders 7 days before
> quarter end._

How to read this:

- **Severity** — a single late access review with documented remediation is mild. Multiple control
  failures in the same domain, or a high failure rate within a sample (e.g., "5 of 25 terminations
  did not have timely access removal"), is meaningful.
- **Pattern** — exceptions clustered in one area suggest a systemic weakness. Scattered single
  exceptions across many areas is more likely operational noise.
- **Repeat exceptions** — if a SOC 2 from prior years is mentioned (sometimes in management's
  response), check whether the same exception was flagged before. Repeat exceptions indicate the
  vendor isn't actually fixing things.
- **Management response** — strong responses describe specific remediation with timelines. "Will be
  addressed" is weak. No response is a red flag.
- **Volume** — zero exceptions across a 12-month Type 2 of a complex system is sometimes a sign of a
  thorough audit, sometimes a sign of a soft auditor or narrow scope. Two to five mild exceptions in
  a 12-month report is typical for a healthy program.

## Common control domains and what to look for

When skimming Section IV, expect to see controls grouped roughly into these domains. Each is a place
to evaluate maturity vs peers.

- **Logical access** — provisioning, deprovisioning, periodic access reviews, MFA, password policy,
  privileged access
- **Change management** — code review, deployment approvals, segregation between dev/prod, rollback
  capability
- **Risk assessment** — annual risk assessment, threat modeling, risk register
- **Monitoring** — log collection, alerting, SIEM, response timelines
- **Incident response** — IR plan, tabletop exercises, breach notification process
- **Vendor management** — third-party risk reviews, subprocessor inventory, contract reviews
- **HR / personnel** — background checks, security training, confidentiality agreements, termination
  process
- **Physical / environmental** — usually carved out to the cloud provider
- **System operations** — backup, recovery, capacity, availability
- **Encryption** — at rest, in transit, key management
- **Vulnerability management** — scanning, patching SLAs, pen testing
- **BCDR** — business continuity plan, DR testing, RTO/RPO

## Common red flags to scan for

- Adverse, qualified, or disclaimed opinion (read why)
- Coverage gap from prior period
- Type 2 period under 6 months for a non-first-year audit
- System scope that doesn't include the actual product being purchased
- High volume of exceptions, or exceptions clustered in one control domain
- Repeat exceptions from prior years
- CUECs that shift surprising amounts of responsibility to the customer
- No mention of subservice organization monitoring when there are clear subservice orgs
- Management responses that are vague or absent
- Auditor is unknown / not a recognized firm (this isn't disqualifying — many small firms do
  excellent SOC 2 work — but it's a signal worth noting)

## Common non-issues that look scary but aren't

- A few mild exceptions with documented remediation — this is normal
- Carve-out subservice organizations — this is the standard model
- Section V "other information" being unaudited — that's by design; it's there as context
- Privacy TSC not in scope — many vendors handle privacy through other frameworks
- 3-month first-year Type 2 — normal transition from Type 1
