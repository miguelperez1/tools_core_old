import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel

from maya_core.lookdev.material_utils import material_utils

reload(material_utils)


def create_vray_light(light_type, name=None, texture=None):
    trans = cmds.createNode('transform')
    trans_node = pm.PyNode(trans)

    lgt = cmds.shadingNode(light_type, n=trans + "Shape", p=trans, asLight=True)
    light_node = pm.PyNode(lgt)

    mel.eval('sets -edit -forceElement  defaultLightSet {} ;'.format(lgt))

    light_node.invisible.set(1)

    if name:
        light_node.rename(name + "Shape")
        trans_node.rename(name)

    if texture:
        tex_nodes = material_utils.create_texture(name=name, path=texture)
        texture_node = tex_nodes['texture_node']
        cc_node = tex_nodes['cc_node']
        uv_node = tex_nodes['uv_node']

        if light_type == "VRayLightDomeShape":
            env_node = pm.shadingNode("VRayPlaceEnvTex", asUtility=True)
            env_node.mappingType.set(2)
            env_node.useTransform.set(1)

            pm.disconnectAttr(uv_node.outUV, texture_node.uvCoord)

            pm.connectAttr(env_node.outUV, texture_node.uvCoord)
            pm.connectAttr(uv_node.uvCoord, env_node.outUV)

            light_node.useDomeTex.set(1)
            light_node.viewportTexEnable.set(0)

            pm.connectAttr(cc_node.outColor, light_node.domeTex)

            pm.connectAttr(trans_node.worldMatrix, env_node.transform)

            if name:
                env_node.rename(name + "_ENV")

        elif light_type == "VRayLightRectShape":
            light_node.useRectTex.set(1)
            pm.connectAttr(cc_node.outColor, light_node.rectTex)

        light_node.multiplyByTheLightColor.set(1)

    return light_node


def create_gobo(name, texture, directional=.975):
    gobo_light = create_vray_light("VRayLightRectShape", name, texture)
    gobo_light.directional.set(directional)
