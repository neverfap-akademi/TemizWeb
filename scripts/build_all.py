#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import argparse
import ipaddress
import re
import time

from generate_strict_page import generate_strict_page

ROOT=Path(__file__).resolve().parents[1]
FILTER_SRC=ROOT/'filters'/'src'
FILTER_DIST=ROOT/'filters'/'dist'/'temizweb-main.txt'
DNS_SRC=ROOT/'dns'/'src'
DNS_DIST=ROOT/'dns'/'dist'

UPSTREAMS = {
    # Official HaGeZi NSFW Adblock-format list.
    # DNS domains are derived from the same ||domain^ rules, so the build
    # does not depend on a second upstream path that may be renamed.
    "adblock": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/nsfw.txt",
}
DOMAIN_RE=re.compile(r'^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$',re.I)

def fetch(url:str, attempts:int=4)->str:
    error=None
    for n in range(attempts):
        try:
            req=Request(url,headers={'User-Agent':'TemizWeb-Builder/1.0'})
            with urlopen(req,timeout=120) as r:
                data=r.read().decode('utf-8',errors='replace')
            if len(data)<10000: raise RuntimeError(f'upstream response too small: {len(data)} bytes')
            return data
        except (URLError,HTTPError,TimeoutError,RuntimeError) as e:
            error=e; time.sleep(2**n)
    raise RuntimeError(f'Could not download {url}: {error}')

def normalize_domain(raw:str):
    s=raw.strip().lower()
    if not s or s.startswith(('#','!','[')): return None
    if ' ' in s:
        p=s.split()
        if len(p)>=2:
            try: ipaddress.ip_address(p[0]); s=p[1]
            except ValueError: return None
    s=s.removeprefix('||').removesuffix('^').rstrip('.')
    if s.startswith('*.'): s=s[2:]
    return s if DOMAIN_RE.fullmatch(s) else None

def read_domains(path:Path):
    out=set()
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            d=normalize_domain(line)
            if d: out.add(d)
    return out

def clean_adblock(text:str):
    out=[]
    for raw in text.splitlines():
        s=raw.strip()
        if s.startswith('||') and s.endswith('^') and '$' not in s:
            out.append(s)
    if len(out)<1000: raise RuntimeError(f'HaGeZi adblock parse produced only {len(out)} rules')
    return out

def parse_domains(text:str):
    out={d for line in text.splitlines() if (d:=normalize_domain(line))}
    if len(out)<1000: raise RuntimeError(f'HaGeZi domains parse produced only {len(out)} domains')
    return out

def write_dns(name:str,domains:set[str]):
    ordered=sorted(domains)
    (DNS_DIST/f'{name}-domains.txt').write_text('# TemizWeb DNS\n'+'\n'.join(ordered)+'\n',encoding='utf-8')
    (DNS_DIST/f'{name}-hosts.txt').write_text('# TemizWeb DNS\n'+'\n'.join('0.0.0.0 '+d for d in ordered)+'\n',encoding='utf-8')
    (DNS_DIST/f'{name}-adguard.txt').write_text('! Title: TemizWeb DNS\n'+'\n'.join('||'+d+'^' for d in ordered)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--fixture-dir',type=Path); a=ap.parse_args()
    if a.fixture_dir:
        adblock=(a.fixture_dir/'nsfw-adblock.txt').read_text(encoding='utf-8')
        domain_text=(a.fixture_dir/'nsfw-domains.txt').read_text(encoding='utf-8')
        minimum=2
    else:
        adblock = fetch(UPSTREAMS["adblock"])
        domain_text = None
        minimum = 1000

    external_rules = []
    adult = set()

    for raw in adblock.splitlines():
        rule = raw.strip()

        # Keep only plain domain-blocking rules. Exclude modifiers and
        # advanced syntax that cannot safely be converted to DNS domains.
        if not (
            rule.startswith("||")
            and rule.endswith("^")
            and "$" not in rule
        ):
            continue

        domain = normalize_domain(rule)
        if not domain:
            continue

        external_rules.append(rule)
        adult.add(domain)

    if len(external_rules) < minimum:
        raise RuntimeError(
            f"Too few upstream adblock rules: {len(external_rules)}"
        )

    # Offline fixtures still include a separate domains file. Validate it,
    # but the live build deliberately derives DNS domains from adblock rules.
    if domain_text is not None:
        fixture_domains = {
            domain
            for line in domain_text.splitlines()
            if (domain := normalize_domain(line))
        }
        }
        if len(fixture_domains) < minimum:
            raise RuntimeError(
                f"Too few fixture domains: {len(fixture_domains)}"
            )
        adult |= fixture_domains

    if len(adult) < minimum:
        raise RuntimeError(
            f"Too few upstream domains derived from adblock: {len(adult)}"
        )

    # Generate the universal full-page intent layer before merging
    # all filter source files.
    generate_strict_page(
        FILTER_SRC / "35-strict-page.txt"
    )

    parts = [
        path.read_text(
            encoding="utf-8"
        ).rstrip()
        for path in sorted(
            FILTER_SRC.glob("*.txt")
        )
    ]

    merged = (
        "\n\n".join(parts)
        + "\n\n! Upstream: HaGeZi NSFW (GPL-3.0)\n"
        + "\n".join(
            dict.fromkeys(external_rules)
        )
        + "\n"
    )

    FILTER_DIST.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    FILTER_DIST.write_text(
        merged,
        encoding="utf-8",
    )

    adult |= read_domains(
        DNS_SRC / "turkish-adult-supplement.txt"
    )

    allow = read_domains(
        DNS_SRC / "allowlist.txt"
    )

    vpn = read_domains(
        DNS_SRC / "vpn-proxy.txt"
    )

    adult -= allow
    strict = (adult | vpn) - allow
    DNS_DIST.mkdir(parents=True,exist_ok=True)
    write_dns('temizweb-balanced',adult); write_dns('temizweb-strict',strict)
    print(f'uBlock: {len(external_rules)} upstream rules; DNS balanced: {len(adult)}; strict: {len(strict)}')
if __name__=='__main__': main()
