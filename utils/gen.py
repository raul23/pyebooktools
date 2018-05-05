import ast
from configparser import ConfigParser, NoOptionError, NoSectionError
import json
import linecache
import logging.config
from pathlib import Path
import sys

import yaml

from .path import check_file_exists


# logger = logging.getLogger(__name__)


def get_data_type(val):
    """
    Given a string, returns its corresponding data type

    ref.: https://stackoverflow.com/a/10261229

    :param val: string value
    :return: Data type of string value
    """
    try:
        # TODO: might not be safe to evaluate string
        t = ast.literal_eval(val)
    except ValueError:
        return str
    except SyntaxError:
        return str
    else:
        if type(t) is bool:
            return bool
        elif type(t) is int:
            return int
        elif type(t) is float:
            return float
        else:
            return str


def get_option_value(parser, section, option):
    value_type = get_data_type(parser.get(section, option))
    try:
        if value_type == int:
            return parser.getint(section, option)
        elif value_type == float:
            return parser.getfloat(section, option)
        elif value_type == bool:
            return parser.getboolean(section, option)
        else:
            value = parser.get(section, option)
            # Get the string before the escaping was applied by configparser
            # configparser adds an extra '\' before '\n' when it encounters a
            # newline in the configuration file config.ini
            # ref.: https://bit.ly/2HMpvng
            value = bytes(value, 'utf-8').decode('unicode_escape')
            return value
    except NoSectionError as e:
        get_full_exception(e)
        return None
    except NoOptionError as e:
        get_full_exception(e)
        return None


def is_yaml_file(ext):
    if ext[0] == '.':
        ext = ext[1:]
    return ext in ['yaml', 'yml']


# f: file object
def load_json(f):
    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        get_full_exception(e)
        return None
    return data


# f: file object
def load_yaml(f):
    try:
        data = yaml.load(f)
    except yaml.YAMLError as e:
        get_full_exception(e)
        return None
    return data


def get_full_exception(error=None, to_print=True):
    """
    For a given exception, print/return filename, line number, the line itself,
    and exception description.

    ref.: https://stackoverflow.com/a/20264059

    :return: TODO
    """
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    if error is None:
        err_desc = exc_obj
    else:
        err_desc = '{}: {}'.format(repr(error).split('(')[0], exc_obj)
    # TODO: find a way to add the error description (e.g. AttributeError) without
    # having to provide the error description as input to the function
    exception_msg = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), err_desc)
    if to_print:
        print(exception_msg)
    else:
        return exception_msg


def read_config_from_ini(config_path):
    if not check_file_exists(config_path):
        print("[ERROR] Main ini configuration file doesn't exit: {}".format(config_path))
        return None
    parser = ConfigParser()
    found = parser.read(config_path)
    if config_path not in found:
        print('[ERROR] {} is empty'.format(config_path))
        return None
    options = {}
    for section in parser.sections():
        options.setdefault(section, {})
        for option in parser.options(section):
            options[section].setdefault(option, None)
            value = get_option_value(parser, section, option)
            if value is None:
                print("[ERROR] The option '{}' could not be retrieved from {}".format(option, config_path))
                return None
            options[section][option] = value
    return options


def read_config_from_yaml(config_path):
    if not check_file_exists(config_path):
        print("[ERROR] Main yaml configuration file doesn't exit: {}".format(config_path))
        return None
    with open(config_path, 'r') as f:
        return load_yaml(f)


def setup_logging(config_path):
    if not check_file_exists(config_path):
        print("[ERROR] Logging configuration file doesn't exit: {}".format(config_path))
        return None
    config_dict = None
    ext = Path(config_path).suffix
    with open(config_path, 'r') as f:
        if ext == '.json':
            config_dict = load_json(f)
        elif is_yaml_file(ext):
            config_dict = load_yaml(f)
        else:
            print('[ERROR] File format for logging configuration file not '
                  'supported: {}'.format(config_path))
    try:
        logging.config.dictConfig(config_dict)
    except ValueError as e:
        get_full_exception(e)
        config_dict = None

    return config_dict

