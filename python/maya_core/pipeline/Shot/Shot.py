import os


class Shot(object):
    def __init__(self, project, seq_num, shot_num):
        super(Shot, self).__init__()

        self.project = project
        self.seq_num = seq_num
        self.shot_num = shot_num

    def create_shot(self):
        os.mkdir(os.path.join(self.project.seq_root, self.seq_num, self.shot_num))

    def create_shot_manifest(self):
        pass
