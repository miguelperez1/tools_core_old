import os
import json

import maya.cmds as cmds
import pymel.core as pm

projects_root  = r"F:\share\projects"

class Project(object):
    def __init__(self, name):
        super(Project, self).__init__()

        self.name = name

    def create_project(self):
        pass
