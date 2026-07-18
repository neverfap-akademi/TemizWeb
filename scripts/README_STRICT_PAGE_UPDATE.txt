TemizWeb strict-page v4

Why v3 compiled but did not work in Firefox/uBlock Origin:
- v3 generated individual cosmetic rules around 57,000–61,000 characters long.
- Python and CI accepted them, but uBlock could discard such oversized rules.
- v3 also nested procedural selectors inside :has(), which is fragile.

v4 changes:
- Forces procedural handling with #?#.
- Starts from the actual title/heading/search field and climbs with :upward(html).
- Uses chained token checks instead of giant combination regexes.
- Keeps each generated rule under 12,000 characters (currently about 2,700 max).
- Keeps recovery, NeverFap/NoFap, legal/help and linguistic exceptions.

Replace these files in the repository scripts folder, then run:
python scripts/build_all.py --fixture-dir tests/fixtures
python scripts/check_all.py

After GitHub Actions updates filters/dist/temizweb-main.txt, in Firefox/uBlock:
1. Dashboard > Filter lists.
2. Purge all caches / update the TemizWeb list.
3. Verify the TemizWeb subscription shows a recent timestamp.
4. Reload test pages with cache bypass.
