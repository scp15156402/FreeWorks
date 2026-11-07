#!/bin/bash
# Download and extract the FreeCAD Linux AppImage used for headless testing.
#   dev/fetch_freecad.sh            -> version pinned in versions.json
#   dev/fetch_freecad.sh 1.2.0      -> a specific version (e.g. to test an upgrade)
# Result: dev/.freecad/<version>/squashfs-root/AppRun, and dev/.freecad/current -> <version>
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PINNED=$(python3 -c "import json;print(json.load(open('$ROOT/versions.json'))['freecad']['version'])")
NAME_PINNED=$(python3 -c "import json;print(json.load(open('$ROOT/versions.json'))['freecad']['linux_appimage'])")
VER="${1:-$PINNED}"
NAME="${NAME_PINNED//$PINNED/$VER}"
DEST="$ROOT/dev/.freecad/$VER"
if [ -x "$DEST/squashfs-root/AppRun" ]; then
  echo "FreeCAD $VER already present: $DEST/squashfs-root/AppRun"
else
  mkdir -p "$DEST"
  echo "Downloading $NAME ..."
  curl -fSL --retry 3 -o "$DEST/fc.AppImage" "https://github.com/FreeCAD/FreeCAD/releases/download/$VER/$NAME"
  chmod +x "$DEST/fc.AppImage"
  (cd "$DEST" && ./fc.AppImage --appimage-extract >/dev/null && rm -f fc.AppImage)
  echo "Extracted: $DEST/squashfs-root/AppRun"
fi
ln -sfn "$VER" "$ROOT/dev/.freecad/current"
