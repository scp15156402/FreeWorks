import time, sys
from Xlib import X, XK, display
from Xlib.ext import xtest
d = display.Display(sys.argv[1]); T0=float(sys.argv[2])
def at(t):
    w=T0+t-time.time()
    if w>0: time.sleep(w)
def kc(name): return d.keysym_to_keycode(XK.string_to_keysym(name))
def key(name, mods=()):
    for m in mods: xtest.fake_input(d, X.KeyPress, kc(m))
    xtest.fake_input(d, X.KeyPress, kc(name)); xtest.fake_input(d, X.KeyRelease, kc(name))
    for m in reversed(mods): xtest.fake_input(d, X.KeyRelease, kc(m))
    d.sync()
def move(x,y): xtest.fake_input(d, X.MotionNotify, x=x, y=y); d.sync()
def btn(b, down): xtest.fake_input(d, X.ButtonPress if down else X.ButtonRelease, b); d.sync()
def click(x,y,b=1): move(x,y); time.sleep(0.05); btn(b,1); time.sleep(0.05); btn(b,0)
def typ(s):
    for ch in s: key(ch); time.sleep(0.03)
for t, act in [
    (15, lambda: click(400, 300)),
    (16, lambda: key('7', ['Control_L'])),
    (17, lambda: (move(980,560), time.sleep(.1), btn(3,1), [ (move(980+6*i,560-6*i), time.sleep(0.03)) for i in range(1,12)])),
    (18.5, lambda: btn(3,0)),
    (20, lambda: (move(900,500), key('space'))),
    (21.5, lambda: key('Escape')),
    (22.5, lambda: key('s')),
    (24, lambda: key('Escape')),
    (27, lambda: (move(980,560), key('c'))),
    (28, lambda: click(1000,560)),
    (28.6, lambda: click(1060,560)),
    (30, lambda: key('Escape')),
    (30.5, lambda: key('Escape')),
    (31, lambda: click(500,400,3)),
    (33, lambda: key('Escape')),
    (34, lambda: key('w')),
    (34.6, lambda: typ('pad')),
]:
    at(t); act()
time.sleep(2)
