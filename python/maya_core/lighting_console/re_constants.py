import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from collections import OrderedDict

VRayAOVS = OrderedDict()

VRayAOVS['Atmospheric Effects'] = 'atmosphereChannel'
# VRayAOVS['Background'] = 'backgroundChannel'
# VRayAOVS['Bump Normals'] = 'bumpNormalsChannel'
# VRayAOVS['Caustics'] = 'causticsChannel'
# VRayAOVS['Coat Filter'] = 'coatFilterChannel'
# VRayAOVS['Coat Glossiness'] = 'coatGlossinessChannel'
# VRayAOVS['Coat Reflection'] = 'coatReflectionChannel'
# VRayAOVS['Coat Specular'] = 'vrayCoatChannel'
# VRayAOVS['Coverage'] = 'CoverageChannel'
VRayAOVS['Cryptomatte'] = 'cryptomatteChannel'
VRayAOVS['Custom Color'] = 'customColor'
# VRayAOVS['DR Bucket'] = 'drBucketChannel'
VRayAOVS['Denoiser'] = 'denoiserChannel'
# VRayAOVS['Diffuse'] = 'diffuseChannel'
VRayAOVS['Extra Tex'] = 'ExtraTexElement'
VRayAOVS['GI'] = 'giChannel'
# VRayAOVS['Light Mix'] = 'LightMixElement'
VRayAOVS['Light Select'] = 'LightSelectElement'
# VRayAOVS['Lighting'] = 'lightingChannel'
# VRayAOVS['Lighting Analysis'] = 'LightingAnalysisChannel'
# VRayAOVS['Material ID'] = 'materialIDChannel'
VRayAOVS['Material Select'] = 'MaterialSelectElement'
# VRayAOVS['Matte Shadow'] = 'matteShadowChannel'
# VRayAOVS['Multi Matte'] = 'MultiMatteElement'
# VRayAOVS['Multi Matte ID'] = 'multimatteIDChannel'
# VRayAOVS['Normals'] = 'normalsChannel'
# VRayAOVS['Object ID'] = 'nodeIDChannel'
# VRayAOVS['Object Select'] = 'objectSelectChannel'
# VRayAOVS['Raw Coat Filter'] = 'rawCoatFilterChannel'
# VRayAOVS['Raw Coat Reflection'] = 'rawCoatReflectionChannel'
# VRayAOVS['Raw Diffuse Filter'] = 'rawDiffuseFilterChannel'
# VRayAOVS['Raw GI'] = 'rawGiChannel'
# VRayAOVS['Raw Light'] = 'rawLightChannel'
# VRayAOVS['Raw Reflection'] = 'rawReflectionChannel'
# VRayAOVS['Raw Reflection Filter'] = 'rawReflectionFilterChannel'
# VRayAOVS['Raw Refraction'] = 'rawRefractionChannel'
# VRayAOVS['Raw Refraction Filter'] = 'rawRefractionFilterChannel'
# VRayAOVS['Raw Shadow'] = 'rawShadowChannel'
# VRayAOVS['Raw Sheen Filter'] = 'rawSheenFilterChannel'
# VRayAOVS['Raw Sheen Reflection'] = 'rawSheenReflectionChannel'
# VRayAOVS['Raw Total Light'] = 'rawTotalLightChannel'
# VRayAOVS['Reflect IOR'] = 'reflectIORChannel'
# VRayAOVS['Reflection'] = 'reflectChannel'
# VRayAOVS['Reflection Filter'] = 'reflectionFilterChannel'
# VRayAOVS['Reflection Glossiness'] = 'reflectGlossinessChannel'
# VRayAOVS['Refraction'] = 'refractChannel'
# VRayAOVS['Refraction Filter'] = 'refractionFilterChannel'
# VRayAOVS['Refraction Glossiness'] = 'refractGlossinessChannel'
# VRayAOVS['Render ID'] = 'renderIDChannel'
# VRayAOVS['SSS'] = 'FastSSS2Channel'
VRayAOVS['Sample Rate'] = 'sampleRateChannel'
VRayAOVS['Sampler Info'] = 'samplerInfo'
VRayAOVS['Self Illumination'] = 'selfIllumChannel'
# VRayAOVS['Shadow'] = 'shadowChannel'
# VRayAOVS['Sheen Filter'] = 'sheenFilterChannel'
# VRayAOVS['Sheen Glossiness'] = 'sheenGlossinessChannel'
# VRayAOVS['Sheen Reflection'] = 'sheenReflectionChannel'
# VRayAOVS['Sheen Specular'] = 'vraySheenChannel'
# VRayAOVS['Specular'] = 'specularChannel'
# VRayAOVS['Toon'] = 'Toon'
# VRayAOVS['Toon Lighting'] = 'toonLightingChannel'
# VRayAOVS['Toon Specular'] = 'toonSpecularChannel'
# VRayAOVS['Total Light'] = 'totalLightChannel'
# VRayAOVS['Unclamped Color'] = 'unclampedColorChannel'
# VRayAOVS['VRScans Paint Mask'] = 'VRScansPaintMaskChannel'
# VRayAOVS['VRScans Zone Mask'] = 'VRScansZoneMaskChannel'
VRayAOVS['Velocity'] = 'velocityChannel'
VRayAOVS['Z-depth'] = 'zdepthChannel'

deep_output_res = [
    'atmosphereChannel',
    'customColor',
    'denoiserChannel',
    'ExtraTexElement',
    'giChannel',
    'LightSelectElement',
    'MaterialSelectElement',
    'sampleRateChannel',
    'samplerInfo',
    'selfIllumChannel',
    'velocityChannel',
    'zdepthChannel'
]

VRayRenderElementsAttributes = {}

VRayRenderElementsAttributes['cryptomatteChannel'] = {
    'vray_idtype_cryptomatte': {
        'name': 'vray_idtype_cryptomatte',
        'label': "ID Type: ",
        'widget_class': 'ComboBoxAttrWidget',
        'values': [
            'Node name',
            'Material name',
            'Node name with heirarchy',
            'V-Ray user attribute',
            'asset (reference scene) name',
            '',
            'Sub object name'
        ]
    },
    'vray_add_root_name_cryptomatte': {
        'name': 'vray_add_root_name_cryptomatte',
        'label': "Sub object name mode: ",
        'widget_class': 'ComboBoxAttrWidget',
        'values': [
            'Sub object name only',
            'Add short root object name',
            'Add full root object name'
        ]
    },
    'vray_userattr_cryptomatte': {
        'name': 'vray_userattr_cryptomatte',
        'label': 'User attribute name',
        'widget_class': 'LineEditAttrWidget',
        'values': []
    },
    'vray_numlevels_cryptomatte': {
        'name': 'vray_numlevels_cryptomatte',
        'label': 'Num levels',
        'widget_class': 'SliderAttrWidget',
        'values': [1, 20]
    }
}

VRayRenderElementsAttributes['LightSelectElement'] = {
    'vray_type_lightselect': {
        'name': 'vray_type_lightselect',
        'label': "Type",
        'widget_class': 'ComboBoxAttrWidget',
        'values': [
            'Direct illumination',
            'Direct raw',
            'Direct diffuse',
            'Direct specular',
            'Full',
            'Indirect',
            'Indirect diffuse',
            'Indirect specular',
            '',
            'Light path expression'
        ]
    },
    'vray_lpe_lightselect': {
        'name': 'vray_lpe_lightselect',
        'label': 'Light Path Expression',
        'widget_class': 'LineEditAttrWidget',
        'values': []
    }
}

for re_label, re in VRayAOVS.items():
    if not VRayRenderElementsAttributes.has_key(re):
        VRayRenderElementsAttributes[re] = {}

    VRayRenderElementsAttributes[re]['enabled'] = {
        'name': 'enabled',
        'label': 'Enabled',
        'widget_class': 'CheckBoxAttrWidget',
        'values': [0, 1]
    }

    if re in deep_output_res:
        VRayRenderElementsAttributes[re]['enableDeepOutput'] = {
            'name': 'enableDeepOutput',
            'label': 'Enable deep output',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        }

for render_element in VRayAOVS.values():
    pm_node = pm.PyNode(mel.eval("vrayAddRenderElement {}".format(render_element)))

    for attr in pm.listAttr(pm_node):
        if attr.startswith("vray_name_"):
            VRayRenderElementsAttributes[render_element][attr] = {
                'name': attr,
                'label': 'Filename suffix',
                'widget_class': 'LineEditAttrWidget',
                'values': []
            }
            continue

        elif attr.startswith("vray_denoise_"):
            VRayRenderElementsAttributes[render_element][attr] = {
                'name': attr,
                'label': 'Denoise',
                'widget_class': 'CheckBoxAttrWidget',
                'values': [0, 1]
            }
            continue

        elif attr.startswith("vray_colorMapping_"):
            VRayRenderElementsAttributes[render_element][attr] = {
                'name': attr,
                'label': 'Apply color mapping',
                'widget_class': 'CheckBoxAttrWidget',
                'values': [0, 1]
            }
            continue
        elif attr.startswith("vray_considerforaa_"):
            VRayRenderElementsAttributes[render_element][attr] = {
                'name': attr,
                'label': 'Consider for Anti-Aliasing',
                'widget_class': 'CheckBoxAttrWidget',
                'values': [0, 1]
            }
            continue

    pm.delete(pm_node)
