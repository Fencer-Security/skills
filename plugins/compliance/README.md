# compliance

SOC 2 review skills — vendor diligence and self-review readiness assessments. The defining principle: reports are evaluated against what's reasonable for the company's stage, industry, and customer base, then calibrated to the perspective of whoever will be reviewing the report.

## Skills

- **[`soc2-review`](skills/soc2-review/SKILL.md)** — Reviews a SOC 2 Type 1 or Type 2 report in two modes: **vendor diligence** (evaluating a vendor's report for procurement) or **self-review** (assessing your own report through the lens of a target reviewer — e.g., Fortune 500 financial services, healthcare systems, government agencies). Produces a structured markdown report with risk-rated findings, a recommendation, and actionable next steps. Triggers on phrases like "review this SOC 2," "diligence this vendor," "how would a bank evaluate our SOC 2," or sharing a SOC 2 PDF.

## What this is not

- Not a substitute for a full vendor risk management program — it's a focused diligence pass on a single artifact.
- Not legal or audit advice. The output is a structured opinion, not a determination of compliance with any framework.

## Install

```
/plugin marketplace add https://github.com/Fencer-Security/skills
/plugin install compliance@fencer
```

## License

[Apache-2.0](../../LICENSE).
