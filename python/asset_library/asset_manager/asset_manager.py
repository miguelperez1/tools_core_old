import os
import re
import json
from collections import OrderedDict
import logging

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(10)

LIBRARIES = {
    'root': r"F:\share\assets\libraries",
    'model': r"F:\share\assets\libraries\model",
    'material': r"F:\share\assets\libraries\material",
    'gobolights': r"F:\share\assets\libraries\gobolights",
    'hdri': r"F:\share\assets\libraries\hdri",
    'plants': r"F:\share\assets\libraries\plants",
    'rigs': r"F:\share\assets\libraries\rigs",
    'studiolights': r"F:\share\assets\libraries\studiolights",
    'texture': r"F:\share\assets\libraries\texture",
}

STD_LIBRARIES = [
    "model",
    "material",
    "plants",
    "rigs"
]

IMG_LIBRARIES = [
    "hdri",
    "studiolights",
    "gobolights",
    "texture"
]

IMG_FILE_TYPES = [
    "jpg",
    "exr",
    "tex",
    "png",
    "tiff",
    "tif",
    "jpeg",
    "hdr"
]

ASSET_KEY_ORDER = [
    "asset_name",
    "asset_preview",
    "asset_path",
    "maya_file",
    "material_data",
    "tags",
    "vrmesh",
    "vrproxy_maya",
    "vrscene",
    "vrscene_maya",
    "mesh",
    "megascan_id",
    "scale"
]


def create_library_data(library, override=True):
    if library not in STD_LIBRARIES and library not in IMG_LIBRARIES:
        logger.error("%s is not a valid library type", library)
        return False

    library_root = LIBRARIES[library]

    library_json_path = os.path.join(library_root, "library_data.json")

    # Check if library data already exists
    library_data = get_library_data(library)

    if not library_data:
        library_data = {
            "assets": {},
            "tags": []
        }

    # STD_LIBRARY BUILDS
    if library in STD_LIBRARIES:
        for asset in os.listdir(library_root):
            asset_root = os.path.join(library_root, asset)

            if not os.path.isdir(asset_root):
                continue

            if asset in library_data["assets"].keys() and not override:
                continue

            if asset in library_data["assets"].keys() and override:
                library_data["assets"][asset] = OrderedDict()

            # Check for existing asset data
            asset_data = get_asset_data(library, asset)

            if asset_data:
                ordered_asset_data = OrderedDict()

                for key in ASSET_KEY_ORDER:
                    if key in asset_data.keys():
                        ordered_asset_data[key] = asset_data[key]

                library_data["assets"][asset_data["asset_name"]] = ordered_asset_data

                for tag in asset_data['tags']:
                    if tag not in library_data["tags"]:
                        library_data["tags"].append(tag)
            else:
                # Else automatic find and create asset json
                asset_data = {
                    "asset_name": asset,
                    "asset_preview": "",
                    "vrmesh": "",
                    "vrproxy_maya": "",
                    "vrscene": "",
                    "vrscene_maya": "",
                    "maya_file": "",
                    "mesh": "",
                    "scale": None,
                    "material_data": {},
                    "megascan_id": "",
                    "tags": []
                }

                # Find asset preview
                for subdir in os.listdir(asset_root):
                    # asset_preview
                    if subdir.endswith("_preview.png"):
                        asset_data["asset_preview"] = os.path.join(asset_root, subdir)

                    # maya_file
                    if subdir == "maya":
                        maya_path = os.path.join(asset_root, subdir, "{}.ma".format(asset))

                        if os.path.isfile(maya_path):
                            asset_data["maya_file"] = maya_path

                    # mesh
                    if subdir == "mesh":
                        mesh_subdirs = os.listdir(os.path.join(asset_root, subdir))

                        for ms in mesh_subdirs:
                            if re.search("(.fbx|.obj)", ms):
                                asset_data["mesh"] = os.path.join(asset_root, subdir, "mesh", ms)
                                break

                    # vray data
                    if "vrayproxy" in os.listdir(asset_root):
                        vrayproxy_dir = os.path.join(asset_root, "vrayproxy")

                        if os.path.isdir(vrayproxy_dir):
                            vrmesh_path = os.path.join(vrayproxy_dir, "{}.vrmesh".format(asset))

                            if os.path.isfile(vrmesh_path):
                                asset_data["vrmesh"] = vrmesh_path

                            vrproxy_path = os.path.join(vrayproxy_dir, "{}_vrayproxy.ma".format(asset))

                            if os.path.isfile(vrproxy_path):
                                asset_data["vrproxy_maya"] = vrproxy_path

                # Write asset data json

                write_asset_data(library, asset, sort_asset_data(asset_data))

    # IMG_LIBRARY BUILDS
    elif library in IMG_LIBRARIES:
        for asset in os.listdir(LIBRARIES[library]):
            asset_path = os.path.join(LIBRARIES[library], asset)
            asset_name = asset.split(".")[0]

            if not os.path.isfile(asset_path):
                continue

            file_type = asset.split(".")[-1]

            if file_type not in IMG_FILE_TYPES:
                continue

            if asset_name in library_data["assets"].keys() and not override:
                continue

            asset_tags = []

            if asset_name in library_data["assets"].keys() and override:
                # IMPORTANT Always keep old asset tags, only rewrite tags through other processes
                asset_tags = library_data["assets"][asset_name]["tags"]
                library_data["assets"][asset_name] = {}

            asset_data = OrderedDict()

            asset_data["asset_name"] = asset_name
            asset_data["asset_preview"] = ""
            asset_data["asset_path"] = asset_path
            asset_data["tags"] = asset_tags

            # asset_preview
            asset_preview_path = os.path.join(library_root, "thumbnails", "{}_preview.png".format(asset_name))

            if os.path.isfile(asset_preview_path):
                asset_data["asset_preview"] = asset_preview_path

            library_data["assets"][asset_name] = asset_data

            for tag in asset_tags:
                if tag not in library_data["tags"]:
                    library_data["tags"].append(tag)

    # Check if assets in library exists, if not remove

    for asset, asset_data in library_data["assets"].items():
        if library in STD_LIBRARIES:
            if not os.path.isdir(os.path.join(library_root, asset)):
                logger.warning("%s no longer exists, removing from library_data", asset)
                library_data["assets"].pop(asset)
        elif library in IMG_LIBRARIES:
            if not os.path.isfile(asset_data["asset_path"]):
                logger.warning("%s no longer exists, removing from library_data", asset)
                library_data["assets"].pop(asset)

    # Order library data by asset name
    ordered_library_data = OrderedDict()
    ordered_library_data["assets"] = OrderedDict()
    ordered_library_data["tags"] = []

    for asset in sorted(library_data["assets"].keys(), key=lambda a: a.lower()):
        ordered_library_data["assets"][asset] = sort_asset_data(library_data["assets"][asset])

    ordered_library_data["tags"] = sorted(list(set(library_data["tags"])))

    # Write library data

    with open(library_json_path, "w") as f:
        json.dump(ordered_library_data, f, indent=4)

    if get_library_data(library) and get_library_data(library) == ordered_library_data:
        logger.info("Created %s library data successfully", library)
        return True
    else:
        logger.error("Error creating % library data", library)
        return False


def update_asset_in_library(library, asset, asset_data):
    library_data = get_library_data(library)

    library_data["assets"][asset] = sort_asset_data(asset_data)

    write_library_data(library, library_data)

    if get_library_data(library) == library_data:
        logger.info("Successfully updated %s in %s library", asset, library)
        return True
    else:
        logger.error("Error updating %s in %s library", asset, library)
        return False


def refresh_all_libraries():
    for library in LIBRARIES.keys():
        create_library_data(library)


def get_library_data(library):
    library_json_path = os.path.join(LIBRARIES[library], "library_data.json")

    if not os.path.isfile(library_json_path):
        return None

    library_data = json.load(open(library_json_path))

    return library_data


def get_asset_data(library, asset):
    asset_json_path = os.path.join(LIBRARIES[library], asset, "asset_data.json")

    if not os.path.isfile(asset_json_path):
        logger.error("Could not find asset json path for %s", asset)
        return None

    asset_data = json.load(open(asset_json_path))

    return asset_data


def sort_asset_data(asset_data):
    ordered_asset_data = OrderedDict()

    for key in ASSET_KEY_ORDER:
        if key in asset_data.keys():
            ordered_asset_data[key] = asset_data[key]

    return ordered_asset_data


def write_library_data(library, library_data, override=True):
    library_json_path = os.path.join(LIBRARIES[library], "library_data.json")

    if get_library_data(library) and not override:
        return False

    # Resort assets and asset data
    ordered_library_data = OrderedDict()
    ordered_library_data["assets"] = OrderedDict()
    ordered_library_data["tags"] = []

    for asset in sorted(library_data["assets"].keys(), key=lambda a: a.lower()):
        ordered_library_data["assets"][asset] = sort_asset_data(library_data["assets"][asset])

    ordered_library_data["tags"] = sorted(list(set(library_data["tags"])))

    # Write data
    with open(library_json_path, "w") as f:
        json.dump(ordered_library_data, f, indent=4)

    # Check if write was successful
    data = json.load(open(library_json_path))

    if library_data == data:
        logger.info("Successfully wrote %s library data", library)
        return True
    else:
        logger.error("Error writing %s library data", library)
        return False


def write_asset_data(library, asset, asset_data, override=True, update_library_data=True):
    asset_json_path = os.path.join(LIBRARIES[library], asset, "asset_data.json")

    if get_asset_data(library, asset) and not override:
        return False

    with open(asset_json_path, "w") as f:
        json.dump(asset_data, f, indent=4)

    if update_library_data:
        update_asset_in_library(library, asset, asset_data)

    data = json.load(open(asset_json_path))

    if asset_data == data:
        logger.info("Successfully wrote %s asset data", asset)
        return True
    else:
        return False


def add_asset_tag(library, asset, tags):
    asset_data = get_asset_data(library, asset)

    if not asset_data:
        return

    current_tags = asset_data["tags"]
    new_tags = []

    if isinstance(tags, str):
        if "," in tags:
            new_tags = tags.split(",")
        else:
            new_tags = [tags]
    elif isinstance(tags, list):
        new_tags.extend(tags)

    new_tags.extend(current_tags)

    asset_data["tags"] = sorted(list(set(new_tags)))

    write_asset_data(library, asset, asset_data)


# HELPER TRANSITION FUNCTIONS

def _reformat_asset_datas():
    for library in STD_LIBRARIES:
        library_path = LIBRARIES[library]

        if not os.path.isdir(library_path):
            continue

        for asset in os.listdir(library_path):
            asset_path = os.path.join(library_path, asset)

            if not os.path.isdir(asset_path):
                continue

            if "data.json" not in os.listdir(asset_path):
                continue

            logger.info("Converting %s asset data json", asset)

            old_asset_json_path = os.path.join(asset_path, "data.json")

            with open(old_asset_json_path) as f:
                old_asset_data = json.load(f)

            asset_data = {
                "asset_name": "",
                "asset_preview": "",
                "vrmesh": "",
                "vrproxy_maya": "",
                "vrscene": "",
                "vrscene_maya": "",
                "maya_file": "",
                "mesh": "",
                "scale": 1.0,
                "material_data": {},
                "megascan_id": "",
                "tags": []
            }

            # Copy existing data
            for key in asset_data.keys():
                if key in old_asset_data.keys() and key != "tags":
                    asset_data[key] = old_asset_data[key]

                if "tags" in old_asset_data.keys():
                    tags = []
                    old_tags = old_asset_data["tags"]

                    if "," in old_tags:
                        tags = [t.replace(" ", "") for t in old_asset_data['tags'].split(",")]
                    elif old_tags and "," not in old_tags:
                        tags = [old_tags]

                    asset_data["tags"] = sorted(list(set(tags)))

            # Set new data

            # Maya file
            if "import_file" in old_asset_data.keys() and old_asset_data["import_file"].endswith(".ma"):
                asset_data["maya_file"] = old_asset_data["import_file"]

            # VRay Data
            if "vrayproxy" in os.listdir(asset_path):
                vrayproxy_dir = os.path.join(asset_path, "vrayproxy")

                if os.path.isdir(vrayproxy_dir):
                    vrmesh_path = os.path.join(vrayproxy_dir, "{}.vrmesh".format(asset))

                    if os.path.isfile(vrmesh_path):
                        asset_data["vrmesh"] = vrmesh_path

                    vrproxy_path = os.path.join(vrayproxy_dir, "{}_vrayproxy.ma".format(asset))

                    if os.path.isfile(vrproxy_path):
                        asset_data["vrproxy_maya"] = vrproxy_path

            if write_asset_data(library, asset, asset_data):
                os.remove(old_asset_json_path)

                if not os.path.isfile(old_asset_json_path):
                    logger.info("Removed %s old asset data", asset)


def _copy_img_tags():
    for library in IMG_LIBRARIES:
        all_tags = []

        new_library_data = get_library_data(library)

        library_root = LIBRARIES[library]

        old_library_json = os.path.join(library_root, "assets.json")

        if not os.path.isfile(old_library_json):
            continue

        old_library_data = json.load(open(old_library_json))

        for asset, asset_data in old_library_data["assets"].items():
            if asset not in new_library_data["assets"].keys():
                continue

            if "tags" in asset_data.keys():
                tags = [t.replace(" ", "") for t in asset_data["tags"].split(",")]

                if "" in tags:
                    tags.remove("")

                new_library_data["assets"][asset]["tags"] = sorted(list(set(tags)))

                for tag in tags:
                    if tag not in all_tags:
                        all_tags.append(tag)

        new_library_data["tags"] = sorted(list(set(all_tags)))

        with open(os.path.join(library_root, "library_data.json"), "w") as f:
            json.dump(new_library_data, f, indent=4)


def _fix_scale():
    for library in STD_LIBRARIES:
        library_data = get_library_data(library)

        for asset, asset_data in library_data["assets"].items():
            if "scale" in asset_data.keys() and asset_data["scale"] == 1.0:
                asset_data["scale"] = None

            write_asset_data(library, asset, asset_data)

        create_library_data(library)


def _reorder_existing_asset_datas():
    for library in STD_LIBRARIES:
        library_data = get_library_data(library)

        for asset, asset_data in library_data["assets"].items():
            new_asset_data = OrderedDict()
            for key in ASSET_KEY_ORDER:
                if key in asset_data.keys():
                    new_asset_data[key] = asset_data[key]

            write_asset_data(library, asset, new_asset_data)

        create_library_data(library)


def _delete_library_jsons():
    for library, library_path in LIBRARIES.items():
        library_json = os.path.join(library_path, "library_data.json")

        if os.path.isfile(library_json):
            os.remove(library_json)


if __name__ == '__main__':
    add_asset_tag("model", "aman", ["test_tag", "test_tag1"])
