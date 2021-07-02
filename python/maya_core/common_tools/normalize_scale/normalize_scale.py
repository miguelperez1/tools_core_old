import maya.cmds as cmds


def normalize_scale(size, object_b):
    b_bbox = cmds.exactWorldBoundingBox(object_b)

    b_y_size = b_bbox[4] - b_bbox[1]

    ratio = size / b_y_size

    b_scale_x = cmds.getAttr('{}.scaleX'.format(object_b))
    b_scale_y = cmds.getAttr('{}.scaleY'.format(object_b))
    b_scale_z = cmds.getAttr('{}.scaleZ'.format(object_b))

    cmds.setAttr('{}.scaleX'.format(object_b), (b_scale_x * ratio))
    cmds.setAttr('{}.scaleY'.format(object_b), (b_scale_y * ratio))
    cmds.setAttr('{}.scaleZ'.format(object_b), (b_scale_z * ratio))
    cmds.makeIdentity(object_b, apply=True, t=1, r=1, s=1, n=0)