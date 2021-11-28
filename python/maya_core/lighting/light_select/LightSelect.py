import logging

import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

logger = logging.getLogger(__name__)
logger.setLevel(10)

LIGHT_TYPES = [
    'VRayLightIESShape',
    'VRayLightSphereShape',
    'VRayLightRectShape',
    'VRayLightDomeShape',
    'volumeLight',
    'areaLight',
    'spotLight',
    'pointLight',
    'directionalLight',
    'ambientLight'
]


class LightSelect(object):
    def __init__(self, name=None, ls_node=None, lights=None):
        self.ls_node = ls_node
        self.lights = lights
        self.name = name

        if self.ls_node is None:
            self.create_light_select()
        else:
            self.get_lights()

    def create_light_select(self):
        logger.debug("Creating Light Select render element.")
        self.ls_node = pm.PyNode(mel.eval("vrayAddRenderElement LightSelectElement"))

        if self.name is not None:
            if not self.name.startswith("LS_"):
                self.name = "LS_" + self.name
            pm.rename(self.ls_node, self.name)

        if self.lights is not None:
            self.add_lights(self.lights)

    def add_lights(self, lights=None):
        logger.debug("Adding %s to %s", lights, str(self.ls_node))

        all_lights = []

        if isinstance(lights, pm.PyNode):
            all_lights.append(lights)
        elif isinstance(lights, list):
            all_lights.extend(lights)
        elif isinstance(lights, str):
            try:
                l = pm.PyNode(lights)
                all_lights.append(l)
            except Exception as e:
                logger.error(e)

        for light in all_lights:
            # Check to make sure it is a light
            if pm.nodeType(light) not in LIGHT_TYPES:
                logger.warning("%s is not a light, skipping.", str(light))
                continue
            try:
                cmds.sets(str(light), edit=True, add=str(self.ls_node))
            except Exception:
                logger.warning("Could not add %s to light select, skipping.", str(light))

    def get_lights(self):
        return pm.sets(self.ls_node, q=True)
