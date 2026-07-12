bl_info = {
    "name": "NyanwTool",
    "author": "NyanWake ",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > NyanwTool",
    "description": "Workflow tools for creating ARkit blendshapes",
    "category": "3D View",
}

import bpy

if "operators" in locals():
    import importlib

    from . import blendshape_list
    from . import mirror
    from . import presets
    from . import shape_sets

    importlib.reload(blendshape_list)
    importlib.reload(mirror)
    importlib.reload(presets)
    importlib.reload(shape_sets)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    from . import blendshape_list
    from . import operators
    from . import ui


def register():
    blendshape_list.register()
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()
    blendshape_list.unregister()


if __name__ == "__main__":
    register()
