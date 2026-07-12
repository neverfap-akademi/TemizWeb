# TemizWeb Revision 4

This patch replaces:

- `filters/src/20-social.txt`
- `filters/src/30-search.txt`
- `filters/src/40-generic-content.txt`

Key changes:

- Generic procedural rules use `*##` specific-generic syntax.
- Search Mode 1 uses the same payload for Google, Bing, DuckDuckGo, Brave, Yandex and Yahoo.
- Recovery/legal exceptions use strong phrases rather than broad single words.
- Turkish Unicode boundaries and ASCII spellings are supported.
- Person + leak matching requires a media signal, while narrow explicit phrases remain aggressive.
- Added AI nudification, cam, leak, download, live, text-erotica and spelling variants.
- Direct high-confidence pages also hide `[role="main"]` and `iframe` while preserving navigation.

Before release, validate selectors and performance on Android Firefox/uBlock Origin.
