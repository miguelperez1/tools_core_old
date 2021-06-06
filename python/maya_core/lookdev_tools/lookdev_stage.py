import maya.cmds as cmds
import maya.mel as mel

import pymel.core as pm


def import_hdr():
    dome_trans = pm.createNode("transform", n="lookdev_hdr")
    dome_light = pm.shadingNode("VRayLightDomeShape", p=dome_trans, n="lookdev_hdrShape", asLight=True)

    dome_light.intensity.set(2)
    dome_light.useDomeTex.set(1)
    dome_light.multiplyByTheLightColor.set(1)
    dome_light.invisible.set(1)
    dome_light.viewportTexEnable.set(0)

    dome_tex = pm.shadingNode("file", n="lookdev_hdr_tex", asTexture=True, isColorManaged=True)

    dome_path = r"F:\share\assets\libraries\hdri\Sunset_Sunrise_Soft_1800_024.hdr"
    dome_tex.fileTextureName.set(dome_path)

    vray_place_tex = pm.createNode("VRayPlaceEnvTex", n="lookdev_hdr_VRayPlaceEnvTex")
    vray_place_tex.useTransform.set(1)
    vray_place_tex.mappingType.set(2)

    dome_uv = pm.shadingNode("place2dTexture", name='lookdev_hdr_tex_place2d', asUtility=True)
    dome_cc = pm.shadingNode("colorCorrect", name='lookdev_hdr_tex_place2d', asUtility=True)

    pm.connectAttr(dome_trans.worldMatrix, vray_place_tex.transform)
    pm.connectAttr(dome_uv.uvCoord, vray_place_tex.outUV)
    pm.connectAttr(vray_place_tex.outUV, dome_tex.uvCoord)
    pm.connectAttr(dome_tex.outColor, dome_cc.inColor)
    pm.connectAttr(dome_cc.outColor, dome_light.domeTex)
    pm.connectAttr(dome_cc.colGammaX, dome_cc.colGammaY)
    pm.connectAttr(dome_cc.colGammaX, dome_cc.colGammaZ)

    return dome_trans


def set_render_settings():
    vray_settings = pm.PyNode("vraySettings")

    x = 512
    y = 512

    vray_settings.width.set(y)
    vray_settings.height.set(y)

    cmds.setAttr("defaultResolution.width", x)
    cmds.setAttr("defaultResolution.height", y)
    cmds.setAttr("defaultResolution.deviceAspectRatio", (x / y))
    cmds.setAttr("defaultResolution.lockDeviceAspectRatio", 0)
    cmds.setAttr("defaultResolution.pixelAspect", 1.0)

    vray_settings.aspectRatio.set(float(x) / float(y))


def create_directional_light():
    transform = pm.createNode("transform", n="lookdev_directional")
    light = pm.shadingNode("directionalLight", p=transform, n="lookdev_directionalShape", asLight=True)

    light.intensity.set(2)

    transform.scaleX.set(5)
    transform.scaleY.set(5)
    transform.scaleZ.set(5)
    transform.rotateX.set(-45)
    transform.rotateY.set(-45)

    return light


def create_shotcam():
    if cmds.objExists("shotCam"):
        return

    cameraName = cmds.camera()
    camera = cmds.rename(cameraName[0], 'shotCam')
    cmds.setAttr('{}.displayGateMaskOpacity'.format(camera), 1)
    cmds.setAttr('{}.displayGateMaskColor'.format(camera), 0, 0, 0, type='double3')
    cmds.setAttr('{}.focalLength'.format(camera), 50)
    cmds.setAttr("{}.displayResolution".format(camera), 1)

    pm.camera(camera, e=1, filmFit="fill")


def create_lookdev_light_rig():
    lookdev_light_rig = pm.group(empty=True, n="lookdev_light_rig")

    hdr = import_hdr()
    directional = create_directional_light()

    pm.parent(hdr, lookdev_light_rig)
    pm.parent(directional, lookdev_light_rig)


def main():
    set_render_settings()
    if not cmds.objExists("lookdev_light_rig"):
        create_lookdev_light_rig()
    create_shotcam()


if __name__ == '__main__':
    main()
