import os
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(basedir, "config.yaml"), "r") as _cf:
        config_from_file = yaml.load(_cf)
        CONFIG_FILE_EXISTS = True
except (FileNotFoundError, PermissionError):
    # log message?
    CONFIG_FILE_EXISTS = False


def get_option_config_file(config_var):
    if CONFIG_FILE_EXISTS:
        # try, except, return None --- it's okay if settings file is missing
        try:
            return config_from_file[config_var]
        except:
            # log message? it's not an error if the setting isn't in a config file
            return None
    return None


def chain_load_setting(config_file_option, envvar, default):
    # Settings file order (last wins)
    # 1. Default
    # 2. Settings file
    # 3. Env var

    # 1
    value = default

    # 2
    _conf_value = get_option_config_file(config_file_option)
    if _conf_value is not None:  # valid _conf_value could be Falsey
        value = _conf_value

    # 3
    value = os.getenv(envvar, value)

    return value