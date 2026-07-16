#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ipaddress
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from generate_strict_page import generate_strict_page

ROOT = Path(__file__).resolve().parents[1]
FILTER_SRC = ROOT / "filters" / "src"
FILTER_DIST = ROOT / "filters" / "dist" / "temizweb-main.txt"
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

    generate_strict_page(FILTER_SRC / "35-strict-page.txt")

    parts = [
        path.read_text(encoding="utf-8").rstrip()
        for path in sorted(FILTER_SRC.glob("*.txt"))
    ]
    merged = (
        "\n\n".join(parts)
        + "\n\n! Upstream: HaGeZi NSFW (GPL-3.0)\n"
        + "\n".join(dict.fromkeys(external_rules))
        + "\n"
    )
    FILTER_DIST.parent.mkdir(parents=True, exist_ok=True)
    FILTER_DIST.write_text(merged, encoding="utf-8")

    adult |= read_domains(DNS_SRC / "turkish-adult-supplement.txt")
    allow = read_domains(DNS_SRC / "allowlist.txt")
    vpn = read_domains(DNS_SRC / "vpn-proxy.txt")
    adult -= allow
    strict = (adult | vpn) - allow

    DNS_DIST.mkdir(parents=True, exist_ok=True)
    write_dns("temizweb-balanced", adult)
    write_dns("temizweb-strict", strict)
    print(
        f"uBlock: {len(external_rules)} upstream rules; "
        f"DNS balanced: {len(adult)}; strict: {len(strict)}"
    )


if __name__ == "__main__":
    main()
