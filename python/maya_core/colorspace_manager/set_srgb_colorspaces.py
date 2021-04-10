import maya.cmds as cmds

import re

def main():
    
    files = cmds.ls(type='file')

    srgb =['specular', 'diffuse', 'albedo', 'color']
    raw = ['gloss', 'roughness', 'normal', 'displacement', 'opacity', 'hdr', 'metal', 'rough', 'metalness']


    for file_node in files:
        path = cmds.getAttr('{}.fileTextureName'.format(file_node)).lower()
        cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(file_node), 1)
        for texture_type in srgb:
            if re.search((texture_type), path):
                print('srgb: {}'.format(path))
                cmds.setAttr('{}.colorSpace'.format(file_node), 'sRGB', type='string')
                
        for texture_type in raw:
            if re.search(texture_type, path):
                print('raw: {}'.format(path))
                cmds.setAttr('{}.colorSpace'.format(file_node), 'Raw', type='string')

                
if __name__ == 'maya_core.colorspace_manager.set_srgb_colorspaces':
    main()
