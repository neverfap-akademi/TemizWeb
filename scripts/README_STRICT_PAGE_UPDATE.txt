TemizWeb scripts update
=======================

Files:
- build_all.py
- check_all.py
- generate_strict_page.py

Installation:
1. In the GitHub repository, open the scripts folder.
2. Replace the existing build_all.py and check_all.py.
3. Add/replace generate_strict_page.py.
4. Commit all three files together.
5. Run the existing Build TemizWeb GitHub Action.

The builder automatically generates:
filters/src/35-strict-page.txt

Validated locally with:
python3 -m py_compile scripts/*.py
python3 scripts/build_all.py --fixture-dir tests/fixtures
python3 scripts/check_all.py

Expected generated strict-page output:
- 267 hostname-targeted focused rules
- shared Turkish/English risk engine
- targeted coverage for Google, Nitter, OK.ru, stock-image sites and others
- news/legal/recovery exceptions
