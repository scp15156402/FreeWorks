# FreeWorks - SolidWorks-style user experience for FreeCAD 1.1.x
# SPDX-License-Identifier: LGPL-2.1-or-later
import os
import FreeCAD as App
import FreeCADGui as Gui


class FreeWorksWorkbench(Gui.Workbench):
    MenuText = "FreeWorks"
    ToolTip = "SolidWorks-style interface: CommandManager, FeatureManager, shortcuts, gestures"

    def __init__(self):
        import freeworks
        self.__class__.Icon = os.path.join(freeworks.ICON_DIR, "freeworks.svg")

    def Initialize(self):
        from freeworks import commands
        commands.register()

    def Activated(self):
        from PySide import QtCore
        from freeworks import startup
        QtCore.QTimer.singleShot(0, startup.on_activated)

    def Deactivated(self):
        pass

    def ContextMenu(self, recipient):
        try:
            from freeworks import contextmenu
            for sub, cmds in contextmenu.items(recipient):
                self.appendContextMenu(sub, cmds)
        except Exception as e:
            App.Console.PrintWarning("FreeWorks context menu: %s\n" % e)

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(FreeWorksWorkbench())

# Apply preferences and the icon theme as early as possible (before FreeCAD
# loads workbench icons) so the whole UI starts in FreeWorks style.
try:
    from freeworks import prefs, naming
    # FreeCAD 1.1 floats the task panel as an overlay on the right; SolidWorks
    # keeps the PropertyManager docked next to the FeatureManager.
    _ov = App.ParamGet("User parameter:BaseApp/MainWindow/DockWindows/OverlayRight")
    if "Tasks" in _ov.GetString("Widgets", ""):
        _ov.SetString("Widgets", _ov.GetString("Widgets", "").replace("Tasks,", "").replace("Tasks", ""))
    prefs.apply()
    naming.sync_icon_theme()
except Exception as e:
    App.Console.PrintWarning("FreeWorks early init: %s\n" % e)
