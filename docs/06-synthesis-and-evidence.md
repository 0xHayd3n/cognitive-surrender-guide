# 6. Synthesis, evidence, and reporting audit

[Home](../README.md) · [Previous: Study 3](05-study-3.md) · [Next: limitations](07-limits-and-discussion.md)

Source: General Discussion, especially pp. 41–46 and Figure 10. [Corresponding public v1 PDF, p. 41](https://osf.io/download/9gxaq/#page=41) · [SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6097646). Machine-readable selected measurements: [results.json](../metadata/results.json).

## What is pooled

The authors describe a preregistered trial-level synthesis across their own studies: N=1,372 and 9,593 trials, including the ancillary Study 1 online sample. This is a within-paper synthesis, not an independent external meta-analysis or a replication conducted by this guide. Study contexts, no-AI baselines, and confidence measurement differ. The authors include platform/context information in the modeling as described in their analysis section. (pp. 20–21, 41–42.)

The pooled accurate-versus-faulty contrast is OR=16.07, 95% CI [11.50,22.46]. Per-study Cohen's h values listed in this section are .83, .86, and .78; the trial-weighted h is .82. The AI-quality gap remains under time pressure (OR=14.28, 95% CI [8.51,23.98]) and incentives plus feedback (OR=11.05, 95% CI [6.48,18.83]). These are modeled odds contrasts, not ratios of raw accuracy. (p. 42.)

Figure 10 plots model-predicted correctness against frequency of use, with confidence bands and rug plots. It illustrates that heavy use aligns performance more strongly with recommendation quality. Because degree of use is selected, a dose-like association cannot on its own establish that forcing an additional consultation causes the plotted change. No chart values have been estimated from pixels in this companion. (p. 43.)

## Individual differences

Higher Trust in AI is associated with a larger accurate/faulty performance divergence: OR=2.81, 95% CI [2.36,3.34]. NFC and fluid intelligence are associated with smaller divergences: OR=.83, 95% CI [.70,.98], and OR=.69, 95% CI [.57,.83]. These are observational moderators, with z-scored traits, not experimentally assigned capacities. The mixed pattern within individual studies should remain visible alongside pooled effects. (p. 44.)

## The operational split between surrender and offloading

Among **consulted, faulty-AI trials**, the authors report 73.2% following the wrong answer, 19.7% overriding it and getting the answer right, and 7.1% overriding but remaining wrong. They label these surrender, offloading, and failed override. This is a useful outcome partition; it is narrower than a direct assessment of subjective agency or every type of strategic offloading. (p. 44.)

With incentives plus feedback, the reported shares become 57.9% surrender and 37.1% successful offloading, with roughly 5% failed overrides. Under pressure, successful offloading is 6.2% and failed override 13.8%. These conditional percentages are not prevalence estimates of cognitive surrender in society. Trait associations likewise concern this defined contrast, not a permanent user diagnosis.

## Reporting audit

These are unresolved features of the studied manuscript. They should be checked against supplement, data, or author clarification before exact reconciliation.

| Issue | What the source says | How this guide handles it |
| --- | --- | --- |
| Participant total | Main study Ns 359+485+450=1,294; adding the ancillary 81 yields 1,375. Pooled N is 1,372. | Retain the reported analysis N; flag the three-person difference. Do not invent exclusions. |
| Trial total | 1,372 × 7 gives 9,604, versus reported 9,593 trials. | Do not assume a complete seven-trial record for every pooled participant; missing/excluded trials are not explained in the attachment. |
| Study 1 effect size | Study 1 narrative gives h=.81 with CI [.72,.91] on p. 25; synthesis lists S1 h=.83 on p. 42. | Preserve location-specific values; no claim of an error or identical analysis set. |
| Figure 10 counts | Caption lists Brain-Only Inc+Fd=212, Control=1,530, Timer=227; Study 3 methods assign 238 to Inc+Fd and 212 to control. | Caption and assigned sample counts may reflect different analysis sets or labeling; unresolved. Do not use the caption to overwrite methods. |
| Supplement availability | A–D and W1–W3 are referenced but absent from the attached 58 pages. | Mark them uninspected and describe only the purposes explicitly stated in the manuscript. |

The first two arithmetic comparisons are companion checks, not author-reported findings. A discrepancy is not evidence of misconduct or a demonstration that the main effect disappears. It is a limit on how precisely the guide can reconstruct analysis populations without the materials.

## What the evidence does and does not separate

Random assignment helps support effects of the timer, intervention bundle, availability, and engineered advice quality in their respective designs. Final answers do not uniquely separate surrender, mistaken verification, rational deference under uncertainty, and all possible advice-taking mechanisms. The broad Tri-System proposal and mechanism language about suppressed deliberation remain interpretations requiring converging measures. This distinction is preserved in [claims.json](../metadata/claims.json).
