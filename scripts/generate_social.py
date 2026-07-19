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
- Block strongly PMO-risky social-media search queries in PMO/main mode,
  while preserving recovery, legal-help and educational queries.
"""

from __future__ import annotations

from pathlib import Path

from generate_strict_page import (
    EDITORIAL,
    DIRECT,
    LEAK,
    MEDIA,
    NUDITY,
    PEOPLE,
    SEXUALIZED,
    alt,
    build_pattern_families,
    build_safe_pattern,
)


ROOT = Path(__file__).resolve().parents[1]

ADDICTION_OUTPUT = (
    ROOT
    / "filters"
    / "src"
    / "15-social-addiction.txt"
)

CONTENT_OUTPUT = (
    ROOT
    / "filters"
    / "src"
    / "25-social-content.txt"
)


# ---------------------------------------------------------------------------
# Anti-addiction rules
# ---------------------------------------------------------------------------
#
# These rules target passive consumption surfaces.
# Composer, upload and publishing controls must remain usable.
# YouTube Studio is a separate hostname and is intentionally untouched.
#
ADDICTION_RULES = (
    # ------------------------------------------------------------------
    # Legacy-rule exceptions
    # ------------------------------------------------------------------
    #
    # Older handwritten TemizWeb layers globally hid Shorts cards and
    # Instagram Explore links. Disable those broad rules first.
    #
    (
        "Allow desktop Shorts rich cards",
        'youtube.com#@#ytd-rich-item-renderer:has('
        'a[href^="/shorts/"])',
    ),
    (
        "Allow desktop Shorts search results",
        'youtube.com#@#ytd-video-renderer:has('
        'a[href^="/shorts/"])',
    ),
    (
        "Allow desktop Shorts channel items",
        "youtube.com#@#ytd-reel-item-renderer",
    ),
    (
        "Allow mobile Shorts rich cards",
        'm.youtube.com#@#ytm-rich-item-renderer:has('
        'a[href*="/shorts/"])',
    ),
    (
        "Allow mobile Shorts search results",
        'm.youtube.com#@#ytm-video-with-context-renderer:has('
        'a[href*="/shorts/"])',
    ),
    (
        "Allow mobile Shorts channel items",
        "m.youtube.com#@#ytm-reel-item-renderer",
    ),
    (
        "Allow desktop Shorts shelves outside homepage",
        'youtube.com#@#ytd-rich-section-renderer:has('
        'a[href^="/shorts/"])',
    ),
    (
        "Allow mobile Shorts lockups outside homepage",
        "m.youtube.com#@#ytm-shorts-lockup-view-model",
    ),
    (
        "Restore YouTube Subscriptions navigation",
        'youtube.com#@#ytd-guide-entry-renderer:has('
        'a[href^="/feed/subscriptions"]),'
        'ytd-mini-guide-entry-renderer:has('
        'a[href^="/feed/subscriptions"])',
    ),
    (
        "Restore mobile YouTube Subscriptions navigation",
        'm.youtube.com#@#ytm-pivot-bar-item-renderer:has('
        'a[href*="/feed/subscriptions"]),'
        'ytm-guide-entry-renderer:has('
        'a[href*="/feed/subscriptions"])',
    ),
    (
        "Restore Instagram Explore Search link exact",
        'instagram.com#@#a[href="/explore/"]',
    ),
    (
        "Restore Instagram Explore Search link prefix",
        'instagram.com#@#a[href^="/explore/"]',
    ),

    # ------------------------------------------------------------------
    # YouTube desktop
    # ------------------------------------------------------------------
    #
    # Homepage recommendations and the global Shorts entrance are hidden.
    # Search Shorts, channel Shorts and direct Shorts remain available.
    #
    (
        "YouTube desktop home page-subtype feed",
        'youtube.com##ytd-browse[page-subtype="home"] '
        "ytd-rich-grid-renderer",
    ),
    (
        "YouTube desktop what-to-watch browse feed",
        'youtube.com##ytd-browse[browse-id="FEwhat_to_watch"] '
        "ytd-rich-grid-renderer",
    ),
    (
        "YouTube desktop root homepage rich grid",
        "youtube.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "ytd-rich-grid-renderer",
    ),
    (
        "YouTube desktop root homepage browse results",
        "youtube.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "ytd-two-column-browse-results-renderer "
        "ytd-rich-grid-renderer",
    ),
    (
        "YouTube desktop homepage Shorts shelves",
        "youtube.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "ytd-rich-section-renderer:"
        'has(a[href^="/shorts/"])',
    ),
    (
        "YouTube desktop homepage reel shelves",
        "youtube.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "ytd-reel-shelf-renderer",
    ),
    (
        "YouTube desktop Shorts guide navigation",
        'youtube.com#?#ytd-guide-entry-renderer:has('
        'a[href^="/shorts/"]),'
        'ytd-guide-entry-renderer:has('
        'a[href="/shorts"]),'
        'ytd-mini-guide-entry-renderer:has('
        'a[href^="/shorts/"]),'
        'ytd-mini-guide-entry-renderer:has('
        'a[href="/shorts"])',
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
        'youtube.com#?#ytd-guide-entry-renderer:has('
        'a[title="Shorts"]),'
        'ytd-mini-guide-entry-renderer:has('
        'a[title="Shorts"]),'
        'ytd-guide-entry-renderer:has('
        'a[aria-label="Shorts"]),'
        'ytd-mini-guide-entry-renderer:has('
        'a[aria-label="Shorts"])',
    ),
    (
        "YouTube desktop watch-next recommendations",
        "youtube.com##ytd-watch-next-secondary-results-renderer",
    ),
    (
        "YouTube desktop endscreen recommendations",
        "youtube.com##.ytp-endscreen-content",
    ),

    # ------------------------------------------------------------------
    # YouTube mobile
    # ------------------------------------------------------------------
    (
        "YouTube mobile root homepage rich grid",
        "m.youtube.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "ytm-rich-grid-renderer",
    ),
    (
        "YouTube mobile homepage Shorts shelves",
        "m.youtube.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "ytm-reel-shelf-renderer",
    ),
    (
        "YouTube mobile homepage Shorts lockups",
        "m.youtube.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "ytm-shorts-lockup-view-model",
    ),
    (
        "YouTube mobile what-to-watch feed",
        'm.youtube.com##ytm-browse['
        'tab-identifier="FEwhat_to_watch"] '
        "ytm-rich-grid-renderer,"
        'ytm-browse[browse-id="FEwhat_to_watch"] '
        "ytm-rich-grid-renderer",
    ),
    (
        "YouTube mobile Shorts navigation",
        'm.youtube.com#?#ytm-pivot-bar-item-renderer:has('
        'a[href*="/shorts"]),'
        'ytm-guide-entry-renderer:has('
        'a[href*="/shorts"])',
    ),
    (
        "YouTube mobile related recommendations",
        "m.youtube.com#?#ytm-item-section-renderer:"
        "has(ytm-compact-video-renderer)",
    ),
    (
        "YouTube mobile endscreen recommendations",
        "m.youtube.com##.ytp-endscreen-content",
    ),

    # ------------------------------------------------------------------
    # Instagram
    # ------------------------------------------------------------------
    #
    # Hide individual feed articles and discovery tiles, not the entire
    # <main> element. The search bar/dialog may be rendered inside <main>
    # in some Instagram layouts.
    #
    (
        "Instagram root homepage post articles",
        "instagram.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "main article",
    ),
    (
        "Instagram suggested post articles",
        "instagram.com#?#"
        "main section:has-text("
        "/(?:Suggested for you|Suggestions for you|For you|"
        "Önerilenler|Senin için(?: önerilenler)?)/i"
        ") article",
    ),
    (
        "Instagram suggested post links",
        "instagram.com#?#"
        "main section:has-text("
        "/(?:Suggested for you|Suggestions for you|For you|"
        "Önerilenler|Senin için(?: önerilenler)?)/i"
        ') a[href^="/p/"],'
        "main section:has-text("
        "/(?:Suggested for you|Suggestions for you|For you|"
        "Önerilenler|Senin için(?: önerilenler)?)/i"
        ') a[href^="/reel/"]',
    ),
    (
        "Instagram Explore post tiles",
        "instagram.com#?#"
        ":matches-path("
        "/^[/]explore(?:[/].*)?(?:[?].*)?$/"
        ") main "
        'a[href^="/p/"]',
    ),
    (
        "Instagram Explore reel tiles",
        "instagram.com#?#"
        ":matches-path("
        "/^[/]explore(?:[/].*)?(?:[?].*)?$/"
        ") main "
        'a[href^="/reel/"]',
    ),
    (
        "Instagram Explore recommendation images",
        "instagram.com#?#"
        ":matches-path("
        "/^[/]explore(?:[/].*)?(?:[?].*)?$/"
        ") main "
        'a[href^="/explore/"] img',
    ),
    (
        "Instagram Explore loading indicators",
        "instagram.com#?#"
        ":matches-path("
        "/^[/]explore(?:[/].*)?(?:[?].*)?$/"
        ") main "
        '[role="progressbar"]',
    ),
    (
        "Instagram root loading indicators",
        "instagram.com#?#"
        ":matches-path(/^[/](?:[?].*)?$/) "
        "main "
        '[role="progressbar"]',
    ),
    (
        "Instagram Reels navigation",
        'instagram.com##a[href="/reels/"]',
    ),
    (
        "Instagram Reels endless feed",
        "instagram.com#?#"
        ":matches-path("
        "/^[/]reels[/]?(?:[?].*)?$/"
        ") main",
    ),

    # ------------------------------------------------------------------
    # X / Twitter
    # ------------------------------------------------------------------
    #
    # Remove Home navigation and the passive /home primary column.
    # Search, profiles, direct posts, messages, notifications and composer
    # controls remain available.
    #
    (
        "X Home navigation button",
        'x.com##a[data-testid="AppTabBar_Home_Link"]',
    ),
    (
        "Twitter Home navigation button",
        'twitter.com##a[data-testid="AppTabBar_Home_Link"]',
    ),
    (
        "X Home primary column",
        "x.com#?#"
        ":matches-path(/^[/]home(?:[?].*)?$/) "
        'div[data-testid="primaryColumn"]',
    ),
    (
        "Twitter Home primary column",
        "twitter.com#?#"
        ":matches-path(/^[/]home(?:[?].*)?$/) "
        'div[data-testid="primaryColumn"]',
    ),
    (
        "X Home fallback main region",
        "x.com#?#"
        ":matches-path(/^[/]home(?:[?].*)?$/) "
        'main[role="main"]',
    ),
    (
        "Twitter Home fallback main region",
        "twitter.com#?#"
        ":matches-path(/^[/]home(?:[?].*)?$/) "
        'main[role="main"]',
    ),
    (
        "X Explore discovery content",
        "x.com#?#"
        ":matches-path("
        "/^[/]explore(?:[/].*)?(?:[?].*)?$/"
        ") main section:"
        'not(:has([data-testid="SearchBox_Search_Input"]))',
    ),
    (
        "Twitter Explore discovery content",
        "twitter.com#?#"
        ":matches-path("
        "/^[/]explore(?:[/].*)?(?:[?].*)?$/"
        ") main section:"
        'not(:has([data-testid="SearchBox_Search_Input"]))',
    ),
    (
        "X trends sidebar",
        "x.com#?#aside:has-text("
        "/(?:What’s happening|What's happening|Trends for you|"
        "Gündemdekiler|İlgini çekebilecek gündemler)/i"
        ")",
    ),
    (
        "Twitter trends sidebar",
        "twitter.com#?#aside:has-text("
        "/(?:What’s happening|What's happening|Trends for you|"
        "Gündemdekiler|İlgini çekebilecek gündemler)/i"
        ")",
    ),
    (
        "X who-to-follow sidebar",
        "x.com#?#aside:has-text("
        "/(?:Who to follow|Kimi takip etmeli)/i"
        ")",
    ),
    (
        "Twitter who-to-follow sidebar",
        "twitter.com#?#aside:has-text("
        "/(?:Who to follow|Kimi takip etmeli)/i"
        ")",
    ),
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


# Account/profile search results use a deliberately higher threshold than
# ordinary post/card rules. A normal account is not hidden merely because
# one of its posts is risky.
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
    """Return high-threshold patterns for clearly PMO-focused accounts.

    Account cards require either a direct explicit identity or multiple
    matching signal families. This is intentionally stricter than ordinary
    post/card filtering.
    """

    nsfw_identity = (
        r"(?:nsfw|18\+|adult\s+content|"
        r"yeti[şs]kin\s+i[cç]erik)"
    )

    return {
        "direct_identity": (
            alt(DIRECT),
        ),
        "sexualized_person": (
            alt(SEXUALIZED),
            alt(PEOPLE),
        ),
        "nudity_person": (
            alt(NUDITY),
            alt(PEOPLE),
        ),
        "leak_person": (
            alt(LEAK),
            alt(PEOPLE),
        ),
        "nsfw_media": (
            nsfw_identity,
            alt(MEDIA),
        ),
        "leak_person_media": (
            alt(LEAK),
            alt(PEOPLE),
            alt(MEDIA),
        ),
        "nudity_person_media": (
            alt(NUDITY),
            alt(PEOPLE),
            alt(MEDIA),
        ),
        "sexualized_person_media": (
            alt(SEXUALIZED),
            alt(PEOPLE),
            alt(MEDIA),
        ),
    }


def _content_rule(
    host: str,
    selector: str,
    patterns: tuple[str, ...],
    *,
    editorial: bool,
) -> str:
    """Build one procedural uBlock card/account filtering rule."""

    chain = selector

    for pattern in patterns:
        chain += f":has-text(/{pattern}/iu)"

    if editorial:
        chain += (
            f":not(:has-text(/{alt(EDITORIAL)}/iu))"
        )

    chain += (
        f":not(:has-text(/{build_safe_pattern()}/iu))"
    )

    return f"{host}#?#{chain}"


def build_social_search_query_rules() -> list[tuple[str, str]]:
    """Block strongly PMO-risky searches on supported social platforms.

    These rules inspect the search field value itself instead of relying
    only on result-card titles.

    They are generated into 25-social-content.txt, so they appear in:
    - temizweb-pmo.txt
    - temizweb-main.txt

    They do not appear in temizweb-social.txt.

    Recovery, legal-help, victim-support and educational queries remain
    allowed through the shared SAFE pattern.
    """

    families = build_pattern_families()
    safe = build_safe_pattern()
    rules: list[tuple[str, str]] = []

    search_inputs = {
        "youtube.com": (
            "input#search",
            'input[name="search_query"]',
            'input[aria-label="Search"]',
            'input[aria-label="Ara"]',
        ),
        "m.youtube.com": (
            "input#search",
            'input[name="search_query"]',
            "input.searchbox-input",
            'input[aria-label="Search"]',
            'input[aria-label="Ara"]',
        ),
        "instagram.com": (
            'input[placeholder="Search"]',
            'input[placeholder="Ara"]',
            'input[aria-label="Search input"]',
            'input[aria-label="Arama girişi"]',
            'input[aria-label="Search"]',
            'input[aria-label="Ara"]',
        ),
        "x.com": (
            'input[data-testid="SearchBox_Search_Input"]',
            'input[placeholder="Search"]',
            'input[placeholder="Ara"]',
            'input[aria-label="Search query"]',
            'input[aria-label="Arama sorgusu"]',
        ),
        "twitter.com": (
            'input[data-testid="SearchBox_Search_Input"]',
            'input[placeholder="Search"]',
            'input[placeholder="Ara"]',
            'input[aria-label="Search query"]',
            'input[aria-label="Arama sorgusu"]',
        ),
    }

    for host, selectors in search_inputs.items():
        for selector in selectors:
            for family_name, patterns in families.items():
                chain = (
                    f"{selector}:watch-attr(value)"
                )

                for pattern in patterns:
                    chain += (
                        f":matches-attr(value=/{pattern}/iu)"
                    )

                chain += (
                    f":not(:matches-attr(value=/{safe}/iu))"
                )

                chain += (
                    ":upward(html) > body"
                )

                rules.append(
                    (
                        (
                            f"{host} / search query / "
                            f"{family_name}"
                        ),
                        f"{host}#?#{chain}",
                    )
                )

    return rules


def generate_social_layers(
    addiction_output: Path = ADDICTION_OUTPUT,
    content_output: Path = CONTENT_OUTPUT,
) -> tuple[Path, Path]:
    """Generate social anti-addiction and social PMO layers."""

    addiction_lines = [
        (
            "! "
            "============================================================================="
        ),
        (
            "! TemizWeb — "
            "INTENTIONAL SOCIAL MEDIA MODE"
        ),
        (
            "! GENERATED FILE — "
            "edit scripts/generate_social.py instead."
        ),
        (
            "! Preserves search, profiles, messages, direct content, "
            "composing, uploads"
        ),
        (
            "! and publishing. Removes passive feeds and "
            "algorithmic discovery."
        ),
        (
            "! "
            "============================================================================="
        ),
        "",
    ]

    for index, (label, rule) in enumerate(
        ADDICTION_RULES,
        1,
    ):
        addiction_lines.extend(
            (
                f"! Rule {index}: {label}",
                rule,
                "",
            )
        )

    families = build_pattern_families()

    content_lines = [
        (
            "! "
            "============================================================================="
        ),
        (
            "! TemizWeb — "
            "SOCIAL PMO CONTENT FILTER"
        ),
        (
            "! GENERATED FILE — "
            "edit scripts/generate_social.py instead."
        ),
        (
            "! Filters strong PMO search queries and the smallest "
            "matching post/video card."
        ),
        (
            "! Account cards use a separate, much higher "
            "identity threshold."
        ),
        (
            "! Recovery, legal help, education, composing, "
            "uploads and publishing remain."
        ),
        (
            "! "
            "============================================================================="
        ),
        "",
    ]

    count = 0

    # ------------------------------------------------------------------
    # Strong social-media search-query filtering
    # ------------------------------------------------------------------
    #
    # These rules are written to the PMO content layer, not to the
    # anti-addiction-only layer.
    #
    social_search_rules = (
        build_social_search_query_rules()
    )

    for label, rule in social_search_rules:
        count += 1

        content_lines.extend(
            (
                (
                    f"! Rule {count}: "
                    f"Social search:{label}"
                ),
                rule,
                "",
            )
        )

    # ------------------------------------------------------------------
    # Individual post/video/card filtering
    # ------------------------------------------------------------------
    for host, selectors in SOCIAL_TARGETS.items():
        for selector in selectors:
            for family_name, patterns in families.items():
                count += 1

                content_lines.extend(
                    (
                        (
                            f"! Rule {count}: "
                            f"{host} / {selector} / "
                            f"post:{family_name}"
                        ),
                        _content_rule(
                            host,
                            selector,
                            patterns,
                            editorial=(
                                family_name
                                == "leak_person"
                            ),
                        ),
                        "",
                    )
                )

    # ------------------------------------------------------------------
    # Strong explicit account-identity filtering
    # ------------------------------------------------------------------
    account_families = (
        build_account_identity_families()
    )

    for host, selectors in ACCOUNT_TARGETS.items():
        for selector in selectors:
            for (
                family_name,
                patterns,
            ) in account_families.items():
                count += 1

                content_lines.extend(
                    (
                        (
                            f"! Rule {count}: "
                            f"{host} / {selector} / "
                            f"account:{family_name}"
                        ),
                        _content_rule(
                            host,
                            selector,
                            patterns,
                            editorial=False,
                        ),
                        "",
                    )
                )

    addiction_output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    addiction_output.write_text(
        "\n".join(addiction_lines),
        encoding="utf-8",
    )

    content_output.write_text(
        "\n".join(content_lines),
        encoding="utf-8",
    )

    print(
        "Generated social anti-addiction layer: "
        f"{addiction_output.relative_to(ROOT)} "
        f"({len(ADDICTION_RULES)} rules)"
    )

    print(
        "Generated social PMO content layer: "
        f"{content_output.relative_to(ROOT)} "
        f"({count} rules)"
    )

    return addiction_output, content_output


if __name__ == "__main__":
    generate_social_layers()
