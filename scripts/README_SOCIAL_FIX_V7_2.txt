TemizWeb scripts v7.2 — social UI fixes

Changes:
- X/Twitter: hides the Home tab strip itself on /home, then hides timeline cards.
  Composer/upload/publish controls are not selected.
- YouTube: homepage feed is now path-scoped instead of depending only on
  page-subtype attributes.
- YouTube: explicit cosmetic exceptions disable older global Shorts rules,
  allowing searched Shorts and channel Shorts; scoped homepage/subscription
  shelf rules remain.
- Instagram: explicit cosmetic exceptions restore the Explore/Search link.
- Instagram: Explore filtering now targets recommendation post/reel tiles,
  not the whole section that contains the search UI.

After rebuilding, force-update TemizWeb in uBlock Origin and reload pages.
