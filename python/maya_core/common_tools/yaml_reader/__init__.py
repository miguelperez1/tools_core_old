import sys
import yaml


def read_yaml(yaml_path):
    with open(yaml_path) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        data = yaml.load(file, Loader=yaml.FullLoader)
        return data