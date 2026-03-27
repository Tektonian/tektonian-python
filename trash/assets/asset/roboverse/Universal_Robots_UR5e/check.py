from pxr import Usd, UsdPhysics

stage = Usd.Stage.Open("/home/zuo/Documents/RoboVerse/roboverse_data/robots/universal_robots_ur5e/ur5e/ur5e.usd")
for prim in stage.Traverse():
    if prim.IsA(UsdPhysics.RevoluteJoint) or prim.IsA(UsdPhysics.PrismaticJoint):
        joint = UsdPhysics.RevoluteJoint(prim) if prim.IsA(UsdPhysics.RevoluteJoint) else UsdPhysics.PrismaticJoint(prim)
        name = prim.GetPath().pathString
        lo = joint.GetLowerLimitAttr().Get()
        hi = joint.GetUpperLimitAttr().Get()
        print(name, lo, hi)
