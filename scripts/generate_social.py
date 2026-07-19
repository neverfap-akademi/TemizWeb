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
    # YouTube desktop: homepage and algorithmic feeds.
    ("YouTube desktop homepage feed", "youtube.com##ytd-browse[page-subtype=\"home\"] ytd-rich-grid-renderer"),
    ("YouTube desktop what-to-watch feed", "youtube.com##ytd-browse[browse-id=\"FEwhat_to_watch\"] ytd-rich-grid-renderer"),
    ("YouTube desktop Shorts navigation", "youtube.com##ytd-guide-entry-renderer:has(a[href^=\"/shorts\"]),ytd-mini-guide-entry-renderer:has(a[href^=\"/shorts\"])"),
    ("YouTube desktop homepage Shorts shelves", "youtube.com##ytd-browse[page-subtype=\"home\"] ytd-reel-shelf-renderer,ytd-browse[page-subtype=\"home\"] ytd-rich-section-renderer:has(a[href^=\"/shorts/\"] )"),
    ("YouTube desktop subscriptions Shorts shelves", "youtube.com##ytd-browse[browse-id=\"FEsubscriptions\"] ytd-reel-shelf-renderer,ytd-browse[browse-id=\"FEsubscriptions\"] ytd-rich-section-renderer:has(a[href^=\"/shorts/\"] )"),
    ("YouTube desktop watch-next recommendations", "youtube.com##ytd-watch-next-secondary-results-renderer"),
    ("YouTube desktop endscreen recommendations", "youtube.com##.ytp-endscreen-content"),

    # YouTube mobile. Search/channel Shorts are not globally hidden.
    ("YouTube mobile homepage feed", "m.youtube.com##ytm-browse[tab-identifier=\"FEwhat_to_watch\"] ytm-rich-grid-renderer,ytm-browse[browse-id=\"FEwhat_to_watch\"] ytm-rich-grid-renderer"),
    ("YouTube mobile Shorts navigation", "m.youtube.com##ytm-pivot-bar-item-renderer:has(a[href*=\"/shorts\"]),ytm-guide-entry-renderer:has(a[href*=\"/shorts\"] )"),
    ("YouTube mobile homepage Shorts shelves", "m.youtube.com##ytm-browse[tab-identifier=\"FEwhat_to_watch\"] ytm-reel-shelf-renderer,ytm-browse[browse-id=\"FEwhat_to_watch\"] ytm-reel-shelf-renderer"),
    ("YouTube mobile subscriptions Shorts shelves", "m.youtube.com##ytm-browse[browse-id=\"FEsubscriptions\"] ytm-reel-shelf-renderer"),
    ("YouTube mobile related recommendations", "m.youtube.com##ytm-item-section-renderer:has(ytm-compact-video-renderer)"),
    ("YouTube mobile endscreen recommendations", "m.youtube.com##.ytp-endscreen-content"),

    # Instagram: preserve search/profile/direct content/create/messages.
    # Only feed items/stories are hidden on the root homepage.
    ("Instagram homepage posts", "instagram.com##article:matches-path(/^\\/(?:\\?.*)?$/)"),
    ("Instagram homepage story tray", "instagram.com##main section:matches-path(/^\\/(?:\\?.*)?$/):has(canvas)"),
    ("Instagram homepage suggested modules", "instagram.com##main section:matches-path(/^\\/(?:\\?.*)?$/):has-text(/(?:Suggested for you|Suggestions for you|For you|Önerilenler|Senin için)/i)"),
    # Keep the Search/Explore button, remove discovery grid itself.
    ("Instagram Explore discovery grid", "instagram.com##main section:matches-path(/^\\/explore\\/?(?:\\?.*)?$/)"),
    ("Instagram Reels navigation", "instagram.com##a[href=\"/reels/\"]"),
    ("Instagram Reels endless feed", "instagram.com##main:matches-path(/^\\/reels\\/?(?:\\?.*)?$/)"),

    # X/Twitter: preserve compose box, search, profiles, direct threads,
    # messages, notifications, bookmarks, lists and production controls.
    # Only tweet cards on /home are removed.
    ("X home timeline tweets", "x.com##article[data-testid=\"tweet\"]:matches-path(/^\\/home(?:\\?.*)?$/)"),
    ("Twitter home timeline tweets", "twitter.com##article[data-testid=\"tweet\"]:matches-path(/^\\/home(?:\\?.*)?$/)"),
    ("X home timeline cells", "x.com##div[data-testid=\"cellInnerDiv\"]:matches-path(/^\\/home(?:\\?.*)?$/):has(article[data-testid=\"tweet\"])"),
    ("Twitter home timeline cells", "twitter.com##div[data-testid=\"cellInnerDiv\"]:matches-path(/^\\/home(?:\\?.*)?$/):has(article[data-testid=\"tweet\"])"),
    ("X Explore discovery content", "x.com##main section:matches-path(/^\\/explore(?:\\/.*)?(?:\\?.*)?$/):not(:has([data-testid=\"SearchBox_Search_Input\"]))"),
    ("Twitter Explore discovery content", "twitter.com##main section:matches-path(/^\\/explore(?:\\/.*)?(?:\\?.*)?$/):not(:has([data-testid=\"SearchBox_Search_Input\"]))"),
    ("X trends sidebar", "x.com##aside:has-text(/(?:What’s happening|What's happening|Trends for you|Gündemdekiler|İlgini çekebilecek gündemler)/i)"),
    ("Twitter trends sidebar", "twitter.com##aside:has-text(/(?:What’s happening|What's happening|Trends for you|Gündemdekiler|İlgini çekebilecek gündemler)/i)"),
    ("X who-to-follow sidebar", "x.com##aside:has-text(/(?:Who to follow|Kimi takip etmeli)/i)"),
    ("Twitter who-to-follow sidebar", "twitter.com##aside:has-text(/(?:Who to follow|Kimi takip etmeli)/i)"),
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
    return {
        "direct_identity": (alt(DIRECT),),
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
