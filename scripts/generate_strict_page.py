#!/usr/bin/env python3

"""
Generate TemizWeb's universal strict-page layer.

This does not produce tens of thousands of literal rules. It combines
large vocabularies into compact regular expressions that represent
hundreds of thousands or millions of possible phrase combinations.

The generated filter hides the whole page when a strong-risk phrase is
present in:

1. the document title;
2. the main H1 heading;
3. an ASCII / URL-encoded path or query.

Strong recovery, legal, reporting and victim-support contexts override
the block.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "filters" / "src" / "35-strict-page.txt"


def alt(parts: list[str] | tuple[str, ...]) -> str:
    """Join regex fragments as a non-capturing alternation."""
    cleaned = [part.strip() for part in parts if part.strip()]
    return "(?:" + "|".join(cleaned) + ")"


# ---------------------------------------------------------------------
# PAGE-LEVEL VOCABULARIES
#
# These are intentionally stricter than card-level vocabularies.
# A page title/query demonstrates intent more strongly than one social
# post mentioning the same terms.
# ---------------------------------------------------------------------

PEOPLE = (
    # Turkish
    r"kadın",
    r"kadınlar",
    r"kadını",
    r"kadınları",
    r"kadin",
    r"kadinlar",
    r"kadini",
    r"kadinlari",
    r"kız",
    r"kızlar",
    r"kızı",
    r"kızları",
    r"kiz",
    r"kizlar",
    r"kizi",
    r"kizlari",
    r"bayan",
    r"bayanlar",
    r"ünlü",
    r"ünlüler",
    r"unlu",
    r"unluler",
    r"model",
    r"modeller",
    r"oyuncu",
    r"oyuncular",
    r"şarkıcı",
    r"şarkıcılar",
    r"sarkici",
    r"sarkicilar",
    r"öğrenci",
    r"öğrenciler",
    r"ogrenci",
    r"ogrenciler",
    r"liseli",
    r"liseliler",
    r"türbanlı",
    r"türbanlılar",
    r"turbanli",
    r"turbanlilar",
    r"başörtülü",
    r"başörtülüler",
    r"basortulu",
    r"basortululer",
    r"gelin",
    r"gelinler",
    r"hemşire",
    r"hemşireler",
    r"hemsire",
    r"hemsireler",
    r"öğretmen",
    r"öğretmenler",
    r"ogretmen",
    r"ogretmenler",
    r"polis",
    r"hostes",
    r"hostesler",
    r"sevgili",
    r"sevgililer",
    r"eski\s+sevgili",
    r"türk\s+kızları",
    r"türk\s+kadınları",
    r"turk\s+kizlari",
    r"turk\s+kadinlari",

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
    r"bride",
    r"brides",
    r"nurse",
    r"nurses",
    r"teacher",
    r"teachers",
    r"policewoman",
    r"policewomen",
    r"influencer",
    r"influencers",
    r"turkish\s+girl",
    r"turkish\s+girls",
    r"turkish\s+woman",
    r"turkish\s+women",
)


NUDITY = (
    r"çıplak",
    r"çıplaklık",
    r"ciplak",
    r"ciplaklik",
    r"nude",
    r"nudes",
    r"nudity",
    r"naked",
    r"topless",
    r"üstsüz",
    r"ustsuz",
    r"çırılçıplak",
    r"cirilciplak",
    r"anadan\s+doğma",
    r"anadan\s+dogma",
)


SEXUALIZED = (
    r"seksi",
    r"erotik",
    r"ateşli",
    r"atesli",
    r"azdırıcı",
    r"azdirici",
    r"tahrik\s+edici",
    r"hot",
    r"sexy",
    r"erotic",
    r"seductive",
    r"provocative",
    r"sultry",
    r"steamy",
    r"racy",
    r"thirst\s*trap",
    r"thirsttrap",
)


REVEALING = (
    # Turkish
    r"bikinili",
    r"mayolu",
    r"iç\s+çamaşırlı",
    r"ic\s+camasirli",
    r"sütyenli",
    r"sutyenli",
    r"sütyensiz",
    r"sutyensiz",
    r"dekolteli",
    r"transparan",
    r"şeffaf\s+kıyafetli",
    r"seffaf\s+kiyafetli",
    r"mini\s+etekli",
    r"tangalı",
    r"tangali",

    # English
    r"bikini",
    r"micro\s+bikini",
    r"swimsuit",
    r"lingerie",
    r"underwear",
    r"bra",
    r"braless",
    r"no\s+bra",
    r"thong",
    r"transparent",
    r"see[\s-]?through",
    r"sheer",
    r"revealing",
    r"cleavage",
    r"side\s*boob",
    r"under\s*boob",
    r"nip\s*slip",
    r"wardrobe\s+malfunction",
    r"wet\s+t[\s-]?shirt",
)


LEAK = (
    # Turkish
    r"ifşa",
    r"ifsa",
    r"ifşası",
    r"ifsasi",
    r"ifşaları",
    r"ifsalari",
    r"sızdırılmış",
    r"sizdirilmis",
    r"sızdırılan",
    r"sizdirilan",
    r"sızıntı",
    r"sizinti",
    r"internete\s+düştü",
    r"internete\s+dustu",
    r"özel\s+görüntü",
    r"ozel\s+goruntu",
    r"gizli\s+çekim",
    r"gizli\s+cekim",

    # English
    r"leak",
    r"leaks",
    r"leaked",
    r"leaking",
    r"private\s+leak",
    r"private\s+video",
    r"private\s+photos?",
    r"private\s+pics?",
    r"sex\s+tape",
    r"hidden\s+camera",
    r"secretly\s+filmed",
)


MEDIA = (
    # Turkish
    r"foto",
    r"fotolar",
    r"fotoğraf",
    r"fotoğraflar",
    r"fotograf",
    r"fotograflar",
    r"resim",
    r"resimler",
    r"görüntü",
    r"görüntüler",
    r"goruntu",
    r"goruntuler",
    r"video",
    r"videolar",
    r"kaset",
    r"kaseti",
    r"klip",
    r"klipler",
    r"galeri",
    r"galerisi",
    r"arşiv",
    r"arşivi",
    r"arsiv",
    r"arsivi",
    r"link",
    r"linki",
    r"telegram",
    r"kanal",
    r"grup",
    r"grubu",

    # English
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
    r"telegram",
    r"channel",
)


PORN_CORE = (
    # Turkish
    r"porno",
    r"pornografi",
    r"seks",
    r"sevişme",
    r"sevisme",
    r"sikiş",
    r"sikis",
    r"sikişme",
    r"sikisme",
    r"erotik\s+video",
    r"yetişkin\s+video",
    r"yetiskin\s+video",

    # English / international
    r"porn",
    r"porno",
    r"pornography",
    r"xxx",
    r"hardcore",
    r"softcore",
    r"hentai",
    r"rule\s*34",
    r"rule34",
    r"adult\s+video",
    r"adult\s+movie",
)


CONSUMPTION = (
    # Turkish
    r"izle",
    r"seyret",
    r"aç",
    r"ac",
    r"indir",
    r"bul",
    r"ara",
    r"link",
    r"linki",
    r"sitesi",
    r"site",
    r"video",
    r"videosu",
    r"filmi",
    r"film",
    r"galeri",
    r"galerisi",
    r"arşiv",
    r"arşivi",
    r"arsiv",
    r"arsivi",
    r"foto",
    r"fotoğraf",
    r"fotograf",
    r"resim",
    r"görüntü",
    r"goruntu",
    r"canlı",
    r"canli",

    # English
    r"watch",
    r"view",
    r"see",
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
    r"site",
    r"sites",
    r"links?",
    r"free",
    r"online",
    r"live",
)


NAMED_EXPLICIT = (
    r"pornhub",
    r"xvideos",
    r"xnxx",
    r"xhamster",
    r"redtube",
    r"youporn",
    r"brazzers",
    r"onlyfans\s+(?:ifşa|ifsa|leak|leaks|leaked|nude|nudes|porn)",
    r"(?:ifşa|ifsa|leaked|free)\s+onlyfans",
    r"fansly\s+(?:ifşa|ifsa|leak|leaks|leaked|nude|nudes|porn)",
    r"gonewild",
    r"camgirl",
    r"camgirls",
    r"webcam\s+sex",
    r"sex\s+cam",
    r"sex\s+cams",
    r"live\s+sex",
    r"escort\s+(?:ilan|ilanları|numara|numaraları|bul|ara)",
)


# Strong phrases that do not require a person term.
DIRECT_STRONG = (
    r"porno\s+(?:izle|seyret|aç|ac|indir|video|videosu|film|filmi|galeri|arşiv|arsiv|site|sitesi|link)",
    r"bedava\s+porno",
    r"ücretsiz\s+porno",
    r"ucretsiz\s+porno",
    r"online\s+porno",
    r"seks\s+(?:izle|video|videosu|film|filmi|kaset|kaseti|görüntü|goruntu|yayın|yayin|kamera|webcam)",
    r"sevişme\s+(?:izle|video|videosu|görüntü|goruntu|kaset|kaseti)",
    r"sevisme\s+(?:izle|video|videosu|goruntu|kaset|kaseti)",
    r"intikam\s+pornosu\s+(?:izle|video|görüntü|goruntu|ifşa|ifsa|arşiv|arsiv)",
    r"revenge\s+porn\s+(?:videos?|images?|photos?|pics?|watch|gallery|download)",
    r"porn\s+(?:videos?|movies?|clips?|gifs?|images?|pictures?|pics?|photos?|gallery|stream|streaming|download)",
    r"free\s+porn",
    r"watch\s+porn",
    r"download\s+porn",
    r"adult\s+(?:movies?|videos?)",
    r"sex\s+(?:videos?|movies?|tape|cams?|webcams?)",
    r"nude\s+(?:gallery|photos?|pics?|pictures?|images?|videos?|selfies?)",
    r"naked\s+(?:gallery|photos?|pics?|pictures?|images?|videos?|selfies?)",
    r"leaked\s+nudes?",
    r"nude\s+leaks?",
    r"celebrity\s+nudes?",
    r"private\s+(?:video|photos?|pics?)\s+leak(?:ed)?",
    r"leaked\s+private\s+(?:video|photos?|pics?)",
    r"gizli\s+(?:kamera|çekim)\s+(?:seks|sevişme|çıplak)",
    r"gizli\s+cekim\s+(?:seks|sevisme|ciplak)",
    r"voyeur\s+(?:video|videos?|pics?|photos?)",
    r"upskirt\s+(?:video|videos?|pics?|photos?)",
)


# ---------------------------------------------------------------------
# PROTECTED CONTEXTS
# ---------------------------------------------------------------------

RECOVERY_PROTECTED = (
    r"porno\s+bağımlılı(?:ğı|k)",
    r"porno\s+bagimlili(?:gi|k)",
    r"pornografi\s+bağımlılı(?:ğı|k)",
    r"pornografi\s+bagimlili(?:gi|k)",
    r"pornoyu\s+bırak",
    r"pornoyu\s+birak",
    r"porno\s+izlemeyi\s+bırak",
    r"porno\s+izlemeyi\s+birak",
    r"pornodan\s+kurtul",
    r"porno\s+bağımlılığı\s+tedavisi",
    r"porno\s+bagimliligi\s+tedavisi",
    r"pornografinin\s+zararları",
    r"pornografinin\s+zararlari",
    r"porno\s+engelleme",
    r"pornografi\s+araştırma",
    r"pornografi\s+arastirma",
    r"porn\s+addiction",
    r"pornography\s+addiction",
    r"quit\s+porn",
    r"stop\s+watching\s+porn",
    r"porn\s+recovery",
    r"pornography\s+recovery",
    r"porn\s+addiction\s+treatment",
    r"harms\s+of\s+pornography",
    r"porn\s+blocker",
    r"block\s+adult\s+content",
    r"pornography\s+research",
)


ABUSE_SUBJECT = (
    r"intikam\s+pornosu",
    r"özel\s+görüntü",
    r"ozel\s+goruntu",
    r"mahrem\s+görüntü",
    r"mahrem\s+goruntu",
    r"ifşa",
    r"ifsa",
    r"sızdırılmış\s+görüntü",
    r"sizdirilmis\s+goruntu",
    r"gizli\s+kamera",
    r"gizli\s+çekim",
    r"gizli\s+cekim",
    r"deepfake",
    r"çıplaklaştırma",
    r"ciplaklastirma",
    r"revenge\s+porn",
    r"intimate\s+image\s+abuse",
    r"non[\s-]?consensual\s+intimate\s+images?",
    r"image[\s-]?based\s+sexual\s+abuse",
    r"leaked\s+images?",
    r"leaked\s+photos?",
    r"hidden\s+camera",
    r"voyeurism",
    r"upskirt",
    r"deepfake\s+abuse",
    r"nudification",
)


HELP_CONTEXT = (
    # Turkish
    r"mağdur",
    r"mağduru",
    r"mağdurlar",
    r"mağdurları",
    r"magdur",
    r"magduru",
    r"magdurlar",
    r"magdurlari",
    r"mağdur\s+desteği",
    r"magdur\s+destegi",
    r"destek",
    r"yardım",
    r"yardim",
    r"hukuk",
    r"hukuki",
    r"yasal",
    r"yasa",
    r"yasası",
    r"yasasi",
    r"suç",
    r"suçu",
    r"suc",
    r"sucu",
    r"şikâyet",
    r"şikayet",
    r"sikayet",
    r"ihbar",
    r"bildir",
    r"kaldırma\s+talebi",
    r"kaldirma\s+talebi",
    r"nasıl\s+kaldırılır",
    r"nasil\s+kaldirilir",
    r"haklar",
    r"hakları",
    r"haklari",
    r"korunma",
    r"önleme",
    r"onleme",

    # English
    r"victim",
    r"victims",
    r"victim\s+support",
    r"survivor",
    r"survivors",
    r"support",
    r"help",
    r"legal",
    r"law",
    r"laws",
    r"crime",
    r"criminal",
    r"report",
    r"reporting",
    r"remove",
    r"removal",
    r"takedown",
    r"rights",
    r"safety",
    r"prevention",
)


def build_patterns() -> tuple[str, str, str]:
    people = alt(PEOPLE)
    nudity = alt(NUDITY)
    sexualized = alt(SEXUALIZED)
    revealing = alt(REVEALING)
    leak = alt(LEAK)
    media = alt(MEDIA)
    porn_core = alt(PORN_CORE)
    consumption = alt(CONSUMPTION)
    named_explicit = alt(NAMED_EXPLICIT)
    direct_strong = alt(DIRECT_STRONG)

    # Any punctuation, words or branding may occur between important terms.
    # The maximum distances are deliberately finite to avoid matching an
    # unrelated term elsewhere in a long title.
    page_risk_parts = (
        named_explicit,
        direct_strong,

        # "çıplak kadın", "nude amazing Turkish girl", etc.
        rf"{nudity}.{{0,55}}{people}",
        rf"{people}.{{0,55}}{nudity}",

        # "hot women", "seksi Türk kızları", etc.
        rf"{sexualized}.{{0,55}}{people}",
        rf"{people}.{{0,55}}{sexualized}",

        # Bikini / lingerie / transparent clothing intent.
        rf"{revealing}.{{0,55}}{people}",
        rf"{people}.{{0,55}}{revealing}",

        # Page-level leak intent. Unlike card filtering, media is not
        # required when leak + person/group already establishes intent.
        rf"{leak}.{{0,90}}{people}",
        rf"{people}.{{0,90}}{leak}",

        # Strong consumption intent.
        rf"{porn_core}.{{0,45}}{consumption}",
        rf"{consumption}.{{0,45}}{porn_core}",

        # Leak + media is strong even when a person term is omitted.
        rf"{leak}.{{0,55}}{media}",
        rf"{media}.{{0,55}}{leak}",
    )

    page_risk = alt(page_risk_parts)

    recovery = alt(RECOVERY_PROTECTED)
    abuse_subject = alt(ABUSE_SUBJECT)
    help_context = alt(HELP_CONTEXT)

    protected_parts = (
        recovery,

        # Both directions cover:
        # "intikam pornosu mağdur desteği"
        # "hukuki yardım: intikam pornosu"
        rf"{abuse_subject}.{{0,100}}{help_context}",
        rf"{help_context}.{{0,100}}{abuse_subject}",
    )

    protected = alt(protected_parts)

    # URL matching is intentionally ASCII-oriented because accented
    # characters may be UTF-8 percent encoded differently by websites.
    url_separator = r"(?:%20|%2520|\+|[-_./]|%2f|%3a){1,6}"

    url_people = alt(
        (
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
            r"kadin",
            r"kadinlar",
            r"kiz",
            r"kizlar",
            r"bayan",
            r"unlu",
            r"unluler",
            r"turk",
            r"turkish",
        )
    )

    url_nudity = alt(
        (
            r"nude",
            r"nudes",
            r"nudity",
            r"naked",
            r"topless",
            r"ciplak",
            r"ciplaklik",
            r"ustsuz",
        )
    )

    url_sexualized = alt(
        (
            r"hot",
            r"sexy",
            r"erotic",
            r"seductive",
            r"provocative",
            r"sultry",
            r"atesli",
            r"seksi",
            r"erotik",
            r"azdirici",
        )
    )

    url_leak = alt(
        (
            r"ifsa",
            r"ifsha",
            r"leak",
            r"leaks",
            r"leaked",
            r"sizdirilmis",
            r"sizinti",
            r"private",
        )
    )

    url_media = alt(
        (
            r"photo",
            r"photos",
            r"pic",
            r"pics",
            r"picture",
            r"pictures",
            r"image",
            r"images",
            r"video",
            r"videos",
            r"gallery",
            r"archive",
            r"collection",
            r"pack",
            r"foto",
            r"fotograf",
            r"resim",
            r"goruntu",
            r"galeri",
            r"arsiv",
        )
    )

    url_porn = alt(
        (
            r"porn",
            r"porno",
            r"xxx",
            r"hentai",
            r"sex",
            r"seks",
            r"sikis",
            r"sevisme",
        )
    )

    url_action = alt(
        (
            r"watch",
            r"download",
            r"stream",
            r"video",
            r"videos",
            r"movie",
            r"movies",
            r"gallery",
            r"archive",
            r"free",
            r"online",
            r"izle",
            r"indir",
            r"video",
            r"film",
            r"galeri",
            r"arsiv",
        )
    )

    url_risk = alt(
        (
            rf"{url_nudity}{url_separator}{url_people}",
            rf"{url_people}{url_separator}{url_nudity}",
            rf"{url_sexualized}{url_separator}{url_people}",
            rf"{url_people}{url_separator}{url_sexualized}",
            rf"{url_leak}(?:.{{0,120}}){url_people}",
            rf"{url_people}(?:.{{0,120}}){url_leak}",
            rf"{url_leak}{url_separator}{url_media}",
            rf"{url_media}{url_separator}{url_leak}",
            rf"{url_porn}{url_separator}{url_action}",
            rf"{url_action}{url_separator}{url_porn}",
            r"onlyfans(?:.{0,80})(?:ifsa|ifsha|leak|leaked|nude|porn)",
            r"(?:ifsa|ifsha|leak|leaked|free)(?:.{0,80})onlyfans",
        )
    )

    return page_risk, protected, url_risk


def generate_strict_page(output_path: Path = DEFAULT_OUTPUT) -> Path:
    page_risk, protected, url_risk = build_patterns()

    lines = [
        "! =============================================================================",
        "! TemizWeb — UNIVERSAL STRICT FULL-PAGE INTENT FILTER",
        "! File: filters/src/35-strict-page.txt",
        "!",
        "! GENERATED FILE — edit scripts/generate_strict_page.py instead.",
        "!",
        "! PURPOSE",
        "! - Apply Google-style full-page strictness to destination websites.",
        "! - Trigger from strong-risk page titles, H1 headings or URL paths.",
        "! - Cover Turkish and English combinatorial phrase variants.",
        "! - Preserve recovery, legal, reporting and victim-support contexts.",
        "!",
        "! IMPORTANT",
        "! - This is stricter than card-level filtering.",
        "! - A strong page/query intent hides the whole body.",
        "! - SafeSearch and Restricted Mode are still not forced.",
        "! =============================================================================",
        "",
        "! Strong-risk phrase in document title",
        (
            "*##html"
            f":has(title:has-text(/{page_risk}/iu))"
            f":not(:has(title:has-text(/{protected}/iu)))"
            f":not(:has(h1:has-text(/{protected}/iu)))"
            " > body"
        ),
        "",
        "! Strong-risk phrase in main page heading",
        (
            "*##html"
            f":has(h1:has-text(/{page_risk}/iu))"
            f":not(:has(title:has-text(/{protected}/iu)))"
            f":not(:has(h1:has-text(/{protected}/iu)))"
            " > body"
        ),
        "",
        "! ASCII and URL-encoded path/query fallback",
        (
            "*##html"
            f":matches-path(/{url_risk}/i)"
            f":not(:has(title:has-text(/{protected}/iu)))"
            f":not(:has(h1:has-text(/{protected}/iu)))"
            " > body"
        ),
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(
        "Generated universal strict-page filter: "
        f"{output_path.relative_to(ROOT)}"
    )
    return output_path


if __name__ == "__main__":
    generate_strict_page()
