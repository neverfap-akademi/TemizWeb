#!/usr/bin/env python3
from pathlib import Path
import sys

from generate_strict_page import build_patterns, run_regression_tests

ROOT = Path(__file__).resolve().parents[1]
errors = []
filter_dist = ROOT / "filters" / "dist" / "temizweb-main.txt"
strict_source = ROOT / "filters" / "src" / "35-strict-page.txt"

if not strict_source.exists():
    errors.append("missing generated filters/src/35-strict-page.txt")
else:
    strict_text = strict_source.read_text(encoding="utf-8")
    requirements = (
        "COMPACT HOSTNAME-TARGETED STRICT FULL-PAGE FILTER",
        "nitter.net", "ok.ru", "shutterstock.com", "pixabay.com",
        'textarea[name="q"]', 'input[name="q"]',
        ":matches-path(", ":watch-attr(value)", "#?#",
        ":upward(html)", ":not(:has-text(",
    )
    for required in requirements:
        if required not in strict_text:
            errors.append("strict-page source missing signal: " + required)

    active = [
        line.strip() for line in strict_text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    ]
    if len(active) < 150:
        errors.append(f"strict-page source has too few focused rules: {len(active)}")

    overlong = [len(line) for line in active if len(line) > 12000]
    if overlong:
        errors.append(
            "strict-page source contains overlong uBlock rules; "
            f"longest is {max(overlong)} characters"
        )

    try:
        page_risk, protected, url_risk = build_patterns()
        if not page_risk or not protected or not url_risk:
            errors.append("strict-page generated pattern is empty")
        run_regression_tests()
    except Exception as exc:
        errors.append("strict-page regression failure: " + str(exc))

if not filter_dist.exists():
    errors.append("missing filters/dist/temizweb-main.txt")
else:
    text = filter_dist.read_text(encoding="utf-8")
    active = [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("!")
    ]
    if len(active) != len(set(active)):
        errors.append("duplicate uBlock rules")
    if len(active) < 20:
        errors.append("too few uBlock rules")
    if "COMPACT HOSTNAME-TARGETED STRICT FULL-PAGE FILTER" not in text:
        errors.append("merged uBlock output missing strict-page layer")

files = list((ROOT / "dns" / "dist").glob("*-domains.txt"))
for path in sorted(files):
    domains = [
        line.strip() for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if domains != sorted(set(domains)):
        errors.append(path.name + " not sorted/unique")
if not files:
    errors.append("missing DNS outputs")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("All generated outputs passed validation")
