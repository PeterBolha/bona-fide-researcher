import yaml


def load_config(config_path) -> dict:
    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)

    return yaml_config