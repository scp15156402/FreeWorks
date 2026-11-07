#!/bin/bash
export FREEWORKS_TESTS="$(cd "$(dirname "$0")" && pwd)"
# interactive test: Xvfb :77, FreeCAD + driver
pkill -f "Xvfb :77" 2>/dev/null; sleep 0.5
Xvfb :77 -screen 0 1700x1000x24 >/dev/null 2>&1 & XP=$!
sleep 1
export DISPLAY=:77 FREECAD_USER_HOME=${FCHOME:-/tmp/freeworks-profile} LANG=C.UTF-8 FREEWORKS_NO_WELCOME=1
export T0=$(python3 -c "import time;print(time.time())")
SHOT=/tmp/i_end.png PRE="$(dirname "$0")/pre_inter.py" DELAY=9000 POST=30000 timeout 80 ${FREECAD_APPRUN:-$(cd "$(dirname "$0")/../../.." && pwd)/dev/.freecad/current/squashfs-root/AppRun} "$(dirname "$0")/shot.py" >/tmp/fc_inter.out 2>&1 &
python3 "$(dirname "$0")/drive.py" :77 $T0
wait %2 2>/dev/null; sleep 1; kill $XP 2>/dev/null
