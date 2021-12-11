import os
import json

import logging

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(10)

LIBRARIES = {
    'root': r"F:\share\assets\libraries",
    'model': r"F:\share\assets\libraries\model",
    'material': r"F:\share\assets\libraries\material",
    'clouds': r"F:\share\assets\libraries\clouds",
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


def create_library_data(library, override=True):
    library_json_path = '{}\\library_data.json'.format(LIBRARIES[library])

    # Check if library data already exists
    library_data = get_library_data(library)

    if not library_data:
        library_data = {
            "assets": {},
            "tags": []
        }

    # TODO STD_LIBRARY BUILD
    if library in STD_LIBRARIES:
        for asset in os.listdir(LIBRARIES[library]):
            if not os.path.isdir(os.path.join(LIBRARIES[library], asset)):
                continue

            if asset in library_data["assets"].keys() and not override:
                continue

            if asset in library_data["assets"].keys() and override:
                library_data["assets"][asset] = {}

            # Check for existing asset data
            asset_data = get_asset_data(library, asset)

            if asset_data:
                library_data["assets"][asset_data["asset_name"]] = asset_data

                for tag in asset_data['tags']:
                    if tag not in library_data["tags"]:
                        library_data["tags"].append(tag)
            else:
                # TODO Else do the automatic find and create asset json
                asset_data = {
                    "asset_name": asset,
                }

                # Find asset preview

                # Find maya file

                # Find proxy

                pass

    # TODO NON STD_LIBRARY BUILD
    else:
        pass

    with open(library_json_path, "w") as f:
        json.dump(library_data, f, indent=4)

    return os.path.isfile(library_json_path)


def refresh_libraries():
    for library in LIBRARIES.keys():
        if create_library_data(library):
            logger.info("%s data created successfully", library.capitalize())


def get_library_data(library):
    library_json_path = os.path.join(LIBRARIES[library], "library_data.json")

    if not os.path.isfile(library_json_path):
        return None

    library_data = json.load(open(library_json_path))

    return library_data


def get_asset_data(library, asset):
    asset_json_path = os.path.join(LIBRARIES[library], asset, "data.json")

    if not os.path.isfile(asset_json_path):
        logger.error("Could not find asset json path for %s", asset)
        return None

    asset_data = json.load(open(asset_json_path))

    return asset_data


def write_asset_data(library, asset, asset_data, override=True):
    asset_json_path = os.path.join(LIBRARIES[library], asset, "asset_data.json")

    if get_asset_data(library, asset) and not override:
        return False

    with open(asset_json_path, "w") as f:
        json.dump(asset_data, f, indent=4)

    data = json.load(open(asset_json_path))

    return asset_data == data


def add_asset_tag(library, asset, tags):
    asset_data = get_asset_data(library, asset)

    asset_data["tags"].extend(tags)

    write_asset_data(library, asset, asset_data)


# TODO CLEAR
# TMP FUNCTIONS

def reformat_asset_datas():
    for library in STD_LIBRARIES:
        library_path = LIBRARIES[library]

        if not os.path.isdir(library_path):
            continue

        for asset in os.listdir(library_path):
            asset_path = os.path.join(library_path, asset)
            if not os.path.isdir(asset_path):
                continue

            if not "data.json" in os.listdir(asset_path):
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

                    asset_data["tags"] = tags

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
                logger.info("Successfully wrote %s asset data", asset)
            else:
                logger.error("Did not write new asset data for %s", asset)


if __name__ == '__main__':
    reformat_asset_datas()
