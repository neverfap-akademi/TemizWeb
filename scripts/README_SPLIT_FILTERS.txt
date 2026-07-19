TemizWeb split-filter update
============================

This update preserves the existing combined output exactly and additionally writes:

- filters/dist/temizweb-pmo.txt
- filters/dist/temizweb-social.txt
- filters/dist/temizweb-main.txt (unchanged combined behavior)

Separation policy
-----------------

PMO list:
- Existing PMO filtering on search engines and ordinary sites
- Strict page filtering
- Generic card/article filtering with recovery exceptions
- PMO filtering of individual social posts, videos, Shorts and strong explicit account identities
- HaGeZi NSFW upstream domain rules

Social anti-addiction list:
- Existing YouTube interface layer (10-youtube.txt)
- Generated intentional-use social layer (15-social-addiction.txt)
- No PMO keyword/card rules
- No HaGeZi NSFW upstream rules

The checker verifies that:
- Main still contains both layers
- PMO and social lists contain no duplicate active rules
- Neither list contains the other layer's generated marker
- PMO + social active rules exactly cover the combined main list
- Every split rule already exists in main

Run:
python scripts/build_all.py --fixture-dir tests/fixtures
python scripts/check_all.py
