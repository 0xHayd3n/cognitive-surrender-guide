# Verification and limits

Prepared on **2026-10-20**, on **HaydenPC**, following the maintainer's established [Harness Learning Guide](https://github.com/0xHayd3n/harness-learning-guide) format.

## Source coverage

- Read the complete actual attached `ssrn-6097646.pdf` through Library: 58 PDF pages, cover marker v20260111, all manuscript sections, tables, figure captions, and references.
- Independently reviewed study designs, denominators, selected reported percentages/CIs/odds, profile thresholds, null interactions, and reporting caveats against that attachment.
- Inspected Tables 1–2 and Figures 1–10 in the official OSF v1 PDF with matching title, authors, cover marker, page count, and reference endpoint. No chart values were digitized.
- The auxiliary public PDF hash is `6d7b00690f4aa5bbf9b4db8b2e3e9aa6585ba40977ad9e554393d88ee313f90d`. Its 1,891,090 bytes differ from the attachment's 1,912,650 bytes. No attachment binary equality is claimed; attachment text remains the content source.
- Crossref verified SSRN DOI/title/authors/year. Official OSF metadata verified its v1 dates, CC0 record license, PDF, and materials link. The attachment's own reuse license remains unestablished.
- The linked OSF materials/preregistration project and its file list returned **401 Unauthorized**. The public preprint inventory contained only the main PDF. Web Appendices A–D and W1–W3 remain uninspected. Exact exclusions, prompts, registration timing, and reported-count reconciliation cannot be independently audited here.

## Repository checks

Run from this repository:

```bash
python scripts/validate_repository.py
```

The validator checks UTF-8 text, required modules/files, strict JSON, all-author citation consistency, local Markdown links/anchors, source identifiers, claim scope/caveats, numeric PDF page bounds, optional result identifiers/values/intervals/denominators, and version consistency. No PDF or raw source extraction is included.

Public publication checks are recorded below once the repository has been published.

## Scientific scope

No participants were recruited, models trained, statistics rerun, or results replicated. Repository checks cannot prove the theory, recover unavailable supplements, or resolve the manuscript's sample/trial/effect-size differences. Conceptual propositions, author interpretations, selected usage associations, and experimental contrasts are labeled separately throughout the guide.
