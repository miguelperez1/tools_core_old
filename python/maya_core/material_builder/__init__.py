import maya.cmds as cmds

from maya_core.common_tools import logger

log = logger.Logger()


def build_vraymtl(asset_data, debug=False):
    log.status = debug

    errors = []
    if not asset_data.has_key("name"):
        errors.append("asset data has no name key")
    if not asset_data.has_key("assign"):
        errors.append("asset data has no assign key")
    if not asset_data.has_key("use_rough"):
        errors.append("asset data has no use_rough key")

    if len(errors) > 0:
        log.status = True
        for error in errors:
            log.error(error)
        return

    selected = cmds.ls(sl=True)
    node = asset_data['name']

    shader = cmds.shadingNode('VRayMtl', name="%s_mat" % node, asShader=True)
    log.info("Created " + shader)

    shading_group = cmds.sets(name='%s_shading_group' % shader, empty=True, renderable=True, noSurfaceShader=True)
    log.info("Created " + shading_group)

    cmds.connectAttr('{}.outColor'.format(shader), '{}.surfaceShader'.format(shading_group))

    file_nodes = []
    for key, value in asset_data.items():
        if key.endswith('_tex') and value != "":
            tex = cmds.shadingNode('file', name='{0}_{1}'.format(asset_data['name'], key), asTexture=True,
                                   isColorManaged=True)

            log.info("Created " + tex)

            cc_node = cmds.shadingNode("colorCorrect", n="{}_ccNode".format(key), asUtility=True)

            log.info("Created " + cc_node)

            cmds.connectAttr("{}.colGammaX".format(cc_node), "{}.colGammaY".format(cc_node))
            cmds.connectAttr("{}.colGammaX".format(cc_node), "{}.colGammaZ".format(cc_node))

            cmds.connectAttr("{}.outColor".format(tex), "{}.inColor".format(cc_node))

            # Diffuse
            if key.startswith('diffuse'):
                cmds.connectAttr('{}.outColor'.format(cc_node), '{}.color'.format(shader))

            # Specular
            if key.startswith('specular'):
                cmds.connectAttr('{}.outColor'.format(cc_node), '{}.reflectionColor'.format(shader))

            # Metallic
            if key.startswith('metallic'):
                cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(tex), 1)
                cmds.setAttr('{}.colorSpace'.format(tex), 'Raw', type='string')
                cmds.connectAttr('{}.outColor.outColorR'.format(cc_node), '{}.metalness'.format(shader))

            # Normal
            if key.startswith('normal'):
                cmds.setAttr('{}.bumpMapType'.format(shader), 4)
                cmds.setAttr('{}.bumpMult'.format(shader), .5)
                cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(tex), 1)
                cmds.setAttr('{}.colorSpace'.format(tex), 'Raw', type='string')
                cmds.connectAttr('{}.outColor'.format(cc_node), '{}.bumpMap'.format(shader))

            # Roughness / Gloss
            if key.startswith('roughness') or key.startswith("gloss"):
                cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(tex), 1)
                cmds.setAttr('{}.colorSpace'.format(tex), 'Raw', type='string')
                cmds.connectAttr('{}.outColor.outColorR'.format(cc_node), '{}.reflectionGlossiness'.format(shader))

                if asset_data['use_rough']:
                    cmds.setAttr("{}.useRoughness".format(shader), 1)

            # opacity
            if key.startswith('opacity'):
                cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(tex), 1)
                cmds.setAttr('{}.colorSpace'.format(tex), 'Raw', type='string')
                cmds.connectAttr('{}.outColor'.format(cc_node), '{}.opacityMap'.format(shader))

            # Displacement
            if key.startswith('displacement'):
                continue
                disp_node = cmds.createNode('displacementShader', n='{}_displacementShader'.format(node))
                cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(tex), 1)
                cmds.setAttr('{}.colorSpace'.format(tex), 'Raw', type='string')
                cmds.connectAttr('{}.outColor.outColorR'.format(tex), '{}.displacement'.format(disp_node))
                cmds.connectAttr('{}.displacement'.format(disp_node), '{}.displacementShader'.format(shading_group))
                cmds.vray("addAttributesFromGroup", tex, "vray_file_allow_neg_colors", 1)
                cmds.setAttr('{}.vrayFileAllowNegColors'.format(tex), 1)

            cmds.setAttr('{}.fileTextureName'.format(tex), value, type='string')
            file_nodes.append(tex)

    uv_node = cmds.shadingNode("place2dTexture", name='{}_place2d'.format(node), asUtility=True)

    message = "Created " + shader

    for texture in file_nodes:
        cmds.connectAttr('{}.outUV'.format(uv_node), '{}.uvCoord'.format(texture))

    if asset_data["assign"]:
        cmds.sets(selected, e=True, forceElement=shading_group)

        message += ", assigned to {} ".format(" ".join(selected))

    log.result(message + "successfully")

    return shading_group
