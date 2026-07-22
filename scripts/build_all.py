#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ipaddress
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from generate_strict_page import build_safe_pattern, generate_strict_page
from generate_social import generate_social_layers

ROOT = Path(__file__).resolve().parents[1]
FILTER_SRC = ROOT / "filters" / "src"
FILTER_DIST_DIR = ROOT / "filters" / "dist"
FILTER_DIST_MAIN = FILTER_DIST_DIR / "temizweb-main.txt"
FILTER_DIST_PMO = FILTER_DIST_DIR / "temizweb-pmo.txt"
FILTER_DIST_SOCIAL = FILTER_DIST_DIR / "temizweb-social.txt"
FILTER_DIST_MAIN_SAFARI = FILTER_DIST_DIR / "temizweb-main-safari.txt"
FILTER_DIST_PMO_SAFARI = FILTER_DIST_DIR / "temizweb-pmo-safari.txt"
FILTER_DIST_SOCIAL_SAFARI = FILTER_DIST_DIR / "temizweb-social-safari.txt"

# Anti-addiction UI files. Everything else remains in the PMO/content list.
# 10-youtube.txt is retained because the generated 15 layer contains the
# exceptions that safely override its older broad Shorts rules.
SOCIAL_SOURCE_NAMES = {
    "10-youtube.txt",
    "15-social-addiction.txt",
}
DNS_SRC = ROOT / "dns" / "src"
DNS_DIST = ROOT / "dns" / "dist"
UPSTREAMS = {
    "adblock": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/nsfw.txt",
}
DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$",
    re.I,
)


def fetch(url: str, attempts: int = 4) -> str:
    error = None
    for n in range(attempts):
        try:
            req = Request(url, headers={"User-Agent": "TemizWeb-Builder/1.0"})
            with urlopen(req, timeout=120) as response:
                data = response.read().decode("utf-8", errors="replace")
            if len(data) < 10000:
                raise RuntimeError(f"upstream response too small: {len(data)} bytes")
            return data
        except (URLError, HTTPError, TimeoutError, RuntimeError) as exc:
            error = exc
            time.sleep(2**n)
    raise RuntimeError(f"Could not download {url}: {error}")


def normalize_domain(raw: str):
    value = raw.strip().lower()
    if not value or value.startswith(("#", "!", "[")):
        return None
    if " " in value:
        parts = value.split()
        if len(parts) >= 2:
            try:
                ipaddress.ip_address(parts[0])
                value = parts[1]
            except ValueError:
                return None
    value = value.removeprefix("||").removesuffix("^").rstrip(".")
    if value.startswith("*."):
        value = value[2:]
    return value if DOMAIN_RE.fullmatch(value) else None


def read_domains(path: Path):
    out = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            domain = normalize_domain(line)
            if domain:
                out.add(domain)
    return out


def write_dns(name: str, domains: set[str]):
    ordered = sorted(domains)
    (DNS_DIST / f"{name}-domains.txt").write_text(
        "# TemizWeb DNS\n" + "\n".join(ordered) + "\n", encoding="utf-8"
    )
    (DNS_DIST / f"{name}-hosts.txt").write_text(
        "# TemizWeb DNS\n" + "\n".join("0.0.0.0 " + d for d in ordered) + "\n",
        encoding="utf-8",
    )
    (DNS_DIST / f"{name}-adguard.txt").write_text(
        "! Title: TemizWeb DNS\n" + "\n".join("||" + d + "^" for d in ordered) + "\n",
        encoding="utf-8",
    )




def deduplicate_filter_text(text: str) -> str:
    """Remove duplicate active uBlock rules while preserving comments/order.

    Generated social layers can intentionally supersede older handwritten
    rules that remain in filters/src. Keep the first occurrence so source
    ordering and exception priority stay stable, but preserve every comment
    and blank line for readability and attribution.
    """
    seen: set[str] = set()
    output: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("!"):
            output.append(line)
            continue
        if stripped in seen:
            continue
        seen.add(stripped)
        output.append(line)

    return "\n".join(output).rstrip() + "\n"



SAFARI_COSMETIC_RE = re.compile(
    r"^(?P<domains>[^#]+?)(?P<operator>#@#|#\?#|##)(?P<body>.+)$"
)
SAFARI_DOMAIN_RE = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$",
    re.I,
)


def build_safari_custom_filters(text: str) -> str:
    """Compile normal uBlock rules into Safari uBOL Custom Filters.

    Safari's Custom Filters UI works reliably with concrete, site-scoped
    cosmetic/procedural rules. Network and generic rules are omitted.

    Cosmetic exception rules (``#@#``) are not emitted directly because the
    Safari UI does not preserve them reliably. Instead, they are resolved at
    build time: an exact site-scoped hide rule cancelled by a matching
    exception is removed from the Safari output. This preserves intentional
    restores such as Instagram search and channel Shorts while keeping the
    narrower homepage/feed rules.
    """
    parsed_rules: list[tuple[str, str, str]] = []
    exceptions: set[tuple[str, str]] = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("!"):
            continue

        match = SAFARI_COSMETIC_RE.match(line)
        if not match:
            continue

        operator = match.group("operator")
        body = match.group("body").strip()
        if not body:
            continue

        for raw_domain in match.group("domains").split(","):
            domain = raw_domain.strip().lower()
            if not domain or domain.startswith("~") or domain == "*":
                continue
            if not SAFARI_DOMAIN_RE.fullmatch(domain):
                continue

            if operator == "#@#":
                exceptions.add((domain, body))
            else:
                parsed_rules.append((domain, operator, body))

    output: list[str] = []
    seen: set[str] = set()

    for domain, operator, body in parsed_rules:
        # Resolve exact cosmetic exceptions before serialising for Safari.
        # Both ## and #?# hide rules normalise to the same Safari ## form.
        if (domain, body) in exceptions:
            continue

        safari_rule = f"{domain}##{body}"
        if safari_rule in seen:
            continue
        seen.add(safari_rule)
        output.append(safari_rule)

    header = (
        "! Title: TemizWeb Safari Custom Filters\n"
        "! Generated automatically from the normal TemizWeb list.\n"
        "! Contains concrete site-scoped cosmetic/procedural rules only.\n"
        "! Network/DNS rules are omitted; cosmetic exceptions are resolved "
        "during generation.\n\n"
    )
    return header + "\n".join(output) + "\n"

def protect_generic_content(text: str) -> str:
    """Add the shared recovery override to generic card/article rules.

    Strict-page protection only prevents a whole-page hide. The older generic
    content layer can still hide the article element itself. This function
    adds the same high-confidence recovery/legal/education exception to every
    active procedural cosmetic rule in 40-generic-content.txt, without
    modifying the source file on disk.
    """
    safe = build_safe_pattern()
    guard = f":not(:has-text(/{safe}/iu))"
    output = []

    for line in text.splitlines():
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("!")
            and "##" in stripped
            and ":has-text(" in stripped
            and guard not in stripped
        ):
            line = line + guard
        output.append(line)

    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-dir", type=Path)
    args = parser.parse_args()

    if args.fixture_dir:
        adblock = (args.fixture_dir / "nsfw-adblock.txt").read_text(encoding="utf-8")
        domain_text = (args.fixture_dir / "nsfw-domains.txt").read_text(encoding="utf-8")
        minimum = 2
    else:
        adblock = fetch(UPSTREAMS["adblock"])
        domain_text = None
        minimum = 1000

    external_rules = []
    adult = set()
    for raw in adblock.splitlines():
        rule = raw.strip()
        if not (rule.startswith("||") and rule.endswith("^") and "$" not in rule):
            continue
        domain = normalize_domain(rule)
        if not domain:
            continue
        external_rules.append(rule)
        adult.add(domain)

    if len(external_rules) < minimum:
        raise RuntimeError(f"Too few upstream adblock rules: {len(external_rules)}")

    if domain_text is not None:
        fixture_domains = {
            domain
            for line in domain_text.splitlines()
            if (domain := normalize_domain(line))
        }
        if len(fixture_domains) < minimum:
            raise RuntimeError(f"Too few fixture domains: {len(fixture_domains)}")
        adult |= fixture_domains

    if len(adult) < minimum:
        raise RuntimeError(f"Too few upstream domains derived from adblock: {len(adult)}")

    generate_social_layers(
        FILTER_SRC / "15-social-addiction.txt",
        FILTER_SRC / "25-social-content.txt",
    )
    generate_strict_page(FILTER_SRC / "35-strict-page.txt")

    def read_filter_source(path: Path) -> str:
        text = path.read_text(encoding="utf-8").rstrip()
        if path.name == "40-generic-content.txt":
            text = protect_generic_content(text)
        return text

    source_paths = sorted(FILTER_SRC.glob("*.txt"))

    # Backward-compatible combined output: every source file in the exact same
    # sorted order as before, followed by the same HaGeZi upstream rules.
    main_parts = [read_filter_source(path) for path in source_paths]
    main_merged = (
        "\n\n".join(main_parts)
        + "\n\n! Upstream: HaGeZi NSFW (GPL-3.0)\n"
        + "\n".join(dict.fromkeys(external_rules))
        + "\n"
    )
    main_merged = deduplicate_filter_text(main_merged)

    # PMO/content output: all content-classification layers, including PMO
    # filtering inside social-media posts/accounts, but excluding only the
    # anti-addiction interface files. The upstream NSFW list stays here.
    pmo_parts = [
        read_filter_source(path)
        for path in source_paths
        if path.name not in SOCIAL_SOURCE_NAMES
    ]
    pmo_merged = (
        "\n\n".join(pmo_parts)
        + "\n\n! Upstream: HaGeZi NSFW (GPL-3.0)\n"
        + "\n".join(dict.fromkeys(external_rules))
        + "\n"
    )
    pmo_merged = deduplicate_filter_text(pmo_merged)

    # Social anti-addiction output: header plus the existing YouTube UI layer
    # and the generated cross-platform intentional-use layer. It deliberately
    # contains no PMO keyword/card rules and no external NSFW domain rules.
    social_parts = []
    header = FILTER_SRC / "00-header.txt"
    if header.exists():
        social_parts.append(read_filter_source(header))
    social_parts.extend(
        read_filter_source(path)
        for path in source_paths
        if path.name in SOCIAL_SOURCE_NAMES
    )
    social_merged = deduplicate_filter_text("\n\n".join(social_parts) + "\n")

    FILTER_DIST_DIR.mkdir(parents=True, exist_ok=True)
    FILTER_DIST_MAIN.write_text(main_merged, encoding="utf-8")
    FILTER_DIST_PMO.write_text(pmo_merged, encoding="utf-8")
    FILTER_DIST_SOCIAL.write_text(social_merged, encoding="utf-8")

    FILTER_DIST_MAIN_SAFARI.write_text(
        build_safari_custom_filters(main_merged), encoding="utf-8"
    )
    FILTER_DIST_PMO_SAFARI.write_text(
        build_safari_custom_filters(pmo_merged), encoding="utf-8"
    )
    FILTER_DIST_SOCIAL_SAFARI.write_text(
        build_safari_custom_filters(social_merged), encoding="utf-8"
    )

    adult |= read_domains(DNS_SRC / "turkish-adult-supplement.txt")
    allow = read_domains(DNS_SRC / "allowlist.txt")
    vpn = read_domains(DNS_SRC / "vpn-proxy.txt")
    adult -= allow
    strict = (adult | vpn) - allow

    DNS_DIST.mkdir(parents=True, exist_ok=True)
    write_dns("temizweb-balanced", adult)
    write_dns("temizweb-strict", strict)
    print(
        f"uBlock main/PMO/social + Safari custom-filter outputs written; "
        f"{len(external_rules)} upstream rules; "
        f"DNS balanced: {len(adult)}; strict: {len(strict)}"
    )


if __name__ == "__main__":
    main()
