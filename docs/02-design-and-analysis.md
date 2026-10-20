# 2. Design and analysis

[Home](../README.md) · [Previous: theory](01-theory-and-context.md) · [Next: Study 1](03-study-1.md)

Source: Empirical Overview pp. 18–21; study methods pp. 21–22, 27–28, 33; synthesis pp. 41–44. [Corresponding public v1 PDF, p. 18](https://osf.io/download/9gxaq/#page=18) · [SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6097646).

## The common task

Participants answer seven open-ended reasoning items adapted from the CRT-7. Each is designed to elicit a plausible intuitive error and a different correct response. In AI-available trials, the survey embeds GPT-4o. Participants retain control over their final answer and may consult the assistant repeatedly or ignore it. Hidden seed prompts manipulate whether the assistant supplies the correct response or the canonical intuitive error with an explanation. The paper does not report retraining model weights; the experimental intervention is prompt-controlled recommendation quality. (pp. 18–20.)

This is useful experimental control: it makes advice quality vary independently of participant skill. It is also an artificial environment. A roughly balanced manipulation of correct and faulty recommendations is not a measurement of GPT-4o's natural error rate. The study tests human response to engineered advice, not a model leaderboard.

## Three designs

| Study | Between-person assignment | Within-person trial variation | Baseline |
| --- | --- | --- | --- |
| 1 | Brain-Only n=121 versus AI-Assisted n=238 | Assigned AI recommendation quality among AI-Assisted participants | Separate randomized Brain-Only group |
| 2 | 30-second deadline n=228 versus untimed control n=257 | Assigned recommendation quality on available trials | One randomly positioned no-AI probe per participant |
| 3 | Incentives plus correctness feedback n=238 versus control n=212 | Assigned recommendation quality on available trials | One randomly positioned no-AI probe per participant |

The baseline changes after Study 1. A single probe inside an AI-enabled session is not the same exposure regime as an entire Brain-Only session. Trial order and prior feedback may matter; do not pool the baselines conceptually without retaining study context. (pp. 21–22, 27–28, 33.)

## Four denominators to keep separate

1. **All participants** in an assigned condition answer final questions.
2. **AI-available trials** have assigned correct/faulty advice even if the participant does not open chat.
3. **Chat-engaged trials** allow a conditional follow/override analysis.
4. **AI-Users and Independents** divide people by observed frequency of use, in Studies 2–3: at least two uses versus at most one.

The first two benefit from randomization. The latter two reflect choices made during the task. A comparison of frequent users with nonusers can reflect skill, trust, item difficulty, or other self-selection. It is not a randomized estimate of the effect of deciding to consult. A rate among consulted faulty trials should never be described as a rate among all participants.

## Measures and models

The principal outcomes are correctness, whether chat was used, and whether the AI recommendation was followed. Override and correctness are different variables: a person can reject AI and still be wrong. Confidence uses a 0–100 scale globally after the task in Studies 1–2, but after each item and before feedback in Study 3. These measures cannot be treated as one interchangeable confidence series. (p. 20; p. 33.)

The individual-difference measures are Trust in AI, Need for Cognition (NFC), a timed 13-item fluid-intelligence measure, and, only in Study 1, Need for Cognitive Closure (NFCC). The authors standardize individual-difference scores. These traits are measured, not assigned. Their associations do not show that manipulating a trait would cause the observed change. (pp. 20–21.)

The authors describe logistic generalized linear mixed models for binary outcomes and linear mixed models for confidence and log response times, with participant/item effects as applicable. Odds ratios (OR), raw coefficients, confidence intervals, and significance tests answer different questions. OR=4 does not mean four times the probability: probability depends on the baseline odds. Raw percentage differences are descriptive percentage-point contrasts. (pp. 20–21.)

## Open-science and access boundary

The manuscript describes the experiments and pooled synthesis as preregistered, reports University of Pennsylvania IRB approval #858904, and says materials, preregistrations, and codebooks are available through OSF. The attached text does not provide a project identifier. The official OSF preprint metadata separately links [osf.io/n84tx](https://osf.io/n84tx), but its project and file-list API returned 401 Unauthorized when checked. This confirms the authors' link, not access to the materials or registrations. This guide has not authenticated registrations, examined data, run models, or verified compliance with the registered plans. (pp. 19, 21, 41–42.)

Web Appendix B is named for supplementary methods; C for exclusions; D for hypotheses and statistics. Table W2 is named for exact items/answers and W3 for seed prompts. They are not embedded in the attachment. We therefore explain the reported procedure while leaving exact implementation, exclusion reconciliation, and registration auditing open. See [source map](08-source-map.md#external-supplements-referenced-but-not-included).
