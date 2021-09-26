import json

import pymel.core as pm
import maya.cmds as cmds

def create_node_struct(d, parent=None):
    print (d['node_name'], parent)
    if "children" in d.keys():
        if d['node_name'] == "top_level":
            _ = [create_node_struct(a, parent) for a in d['children']]
        else:
            p = pm.createNode("transform", n=d['node_name'], p=parent)
            print("created {}".format(str(p)))
            _ = [create_node_struct(a, p) for a in d['children']]
    else:
        p = pm.createNode("transform", n=d['node_name'], p=parent)
        print("created {}".format(str(p)))


class MayaAsset(object):
    def __init__(self, asset_data=None, node=None):
        self.asset_data = asset_data
        self.world_node = node

        if self.world_node is None and self.asset_data is not None:
            self.create_maya_asset_node()

    def create_maya_asset_node(self):
        # Create Nodes
        self.world_node = pm.createNode("transform", n=self.asset_data['asset_name'])

        asset_structure_json_path = r"F:\share\tools\tools_core\python\maya_core\pipeline\Asset\MayaAsset_node_structure.json"

        json_file = open(asset_structure_json_path, "r")
        asset_structure_data = json.load(json_file)
        json_file.close()

        create_node_struct(asset_structure_data, parent=self.world_node)

        # Create Attrs
        cmds.addAttr(str(self.world_node), ln="mayaAsset", at="long")
        cmds.addAttr(str(self.world_node), ln="assetType", dt="string")
        cmds.addAttr(str(self.world_node), ln="assetName", dt="string")

        self.world_node.mayaAsset.set(1)
        self.world_node.mayaAsset.lock()
        self.world_node.assetType.set(self.asset_data['asset_type'])
        self.world_node.assetType.lock()
        self.world_node.assetName.set(self.asset_data['asset_name'])
        self.world_node.assetName.lock()

    def apply_hair_cache(self, cache_path):
        pass

    def cache_hair(self, cache_path, frame_range):
        pass

    def cache_geo(self):
        pass
