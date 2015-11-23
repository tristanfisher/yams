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


# SETTING_LOG_LEVEL = chain_load_setting('LOG_LEVEL', 'YAMA_LOG_LEVEL', default='ERROR')
# SETTING_DEBUG = chain_load_setting('DEBUG', 'YAMA_DEBUG', default=False)
#
# SETTING_YAMS_HOST = chain_load_setting('YAMS_HOST', 'YAMA_YAMS_HOST', default='127.0.0.1')
# SETTING_YAMS_PORT = chain_load_setting('YAMS_PORT', 'YAMA_YAMS_PORT', default=1112)
# SETTING_YAMS_TIMEOUT = chain_load_setting('SOCKET_TIMEOUT', 'YAMA_SOCKET_TIMEOUT', default=15)
#
# SETTING_YAMS_VERIFY_SSL = chain_load_setting('VERIFY_SSL', 'YAMA_VERIFY_SSL', (not SETTING_DEBUG))
#
# # Avoid busy-waiting.
# # A value of 0 denotes "yield to any other ready thread," but otherwise go go go.
# # I've found this to be CPU intensive (eventually running up to a full core -- wasting electricity), but leaving as a
# # named var in case a host runs YAMA as its primary purpose and the default is "laggy"
# YIELD_TO_READY_THREADS=0
# SETTING_YAMS_THREAD_YIELD_EPSILON = chain_load_setting('YAMA_THREAD_YIELD_EPSILON', 'YAMA_THREAD_YIELD_EPSILON', default=0.5)
#
# VERSION = '0.0.1a'