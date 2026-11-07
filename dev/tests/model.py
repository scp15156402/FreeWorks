import FreeCADGui as Gui, FreeCAD as App, Part, Sketcher
from freeworks import naming
V=App.Vector
doc=naming.new_document("part")
body=[o for o in doc.Objects if o.TypeId=="PartDesign::Body"][0]
org=body.Origin
top=[f for f in org.OriginFeatures if f.Role=="XY_Plane"][0]
sk=body.newObject('Sketcher::SketchObject','Sketch'); sk.AttachmentSupport=[(top,'')]; sk.MapMode='FlatFace'
pts=[V(-30,-20,0),V(30,-20,0),V(30,20,0),V(-30,20,0)]
for i in range(4): sk.addGeometry(Part.LineSegment(pts[i],pts[(i+1)%4]))
for i in range(4): sk.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%4,1))
sk.addConstraint(Sketcher.Constraint('Horizontal',0)); sk.addConstraint(Sketcher.Constraint('Horizontal',2))
sk.addConstraint(Sketcher.Constraint('Vertical',1)); sk.addConstraint(Sketcher.Constraint('Vertical',3))
sk.addConstraint(Sketcher.Constraint('DistanceX',0,1,0,2,60)); sk.addConstraint(Sketcher.Constraint('DistanceY',1,1,1,2,40))
sk.addConstraint(Sketcher.Constraint('Symmetric',0,1,1,2,-1,1))
doc.recompute()
pad=body.newObject('PartDesign::Pad','Pad'); pad.Profile=sk; pad.Length=20; doc.recompute()
sk2=body.newObject('Sketcher::SketchObject','Sketch'); sk2.AttachmentSupport=[(pad,'Face6')]; sk2.MapMode='FlatFace'
sk2.addGeometry(Part.Circle(V(0,0,0),V(0,0,1),10)); sk2.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1)); sk2.addConstraint(Sketcher.Constraint('Diameter',0,20)); doc.recompute()
pk=body.newObject('PartDesign::Pocket','Pocket'); pk.Profile=sk2; pk.Type=1; doc.recompute()
fl=body.newObject('PartDesign::Fillet','Fillet'); fl.Base=(pk,['Edge1','Edge3','Edge5','Edge7']); fl.Radius=4; doc.recompute()
for o in (sk,sk2,pad,pk): 
    try: o.ViewObject.Visibility = (o is fl)
    except Exception: pass
fl.ViewObject.Visibility=True
Gui.activeDocument().activeView().viewIsometric(); Gui.SendMsgToActiveView("ViewFit")
App.Console.PrintMessage("LABELS %s\n" % [o.Label for o in doc.Objects])
open('/tmp/labels.txt','w').write(str([(o.Name,o.Label) for o in doc.Objects]))
