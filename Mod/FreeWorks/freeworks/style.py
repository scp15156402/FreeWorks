"""FreeWorks widget styles. Applied only to FreeWorks' own widgets (never to the main window,
so FreeCAD's widgets do not carry extra style data)."""

STYLE = """
#FreeWorksTop { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FDFDFD, stop:1 #EEEFF1); border-bottom: 1px solid #D0D3D8; }
#FreeWorksTop QMenuBar { background: transparent; border: none; font-size: 9pt; }
#FreeWorksTop QMenuBar::item { padding: 3px 8px; background: transparent; }
#FreeWorksTop QMenuBar::item:selected { background: #CCE4F7; border: 1px solid #99C9EF; }
#FreeWorksTitle { color: #222; font-size: 10pt; }
#FreeWorksLogo { border: none; padding: 1px 4px; }
#FreeWorksQuick QToolButton { border: 1px solid transparent; border-radius: 2px; padding: 1px; }
#FreeWorksQuick QToolButton:hover { background: #E5F1FB; border-color: #A9CDEF; }
#FreeWorksSearch { border: 1px solid #B9BEC6; border-radius: 2px; padding: 2px 6px; background: #FFFFFF; min-width: 220px; }
#FreeWorksSearch:focus { border-color: #2F7BE5; }
#FreeWorksSearchMode { border: none; padding: 0 2px; }
#FreeWorksCM { background: #F7F7F8; }
#FreeWorksCMPanel { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #FFFFFF, stop:1 #F1F2F4); border-bottom: 1px solid #C9CCD1; }
#FreeWorksCMPanel QToolButton { border: 1px solid transparent; border-radius: 2px; padding: 1px 2px; color: #1B1B1B; font-size: 8pt; }
#FreeWorksCMPanel QToolButton:hover { background: #E5F1FB; border-color: #A9CDEF; }
#FreeWorksCMPanel QToolButton:pressed { background: #CCE4F7; border-color: #6FA8E3; }
#FreeWorksCMPanel QToolButton:disabled { color: #9AA0A8; }
#FreeWorksCMPanel QToolButton[popupMode="1"] { padding-right: 10px; }
#FreeWorksCMSep { background: #D3D6DB; max-width: 1px; min-width: 1px; margin: 4px 3px; }
#FreeWorksTabs { background: #EDEEF0; border: none; }
#FreeWorksTabs::tab { background: transparent; border: 1px solid transparent; border-top: none; padding: 2px 12px 3px 12px; margin-right: 1px; color: #333; font-size: 8.5pt; }
#FreeWorksTabs::tab:selected { background: #FFFFFF; border-color: #C9CCD1; color: #000; }
#FreeWorksTabs::tab:hover:!selected { background: #E5F1FB; }
#FreeWorksHeadsUp, #FreeWorksFilters { background: transparent; }
#FreeWorksHeadsUp QToolButton, #FreeWorksFilters QToolButton { background: transparent; border: 1px solid transparent; border-radius: 3px; padding: 2px; }
#FreeWorksHeadsUp QToolButton:hover, #FreeWorksFilters QToolButton:hover { background: rgba(229,241,251,200); border-color: #A9CDEF; }
#FreeWorksHeadsUp QToolButton:checked, #FreeWorksFilters QToolButton:checked { background: rgba(204,228,247,230); border-color: #6FA8E3; }
#FreeWorksFilters { background: rgba(250,250,251,235); border: 1px solid #C6C9CE; border-radius: 3px; }
#FreeWorksPopupFrame { background: #FAFAFB; border: 1px solid #A7ADB6; }
#FreeWorksPopupTitle { font-weight: bold; color: #333; padding: 2px; }
#FreeWorksViewCell { background: #FFFFFF; border: 1px solid #C6C9CE; border-radius: 2px; padding: 4px; }
#FreeWorksViewCell:hover { background: #E5F1FB; border-color: #6FA8E3; }
#FreeWorksNewButton { border: 1px solid #C6C9CE; border-radius: 3px; background: #FFFFFF; font-size: 11pt; padding: 8px; }
#FreeWorksNewButton:hover { background: #E5F1FB; border-color: #2F7BE5; }
#FreeWorksStatusCtx { color: #333; padding: 0 10px; }
#FreeWorksStatusUnits { color: #333; padding: 0 8px; border-left: 1px solid #C6C9CE; }
"""
