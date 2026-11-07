#!/bin/bash
# FreeWorks automated tests (Linux, headless). Exit code 0 = all passed.
#   dev/run_tests.sh                 # FreeCAD pinned in versions.json (downloaded on first run)
#   FREECAD_APPRUN=/path/AppRun dev/run_tests.sh
# Needs: python3, xvfb-run, curl. Output: dev/tests/out/ (results.json, report.md, screenshots)
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dev/tests/out"
rm -rf "$OUT"; mkdir -p "$OUT"
FAIL=0

echo "== static checks"
python3 "$ROOT/dev/tests/pscheck.py" "$ROOT/get.ps1" "$ROOT/install.ps1" "$ROOT/uninstall.ps1" || FAIL=1
python3 - "$ROOT" <<'EOF' || FAIL=1
import ast, glob, sys, json
root = sys.argv[1]
bad = []
for f in glob.glob(root + "/Mod/FreeWorks/**/*.py", recursive=True) + glob.glob(root + "/dev/**/*.py", recursive=True) + glob.glob(root + "/tools/*.py"):
    try:
        ast.parse(open(f, encoding="utf-8").read(), f)
    except SyntaxError as e:
        bad.append("%s: %s" % (f, e))
json.load(open(root + "/versions.json"))
v = {open(root + "/Mod/FreeWorks/package.xml").read().split("<version>")[1].split("<")[0],
     open(root + "/Mod/FreeWorks/freeworks/__init__.py").read().split('__version__ = "')[1].split('"')[0],
     json.load(open(root + "/versions.json"))["freeworks"]}
if len(v) != 1:
    bad.append("version mismatch: %s" % v)
print("python syntax + versions:", "OK" if not bad else bad)
sys.exit(1 if bad else 0)
EOF

APPRUN="${FREECAD_APPRUN:-$ROOT/dev/.freecad/current/squashfs-root/AppRun}"
if [ ! -x "$APPRUN" ]; then "$ROOT/dev/fetch_freecad.sh" || exit 2; APPRUN="$ROOT/dev/.freecad/current/squashfs-root/AppRun"; fi

echo "== FreeCAD GUI suite"
PROFILE="$(mktemp -d)"
mkdir -p "$PROFILE/Mod"
cp -r "$ROOT/Mod/FreeWorks" "$PROFILE/Mod/"
cp "$ROOT/CHANGELOG.md" "$PROFILE/"
export FREECAD_USER_HOME="$PROFILE" FREEWORKS_NO_WELCOME=1 FREEWORKS_DEBUG_LOG="$OUT/freeworks.log" FREEWORKS_TEST_OUT="$OUT" LANG=C.UTF-8
timeout 300 xvfb-run -a -s "-screen 0 1700x1000x24" "$APPRUN" "$ROOT/dev/tests/suite.py" > "$OUT/freecad.out" 2>&1
rm -rf "$PROFILE"

python3 - "$OUT" <<'EOF' || FAIL=1
import json, sys, os
out = sys.argv[1]
p = os.path.join(out, "results.json")
if not os.path.exists(p):
    print("suite did not finish - see", os.path.join(out, "freecad.out")); sys.exit(1)
d = json.load(open(p))
lines = ["# FreeWorks test report", "", "FreeCAD %s - %d passed, %d failed" % (d["freecad"], d["passed"], d["failed"]), "",
         "| | Test | Detail |", "|---|---|---|"]
for r in d["results"]:
    lines.append("| %s | %s | %s |" % ("PASS" if r["ok"] else "**FAIL**", r["test"], r["detail"].replace("|", "/").replace("\n", " ")[:160]))
open(os.path.join(out, "report.md"), "w").write("\n".join(lines) + "\n")
for r in d["results"]:
    print("%s  %s  %s" % ("PASS" if r["ok"] else "FAIL", r["test"], "" if r["ok"] else r["detail"][:200]))
print("\n%d passed, %d failed  (report: dev/tests/out/report.md)" % (d["passed"], d["failed"]))
sys.exit(1 if d["failed"] else 0)
EOF
exit $FAIL
