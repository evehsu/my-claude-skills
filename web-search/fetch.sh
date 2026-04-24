#!/usr/bin/env bash
# Usage: fetch.sh <url> <output_path_without_extension>
# HEAD-probes the URL to detect content-type, then downloads the raw bytes
# to <output_path_without_extension>.<html|pdf>. Prints the final filename
# on success, exits non-zero on failure.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <url> <output_path_without_extension>" >&2
  exit 2
fi

URL="$1"
OUT_BASE="$2"
UA="Mozilla/5.0 (compatible; claude-skill-web-search/1.0)"

CT=$(curl -sIL -A "$UA" --max-time 20 "$URL" \
  | awk -F': *' 'tolower($1)=="content-type" {print tolower($2)}' \
  | tail -n1)

case "$CT" in
  *pdf*) EXT="pdf" ;;
  *)     EXT="html" ;;
esac

curl -sSL -A "$UA" --max-time 60 -o "${OUT_BASE}.${EXT}" "$URL"
echo "${OUT_BASE}.${EXT}"
