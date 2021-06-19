import os
import glob
from collections import OrderedDict
import shutil

from maya_core.asset_manager.asset_builder import AssetBuilder
from maya_core.common_tools import logger

import json

megascans_library = r"F:\share\assets\quixel\Downloaded\3d"

log = logger.Logger()
log.status = True

def build_megascan_assets():
    assets = {}

    for dir in os.listdir(megascans_library):
        for subdir in os.listdir(os.path.join(megascans_library, dir)):
            if subdir.endswith(".json"):
                asset_data = {}

                json_file = open(os.path.join(megascans_library, dir, subdir), "r")
                asset_data = json.load(json_file)
                json_file.close()

                asset_id = asset_data["id"]

                # Check if singular mesh exists
                mesh_file = os.path.join(megascans_library, dir, "{}_LOD0.obj".format(asset_id))
                if os.path.isfile(mesh_file):
                    asset_data["mesh"] = mesh_file
                else:
                    continue

                # Get asset name
                var_num = 1
                asset_name = asset_data["semanticTags"]["name"].title().replace(" ", "_").replace(".",
                                                                                                  "_").lower() + "_var{}".format(
                    var_num)

                while asset_name in assets.keys():
                    var_num = int(asset_name[-1]) + 1
                    asset_name = "{0}_var{1}".format(asset_name.split("_var")[0], var_num)

                preview_file = os.path.join(megascans_library, dir, "{}_preview.png".format(asset_id))

                material_data = get_megascan_material(os.path.join(megascans_library, dir), asset_name, asset_id)

                asset_data = {
                    "name": asset_name,
                    "type": "model",
                    "tags": "megascans",
                    "mesh": mesh_file,
                    "preview": preview_file,
                    "material": material_data,
                    "scale": 1,
                    "has_proxy": True
                }

                assets[asset_name] = asset_data

                asset_builder = AssetBuilder.AssetBuilder(asset_data)

    ordered_assets = OrderedDict(sorted(assets.items()))

    for asset, data in ordered_assets.items():
        print (asset, data)


def get_megascan_material(path, asset_name, asset_id):
    material_data = {
        "name": asset_name,
        "mat_type": "VRayMtl",
        "use_rough": 0,
        "assign": 0,
        "create_empty": 0
    }

    diffuse_path = os.path.join(path, "{}_4K_Albedo.exr".format(asset_id))
    if os.path.isfile(diffuse_path):
        material_data["diffuse_tex"] = diffuse_path

    specular_path = os.path.join(path, "{}_4K_Specular.exr".format(asset_id))
    if os.path.isfile(specular_path):
        material_data["specular_tex"] = specular_path

    gloss_path = os.path.join(path, "{}_4K_Gloss.exr".format(asset_id))
    if os.path.isfile(gloss_path):
        material_data["gloss_tex"] = gloss_path

    normal_path = os.path.join(path, "{}_4K_Normal_LOD0.exr".format(asset_id))
    if os.path.isfile(normal_path):
        material_data["normal_tex"] = normal_path

    return material_data


def delete_existing_megascans():
    models_path = r"F:\share\assets\libraries\model"

    for dir in os.listdir(models_path):
        data_file = os.path.join(models_path, dir, "data.json")
        if os.path.isfile(data_file):
            json_file = open(data_file, "r")
            asset_data = json.load(json_file)
            json_file.close()

            if "megascans" in asset_data["tags"]:
                print "Deleting {}".format(os.path.join(models_path, dir))
                shutil.rmtree(os.path.join(models_path, dir))


def main():
    build_megascan_assets()

if __name__ == '__main__':
    main()
    # delete_existing_megascans()
