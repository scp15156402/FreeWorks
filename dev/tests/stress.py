"""FreeWorks stress test (run by: dev/run_tests.sh --stress).

Hammers the interface with hundreds of rapid operations and checks for errors, UI stalls,
leaked widgets and memory growth. Writes $FREEWORKS_TEST_OUT/stress.json and quits."""
import gc, json, os, resource, time, traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

OUT = os.environ["FREEWORKS_TEST_OUT"]
R = []


STAGES = []


def stage(n):
    STAGES.append((n, widgets(), round(rss_mb())))


def rec(name, ok, detail=""):
    R.append({"test": "stress: " + name, "ok": bool(ok), "detail": str(detail)[:400]})


def pump(ms=0):
    end = time.time() + ms / 1000.0
    while True:
        QtWidgets.QApplication.processEvents()
        # objects scheduled with deleteLater() are only destroyed when explicitly flushed here
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
        if time.time() >= end:
            break


def rss_mb():
    """current resident memory (not the peak)"""
    try:
        with open("/proc/self/statm") as f:
            return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 1048576.0
    except Exception:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def widgets():
    return len(QtWidgets.QApplication.allWidgets())


def run():
    import freeworks
    from freeworks import naming, shell, shortcuts, contextmenu, context, gestures
    try:
        doc = naming.new_document("part")
        pump(500)
        base_err = len(freeworks.STATS["errors"])
        w0, m0 = widgets(), rss_mb()

        # 1. sketch edit in/out
        import Part, Sketcher
        body = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"][0]
        top = [f for f in body.Origin.OriginFeatures if f.Role == "XY_Plane"][0]
        sk = body.newObject("Sketcher::SketchObject", "Sketch")
        sk.AttachmentSupport = [(top, "")]; sk.MapMode = "FlatFace"
        sk.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 10)); doc.recompute()
        pad = body.newObject("PartDesign::Pad", "Pad"); pad.Profile = sk; pad.Length = 10; doc.recompute()
        t = time.time()
        for i in range(30):
            Gui.ActiveDocument.setEdit(sk.Name); pump(60)
            shell._S["controller"].tick()
            Gui.ActiveDocument.resetEdit(); pump(60)
            shell._S["controller"].tick()
        pump(300)
        ws, ms_ = widgets(), rss_mb()
        rec("30 sketch edit/exit cycles", context.current() == "part" and shell._S["cm"].current_name() == "Features",
            "%.1fs; FreeCAD's sketch editor itself keeps ~60 widgets per edit (also without FreeWorks): %d -> %d widgets, %.0f -> %.0f MB"
            % (time.time() - t, w0, ws, m0, ms_))
        w0, m0 = ws, ms_          # leak checks below cover what FreeWorks controls

        stage('2. CommandManager ')
        # 2. CommandManager tab switching
        cm = shell._S["cm"]
        t = time.time()
        for i in range(300):
            cm.tabs.setCurrentIndex(i % cm.tabs.count())
            if i % 25 == 0:
                pump()
        rec("300 CommandManager tab switches", True, "%.2f ms each" % ((time.time() - t) / 300 * 1000))

        stage('3. shortcuts')
        # 3. shortcuts (view / zoom keys)
        t = time.time()
        for i in range(200):
            shortcuts.dispatch(["Ctrl+1", "Ctrl+5", "Ctrl+7", "Z", "Shift+Z", "Ctrl+Shift+Z"][i % 6])
            if i % 20 == 0:
                pump()
        rec("200 shortcut dispatches", True, "%.2f ms each" % ((time.time() - t) / 200 * 1000))

        stage('4. context menu bu')
        # 4. context menu building with different selections
        t = time.time()
        for i in range(200):
            Gui.Selection.clearSelection()
            if i % 3 == 1:
                Gui.Selection.addSelection(pad)
            elif i % 3 == 2:
                Gui.Selection.addSelection(pad, "Face1")
            contextmenu.items("View")
        Gui.Selection.clearSelection()
        rec("200 context menu builds", True, "%.2f ms each" % ((time.time() - t) / 200 * 1000))

        stage('5. mouse gestures')
        # 5. mouse gestures (real events on the 3D viewport)
        vps = gestures.view_widgets()
        n_ok = 0
        if vps:
            vp = vps[0]
            c = QtCore.QPointF(vp.width() / 2, vp.height() / 2)
            for i in range(25):
                g = vp.mapToGlobal(c.toPoint())
                QtWidgets.QApplication.sendEvent(vp, QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress, c, QtCore.QPointF(g), QtCore.Qt.RightButton, QtCore.Qt.RightButton, QtCore.Qt.NoModifier))
                for k in range(1, 8):
                    p = QtCore.QPointF(c.x() + 12 * k, c.y() - 12 * k)
                    QtWidgets.QApplication.sendEvent(vp, QtGui.QMouseEvent(QtCore.QEvent.MouseMove, p, QtCore.QPointF(vp.mapToGlobal(p.toPoint())), QtCore.Qt.NoButton, QtCore.Qt.RightButton, QtCore.Qt.NoModifier))
                QtWidgets.QApplication.sendEvent(vp, QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, p, QtCore.QPointF(vp.mapToGlobal(p.toPoint())), QtCore.Qt.RightButton, QtCore.Qt.NoButton, QtCore.Qt.NoModifier))
                pump(30)
                n_ok += 1
        rec("25 mouse gestures", n_ok == 25 and vps, n_ok)

        stage('6. documents')
        # 6. documents: create / switch / close, three rounds.  Plain FreeCAD 1.1.4 also grows ~450 MB
        # in the first round (GL buffers, allocator arenas, TechDraw/Assembly caches) and then levels
        # off, so a real leak shows up as growth that keeps going between rounds 2 and 3.
        t = time.time()
        mdi = context.mdi_area()
        round_rss = [round(rss_mb())]
        for rnd in range(3):
            for i in range(12):
                naming.new_document(["part", "assembly", "drawing"][i % 3]); pump(150)
                shell._S["controller"].tick()
            for i in range(60):
                subs = mdi.subWindowList()
                mdi.setActiveSubWindow(subs[i % len(subs)])
                if i % 6 == 0:
                    pump(20)
                shell._S["controller"].tick()
            for n in list(App.listDocuments()):
                App.closeDocument(n)
            pump(800)
            shell._S["controller"].tick()
            round_rss.append(round(rss_mb()))
        rec("3 x (12 documents created, 60 window switches, all closed)", context.current() == "none",
            "%.1fs; RSS after each round %s MB" % (time.time() - t, round_rss))
        rec("memory levels off (round 3 adds < 100 MB)", round_rss[3] - round_rss[2] < 100,
            "round 2 -> 3: %+d MB (plain FreeCAD: about +45 MB)" % (round_rss[3] - round_rss[2]))

        stage('7. leaks')
        # 7. leaks / errors / stalls
        gc.collect(); pump(500)
        w1, m1 = widgets(), rss_mb()
        rec("no FreeWorks widget leak (growth < 150 after the sketch stage)", w1 - w0 < 150, "%d -> %d widgets; stages %s" % (w0, w1, STAGES))
        rec("memory after all stages (info)", True, "%.0f -> %.0f MB (current RSS)" % (m0, m1))
        errs = freeworks.STATS["errors"][base_err:]
        rec("no FreeWorks errors", not errs, errs[:3])
        rec("UI stalls during stress (info)", True, [(round(ms), w) for _, ms, w in freeworks.STATS["stalls"]][:6])
        slow = [(n, round(ms)) for _, n, ms in freeworks.STATS["slow"]]
        rec("no slow FreeWorks callbacks", not slow, slow[:6])
    except Exception:
        rec("stress run (exception)", False, traceback.format_exc())
    json.dump(R, open(os.path.join(OUT, "stress.json"), "w"), indent=1)
    QtWidgets.QApplication.quit()


def wait(n=0):
    try:
        from freeworks import shell
        ok = shell._S.get("dock") is not None
    except Exception:
        ok = False
    if ok or n > 120:
        QtCore.QTimer.singleShot(1500, run)
    else:
        QtCore.QTimer.singleShot(250, lambda: wait(n + 1))


Gui.getMainWindow().resize(1700, 1000)
QtCore.QTimer.singleShot(500, wait)
