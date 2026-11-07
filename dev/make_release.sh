#!/bin/bash
# Build dist/FreeWorks.zip for a GitHub release (run from the repository root).
set -e
VER=$(sed -n 's:.*<version>\(.*\)</version>.*:\1:p' Mod/FreeWorks/package.xml)
grep -q "__version__ = \"$VER\"" Mod/FreeWorks/freeworks/__init__.py || { echo "version mismatch: package.xml=$VER vs __init__.py"; exit 1; }
rm -rf dist && mkdir -p dist/FreeWorks
git archive HEAD Install.cmd Update.cmd install.ps1 uninstall.ps1 get.ps1 versions.json README.md CHANGELOG.md LICENSE branding Mod docs/assets/logo.png | tar -x -C dist/FreeWorks
(cd dist && zip -qr FreeWorks.zip FreeWorks && rm -rf FreeWorks)
echo "dist/FreeWorks.zip  (v$VER) - attach it to the GitHub release v$VER"
