#!/usr/bin/env python3

"""
Generate TemizWeb's universal strict full-page intent filter.

This layer is deliberately stricter than post/card filtering.

A social post mentioning a leak may be news or discussion. A page title,
search heading, search field or URL containing a strong combination such
as "ifşa Türk kızları", "seksi kızlar" or "nude women gallery" expresses
a much stronger browsing intent.

The generator creates:

1. Title detection
2. Heading detection
3. Metadata detection
4. Search-input detection
5. Search-region detection
6. URL/path detection
7. Protected-context exceptions
8. Python regression tests for the generated language engine
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote, quote_plus


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "filters" / "src" / "35-strict-page.txt"


def alt(parts: tuple[str, ...] | list[str]) -> str:
    """Return a non-capturing regex alternation."""
    cleaned = [
        part.strip()
        for part in parts
        if part and part.strip()
    ]
    return "(?:" + "|".join(cleaned) + ")"


def literal_regex(value: str) -> str:
    """
    Convert a human-readable literal into a whitespace-tolerant regex.

    Example:
        "türk kızları" -> "türk\\s+kızları"
    """
    words = value.split()
    return r"\s+".join(
        re.escape(word)
        for word in words
    )


# ---------------------------------------------------------------------
# STRONG PAGE-INTENT VOCABULARY
# ---------------------------------------------------------------------

PEOPLE = (
    # Turkish with common suffixes and ASCII variants
    r"kad[ıi]n(?:lar(?:[ıi])?|[ıi])?",
    r"k[ıi]z(?:lar(?:[ıi])?|[ıi])?",
    r"bayan(?:lar[ıi]?)?",
    r"[üu]nl[üu](?:ler(?:in)?)?",
    r"model(?:ler(?:in)?)?",
    r"oyuncu(?:lar(?:[ıi]n)?)?",
    r"[şs]ark[ıi]c[ıi](?:lar(?:[ıi]n)?)?",
    r"[öo][ğg]renci(?:ler(?:in)?)?",
    r"liseli(?:ler(?:in)?)?",
    r"t[üu]rbanl[ıi](?:lar(?:[ıi]n)?)?",
    r"ba[şs][öo]rt[üu]l[üu](?:ler(?:in)?)?",
    r"hem[şs]ire(?:ler(?:in)?)?",
    r"[öo][ğg]retmen(?:ler(?:in)?)?",
    r"hostes(?:ler(?:in)?)?",
    r"gelin(?:ler(?:in)?)?",
    r"sevgili(?:ler(?:in)?)?",
    r"eski\s+sevgili(?:ler(?:in)?)?",
    r"t[üu]rk\s+k[ıi]zlar[ıi]",
    r"t[üu]rk\s+kad[ıi]nlar[ıi]",

    # English
    r"woman",
    r"women",
    r"girl",
    r"girls",
    r"lady",
    r"ladies",
    r"female",
    r"females",
    r"babe",
    r"babes",
    r"model",
    r"models",
    r"celebrity",
    r"celebrities",
    r"actress",
    r"actresses",
    r"singer",
    r"singers",
    r"student",
    r"students",
    r"schoolgirl",
    r"schoolgirls",
    r"influencer",
    r"influencers",
    r"bride",
    r"brides",
    r"nurse",
    r"nurses",
    r"teacher",
    r"teachers",
    r"turkish\s+girl",
    r"turkish\s+girls",
    r"turkish\s+woman",
    r"turkish\s+women",
)


SEXUALIZED = (
    r"seksi",
    r"erotik",
    r"ate[şs]li",
    r"azd[ıi]r[ıi]c[ıi]",
    r"tahrik\s+edici",
    r"ba[şs]tan\s+[cç][ıi]kar[ıi]c[ıi]",
    r"hot",
    r"sexy",
    r"erotic",
    r"seductive",
    r"provocative",
    r"sultry",
    r"steamy",
    r"racy",
    r"thirst[\s-]*trap",
)


NUDITY = (
    r"[cç][ıi]plak",
    r"[cç][ıi]plakl[ıi]k",
    r"[cç][ıi]r[ıi]l[cç][ıi]plak",
    r"[üu]sts[üu]z",
    r"anadan\s+do[ğg]ma",
    r"nude",
    r"nudes",
    r"nudity",
    r"naked",
    r"topless",
)


REVEALING = (
    r"bikinili",
    r"mayolu",
    r"i[cç]\s+[cç]ama[şs][ıi]rl[ıi]",
    r"s[üu]tyenli",
    r"s[üu]tyensiz",
    r"dekolteli",
    r"transparan",
    r"[şs]effaf\s+k[ıi]yafetli",
    r"tangal[ıi]",
    r"bikini",
    r"micro\s+bikini",
    r"swimsuit",
    r"lingerie",
    r"underwear",
    r"braless",
    r"no[\s-]*bra",
    r"thong",
    r"transparent",
    r"see[\s-]*through",
    r"sheer",
    r"revealing",
    r"cleavage",
    r"side[\s-]*boob",
    r"under[\s-]*boob",
    r"nip[\s-]*slip",
    r"wet[\s-]*t[\s-]*shirt",
)


LEAK = (
    r"if[şs]a",
    r"if[şs]as[ıi]",
    r"if[şs]alar[ıi]",
    r"s[ıi]zd[ıi]r[ıi]lm[ıi][şs]",
    r"s[ıi]zd[ıi]r[ıi]lan",
    r"s[ıi]z[ıi]nt[ıi]",
    r"internete\s+d[üu][şs]t[üu]",
    r"[öo]zel\s+g[öo]r[üu]nt[üu]",
    r"mahrem\s+g[öo]r[üu]nt[üu]",
    r"gizli\s+[cç]ekim",
    r"leak",
    r"leaks",
    r"leaked",
    r"private\s+leak",
    r"private\s+video",
    r"private\s+photos?",
    r"private\s+pics?",
    r"sex\s+tape",
    r"hidden\s+camera",
    r"secretly\s+filmed",
)


MEDIA = (
    r"foto(?:lar)?",
    r"foto[ğg]raf(?:lar)?",
    r"resim(?:ler)?",
    r"g[öo]r[üu]nt[üu](?:ler)?",
    r"video(?:lar)?",
    r"kaset(?:i)?",
    r"klip(?:ler)?",
    r"galeri(?:si)?",
    r"ar[şs]iv(?:i)?",
    r"link(?:i)?",
    r"telegram",
    r"kanal(?:[ıi])?",
    r"grup(?:u)?",
    r"photo",
    r"photos",
    r"picture",
    r"pictures",
    r"pic",
    r"pics",
    r"image",
    r"images",
    r"video",
    r"videos",
    r"clip",
    r"clips",
    r"gif",
    r"gifs",
    r"gallery",
    r"archive",
    r"collection",
    r"pack",
    r"album",
    r"stream",
    r"download",
)


PORN_CORE = (
    r"porno",
    r"pornografi",
    r"seks",
    r"sevi[şs]me",
    r"siki[şs](?:me)?",
    r"porn",
    r"pornography",
    r"xxx",
    r"hardcore",
    r"softcore",
    r"hentai",
    r"rule[\s-]*34",
    r"adult\s+video",
    r"adult\s+movie",
)


CONSUMPTION = (
    r"izle",
    r"seyret",
    r"a[cç]",
    r"indir",
    r"bul",
    r"ara",
    r"link(?:i)?",
    r"site(?:si)?",
    r"video(?:su)?",
    r"film(?:i)?",
    r"galeri(?:si)?",
    r"ar[şs]iv(?:i)?",
    r"foto(?:[ğg]raf)?",
    r"resim",
    r"g[öo]r[üu]nt[üu]",
    r"canl[ıi]",
    r"watch",
    r"view",
    r"download",
    r"stream",
    r"videos?",
    r"movies?",
    r"films?",
    r"clips?",
    r"gifs?",
    r"images?",
    r"pictures?",
    r"pics?",
    r"photos?",
    r"gallery",
    r"archive",
    r"collection",
    r"sites?",
    r"links?",
    r"free",
    r"online",
    r"live",
)


DIRECT_STRONG = (
    r"pornhub",
    r"xvideos",
    r"xnxx",
    r"xhamster",
    r"redtube",
    r"youporn",
    r"brazzers",
    r"gonewild",
    r"camgirls?",
    r"webcam\s+sex",
    r"live\s+sex",
    r"sex\s+cams?",
    r"onlyfans.{0,50}(?:if[şs]a|leak|leaked|nude|porn)",
    r"(?:if[şs]a|leak|leaked|free).{0,50}onlyfans",
    r"fansly.{0,50}(?:if[şs]a|leak|leaked|nude|porn)",
    r"free\s+porn",
    r"watch\s+porn",
    r"download\s+porn",
    r"leaked\s+nudes?",
    r"nude\s+leaks?",
    r"celebrity\s+nudes?",
    r"revenge\s+porn.{0,40}(?:video|image|photo|watch|gallery)",
    r"intikam\s+pornosu.{0,40}(?:izle|video|g[öo]r[üu]nt[üu]|if[şs]a|ar[şs]iv)",
)


# ---------------------------------------------------------------------
# PROTECTED CONTEXTS
# ---------------------------------------------------------------------

RECOVERY = (
    r"porno\s+ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi]",
    r"pornografi\s+ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi]",
    r"pornoyu\s+b[ıi]rak",
    r"porno\s+izlemeyi\s+b[ıi]rak",
    r"pornodan\s+kurtul",
    r"porno.{0,30}tedavi",
    r"pornografinin\s+zararlar[ıi]",
    r"porno\s+engelleme",
    r"porn\s+addiction",
    r"pornography\s+addiction",
    r"quit\s+porn",
    r"stop\s+watching\s+porn",
    r"porn\s+recovery",
    r"pornography\s+recovery",
    r"porn.{0,30}treatment",
    r"harms\s+of\s+pornography",
    r"porn\s+blocker",
    r"block\s+adult\s+content",
    r"pornography\s+research",
)


ABUSE_SUBJECT = (
    r"intikam\s+pornosu",
    r"[öo]zel\s+g[öo]r[üu]nt[üu]",
    r"mahrem\s+g[öo]r[üu]nt[üu]",
    r"if[şs]a",
    r"s[ıi]zd[ıi]r[ıi]lm[ıi][şs]\s+g[öo]r[üu]nt[üu]",
    r"gizli\s+kamera",
    r"gizli\s+[cç]ekim",
    r"deepfake",
    r"[cç][ıi]plakla[şs]t[ıi]rma",
    r"revenge\s+porn",
    r"intimate\s+image\s+abuse",
    r"non[\s-]*consensual\s+intimate\s+images?",
    r"image[\s-]*based\s+sexual\s+abuse",
    r"leaked\s+(?:images?|photos?)",
    r"hidden\s+camera",
    r"voyeurism",
    r"upskirt",
    r"nudification",
)


HELP_CONTEXT = (
    r"ma[ğg]dur(?:u|lar[ıi]?)?",
    r"destek",
    r"yard[ıi]m",
    r"hukuk(?:i)?",
    r"yasal",
    r"yasa(?:s[ıi])?",
    r"su[cç](?:u)?",
    r"[şs]ikayet",
    r"ihbar",
    r"bildir",
    r"kald[ıi]rma",
    r"haklar[ıi]?",
    r"korunma",
    r"[öo]nleme",
    r"victims?",
    r"survivors?",
    r"support",
    r"help",
    r"legal",
    r"laws?",
    r"crime",
    r"criminal",
    r"report",
    r"reporting",
    r"removal",
    r"takedown",
    r"rights",
    r"prevention",
)


LINGUISTIC_CONTEXT = (
    r"kelimesi",
    r"kelimenin",
    r"anlam[ıi]",
    r"ne\s+demek",
    r"[cç]eviri",
    r"s[öo]zl[üu]k",
    r"tan[ıi]m",
    r"definition",
    r"meaning",
    r"translation",
    r"dictionary",
    r"etymology",
)


# ---------------------------------------------------------------------
# URL TOKENS
# ---------------------------------------------------------------------

URL_PEOPLE_LITERALS = (
    "kadın",
    "kadınlar",
    "kadin",
    "kadinlar",
    "kız",
    "kızlar",
    "kiz",
    "kizlar",
    "türk kızları",
    "turk kizlari",
    "woman",
    "women",
    "girl",
    "girls",
    "female",
    "model",
    "models",
    "celebrity",
    "turkish girls",
    "turkish women",
)

URL_SEXUALIZED_LITERALS = (
    "seksi",
    "ateşli",
    "atesli",
    "erotik",
    "hot",
    "sexy",
    "erotic",
    "seductive",
    "provocative",
)

URL_NUDITY_LITERALS = (
    "çıplak",
    "ciplak",
    "çıplaklık",
    "ciplaklik",
    "nude",
    "nudes",
    "naked",
    "topless",
)

URL_LEAK_LITERALS = (
    "ifşa",
    "ifsa",
    "sızdırılmış",
    "sizdirilmis",
    "sızıntı",
    "sizinti",
    "leak",
    "leaks",
    "leaked",
)

URL_MEDIA_LITERALS = (
    "foto",
    "fotoğraf",
    "fotograf",
    "resim",
    "görüntü",
    "goruntu",
    "video",
    "galeri",
    "arşiv",
    "arsiv",
    "photo",
    "photos",
    "pics",
    "images",
    "videos",
    "gallery",
    "archive",
)


def encode_url_literal(value: str) -> tuple[str, ...]:
    """
    Return common representations of one URL phrase.

    This handles:
    - plain Unicode
    - ASCII-looking literal
    - %20 encoding
    - + encoding
    - hyphenated and underscored slugs
    """
    variants = {
        value,
        quote(value, safe=""),
        quote_plus(value, safe=""),
        value.replace(" ", "-"),
        value.replace(" ", "_"),
        value.replace(" ", "+"),
    }

    return tuple(
        re.escape(item)
        for item in sorted(variants)
        if item
    )


def build_url_group(values: tuple[str, ...]) -> str:
    fragments: list[str] = []

    for value in values:
        fragments.extend(
            encode_url_literal(value)
        )

    return alt(tuple(dict.fromkeys(fragments)))


# ---------------------------------------------------------------------
# PATTERN CONSTRUCTION
# ---------------------------------------------------------------------

def build_patterns() -> tuple[str, str, str]:
    people = alt(PEOPLE)
    sexualized = alt(SEXUALIZED)
    nudity = alt(NUDITY)
    revealing = alt(REVEALING)
    leak = alt(LEAK)
    media = alt(MEDIA)
    porn_core = alt(PORN_CORE)
    consumption = alt(CONSUMPTION)
    direct_strong = alt(DIRECT_STRONG)

    # Finite distances allow branding and filler words:
    #
    # "ifşa amazing girl türk kızları"
    # "seksi ve güzel Türk kızları"
    # "private Turkish celebrity photos leaked"
    risk_parts = (
        direct_strong,

        rf"{sexualized}.{{0,80}}{people}",
        rf"{people}.{{0,80}}{sexualized}",

        rf"{nudity}.{{0,80}}{people}",
        rf"{people}.{{0,80}}{nudity}",

        rf"{revealing}.{{0,80}}{people}",
        rf"{people}.{{0,80}}{revealing}",

        # Page-level intent is stricter than card filtering:
        # leak + person is sufficient; media is not required.
        rf"{leak}.{{0,120}}{people}",
        rf"{people}.{{0,120}}{leak}",

        rf"{leak}.{{0,80}}{media}",
        rf"{media}.{{0,80}}{leak}",

        rf"{porn_core}.{{0,60}}{consumption}",
        rf"{consumption}.{{0,60}}{porn_core}",
    )

    page_risk = alt(risk_parts)

    recovery = alt(RECOVERY)
    abuse_subject = alt(ABUSE_SUBJECT)
    help_context = alt(HELP_CONTEXT)
    linguistic_context = alt(LINGUISTIC_CONTEXT)

    protected_parts = (
        recovery,

        rf"{abuse_subject}.{{0,140}}{help_context}",
        rf"{help_context}.{{0,140}}{abuse_subject}",

        # Prevent dictionary/translation searches such as:
        # "seksi kelimesinin anlamı"
        rf"(?:{sexualized}|{nudity}|{leak}).{{0,80}}{linguistic_context}",
        rf"{linguistic_context}.{{0,80}}(?:{sexualized}|{nudity}|{leak})",
    )

    protected = alt(protected_parts)

    url_people = build_url_group(
        URL_PEOPLE_LITERALS
    )
    url_sexualized = build_url_group(
        URL_SEXUALIZED_LITERALS
    )
    url_nudity = build_url_group(
        URL_NUDITY_LITERALS
    )
    url_leak = build_url_group(
        URL_LEAK_LITERALS
    )
    url_media = build_url_group(
        URL_MEDIA_LITERALS
    )

    # URL strings may contain arbitrary encoded filler between groups.
    url_risk = alt(
        (
            rf"{url_sexualized}.{{0,180}}{url_people}",
            rf"{url_people}.{{0,180}}{url_sexualized}",

            rf"{url_nudity}.{{0,180}}{url_people}",
            rf"{url_people}.{{0,180}}{url_nudity}",

            rf"{url_leak}.{{0,220}}{url_people}",
            rf"{url_people}.{{0,220}}{url_leak}",

            rf"{url_leak}.{{0,180}}{url_media}",
            rf"{url_media}.{{0,180}}{url_leak}",

            r"onlyfans.{0,160}(?:ifsa|if%C5%9Fa|leak|leaked|nude|porn)",
            r"(?:ifsa|if%C5%9Fa|leak|leaked|free).{0,160}onlyfans",

            r"(?:porn|porno|xxx|hentai).{0,100}"
            r"(?:watch|izle|video|videos|gallery|galeri|archive|arsiv|download|indir)",
        )
    )

    return page_risk, protected, url_risk


# ---------------------------------------------------------------------
# REAL REGRESSION TESTS
# ---------------------------------------------------------------------

POSITIVE_TESTS = (
    "seksi kızlar",
    "seksi kizlar",
    "seksi güzel Türk kızları",
    "Türk kızları seksi videolar",
    "hot women",
    "hot amazing Turkish girls",
    "sexy female models",
    "çıplak kadın",
    "ciplak kadinlar",
    "nude Turkish women",
    "naked girl gallery",
    "ifşa amazing girl türk kızları",
    "ifsa turk kizlari",
    "Türk kızları yeni ifşa",
    "ünlü oyuncu özel görüntü ifşa",
    "leaked celebrity photos",
    "private Turkish model leaked",
    "onlyfans ifşa",
    "free porn videos",
    "porno izle",
)


NEGATIVE_TESTS = (
    "kadın bilim insanları",
    "Türk kızlarının eğitim başarısı",
    "kadın doktorların çalışma koşulları",
    "hot weather",
    "hot water system",
    "model uçak yapımı",
    "bikini tarihi",
    "mayo tasarımı",
    "seksi kelimesinin anlamı",
    "hot kelimesinin Türkçe çevirisi",
    "nude kelimesi ne demek",
    "ifşa kelimesinin anlamı",
    "intikam pornosu mağdur desteği",
    "ifşa mağduru hukuki yardım",
    "özel görüntülerin yayılması suçu",
    "intimate image abuse support",
    "revenge porn law",
    "porn recovery",
    "pornography addiction treatment",
)


def run_regression_tests() -> None:
    page_risk, protected, _ = build_patterns()

    try:
        risk_re = re.compile(
            page_risk,
            re.IGNORECASE,
        )
        protected_re = re.compile(
            protected,
            re.IGNORECASE,
        )
    except re.error as exc:
        raise RuntimeError(
            f"Strict-page regex failed to compile: {exc}"
        ) from exc

    failures: list[str] = []

    for text in POSITIVE_TESTS:
        risk_match = risk_re.search(text)
        protected_match = protected_re.search(text)

        if not risk_match:
            failures.append(
                f"Expected BLOCK but risk regex missed: {text!r}"
            )
        elif protected_match:
            failures.append(
                f"Expected BLOCK but protection regex matched: {text!r}"
            )

    for text in NEGATIVE_TESTS:
        risk_match = risk_re.search(text)
        protected_match = protected_re.search(text)

        effective_block = bool(
            risk_match and not protected_match
        )

        if effective_block:
            failures.append(
                f"Expected ALLOW but effective block matched: {text!r}"
            )

    if failures:
        raise RuntimeError(
            "Strict-page regression failures:\n"
            + "\n".join(
                f"- {failure}"
                for failure in failures
            )
        )

    print(
        "Strict-page language regression tests passed: "
        f"{len(POSITIVE_TESTS)} block cases, "
        f"{len(NEGATIVE_TESTS)} allow cases"
    )


# ---------------------------------------------------------------------
# UBLOCK RULE GENERATION
# ---------------------------------------------------------------------

def protection_guards(
    protected: str,
) -> str:
    """
    Return common protected-context guards.

    We inspect several prominent regions because protected wording may
    occur in the title, heading or search-result header.
    """
    return (
        f":not(:has(title:has-text(/{protected}/iu)))"
        f":not(:has(h1:has-text(/{protected}/iu)))"
        f":not(:has(h2:has-text(/{protected}/iu)))"
        f":not(:has(h3:has-text(/{protected}/iu)))"
        f":not(:has([role=\"heading\"]:has-text(/{protected}/iu)))"
    )


def generate_strict_page(
    output_path: Path = DEFAULT_OUTPUT,
) -> Path:
    run_regression_tests()

    page_risk, protected, url_risk = build_patterns()
    guards = protection_guards(protected)

    rules = (
        # Document title
        (
            "*##html"
            f":has(title:has-text(/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),

        # Standard heading levels
        (
            "*##html"
            f":has(h1:has-text(/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has(h2:has-text(/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has(h3:has-text(/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),

        # ARIA heading used by JavaScript applications
        (
            "*##html"
            f":has([role=\"heading\"]:has-text(/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),

        # Open Graph and Twitter metadata
        (
            "*##html"
            f":has(meta[property=\"og:title\"]"
            f":matches-attr(content=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has(meta[name=\"twitter:title\"]"
            f":matches-attr(content=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has(meta[name=\"description\"]"
            f":matches-attr(content=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),

        # Search input values
        (
            "*##html"
            f":has(input[type=\"search\"]"
            f":matches-attr(value=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has(input[name=\"q\"]"
            f":matches-attr(value=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has(input[role=\"searchbox\"]"
            f":matches-attr(value=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),

        # Common custom search attributes
        (
            "*##html"
            f":has([data-query]"
            f":matches-attr(data-query=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has([data-search-query]"
            f":matches-attr(data-search-query=/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),

        # Text shown inside a bounded search region
        (
            "*##html"
            f":has([role=\"search\"]:has-text(/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),
        (
            "*##html"
            f":has(form[role=\"search\"]:has-text(/{page_risk}/iu))"
            f"{guards}"
            " > body"
        ),

        # URL path and query fallback
        (
            "*##html"
            f":matches-path(/{url_risk}/i)"
            f"{guards}"
            " > body"
        ),
    )

    lines = [
        "! =============================================================================",
        "! TemizWeb — UNIVERSAL STRICT FULL-PAGE INTENT FILTER",
        "! File: filters/src/35-strict-page.txt",
        "!",
        "! GENERATED FILE — edit scripts/generate_strict_page.py instead.",
        "!",
        "! SIGNALS",
        "! - Document title",
        "! - H1, H2, H3 and ARIA headings",
        "! - Open Graph, Twitter and description metadata",
        "! - Search input values and custom query attributes",
        "! - Bounded search-region text",
        "! - URL path/query, including common UTF-8 encodings",
        "!",
        "! POLICY",
        "! - Page-intent detection is stricter than card filtering.",
        "! - Strong recovery, legal and victim-support contexts override blocking.",
        "! - SafeSearch and Restricted Mode are not forced.",
        "! =============================================================================",
        "",
    ]

    for index, rule in enumerate(rules, start=1):
        lines.append(
            f"! Strict-page signal {index}"
        )
        lines.append(rule)
        lines.append("")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(
        "Generated universal strict-page filter: "
        f"{output_path.relative_to(ROOT)}"
    )
    print(
        f"Generated {len(rules)} strict-page signal rules"
    )

    return output_path


if __name__ == "__main__":
    generate_strict_page()
