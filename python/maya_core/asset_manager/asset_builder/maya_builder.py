import sys
import maya.standalone

maya.standalone.initialize()

import maya.cmds as cmds
import maya.mel as mel

from maya_core.common_tools import yaml_reader
from maya_core import material_builder

asset_data = {}


# TO DO
# Add translucency
# Move pivot to bottom of geo and move geo to origin

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


def move_pivot_to_bottom(obj):
    bbox = cmds.exactWorldBoundingBox(obj)
    cmds.xform(obj, ws=True, p=True, cp=True)
    center_pos = cmds.xform(obj, q=True, ws=True, sp=True)
    cmds.xform(obj, ws=True, piv=(center_pos[0], bbox[1], center_pos[2]))


def import_asset():
    if asset_data['model'].endswith('.obj'):
        cmds.file(asset_data['model'], i=True)
    elif asset_data['model'].endswith('.fbx'):
        mel.eval('loadPlugin fbxmaya')
        file_name = asset_data['model'].replace("\\", "/")
        mel.eval('FBXImport -f "{}"'.format(file_name))


def build_pxrsurface():
    pass


def build_pxrdisney():
    pass


def build_material():
    if asset_data['material_type'] == 'VRayMtl':
        return material_builder.build_vraymtl()
    elif asset_data['material_type'] == 'PxrSurface':
        return build_pxrsurface()
    elif asset_data['material_type'] == 'PxrDisney':
        return build_pxrdisney()
    elif asset_data['material_type'] == 'None':
        return None
    else:
        return None


def build_maya():
    # rename/init file
    cmds.file(rename=asset_data['maya_path'])

    # import model
    if asset_data['type'] == 'model':
        import_asset()

    cmds.select(cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True), r=True)
    selected = cmds.ls(sl=True)
    selection = cmds.ls(selection=True)
    shapes = cmds.listRelatives(selection, s=True)

    material = build_material()

    if asset_data['type'] == 'model':
        for node in selected:
            if material is not None:
                cmds.sets(node, e=True, forceElement=material[-1])
            normalize_scale(float(asset_data['scale']), node)

    for obj in cmds.ls(sl=True, type="transform"):
        move_pivot_to_bottom(obj)

        if asset_data['displacement_tex'] is not None:
            for shape in shapes:
                cmds.vray("addAttributesFromGroup", shape, "vray_subdivision", 1)
                cmds.vray("addAttributesFromGroup", shape, "vray_subquality", 1)
                cmds.vray("addAttributesFromGroup", shape, "vray_displacement", 1)
                cmds.setAttr('{}.vrayEdgeLength'.format(shape), 2)
                cmds.setAttr('{}.vrayMaxSubdivs'.format(shape), 256)
                cmds.setAttr('{}.vrayDisplacementKeepContinuity'.format(shape), 1)
                cmds.setAttr('{}.vray2dDisplacementTightBounds'.format(shape), 1)
                cmds.setAttr('{}.vrayDisplacementType'.format(shape), 0)
                cmds.setAttr('{}.vrayDisplacementAmount'.format(shape), 0.005)

        for node in selected:
            cmds.rename(node, asset_data['name'])

    # save
    cmds.file(save=True, type='mayaAscii')


if __name__ == '__main__':
    mel.eval('loadPlugin vrayformaya')
    tmp_asset_data = yaml_reader.read_yaml(sys.argv[1])
    asset_data = tmp_asset_data.get(tmp_asset_data.keys()[0])
    build_maya()
