import bpy

from . import shape_sets


LEFT_RIGHT_PAIRS = (
    ("Left", "Right"),
    ("left", "right"),
    ("LEFT", "RIGHT"),
    ("_L", "_R"),
    ("_l", "_r"),
    (".L", ".R"),
    (".l", ".r"),
    ("-L", "-R"),
    ("-l", "-r"),
    (" L", " R"),
    (" l", " r"),
)


def get_opposite_blendshape_name(blendshape_name):
    for left_name, right_name in LEFT_RIGHT_PAIRS:
        if blendshape_name.endswith(left_name):
            return blendshape_name[:-len(left_name)] + right_name

        if blendshape_name.endswith(right_name):
            return blendshape_name[:-len(right_name)] + left_name

    return None


def get_shape_key_blocks(active_object):
    return shape_sets.get_shape_key_blocks(active_object)


def get_blendshape_values(shape_key_blocks):
    blendshape_values = {}

    for shape_key in shape_key_blocks:
        blendshape_values[shape_key.name] = shape_key.value

    return blendshape_values


def restore_blendshape_values(shape_key_blocks, blendshape_values):
    for shape_key in shape_key_blocks:
        if shape_key.name in blendshape_values:
            shape_key.value = blendshape_values[shape_key.name]


def clear_blendshape_values(shape_key_blocks):
    for shape_key in shape_key_blocks:
        shape_key.value = 0.0


def copy_shape_key_coordinates(source_shape_key, destination_shape_key):
    coordinates = [0.0] * (len(source_shape_key.data) * 3)
    source_shape_key.data.foreach_get("co", coordinates)
    destination_shape_key.data.foreach_set("co", coordinates)


def get_unique_temp_blendshape_name(active_object):
    base_name = "__NyanwToolsTempMirror"
    temp_name = base_name
    suffix = 1

    shape_key_blocks = get_shape_key_blocks(active_object)

    while temp_name in shape_key_blocks:
        temp_name = f"{base_name}_{suffix}"
        suffix += 1

    return temp_name


def create_shape_key_from_source(active_object, source_name, new_shape_key_name):
    shape_key_blocks = get_shape_key_blocks(active_object)
    original_values = get_blendshape_values(shape_key_blocks)

    try:
        clear_blendshape_values(shape_key_blocks)
        shape_key_blocks[source_name].value = 1.0

        new_shape_key = active_object.shape_key_add(
            name=new_shape_key_name,
            from_mix=True,
        )
        new_shape_key.value = 0.0
        return new_shape_key
    finally:
        shape_key_blocks = get_shape_key_blocks(active_object)
        restore_blendshape_values(shape_key_blocks, original_values)


def remove_shape_key(active_object, shape_key_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return

    if shape_key_name not in shape_key_blocks:
        return

    active_object.active_shape_key_index = shape_key_blocks.find(shape_key_name)
    active_object.shape_key_remove(active_object.active_shape_key)


def mirror_shape_key(active_object, shape_key_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None or shape_key_name not in shape_key_blocks:
        return False

    original_active_object = bpy.context.view_layer.objects.active
    original_selection_values = shape_sets.get_shape_key_selection_values(active_object)

    try:
        shape_sets.select_only_shape_key(active_object, shape_key_name)
        active_object.active_shape_key_index = shape_key_blocks.find(shape_key_name)
        bpy.context.view_layer.objects.active = active_object

        with bpy.context.temp_override(
            object=active_object,
            active_object=active_object,
            selected_objects=[active_object],
            selected_editable_objects=[active_object],
        ):
            result = bpy.ops.object.shape_key_mirror(use_topology=False)
    finally:
        shape_sets.restore_shape_key_selection(active_object, original_selection_values)
        bpy.context.view_layer.objects.active = original_active_object

    return result == {'FINISHED'}


def ensure_destination_blendshape(active_object, source_name, destination_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return None

    if destination_name not in shape_key_blocks:
        shape_sets.create_blendshape(
            active_object,
            destination_name,
            insert_after_name=source_name,
        )

    shape_key_blocks = get_shape_key_blocks(active_object)

    if destination_name not in shape_key_blocks:
        return None

    return shape_key_blocks[destination_name]


def create_mirrored_blendshape(active_object, source_name, destination_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return False

    original_active_name = shape_sets.get_active_shape_key_name(active_object)
    original_values = get_blendshape_values(shape_key_blocks)
    temp_name = get_unique_temp_blendshape_name(active_object)
    temp_shape_key = create_shape_key_from_source(
        active_object,
        source_name,
        temp_name,
    )

    try:
        if not mirror_shape_key(active_object, temp_name):
            return False

        destination_shape_key = ensure_destination_blendshape(
            active_object,
            source_name,
            destination_name,
        )

        if destination_shape_key is None:
            return False

        copy_shape_key_coordinates(temp_shape_key, destination_shape_key)
        destination_shape_key.value = 0.0
        return True
    finally:
        remove_shape_key(active_object, temp_name)
        shape_key_blocks = get_shape_key_blocks(active_object)
        restore_blendshape_values(shape_key_blocks, original_values)
        shape_sets.set_active_shape_key(active_object, original_active_name)


def create_mirrored_blendshapes(active_object, source_names):
    shape_key_blocks = get_shape_key_blocks(active_object)
    selected_names = set(source_names)
    processed_pairs = set()
    mirrored_count = 0
    skipped_count = 0

    if shape_key_blocks is None:
        return mirrored_count, len(source_names)

    for source_name in source_names:
        shape_key_blocks = get_shape_key_blocks(active_object)
        destination_name = get_opposite_blendshape_name(source_name)

        if destination_name is None:
            skipped_count += 1
            continue

        if source_name not in shape_key_blocks:
            skipped_count += 1
            continue

        pair_key = frozenset((source_name, destination_name))

        if pair_key in processed_pairs:
            continue

        if destination_name in selected_names:
            processed_pairs.add(pair_key)
            skipped_count += 2
            continue

        if create_mirrored_blendshape(
            active_object,
            source_name,
            destination_name,
        ):
            mirrored_count += 1
        else:
            skipped_count += 1

        processed_pairs.add(pair_key)

    return mirrored_count, skipped_count
