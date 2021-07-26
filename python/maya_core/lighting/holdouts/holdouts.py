import os
import json

from collections import OrderedDict

import logging

import maya.cmds as cmds
import pymel.core as pm

from maya_core.lighting.lighting_console import modifiers_constants

holdouts_json = r"F:\share\tools\tools_core\python\maya_core\lighting\holdouts\holdout_configs.json"

log = logging.getLogger(__name__)
log.setLevel(10)


def build_json_attrs():
    # Populate a json file with vray object properties attributes
    holdout_data = {
        'attrs': modifiers_constants.MODIFIERS['attrs'],
        'attr_groups': modifiers_constants.MODIFIERS['attr_groups'],
        'presets': {}
    }

    with open(holdouts_json, 'w') as f:
        json.dump(holdout_data, f, indent=4)

    pass


def create_holdout(name=None, preset=None, add_objs=[]):
    vrop = pm.createNode("VRayObjectProperties")

    if name:
        pm.rename(vrop, name)
    if preset:
        set_holdout_preset(preset, vrop)
    if add_objs:
        objs = []

        if isinstance(add_objs, str):
            objs.append(add_objs)
        else:
            objs.extend(add_objs)

        for obj in objs:
            cmds.sets(str(obj), edit=True, add=str(vrop))

    return vrop


def set_holdout_preset(preset, vrop):
    # Sets the attributes from json file onto vray op node
    f = open(holdouts_json, 'r')
    holdout_data = json.load(f)

    if not isinstance(vrop, pm.PyNode):
        vrop = pm.PyNode(vrop)

    if preset in holdout_data['presets'].keys():
        for attr, value in holdout_data['presets'][preset].items():
            if attr == 'reflectionExclude' or attr == 'refractionExclude':
                continue

            if hasattr(vrop, attr):
                try:
                    getattr(vrop, attr).set(value)
                except:
                    log.warning("Could not set attr: %s to %s", attr, value)
                    continue


def create_preset(preset_name, vrop):
    # create preset from vrop node
    f = open(holdouts_json, 'r')
    holdout_data = json.load(f)

    if not isinstance(vrop, pm.PyNode):
        vrop = pm.PyNode(vrop)

    preset_data = {}

    for attr in holdout_data['attrs'].keys():
        if hasattr(vrop, attr):
            attr_value = getattr(vrop, attr).get()
            preset_data[attr] = attr_value

    holdout_data['presets'][preset_name] = preset_data

    with open(holdouts_json, 'w') as f:
        json.dump(holdout_data, f, indent=4)


if __name__ == '__main__':
    build_json_attrs()
