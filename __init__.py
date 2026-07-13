bl_info = {
    "name": "NyanwTools",
    "author": "NyanWake",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > NyanwTools",
    "description": "Workflow tools for creating ARKit blendshapes",
    "category": "3D View",
}

import bpy

if "operators" in locals():
    import importlib

    from . import derived
    from . import mirror
    from . import presets
    from . import shape_sets

    importlib.reload(derived)
    importlib.reload(mirror)
    importlib.reload(presets)
    importlib.reload(shape_sets)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    from . import operators
    from . import ui


def register():
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()

if __name__ == "__main__":
    register()
