import os
import operator

from maya_core.common_tools import logger
from maya_core.common_tools import yaml_reader

reload(logger)

LIBRARIES = {
    "model": "F:\\share\\assets\\libraries\\model",
    "material": "F:\\share\\assets\\libraries\\material",
    "hdri": "F:\\share\\assets\\libraries\\hdri",
    "studio_lights": "F:\\share\\assets\\libraries\\studiolights",
    "plants": "F:\\share\\assets\\libraries\\plants",
    "clouds": "F:\\share\\assets\\libraries\\clouds",
    "rigs": "F:\\share\\assets\\libraries\\rigs"
}


def build_asset_library(debug=False):
    log = logger.Logger()
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

                    library_yml.write("{0}: {1}\n".format(asset, preview))

                    log.info("Writing [{}] asset".format(asset))

                    written = True
        else:
            for path in os.listdir(library_path):
                if path.endswith(".exr") or path.endswith(".hdr") or path.endswith(".vdb"):
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
