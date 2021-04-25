import os
import sys
import subprocess

from shutil import copyfile

from maya_core.common_tools import yaml_reader

# TO DO
# ACES Convert

class Asset():
    def __init__(self, asset_name, asset_type, asset_tmp_def):
        self.name = asset_name
        self.asset_type = asset_type
        self.asset_tmp_definition = asset_tmp_def
        self.asset_build_data = yaml_reader.read_yaml(self.asset_tmp_definition).get("{}_asset".format(self.name))

        self.asset_root_path = r'F:\share\assets\libraries\{0}\{1}_root'.format(self.asset_type, self.name)
        self.model_dir_path = self.asset_root_path + "\\model"
        self.maya_dir_path = self.asset_root_path + "\\maya"
        self.houdini_dir_path = self.asset_root_path + "\\houdini"
        self.material_dir_path = self.asset_root_path + "\\material"
        self.textures_dir_path = self.asset_root_path + "\\material\\textures"

        self.asset_dirs = [self.asset_root_path,
                           self.model_dir_path,
                           self.maya_dir_path,
                           self.houdini_dir_path,
                           self.material_dir_path,
                           self.textures_dir_path]

        self.asset_defenition = self.asset_root_path + "\\{}_def.yml".format(self.name)
        self.preview = self.asset_root_path + "\\{}_preview.png".format(self.name)
        self.model_path = self.asset_root_path + "\\model\\{}_model".format(self.name)
        self.material_defenition = self.material_dir_path + "\\{}_mat.yml".format(self.name)
        self.houdini_path = self.asset_root_path + "\\houdini\\{}.hiplc".format(self.name)
        self.maya_path = self.asset_root_path + "\\maya\\{}.ma".format(self.name)
        
    def write_asset_yaml(self):
        tmp_asset_yml = open(self.asset_defenition, "a")
        tmp_asset_yml.write("{}_asset: \n".format(self.name))
        tmp_asset_yml.write("    name: {}\n".format(self.name))
        tmp_asset_yml.write("    type: {}\n".format(self.asset_type))
        tmp_asset_yml.write("    library: {}\n".format(self.asset_build_data.get('library')))
        tmp_asset_yml.write("    preview: {}\n".format(self.asset_build_data.get('preview')))
        tmp_asset_yml.write("    model: {}\n".format(self.model_path))
        tmp_asset_yml.write("    scale: {}\n".format(self.asset_build_data.get('scale')))
        tmp_asset_yml.write("    material_type: {}\n".format(self.asset_build_data.get('material_type')))
        tmp_asset_yml.write("    maya_path: {}\n".format(self.maya_path))
        tmp_asset_yml.write("    houdini_path: {}\n".format(self.houdini_path))
        tmp_asset_yml.write("    roughness_invert: {}\n".format(self.asset_build_data.get('rougness_invert')))
        tmp_asset_yml.close()

    def create_dirs(self):
        for path in self.asset_dirs:
            os.mkdir(path)

    def build_material(self):
        tmp_asset_yml = open(self.asset_defenition, "a")
        for tex_type, path in self.asset_build_data.items():
            if tex_type.endswith('_tex'):
                if path is not None:
                    tex_src= path
                    tex_out = self.textures_dir_path + "\\{0}_{1}.{2}".format(self.name, tex_type, tex_src[-3:])
                    copyfile(tex_src, tex_out)
                    tmp_asset_yml.write("    {0}: {1}\n".format(tex_type, tex_out))
                else:
                    tmp_asset_yml.write("    {0}:\n".format(tex_type))
            else:
                pass
        tmp_asset_yml.close()

    def build_model(self):
        model_src = self.asset_build_data.get('model')
        model_out = self.model_path + model_src[-4:]
        self.model_path = model_out
        copyfile(model_src, model_out)
        pass

    def build_maya(self):
        function = r'F:\share\tools\core\maya_core\asset_builder\maya_builder.py'
        arg = '{}'.format(self.asset_defenition)
        subprocess.call(['mayapy', function, arg])
        pass

    def build_houdini(self):
        pass

    def copy_preview(self):
        if self.asset_build_data.get('preview') is not None:
            preview_out = self.asset_root_path + "\\{0}_preview.{1}".format(self.name, self.asset_build_data.get('preview')[-3:])
            preview_src = self.asset_build_data.get('preview')
            copyfile(preview_src, preview_out)
        else:
            return
            
    def create_asset(self):
        self.create_dirs()
        
        if self.asset_type == 'model':
            self.build_model()
        else:
            pass
            
        self.write_asset_yaml()
        self.build_material()
            
        self.build_maya()
        
        self.copy_preview()
        
        # self.build_houdini()
        
        # # os.system('doskey a = cd {}'.format(self.asset_root_path))
        return self.__class__(self.name, self.asset_type, self.asset_tmp_definition)



