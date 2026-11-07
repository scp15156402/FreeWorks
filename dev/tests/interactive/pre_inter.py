import os
import FreeCADGui as Gui, FreeCAD as App, time, os
from PySide import QtWidgets, QtCore, QtGui
exec(open(os.path.join(os.environ['FREEWORKS_TESTS'], 'model.py')).read())
L=open('/tmp/inter.log','w'); T0=float(os.environ['T0'])
from freeworks import context
def log(msg):
    L.write('%5.1f %s\n'%(time.time()-T0, msg)); L.flush()
def state():
    try:
        v=Gui.activeView(); rot=v.getCameraOrientation() if hasattr(v,'getCameraOrientation') else None
        pops=[w.metaObject().className()+':'+w.objectName() for w in QtWidgets.QApplication.topLevelWidgets() if w.isVisible() and w is not Gui.getMainWindow()]
        log('ctx=%s rot=%s dlg=%s pops=%s focus=%s' % (context.current(), [round(x,2) for x in rot.Q] if rot else None, bool(Gui.Control.activeDialog()), pops, QtWidgets.QApplication.focusWidget().metaObject().className() if QtWidgets.QApplication.focusWidget() else None))
    except Exception as e: log('err %s'%e)
t=QtCore.QTimer(); t.timeout.connect(state); t.start(1000); globals()['_t']=t
def shot(name):
    QtGui.QGuiApplication.primaryScreen().grabWindow(0).save('/tmp/i_%s.png'%name); log('shot '+name)
for tt,name in [(18.1,'gesture'),(21,'viewsel'),(23.3,'sbar'),(29.5,'sketch'),(32.2,'ctxmenu'),(36,'search')]:
    QtCore.QTimer.singleShot(int((T0+tt-time.time())*1000), lambda n=name: shot(n))
QtCore.QTimer.singleShot(int((T0+26-time.time())*1000), lambda: (Gui.Selection.clearSelection(), Gui.ActiveDocument.setEdit('Sketch'), log('edit sketch')))
QtCore.QTimer.singleShot(int((T0+38-time.time())*1000), lambda: QtWidgets.QApplication.quit())
