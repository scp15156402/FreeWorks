import FreeCADGui as Gui, FreeCAD as App, time
from PySide import QtCore, QtGui, QtWidgets
from freeworks import naming, widgets
L=open('/tmp/env.log','w')
def shot(n): QtGui.QGuiApplication.primaryScreen().grabWindow(0).save('/tmp/e_%s.png'%n); L.write('shot %s\n'%n); L.flush()
def s1():
    try:
        d=naming.new_document("assembly"); L.write('asm objs %s\n'%[o.TypeId for o in d.Objects]); L.flush()
    except Exception as e: L.write('asm err %s\n'%e)
def s2():
    try:
        d=naming.new_document("drawing"); L.write('drw objs %s\n'%[o.TypeId for o in d.Objects]); L.flush()
    except Exception as e: L.write('drw err %s\n'%e)
def s3():
    d=widgets.NewDocumentDialog(welcome=True); d.show(); globals()['_d']=d
QtCore.QTimer.singleShot(100, s1); QtCore.QTimer.singleShot(3500, lambda: shot('asm'))
QtCore.QTimer.singleShot(4000, s2); QtCore.QTimer.singleShot(8000, lambda: shot('drw'))
QtCore.QTimer.singleShot(8500, s3); QtCore.QTimer.singleShot(9500, lambda: shot('welcome'))
