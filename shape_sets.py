import bpy

from . import presets

STATUS_GREEN = "GREEN"
STATUS_YELLOW = "YELLOW"
STATUS_RED = "RED"

SEPARATOR_SIDE = "══"


def format_separator_name(separator_name):
    return f"{SEPARATOR_SIDE} {separator_name} {SEPARATOR_SIDE}"


def get_shape_keys(active_object):
    if active_object is None:
        return None

    object_data = getattr(active_object, "data", None)

    if object_data is None:
        return None

    return getattr(object_data, "shape_keys", None)


def get_shape_key_blocks(active_object):
    shape_keys = get_shape_keys(active_object)

    if shape_keys is None:
        return None

    return shape_keys.key_blocks


def get_shape_key_names(active_object):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return ()

    return tuple(shape_key.name for shape_key in shape_key_blocks)


def get_active_shape_key_name(active_object):
    if active_object.active_shape_key is None:
        return None

    return active_object.active_shape_key.name


def set_active_shape_key(active_object, shape_key_name):
    if not shape_key_name:
        return

    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return

    if shape_key_name not in shape_key_blocks:
        return

    active_object.active_shape_key_index = shape_key_blocks.find(shape_key_name)


def blendshape_exists(active_object, blendshape_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return False

    return blendshape_name in shape_key_blocks


def get_previous_shape_key_name(active_object, blendshape_name):
    shape_key_names = get_shape_key_names(active_object)

    for index, current_name in enumerate(shape_key_names):
        if current_name == blendshape_name:
            if index == 0:
                return None

            return shape_key_names[index - 1]

    return None


def get_last_shape_key_name(active_object):
    shape_key_names = get_shape_key_names(active_object)

    if not shape_key_names:
        return None

    return shape_key_names[-1]


def sort_shape_keys(active_object):
    shape_key_blocks = get_shape_key_blocks(active_object)
    if shape_key_blocks is None:
        return

    shape_key_names = [shape_key.name for shape_key in shape_key_blocks]
    if not shape_key_names:
        return

    basis_name = "Basis"
    has_basis = basis_name in shape_key_names

    preset_order = []
    for preset in presets.BLENDSHAPE_PRESETS:
        for blendshape_name in preset["blendshapes"]:
            if blendshape_name in shape_key_names:
                preset_order.append(blendshape_name)

    remaining_names = [
        name
        for name in shape_key_names
        if name != basis_name and name not in preset_order
    ]

    desired_order = []
    if has_basis:
        desired_order.append(basis_name)
    desired_order.extend(preset_order)
    desired_order.extend(remaining_names)

    if shape_key_names == desired_order:
        return

    original_active_shape_key = get_active_shape_key_name(active_object)

    for target_index, shape_key_name in enumerate(desired_order):
        current_index = shape_key_blocks.find(shape_key_name)

        if current_index < 0 or current_index == target_index:
            continue

        move_shape_key_to_index(active_object, shape_key_name, target_index)

    set_active_shape_key(active_object, original_active_shape_key)


def has_user_blendshapes(active_object):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return False

    for shape_key in shape_key_blocks:
        if shape_key.name != "Basis":
            return True

    return False


def get_empty_separator_name(active_object):
    empty_separator_name = " "

    while blendshape_exists(active_object, empty_separator_name):
        empty_separator_name += " "

    return empty_separator_name


def move_shape_key_one_step(active_object, shape_key_name, move_type):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return False

    shape_key_index = shape_key_blocks.find(shape_key_name)

    if shape_key_index < 0:
        return False

    active_object.active_shape_key_index = shape_key_index
    original_active_object = bpy.context.view_layer.objects.active

    try:
        bpy.context.view_layer.objects.active = active_object

        with bpy.context.temp_override(
            object=active_object,
            active_object=active_object,
            selected_objects=[active_object],
            selected_editable_objects=[active_object],
        ):
            result = bpy.ops.object.shape_key_move(type=move_type)
    finally:
        bpy.context.view_layer.objects.active = original_active_object

    return result == {'FINISHED'}


def move_shape_key_to_index(active_object, shape_key_name, target_index):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return False

    current_index = shape_key_blocks.find(shape_key_name)

    if current_index < 0 or target_index < 0:
        return False

    while current_index > target_index:
        if not move_shape_key_one_step(active_object, shape_key_name, 'UP'):
            return False

        current_index = shape_key_blocks.find(shape_key_name)

    while current_index < target_index:
        if not move_shape_key_one_step(active_object, shape_key_name, 'DOWN'):
            return False

        current_index = shape_key_blocks.find(shape_key_name)

    return True


def move_shape_key_just_after(active_object, shape_key_name, anchor_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return False

    original_active_name = get_active_shape_key_name(active_object)

    try:
        current_index = shape_key_blocks.find(shape_key_name)

        if current_index < 0:
            return False

        if anchor_name is None:
            return move_shape_key_to_index(active_object, shape_key_name, 1)

        while current_index > 1:
            previous_name = shape_key_blocks[current_index - 1].name

            if previous_name == anchor_name:
                return True

            if not move_shape_key_one_step(active_object, shape_key_name, 'UP'):
                return False

            current_index = shape_key_blocks.find(shape_key_name)

        return False
    finally:
        set_active_shape_key(active_object, original_active_name)


def move_shape_key_after(active_object, shape_key_name, anchor_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return False

    original_active_name = get_active_shape_key_name(active_object)

    try:
        current_index = shape_key_blocks.find(shape_key_name)

        if current_index < 0:
            return False

        if anchor_name is None:
            target_index = 1
        else:
            anchor_index = shape_key_blocks.find(anchor_name)

            if anchor_index < 0:
                target_index = 1
            else:
                target_index = anchor_index + 1

        return move_shape_key_to_index(active_object, shape_key_name, target_index)
    finally:
        set_active_shape_key(active_object, original_active_name)


def count_existing_blendshapes(active_object, blendshape_names):
    existing_count = 0

    for blendshape_name in blendshape_names:
        if blendshape_exists(active_object, blendshape_name):
            existing_count += 1

    return existing_count


def calculate_status(existing_count, total_count):
    if total_count == 0:
        return STATUS_RED

    if existing_count == total_count:
        return STATUS_GREEN

    if existing_count > 0:
        return STATUS_YELLOW

    return STATUS_RED


def calculate_preset_status(active_object, preset):
    blendshape_names = preset["blendshapes"]
    total_count = len(blendshape_names)
    existing_count = count_existing_blendshapes(active_object, blendshape_names)
    status = calculate_status(existing_count, total_count)

    return status, existing_count, total_count


def calculate_blendshape_status(active_object, blendshape_name):
    if blendshape_exists(active_object, blendshape_name):
        return STATUS_GREEN

    return STATUS_RED


def ensure_basis_shape_key(active_object):
    if get_shape_keys(active_object) is not None:
        return

    active_object.shape_key_add(name="Basis", from_mix=False)


def create_blendshape(active_object, blendshape_name, insert_after_name=None):
    if blendshape_exists(active_object, blendshape_name):
        return False

    original_active_name = get_active_shape_key_name(active_object)

    ensure_basis_shape_key(active_object)

    if insert_after_name and blendshape_exists(active_object, insert_after_name):
        set_active_shape_key(active_object, insert_after_name)

    shape_key = active_object.shape_key_add(name=blendshape_name, from_mix=False)
    shape_key.value = 0.0
    move_shape_key_just_after(active_object, blendshape_name, insert_after_name)
    set_active_shape_key(active_object, original_active_name)

    return True


def create_separator(active_object, separator_name, insert_after_name=None):
    if not separator_name:
        return False

    formatted_separator_name = format_separator_name(separator_name)

    if blendshape_exists(active_object, formatted_separator_name):
        return 0

    created_count = 0

    if has_user_blendshapes(active_object):
        empty_separator_name = get_empty_separator_name(active_object)

        if create_blendshape(
            active_object,
            empty_separator_name,
            insert_after_name=insert_after_name,
        ):
            created_count += 1
            insert_after_name = empty_separator_name

    if create_blendshape(
        active_object,
        formatted_separator_name,
        insert_after_name=insert_after_name,
    ):
        created_count += 1

    return created_count


def create_missing_blendshapes(active_object, preset, blendshape_names):
    created_count = 0
    separator_name = preset["separator"]
    preset_blendshape_names = preset["blendshapes"]
    selected_blendshape_names = set(blendshape_names)
    formatted_separator_name = (
        format_separator_name(separator_name)
        if separator_name
        else None
    )
    previous_blendshape_name = None

    if blendshape_names and separator_name:
        if not blendshape_exists(active_object, formatted_separator_name):
            first_existing_blendshape_name = None

            for blendshape_name in preset_blendshape_names:
                if blendshape_exists(active_object, blendshape_name):
                    first_existing_blendshape_name = blendshape_name
                    break

            if first_existing_blendshape_name is None:
                insert_after_name = get_last_shape_key_name(active_object)
            else:
                insert_after_name = get_previous_shape_key_name(
                    active_object,
                    first_existing_blendshape_name,
                )

            created_count += create_separator(
                active_object,
                separator_name,
                insert_after_name=insert_after_name,
            )

        previous_blendshape_name = formatted_separator_name

    for blendshape_name in preset_blendshape_names:
        if blendshape_exists(active_object, blendshape_name):
            previous_blendshape_name = blendshape_name
            continue

        if blendshape_name not in selected_blendshape_names:
            continue

        if create_blendshape(
            active_object,
            blendshape_name,
            insert_after_name=previous_blendshape_name,
        ):
            created_count += 1
            previous_blendshape_name = blendshape_name

    return created_count
