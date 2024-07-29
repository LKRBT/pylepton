import yaml

def get_cfg():
    with open('/home/raspberry/pylepton/configs/config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config