#!/usr/bin/env bash
set -euo pipefail

ROOT="."
GEOMETRY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --geometry)
      GEOMETRY="--geometry"
      shift
      ;;
    --root)
      ROOT="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

cd "$ROOT"
python -m asf.full_loop --root . $GEOMETRY
