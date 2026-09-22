#!/usr/bin/env bash
# 결제(구독) 기능 다시 켜기: config/billing.json → enabled:true, package.json 에 RevenueCat 플러그인 복원
# 사용: bash tools/enable_billing.sh   (끄기: bash tools/enable_billing.sh off)
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - "$@" <<'PY'
import json,sys
on = not (len(sys.argv)>1 and sys.argv[1]=='off')
cfg=json.load(open('config/billing.json',encoding='utf-8')); cfg['enabled']=on
json.dump(cfg,open('config/billing.json','w',encoding='utf-8'),ensure_ascii=False,indent=2); open('config/billing.json','a').write('\n')
pkg=json.load(open('package.json',encoding='utf-8')); deps=pkg.setdefault('dependencies',{})
if on: deps[cfg['plugin']]=cfg['plugin_version']
else: deps.pop(cfg['plugin'],None)
if not deps: pkg.pop('dependencies')
json.dump(pkg,open('package.json','w',encoding='utf-8'),ensure_ascii=False,indent=2); open('package.json','a').write('\n')
print('billing', 'ON' if on else 'OFF', '| deps:', pkg.get('dependencies'))
PY
