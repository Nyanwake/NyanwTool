import bpy

from . import mirror
from . import presets
from . import shape_sets


FAMILY_SELECTED_PROPERTY_PREFIX = "nyanwtools_family_selected_"
FAMILY_EXPANDED_PROPERTY_PREFIX = "nyanwtools_family_expanded_"
BLENDSHAPE_SELECTED_PROPERTY_PREFIX = "nyanwtools_blendshape_selected_"


def get_family_selected_property_name(preset_index):
    return f"{FAMILY_SELECTED_PROPERTY_PREFIX}{preset_index}"


def get_family_expanded_property_name(preset_index):
    return f"{FAMILY_EXPANDED_PROPERTY_PREFIX}{preset_index}"


def get_blendshape_selected_property_name(preset_index, blendshape_index):
    return f"{BLENDSHAPE_SELECTED_PROPERTY_PREFIX}{preset_index}_{blendshape_index}"


def is_family_selected(scene, preset_index):
    property_name = get_family_selected_property_name(preset_index)

    return getattr(scene, property_name)


def is_blendshape_selected(scene, preset_index, blendshape_index):
    property_name = get_blendshape_selected_property_name(
        preset_index,
        blendshape_index,
    )

    return getattr(scene, property_name)


def set_family_blendshapes_selected(scene, preset_index, is_selected):
    preset = presets.BLENDSHAPE_PRESETS[preset_index]

    for blendshape_index, _blendshape_name in enumerate(preset["blendshapes"]):
        property_name = get_blendshape_selected_property_name(
            preset_index,
            blendshape_index,
        )

        setattr(scene, property_name, is_selected)


def are_all_family_blendshapes_selected(scene, preset_index):
    preset = presets.BLENDSHAPE_PRESETS[preset_index]

    if not preset["blendshapes"]:
        return False

    for blendshape_index, _blendshape_name in enumerate(preset["blendshapes"]):
        if not is_blendshape_selected(scene, preset_index, blendshape_index):
            return False

    return True


def update_family_selection(scene, preset_index):
    property_name = get_family_selected_property_name(preset_index)
    is_selected = are_all_family_blendshapes_selected(scene, preset_index)

    setattr(scene, property_name, is_selected)


def clear_blendshape_selection(scene):
    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
        family_property_name = get_family_selected_property_name(preset_index)
        setattr(scene, family_property_name, False)

        for blendshape_index, _blendshape_name in enumerate(preset["blendshapes"]):
            blendshape_property_name = get_blendshape_selected_property_name(
                preset_index,
                blendshape_index,
            )
            setattr(scene, blendshape_property_name, False)


def get_selected_blendshapes(scene):
    selected_blendshapes = {}

    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
        blendshape_names = []

        for blendshape_index, blendshape_name in enumerate(preset["blendshapes"]):
            if is_blendshape_selected(scene, preset_index, blendshape_index):
                blendshape_names.append(blendshape_name)

        if blendshape_names:
            selected_blendshapes[preset_index] = list(dict.fromkeys(blendshape_names))

    return selected_blendshapes


def get_selected_blendshape_names(scene):
    selected_names = []

    for blendshape_names in get_selected_blendshapes(scene).values():
        selected_names.extend(blendshape_names)

    return list(dict.fromkeys(selected_names))


def register_scene_properties():
    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
        family_selected_property_name = get_family_selected_property_name(preset_index)
        family_expanded_property_name = get_family_expanded_property_name(preset_index)

        setattr(
            bpy.types.Scene,
            family_selected_property_name,
            bpy.props.BoolProperty(
                name=preset["name"],
                default=False,
            ),
        )
        setattr(
            bpy.types.Scene,
            family_expanded_property_name,
            bpy.props.BoolProperty(
                name=f"Show {preset['name']}",
                default=False,
            ),
        )

        for blendshape_index, blendshape_name in enumerate(preset["blendshapes"]):
            blendshape_selected_property_name = get_blendshape_selected_property_name(
                preset_index,
                blendshape_index,
            )

            setattr(
                bpy.types.Scene,
                blendshape_selected_property_name,
                bpy.props.BoolProperty(
                    name=blendshape_name,
                    default=False,
                ),
            )


def unregister_scene_properties():
    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
        family_selected_property_name = get_family_selected_property_name(preset_index)
        family_expanded_property_name = get_family_expanded_property_name(preset_index)

        if hasattr(bpy.types.Scene, family_selected_property_name):
            delattr(bpy.types.Scene, family_selected_property_name)

        if hasattr(bpy.types.Scene, family_expanded_property_name):
            delattr(bpy.types.Scene, family_expanded_property_name)

        for blendshape_index, _blendshape_name in enumerate(preset["blendshapes"]):
            blendshape_selected_property_name = get_blendshape_selected_property_name(
                preset_index,
                blendshape_index,
            )

            if hasattr(bpy.types.Scene, blendshape_selected_property_name):
                delattr(bpy.types.Scene, blendshape_selected_property_name)


class NYANWTOOLS_OT_CreateBlendshapes(bpy.types.Operator):
    bl_idname = "nyanwtools.create_blendshapes"
    bl_label = "Create Blendshapes"
    bl_description = "Create selected missing Blendshapes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_object = context.object

        if active_object is None or active_object.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object.")
            return {'CANCELLED'}

        if active_object.mode != 'OBJECT':
            self.report({'ERROR'}, "Switch to Object Mode.")
            return {'CANCELLED'}

        selected_blendshapes = get_selected_blendshapes(context.scene)

        if not selected_blendshapes:
            self.report({'ERROR'}, "Select at least one Blendshape.")
            return {'CANCELLED'}

        created_count = 0

        for preset_index, blendshape_names in selected_blendshapes.items():
            preset = presets.BLENDSHAPE_PRESETS[preset_index]
            created_count += shape_sets.create_missing_blendshapes(
                active_object,
                preset,
                blendshape_names,
            )

        self.report({'INFO'}, f"Created {created_count} Blendshape(s).")

        return {'FINISHED'}


class NYANWTOOLS_OT_FlipSelectedBlendshape(bpy.types.Operator):
    bl_idname = "nyanwtools.flip_selected_blendshape"
    bl_label = "Flip Selected Blendshapes"
    bl_description = "Copy selected Left or Right Blendshapes to their opposite side"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_object = context.object

        if active_object is None or active_object.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object.")
            return {'CANCELLED'}

        if active_object.mode != 'OBJECT':
            self.report({'ERROR'}, "Switch to Object Mode.")
            return {'CANCELLED'}

        selected_blendshape_names = get_selected_blendshape_names(context.scene)

        if not selected_blendshape_names:
            self.report({'ERROR'}, "Select at least one Blendshape in NyanwTools.")
            return {'CANCELLED'}

        mirrored_count, skipped_count = mirror.create_mirrored_blendshapes(
            active_object,
            selected_blendshape_names,
        )

        if mirrored_count == 0:
            self.report({'INFO'}, "No selected paired Blendshapes to mirror.")
            return {'FINISHED'}

        message = f"Mirrored {mirrored_count} Blendshape(s)."

        if skipped_count:
            message += f" Skipped {skipped_count}."

        self.report({'INFO'}, message)

        return {'FINISHED'}


class NYANWTOOLS_OT_ClearBlendshapeSelection(bpy.types.Operator):
    bl_idname = "nyanwtools.clear_blendshape_selection"
    bl_label = "Clear Selection"
    bl_description = "Clear selected Blendshapes in NyanwTools"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        clear_blendshape_selection(context.scene)

        return {'FINISHED'}


class NYANWTOOLS_OT_ToggleFamilySelection(bpy.types.Operator):
    bl_idname = "nyanwtools.toggle_family_selection"
    bl_label = "Toggle Blendshape Family"
    bl_description = "Select or deselect this Blendshape family"
    bl_options = {'INTERNAL'}

    preset_index: bpy.props.IntProperty()

    def execute(self, context):
        property_name = get_family_selected_property_name(self.preset_index)
        current_value = getattr(context.scene, property_name)
        new_value = not current_value

        setattr(context.scene, property_name, new_value)
        set_family_blendshapes_selected(context.scene, self.preset_index, new_value)

        return {'FINISHED'}


class NYANWTOOLS_OT_ToggleBlendshapeSelection(bpy.types.Operator):
    bl_idname = "nyanwtools.toggle_blendshape_selection"
    bl_label = "Toggle Blendshape"
    bl_description = "Select or deselect this Blendshape"
    bl_options = {'INTERNAL'}

    preset_index: bpy.props.IntProperty()
    blendshape_index: bpy.props.IntProperty()

    def execute(self, context):
        property_name = get_blendshape_selected_property_name(
            self.preset_index,
            self.blendshape_index,
        )
        current_value = getattr(context.scene, property_name)

        setattr(context.scene, property_name, not current_value)
        update_family_selection(context.scene, self.preset_index)

        return {'FINISHED'}


classes = (
    NYANWTOOLS_OT_CreateBlendshapes,
    NYANWTOOLS_OT_FlipSelectedBlendshape,
    NYANWTOOLS_OT_ClearBlendshapeSelection,
    NYANWTOOLS_OT_ToggleFamilySelection,
    NYANWTOOLS_OT_ToggleBlendshapeSelection,
)


def register():
    register_scene_properties()

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    unregister_scene_properties()
