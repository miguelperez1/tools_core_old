import os
import logging

from maya_core.pipeline.Shot import Shot

logger = logging.getLogger(__name__)
logger.setLevel(10)

SEQ_FOLDER_STRUCTURE = {
    'staging': {
        'layout': ['wip', 'publish'],
        'fx': []
    },
    'shots': {},
    'footage': {
        'final': [],
        'wip': []
    }
}


class Sequence(object):
    def __init__(self, project, seq_num, shots=None):
        super(Sequence, self).__init__()

        self.project = project
        self.seq_num = seq_num
        self.create_shots = shots

    def create_sequence(self):
        self.seq_path = os.path.join(self.project.seq_path, self.seq_num)

        if os.path.isdir(self.seq_path):
            logger.error("seq already exists, skippping")
            return

        os.mkdir(self.seq_path)

        for folder, subfolders_data in SEQ_FOLDER_STRUCTURE.items():
            os.mkdir(os.path.join(self.seq_path, folder))

            for sf, sfsf in subfolders_data.items():
                os.mkdir(os.path.join(self.seq_path, folder, sf))

                for f in sfsf:
                    os.mkdir(os.path.join(self.seq_path, folder, sf, f))

        if self.create_shots is None:
            return

        for shot in self.create_shots:
            new_shot = Shot.Shot(self.project, self.seq_num, shot)
            new_shot.create_shot()

    def create_seq_manifest(self):
        pass

    def create_seq_fx(self, fx_name):
        fx_path = os.path.join(self.seq_path, 'staging', 'fx', fx_name)

        if not os.path.isdir(fx_path):
            os.mkdir(fx_path)
            os.mkdir(os.path.join(fx_path, 'wip'))
            os.mkdir(os.path.join(fx_path, 'publish'))
