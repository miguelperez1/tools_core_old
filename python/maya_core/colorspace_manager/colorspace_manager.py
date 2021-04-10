import maya.cmds as cmds

import re


def to_aces():
    files = cmds.ls(type='file')

    utility_srgb_texture = ['specular', 'diffuse', 'albedo', 'color', 'basecolor']
    utility_raw = ['gloss', 'roughness', 'normal', 'displacement', 'opacity', 'metal', 'height']
    utility_linear_texture = ['hdr']

    for file_node in files:
        path = cmds.getAttr('{}.fileTextureName'.format(file_node))
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


def to_srgb():
    files = cmds.ls(type='file')

    srgb = ['specular', 'diffuse', 'albedo', 'color']
    raw = ['gloss', 'roughness', 'normal', 'displacement', 'opacity', 'hdr', 'metal']

    for file_node in files:
        path = cmds.getAttr('{}.fileTextureName'.format(file_node))
        cmds.setAttr('{}.ignoreColorSpaceFileRules'.format(file_node), 1)
        for texture_type in srgb:
            if re.search((texture_type), path):
                print('srgb: {}'.format(path))
                cmds.setAttr('{}.colorSpace'.format(file_node), 'sRGB', type='string')

        for texture_type in raw:
            if re.search(texture_type, path):
                print('raw: {}'.format(path))
                cmds.setAttr('{}.colorSpace'.format(file_node), 'Raw', type='string')
