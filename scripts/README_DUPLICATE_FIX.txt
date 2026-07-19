TemizWeb v7.1 duplicate-rule fix

The new generated social layers may overlap with older handwritten rules still
present in filters/src/10-ui.txt or filters/src/20-social.txt. build_all.py now
removes duplicate active uBlock rules after merging while preserving comments,
order, attribution, and the first occurrence of every rule.
