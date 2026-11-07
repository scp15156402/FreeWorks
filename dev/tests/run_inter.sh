#!/bin/bash
# interactive test: Xvfb :77, FreeCAD + driver
pkill -f "Xvfb :77" 2>/dev/null; sleep 0.5
Xvfb :77 -screen 0 1700x1000x24 >/dev/null 2>&1 & XP=$!
sleep 1
export DISPLAY=:77 FREECAD_USER_HOME=/home/claude/fwhome LANG=C.UTF-8 FREEWORKS_NO_WELCOME=1
export T0=$(python3 -c "import time;print(time.time())")
SHOT=/tmp/i_end.png PRE=/tmp/pre_inter.py DELAY=9000 POST=30000 timeout 80 /home/claude/fc/squashfs-root/AppRun /tmp/shot.py >/tmp/fc_inter.out 2>&1 &
python3 /tmp/drive.py :77 $T0
wait %2 2>/dev/null; sleep 1; kill $XP 2>/dev/null
