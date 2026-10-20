#!/usr/bin/env python3
"""Offline integrity checks for a paper companion; never a research-validity test.

Standard library only. Run from scripts/ after installation, or use --root PATH.
JSON checks enforce a small shared contract without assuming an empirical paper.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REQUIRED = (
    "README.md", "AGENTS.md", "LLMS.txt", "ATTRIBUTION.md", "LICENSE",
    "CONTRIBUTING.md", "CITATION.cff", "references/paper.bib",
    "metadata/paper.json", "metadata/claims.json", "metadata/sources.json",
)
SKIP = {".git", "__pycache__", ".venv", "node_modules"}


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"nonstandard JSON constant: {value}")


def plain_markdown(text):
    """Remove fenced blocks; verify matching fence style and minimum length."""
    result, opening = [], None
    for number, line in enumerate(text.splitlines(), 1):
        fence = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if opening is None:
            if fence:
                opening = (fence[1][0], len(fence[1]), number)
            else:
                result.append(line)
        elif fence and fence[1][0] == opening[0] and len(fence[1]) >= opening[1] and not fence[2].strip():
            opening = None
    return "\n".join(result), opening


def anchors(text):
    found, duplicates = set(), {}
    stripped, _ = plain_markdown(text)
    headings = []
    lines = stripped.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            headings.append(match[1])
        elif index and re.fullmatch(r"\s{0,3}(?:=+|-+)\s*", line) and lines[index - 1].strip():
            headings.append(lines[index - 1].strip())
    for title in headings:
        title = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", title)
        title = re.sub(r"<[^>]+>", "", title).lower()
        base = "".join(ch for ch in title if ch.isalnum() or ch in "_- ").replace(" ", "-")
        count = duplicates.get(base, 0)
        duplicates[base] = count + 1
        found.add(base if count == 0 else f"{base}-{count}")
    found.update(re.findall(r'<a\b[^>]*(?:name|id)=["\']([^"\']+)', stripped, re.I))
    return found


def markdown_destinations(text):
    """Yield inline and reference-definition destinations, including images.

    Balanced parentheses in destinations are supported. Markdown's complete
    grammar is deliberately outside this small offline check.
    """
    for match in re.finditer(r"\]\(\s*", text):
        start = match.end()
        if start < len(text) and text[start] == "<":
            end = text.find(">", start + 1)
            if end != -1:
                yield text[start + 1:end]
            continue
        depth, end = 0, start
        while end < len(text):
            char = text[end]
            if char == "\\":
                end += 2
                continue
            if char == "(":
                depth += 1
            elif char == ")":
                if depth == 0:
                    break
                depth -= 1
            elif char.isspace() and depth == 0:
                break
            end += 1
        if end > start:
            yield text[start:end]
    for match in re.finditer(r"^\s{0,3}\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))", text, re.M):
        yield match[1] or match[2]


class Validator:
    def __init__(self, root):
        self.root = root.resolve()
        self.errors = []
        self.counts = {"files": 0, "modules": 0, "local_links": 0,
                       "external_links": 0, "paper_page_links": 0, "claims": 0,
                       "results": 0, "metric_values": 0}
        self.paper = {}
        self.page_count = None
        self.primary_urls = set()

    def require(self, condition, message):
        if not condition:
            self.errors.append(message)

    def read_json(self, relative):
        try:
            value = json.loads((self.root / relative).read_text(encoding="utf-8"),
                               object_pairs_hook=strict_object, parse_constant=invalid_constant)
            self.require(isinstance(value, dict), f"{relative}: top level must be an object")
            if not isinstance(value, dict):
                return {}
            self.require(value.get("schema_version") == "1.0.0", f"{relative}: schema_version must be 1.0.0")
            return value
        except (OSError, UnicodeError, ValueError) as error:
            self.errors.append(f"{relative}: {error}")
            return {}

    def url(self, value, context, current=None):
        try:
            parsed = urlsplit(value)
        except ValueError as error:
            self.errors.append(f"{context}: invalid URL {value}: {error}")
            return
        if parsed.scheme:
            self.require(parsed.scheme in {"http", "https", "mailto"}, f"{context}: unexpected URL scheme {value}")
            if parsed.scheme in {"http", "https"}:
                self.require(bool(parsed.netloc), f"{context}: URL has no host: {value}")
            self.counts["external_links"] += 1
            base = value.split("#", 1)[0]
            is_pdf = base in self.primary_urls or parsed.path.lower().endswith(".pdf") or "/pdf/" in parsed.path
            if is_pdf and parsed.fragment.startswith("page="):
                match = re.fullmatch(r"page=(\d+)", parsed.fragment)
                self.require(bool(match), f"{context}: invalid PDF page fragment: {value}")
                if match:
                    page = int(match[1])
                    self.require(page >= 1, f"{context}: PDF pages are one-based: {value}")
                    if base in self.primary_urls and self.page_count:
                        self.require(page <= self.page_count, f"{context}: primary PDF page exceeds {self.page_count}: {value}")
                        self.counts["paper_page_links"] += 1
            return
        if parsed.netloc:
            self.errors.append(f"{context}: use an explicit HTTPS URL: {value}")
            return
        if current is None:
            return
        path = unquote(parsed.path).replace("\\", "/")
        target = (current.parent / path).resolve() if path else current
        try:
            target.relative_to(self.root)
        except ValueError:
            self.errors.append(f"{context}: local link escapes repository: {value}")
            return
        self.counts["local_links"] += 1
        self.require(target.is_file(), f"{context}: missing local file: {value}")
        if target.is_file() and parsed.fragment:
            try:
                self.require(unquote(parsed.fragment) in anchors(target.read_text(encoding="utf-8")),
                             f"{context}: missing local anchor: {value}")
            except (OSError, UnicodeError) as error:
                self.errors.append(f"{context}: cannot check anchor {value}: {error}")

    def walk_json(self, value, context):
        if isinstance(value, dict):
            for key, child in value.items():
                self.walk_json(child, f"{context}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                self.walk_json(child, f"{context}[{index}]")
        elif isinstance(value, str) and re.match(r"https?://", value):
            self.url(value, context)

    def pages(self, value, context):
        if type(value) is int:
            self.require(self.page_count is not None and 1 <= value <= self.page_count,
                         f"{context}: page outside 1..{self.page_count}: {value}")
        elif isinstance(value, list):
            self.require(bool(value), f"{context}: empty page list")
            for child in value:
                self.pages(child, context)
        elif isinstance(value, str):
            self.require(bool(re.fullmatch(r"\d+(?:\s*[-–]\s*\d+)?(?:\s*,\s*\d+(?:\s*[-–]\s*\d+)?)*", value)),
                         f"{context}: malformed page range: {value}")
            for number in re.findall(r"\d+", value):
                self.pages(int(number), context)
            for first, last in re.findall(r"(\d+)\s*[-–]\s*(\d+)", value):
                self.require(int(first) <= int(last), f"{context}: reversed page range: {value}")
        else:
            self.errors.append(f"{context}: page value must be an integer, range, or list")

    def claim_source(self, value, context, source_ids):
        if isinstance(value, str):
            if re.match(r"https?://", value):
                self.url(value, context)
            else:
                self.require(value in source_ids, f"{context}: unknown source ID: {value}")
        elif isinstance(value, dict):
            if "source_id" in value:
                self.require(value["source_id"] in source_ids, f"{context}: unknown source_id: {value['source_id']}")
            for key in ("page", "pages", "pdf_page", "pdf_pages"):
                if key in value:
                    self.pages(value[key], f"{context}.{key}")
            if "page" in value and isinstance(value.get("url"), str) and type(value["page"]) is int:
                fragment = urlsplit(value["url"]).fragment
                if fragment.startswith("page="):
                    self.require(fragment == f"page={value['page']}", f"{context}: page/URL mismatch")
        else:
            self.errors.append(f"{context}: source must be an object, URL, or source ID")

    def results(self, data, source_ids, expected_version):
        """Check optional author-reported numerical summaries, never reproduce them."""
        if expected_version and data.get("paper_version") is not None:
            self.require(data["paper_version"] == expected_version, "results.paper_version mismatch")
        rows = data.get("results")
        self.require(isinstance(rows, list) and bool(rows), "results.results must be a nonempty array")
        if not isinstance(rows, list):
            return
        self.counts["results"] = len(rows)
        ids = [row.get("id") for row in rows if isinstance(row, dict)]
        self.require(len(ids) == len(rows) and all(isinstance(identifier, str) and identifier for identifier in ids),
                     "Each result needs a nonempty string ID")
        self.require(len(ids) == len(set(str(identifier) for identifier in ids)), "Duplicate result IDs")

        def finite(value):
            return type(value) in (int, float) and math.isfinite(value)

        for index, row in enumerate(rows):
            context = f"results[{index}]"
            if not isinstance(row, dict):
                continue
            self.require(bool(row.get("denominator")), f"{context}: denominator is required")
            self.require(bool(row.get("caveats") or row.get("limitations")), f"{context}: caveats or limitations are required")
            self.require(row.get("reproduced") is None or row["reproduced"] is False,
                         f"{context}: reproduced must be false when supplied")
            metric = row.get("metric")
            self.require(isinstance(metric, str) and bool(metric.strip()), f"{context}: metric is required")
            percent = isinstance(metric, str) and metric.casefold().endswith("percent")
            evidence = row.get("sources", [])
            self.require(isinstance(evidence, list) and bool(evidence), f"{context}: sources must be a nonempty array")
            if isinstance(evidence, list):
                for number, source in enumerate(evidence):
                    self.claim_source(source, f"{context}.sources[{number}]", source_ids)
            for key in ("page", "pages", "pdf_page", "pdf_pages"):
                if key in row:
                    self.pages(row[key], f"{context}.{key}")
            values = row.get("values")
            self.require(isinstance(values, list) and bool(values), f"{context}: values must be a nonempty array")
            if not isinstance(values, list):
                continue
            for number, item in enumerate(values):
                location = f"{context}.values[{number}]"
                self.counts["metric_values"] += 1
                self.require(isinstance(item, dict), f"{location}: value entry must be an object")
                if not isinstance(item, dict):
                    continue
                value = item.get("value")
                self.require(finite(value), f"{location}: value must be numeric and finite")
                if finite(value) and percent:
                    self.require(0 <= value <= 100, f"{location}: percent value must be in 0..100")
                if "ci95" in item:
                    interval = item["ci95"]
                    valid_interval = isinstance(interval, list) and len(interval) == 2 and all(finite(endpoint) for endpoint in interval)
                    self.require(valid_interval, f"{location}: ci95 must contain two finite numeric endpoints")
                    if valid_interval:
                        lower, upper = interval
                        self.require(lower <= upper, f"{location}: ci95 lower bound exceeds upper bound")
                        if finite(value):
                            self.require(lower <= value <= upper, f"{location}: value lies outside ci95")
                        if percent:
                            self.require(0 <= lower <= upper <= 100, f"{location}: percent ci95 must be in 0..100")

    def run(self):
        for relative in REQUIRED:
            self.require((self.root / relative).is_file(), f"Missing required file: {relative}")
        modules = sorted((self.root / "docs").glob("*.md"))
        self.counts["modules"] = len(modules)
        self.require(len(modules) >= 6, "docs/: expected at least six reading modules")
        paper = self.paper = self.read_json("metadata/paper.json")
        claims = self.read_json("metadata/claims.json")
        sources = self.read_json("metadata/sources.json")
        self.page_count = paper.get("page_count")
        self.require(type(self.page_count) is int and self.page_count > 0, "paper.page_count must be a positive integer")
        if type(self.page_count) is not int or self.page_count <= 0:
            self.page_count = None
        self.require(isinstance(paper.get("title"), str) and bool(paper["title"].strip()), "paper.title is required")

        def gather_urls(value, key=""):
            if isinstance(value, dict):
                for child_key, child in value.items():
                    gather_urls(child, child_key)
            elif isinstance(value, list):
                for child in value:
                    gather_urls(child, key)
            elif isinstance(value, str) and value.startswith("https://") and ("pdf" in key.lower() or "/pdf/" in value or value.split("#")[0].lower().endswith(".pdf")):
                self.primary_urls.add(value.split("#", 1)[0])
        gather_urls(paper)
        for name, value in (("paper", paper), ("claims", claims), ("sources", sources)):
            self.walk_json(value, name)

        authors = paper.get("authors", [])
        self.require(isinstance(authors, list) and bool(authors), "paper.authors must be a nonempty ordered array")
        if not isinstance(authors, list):
            authors = []
        author_names = [a.get("name") if isinstance(a, dict) else a for a in authors]
        self.require(all(isinstance(name, str) and name.strip() for name in author_names), "Every paper author needs a name")
        self.require(len(author_names) == len(set(str(name) for name in author_names)), "Duplicate paper authors")
        companion = paper.get("companion", {})
        self.require(isinstance(companion, dict) and companion.get("experiments_run") is False,
                     "paper.companion.experiments_run must be false")
        if isinstance(companion, dict) and "implementation_reproduced" in companion:
            self.require(companion["implementation_reproduced"] is False, "Companion must not claim an implementation reproduction")
        provenance = paper.get("provenance", {})
        self.require(isinstance(provenance, dict) and bool(provenance), "paper.provenance must record the content route and version")
        if isinstance(provenance, dict):
            for key in ("sha256", "attachment_sha256"):
                if provenance.get(key) is not None:
                    self.require(bool(re.fullmatch(r"[0-9a-f]{64}", str(provenance[key]))), f"paper.provenance.{key}: malformed SHA-256")
            for key in ("pdf_redistributed", "full_text_redistributed", "original_figures_redistributed"):
                if key in provenance:
                    self.require(provenance[key] is False, f"paper.provenance.{key} must be false")

        source_list = sources.get("sources", [])
        self.require(isinstance(source_list, list) and bool(source_list), "sources.sources must be a nonempty array")
        if not isinstance(source_list, list):
            source_list = []
        source_ids = [s.get("id") for s in source_list if isinstance(s, dict)]
        self.require(len(source_ids) == len(source_list) and all(isinstance(s, str) and s for s in source_ids), "Each source needs a nonempty string ID")
        self.require(len(source_ids) == len(set(str(s) for s in source_ids)), "Duplicate source IDs")
        claim_list = claims.get("claims", [])
        self.require(isinstance(claim_list, list) and bool(claim_list), "claims.claims must be a nonempty array")
        if not isinstance(claim_list, list):
            claim_list = []
        claim_ids = [c.get("id") for c in claim_list if isinstance(c, dict)]
        self.counts["claims"] = len(claim_list)
        self.require(len(claim_ids) == len(claim_list) and all(isinstance(c, str) and c for c in claim_ids), "Each claim needs a nonempty string ID")
        self.require(len(claim_ids) == len(set(str(c) for c in claim_ids)), "Duplicate claim IDs")
        for index, claim in enumerate(claim_list):
            context = f"claims[{index}]"
            if not isinstance(claim, dict):
                continue
            self.require(isinstance(claim.get("kind"), str) and bool(claim["kind"].strip()), f"{context}: kind is required")
            self.require(bool(claim.get("scope")), f"{context}: scope is required")
            self.require(bool(claim.get("caveats") or claim.get("limitations")), f"{context}: caveats or limitations are required")
            evidence = claim.get("sources", claim.get("evidence", []))
            self.require(isinstance(evidence, list) and bool(evidence), f"{context}: sources/evidence must be a nonempty array")
            if isinstance(evidence, list):
                for number, source in enumerate(evidence):
                    self.claim_source(source, f"{context}.sources[{number}]", source_ids)
            for key in ("page", "pages", "pdf_page", "pdf_pages"):
                if key in claim:
                    self.pages(claim[key], f"{context}.{key}")

        results_path = self.root / "metadata/results.json"
        if results_path.exists():
            result_data = self.read_json("metadata/results.json")
            self.results(result_data, source_ids, paper.get("version", claims.get("paper_version")))

        texts = {}
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or any(part in SKIP for part in path.relative_to(self.root).parts):
                continue
            self.counts["files"] += 1
            relative = str(path.relative_to(self.root))
            self.require(path.suffix.lower() != ".pdf", f"{relative}: source PDFs must not be redistributed")
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                self.errors.append(f"{relative}: not readable UTF-8 text: {error}")
                continue
            texts[path.relative_to(self.root).as_posix()] = text
            self.require("\ufffd" not in text, f"{relative}: Unicode replacement character")
            self.require(not any(ord(ch) < 32 and ch not in "\n\r\t" for ch in text), f"{relative}: control character")
            self.require(not re.search(r"^<PARSED TEXT FOR PAGE: \d+ / \d+>", text, re.M), f"{relative}: raw source extraction marker")
            if path.suffix.lower() in {".md", ".txt"}:
                stripped, fence = plain_markdown(text)
                self.require(fence is None, f"{relative}: unclosed code fence at line {fence[2] if fence else '?'}")
                for destination in markdown_destinations(stripped):
                    self.url(destination, relative, path)
                definitions = {re.sub(r"\s+", " ", label).casefold() for label in
                               re.findall(r"^\s{0,3}\[([^\]]+)\]:", stripped, re.M)}
                for label, reference in re.findall(r"!?\[([^\]]+)\]\[([^\]]*)\]", stripped):
                    reference = re.sub(r"\s+", " ", reference or label).casefold()
                    self.require(reference in definitions, f"{relative}: undefined Markdown reference: {reference}")
            if path.suffix.lower() == ".json" and path.relative_to(self.root).as_posix() not in {
                    "metadata/paper.json", "metadata/claims.json", "metadata/sources.json"}:
                try:
                    additional = json.loads(text, object_pairs_hook=strict_object, parse_constant=invalid_constant)
                    self.walk_json(additional, relative)
                except ValueError as error:
                    self.errors.append(f"{relative}: {error}")

        cff = texts.get("CITATION.cff", "")
        bib = texts.get("references/paper.bib", "")
        self.require(bool(re.search(r"^cff-version:\s*['\"]?1\.2\.0", cff, re.M)), "CITATION.cff: expected cff-version 1.2.0")
        self.require("preferred-citation:" in cff, "CITATION.cff: missing preferred-citation")
        preferred = cff.split("preferred-citation:", 1)[-1]
        for author in authors:
            if not isinstance(author, dict):
                self.require(str(author) in bib and str(author) in preferred, f"Citation omits author: {author}")
                continue
            name, given, family = author.get("name", ""), author.get("given", ""), author.get("family", "")
            valid_parts = isinstance(given, str) and isinstance(family, str) and bool(given and family)
            self.require(valid_parts, f"paper author {name}: given and family strings required for citation crosscheck")
            if not valid_parts:
                continue
            self.require(f"{family}, {given}" in bib or f"{given} {family}" in bib, f"BibTeX omits author: {name}")
            for key, value in (("given-names", given), ("family-names", family)):
                pattern = rf"{key}:\s*(?:\"{re.escape(value)}\"|'\s*{re.escape(value)}\s*'|{re.escape(value)}\s*(?:\n|$))"
                self.require(bool(re.search(pattern, preferred)), f"CFF preferred citation omits {key} for {name}")
            for document in ("README.md", "ATTRIBUTION.md"):
                self.require(name in texts.get(document, ""), f"{document}: omits paper author {name}")
        for key in ("version", "paper_version"):
            if key in paper and key in claims:
                self.require(paper[key] == claims[key], f"paper/claims {key} mismatch")
        if paper.get("version") is not None and claims.get("paper_version") is not None:
            self.require(paper["version"] == claims["paper_version"], "paper.version/claims.paper_version mismatch")
        arxiv = paper.get("arxiv", {})
        if isinstance(arxiv, dict) and arxiv.get("id") and arxiv.get("version") and claims.get("paper_version"):
            self.require(claims["paper_version"] == f"{arxiv['id']}{arxiv['version']}", "paper arXiv/claims paper_version mismatch")

        if self.errors:
            for error in self.errors:
                print(f"ERROR: {error}")
            return 1
        print("PASS: " + ", ".join(f"{key}={value}" for key, value in self.counts.items()))
        print("Scope: UTF-8 documents, required modules, strict JSON, author citations, local links/anchors, source IDs, PDF page bounds, and optional result values/intervals.")
        print("Limits: no external reachability, complete Markdown/CFF schema, plagiarism detection, source truth, experimental reproduction, or research validity check.")
        return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    return Validator(args.root).run()


if __name__ == "__main__":
    sys.exit(main())
