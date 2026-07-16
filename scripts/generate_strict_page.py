#!/usr/bin/env python3
"""Generate compact hostname-targeted TemizWeb strict-page filters.

The previous generator emitted ~60 KB per cosmetic rule. uBlock Origin could
silently discard those rules even though Python/CI passed. This version uses
small chained procedural tests instead of expanding every vocabulary
combination into one giant regex.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "filters" / "src" / "35-strict-page.txt"


def alt(parts):
    return "(?:" + "|".join(p for p in parts if p) + ")"


PEOPLE = (
    r"kad[ıi]n(?:lar(?:[ıi])?|[ıi])?", r"k[ıi]z(?:lar(?:[ıi])?|[ıi])?",
    r"bayan(?:lar[ıi]?)?", r"[üu]nl[üu](?:ler(?:in)?)?", r"model(?:ler(?:in)?)?",
    r"oyuncu(?:lar(?:[ıi]n)?)?", r"[şs]ark[ıi]c[ıi](?:lar(?:[ıi]n)?)?",
    r"[öo][ğg]renci(?:ler(?:in)?)?", r"liseli(?:ler(?:in)?)?",
    r"t[üu]rbanl[ıi](?:lar(?:[ıi]n)?)?", r"ba[şs][öo]rt[üu]l[üu](?:ler(?:in)?)?",
    r"hem[şs]ire(?:ler(?:in)?)?", r"[öo][ğg]retmen(?:ler(?:in)?)?",
    r"hostes(?:ler(?:in)?)?", r"gelin(?:ler(?:in)?)?", r"sevgili(?:ler(?:in)?)?",
    r"eski\s+sevgili(?:ler(?:in)?)?", r"t[üu]rk\s+k[ıi]zlar[ıi]",
    r"t[üu]rk\s+kad[ıi]nlar[ıi]", r"women?", r"girls?", r"lad(?:y|ies)",
    r"females?", r"babes?", r"models?", r"celebrit(?:y|ies)",
    r"actresses?", r"singers?", r"students?", r"schoolgirls?",
    r"influencers?", r"brides?", r"nurses?", r"teachers?",
    r"turkish\s+(?:girls?|women?)",
)
SEXUALIZED = (
    r"seksi", r"erotik", r"ate[şs]li", r"azd[ıi]r[ıi]c[ıi]",
    r"tahrik\s+edici", r"ba[şs]tan\s+[cç][ıi]kar[ıi]c[ıi]",
    r"hot", r"sexy", r"erotic", r"seductive", r"provocative",
    r"sultry", r"steamy", r"racy", r"thirst[\s-]*trap",
)
NUDITY = (
    r"[cç][ıi]plak(?:l[ıi]k)?", r"[cç][ıi]r[ıi]l[cç][ıi]plak",
    r"[üu]sts[üu]z", r"anadan\s+do[ğg]ma", r"nudes?", r"nudity",
    r"naked", r"topless",
)
REVEALING = (
    r"bikinili", r"mayolu", r"i[cç]\s+[cç]ama[şs][ıi]rl[ıi]",
    r"s[üu]tyenli", r"s[üu]tyensiz", r"dekolteli", r"transparan",
    r"[şs]effaf\s+k[ıi]yafetli", r"tangal[ıi]", r"bikini",
    r"micro\s+bikini", r"swimsuit", r"lingerie", r"underwear",
    r"braless", r"no[\s-]*bra", r"thong", r"transparent",
    r"see[\s-]*through", r"sheer", r"revealing", r"cleavage",
    r"side[\s-]*boob", r"under[\s-]*boob", r"nip[\s-]*slip",
)
LEAK = (
    r"if[şs]a(?:s[ıi]|lar[ıi])?", r"s[ıi]zd[ıi]r[ıi]lm[ıi][şs]",
    r"s[ıi]zd[ıi]r[ıi]lan", r"s[ıi]z[ıi]nt[ıi]", r"internete\s+d[üu][şs]t[üu]",
    r"[öo]zel\s+g[öo]r[üu]nt[üu]", r"mahrem\s+g[öo]r[üu]nt[üu]",
    r"gizli\s+[cç]ekim", r"leaks?", r"leaked", r"private\s+leak",
    r"private\s+(?:video|photos?|pics?)", r"sex\s+tape", r"hidden\s+camera",
)
MEDIA = (
    r"foto(?:lar)?", r"foto[ğg]raf(?:lar)?", r"resim(?:ler)?",
    r"g[öo]r[üu]nt[üu](?:ler)?", r"video(?:lar)?", r"kaset(?:i)?",
    r"klip(?:ler)?", r"galeri(?:si)?", r"ar[şs]iv(?:i)?", r"link(?:i)?",
    r"telegram", r"kanal(?:[ıi])?", r"grup(?:u)?", r"photos?", r"pictures?",
    r"pics?", r"images?", r"videos?", r"clips?", r"gifs?", r"gallery",
    r"archive", r"collection", r"pack", r"album", r"stream", r"download",
)
PORN = (
    r"porno", r"pornografi", r"seks", r"sevi[şs]me", r"siki[şs](?:me)?",
    r"porn", r"pornography", r"xxx", r"hardcore", r"softcore", r"hentai",
    r"rule[\s-]*34", r"adult\s+(?:video|movie)",
)
CONSUMPTION = (
    r"izle", r"seyret", r"indir", r"bul", r"ara", r"link(?:i)?",
    r"site(?:si)?", r"video(?:su)?", r"film(?:i)?", r"galeri(?:si)?",
    r"ar[şs]iv(?:i)?", r"foto(?:[ğg]raf)?", r"resim", r"g[öo]r[üu]nt[üu]",
    r"canl[ıi]", r"watch", r"view", r"download", r"stream", r"videos?",
    r"movies?", r"films?", r"clips?", r"gifs?", r"images?", r"pictures?",
    r"pics?", r"photos?", r"gallery", r"archive", r"collection", r"free",
    r"online", r"live",
)
DIRECT = (
    r"pornhub", r"xvideos", r"xnxx", r"xhamster", r"redtube", r"youporn",
    r"brazzers", r"gonewild", r"camgirls?", r"webcam\s+sex", r"live\s+sex",
    r"sex\s+cams?", r"onlyfans.{0,50}(?:if[şs]a|leak|leaked|nude|porn)",
    r"(?:if[şs]a|leak|leaked|free).{0,50}onlyfans", r"free\s+porn",
    r"watch\s+porn", r"download\s+porn", r"leaked\s+nudes?",
    r"nude\s+leaks?", r"celebrity\s+nudes?",
)
EDITORIAL = (
    r"haber(?:ler(?:i)?|i)?", r"g[üu]ndem", r"son\s+dakika", r"bas[ıi]n",
    r"gazete(?:si)?", r"makale", r"inceleme", r"analiz", r"ara[şs]t[ıi]rma",
    r"belgesel", r"dava", r"mahkeme", r"soru[şs]turma", r"news",
    r"headlines?", r"journalism", r"article", r"reports?", r"analysis",
    r"investigation", r"documentary", r"court", r"lawsuit",
)

# High-confidence recovery/education/help signals. These are intentionally
# allowed anywhere in the rendered page because recovery articles often use
# triggering terms while discussing how to quit.
SAFE = (
    r"never\s*fap", r"no\s*fap", r"pmo\s+recovery", r"porn\s*free",
    r"porn(?:ography)?\s+(?:recovery|addiction|treatment|therapy)",
    r"(?:quit|stop\s+watching|give\s+up|overcome)\s+porn(?:ography)?",
    r"recover(?:y|ing)?\s+from\s+porn(?:ography)?",
    r"porno(?:grafi)?\s+ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi]",
    r"pornoyu\s+b[ıi]rak", r"pornografiyi\s+b[ıi]rak",
    r"porno\s+izlemeyi\s+b[ıi]rak", r"porno\s+izlemekten\s+vazge[cç]",
    r"pornodan\s+kurtul", r"pornografiden\s+kurtul",
    r"porno.{0,80}(?:tedavi|terapi|iyile[şs]me|rehabilitasyon|n[üu]ks)",
    r"(?:tedavi|terapi|iyile[şs]me|n[üu]ks).{0,80}porno",
    r"cinsel\s+i[cç]erik.{0,120}(?:b[ıi]rak|vazge[cç]|kurtul|uzak\s+dur|izleme)",
    r"(?:b[ıi]rak|vazge[cç]|kurtul|uzak\s+dur).{0,120}cinsel\s+i[cç]erik",
    r"intikam\s+pornosu.{0,120}(?:ma[ğg]dur|destek|yard[ıi]m|hukuk|yasa|su[cç])",
    r"if[şs]a.{0,120}(?:ma[ğg]dur|destek|yard[ıi]m|hukuk|yasa|su[cç])",
    r"(?:victim|support|legal|law|crime|takedown).{0,120}(?:revenge\s+porn|intimate\s+image\s+abuse|leaked\s+images?)",
    r"(?:revenge\s+porn|intimate\s+image\s+abuse|leaked\s+images?).{0,120}(?:victim|support|legal|law|crime|takedown)",
    r"(?:seksi|nude|if[şs]a).{0,60}(?:kelimesi|anlam[ıi]|ne\s+demek|[cç]eviri|s[öo]zl[üu]k|definition|meaning|translation)",
)

HOST_GROUPS = {
    "search": (
        "google.com", "google.com.tr", "bing.com", "duckduckgo.com",
        "search.yahoo.com", "yandex.com", "yandex.com.tr", "yandex.ru",
        "brave.com", "startpage.com",
    ),
    "social": (
        "nitter.net", "ok.ru", "reddit.com", "old.reddit.com",
        "pinterest.com",
    ),
    "images": (
        "shutterstock.com", "pixabay.com", "pexels.com", "freepik.com",
        "unsplash.com", "gettyimages.com", "istockphoto.com",
        "depositphotos.com", "dreamstime.com",
    ),
}

# Each signal starts from the actual query-bearing element and climbs to html.
# This avoids nested procedural :has(...:has-text(...)) constructs, which are
# fragile across uBO parser/browser versions. #?# forces procedural evaluation.
SIGNALS = (
    ("text", "title"),
    ("text", "h1"),
    ("text", "h2"),
    ("text", '[role="heading"]'),
    ("attr", 'input[type="search"]', "value"),
    ("attr", 'input[name="q"]', "value"),
    ("attr", 'input[role="searchbox"]', "value"),
    ("text", 'textarea[name="q"]'),
    ("attr", 'textarea[name="q"]', "value"),
    ("text", '[role="combobox"]'),
    ("attr", '[role="combobox"]', "aria-label"),
    ("text", '[role="search"]'),
)


def build_pattern_families():
    return {
        "direct": (alt(DIRECT),),
        "sexualized_person": (alt(SEXUALIZED), alt(PEOPLE)),
        "nudity_person": (alt(NUDITY), alt(PEOPLE)),
        "revealing_person": (alt(REVEALING), alt(PEOPLE)),
        "leak_media": (alt(LEAK), alt(MEDIA)),
        "leak_person": (alt(LEAK), alt(PEOPLE)),
        "porn_consumption": (alt(PORN), alt(CONSUMPTION)),
    }


def build_patterns():
    families = build_pattern_families()
    combined = alt(tuple(alt(v) for v in families.values()))
    return combined, alt(SAFE), combined


def _matches_all(value, patterns):
    return all(re.search(pattern, value, re.I) for pattern in patterns)


def run_regression_tests():
    families = build_pattern_families()
    safe = re.compile(alt(SAFE), re.I)
    editorial = re.compile(alt(EDITORIAL), re.I)

    def blocked(value):
        if safe.search(value):
            return False
        for name, patterns in families.items():
            if _matches_all(value, patterns):
                if name == "leak_person" and editorial.search(value):
                    continue
                return True
        return False

    block = (
        "seksi kızlar", "seksi kizlar", "hot girl", "hot women",
        "çıplak kadın", "nude Turkish women", "ifşa amazing girl türk kızları",
        "ifsa turk kizlari", "leaked celebrity photos", "porno izle",
        "ifşa kız videoları haber",
    )
    allow = (
        "kadın bilim insanları", "hot weather", "ifşa kız haberleri",
        "ifşa Türk kızları haberleri", "pornoyu bırakmak", "porno tedavisi",
        "pornodan kurtulmak", "neverfap", "pmo recovery",
        "Pornonun ıstırabı. Bu bağımlılıktan kurtulmak mümkündür.",
        "ifşa mağduru hukuki yardım", "intikam pornosu mağdur desteği",
    )
    failures = [f"Expected BLOCK: {x!r}" for x in block if not blocked(x)]
    failures += [f"Expected ALLOW: {x!r}" for x in allow if blocked(x)]
    if failures:
        raise RuntimeError("Strict-page regression failures:\n- " + "\n- ".join(failures))
    print(f"Strict-page regression tests passed: {len(block)} block, {len(allow)} allow")


def _chain_for_signal(kind, selector, patterns, attribute=None, editorial_guard=False):
    if kind == "text":
        chain = selector + "".join(f":has-text(/{p}/iu)" for p in patterns)
        if editorial_guard:
            chain += f":not(:has-text(/{alt(EDITORIAL)}/iu))"
    else:
        chain = selector + f":watch-attr({attribute})"
        chain += "".join(f":matches-attr({attribute}=/{p}/iu)" for p in patterns)
        if editorial_guard:
            chain += f":not(:matches-attr({attribute}=/{alt(EDITORIAL)}/iu))"
    return chain + f":upward(html):not(:has-text(/{alt(SAFE)}/iu)) > body"


def generate_strict_page(output_path=DEFAULT_OUTPUT):
    run_regression_tests()
    families = build_pattern_families()
    safe = alt(SAFE)
    editorial = alt(EDITORIAL)
    rules = []

    for group_name, hosts in HOST_GROUPS.items():
        prefix = ",".join(hosts)
        for family_name, patterns in families.items():
            for signal in SIGNALS:
                kind, selector, *rest = signal
                attribute = rest[0] if rest else None
                body = _chain_for_signal(
                    kind, selector, patterns, attribute,
                    editorial_guard=(family_name == "leak_person"),
                )
                rules.append((f"{group_name}/{family_name}/{selector}", f"{prefix}#?#{body}"))

            # URL/path/query: chained matches-path checks avoid giant encoded
            # cross-product regexes. Both Unicode and common ASCII spellings are
            # already represented in the vocabulary classes.
            chain = "html" + "".join(f":matches-path(/{p}/iu)" for p in patterns)
            if family_name == "leak_person":
                chain += f":not(:matches-path(/{editorial}/iu))"
            chain += f":not(:has-text(/{safe}/iu)) > body"
            rules.append((f"{group_name}/{family_name}/URL", f"{prefix}#?#{chain}"))

    lines = [
        "! =============================================================================",
        "! TemizWeb — COMPACT HOSTNAME-TARGETED STRICT FULL-PAGE FILTER",
        "! GENERATED FILE — edit scripts/generate_strict_page.py instead.",
        "! Uses chained signals; no giant 60 KB cosmetic rules.",
        "! =============================================================================", "",
    ]
    for i, (label, rule) in enumerate(rules, 1):
        lines.extend((f"! Rule {i}: {label}", rule, ""))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    active = [r for _, r in rules]
    maximum = max(map(len, active), default=0)
    if maximum > 12000:
        raise RuntimeError(f"Generated cosmetic rule is too long: {maximum} characters")

    print(f"Generated compact strict-page filter: {output_path.relative_to(ROOT)}")
    print(f"Generated {len(rules)} rules; longest rule: {maximum} characters")
    return output_path


if __name__ == "__main__":
    generate_strict_page()
