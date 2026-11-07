#!/bin/bash
export FREEWORKS_TESTS="$(cd "$(dirname "$0")" && pwd)"
# usage: run_fc.sh <macro.py> [timeout]   (runs stock FreeCAD + FreeWorks only)
export FREECAD_USER_HOME=${FCHOME:-/tmp/freeworks-profile}
export LANG=C.UTF-8
timeout ${2:-150} xvfb-run -a -s "-screen 0 1700x1000x24" ${FREECAD_APPRUN:-$(cd "$(dirname "$0")/../../.." && pwd)/dev/.freecad/current/squashfs-root/AppRun} "$1" 2>&1 | grep -v -E 'locale|UTF-8|reconfigure|manual$|^for more'
