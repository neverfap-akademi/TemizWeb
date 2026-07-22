# Safari short-rule compatibility fix

This patch affects only Safari custom-filter generation.

- Splits oversized generated `:has-text()` regexes structurally.
- Adds compact equivalents for leak/person/media, sexual descriptors, hidden camera/voyeur, AI undressing, live-cam, and suggestive-media families.
- Preserves the original rule suffix, including legal, victim-support, Neverfap, recovery, and addiction exceptions.
- Keeps existing compile-time `#@#` exception handling for Instagram search and channel Shorts.
- Does not modify normal Chrome/Firefox outputs.
