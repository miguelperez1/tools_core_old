import os
import json
from collections import OrderedDict
import shutil
import re
# import logging
#
# logger = logging.getLogger("__name__")
# logger.setLevel(10)

from maya_core.asset_manager.asset_builder import asset_builder
from maya_core.asset_manager.library_utils import constants

reload(asset_builder)

libraries = constants.libraries


def rename_root_folders():
    for library, path in libraries.items():
        if library not in ['model', 'material', 'plants', 'rigs']:
            continue

        for dir in os.listdir(path):
            old_path = os.path.join(path, dir)
            new_path = os.path.join(path, dir.replace("_root", ""))

            os.rename(old_path, new_path)

            if os.path.isdir(new_path):
                print new_path


def build_library_jsons(build_library=None):
    # library_datas = [get_library_data(library) for library in libraries.keys()]

    for library, path in libraries.items():
        if library == "root":
            continue

        if build_library and build_library != library:
            continue

        library_json = os.path.join(path, "assets.json")
        library_data = OrderedDict()

        if os.path.exists(library_json):
            json_file = open(library_json, "r")
            current_library_data = json.load(json_file)
            json_file.close()
        else:
            current_library_data = None

        tags = []

        library_data['assets'] = {}

        if library not in ['model', 'material', 'plants', 'rigs']:
            for asset in os.listdir(path):
                if os.path.isdir(os.path.join(path, asset)) or asset.endswith(".json"):
                    continue

                asset_name = asset.split(".")[0]

                preview_path = os.path.join(path, "thumbnails", "{}_preview.png".format(asset.split(".")[0]))

                asset_data = {
                    "asset_name": asset_name,
                    "asset_type": library,
                    "asset_preview": "",
                    "import_file": os.path.join(path, asset),
                }

                asset_data['tags'] = ''
                if current_library_data and asset_name in current_library_data['assets'].keys():
                    current_asset_data = current_library_data['assets'][asset_name]

                    if 'tags' in current_asset_data.keys():
                        asset_tags = current_asset_data['tags']
                        asset_data['tags'] = asset_tags
                        t = asset_data['tags'].split(",")
                        tags.extend(t)

                if os.path.isfile(preview_path):
                    asset_data["asset_preview"] = preview_path
                elif os.path.isfile(preview_path.replace(".png", ".jpg")):
                    asset_data["asset_preview"] = preview_path.replace(".png", ".jpg")

                library_data['assets'][asset_name] = asset_data
        else:
            if os.path.isfile(library_json):
                os.remove(library_json)

            for asset in os.listdir(path):
                if os.path.isfile(os.path.join(path, asset)):
                    continue

                asset_path = os.path.join(path, asset)
                asset_json_path = os.path.join(asset_path, "data.json")

                if os.path.isfile(asset_json_path):

                    json_file = open(asset_json_path, "r")
                    asset_root_data = json.load(json_file)
                    json_file.close()

                    if 'tags' in asset_root_data.keys():
                        t = asset_root_data['tags'].split(",")
                        tags.extend(t)

                library_data['assets'][asset] = asset_root_data

        library_data['tags'] = sorted(list(set(tags)))

        with open(library_json, "w") as f:
            json.dump(library_data, f, indent=4, sort_keys=True)


def fix_roots():
    for library in ['model', 'material', 'rigs', 'plants']:
        library_data = get_library_data(library)

        for asset_data in library_data['assets']:
            maya_file = asset_data['import_file']

            # Read in the file
            with open(maya_file, 'r') as file:
                # logger.debug("Removing root from %s", maya_file)
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace('_root', '')

            # Write the file out again
            with open(maya_file, 'w') as file:
                # logger.debug("Saving %s", maya_file)

                file.write(filedata)


def assemble_material_data():
    pass


def get_existing_megascan_model_assets():
    for asset in get_library_data("models")['assets']:
        pass


def build_megascan_materials():
    materials_library = r"F:\share\assets\quixel\Downloaded\surface"
    assets = {}

    assets_to_build = 0
    for dir in os.listdir(materials_library):
        for subdir in os.listdir(os.path.join(materials_library, dir)):
            if subdir.endswith(".json"):
                assets_to_build += 1

    print("Assets to build: {}".format(assets_to_build))

    for dir in os.listdir(materials_library):
        asset_data = {
            'name': '',
            'asset_type': 'material',
            'preview': None,
            'tags': 'megascans',
            'material_data': None,
            'megascan_id': None
        }

        source_path = os.path.join(materials_library, dir)

        found_jason = False
        for subdir in os.listdir(os.path.join(materials_library, dir)):
            if subdir.endswith(".json"):
                asset_json = os.path.join(materials_library, dir, subdir)
                found_jason = True
            elif subdir.endswith(".exr"):
                asset_id = subdir.split("_")[0]
            if subdir.endswith("view.png"):
                preview_file = os.path.join(materials_library, dir, subdir)

        json_file = open(asset_json, "r")
        asset_data = json.load(json_file)
        json_file.close()

        # Get asset name
        var_num = 1
        asset_name = asset_data["semanticTags"]["name"].replace("(", "").replace(")", "").replace("-", "_").replace(" ",
                                                                                                                    "_").replace(
            ".", "_").lower() + "_var{}".format(var_num)

        if 'id' in asset_data.keys():
            asset_data['megascan_id'] = asset_data['id']

            if megascan_asset_exists(asset_data['id'], "material"):
                print("{} exists, skipping".format(asset_name))
                continue

            print("Building asset from {}".format(dir))

        while asset_name in assets.keys():
            var_num = int(asset_name.split("var")[-1]) + 1
            asset_name = "{0}_var{1}".format(asset_name.split("_var")[0], var_num)

        material_data = get_megascan_material(source_path, asset_name, asset_id)

        asset_data = {
            "name": asset_name,
            "asset_type": "material",
            "tags": "megascans,",
            "preview": preview_file,
            "material_data": material_data,
            'megascan_id': asset_data['megascan_id']
        }

        assets[asset_name] = asset_data

        asset_builder.build_asset(asset_data)

        if os.path.isfile(os.path.join(libraries['material'], asset_name, 'maya', '{}.ma'.format(asset_name))):
            print("Built {} successfully".format(asset_name))
            assets_to_build -= 1
            print("Remaining assets to build: {}".format(assets_to_build))

            build_library_jsons()


def megascan_asset_exists(asset_id, library):
    assets_data = get_library_data(library)['assets']

    for asset, asset_data in assets_data.items():
        if 'megascan_id' in asset_data.keys():
            if asset_id == asset_data['megascan_id']:
                return True

    return False


def build_megascan_models(new=1):
    megascans_library = r"F:\share\assets\quixel\Downloaded\3d"

    current_assets = get_library_data('model')
    assets = []
    assets.extend(current_assets['assets'].keys())

    assets_to_build = 0
    for dir in os.listdir(megascans_library):
        for subdir in os.listdir(os.path.join(megascans_library, dir)):
            if subdir.endswith(".json"):
                assets_to_build += 1

    print "Assets to build: {}".format(assets_to_build)

    for dir in os.listdir(megascans_library):
        asset_data = {
            'name': '',
            'asset_type': 'model',
            'preview': None,
            'tags': 'megascans',
            'mesh': None,
            'material_data': None,
            'scale': 1,
            'has_proxy': 1,
            'megascan_id': None
        }

        megascan_data = None

        for subdir in os.listdir(os.path.join(megascans_library, dir)):

            if subdir.endswith(".json"):
                # Load Json Data
                json_file = open(os.path.join(megascans_library, dir, subdir), "r")
                megascan_data = json.load(json_file)
                json_file.close()

        if megascan_data is None:
            print("Could not find megascan data for {}, skipping".format(dir))
            continue

        # Get asset id
        if 'id' in megascan_data.keys():
            asset_id = megascan_data['id']
            print("Asset id: " + asset_id)
            asset_data['megascan_id'] = asset_id

        # Get asset name
        var_num = 1
        asset_name = megascan_data['semanticTags']['name'].lower().replace(" ", "_") + "_var" + str(var_num)
        asset_name = asset_name.replace("__", "_")

        if megascan_asset_exists(asset_id, "model"):
            print("{} exists, skipping".format(asset_name))
            continue

        print("Building asset from {}".format(dir))

        # Skip if existing
        while asset_name in assets:
            var_num += 1
            asset_name = "{0}_var{1}".format(asset_name.split("_var")[0], var_num)

        assets.append(asset_name)
        asset_data['name'] = asset_name
        print("Asset Name: " + asset_name)

        # Get material data
        material_data = get_megascan_material(os.path.join(megascans_library, dir), asset_name, asset_id)
        asset_data['material_data'] = material_data

        # Get mesh
        mesh_file = os.path.join(megascans_library, dir, "{}_LOD0.obj".format(asset_id))
        if os.path.isfile(mesh_file):
            asset_data["mesh"] = mesh_file
            print("Found mesh file: " + mesh_file)
        else:
            print("Could not find mesh file for {}, skipping".format(dir))

        # Get scale
        for d in megascan_data["meta"]:
            if d["key"] == "height":
                scale = 3.28 * float(d["value"].split("m")[0])
                asset_data['scale'] = scale

        # Get preview
        preview_file = os.path.join(megascans_library, dir, "{}_preview.png".format(asset_id))
        if os.path.isfile(preview_file):
            asset_data['asset_preview'] = preview_file
        elif os.path.isfile(preview_file.replace(".png", ".jpg")):
            asset_data['asset_preview'] = preview_file.replace(".png", ".jpg")

        asset_builder.build_asset(asset_data, build_maya=True)

        if os.path.isfile(os.path.join(libraries['model'], asset_name, 'maya', '{}.ma'.format(asset_name))):
            print("Built {} successfully".format(asset_name))
            assets_to_build -= 1
            print("Remaining assets to build: {}".format(assets_to_build))

            build_library_jsons()


def get_megascan_material(path, asset_name, asset_id):
    material_data = {
        "name": asset_name,
        "material_type": "VRayMtl",
        "textures": {}
    }

    textures = {}

    diffuse_path = os.path.join(path, "{}_4K_Albedo.exr".format(asset_id))
    if os.path.isfile(diffuse_path):
        textures['diffuse'] = {
            'path': diffuse_path,
            'use_ptex': False
        }

    specular_path = os.path.join(path, "{}_4K_Specular.exr".format(asset_id))
    if os.path.isfile(specular_path):
        textures['specular'] = {
            'path': specular_path,
            'use_ptex': False
        }

    gloss_path = os.path.join(path, "{}_4K_Gloss.exr".format(asset_id))
    if os.path.isfile(gloss_path):
        textures['gloss'] = {
            'path': gloss_path,
            'use_ptex': False
        }

    normal_path = os.path.join(path, "{}_4K_Normal_LOD0.exr".format(asset_id))
    if os.path.isfile(normal_path):
        textures['normal'] = {
            'path': normal_path,
            'use_ptex': False
        }

    elif os.path.isfile(normal_path.replace("_LOD0", "")):
        textures['normal'] = {
            'path': normal_path.replace("_LOD0", ""),
            'use_ptex': False
        }

    displacement_path = os.path.join(path, "{}_4K_Displacement.exr".format(asset_id))
    if os.path.isfile(displacement_path):
        textures['displacement'] = {
            'path': displacement_path,
            'use_ptex': False
        }

    material_data["textures"] = textures

    return material_data


def delete_existing_megascans():
    paths = [
        r"F:\share\assets\libraries\model",
        r"F:\share\assets\libraries\material"
    ]

    for m_path in paths:
        for dir in os.listdir(m_path):
            data_file = os.path.join(m_path, dir, "data.json")
            if os.path.isfile(data_file):
                json_file = open(data_file, "r")
                asset_data = json.load(json_file)
                json_file.close()

                if "megascans" in asset_data["tags"]:
                    print "Deleting {}".format(os.path.join(m_path, dir))
                    shutil.rmtree(os.path.join(m_path, dir))


def delete_library_datas():
    for libray, path in libraries.items():
        json_path = os.path.join(path, "assets.json")
        if os.path.isfile(json_path):
            os.remove(json_path)


def rebuild_asset_data_json():
    for library in ['model', 'material', 'plants', 'rigs']:
        library_data = get_library_data(library)

        for asset_data in library_data['assets']:
            asset_root_path = os.path.join(libraries[library], asset_data['asset_name'])

            asset_data_json = os.path.join(asset_root_path, "data.json")

            if os.path.isfile(asset_data_json):
                json_file = open(asset_data_json, "r")
                data = json.load(json_file)
                json_file.close()

                data['import_file'] = asset_data['import_file']

                with open(asset_data_json, "w") as f:
                    json.dump(data, f, indent=4)


def get_library_data(library):
    library_json_path = os.path.join(libraries[library], "assets.json")

    if os.path.isfile(library_json_path):

        json_file = open(library_json_path, "r")
        library_asset_data = json.load(json_file)
        json_file.close()

        return library_asset_data

    else:
        return None


def rename():
    maps_path = r"F:\share\assets\stock_footage\images\src\png_clouds\png_clouds"

    i = 0
    for dir in os.listdir(maps_path):
        source_path = os.path.join(maps_path, dir)
        if os.path.isfile(source_path):
            if source_path.split(".")[-1] in ['exr', 'png', 'jpg', 'tiff', 'tif', 'jpeg']:
                dst_path = os.path.join(maps_path, "cloud_{:03d}".format(i) + ".{}".format(source_path.split(".")[-1]))
                try:
                    os.rename(source_path, dst_path)
                    i += 1
                except:
                    pass


def add_jpgs_to_preview():
    library_data = get_library_data("model")

    for asset in library_data['assets']:
        asset_root = os.path.join(libraries["model"], asset)

        asset_data_json_file = os.path.join(asset_root, "data.json")

        if os.path.isfile(asset_data_json_file):
            json_file = open(asset_data_json_file, "r")
            asset_data = json.load(json_file)
            json_file.close()

            if 'asset_preview' not in asset_data.keys():
                preview_path = os.path.join(asset_root, "{}_preview.jpg".format(asset))
                if os.path.isfile(preview_path):
                    asset_data["asset_preview"] = preview_path

            with open(asset_data_json_file, "w") as f:
                json.dump(asset_data, f, indent=4)


def fix_self_name():
    for lib in ['plants', 'material', 'model', 'rigs', 'material']:
        assets = get_library_data(lib)
        for asset in assets['assets']:
            print(asset)
            json_file = os.path.join(libraries[lib], asset, "data.json")

            # Read in the file
            with open(json_file, 'r') as file:
                filedata = file.read()

            # Replace the target string
            # filedata = filedata.replace('self.name', 'asset_name')
            filedata = filedata.replace('preview', 'asset_preview')
            filedata = filedata.replace('asset_preview.png', 'preview.png')
            filedata = filedata.replace('asset_asset_preview', 'asset_preview')

            # Write the file out again
            with open(json_file, 'w') as file:
                file.write(filedata)

            with open(json_file, 'r') as file:
                filedata = file.read()

            if re.search("self.name", filedata):
                print("found self.name in " + json_file)
            else:
                print("no self.name found")


if __name__ == '__main__':
    # fix_self_name()
    # print(get_library_data("model")['assets'])
    # fix_roots()
    # delete_existing_megascans()
    # rename()
    build_library_jsons()
    # assets_data = get_library_data('model')['assets'].keys()
    # delete_library_datas()
    # build_megascan_materials()
    # build_megascan_models()
    # build_library_jsons()
    # add_jpgs_to_preview()
