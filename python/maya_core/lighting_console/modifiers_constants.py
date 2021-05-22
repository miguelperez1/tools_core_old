from collections import OrderedDict

import maya.cmds as cmds
import pymel.core as pm

MODIFIERS = {
    'attrs': {
        'ignore': {
            'name': 'ignore',
            'label': 'Disable',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'matteSurface': {
            'name': 'matteSurface',
            'label': 'Matte Surface',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'alphaContribution': {
            'name': 'alphaContribution',
            'label': 'Alpha Contribution',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [-1, 1]
        },
        'shadows': {
            'name': 'shadows',
            'label': 'Shadows',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'affectAlpha': {
            'name': 'affectAlpha',
            'label': 'Affect Alpha',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'shadowBrightness': {
            'name': 'shadowBrightness',
            'label': 'Shadow Brightness',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [0, 1]
        },
        'reflectionAmount': {
            'name': 'reflectionAmount',
            'label': 'Reflection Amount',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [0, 1]
        },
        'refractionAmount': {
            'name': 'refractionAmount',
            'label': 'Refraction Amount',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [0, 1]
        },
        'giAmount': {
            'name': 'giAmount',
            'label': 'GI Amount',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [0, 1]
        },
        'noGIOnOtherMattes': {
            'name': 'noGIOnOtherMattes',
            'label': 'No GI On Other Mattes',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'matteForSecondaryRays': {
            'name': 'matteForSecondaryRays',
            'label': 'Matte for Secondary Rays',
            'widget_class': 'ComboBoxAttrWidget',
            'values': [
                'Disable',
                'With Projection Mapping',
                'Without Projection Mapping'
            ]
        },
        'useIrradianceMap': {
            'name': 'useIrradianceMap',
            'label': 'Use Irradiance Map',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'generateGI': {
            'name': 'generateGI',
            'label': 'Generate GI',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'generateGIMultiplier': {
            'name': 'generateGIMultiplier',
            'label': 'Generate GI Multiplier',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [0, 1]
        },
        'giSubdivsMultiplier': {
            'name': 'giSubdivsMultiplier',
            'label': 'Subdivs Multiplier',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [0, 2]
        },
        'generateCaustics': {
            'name': 'generateCaustics',
            'label': 'Generate Caustics',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'receiveCaustics': {
            'name': 'receiveCaustics',
            'label': 'Receive Caustics',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'causticsMultiplier': {
            'name': 'causticsMultiplier',
            'label': 'Caustics Multiplier',
            'widget_class': 'DoubleSliderAttrWidget',
            'values': [0, 1]
        },
        'giSurfaceID': {
            'name': 'giSurfaceID',
            'label': 'GI Surface ID',
            'widget_class': 'SliderAttrWidget',
            'values': [0, 10]
        },
        'sssSurfaceID': {
            'name': 'sssSurfaceID',
            'label': 'SSS Surface ID',
            'widget_class': 'SliderAttrWidget',
            'values': [0, 10]
        },
        'generateRenderElements': {
            'name': 'generateRenderElements',
            'label': 'Generate Render Elements',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'giVisibility': {
            'name': 'giVisibility',
            'label': 'Visible to GI',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'primaryVisibility': {
            'name': 'primaryVisibility',
            'label': 'Primary Visibility',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'reflectionVisibility': {
            'name': 'reflectionVisibility',
            'label': 'Visible in Reflections',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'refractionVisibility': {
            'name': 'refractionVisibility',
            'label': 'Visible in Refractions',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'shadowVisibility': {
            'name': 'shadowVisibility',
            'label': 'Cast Shadows',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'receiveShadows': {
            'name': 'receiveShadows',
            'label': 'Receive Shadows',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'objectIDEnabled': {
            'name': 'objectIDEnabled',
            'label': 'Override Object ID',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'objectID': {
            'name': 'objectID',
            'label': 'Object ID',
            'widget_class': 'SliderAttrWidget',
            'values': [0, 10]
        },
        'useReflectionExclude': {
            'name': 'useReflectionExclude',
            'label': 'Use Reflection Exclude List',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'reflectionListIsInclusive': {
            'name': 'reflectionListIsInclusive',
            'label': 'As Inclusive List',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'reflectionExclude': {
            'name': 'reflectionExclude',
            'label': 'Reflection Exclude',
            'widget_class': 'LineEditAttrWidget',
            'values': []
        },
        'useRefractionExclude': {
            'name': 'useRefractionExclude',
            'label': 'Use Refraction Exclude List',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'refractionListIsInclusive': {
            'name': 'refractionListIsInclusive',
            'label': 'As Inclusive List',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'refractionExclude': {
            'name': 'refractionExclude',
            'label': 'Refraction Exclude',
            'widget_class': 'LineEditAttrWidget',
            'values': []
        },
        'overrideMBSamples': {
            'name': 'overrideMBSamples',
            'label': 'Override Motion Blur Samples',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'mbSamples': {
            'name': 'mbSamples',
            'label': 'Motion Blur Samples',
            'widget_class': 'SliderAttrWidget',
            'values': [1, 16]
        },
        'skipExportEnabled': {
            'name': 'skipExportEnabled',
            'label': 'Override Skip Rendering',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'skipExport': {
            'name': 'skipExport',
            'label': 'Skip Rendering',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },
        'hiddenInOutliner': {
            'name': 'hiddenInOutliner',
            'label': 'Hidden in Outliner',
            'widget_class': 'CheckBoxAttrWidget',
            'values': [0, 1]
        },

    },
    'presets': {
        'hidden': {
            'attr': 'value'
        },
        'matte': {
            'attr': 'value'
        }
    }
}

attr_groups = OrderedDict()

attr_groups['general'] = {
    'label': 'General',
    'attrs': ['ignore']
}

attr_groups['matte_properties'] = {
    'label': 'Matte Properties',
    'attrs': [
        'matteSurface',
        'alphaContribution',
        'shadows',
        'affectAlpha',
        'shadowBrightness',
        'reflectionAmount',
        'refractionAmount',
        'giAmount',
        'noGIOnOtherMattes',
        'matteForSecondaryRays'
    ]
}

attr_groups['additional_surface_properties'] = {
    'label': 'Additional Surface Properties',
    'attrs': [
        'useIrradianceMap',
        'generateGI',
        'generateGIMultiplier',
        'receiveGI',
        'receiveGIMultiplier',
        'giSubdivsMultiplier',
        'generateCaustics',
        'receiveCaustics',
        'causticsMultiplier',
        'giSurfaceID',
        'sssSurfaceID',
    ]
}

attr_groups['miscellaneous'] = {
    'label': 'Miscellaneous',
    'attrs': ['generateRenderElements']
}

attr_groups['visibility_options'] = {
    'label': 'Visibility Options',
    'attrs': [
        'giVisibility',
        'primaryVisibility',
        'reflectionVisibility',
        'refractionVisibility',
        'shadowVisibility',
        'receiveShadows'
    ]
}

attr_groups['object_id'] = {
    'label': 'Object ID',
    'attrs': [
        'objectIDEnabled',
        'objectID',
    ]
}

attr_groups['exclude_lists'] = {
    'label': 'Exclude Lists',
    'attrs': [
        'useReflectionExclude',
        'reflectionListIsInclusive',
        'reflectionExclude',
        'useRefractionExclude',
        'refractionListIsInclusive',
        'refractionExclude'
    ]
}

attr_groups['motion_blur_samples'] = {
    'label': 'Motion Blur Samples',
    'attrs': [
        'overrideMBSamples',
        'mbSamples',
    ]
}

attr_groups['skip_rendering'] = {
    'label': 'Skip Rendering',
    'attrs': [
        'skipExportEnabled',
        'skipExport',
    ]
}

attr_groups['extra_attributes'] = {
    'label': 'Extra Attributes',
    'attrs': [
        'hiddenInOutliner'
    ]
}

MODIFIERS['attr_groups'] = attr_groups
