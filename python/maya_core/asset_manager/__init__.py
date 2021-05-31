import os
import json
import operator

from maya_core.common_tools import logger
from maya_core.common_tools import yaml_reader

from collections import OrderedDict, defaultdict

LIBRARIES_ROOT = "F:\\share\\assets\\libraries\\"

LIBRARIES = OrderedDict()

LIBRARIES["model"] = "F:\\share\\assets\\libraries\\model"
LIBRARIES["material"] = "F:\\share\\assets\\libraries\\material"
LIBRARIES["hdri"] = "F:\\share\\assets\\libraries\\hdri"
LIBRARIES["studio_lights"] = "F:\\share\\assets\\libraries\\studiolights"
LIBRARIES["gobo_lights"] = "F:\\share\\assets\\libraries\\gobolights"
LIBRARIES["clouds"] = "F:\\share\\assets\\libraries\\clouds"
LIBRARIES["rigs"] = "F:\\share\\assets\\libraries\\rigs"
LIBRARIES["plants"] = "F:\\share\\assets\\libraries\\plants"

NORMAL_LIBRARIES = ['model',
                    'material',
                    'rigs',
                    'plants']

log = logger.Logger()


def build_asset_library(debug=False):
    log.status = debug

    written = False

    for library, library_path in LIBRARIES.items():
        log.status = debug
        library_yml_path = library_path + "\\library.yml"

        if os.path.isfile(library_yml_path):
            os.remove(library_yml_path)

        library_yml = open(library_yml_path, "a")

        if library == 'model' or library == 'material' or library == "rigs" or library == "plants":
            for path in os.listdir(library_path):
                dir = os.path.join(library_path, path)
                if dir.endswith("_root"):
                    asset = path.split("_root")[0]

                    preview = ""
                    for subdir in os.listdir(dir):
                        if subdir.endswith(".png"):
                            preview = os.path.join(dir, subdir)

                    asset_data_json_path = os.path.join(library_path, "{}_root".format(asset), "data.json")

                    if not os.path.isfile(asset_data_json_path):
                        data = {
                            "name": asset,
                            "preview": preview,
                            "tags": ""
                        }

                        with open(asset_data_json_path, "w") as file:
                            json.dump(data, file, indent=4, sort_keys=True)

                    library_yml.write("{0}: {1}\n".format(asset, preview))

                    log.info("Writing [{}] asset".format(asset))

                    written = True
        else:
            for path in os.listdir(library_path):
                if path.endswith(".exr") or path.endswith(".hdr") or path.endswith(".vdb") or path.endswith(
                        ".tif") or path.endswith(".tiff"):
                    asset = path[:-4]

                    preview_path = library_path + "\\thumbnails\\{0}_preview.png".format(asset)

                    if path.endswith(".vdb"):
                        library_yml.write("{0}: {1}\n".format(asset, preview_path))
                    else:
                        library_yml.write("{0}: {1}\n".format(path, preview_path))

                    log.info("Writing [{}] asset".format(asset))

                    written = True

        log.status = True
        log.result("Finished writing [{}] library".format(library))

    if written:
        log.status = True
        log.result("Library builds complete")
