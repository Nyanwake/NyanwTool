import bpy

from . import derived
from . import mirror
from . import presets
from . import shape_sets


FAMILY_SELECTED_PROPERTY_PREFIX = "NYANWTOOLS_family_selected_"
FAMILY_EXPANDED_PROPERTY_PREFIX = "NYANWTOOLS_family_expanded_"
BLENDSHAPE_SELECTED_PROPERTY_PREFIX = "NYANWTOOLS_blendshape_selected_"


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


def get_selected_blendshape_items(scene):
    selected_items = []

    for preset_index, blendshape_names in get_selected_blendshapes(scene).items():
        for blendshape_name in blendshape_names:
            selected_items.append((preset_index, blendshape_name))

    return selected_items


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
            created = shape_sets.create_missing_blendshapes(
                active_object,
                preset,
                blendshape_names,
            )
            created_count += created


        self.report({'INFO'}, f"Created {created_count} Blendshape(s).")

        return {'FINISHED'}


class NYANWTOOLS_OT_FlipSelectedBlendshape(bpy.types.Operator):
    bl_idname = "nyanwtools.flip_selected_blendshape"
    bl_label = "Flip Blendshape"
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


class NYANWTOOLS_OT_CombineBlendshape(bpy.types.Operator):
    bl_idname = "nyanwtools.combine_blendshape"
    bl_label = "Combine Blendshape"
    bl_description = "Create or overwrite a Blendshape from the current Shape Key mix"
    bl_options = {'REGISTER', 'UNDO'}

    combine_mode: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})
    target_preset_index: bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})
    target_blendshape_name: bpy.props.StringProperty(default="", options={'SKIP_SAVE'})
    new_blendshape_name: bpy.props.StringProperty(
        name="Name",
        default="Combined",
        options={'SKIP_SAVE'},
    )

    def validate_active_object(self, active_object):
        if active_object is None or active_object.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object.")
            return False

        if active_object.mode != 'OBJECT':
            self.report({'ERROR'}, "Switch to Object Mode.")
            return False

        return True

    def prepare_from_selection(self, context):
        selected_items = get_selected_blendshape_items(context.scene)

        if len(selected_items) > 1:
            self.report({'ERROR'}, "Select only one Blendshape for Combine.")
            return False

        if not selected_items:
            self.combine_mode = "NEW"
            self.target_preset_index = -1
            self.target_blendshape_name = ""
            return True

        preset_index, blendshape_name = selected_items[0]
        self.combine_mode = "TARGET"
        self.target_preset_index = preset_index
        self.target_blendshape_name = blendshape_name
        return True

    def invoke(self, context, event):
        active_object = context.object

        if not self.validate_active_object(active_object):
            return {'CANCELLED'}

        if not self.prepare_from_selection(context):
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        if self.combine_mode == "TARGET":
            layout.label(text="Are you sure you want to apply Combine to:")
            layout.label(text=self.target_blendshape_name, icon='SHAPEKEY_DATA')
            return

        layout.prop(self, "new_blendshape_name")

    def execute(self, context):
        active_object = context.object

        if not self.validate_active_object(active_object):
            return {'CANCELLED'}

        if not self.combine_mode:
            if not self.prepare_from_selection(context):
                return {'CANCELLED'}

        if self.combine_mode == "NEW":
            blendshape_name = self.new_blendshape_name.strip()

            if not blendshape_name:
                self.report({'ERROR'}, "Enter a Blendshape name.")
                return {'CANCELLED'}

            final_name = derived.create_new_combined_blendshape(
                active_object,
                blendshape_name,
            )
            self.report({'INFO'}, f"Created {final_name}.")
            return {'FINISHED'}

        if self.target_preset_index < 0:
            self.report({'ERROR'}, "Select a target Blendshape.")
            return {'CANCELLED'}

        preset = presets.BLENDSHAPE_PRESETS[self.target_preset_index]
        applied = derived.apply_combined_blendshape_to_target(
            active_object,
            preset,
            self.target_blendshape_name,
        )

        if not applied:
            self.report({'ERROR'}, "Could not apply Combine Blendshape.")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Applied Combine to {self.target_blendshape_name}.")
        return {'FINISHED'}


class NYANWTOOLS_OT_ClearBlendshapeSelection(bpy.types.Operator):
    bl_idname = "nyanwtools.clear_blendshape_selection"
    bl_label = "Clear Selection"
    bl_description = "Clear selected Blendshapes in NYANWTOOLS"
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
    add_to_selection: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    def invoke(self, context, event):
        self.add_to_selection = event.ctrl
        return self.execute(context)

    def execute(self, context):
        property_name = get_family_selected_property_name(self.preset_index)

        if not self.add_to_selection:
            clear_blendshape_selection(context.scene)
            setattr(context.scene, property_name, True)
            set_family_blendshapes_selected(context.scene, self.preset_index, True)
            return {'FINISHED'}

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
    add_to_selection: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})

    def invoke(self, context, event):
        self.add_to_selection = event.ctrl
        return self.execute(context)

    def execute(self, context):
        property_name = get_blendshape_selected_property_name(
            self.preset_index,
            self.blendshape_index,
        )
        current_value = getattr(context.scene, property_name)

        if not self.add_to_selection:
            if current_value:
                setattr(context.scene, property_name, False)
                update_family_selection(context.scene, self.preset_index)
                return {'FINISHED'}

            clear_blendshape_selection(context.scene)
            setattr(context.scene, property_name, True)
            update_family_selection(context.scene, self.preset_index)
            return {'FINISHED'}

        setattr(context.scene, property_name, not current_value)
        update_family_selection(context.scene, self.preset_index)

        return {'FINISHED'}


classes = (
    NYANWTOOLS_OT_CreateBlendshapes,
    NYANWTOOLS_OT_FlipSelectedBlendshape,
    NYANWTOOLS_OT_CombineBlendshape,
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

