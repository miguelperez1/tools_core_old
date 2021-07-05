import maya.cmds as cmds
import pymel.core as pm


def add_camera_shake(camera):
    attrs_to_add = [
        'shakeFrequencyX',
        'shakeAmplitudeX',
        'shakeFrequencyY',
        'shakeAmplitudeY',
    ]
    # Add attributes to camera

    for attr in attrs_to_add:
        cmds.addAttr(camera, longName=attr, attributeType="double", k=1)

    cmds.setAttr("{}.shakeEnabled".format(camera), 1)

    # set expression on camera
    expr = "{0}.horizontalShake = (noise(frame * {0}.shakeFrequencyX) * -1 + .5) * {0}.shakeAmplitudeX;\n".format(camera)
    expr += "{0}.verticalShake = (noise(frame * {0}.shakeFrequencyY) * -1 + .5) * {0}.shakeAmplitudeY;".format(camera)
    cmds.expression(s=expr)


def create_shot_cam():
    cameraName = cmds.camera()
    camera = cmds.rename(cameraName[0], 'shotCam')
    cmds.setAttr('{}.displayGateMaskOpacity'.format(camera), 1)
    cmds.setAttr('{}.displayGateMaskColor'.format(camera), 0, 0, 0, type='double3')
    cmds.setAttr('{}.focalLength'.format(camera), 50)
    cmds.setAttr("{}.displayResolution".format(camera), 1)

    pm.camera(camera, e=1, filmFit="fill")

    add_camera_shake(camera)
