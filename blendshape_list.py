import bpy

from . import presets


class NYANWTOOLS_BlendshapeItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    preset_index: bpy.props.IntProperty()
    blendshape_index: bpy.props.IntProperty()


class NYANWTOOLS_UL_BlendshapeList(bpy.types.UIList):
    bl_idname = "NYANWTOOLS_UL_BlendshapeList"

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):
        layout.label(text=item.name)


# ------------------------------------------------------------------------
# Collection helpers
# ------------------------------------------------------------------------

_COLLECTION_NAMES = (
    "nyanwtools_list_0",
    "nyanwtools_list_1",
    "nyanwtools_list_2",
    "nyanwtools_list_3",
    "nyanwtools_list_4",
)

_INDEX_NAMES = (
    "nyanwtools_index_0",
    "nyanwtools_index_1",
    "nyanwtools_index_2",
    "nyanwtools_index_3",
    "nyanwtools_index_4",
)


def get_collection_name(preset_index):
    return _COLLECTION_NAMES[preset_index]


def get_index_name(preset_index):
    return _INDEX_NAMES[preset_index]


def get_collection(scene, preset_index):
    return getattr(scene, get_collection_name(preset_index))


def rebuild_lists(scene):
    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):

        collection = get_collection(scene, preset_index)
        collection.clear()

        for blendshape_index, blendshape_name in enumerate(preset["blendshapes"]):

            item = collection.add()
            item.name = blendshape_name
            item.preset_index = preset_index
            item.blendshape_index = blendshape_index


# ------------------------------------------------------------------------
# Register
# ------------------------------------------------------------------------

classes = (
    NYANWTOOLS_BlendshapeItem,
    NYANWTOOLS_UL_BlendshapeList,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    for collection_name in _COLLECTION_NAMES:
        setattr(
            bpy.types.Scene,
            collection_name,
            bpy.props.CollectionProperty(
                type=NYANWTOOLS_BlendshapeItem,
            ),
        )

    for index_name in _INDEX_NAMES:
        setattr(
            bpy.types.Scene,
            index_name,
            bpy.props.IntProperty(),
        )


def unregister():

    for collection_name in _COLLECTION_NAMES:
        if hasattr(bpy.types.Scene, collection_name):
            delattr(bpy.types.Scene, collection_name)

    for index_name in _INDEX_NAMES:
        if hasattr(bpy.types.Scene, index_name):
            delattr(bpy.types.Scene, index_name)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)