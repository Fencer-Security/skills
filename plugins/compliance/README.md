# compliance

SOC 2 vendor diligence and related compliance review skills. The defining principle: vendors are evaluated against what's reasonable for a peer at their stage, industry, and customer base — not against Fortune 500 standards.

## Skills

- **[`soc2-vendor-review`](skills/soc2-vendor-review/SKILL.md)** — Reviews a SOC 2 Type 1 or Type 2 report against a peer-cohort-calibrated bar and produces a structured markdown report with risk-rated findings, a recommendation (Proceed / Proceed with conditions / Hold / Do not proceed), and a focused list of follow-up questions for the vendor's security team. Triggers on phrases like "review this SOC 2," "diligence this vendor," or sharing a SOC 2 PDF with vendor context.

## What this is not

- Not a substitute for a full vendor risk management program — it's a focused diligence pass on a single artifact.
- Not legal or audit advice. The output is a structured opinion, not a determination of compliance with any framework.
- Not a SOC 2 compliance gap assessment for *your own* program. This is for evaluating someone else's report.

## Install

```
/plugin marketplace add https://github.com/Fencer-Security/skills
/plugin install compliance@fencer
```

## License

[Apache-2.0](../../LICENSE).
