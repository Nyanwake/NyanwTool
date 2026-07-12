import bpy

from . import mirror
from . import presets
from . import shape_sets


FAMILY_EXPANDED_PROPERTY_PREFIX = "nyanwtool_family_expanded_"


def get_family_expanded_property_name(preset_index):
    return f"{FAMILY_EXPANDED_PROPERTY_PREFIX}{preset_index}"


def is_family_selected(scene, preset_index):
    preset_items = [
        item
        for item in scene.nyanwtool_blendshapes
        if item.preset_index == preset_index
    ]

    if not preset_items:
        return False

    return all(item.selected for item in preset_items)


def set_family_blendshapes_selected(scene, preset_index, is_selected):
    for item in scene.nyanwtool_blendshapes:
        if item.preset_index == preset_index:
            item.selected = is_selected


def clear_blendshape_selection(scene):
    for item in scene.nyanwtool_blendshapes:
        item.selected = False


def get_selected_blendshapes(scene):
    selected_blendshapes = {}

    for item in scene.nyanwtool_blendshapes:
        if not item.selected:
            continue

        selected_blendshapes.setdefault(item.preset_index, []).append(item.name)

    return selected_blendshapes


def get_selected_blendshape_names(scene):
    return list(
        dict.fromkeys(
            item.name
            for item in scene.nyanwtool_blendshapes
            if item.selected
        )
    )


def count_selected_blendshapes(scene, preset_index):
    return sum(
        1
        for item in scene.nyanwtool_blendshapes
        if item.preset_index == preset_index and item.selected
    )


def register_scene_properties():
    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
        property_name = get_family_expanded_property_name(preset_index)

        if not hasattr(bpy.types.Scene, property_name):
            setattr(
                bpy.types.Scene,
                property_name,
                bpy.props.BoolProperty(
                    name=f"Show {preset['name']}",
                    default=False,
                ),
            )


def unregister_scene_properties():
    for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
        property_name = get_family_expanded_property_name(preset_index)

        if hasattr(bpy.types.Scene, property_name):
            delattr(bpy.types.Scene, property_name)


class NYANWTOOL_OT_CreateBlendshapes(bpy.types.Operator):
    bl_idname = "nyanwtool.create_blendshapes"
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


class NYANWTOOL_OT_FlipSelectedBlendshape(bpy.types.Operator):
    bl_idname = "nyanwtool.flip_selected_blendshape"
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
            self.report({'ERROR'}, "Select at least one Blendshape in NyanwTool.")
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


class NYANWTOOL_OT_ClearBlendshapeSelection(bpy.types.Operator):
    bl_idname = "nyanwtool.clear_blendshape_selection"
    bl_label = "Clear Selection"
    bl_description = "Clear selected Blendshapes in NyanwTool"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        clear_blendshape_selection(context.scene)

        return {'FINISHED'}


class NYANWTOOL_OT_ToggleFamilySelection(bpy.types.Operator):
    bl_idname = "nyanwtool.toggle_family_selection"
    bl_label = "Toggle Blendshape Family"
    bl_description = "Select or deselect this Blendshape family"
    bl_options = {'INTERNAL'}

    preset_index: bpy.props.IntProperty()

    def execute(self, context):
        current_value = is_family_selected(context.scene, self.preset_index)
        set_family_blendshapes_selected(context.scene, self.preset_index, not current_value)

        return {'FINISHED'}


classes = (
    NYANWTOOL_OT_CreateBlendshapes,
    NYANWTOOL_OT_FlipSelectedBlendshape,
    NYANWTOOL_OT_ClearBlendshapeSelection,
    NYANWTOOL_OT_ToggleFamilySelection,
)


def register():
    register_scene_properties()

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    unregister_scene_properties()
