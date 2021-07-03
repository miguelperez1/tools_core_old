import os

import pymel.core as pm
import maya.cmds as cmds

TEX_TYPES = [
    'diffuse',
    'si',
    'specular',
    'gloss',
    'metal',
    'normal',
    'opacity',
    'displacement'
]

DEFAULT_CONNECTIONS = {
    'VRayMtl': {
        'diffuse': 'outColor.color',
        'specular': 'outColor.reflectionColor',
        'gloss': 'outColorR.reflectionGlossiness',
        'metal': 'outColorR.metalness',
        'opacity': 'outColor.opacityMap',
        'si': 'outColor.illumColor',
        'normal': 'outColor.bumpMap',
        'displacement': 'outColor.displacementShader',
    },
    'PxrSurface': {
        'diffuse': 'color',
        'specular': 'reflectionColor',
        'gloss': 'reflectionGlossiness',
        'normal': ''
    }
}


# Example material_data
# material_data = {
#     'name': name,
#     'material_type': material_type,
#     'textures' : {
#         'diffuse': diffuse_path
#     }


class MaterialBuilder(object):
    def __init__(self, material_data):
        self.material_data = material_data
        self.material_type = material_data['material_type']
        self.name = material_data['name']

    def build_material(self):
        build_method = getattr(self, "build_{}".format(self.material_type))

        return build_method()

    def build_VRayMtl(self):
        shader = pm.PyNode(cmds.shadingNode('VRayMtl', name=self.name + "_mat", asShader=True))
        shading_group = pm.PyNode(cmds.sets(name=str(shader).replace("_mat", "") + "_sg", empty=True, renderable=True,
                                            noSurfaceShader=True))

        pm.connectAttr(shader.outColor, shading_group.surfaceShader)

        if 'textures' not in self.material_data.keys():
            return shader, shading_group

        uv_node = pm.shadingNode("place2dTexture", asUtility=True)
        uv_node.rename(self.name + "_UV")

        displacement = None

        for tex in self.material_data['textures']:
            for tex_type, tex_path in tex.items():
                # create nodes
                connection = DEFAULT_CONNECTIONS['VRayMtl'][tex_type].split(".")

                if tex_type != "displacement":
                    tex_nodes = create_texture(name=self.name + "_" + tex_type, path=tex_path, uv=False)
                    cc_node = tex_nodes['cc_node']

                    pm.connectAttr(getattr(cc_node, connection[0]), getattr(shader, connection[1]))
                else:
                    tex_nodes = create_texture(name=self.name + "_" + tex_type, path=tex_path, cc=False, uv=False)

                    displacement = create_displacement_node(name=self.name, disp_source=tex_nodes["texture_node"])

                    pm.connectAttr(getattr(tex_nodes["texture_node"], connection[0]),
                                   getattr(shading_group, connection[1]))

                pm.connectAttr(uv_node.outUV, tex_nodes['texture_node'].uvCoord)

                # Set default values
                if tex_type == "normal":
                    shader.bumpMapType.set(1)

        return shader, shading_group, displacement

    def build_VRayMtl2Sided(self):
        shader = pm.PyNode(cmds.shadingNode('VRayMtl2Sided', name=self.name + "_2sided_mat", asShader=True))
        shading_group = pm.PyNode(cmds.sets(name=str(shader).replace("_mat", "") + "_2sided_sg", empty=True, renderable=True,
                                            noSurfaceShader=True))

        pm.connectAttr(shader.outColor, shading_group.surfaceShader)

        vray_mtl = self.build_VRayMtl()

        pm.connectAttr(vray_mtl[0].outColor, shader.frontMaterial)
        pm.connectAttr(vray_mtl[0].outColor, shader.backMaterial)

        return shader, shading_group, vray_mtl

    def build_VRayBlendMtl(self):
        print "build_VRayBlendMtl"
        return None


def create_texture(name=None, path=None, cc=True, uv=True):
    nodes = {}

    texture_node = pm.shadingNode('file', asTexture=True, isColorManaged=True)
    nodes['texture_node'] = texture_node

    if path:
        texture_node.fileTextureName.set(path)

    if uv:
        uv_node = pm.shadingNode("place2dTexture", asUtility=True)
        nodes['uv_node'] = uv_node

        pm.connectAttr(uv_node.outUV, texture_node.uvCoord)

    if cc:
        cc_node = create_cc_node(texture_node)
        nodes['cc_node'] = cc_node

    if name:
        texture_node.rename(name + "_TEX")

        if uv:
            uv_node.rename(name + "_UV")

        if cc:
            cc_node.rename(name + "_CC")

    return nodes


def create_cc_node(source_node):
    if not isinstance(source_node, pm.PyNode):
        source_node = pm.PyNode(source_node)

    # Store original outcolor connections
    out_connections = pm.listConnections(source_node, connections=True, plugs=True)

    # Create CC Node
    cc_node = pm.shadingNode('colorCorrect', n=source_node + "_CC", asUtility=True)

    # Connect file to cc
    pm.connectAttr(source_node.outColor, cc_node.inColor)
    pm.connectAttr(source_node.outAlpha, cc_node.inAlpha)

    # Connect gamma attributes
    pm.connectAttr(cc_node.colGammaX, cc_node.colGammaY)
    pm.connectAttr(cc_node.colGammaX, cc_node.colGammaZ)

    # Connect cc to original connections
    for connection_pair in out_connections:
        out_attr = connection_pair[0].split(".")[-1]
        if out_attr.startswith("outColor") or out_attr == "outAlpha":
            source_connection = connection_pair[0].split(".")[-1]
            target_connection = connection_pair[-1]
            pm.connectAttr(cc_node + "." + source_connection, target_connection, f=True)

    return cc_node


def create_displacement_node(name=None, disp_source=None, obj=None):
    disp_node = pm.createNode("VRayDisplacement")
    cmds.vray("addAttributesFromGroup", str(disp_node), "vray_subdivision", 1)
    cmds.vray("addAttributesFromGroup", str(disp_node), "vray_subquality", 1)
    cmds.vray("addAttributesFromGroup", str(disp_node), "vray_displacement", 1)
    disp_node.overrideGlobalDisplacement.set(1)
    disp_node.vrayEdgeLength.set(1)
    disp_node.vrayMaxSubdivs.set(128)
    disp_node.vrayDisplacementShift.set(-0.5)

    if name:
        disp_node.rename(name + "_vrdisp")

    if disp_source:
        pm.connectAttr(disp_source.outColor, disp_node.displacement)

    if obj:
        cmds.sets(str(obj), edit=True, add=str(disp_node))

    return disp_node


def build_material(material_data):
    mb = MaterialBuilder(material_data)

    return mb.build_material()
