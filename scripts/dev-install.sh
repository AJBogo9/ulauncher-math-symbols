#!/usr/bin/env bash
# symlink this repo into ulauncher's extensions dir, so edits load on the next restart
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
dest="${XDG_DATA_HOME:-$HOME/.local/share}/ulauncher/extensions/math-symbols"

if [ -e "$dest" ] && [ ! -L "$dest" ]; then
  echo "$dest exists and is not a symlink, leaving it alone" >&2
  exit 1
fi
mkdir -p "$(dirname "$dest")"
ln -sfn "$repo" "$dest"
echo "linked $dest -> $repo"
echo "restart ulauncher to load it: pkill ulauncher; ulauncher start -v"
