import pymel.core as pm


def normalize_scale(scale, node, axis=None, skip_axis=None):
    if isinstance(node, str):
        node = pm.PyNode(node)

    object_bbox = pm.exactWorldBoundingBox(node)

    axes = ['x', 'y', 'z']

    if axis is not None:
        a_index = axes.index(axis)
        bbox_axis_size = object_bbox[a_index + 3] - object_bbox[a_index]
        ratio = float(scale) / float(bbox_axis_size)
    else:
        bbox_axis_size = get_longest_axis(node, skip_axis)
        ratio = float(scale) / float(bbox_axis_size[0])

    for axis in axes:
        object_axis_scale = getattr(node, "scale{}".format(axis.upper())).get()
        getattr(node, "scale{}".format(axis.upper())).set(object_axis_scale * ratio)

    pm.makeIdentity(node, apply=True, t=1, r=1, s=1, n=0)


def get_longest_axis(node, skip_axis=None):
    object_bbox = pm.exactWorldBoundingBox(node)

    axes = ['x', 'y', 'z']

    if skip_axis is not None:
        axes.remove(skip_axis)

    axes_sizes = []

    for i, axis in enumerate(axes):
        bbox_axis_size = object_bbox[i + 3] - object_bbox[i]
        axes_sizes.append((bbox_axis_size, axis))

    return sorted(axes_sizes)[-1]
