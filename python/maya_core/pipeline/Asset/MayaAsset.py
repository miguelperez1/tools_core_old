import pymel.core as pm
import maya.cmds as cmds

MAYA_ASSET_NODE_STRUCTURE = {
    'Geometry': {
        'Constrain': ['Parts']
    },
    'Cache': {
        'Geo': [],
        'Hair': []
    },
    'Hair': {},
    'Rig': {},
    'Lighting': {
        'lgt_rig': []
    },
    'FX': {},
    'Controls': {},
    'Misc': {}
}


class MayaAsset(object):
    def __init__(self, asset_data=None, node=None):
        self.asset_data = asset_data
        self.world_node = node

        if self.world_node is None and self.asset_data is not None:
            self.create_maya_asset_node()

    def create_maya_asset_node(self):
        # Create Nodes
        self.world_node = pm.createNode("transform", n=self.asset_data['asset_name'])

        for i, j in MAYA_ASSET_NODE_STRUCTURE.items():
            i_node = pm.createNode("transform", n=i, p=self.world_node)

            for k, l in j.items():
                k_node = pm.createNode("transform", n=k, p=i_node)

                for m in l:
                    pm.createNode("transform", n=m, p=k_node)

        # Create Attrs
        cmds.addAttr(str(self.world_node), ln="mayaAsset", at="long")
        cmds.addAttr(str(self.world_node), ln="assetType", dt="string")
        cmds.addAttr(str(self.world_node), ln="assetName", dt="string")
        cmds.addAttr(str(self.world_node), ln="build", dt="string")

        self.world_node.mayaAsset.set(1)
        self.world_node.mayaAsset.lock()
        self.world_node.assetType.set(self.asset_data['asset_type'])
        self.world_node.assetType.lock()
        self.world_node.assetName.set(self.asset_data['asset_name'])
        self.world_node.assetName.lock()
        self.world_node.build.set('v001')

    def apply_hair_cache(self, cache_path):
        pass

    def cache_hair(self, cache_path, frame_range):
        pass

    def cache_geo(self):
        pass
