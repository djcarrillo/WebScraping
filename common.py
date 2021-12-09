import yaml


__config = None


def config():
    global __config
    if not __config:
        with open('config.yaml', mode='r') as directory_sites:
            __config = yaml.load(directory_sites, Loader=yaml.FullLoader)
    return __config


