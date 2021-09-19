import os
import json
import subprocess
from shutil import copyfile

from maya_core.asset_manager.library_utils import constants
# from maya_core.asset_manager.library_utils import library_utils
from maya_core.common_tools.maya_utilities import maya_utilities
from maya_core.lookdev.material_utils import material_utils

import pymel.core as pm
import maya.cmds as cmds

LIBRARIES = constants.libraries


# Example asset data structure
# asset_data = {
#     'name': '',
#     'asset_type': 'model',
#     'preview': None,
#     'tags': 'megascans',
#     'mesh': None,
#     'material_data': None,
#     'scale': 1,
#     'has_proxy': 1
# }
#
# {
#     "asset_name": "bike_stand_var1",
#     "asset_type": "model",
#     "has_proxy": 1,
#     "import_file": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\maya\\bike_stand_var1.ma",
#     "material_data": {
#         "material_type": "VRayMtl",
#         "name": "bike_stand_var1",
#         "textures": [
#             {
#                 "diffuse": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\material\\bike_stand_var1\\textures\\uhcgehnfa_4K_Albedo.exr"
#             },
#             {
#                 "specular": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\material\\bike_stand_var1\\textures\\uhcgehnfa_4K_Specular.exr"
#             },
#             {
#                 "gloss": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\material\\bike_stand_var1\\textures\\uhcgehnfa_4K_Gloss.exr"
#             },
#             {
#                 "normal": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\material\\bike_stand_var1\\textures\\uhcgehnfa_4K_Normal_LOD0.exr"
#             },
#             {
#                 "displacement": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\material\\bike_stand_var1\\textures\\uhcgehnfa_4K_Displacement.exr"
#             }
#         ]
#     },
#     "mesh": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\mesh\\uhcgehnfa_LOD0.obj",
#     "preview": "F:\\share\\assets\\libraries\\model\\bike_stand_var1\\bike_stand_var1_preview.png",
#     "scale": 2.7552,
#     "tags": "megascans,city"
# }

class AssetBuilder(object):
    def __init__(self, asset_data, build_maya=False):
        super(AssetBuilder, self).__init__()
        self.asset_data = asset_data
        self.name = asset_data['name']
        self.asset_type = asset_data['asset_type']

        if 'asset_preview' in self.asset_data.keys():
            self.preview_src = asset_data['asset_preview']

        self.build_maya_file = build_maya

        self.asset_root = os.path.join(LIBRARIES[self.asset_type], self.name)
        self.json_path = os.path.join(self.asset_root, "data.json")
        self.maya_dir = os.path.join(self.asset_root, "maya")
        self.maya_file = os.path.join(self.maya_dir, "{}.ma".format(self.name))
        self.material_dir = os.path.join(self.asset_root, "material")

        self.publish_data = {
            'asset_name': self.name,
            "asset_type": self.asset_type,
            "import_file": self.maya_file
        }

        if 'tags' in self.asset_data.keys():
            self.publish_data['tags'] = self.asset_data['tags']
        if 'scale' in self.asset_data.keys():
            self.publish_data['scale'] = self.asset_data['scale']
        if 'megascan_id' in self.asset_data.keys():
            self.publish_data['megascan_id'] = self.asset_data['megascan_id']

    def create_asset(self, save_type=None):
        import maya.cmds as cmds

        self._create_directories()
        self._copy_preview()
        self._publish_material()
        self._copy_mesh()
        self._create_asset_json()

        if self.build_maya_file:
            self._build_maya()

        if save_type == "file":
            cmds.file(rename=self.maya_file)
            cmds.file(save=True, force=True, type="mayaAscii")
        elif save_type == "selection":
            cmds.select(clear=1)
            cmds.select(self.name)
            cmds.file(self.maya_file, es=True, type="mayaAscii", force=True)

        # library_utils.build_library_jsons()

    def _create_directories(self):
        os.mkdir(self.asset_root)
        os.mkdir(os.path.join(self.asset_root, "build_log"))

        self.maya_dir = os.path.join(self.asset_root, "maya")
        os.mkdir(self.maya_dir)

        os.mkdir(self.material_dir)

        if 'material_data' in self.asset_data.keys() and self.asset_data['material_data']:
            mat_dir = os.path.join(self.asset_root, "material", self.asset_data['material_data']['name'])
            os.mkdir(mat_dir)

            textures_dir = os.path.join(mat_dir, "textures")
            os.mkdir(textures_dir)

        if 'has_proxy' in self.asset_data.keys() and self.asset_data['has_proxy']:
            self.publish_data['has_proxy'] = self.asset_data['has_proxy']
            os.mkdir(os.path.join(self.asset_root, 'vrayproxy'))

        if 'mesh' in self.asset_data.keys() and self.asset_data['mesh']:
            os.mkdir(os.path.join(self.asset_root, 'mesh'))

    def _create_asset_json(self):
        with open(self.json_path, "w") as f:
            json.dump(self.publish_data, f, indent=4)

    def _publish_material(self):
        if 'material_data' in self.asset_data.keys() and self.asset_data['material_data']:
            material_data = self.asset_data['material_data']

            publish_material_data = {
                'name': self.name,
                'material_type': material_data['material_type'],
                'textures': {}
            }

            textures = {}
            for tex_data in material_data['textures'].items():
                tex_type = tex_data[0]
                texture = tex_data[1]['path']
                src_tex = texture.replace("/", "\\")
                dst_tex = os.path.join(self.material_dir, src_tex.split("\\")[-1])

                if not os.path.isfile(src_tex):
                    print(src_tex + " does not exist, skipping copying image")
                    continue

                if src_tex == dst_tex:
                    print("source and destination image are the same, skipping copying image")
                    continue

                try:
                    copyfile(src_tex, dst_tex)
                except Exception as e:
                    print(e)

                # TODO fix this ptex check
                textures[tex_type] = {
                    'path': dst_tex,
                    'use_ptex': False
                }

            publish_material_data['textures'] = textures

            self.publish_data['material_data'] = publish_material_data

    def _copy_preview(self):
        if 'asset_preview' in self.asset_data.keys() and self.asset_data['asset_preview']:
            src_preview = self.asset_data['asset_preview']
            preview_name = "{0}_preview.png".format(self.name)
            dst_preview = os.path.join(self.asset_root, preview_name)

            self.publish_data['asset_preview'] = dst_preview

            copyfile(src_preview, dst_preview)

    def _copy_mesh(self):
        if 'mesh' in self.asset_data.keys() and self.asset_data['mesh']:
            src_mesh = self.asset_data['mesh']
            dst_mesh = os.path.join(self.asset_root, "mesh", src_mesh.split("\\")[-1])
            copyfile(src_mesh, dst_mesh)

            self.publish_data['mesh'] = dst_mesh

    def _build_maya(self):
        function = r'F:\share\tools\tools_core\python\maya_core\asset_manager\asset_builder\maya_builder.py'

        arg = '{}'.format(self.json_path)

        log_path = os.path.join(self.asset_root, "build_log", "build_log.txt")
        f = open(log_path, "w")

        print("running mayapy process for {}".format(self.name))

        subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)

    def publish_textures(self, texture_data=None):
        if not texture_data:
            materials = maya_utilities.get_all_materials()
            for material in materials:
                texs_tmp = maya_utilities.filter_connected_nodes(material, "file")
                texs_tmp.extend(maya_utilities.filter_connected_nodes(material, "VRayPtex"))

                if texs_tmp:
                    texture_data[material] = texs_tmp

        if not texture_data.keys():
            return

        for material, textures in texture_data.items():
            for texture in textures:
                ptex = False
                if texture.nodeType == "VRayPtex":
                    ptex = True

                if not ptex:
                    src = texture.fileTextureName.get().replace("\\", "/")
                else:
                    src = texture.ptexFile.get().replace("\\", "/")
                dst_root = os.path.join(self.material_dir, str(material))

                if not os.path.isdir(dst_root):
                    os.mkdir(dst_root)

                dst = os.path.join(dst_root, src.split("/")[-1])

                try:
                    copyfile(src, dst)
                except Exception as e:
                    print(e)
                    continue

                if not ptex:
                    texture.fileTextureName.set(dst)
                else:
                    texture.ptexFile.set(dst)

    def repath_textures(self):
        materials = maya_utilities.get_all_materials()

        for material in materials:
            texs = maya_utilities.filter_connected_nodes(material, "file")
            texs.extend(maya_utilities.filter_connected_nodes(material, "VRayPtex"))

            for tex in texs:
                ptex = False
                if tex.nodeType() == "VRayPtex":
                    ptex = True

                if not ptex:
                    file_name = tex.fileTextureName.get().replace("\\", "/").split("/")[-1]
                else:
                    file_name = tex.ptexFile.get().replace("\\", "/").split("/")[-1]

                dst = os.path.join(self.material_dir, str(material), file_name)

                if os.path.isfile(dst):
                    print("repathed: {}".format(dst))
                    if not ptex:
                        tex.fileTextureName.set(dst)
                    else:
                        tex.ptexFile.set(dst)
                else:
                    dst = os.path.join(self.material_dir, "textures", file_name)

                    if os.path.isfile(dst):
                        print("repathed: {}".format(dst))

                        if not ptex:
                            tex.fileTextureName.set(dst)
                        else:
                            tex.ptexFile.set(dst)

    def export_proxy(self):
        # Create proxy
        world_node = pm.PyNode(self.name)

        proxy_path = os.path.join(self.asset_root, "vrayproxy")
        proxy_maya_path = proxy_path + "\\{0}_vrayproxy.ma".format(self.name)

        cmds.select(clear=True)
        pm.select(self.name)

        # export proxy
        cmds.vrayCreateProxy(exportType=1, previewFaces=17500, dir=proxy_path, fname=self.name + ".vrmesh",
                             overwrite=True,
                             previewType="clustering", makeBackup=True, ignoreHiddenObjects=False,
                             vertexColorsOn=True,
                             exportHierarchy=True, includeTransformation=True)

        # deslect everything
        cmds.select(clear=True)

        # create vray_proxy nodes
        vrmesh = self.name + "_vrmesh"
        vraymeshmtl = vrmesh + "_vraymeshmtl"
        vrproxy_path = proxy_path + "\\{}.vrmesh".format(self.name)
        vrmesh_vrdisp = None

        cmds.vrayCreateProxy(createProxyNode=True, node=vrmesh, existing=True,
                             dir=vrproxy_path, geomToLoad=3, newProxyNode=False)

        cmds.select(clear=1)
        cmds.select(self.name)

        material = [m for m in maya_utilities.get_materials_from_selection() if
                    pm.nodeType(m) in ['VRayMtl', 'VRayMtl2Sided']]

        if material:
            # assign shader
            cmds.connectAttr("{}.outColor".format(material[0]), "{}.shaders[0]".format(vraymeshmtl))

            if pm.nodeType(material[0]) == "VRayMtl":
                pm.connectAttr("{}.diffuseColor".format(material[0]), "{}.color".format(vraymeshmtl))
            elif pm.nodeType(material[0]) == "VRayMtl2Sided":
                pm.connectAttr("{}.outColor".format(material[0]), "{}.color".format(vraymeshmtl))

            sgs = pm.listConnections(world_node.getShape(), type="shadingEngine")

            if sgs:
                sg = sgs[0]

                if pm.listConnections(sg.displacementShader):
                    displacement_tex_node = pm.PyNode("{}_displacement_TEX".format(self.name))
                    vraymeshmtlsg = pm.PyNode("{}_vrmesh_vraymeshmtlSG".format(self.name))
                    pm.connectAttr(displacement_tex_node.outColor, vraymeshmtlsg.displacementShader)

                    vrmesh_vrdisp = material_utils.create_displacement_node(self.name, displacement_tex_node,
                                                                            pm.PyNode(vrmesh))

        # select vray_proxy
        cmds.select(clear=True)

        # save selection as new maya file
        pm.select(vrmesh, r=1)

        if vrmesh_vrdisp is not None:
            pm.select(str(vrmesh_vrdisp), add=True, r=1, ne=1)

        pm.exportSelected(proxy_maya_path, type="mayaAscii", channels=True, force=True)


def build_asset(asset_data, build_maya=False):
    if not asset_data:
        print("no asset data provided")
        return

    asset_builder = AssetBuilder(asset_data, build_maya=build_maya)
    asset_builder.create_asset()
