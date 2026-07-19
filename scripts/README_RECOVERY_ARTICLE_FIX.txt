TemizWeb scripts v5 — recovery article protection

Problem fixed:
The strict-page layer correctly allowed NeverFap/PMO recovery pages, but the
older 40-generic-content.txt layer could still hide the <article> or
[role="article"] element itself.

How v5 works:
- generate_strict_page.py exposes one shared high-confidence SAFE pattern.
- build_all.py adds that SAFE pattern as an extra :not(:has-text(...)) guard
  to active procedural rules from 40-generic-content.txt while merging.
- The source 40-generic-content.txt file is not rewritten.
- check_all.py confirms merged generic rules contain the recovery override.

This protects article bodies containing NeverFap, NoFap, PMO recovery,
porn addiction, pornoyu bırakmak, pornodan kurtulmak, treatment/help/legal
contexts, while preserving the existing risk rules.
