#!/usr/bin/env python3
from pathlib import Path
import sys

from generate_strict_page import build_patterns, run_regression_tests

ROOT = Path(__file__).resolve().parents[1]
errors = []
filter_dist = ROOT / "filters" / "dist" / "temizweb-main.txt"
strict_source = ROOT / "filters" / "src" / "35-strict-page.txt"
social_addiction = ROOT / "filters" / "src" / "15-social-addiction.txt"
social_content = ROOT / "filters" / "src" / "25-social-content.txt"


for path, marker, requirements in (
    (
        social_addiction,
        "INTENTIONAL SOCIAL MEDIA MODE",
        (
            "YouTube desktop root homepage rich grid",
            "Instagram Explore post tiles",
            "X home tab strip",
            "youtube.com##ytd-rich-grid-renderer:matches-path",
            "instagram.com##article:matches-path",
            "x.com##article[data-testid=\"tweet\"]",
        ),
    ),
    (
        social_content,
        "SOCIAL PMO CONTENT FILTER",
        (
            "youtube.com#?#ytd-video-renderer",
            "instagram.com#?#article",
            "x.com#?#article[data-testid=\"tweet\"]",
            ":not(:has-text(",
        ),
    ),
):
    if not path.exists():
        errors.append(f"missing generated {path.relative_to(ROOT)}")
        continue
    value = path.read_text(encoding="utf-8")
    if marker not in value:
        errors.append(f"{path.name} missing marker: {marker}")
    for required in requirements:
        if required not in value:
            errors.append(f"{path.name} missing required rule/signal: {required}")

    forbidden = (
        "studio.youtube.com",
        "tweetTextarea_0",
        "input[type=\"file\"]",
        "div[role=\"dialog\"]",
    )
    for token in forbidden:
        if token in value:
            errors.append(
                f"{path.name} unexpectedly targets production/upload surface: {token}"
            )

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
    if "INTENTIONAL SOCIAL MEDIA MODE" not in text:
        errors.append("merged uBlock output missing social anti-addiction layer")
    if "SOCIAL PMO CONTENT FILTER" not in text:
        errors.append("merged uBlock output missing social PMO content layer")

    generic_rules = [
        line for line in text.splitlines()
        if line.startswith("*##") and ":has-text(" in line
    ]
    if generic_rules:
        missing_recovery_guard = [
            line for line in generic_rules
            if r"never\s*fap" not in line
            or r"pornoyu\s+b[ıi]rak" not in line
        ]
        if missing_recovery_guard:
            errors.append(
                "generic content rules missing shared PMO recovery override: "
                f"{len(missing_recovery_guard)} rule(s)"
            )

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
