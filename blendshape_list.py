import bpy

from . import presets
from . import shape_sets


class NYANWTOOL_BlendshapeItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

    family: bpy.props.StringProperty()

    preset_index: bpy.props.IntProperty()

    exists: bpy.props.BoolProperty(
        default=False,
    )

    selected: bpy.props.BoolProperty(
        default=False,
    )



def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    ensure_scene_properties()

    try:
        scene = bpy.context.scene
    except Exception:
        scene = None

    if scene is not None:
        rebuild_list(scene)


def ensure_scene_properties():
    if not hasattr(bpy.types.Scene, "nyanwtool_blendshapes"):
        bpy.types.Scene.nyanwtool_blendshapes = bpy.props.CollectionProperty(
            type=NYANWTOOL_BlendshapeItem,
        )

    if not hasattr(bpy.types.Scene, "nyanwtool_blendshape_index"):
        bpy.types.Scene.nyanwtool_blendshape_index = bpy.props.IntProperty()

    if not hasattr(bpy.types.Scene, "nyanwtool_current_preset_index"):
        bpy.types.Scene.nyanwtool_current_preset_index = bpy.props.IntProperty(
            default=-1,
        )


def unregister():
    del bpy.types.Scene.nyanwtool_current_preset_index
    del bpy.types.Scene.nyanwtool_blendshape_index
    del bpy.types.Scene.nyanwtool_blendshapes

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


class NYANWTOOL_UL_BlendshapeList(bpy.types.UIList):
    bl_idname = "NYANWTOOL_UL_BlendshapeList"

    def filter_items(self, context, data, propname):
        blendshape_items = getattr(data, propname)
        current_preset_index = getattr(context.scene, "nyanwtool_current_preset_index", -1)

        visible = [
            self.bitflag_filter_item
            if item.preset_index == current_preset_index
            else 0
            for item in blendshape_items
        ]

        return visible, list(range(len(blendshape_items)))

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_property,
        index,
    ):
        row = layout.row(align=True)
        row.prop(item, "selected", text="", emboss=False)

        if shape_sets.blendshape_exists(context.object, item.name):
            row.label(text=item.name, icon='CHECKMARK')
        else:
            row.label(text=item.name, icon='CANCEL')


classes = (
    NYANWTOOL_BlendshapeItem,
    NYANWTOOL_UL_BlendshapeList,
)


def rebuild_list(scene):
    previous_selection = {
        (item.preset_index, item.name): item.selected
        for item in scene.nyanwtool_blendshapes
    }

    collection = scene.nyanwtool_blendshapes
    collection.clear()

    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
        for blendshape in preset["blendshapes"]:
            item = collection.add()
            item.name = blendshape
            item.family = preset["name"]
            item.preset_index = preset_index
            item.selected = previous_selection.get((preset_index, blendshape), False)
            item.exists = shape_sets.blendshape_exists(scene.object, blendshape)