import os
import json
import subprocess
from shutil import copyfile

from maya_core.asset_manager.library_utils import constants
from maya_core.asset_manager.library_utils import library_utils

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

# Example published asset json data
# {
#     "asset_name": "icelandic_rock_assembly_var2",
#     "asset_preview": "F:\\share\\assets\\libraries\\model\\icelandic_rock_assembly_var2\\icelandic_rock_assembly_var2_preview.png",
#     "asset_type": "model",
#     "tags": "megascans,environment"
#     "material_data": material_data
# }

class AssetBuilder(object):
    def __init__(self, asset_data, build_maya_file=False):
        super(AssetBuilder, self).__init__()
        self.asset_data = asset_data
        self.name = asset_data['name']
        self.asset_type = asset_data['asset_type']

        if 'preview' in self.asset_data.keys():
            self.preview_src = asset_data['preview']

        self.build_maya_file = build_maya_file

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
            cmds.file(self.maya_file, es=True, save=True, type="mayaAscii")

        library_utils.build_library_jsons()

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
                'material_type': material_data['material_type']
            }

            textures = []
            for tex_data in material_data['textures']:
                for tex_type, texture in tex_data.items():
                    src_tex = texture.replace("/", "\\")
                    dst_tex = os.path.join(self.textures_dir, src_tex.split("\\")[-1])
                    copyfile(src_tex, dst_tex)

                    tex_data = {
                        tex_type: dst_tex
                    }

                    textures.append(tex_data)

            publish_material_data['textures'] = textures

            self.publish_data['material_data'] = publish_material_data

    def _copy_preview(self):
        if 'preview' in self.asset_data.keys() and self.asset_data['preview']:
            src_preview = self.asset_data['preview']
            preview_name = "{0}_preview.png".format(self.name)
            dst_preview = os.path.join(self.asset_root, preview_name)

            self.publish_data['preview'] = dst_preview

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

        subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)

    def publish_textures(self, materials=None):
        if materials:
            for material in materials:
                # search all connections for file nodes
                pass
        else:
            # publish from all materials in scene
            pass
        pass


def build_asset(asset_data):
    if not asset_data:
        return

    asset_builder = AssetBuilder(asset_data)
