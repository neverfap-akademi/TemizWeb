#!/usr/bin/env python3
"""Generate TemizWeb hostname-targeted strict full-page filters.

The language engine is shared across all supported sites. Only the hostname
and query-location adapters differ. This avoids unreliable generic procedural
filters while keeping the vocabulary centralized.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote, quote_plus

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "filters" / "src" / "35-strict-page.txt"


def alt(parts):
    cleaned = [p.strip() for p in parts if p and p.strip()]
    return "(?:" + "|".join(cleaned) + ")"


PEOPLE = (
    r"kad[ıi]n(?:lar(?:[ıi])?|[ıi])?", r"k[ıi]z(?:lar(?:[ıi])?|[ıi])?",
    r"bayan(?:lar[ıi]?)?", r"[üu]nl[üu](?:ler(?:in)?)?", r"model(?:ler(?:in)?)?",
    r"oyuncu(?:lar(?:[ıi]n)?)?", r"[şs]ark[ıi]c[ıi](?:lar(?:[ıi]n)?)?",
    r"[öo][ğg]renci(?:ler(?:in)?)?", r"liseli(?:ler(?:in)?)?",
    r"t[üu]rbanl[ıi](?:lar(?:[ıi]n)?)?", r"ba[şs][öo]rt[üu]l[üu](?:ler(?:in)?)?",
    r"hem[şs]ire(?:ler(?:in)?)?", r"[öo][ğg]retmen(?:ler(?:in)?)?",
    r"hostes(?:ler(?:in)?)?", r"gelin(?:ler(?:in)?)?", r"sevgili(?:ler(?:in)?)?",
    r"eski\s+sevgili(?:ler(?:in)?)?", r"t[üu]rk\s+k[ıi]zlar[ıi]",
    r"t[üu]rk\s+kad[ıi]nlar[ıi]", r"woman", r"women", r"girl", r"girls",
    r"lady", r"ladies", r"female", r"females", r"babe", r"babes",
    r"model", r"models", r"celebrity", r"celebrities", r"actress", r"actresses",
    r"singer", r"singers", r"student", r"students", r"schoolgirl", r"schoolgirls",
    r"influencer", r"influencers", r"bride", r"brides", r"nurse", r"nurses",
    r"teacher", r"teachers", r"turkish\s+girls?", r"turkish\s+women?",
)

SEXUALIZED = (
    r"seksi", r"erotik", r"ate[şs]li", r"azd[ıi]r[ıi]c[ıi]",
    r"tahrik\s+edici", r"ba[şs]tan\s+[cç][ıi]kar[ıi]c[ıi]",
    r"hot", r"sexy", r"erotic", r"seductive", r"provocative",
    r"sultry", r"steamy", r"racy", r"thirst[\s-]*trap",
)

NUDITY = (
    r"[cç][ıi]plak(?:l[ıi]k)?", r"[cç][ıi]r[ıi]l[cç][ıi]plak",
    r"[üu]sts[üu]z", r"anadan\s+do[ğg]ma", r"nude", r"nudes",
    r"nudity", r"naked", r"topless",
)

REVEALING = (
    r"bikinili", r"mayolu", r"i[cç]\s+[cç]ama[şs][ıi]rl[ıi]",
    r"s[üu]tyenli", r"s[üu]tyensiz", r"dekolteli", r"transparan",
    r"[şs]effaf\s+k[ıi]yafetli", r"tangal[ıi]", r"bikini",
    r"micro\s+bikini", r"swimsuit", r"lingerie", r"underwear",
    r"braless", r"no[\s-]*bra", r"thong", r"transparent",
    r"see[\s-]*through", r"sheer", r"revealing", r"cleavage",
    r"side[\s-]*boob", r"under[\s-]*boob", r"nip[\s-]*slip",
    r"wet[\s-]*t[\s-]*shirt",
)

LEAK = (
    r"if[şs]a(?:s[ıi]|lar[ıi])?", r"s[ıi]zd[ıi]r[ıi]lm[ıi][şs]",
    r"s[ıi]zd[ıi]r[ıi]lan", r"s[ıi]z[ıi]nt[ıi]", r"internete\s+d[üu][şs]t[üu]",
    r"[öo]zel\s+g[öo]r[üu]nt[üu]", r"mahrem\s+g[öo]r[üu]nt[üu]",
    r"gizli\s+[cç]ekim", r"leaks?", r"leaked", r"private\s+leak",
    r"private\s+(?:video|photos?|pics?)", r"sex\s+tape",
    r"hidden\s+camera", r"secretly\s+filmed",
)

MEDIA = (
    r"foto(?:lar)?", r"foto[ğg]raf(?:lar)?", r"resim(?:ler)?",
    r"g[öo]r[üu]nt[üu](?:ler)?", r"video(?:lar)?", r"kaset(?:i)?",
    r"klip(?:ler)?", r"galeri(?:si)?", r"ar[şs]iv(?:i)?", r"link(?:i)?",
    r"telegram", r"kanal(?:[ıi])?", r"grup(?:u)?", r"photos?", r"pictures?",
    r"pics?", r"images?", r"videos?", r"clips?", r"gifs?", r"gallery",
    r"archive", r"collection", r"pack", r"album", r"stream", r"download",
)

PORN_CORE = (
    r"porno", r"pornografi", r"seks", r"sevi[şs]me", r"siki[şs](?:me)?",
    r"porn", r"pornography", r"xxx", r"hardcore", r"softcore", r"hentai",
    r"rule[\s-]*34", r"adult\s+(?:video|movie)",
)

CONSUMPTION = (
    r"izle", r"seyret", r"a[cç]", r"indir", r"bul", r"ara", r"link(?:i)?",
    r"site(?:si)?", r"video(?:su)?", r"film(?:i)?", r"galeri(?:si)?",
    r"ar[şs]iv(?:i)?", r"foto(?:[ğg]raf)?", r"resim", r"g[öo]r[üu]nt[üu]",
    r"canl[ıi]", r"watch", r"view", r"download", r"stream", r"videos?",
    r"movies?", r"films?", r"clips?", r"gifs?", r"images?", r"pictures?",
    r"pics?", r"photos?", r"gallery", r"archive", r"collection", r"sites?",
    r"links?", r"free", r"online", r"live",
)

DIRECT = (
    r"pornhub", r"xvideos", r"xnxx", r"xhamster", r"redtube", r"youporn",
    r"brazzers", r"gonewild", r"camgirls?", r"webcam\s+sex", r"live\s+sex",
    r"sex\s+cams?", r"onlyfans.{0,50}(?:if[şs]a|leak|leaked|nude|porn)",
    r"(?:if[şs]a|leak|leaked|free).{0,50}onlyfans",
    r"fansly.{0,50}(?:if[şs]a|leak|leaked|nude|porn)", r"free\s+porn",
    r"watch\s+porn", r"download\s+porn", r"leaked\s+nudes?",
    r"nude\s+leaks?", r"celebrity\s+nudes?",
)

RECOVERY = (
    # Direct Turkish recovery language
    r"porno(?:grafi)?\s+ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi](?:ndan)?",
    r"porno(?:grafi)?\s+ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi]\s+tedavi(?:si)?",
    r"porno(?:grafi)?\s+ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi]ndan\s+kurtul",
    r"pornoyu\s+b[ıi]rak(?:mak|ma|maya|t[ıi]m)?",
    r"pornografiyi\s+b[ıi]rak(?:mak|ma|maya|t[ıi]m)?",
    r"porno\s+izlemeyi\s+b[ıi]rak(?:mak|ma|maya|t[ıi]m)?",
    r"porno\s+izlemekten\s+vazge[cç](?:mek|me)",
    r"pornodan\s+kurtul(?:mak|ma|maya)?",
    r"pornografiden\s+kurtul(?:mak|ma|maya)?",
    r"porno.{0,45}(?:tedavi|terapi|iyile[şs]me|rehabilitasyon)",
    r"(?:tedavi|terapi|iyile[şs]me).{0,45}porno",
    r"pornografinin\s+zararlar[ıi]",
    r"porno(?:grafi)?\s+(?:engelleme|filtresi|filtreleme|bloklama)",
    r"cinsel\s+i[cç]erik(?:ler)?(?:i|ten)?.{0,100}"
    r"(?:b[ıi]rak|vazge[cç]|kurtul|uzak\s+dur|izleme)",
    r"(?:b[ıi]rak|vazge[cç]|kurtul|uzak\s+dur).{0,100}"
    r"cinsel\s+i[cç]erik",
    r"cinsel\s+i[cç]erik(?:li)?\s+video(?:lar[ıi])?\s+izlemekten\s+vazge[cç]",
    r"m[üu]stehcen\s+i[cç]erik(?:ler)?(?:i|ten)?.{0,100}"
    r"(?:b[ıi]rak|vazge[cç]|kurtul|uzak\s+dur|izleme)",
    r"pmo\s+(?:ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi]|iyile[şs]me|kurtulma|recovery|tedavi)",
    r"(?:pmo|porno).{0,60}(?:n[üu]ks|relapse|yeniden\s+ba[şs]lama)",
    r"(?:n[üu]ks|relapse).{0,60}(?:pmo|porno)",

    # Recovery communities / established terminology
    r"never\s*fap",
    r"neverfap",
    r"no\s*fap",
    r"nofap",
    r"porn\s*free",
    r"pornfree",
    r"reboot(?:ing)?",

    # English recovery language
    r"porn(?:ography)?\s+addiction",
    r"quit(?:ting)?\s+porn(?:ography)?",
    r"stop(?:ping)?\s+watching\s+porn(?:ography)?",
    r"stop(?:ping)?\s+viewing\s+sexual\s+content",
    r"give\s+up\s+porn(?:ography)?",
    r"overcome\s+porn(?:ography)?",
    r"break\s+(?:a\s+)?porn\s+habit",
    r"freedom\s+from\s+porn(?:ography)?",
    r"recover(?:y|ing)?\s+from\s+porn(?:ography)?",
    r"porn(?:ography)?\s+recovery",
    r"pmo\s+recovery",
    r"porn.{0,45}(?:treatment|therapy|recovery|rehab|healing)",
    r"(?:treatment|therapy|recovery|healing).{0,45}porn",
    r"harms?\s+of\s+pornography",
    r"porn\s+blocker",
    r"block\s+(?:porn|adult|sexual)\s+content",
    r"pornography\s+research",
    r"sexual\s+content.{0,100}(?:quit|stop|avoid|recovery|addiction)",
    r"(?:quit|stop|avoid|recovery).{0,100}sexual\s+content",
)


# High-confidence recovery signals that are safe enough to override strict
# full-page blocking when they occur anywhere in the rendered page content.
# These are intentionally narrower than the full RECOVERY vocabulary.
BODY_RECOVERY_STANDALONE = (
    r"never\s*fap",
    r"neverfap",
    r"no\s*fap",
    r"nofap",
    r"pmo\s+recovery",
    r"porn(?:ography)?\s+recovery",
    r"porn(?:ography)?\s+addiction",
    r"porno(?:grafi)?\s+ba[ğg][ıi]ml[ıi]l[ıi][ğg][ıi]",
    r"pornoyu\s+b[ıi]rak",
    r"pornografiyi\s+b[ıi]rak",
    r"porno\s+izlemeyi\s+b[ıi]rak",
    r"pornodan\s+kurtul",
    r"pornografiden\s+kurtul",
    r"quit(?:ting)?\s+porn(?:ography)?",
    r"stop(?:ping)?\s+watching\s+porn(?:ography)?",
    r"recover(?:y|ing)?\s+from\s+porn(?:ography)?",
    r"freedom\s+from\s+porn(?:ography)?",
    r"porn\s*free",
    r"pornfree",
)

# Broader recovery words are only safe when they occur near a PMO/content
# subject. This protects subtle articles without making generic occurrences
# of words such as "treatment" or "addiction" a global bypass.
BODY_RECOVERY_SUBJECT = (
    r"porno", r"pornografi", r"porn", r"pornography", r"pmo",
    r"cinsel\s+i[cç]erik", r"sexual\s+content",
    r"m[üu]stehcen\s+i[cç]erik", r"adult\s+content",
)

BODY_RECOVERY_ACTION = (
    r"ba[ğg][ıi]ml[ıi]l[ıi]k", r"addiction",
    r"b[ıi]rak(?:mak|ma|maya|t[ıi]m)?", r"quit(?:ting)?",
    r"vazge[cç](?:mek|me)", r"stop(?:ping)?",
    r"kurtul(?:mak|ma|maya)?", r"overcome",
    r"tedavi(?:si)?", r"treatment", r"therapy", r"terapi",
    r"iyile[şs]me", r"recovery", r"healing", r"rehab",
    r"n[üu]ks", r"relapse", r"reboot(?:ing)?",
    r"engelleme", r"filtreleme", r"blocker", r"avoid",
    r"uzak\s+dur", r"temiz\s+kal", r"porn\s*free",
)

ABUSE = (
    r"intikam\s+pornosu", r"[öo]zel\s+g[öo]r[üu]nt[üu]",
    r"mahrem\s+g[öo]r[üu]nt[üu]", r"if[şs]a", r"gizli\s+(?:kamera|[cç]ekim)",
    r"deepfake", r"[cç][ıi]plakla[şs]t[ıi]rma", r"revenge\s+porn",
    r"intimate\s+image\s+abuse", r"non[\s-]*consensual\s+intimate\s+images?",
    r"image[\s-]*based\s+sexual\s+abuse", r"leaked\s+(?:images?|photos?)",
    r"hidden\s+camera", r"voyeurism", r"upskirt", r"nudification",
)

HELP = (
    r"ma[ğg]dur(?:u|lar[ıi]?)?", r"destek", r"yard[ıi]m", r"hukuk(?:i)?",
    r"yasal", r"yasa(?:s[ıi])?", r"su[cç](?:u)?", r"[şs]ikayet", r"ihbar",
    r"bildir", r"kald[ıi]rma", r"haklar[ıi]?", r"korunma", r"[öo]nleme",
    r"victims?", r"survivors?", r"support", r"help", r"legal", r"laws?",
    r"crime", r"criminal", r"reporting", r"removal", r"takedown", r"rights",
    r"prevention",
)

LINGUISTIC = (
    r"kelimesi", r"kelimenin", r"anlam[ıi]", r"ne\s+demek", r"[cç]eviri",
    r"s[öo]zl[üu]k", r"tan[ıi]m", r"definition", r"meaning", r"translation",
    r"dictionary", r"etymology",
)

EDITORIAL = (
    r"haber(?:ler(?:i)?|i)?", r"g[üu]ndem", r"son\s+dakika", r"bas[ıi]n",
    r"gazete(?:si)?", r"makale", r"inceleme", r"analiz", r"ara[şs]t[ıi]rma",
    r"belgesel", r"dava", r"mahkeme", r"soru[şs]turma", r"news",
    r"headlines?", r"journalism", r"article", r"reports?", r"analysis",
    r"investigation", r"documentary", r"court", r"lawsuit",
)

# Hostname-targeted procedural rules. Add new sites here, not new vocabularies.
HOST_GROUPS = {
    "search": (
        "google.com", "google.com.tr", "bing.com", "duckduckgo.com",
        "search.yahoo.com", "yandex.com", "yandex.com.tr", "yandex.ru",
        "brave.com", "startpage.com",
    ),
    "social_search": (
        "nitter.net", "ok.ru", "reddit.com", "www.reddit.com",
        "old.reddit.com", "pinterest.com", "www.pinterest.com",
    ),
    "image_search": (
        "shutterstock.com", "www.shutterstock.com", "pixabay.com", "www.pixabay.com",
        "pexels.com", "www.pexels.com", "freepik.com", "www.freepik.com",
        "unsplash.com", "www.unsplash.com", "gettyimages.com", "www.gettyimages.com",
        "istockphoto.com", "www.istockphoto.com", "depositphotos.com",
        "www.depositphotos.com", "dreamstime.com", "www.dreamstime.com",
    ),
}

COMMON_SIGNALS = (
    'title:has-text(/{pattern}/iu)',
    'h1:has-text(/{pattern}/iu)',
    'h2:has-text(/{pattern}/iu)',
    '[role="heading"]:has-text(/{pattern}/iu)',
    'input[type="search"]:watch-attr(value):matches-attr(value=/{pattern}/iu)',
    'input[name="q"]:watch-attr(value):matches-attr(value=/{pattern}/iu)',
    'input[role="searchbox"]:watch-attr(value):matches-attr(value=/{pattern}/iu)',
    'textarea[name="q"]:has-text(/{pattern}/iu)',
    'textarea[name="q"]:watch-attr(value):matches-attr(value=/{pattern}/iu)',
    '[role="combobox"]:has-text(/{pattern}/iu)',
    '[role="combobox"]:watch-attr(aria-label):matches-attr(aria-label=/{pattern}/iu)',
    '[role="search"]:has-text(/{pattern}/iu)',
)


def encoded_group(values):
    out = []
    for value in values:
        variants = {
            value, quote(value, safe=""), quote_plus(value, safe=""),
            value.replace(" ", "-"), value.replace(" ", "_"), value.replace(" ", "+"),
        }
        out.extend(re.escape(v) for v in sorted(variants))
    return alt(tuple(dict.fromkeys(out)))


def build_pattern_families():
    people, sexualized, nudity = alt(PEOPLE), alt(SEXUALIZED), alt(NUDITY)
    revealing, leak, media = alt(REVEALING), alt(LEAK), alt(MEDIA)
    porn, consumption, direct = alt(PORN_CORE), alt(CONSUMPTION), alt(DIRECT)
    editorial = alt(EDITORIAL)

    text = {
        "direct": direct,
        "sexualized_person": alt((rf"{sexualized}.{{0,80}}{people}", rf"{people}.{{0,80}}{sexualized}")),
        "nudity_person": alt((rf"{nudity}.{{0,80}}{people}", rf"{people}.{{0,80}}{nudity}")),
        "revealing_person": alt((rf"{revealing}.{{0,80}}{people}", rf"{people}.{{0,80}}{revealing}")),
        "leak_media": alt((rf"{leak}.{{0,90}}{media}", rf"{media}.{{0,90}}{leak}")),
        "leak_person": alt((
            rf"(?!.*{editorial}){leak}.{{0,120}}{people}",
            rf"(?!.*{editorial}){people}.{{0,120}}{leak}",
        )),
        "porn_consumption": alt((rf"{porn}.{{0,60}}{consumption}", rf"{consumption}.{{0,60}}{porn}")),
    }

    abuse, help, recovery, linguistic = alt(ABUSE), alt(HELP), alt(RECOVERY), alt(LINGUISTIC)
    protected = alt((
        recovery,
        rf"{abuse}.{{0,140}}{help}", rf"{help}.{{0,140}}{abuse}",
        rf"(?:{sexualized}|{nudity}|{leak}).{{0,80}}{linguistic}",
        rf"{linguistic}.{{0,80}}(?:{sexualized}|{nudity}|{leak})",
    ))

    url_people = encoded_group(("kadın", "kadınlar", "kadin", "kadinlar", "kız", "kızlar", "kiz", "kizlar", "türk kızları", "turk kizlari", "woman", "women", "girl", "girls", "female", "model", "models", "celebrity", "turkish girls", "turkish women"))
    url_sexualized = encoded_group(("seksi", "ateşli", "atesli", "erotik", "hot", "sexy", "erotic", "seductive", "provocative"))
    url_nudity = encoded_group(("çıplak", "ciplak", "çıplaklık", "ciplaklik", "nude", "nudes", "naked", "topless"))
    url_leak = encoded_group(("ifşa", "ifsa", "sızdırılmış", "sizdirilmis", "sızıntı", "sizinti", "leak", "leaks", "leaked"))
    url_media = encoded_group(("foto", "fotoğraf", "fotograf", "resim", "görüntü", "goruntu", "video", "galeri", "arşiv", "arsiv", "photo", "photos", "pics", "images", "videos", "gallery", "archive"))
    url_editorial = encoded_group(("haber", "haberler", "haberleri", "gündem", "gundem", "son dakika", "news", "headlines", "article", "report", "investigation", "court", "lawsuit"))

    urls = {
        "direct": alt((r"onlyfans.{0,180}(?:ifsa|if%C5%9Fa|leak|leaked|nude|porn)", r"(?:ifsa|if%C5%9Fa|leak|leaked|free).{0,180}onlyfans", r"(?:porn|porno|xxx|hentai).{0,120}(?:watch|izle|video|videos|gallery|galeri|archive|arsiv|download|indir)")),
        "sexualized_person": alt((rf"{url_sexualized}.{{0,220}}{url_people}", rf"{url_people}.{{0,220}}{url_sexualized}")),
        "nudity_person": alt((rf"{url_nudity}.{{0,220}}{url_people}", rf"{url_people}.{{0,220}}{url_nudity}")),
        "leak_media": alt((rf"{url_leak}.{{0,220}}{url_media}", rf"{url_media}.{{0,220}}{url_leak}")),
        "leak_person": alt((rf"(?!.*{url_editorial}){url_leak}.{{0,260}}{url_people}", rf"(?!.*{url_editorial}){url_people}.{{0,260}}{url_leak}")),
    }
    return text, protected, urls


def build_url_protected():
    """Build URL/path recovery exceptions, including encoded Turkish forms."""
    recovery_subject = encoded_group((
        "porno", "pornografi", "porn", "pornography", "pmo",
        "cinsel içerik", "cinsel icerik", "sexual content",
        "müstehcen içerik", "mustehcen icerik",
    ))
    recovery_action = encoded_group((
        "bırak", "birak", "bırakmak", "birakmak", "bırakma", "birakma",
        "vazgeç", "vazgec", "vazgeçmek", "vazgecmek",
        "kurtul", "kurtulmak", "tedavi", "tedavisi", "terapi",
        "iyileşme", "iyilesme", "bağımlılık", "bagimlilik",
        "engelleme", "filtreleme", "nüks", "nuks", "relapse",
        "recovery", "quit", "stop watching", "treatment", "therapy",
        "healing", "addiction", "blocker", "avoid",
    ))
    recovery_brand = encoded_group((
        "neverfap", "never fap", "nofap", "no fap", "pornfree",
        "porn free", "pmo recovery", "reboot", "rebooting",
    ))

    return alt((
        recovery_brand,
        rf"{recovery_subject}.{{0,260}}{recovery_action}",
        rf"{recovery_action}.{{0,260}}{recovery_subject}",
    ))



def build_body_recovery_override():
    """Return a body-wide recovery override for supported hostnames."""
    standalone = alt(BODY_RECOVERY_STANDALONE)
    subject = alt(BODY_RECOVERY_SUBJECT)
    action = alt(BODY_RECOVERY_ACTION)
    contextual = alt((
        rf"{subject}.{{0,180}}{action}",
        rf"{action}.{{0,180}}{subject}",
    ))
    return alt((standalone, contextual))


def build_patterns():
    text, protected, urls = build_pattern_families()
    return alt(tuple(text.values())), protected, alt(tuple(urls.values()))


def effective_text_block(text_value, compiled, protected_re):
    return bool(any(rx.search(text_value) for rx in compiled.values()) and not protected_re.search(text_value))


def run_regression_tests():
    text, protected, urls = build_pattern_families()
    compiled = {k: re.compile(v, re.I) for k, v in text.items()}
    url_compiled = {k: re.compile(v, re.I) for k, v in urls.items()}
    protected_re = re.compile(protected, re.I)
    url_protected_re = re.compile(build_url_protected(), re.I)
    body_recovery_re = re.compile(build_body_recovery_override(), re.I)

    block = (
        "seksi kız", "seksi kızlar", "seksi kiz", "seksi kizlar",
        "seksi güzel Türk kızları", "hot girl", "hot girls", "hot women",
        "hot amazing Turkish girl", "sexy female models", "çıplak kadın",
        "ciplak kadinlar", "nude Turkish women", "naked girl gallery",
        "ifşa amazing girl türk kızları", "ifsa turk kizlari",
        "Türk kızları yeni ifşa", "ünlü oyuncu özel görüntü ifşa",
        "leaked celebrity photos", "private Turkish model leaked",
        "onlyfans ifşa", "free porn videos", "porno izle",
        "ifşa kız videoları haber", "leaked girl videos news",
    )
    allow = (
        "kadın bilim insanları", "Türk kızlarının eğitim başarısı", "hot weather",
        "hot water system", "model uçak yapımı", "bikini tarihi", "mayo tasarımı",
        "seksi kelimesinin anlamı", "ifşa kelimesinin anlamı", "ifşa kız haberleri",
        "ifşa Türk kızları haberleri", "ünlü oyuncu ifşa davası",
        "leaked celebrity news", "celebrity leak investigation",
        "intikam pornosu mağdur desteği", "ifşa mağduru hukuki yardım",
        "özel görüntülerin yayılması suçu", "intimate image abuse support",
        "revenge porn law", "porn recovery", "pornography addiction treatment",
        "pornoyu bırakmak", "porno tedavisi", "pornodan kurtulmak",
        "neverfap", "pmo recovery",
        "cinsel içerikler videoları izlemekten vazgeçmek",
        "cinsel içerik izlemeyi bırakma", "porno bağımlılığından kurtulma",
        "Pornonun ıstırabı üzerine bir yazı. Bu bağımlılık insanı tüketiyor.",
        "Başlık tetikleyici olabilir ama içerik NeverFap yaklaşımını anlatıyor.",
        "Bu yazıda pornografiden kurtulma ve nüks önleme ele alınıyor.",
        "Sexual content can be destructive; this article discusses addiction recovery.",
    )
    url_block = (
        "search?q=seksi+k%C4%B1z", "search?q=seksi+kiz", "search?q=hot+girl",
        "search?q=hot%20girls", "search?q=%C3%A7%C4%B1plak+kad%C4%B1n",
        "search?q=ciplak+kadin", "search?q=if%C5%9Fa+turk+kizlari",
        "search?q=ifsa+turk+kizlari", "search?f=tweets&q=seksi+k%C4%B1z",
    )
    url_allow = (
        "search?q=if%C5%9Fa+k%C4%B1z+haberleri", "search?q=ifsa+kiz+haberleri",
        "search?q=hot+weather", "search?q=kadin+bilim+insanlari",
        "search?q=pornoyu+b%C4%B1rakmak", "search?q=porno+tedavisi",
        "search?q=pornodan+kurtulmak", "search?q=neverfap",
        "search?q=pmo+recovery",
        "search?q=cinsel+i%C3%A7erik+izlemekten+vazge%C3%A7mek",
    )

    failures = []
    for value in block:
        if not effective_text_block(value, compiled, protected_re):
            failures.append(f"Expected BLOCK: {value!r}")
    for value in allow:
        if effective_text_block(value, compiled, protected_re):
            failures.append(f"Expected ALLOW: {value!r}")
    for value in url_block:
        if not any(rx.search(value) for rx in url_compiled.values()):
            failures.append(f"Expected URL BLOCK: {value!r}")
    for value in url_allow:
        effective_url_block = (
            any(rx.search(value) for rx in url_compiled.values())
            and not url_protected_re.search(value)
        )
        if effective_url_block:
            failures.append(f"Expected URL ALLOW: {value!r}")
    body_recovery_cases = (
        "Pornonun ıstırabı. Bağımlılık döngüsünü kırmak mümkündür.",
        "NeverFap topluluğu iyileşme sürecine destek olur.",
        "Cinsel içerik izlemekten vazgeçmek ve temiz kalmak.",
        "Porn addiction recovery and relapse prevention.",
    )
    for value in body_recovery_cases:
        if not body_recovery_re.search(value):
            failures.append(f"Expected BODY RECOVERY OVERRIDE: {value!r}")
    if failures:
        raise RuntimeError("Strict-page regression failures:\n- " + "\n- ".join(failures))
    print(f"Strict-page regression tests passed: {len(block)} block text, {len(allow)} allow text, {len(url_block)} block URLs, {len(url_allow)} allow URLs")


def guards(protected, body_recovery):
    """Protect recovery/legal intent in intent signals and meaningful page content."""
    return (
        f":not(:has(body:has-text(/{body_recovery}/iu)))"
        f":not(:has(title:has-text(/{protected}/iu)))"
        f":not(:has(h1:has-text(/{protected}/iu)))"
        f":not(:has(h2:has-text(/{protected}/iu)))"
        f":not(:has([role=\"heading\"]:has-text(/{protected}/iu)))"
        f":not(:has(input[type=\"search\"]:watch-attr(value):matches-attr(value=/{protected}/iu)))"
        f":not(:has(input[name=\"q\"]:watch-attr(value):matches-attr(value=/{protected}/iu)))"
        f":not(:has(input[role=\"searchbox\"]:watch-attr(value):matches-attr(value=/{protected}/iu)))"
        f":not(:has(textarea[name=\"q\"]:has-text(/{protected}/iu)))"
        f":not(:has(textarea[name=\"q\"]:watch-attr(value):matches-attr(value=/{protected}/iu)))"
        f":not(:has([role=\"combobox\"]:has-text(/{protected}/iu)))"
        f":not(:has([role=\"combobox\"]:watch-attr(aria-label):matches-attr(aria-label=/{protected}/iu)))"
        f":not(:has([role=\"search\"]:has-text(/{protected}/iu)))"
    )


def generate_strict_page(output_path=DEFAULT_OUTPUT):
    run_regression_tests()
    text, protected, urls = build_pattern_families()
    body_recovery = build_body_recovery_override()
    protection = guards(protected, body_recovery)
    url_protected = build_url_protected()
    rules = []

    for group_name, hosts in HOST_GROUPS.items():
        prefix = ",".join(hosts)
        for family_name, pattern in text.items():
            for signal in COMMON_SIGNALS:
                selector = signal.format(pattern=pattern)
                rules.append((f"{group_name}/{family_name}/DOM", f"{prefix}##html:has({selector}){protection} > body"))
        for family_name, pattern in urls.items():
            rules.append((
                f"{group_name}/{family_name}/URL",
                f"{prefix}##html:matches-path(/{pattern}/i)"
                f":not(:matches-path(/{url_protected}/i)){protection} > body",
            ))

    lines = [
        "! =============================================================================",
        "! TemizWeb — HOSTNAME-TARGETED STRICT FULL-PAGE INTENT FILTER",
        "! GENERATED FILE — edit scripts/generate_strict_page.py instead.",
        "! Shared language engine; hostname/query-location adapters only.",
        "! =============================================================================", "",
    ]
    for i, (label, rule) in enumerate(rules, 1):
        lines.extend((f"! Rule {i}: {label}", rule, ""))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated hostname-targeted strict-page filter: {output_path.relative_to(ROOT)}")
    print(f"Generated {len(rules)} focused strict-page rules across {sum(len(v) for v in HOST_GROUPS.values())} host entries")
    return output_path


if __name__ == "__main__":
    generate_strict_page()
