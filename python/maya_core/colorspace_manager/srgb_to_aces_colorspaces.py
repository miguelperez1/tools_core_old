import maya.cmds as cmds

import re

def main():
    
    files = cmds.ls(type='file')

    utility_srgb_texture =['specular', 'diffuse', 'albedo', 'color', 'basecolor']
    utility_raw = ['gloss', 'roughness', 'normal', 'displacement', 'opacity', 'metal', 'height', 'rough']
    utility_linear_texture = ['hdr']


    for file_node in files:
        path = cmds.getAttr('{}.fileTextureName'.format(file_node)).lower()
        cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(file_node), 1)
        for texture_type in utility_srgb_texture:
            if re.search((texture_type), path):
                print('Utility_SRGB_Texture: {}'.format(path))
                cmds.setAttr('{}.colorSpace'.format(file_node), 'Utility - sRGB - Texture', type='string')
                
        for texture_type in utility_raw:
            if re.search(texture_type, path):
                print('Utility_raw: {}'.format(path))
                cmds.setAttr('{}.colorSpace'.format(file_node), 'Utility - Raw', type='string')

        for texture_type in utility_linear_texture:
            if re.search(texture_type, path):
                print('Utility_linear: {}'.format(path))
                cmds.setAttr('{}.colorSpace'.format(file_node), 'Utility - Linear - sRGB', type='string')
                
if __name__ == 'maya_core.colorspace_manager.srgb_to_aces_colorspaces':
    main()
