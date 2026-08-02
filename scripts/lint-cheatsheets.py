#!/usr/bin/env python3
"""Lint cheatsheet files against the format described in CLAUDE.md.

Usage:
    scripts/lint-cheatsheets.py [FILE...]   # defaults to cheatsheet-files/*.md
    scripts/lint-cheatsheets.py --strict    # treat warnings as errors
    scripts/lint-cheatsheets.py --list-rules

Exit status: 0 = clean (warnings allowed), 1 = errors found, 2 = bad invocation.
"""

import argparse
import fnmatch
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHEAT_DIR = REPO_ROOT / "cheatsheet-files"
IGNORE_FILE = REPO_ROOT / ".cheatlintignore"

# `#platform/x #target/y #cat/z` -- target may contain spaces/commas (see crowdsec.md).
TAG_RE = re.compile(r"^#platform/(\S+)\s+#target/(.+?)\s+#cat/(\S+)\s*$")
KEYWORD_RE = re.compile(r"^%\s*(.+?)\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE_RE = re.compile(r"^(```+)\s*(\S*)")
SECTION_RE = re.compile(r"^(?P<tool>.+?)\s+-\s+(?P<action>.+)$")

RULES = {
    "preamble": "file must start with the `# Title` heading (no generator preamble)",
    "title": "exactly one level-1 heading, and it must be the first heading",
    "description": "a description paragraph must follow the title",
    "tag-line": "a `#platform/... #target/... #cat/...` line is required",
    "keyword-line": "a `% keyword, keyword` line is required",
    "order": "order must be: title, description, tag line, keyword line, sections",
    "sections": "at least one `## Tool - Action` section is required",
    "section-heading": "`##` headings must read `## <Tool> - <Action>`",
    "section-tool": "the `##` tool prefix must match the title's tool name",
    "fence-balance": "code fences must be balanced",
    "section-example": "every section must contain at least one fenced command",
    "fence-lang": "code fences are conventionally unlabelled (warning)",
    "eof-newline": "file must end with a newline",
}


class Finding:
    def __init__(self, path, line, level, rule, message):
        self.path, self.line, self.level = path, line, level
        self.rule, self.message = rule, message

    def format(self, root=None):
        shown = self.path
        if root:
            try:
                shown = self.path.relative_to(root)
            except ValueError:
                pass
        return f"{shown}:{self.line}: {self.level} [{self.rule}] {self.message}"


class Linter:
    def __init__(self, path, text):
        self.path = path
        self.raw = text
        self.lines = text.splitlines()
        self.findings = []
        # Populated by _scan().
        self.headings = []   # (lineno, level, text)
        self.fences = []     # (lineno, info)
        self.in_fence = []   # bool per line index
        self.tag = None      # (lineno, match)
        self.keyword = None  # (lineno, match)

    def error(self, line, rule, message):
        self.findings.append(Finding(self.path, line, "error", rule, message))

    def warn(self, line, rule, message):
        self.findings.append(Finding(self.path, line, "warning", rule, message))

    def run(self):
        self._scan()
        self._check_header()
        self._check_sections()
        self._check_fences()
        self._check_eof()
        return self.findings

    def _scan(self):
        """Walk the file once, tracking fence state so `#` inside code is not a heading."""
        open_fence = None
        for idx, line in enumerate(self.lines):
            lineno = idx + 1
            fence = FENCE_RE.match(line)
            if fence:
                marker, info = fence.group(1), fence.group(2)
                if open_fence is None:
                    open_fence = marker
                    self.fences.append((lineno, info))
                    self.in_fence.append(True)
                    continue
                if marker.startswith(open_fence):
                    open_fence = None
                    self.in_fence.append(True)
                    continue
            self.in_fence.append(open_fence is not None)
            if open_fence is not None:
                continue
            heading = HEADING_RE.match(line)
            if heading:
                self.headings.append((lineno, len(heading.group(1)), heading.group(2)))
                continue
            if self.tag is None:
                tag = TAG_RE.match(line)
                if tag:
                    self.tag = (lineno, tag)
                    continue
            if self.keyword is None:
                keyword = KEYWORD_RE.match(line)
                if keyword:
                    self.keyword = (lineno, keyword)
        self.open_fence_at_eof = open_fence is not None

    def _first_content_line(self):
        for idx, line in enumerate(self.lines):
            if line.strip():
                return idx + 1, line
        return None, None

    def _check_header(self):
        lineno, line = self._first_content_line()
        if lineno is None:
            self.error(1, "title", "file is empty")
            return

        if not line.startswith("# "):
            self.error(
                lineno, "preamble",
                f"file must open with the `# Title` heading, found: {line[:60]!r}",
            )

        h1 = [h for h in self.headings if h[1] == 1]
        if not h1:
            self.error(lineno, "title", "no level-1 `# Title` heading found")
            return
        if len(h1) > 1:
            for extra in h1[1:]:
                self.error(extra[0], "title", f"unexpected second level-1 heading: {extra[2]!r}")
        if self.headings[0][1] != 1:
            self.error(
                self.headings[0][0], "title",
                f"first heading must be level-1, found level-{self.headings[0][1]}",
            )
        title_line = h1[0][0]

        if self.tag is None:
            self.error(title_line, "tag-line",
                       "missing `#platform/... #target/... #cat/...` line")
        if self.keyword is None:
            self.error(title_line, "keyword-line",
                       "missing `% keyword, keyword` keyword line")

        # Description: prose between the title and the tag line.
        stop = self.tag[0] if self.tag else (self.keyword[0] if self.keyword else len(self.lines) + 1)
        has_description = any(
            self.lines[i].strip() and not self.in_fence[i]
            for i in range(title_line, min(stop, len(self.lines)) )
            if not HEADING_RE.match(self.lines[i])
        )
        if not has_description:
            self.error(title_line, "description",
                       "no description paragraph between the title and the tag line")

        if self.tag and self.keyword and self.keyword[0] < self.tag[0]:
            self.error(self.keyword[0], "order",
                       "`%` keyword line must come after the `#platform/...` tag line")
        if self.tag and self.tag[0] < title_line:
            self.error(self.tag[0], "order", "tag line must come after the title")

        if self.keyword:
            terms = [t.strip() for t in self.keyword[1].group(1).split(",")]
            if not any(terms):
                self.error(self.keyword[0], "keyword-line", "keyword line has no keywords")

        sections = [h for h in self.headings if h[1] == 2]
        if sections and self.keyword and sections[0][0] < self.keyword[0]:
            self.error(sections[0][0], "order",
                       "sections must come after the tag and keyword lines")

    def _expected_tool(self):
        """Tool prefix expected on `##` headings, taken from the title's first token."""
        h1 = [h for h in self.headings if h[1] == 1]
        if not h1:
            return None
        return h1[0][2].split()[0] if h1[0][2].split() else None

    def _check_sections(self):
        sections = [h for h in self.headings if h[1] == 2]
        if not sections:
            self.error(1, "sections", "no `## Tool - Action` sections found")
            return

        expected = self._expected_tool()
        for lineno, _level, text in sections:
            match = SECTION_RE.match(text)
            if not match:
                self.error(lineno, "section-heading",
                           f"heading must read `## <Tool> - <Action>`, found: {text!r}")
                continue
            tool = match.group("tool")
            if expected and tool.lower() != expected.lower():
                self.error(lineno, "section-tool",
                           f"section prefix {tool!r} does not match title tool {expected!r}")

        # Each `##` section, including its `###` subsections, needs a runnable example.
        bounds = [s[0] for s in sections] + [len(self.lines) + 1]
        for i, (lineno, _level, text) in enumerate(sections):
            start, end = bounds[i], bounds[i + 1]
            if not any(start < f[0] < end for f in self.fences):
                self.error(lineno, "section-example",
                           f"section {text!r} contains no fenced command block")

    def _check_fences(self):
        if self.open_fence_at_eof:
            self.error(self.fences[-1][0] if self.fences else 1, "fence-balance",
                       "unclosed code fence")
        for lineno, info in self.fences:
            if info:
                self.warn(lineno, "fence-lang",
                          f"fence is labelled ```{info}; this collection uses unlabelled fences")

    def _check_eof(self):
        if self.raw and not self.raw.endswith("\n"):
            self.error(len(self.lines), "eof-newline", "file does not end with a newline")


def load_ignores():
    if not IGNORE_FILE.exists():
        return []
    patterns = []
    for line in IGNORE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    return patterns


def is_ignored(path, patterns):
    name = path.name
    try:
        rel = str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        rel = name
    return any(fnmatch.fnmatch(name, p) or fnmatch.fnmatch(rel, p) for p in patterns)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", type=Path,
                        help="files to lint (default: cheatsheet-files/*.md)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--no-ignore", action="store_true",
                        help="lint files listed in .cheatlintignore too")
    parser.add_argument("--list-rules", action="store_true", help="print the rules and exit")
    args = parser.parse_args(argv)

    if args.list_rules:
        for name, description in RULES.items():
            print(f"{name:18} {description}")
        return 0

    files = args.files or sorted(CHEAT_DIR.glob("*.md"))
    if not files:
        print("no cheatsheet files found", file=sys.stderr)
        return 2

    patterns = [] if args.no_ignore else load_ignores()
    findings, skipped, checked = [], [], 0
    for path in files:
        if is_ignored(path, patterns):
            skipped.append(path.name)
            continue
        if not path.is_file():
            print(f"{path}: no such file", file=sys.stderr)
            return 2
        checked += 1
        findings.extend(Linter(path, path.read_text(encoding="utf-8")).run())

    findings.sort(key=lambda f: (str(f.path), f.line))
    for finding in findings:
        print(finding.format(REPO_ROOT))

    errors = sum(1 for f in findings if f.level == "error")
    warnings = len(findings) - errors
    summary = f"{checked} file(s) checked, {errors} error(s), {warnings} warning(s)"
    if skipped:
        summary += f", {len(skipped)} skipped ({', '.join(sorted(skipped))})"
    print(summary)

    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
