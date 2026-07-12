import bpy


class NYANWTOOLS_BlendshapeItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

    family: bpy.props.StringProperty()

    exists: bpy.props.BoolProperty(
        default=False,
    )

    selected: bpy.props.BoolProperty(
        default=False,
    )


classes = (
    NYANWTOOLS_BlendshapeItem,
    NYANWTOOLS_UL_BlendshapeList,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.nyanwtools_blendshapes = bpy.props.CollectionProperty(
        type=NYANWTOOLS_BlendshapeItem,
    )

    bpy.types.Scene.nyanwtools_blendshape_index = bpy.props.IntProperty()


def unregister():

    del bpy.types.Scene.nyanwtools_blendshape_index
    del bpy.types.Scene.nyanwtools_blendshapes

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

        
class NYANWTOOLS_UL_BlendshapeList(bpy.types.UIList):

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

        if item.exists:
            row.label(icon='CHECKMARK')
        else:
            row.label(icon='CANCEL')

        row.label(text=item.name)

from . import presets


def rebuild_list(scene):

    collection = scene.nyanwtools_blendshapes
    collection.clear()

    for preset in presets.BLENDSHAPE_PRESETS:

        for blendshape in preset["blendshapes"]:

            item = collection.add()
            item.name = blendshape
            item.family = preset["name"]
            item.exists = False