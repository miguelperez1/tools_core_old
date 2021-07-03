import os
import sys
import json

import maya.standalone as standalone

standalone.initialize(name='python')

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from maya_core.asset_manager.library_utils import constants
from maya_core.lookdev.material_utils import material_utils
from maya_core.common_tools.normalize_scale import normalize_scale

libraries = constants.libraries


def build_maya(asset_data):
    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']
    asset_root = os.path.join(libraries[asset_type], asset_name)

    mesh_node = None

    # Initialize file

    # Import mesh, scale
    if asset_type == 'model':
        if asset_data['mesh']:
            # import mesh
            cmds.file(asset_data['mesh'], i=True)

            cmds.select(cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True), r=True)

            mesh_node = pm.PyNode(cmds.ls(sl=1)[0])

            cmds.select(clear=1)

            # rename mesh
            mesh_node.rename(asset_name)

            # scale mesh
            if "scale" in asset_data.keys():
                normalize_scale.normalize_scale(asset_data['scale'], str(mesh_node))

    # Create material
    if asset_data['material_data']:

        material = material_utils.build_material(asset_data['material_data'])

        # Assign material
        if mesh_node:
            cmds.sets(str(mesh_node), e=True, forceElement=str(material[1]))

            if material[-1]:
                cmds.sets(str(mesh_node), edit=True, add=str(material[-1]))

    # Save file before creating proxy nodes
    cmds.file(save=True, type="mayaAscii")

    # Create proxy
    if 'has_proxy' in asset_data.keys() and asset_data['has_proxy']:
        proxy_path = os.path.join(asset_root, "vrayproxy")
        proxy_maya_path = proxy_path + "\\{0}_vrayproxy.ma".format(asset_name)

        cmds.select(clear=True)
        pm.select(asset_name)

        # export proxy
        cmds.vrayCreateProxy(exportType=1, previewFaces=17500, dir=proxy_path, fname=asset_name + ".vrmesh",
                             overwrite=True,
                             previewType="clustering", makeBackup=True, ignoreHiddenObjects=False, vertexColorsOn=True,
                             exportHierarchy=True, includeTransformation=True)

        # deslect everything
        cmds.select(clear=True)

        # create vray_proxy nodes
        vrmesh = asset_name + "_vrmesh"
        vraymeshmtl = vrmesh + "_vraymeshmtl"
        vrproxy_path = proxy_path + "\\{}.vrmesh".format(asset_name)

        cmds.vrayCreateProxy(createProxyNode=True, node=vrmesh, existing=True,
                             dir=vrproxy_path, geomToLoad=3, newProxyNode=False)

        # assign shader
        cmds.connectAttr("{}.outColor".format(material[0]), "{}.shaders[0]".format(vraymeshmtl))
        pm.connectAttr(material[0].diffuseColor, "{}.color".format(vraymeshmtl))

        if material[-1]:
            displacement_tex_node = pm.PyNode("{}_displacement_TEX".format(asset_name))
            vraymeshmtlsg = pm.PyNode("{}_vrmesh_vraymeshmtlSG".format(asset_name))
            pm.connectAttr(displacement_tex_node.outColor, vraymeshmtlsg.displacementShader)

            vrmesh_vrdisp = material_utils.create_displacement_node(vrmesh, displacement_tex_node, pm.PyNode(vrmesh))
            print vrmesh_vrdisp

        # select vray_proxy
        cmds.select(clear=True)

        # save selection as new maya file
        pm.select(vrmesh, r=1)

        if material[-1]:
            pm.select(str(vrmesh_vrdisp), add=True, r=1, ne=1)

        pm.exportSelected(proxy_maya_path, type="mayaAscii", channels=True, force=True)


def main():
    mel.eval('loadPlugin vrayformaya')
    mel.eval('loadPlugin fbxmaya')
    mel.eval('loadPlugin objExport')

    cmds.file(f=True, new=True)

    json_file = open(sys.argv[1], "r")
    asset_data = json.load(json_file)
    json_file.close()

    cmds.file(rename=os.path.join(asset_data['import_file']))
    cmds.file(save=True, type='mayaAscii')

    build_maya(asset_data)

    if os.path.isfile(asset_data['import_file']):
        print "Built {} successfully".format(asset_data['asset_name'])


if __name__ == '__main__':
    main()
