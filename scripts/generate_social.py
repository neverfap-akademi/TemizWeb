#!/usr/bin/env python3
"""Generate TemizWeb's intentional-use social-media layers.

Outputs:
- filters/src/15-social-addiction.txt
- filters/src/25-social-content.txt

Policy:
- Preserve search, profiles/channels, direct posts/videos, messages,
  notifications, bookmarks/lists, composing, uploading and publishing.
- Remove passive endless feeds and algorithmic discovery surfaces.
- Filter PMO-risk cards/posts/videos during intentional browsing while
  preserving recovery, legal-help, victim-support and educational material.
"""
from __future__ import annotations

from pathlib import Path

from generate_strict_page import (
    EDITORIAL,
    alt,
    DIRECT,
    LEAK,
    MEDIA,
    NUDITY,
    PEOPLE,
    SEXUALIZED,
    build_pattern_families,
    build_safe_pattern,
)

ROOT = Path(__file__).resolve().parents[1]
ADDICTION_OUTPUT = ROOT / "filters" / "src" / "15-social-addiction.txt"
CONTENT_OUTPUT = ROOT / "filters" / "src" / "25-social-content.txt"


# ---------------------------------------------------------------------------
# Anti-addiction rules
# ---------------------------------------------------------------------------
# These rules target consumption surfaces, never composer/upload controls.
# YouTube Studio is a different hostname and is intentionally untouched.

ADDICTION_RULES = (
    # ------------------------------------------------------------------
    # Legacy-rule exceptions
    # ------------------------------------------------------------------
    # Older handwritten TemizWeb layers globally hid every Shorts card and
    # Instagram's Explore link. Disable those broad selectors first.
    ("Allow desktop Shorts rich cards", 'youtube.com#@#ytd-rich-item-renderer:has(a[href^="/shorts/"])'),
    ("Allow desktop Shorts search results", 'youtube.com#@#ytd-video-renderer:has(a[href^="/shorts/"])'),
    ("Allow desktop Shorts channel items", 'youtube.com#@#ytd-reel-item-renderer'),
    ("Allow mobile Shorts rich cards", 'm.youtube.com#@#ytm-rich-item-renderer:has(a[href*="/shorts/"])'),
    ("Allow mobile Shorts search results", 'm.youtube.com#@#ytm-video-with-context-renderer:has(a[href*="/shorts/"])'),
    ("Allow mobile Shorts channel items", 'm.youtube.com#@#ytm-reel-item-renderer'),
    ("Allow desktop Shorts shelves outside homepage", 'youtube.com#@#ytd-rich-section-renderer:has(a[href^="/shorts/"])'),
    ("Allow mobile Shorts lockups outside homepage", 'm.youtube.com#@#ytm-shorts-lockup-view-model'),
    ("Restore YouTube Subscriptions navigation", 'youtube.com#@#ytd-guide-entry-renderer:has(a[href^="/feed/subscriptions"]),ytd-mini-guide-entry-renderer:has(a[href^="/feed/subscriptions"])'),
    ("Restore mobile YouTube Subscriptions navigation", 'm.youtube.com#@#ytm-pivot-bar-item-renderer:has(a[href*="/feed/subscriptions"]),ytm-guide-entry-renderer:has(a[href*="/feed/subscriptions"])'),
    ("Restore Instagram Explore/Search link exact", 'instagram.com#@#a[href="/explore/"]'),
    ("Restore Instagram Explore/Search link prefix", 'instagram.com#@#a[href^="/explore/"]'),

    # ------------------------------------------------------------------
    # YouTube — homepage Shorts removed; channel/search/direct Shorts allowed
    # ------------------------------------------------------------------
    # The global Shorts entry button is removed. Shorts content is hidden only
    # on the root homepage; channel tabs, search results and direct Shorts work.
    (
        "YouTube desktop home page-subtype feed",
        'youtube.com##ytd-browse[page-subtype="home"] ytd-rich-grid-renderer',
    ),
    (
        "YouTube desktop what-to-watch browse feed",
        'youtube.com##ytd-browse[browse-id="FEwhat_to_watch"] ytd-rich-grid-renderer',
    ),
    (
        "YouTube desktop root homepage rich grid",
        'youtube.com#?#:matches-path(/^[/](?:[?].*)?$/) ytd-rich-grid-renderer',
    ),
    (
        "YouTube desktop root homepage browse results",
        'youtube.com#?#:matches-path(/^[/](?:[?].*)?$/) '
        'ytd-two-column-browse-results-renderer ytd-rich-grid-renderer',
    ),
    (
        "YouTube desktop homepage Shorts shelves",
        'youtube.com#?#:matches-path(/^[/](?:[?].*)?$/) '
        'ytd-rich-section-renderer:has(a[href^="/shorts/"])',
    ),
    (
        "YouTube desktop homepage reel shelves",
        'youtube.com#?#:matches-path(/^[/](?:[?].*)?$/) '
        'ytd-reel-shelf-renderer',
    ),
    (
        "YouTube desktop what-to-watch feed",
        'youtube.com##ytd-browse[browse-id="FEwhat_to_watch"] ytd-rich-grid-renderer',
    ),
    (
        "YouTube desktop Shorts guide navigation",
        'youtube.com#?#ytd-guide-entry-renderer:has(a[href^="/shorts/"]),'
        'ytd-guide-entry-renderer:has(a[href="/shorts"]),'
        'ytd-mini-guide-entry-renderer:has(a[href^="/shorts/"]),'
        'ytd-mini-guide-entry-renderer:has(a[href="/shorts"])',
    ),
    (
        "YouTube desktop Shorts navigation anchors",
        'youtube.com##ytd-guide-renderer a[href="/shorts"],'
        'ytd-mini-guide-renderer a[href="/shorts"],'
        'ytd-guide-renderer a[href^="/shorts/"],'
        'ytd-mini-guide-renderer a[href^="/shorts/"]',
    ),
    (
        "YouTube desktop Shorts titled navigation",
        'youtube.com#?#ytd-guide-entry-renderer:has(a[title="Shorts"]),'
        'ytd-mini-guide-entry-renderer:has(a[title="Shorts"]),'
        'ytd-guide-entry-renderer:has(a[aria-label="Shorts"]),'
        'ytd-mini-guide-entry-renderer:has(a[aria-label="Shorts"])',
    ),
    (
        "YouTube desktop watch-next recommendations",
        'youtube.com##ytd-watch-next-secondary-results-renderer',
    ),
    (
        "YouTube desktop endscreen recommendations",
        'youtube.com##.ytp-endscreen-content',
    ),

    # ------------------------------------------------------------------
    # Instagram — search UI remains; passive content and loaders disappear
    # ------------------------------------------------------------------
    # Hide the whole passive homepage canvas immediately. Instagram's Search
    # sidebar/dialog lives outside this main surface in current Firefox builds.
    (
        "Instagram root homepage post articles",
        'instagram.com#?#:matches-path(/^[/](?:[?].*)?$/) main article',
    ),

    # Suggested modules are removed at their containing section, including the
    # header, posts and spinner. Multiple structures cover current layouts.
    (
        "Instagram suggested post articles",
        'instagram.com#?#main section:has-text('
        '/(?:Suggested for you|Suggestions for you|For you|Önerilenler|'
        'Senin için(?: önerilenler)?)/i) article',
    ),
    (
        "Instagram suggested post links",
        'instagram.com#?#main section:has-text('
        '/(?:Suggested for you|Suggestions for you|For you|Önerilenler|'
        'Senin için(?: önerilenler)?)/i) '
        'a[href^="/p/"],'
        'main section:has-text('
        '/(?:Suggested for you|Suggestions for you|For you|Önerilenler|'
        'Senin için(?: önerilenler)?)/i) '
        'a[href^="/reel/"]',
    ),

    # On Explore/Search, leave the search sidebar and input intact while hiding
    # result/recommendation media and persistent loading indicators in main.
    (
        "Instagram Explore post tiles",
        'instagram.com#?#:matches-path(/^[/]explore(?:[/].*)?(?:[?].*)?$/) '
        'main a[href^="/p/"]',
    ),
    (
        "Instagram Explore reel tiles",
        'instagram.com#?#:matches-path(/^[/]explore(?:[/].*)?(?:[?].*)?$/) '
        'main a[href^="/reel/"]',
    ),
    (
        "Instagram Explore recommendation images",
        'instagram.com#?#:matches-path(/^[/]explore(?:[/].*)?(?:[?].*)?$/) '
        'main a[href^="/explore/"] img',
    ),
    (
        "Instagram Explore loading indicators",
        'instagram.com#?#:matches-path(/^[/]explore(?:[/].*)?(?:[?].*)?$/) '
        'main [role="progressbar"]',
    ),
    (
        "Instagram root loading indicators",
        'instagram.com#?#:matches-path(/^[/](?:[?].*)?$/) '
        'main [role="progressbar"]',
    ),
    ),
    ("Instagram Reels navigation", 'instagram.com##a[href="/reels/"]'),
    ("Instagram Reels endless feed", 'instagram.com##main:matches-path(/^[/]reels[/]?(?:[?].*)?$/)'),

    # ------------------------------------------------------------------
    # X / Twitter — remove Home destination and its primary surface
    # ------------------------------------------------------------------
    # The Home navigation button is removed so users cannot enter the passive
    # timeline. If /home is already open, the entire primary column is hidden
    # immediately, eliminating repeated For You/Following flashes. Global
    # compose buttons and compose dialogs remain outside these selectors.
    ("X Home navigation button", 'x.com##a[data-testid="AppTabBar_Home_Link"]'),
    ("Twitter Home navigation button", 'twitter.com##a[data-testid="AppTabBar_Home_Link"]'),
    ("X Home primary column", 'x.com##div[data-testid="primaryColumn"]:matches-path(/^[/]home(?:[?].*)?$/)'),
    ("Twitter Home primary column", 'twitter.com##div[data-testid="primaryColumn"]:matches-path(/^[/]home(?:[?].*)?$/)'),
    ("X Home fallback main region", 'x.com##main[role="main"]:matches-path(/^[/]home(?:[?].*)?$/)'),
    ("Twitter Home fallback main region", 'twitter.com##main[role="main"]:matches-path(/^[/]home(?:[?].*)?$/)'),
    ("X Explore discovery content", 'x.com##main section:matches-path(/^[/]explore(?:[/].*)?(?:[?].*)?$/):not(:has([data-testid="SearchBox_Search_Input"]))'),
    ("Twitter Explore discovery content", 'twitter.com##main section:matches-path(/^[/]explore(?:[/].*)?(?:[?].*)?$/):not(:has([data-testid="SearchBox_Search_Input"]))'),
    ("X trends sidebar", 'x.com##aside:has-text(/(?:What’s happening|What\'s happening|Trends for you|Gündemdekiler|İlgini çekebilecek gündemler)/i)'),
    ("Twitter trends sidebar", 'twitter.com##aside:has-text(/(?:What’s happening|What\'s happening|Trends for you|Gündemdekiler|İlgini çekebilecek gündemler)/i)'),
    ("X who-to-follow sidebar", 'x.com##aside:has-text(/(?:Who to follow|Kimi takip etmeli)/i)'),
    ("Twitter who-to-follow sidebar", 'twitter.com##aside:has-text(/(?:Who to follow|Kimi takip etmeli)/i)'),
)



# ---------------------------------------------------------------------------
# Social PMO card filtering
# ---------------------------------------------------------------------------

SOCIAL_TARGETS = {
    "youtube.com": (
        "ytd-video-renderer",
        "ytd-rich-item-renderer",
        "ytd-grid-video-renderer",
        "ytd-playlist-video-renderer",
        "ytd-reel-item-renderer",
    ),
    "m.youtube.com": (
        "ytm-video-with-context-renderer",
        "ytm-rich-item-renderer",
        "ytm-compact-video-renderer",
        "ytm-reel-item-renderer",
    ),
    "instagram.com": (
        "article",
        'a[href*="/p/"]',
        'a[href*="/reel/"]',
    ),
    "x.com": (
        'article[data-testid="tweet"]',
    ),
    "twitter.com": (
        'article[data-testid="tweet"]',
    ),
}

# Account/profile search results use a deliberately higher threshold than posts.
# A normal account is never hidden merely because one of its posts is risky.
ACCOUNT_TARGETS = {
    "instagram.com": (
        'div[role="listitem"]',
    ),
    "x.com": (
        'div[data-testid="UserCell"]',
    ),
    "twitter.com": (
        'div[data-testid="UserCell"]',
    ),
}


def build_account_identity_families() -> dict[str, tuple[str, ...]]:
    """Return high-threshold patterns for clearly PMO-dedicated accounts.

    Account cards require either a direct explicit identity or three distinct
    signal families. This is intentionally stricter than post/card filtering.
    """
    nsfw_identity = r"(?:nsfw|18\+|adult\s+content|yeti[şs]kin\s+i[cç]erik)"
    return {
        "direct_identity": (alt(DIRECT),),
        # Account identity is stronger evidence than one ordinary post. Names or
        # bios such as “seksi kızlar” and “nude women” are sufficient here.
        "sexualized_person": (alt(SEXUALIZED), alt(PEOPLE)),
        "nudity_person": (alt(NUDITY), alt(PEOPLE)),
        "leak_person": (alt(LEAK), alt(PEOPLE)),
        "nsfw_media": (nsfw_identity, alt(MEDIA)),
        # Three-signal forms remain for indirect or noisy account descriptions.
        "leak_person_media": (alt(LEAK), alt(PEOPLE), alt(MEDIA)),
        "nudity_person_media": (alt(NUDITY), alt(PEOPLE), alt(MEDIA)),
        "sexualized_person_media": (alt(SEXUALIZED), alt(PEOPLE), alt(MEDIA)),
    }


def _content_rule(host: str, selector: str, patterns: tuple[str, ...], *, editorial: bool) -> str:
    chain = selector
    for pattern in patterns:
        chain += f":has-text(/{pattern}/iu)"
    if editorial:
        chain += f":not(:has-text(/{alt(EDITORIAL)}/iu))"
    chain += f":not(:has-text(/{build_safe_pattern()}/iu))"
    return f"{host}#?#{chain}"


def generate_social_layers(
    addiction_output: Path = ADDICTION_OUTPUT,
    content_output: Path = CONTENT_OUTPUT,
) -> tuple[Path, Path]:
    addiction_lines = [
        "! =============================================================================",
        "! TemizWeb — INTENTIONAL SOCIAL MEDIA MODE",
        "! GENERATED FILE — edit scripts/generate_social.py instead.",
        "! Preserves search, profiles, messages, direct content, composing, uploads",
        "! and publishing. Removes passive feeds and algorithmic discovery.",
        "! =============================================================================",
        "",
    ]
    for index, (label, rule) in enumerate(ADDICTION_RULES, 1):
        addiction_lines.extend((f"! Rule {index}: {label}", rule, ""))

    families = build_pattern_families()
    content_lines = [
        "! =============================================================================",
        "! TemizWeb — SOCIAL PMO CONTENT FILTER",
        "! GENERATED FILE — edit scripts/generate_social.py instead.",
        "! Filters the smallest post/video card while preserving normal accounts.",
        "! Account cards use a separate, much higher identity threshold.",
        "! Recovery, legal help, education, composing, uploads and publishing remain.",
        "! =============================================================================",
        "",
    ]
    count = 0
    for host, selectors in SOCIAL_TARGETS.items():
        for selector in selectors:
            for family_name, patterns in families.items():
                count += 1
                content_lines.extend(
                    (
                        f"! Rule {count}: {host} / {selector} / post:{family_name}",
                        _content_rule(
                            host,
                            selector,
                            patterns,
                            editorial=(family_name == "leak_person"),
                        ),
                        "",
                    )
                )

    account_families = build_account_identity_families()
    for host, selectors in ACCOUNT_TARGETS.items():
        for selector in selectors:
            for family_name, patterns in account_families.items():
                count += 1
                content_lines.extend(
                    (
                        f"! Rule {count}: {host} / {selector} / account:{family_name}",
                        _content_rule(
                            host,
                            selector,
                            patterns,
                            editorial=False,
                        ),
                        "",
                    )
                )

    addiction_output.parent.mkdir(parents=True, exist_ok=True)
    addiction_output.write_text("\n".join(addiction_lines), encoding="utf-8")
    content_output.write_text("\n".join(content_lines), encoding="utf-8")

    print(
        f"Generated social anti-addiction layer: {addiction_output.relative_to(ROOT)} "
        f"({len(ADDICTION_RULES)} rules)"
    )
    print(
        f"Generated social PMO content layer: {content_output.relative_to(ROOT)} "
        f"({count} rules)"
    )
    return addiction_output, content_output


if __name__ == "__main__":
    generate_social_layers()
