import FreeCADGui as Gui, FreeCAD as App, os
from PySide import QtCore, QtGui
OUT=os.environ.get('SHOT','/tmp/shot.png'); DELAY=int(os.environ.get('DELAY','8000'))
def snap():
    try:
        pre=os.environ.get('PRE')
        if pre: exec(open(pre).read(), {'Gui':Gui,'App':App,'QtCore':QtCore,'QtGui':QtGui})
    except Exception:
        import traceback; traceback.print_exc()
    QtCore.QTimer.singleShot(int(os.environ.get('POST','4000')), fin)
def fin():
    QtGui.QApplication.processEvents()
    Gui.getMainWindow().grab().save(OUT); App.Console.PrintMessage("SNAP OK\n")
    QtGui.QApplication.quit()
def start():
    Gui.getMainWindow().resize(1700,1000); QtCore.QTimer.singleShot(DELAY, snap)
QtCore.QTimer.singleShot(100, start)
