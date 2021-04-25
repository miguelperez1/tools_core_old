import os
from shutil import copyfile

from maya_core.common_tools import logger

log = logger.Logger()


def publish_startup_script():
    target_py_path = "C:\\Users\\Miguel\\Documents\\maya\\scripts\\userSetup.py"
    src_py_path = "F:\\share\\tools\\tools_core\\python\\maya_core\\maya_startup\\userSetup.py"

    if os.path.isfile(target_py_path) and os.path.isfile(src_py_path):
        os.remove(target_py_path)

    copyfile(src_py_path, target_py_path)

    if os.path.isfile(target_py_path):
        log.result("Copied userSetup.py successfully")


if __name__ == '__main__':
    publish_startup_script()
