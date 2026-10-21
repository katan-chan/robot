"""Kiểm model theo Quy ước rồi in mô tả link, vị trí bàn chân và đơn vị.

    blender -b --factory-startup F.blend --python blender/inspect_model.py -- --result R
"""
import argparse, sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c


def inspect(a):
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    errors = c.validate(scene, c.load_servos())
    if errors:
        return {"ok": False, "errors": errors}
    return {"ok": True, **c.collect(scene)}


if __name__ == "__main__":
    c.run(inspect, argparse.ArgumentParser())
