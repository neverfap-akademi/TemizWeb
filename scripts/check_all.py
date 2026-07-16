#!/usr/bin/env python3

from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

filter_dist = ROOT / "filters" / "dist" / "temizweb-main.txt"
strict_source = ROOT / "filters" / "src" / "35-strict-page.txt"


if not strict_source.exists():
    errors.append(
        "missing generated filters/src/35-strict-page.txt"
    )
else:
    strict_text = strict_source.read_text(encoding="utf-8")

    strict_requirements = (
        "UNIVERSAL STRICT FULL-PAGE INTENT FILTER",
        ":has(title:has-text(",
        ":has(h1:has-text(",
        ":matches-path(",
        "ifşa",
        "ifsa",
        "leaked",
        "çıplak",
        "ciplak",
        "nude",
        "hot",
        "sexy",
        "intikam",
        "victim",
        "mağdur",
        r"porn\s+recovery",
    )

    for required in strict_requirements:
        if required not in strict_text:
            errors.append(
                "strict-page source missing: " + required
            )

    active_strict = [
        line.strip()
        for line in strict_text.splitlines()
        if line.strip()
        and not line.lstrip().startswith("!")
    ]

    if len(active_strict) != 3:
        errors.append(
            "strict-page source must contain exactly "
            f"3 active generated rules, found {len(active_strict)}"
        )


if not filter_dist.exists():
    errors.append(
        "missing filters/dist/temizweb-main.txt"
    )
else:
    text = filter_dist.read_text(encoding="utf-8")

    for header in (
        "! Title:",
        "! Version:",
        "! License:",
        "! Expires:",
    ):
        if header not in text:
            errors.append("missing " + header)

    active = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
        and not line.lstrip().startswith("!")
    ]

    if len(active) != len(set(active)):
        errors.append("duplicate uBlock rules")

    if len(active) < 20:
        errors.append("too few uBlock rules")

    merged_requirements = (
        "UNIVERSAL STRICT FULL-PAGE INTENT FILTER",
        ":has(title:has-text(",
        ":has(h1:has-text(",
        ":matches-path(",
    )

    for required in merged_requirements:
        if required not in text:
            errors.append(
                "merged uBlock output missing strict-page marker: "
                + required
            )


dns_domain_files = list(
    (ROOT / "dns" / "dist").glob("*-domains.txt")
)

for path in sorted(dns_domain_files):
    domains = [
        line.strip()
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
        and not line.startswith("#")
    ]

    if domains != sorted(set(domains)):
        errors.append(
            path.name + " not sorted/unique"
        )


if not dns_domain_files:
    errors.append("missing DNS outputs")


if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)


print("All generated outputs passed validation")
