#!/bin/bash
# usage: run_fc.sh <macro.py> [timeout]   (runs stock FreeCAD + FreeWorks only)
export FREECAD_USER_HOME=${FCHOME:-/home/claude/fchome}
export LANG=C.UTF-8
timeout ${2:-150} xvfb-run -a -s "-screen 0 1700x1000x24" /home/claude/fc/squashfs-root/AppRun "$1" 2>&1 | grep -v -E 'locale|UTF-8|reconfigure|manual$|^for more'
