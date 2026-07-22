# Safari cosmetic-exception fix

This patch changes only Safari custom-filter generation and validation.

- Normal Chrome/Firefox `temizweb-main.txt`, `temizweb-pmo.txt`, and `temizweb-social.txt` are unchanged.
- `#@#` cosmetic exceptions are resolved during Safari generation.
- Matching broad hide rules are omitted from Safari output.
- Narrow homepage/feed rules remain.
- Fixes Instagram Explore/search restoration in Main mode.
- Fixes YouTube channel Shorts restoration in Main and Social modes.
