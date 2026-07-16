from . import shape_sets


TEMP_COMBINE_NAME = "__NyanwToolsTempCombine"


def get_shape_key_blocks(active_object):
    return shape_sets.get_shape_key_blocks(active_object)


def copy_shape_key_coordinates(source_shape_key, destination_shape_key):
    coordinates = [0.0] * (len(source_shape_key.data) * 3)
    source_shape_key.data.foreach_get("co", coordinates)
    destination_shape_key.data.foreach_set("co", coordinates)


def get_unique_blendshape_name(active_object, base_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return base_name

    if base_name not in shape_key_blocks:
        return base_name

    suffix = 1

    while True:
        blendshape_name = f"{base_name}.{suffix:03d}"

        if blendshape_name not in shape_key_blocks:
            return blendshape_name

        suffix += 1


def create_shape_key_from_mix(active_object, blendshape_name):
    shape_sets.ensure_basis_shape_key(active_object)

    shape_key = active_object.shape_key_add(
        name=blendshape_name,
        from_mix=True,
    )
    shape_key.value = 0.0

    return shape_key


def remove_shape_key(active_object, blendshape_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return

    if blendshape_name not in shape_key_blocks:
        return

    active_object.active_shape_key_index = shape_key_blocks.find(blendshape_name)
    active_object.shape_key_remove(active_object.active_shape_key)


def create_new_combined_blendshape(active_object, blendshape_name):
    final_name = get_unique_blendshape_name(active_object, blendshape_name)
    create_shape_key_from_mix(active_object, final_name)

    return final_name


def get_existing_blendshape(active_object, blendshape_name):
    shape_key_blocks = get_shape_key_blocks(active_object)

    if shape_key_blocks is None:
        return None

    if blendshape_name not in shape_key_blocks:
        return None

    return shape_key_blocks[blendshape_name]


def apply_combined_blendshape_to_target(active_object, blendshape_name):
    if not blendshape_name or blendshape_name == "Basis":
        return False

    destination_shape_key = get_existing_blendshape(active_object, blendshape_name)

    if destination_shape_key is None:
        return False

    temp_name = get_unique_blendshape_name(active_object, TEMP_COMBINE_NAME)
    temp_shape_key = create_shape_key_from_mix(active_object, temp_name)

    try:
        copy_shape_key_coordinates(temp_shape_key, destination_shape_key)
        destination_shape_key.value = 0.0
        return True
    finally:
        remove_shape_key(active_object, temp_name)
