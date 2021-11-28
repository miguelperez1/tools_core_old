import os
import logging

SHOT_FOLDER_STRUCTURE = {
    'animation': {
        'wip': [],
        'publish': []
    },
    'cache': {
        'geo': [],
        'hair': [],
        'camera': []
    },
    'layout': {
        'wip': [],
        'publish': []
    },
    'lighting': {
        'lgt': ['wip', 'publish'],
        'comp': ['wip', 'publish'],
        'publish': ['exr'],
        'src_renders': ['old', 'standby', 'current']
    },
    'fx': {},
    'footage': {
        'final': [],
        'wip': []
    }
}

logger = logging.getLogger(__name__)
logger.setLevel(10)


class Shot(object):
    def __init__(self, project, seq_num, shot_num):
        super(Shot, self).__init__()

        self.project = project
        self.seq_num = seq_num
        self.shot_num = shot_num

    def create_shot(self):

        self.shot_path = os.path.join(self.project.seq_path, self.seq_num, 'shots',
                                      "{0}_{1}".format(self.seq_num, self.shot_num))

        if os.path.isdir(self.shot_path):
            logger.warning("shot exists, skipping")
            return

        os.mkdir(self.shot_path)

        for folder, subfolders_data in SHOT_FOLDER_STRUCTURE.items():
            os.mkdir(os.path.join(self.shot_path, folder))

            for sf, sfsf in subfolders_data.items():
                os.mkdir(os.path.join(self.shot_path, folder, sf))

                for f in sfsf:
                    os.mkdir(os.path.join(self.shot_path, folder, sf, f))

    def create_shot_manifest(self):
        pass
