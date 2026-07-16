import os

import bpy
import bpy.utils.previews

from . import operators
from . import presets
from . import shape_sets

LOGO_ICON = "LOGO"

ICON_FILES = {
    LOGO_ICON: "logo.png",
    shape_sets.STATUS_GREEN: "green.png",
    shape_sets.STATUS_YELLOW: "yellow.png",
    shape_sets.STATUS_RED: "red.png",
}

FALLBACK_STATUS_ICONS = {
    shape_sets.STATUS_GREEN: 'CHECKMARK',
    shape_sets.STATUS_YELLOW: 'ERROR',
    shape_sets.STATUS_RED: 'CANCEL',
}

preview_collections = {}

def get_icon_folder_path():
    return os.path.join(os.path.dirname(__file__), "icons")

def load_icons():
    icon_previews = bpy.utils.previews.new()
    icon_folder_path = get_icon_folder_path()

    for icon_name, icon_file_name in ICON_FILES.items():
        icon_path = os.path.join(icon_folder_path, icon_file_name)

        if os.path.exists(icon_path):
            icon_previews.load(icon_name, icon_path, 'IMAGE')

    preview_collections["main"] = icon_previews

def unload_icons():
    for icon_previews in preview_collections.values():
        bpy.utils.previews.remove(icon_previews)

    preview_collections.clear()

def get_status_icon_id(status):
    icon_previews = preview_collections.get("main")

    if icon_previews is None:
        return 0

    icon = icon_previews.get(status)

    if icon is None:
        return 0

    return icon.icon_id

def get_icon_id(icon_name):
    icon_previews = preview_collections.get("main")

    if icon_previews is None:
        return 0

    icon = icon_previews.get(icon_name)

    if icon is None:
        return 0

    return icon.icon_id

def draw_panel_header(layout):
    logo_icon_id = get_icon_id(LOGO_ICON)
    
    if logo_icon_id:
        layout.label(text="NyanWake's Blendshape Tool", icon_value=logo_icon_id)
    else:
        layout.label(text="NyanWake's Blendshape Tool", icon='TOOL_SETTINGS')

def draw_status_operator(layout, operator_idname, status, text, is_selected):
    icon_id = get_status_icon_id(status)
    
    if icon_id:
        return layout.operator(
            operator_idname,
            text=text,
            icon_value=icon_id,
            depress=is_selected,
        )
    
    return layout.operator(
        operator_idname,
        text=text,
        icon=FALLBACK_STATUS_ICONS[status],
        depress=is_selected,
    )

def draw_blendshape_row(layout, context, active_object, preset_index, blendshape_index, blendshape_name):
    row = layout.row(align=True)
    row.separator()
    
    selected_property_name = operators.get_blendshape_selected_property_name(
        preset_index,
        blendshape_index,
    )
    status = shape_sets.calculate_blendshape_status(active_object, blendshape_name)
    is_selected = getattr(context.scene, selected_property_name)
    
    toggle_operator = draw_status_operator(
        row,
        "nyanwtools.toggle_blendshape_selection",
        status,
        blendshape_name,
        is_selected,
    )
    toggle_operator.preset_index = preset_index
    toggle_operator.blendshape_index = blendshape_index

def draw_preset_row(layout, context, active_object, preset_index, preset):
    status, existing_count, total_count = shape_sets.calculate_preset_status(
        active_object,
        preset,
    )

    selected_property_name = operators.get_family_selected_property_name(preset_index)
    expanded_property_name = operators.get_family_expanded_property_name(preset_index)
    is_expanded = getattr(context.scene, expanded_property_name)
    is_selected = getattr(context.scene, selected_property_name)

    row = layout.row(align=True)
    row.prop(
        context.scene,
        expanded_property_name,
        text="",
        icon='TRIA_DOWN' if is_expanded else 'TRIA_RIGHT',
        emboss=False,
    )
    toggle_operator = draw_status_operator(
        row,
        "nyanwtools.toggle_family_selection",
        status,
        f"{preset['name']} {existing_count}/{total_count}",
        is_selected,
    )
    toggle_operator.preset_index = preset_index

    if not is_expanded:
        return

    column = layout.column(align=True)

    for blendshape_index, blendshape_name in enumerate(preset["blendshapes"]):
        draw_blendshape_row(
            column,
            context,
            active_object,
            preset_index,
            blendshape_index,
            blendshape_name,
        )

class NYANWTOOLS_PT_MainPanel(bpy.types.Panel):
    bl_label = "NyanwTools"
    bl_idname = "NYANWTOOLS_PT_main_panel"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NyanwTools"

    def draw(self, context):
        layout = self.layout
        active_object = context.object

        draw_panel_header(layout)

        #
        # Shape Sets
        #
        box = layout.box()
        header_row = box.row(align=True)
        header_row.label(text="Blendshape Sets", icon='SHAPEKEY_DATA')

        for preset_index, preset in enumerate(presets.BLENDSHAPE_PRESETS):
            draw_preset_row(
                box,
                context,
                active_object,
                preset_index,
                preset,
            )

        create_row = box.row()
        create_row.scale_y = 1.5
        create_row.operator("nyanwtools.create_blendshapes", icon='ADD')



def draw_native_shape_keys_buttons(self, context):
    active_object = context.object

    if active_object is None or active_object.type != 'MESH':
        return

    layout = self.layout
    layout.separator()

    row = layout.row(align=True)
    row.operator(
        "nyanwtools.flip_selected_blendshape",
        text="Flip Blendshape",
        icon='MOD_MIRROR',
    )
    row.operator(
        "nyanwtools.combine_blendshape",
        text="Combine Blendshape",
        icon='SHAPEKEY_DATA',
    )


def register_native_shape_keys_buttons():
    shape_keys_panel = getattr(bpy.types, "DATA_PT_shape_keys", None)

    if shape_keys_panel is None:
        return

    try:
        shape_keys_panel.remove(draw_native_shape_keys_buttons)
    except (AttributeError, ValueError):
        pass

    shape_keys_panel.prepend(draw_native_shape_keys_buttons)


def unregister_native_shape_keys_buttons():
    shape_keys_panel = getattr(bpy.types, "DATA_PT_shape_keys", None)

    if shape_keys_panel is None:
        return

    try:
        shape_keys_panel.remove(draw_native_shape_keys_buttons)
    except (AttributeError, ValueError):
        pass

classes = (
    NYANWTOOLS_PT_MainPanel,
)

def register():
    load_icons()

    for cls in classes:
        bpy.utils.register_class(cls)

    register_native_shape_keys_buttons()

def unregister():
    unregister_native_shape_keys_buttons()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    unload_icons()
