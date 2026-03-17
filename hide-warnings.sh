#!/usr/bin/env bash
# hide-warnings.sh — remove the warnings notification from the generated index.html
# Usage: ./hide-warnings.sh [path/to/index.html]

set -euo pipefail
HTML="${1:-index.html}"
[[ -f "$HTML" ]] || { echo "Error: '$HTML' not found." >&2; exit 1; }

python3 - "$HTML" << 'PYEOF'
import sys, re
path = sys.argv[1]
content = open(path).read()
# Strip any previous patch
content = re.sub(r'<script data-bpw>[^<]*</script>', '', content)
# Minimal one-liner to remove the notification element and its variants
snippet = '<script data-bpw>const r=()=>document.querySelectorAll(".page__aside-element_for_notification, .notification, .document-warnings").forEach(e=>e.remove());r();new MutationObserver(r).observe(document.documentElement,{childList:true,subtree:true});</script>'
content = content.replace('</body>', snippet + '</body>', 1)
open(path, 'w').write(content)
print('Patched:', path)
PYEOF
