#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
f=ROOT/'filters/dist/temizweb-main.txt'
if not f.exists(): errors.append('missing filters/dist/temizweb-main.txt')
else:
 t=f.read_text(encoding='utf-8');
 for h in ('! Title:','! Version:','! License:','! Expires:'):
  if h not in t: errors.append('missing '+h)
 active=[x.strip() for x in t.splitlines() if x.strip() and not x.lstrip().startswith('!')]
 if len(active)!=len(set(active)): errors.append('duplicate uBlock rules')
 if len(active)<20: errors.append('too few uBlock rules')
for p in sorted((ROOT/'dns/dist').glob('*-domains.txt')):
 ds=[x.strip() for x in p.read_text(encoding='utf-8').splitlines() if x.strip() and not x.startswith('#')]
 if ds!=sorted(set(ds)): errors.append(p.name+' not sorted/unique')
if not list((ROOT/'dns/dist').glob('*-domains.txt')): errors.append('missing DNS outputs')
if errors: print('\n'.join(errors),file=sys.stderr); raise SystemExit(1)
print('All generated outputs passed validation')
