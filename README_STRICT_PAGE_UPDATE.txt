TemizWeb social-media update
============================

Generated files:
- filters/src/15-social-addiction.txt
- filters/src/25-social-content.txt

Behavior:
- YouTube: removes homepage/recommendation feeds and Shorts discovery shelves,
  while preserving searched Shorts, channel Shorts, direct Shorts, uploads,
  publishing and YouTube Studio.
- Instagram: removes the homepage feed, Explore recommendation grid and Reels
  discovery feed while preserving Search, profiles, direct posts, messages,
  Create/upload and publishing controls.
- X/Twitter: removes tweets from /home and discovery/sidebar recommendation
  surfaces while preserving search, profiles, direct threads, lists, bookmarks,
  notifications, messages, composing, media upload and publishing.
- All three: risky PMO cards/posts/videos are filtered with the shared strict
  language engine; recovery, legal-help, victim-support and educational content
  is protected.

Run:
  python scripts/build_all.py --fixture-dir tests/fixtures
  python scripts/check_all.py
