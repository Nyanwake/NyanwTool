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
    shape_keys = getattr(active_object.data, "shape_keys", None)

    if shape_keys is None:
        return None

    return shape_keys.key_blocks


def get_active_blendshape(active_object):
    active_shape_key = active_object.active_shape_key

    if active_shape_key is None:
        return None

    if active_shape_key.name == "Basis":
        return None

    return active_shape_key


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
    base_name = "__NyanwToolTempMirror"
    temp_name = base_name
    suffix = 1

    shape_key_blocks = get_shape_key_blocks(active_object)

    while temp_name in shape_key_blocks:
        temp_name = f"{base_name}_{suffix}"
        suffix += 1

    return temp_name


def create_shape_key_from_source(active_object, source_name, new_shape_key_name, insert_after_name=None):
    shape_key_blocks = get_shape_key_blocks(active_object)
    original_values = get_blendshape_values(shape_key_blocks)

    try:
        shape_key_blocks = get_shape_key_blocks(active_object)
        clear_blendshape_values(shape_key_blocks)
        shape_key_blocks[source_name].value = 1.0

        if insert_after_name and insert_after_name in shape_key_blocks:
            shape_sets.set_active_shape_key(active_object, insert_after_name)

        new_shape_key = active_object.shape_key_add(
            name=new_shape_key_name,
            from_mix=True,
        )
        new_shape_key.value = 0.0
        shape_key_blocks = get_shape_key_blocks(active_object)
        shape_sets.move_shape_key_after(
            active_object,
            new_shape_key_name,
            insert_after_name,
        )
        active_object.active_shape_key_index = shape_key_blocks.find(new_shape_key_name)
        return new_shape_key
    finally:
        shape_key_blocks = get_shape_key_blocks(active_object)
        restore_blendshape_values(shape_key_blocks, original_values)


def remove_temp_blendshape(active_object, temp_shape_key_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return

    if temp_shape_key_name not in shape_key_blocks:
        return

    active_object.active_shape_key_index = shape_key_blocks.find(temp_shape_key_name)
    active_object.shape_key_remove(active_object.active_shape_key)


def create_mirrored_blendshape(active_object, source_name, destination_name):
    shape_key_blocks = get_shape_key_blocks(active_object)
    original_active_name = active_object.active_shape_key.name
    original_values = get_blendshape_values(shape_key_blocks)
    original_active_object = bpy.context.view_layer.objects.active

    try:
        if destination_name in shape_key_blocks:
            temp_name = get_unique_temp_blendshape_name(active_object)
            temp_shape_key = create_shape_key_from_source(
                active_object,
                source_name,
                temp_name,
                insert_after_name=source_name,
            )

            shape_key_blocks = get_shape_key_blocks(active_object)
            copy_shape_key_coordinates(
                temp_shape_key,
                shape_key_blocks[destination_name],
            )
            remove_temp_blendshape(active_object, temp_name)
        else:
            create_shape_key_from_source(
                active_object,
                source_name,
                destination_name,
                insert_after_name=source_name,
            )

        shape_key_blocks = get_shape_key_blocks(active_object)
        active_object.active_shape_key_index = shape_key_blocks.find(destination_name)
        bpy.context.view_layer.objects.active = active_object

        with bpy.context.temp_override(
            object=active_object,
            active_object=active_object,
        ):
            bpy.ops.object.shape_key_mirror(use_topology=False)
    finally:
        bpy.context.view_layer.objects.active = original_active_object
        shape_key_blocks = get_shape_key_blocks(active_object)
        restore_blendshape_values(shape_key_blocks, original_values)

        if original_active_name in shape_key_blocks:
            active_object.active_shape_key_index = shape_key_blocks.find(
                original_active_name,
            )


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

        create_mirrored_blendshape(
            active_object,
            source_name,
            destination_name,
        )
        processed_pairs.add(pair_key)
        mirrored_count += 1

    return mirrored_count, skipped_count
