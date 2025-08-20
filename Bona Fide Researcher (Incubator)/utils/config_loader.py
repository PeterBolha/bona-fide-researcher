"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
import yaml


def load_config(config_path) -> dict:
    with open(config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)

    return yaml_config