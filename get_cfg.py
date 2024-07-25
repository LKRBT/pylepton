import yaml

def get_cfg():
    with open('configs/config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config