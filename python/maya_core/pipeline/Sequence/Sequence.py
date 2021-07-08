import os

from maya_core.pipeline.Shot import Shot
reload(Shot)

class Sequence(object):
    def __init__(self, project, seq_num, shots=None):
        super(Sequence, self).__init__()

        self.project = project
        self.seq_num = seq_num
        self.create_shots = shots

    def create_sequence(self):
        os.mkdir(os.path.join(self.project.seq_root, self.seq_num))

        for shot in self.create_shots:
            new_shot = Shot.Shot(self.project, self.seq_num, shot)
            new_shot.create_shot()

    def create_seq_manifest(self):
        pass
