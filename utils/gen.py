import argparse
import ast
from configparser import ConfigParser, NoOptionError, NoSectionError
import linecache
import sys
import textwrap as _textwrap


# TODO: add function in utilities
def get_data_type(val):
    """
    Given a string, returns its corresponding data type

    ref.: https://stackoverflow.com/a/10261229

    :param val: string value
    :return: Data type of string value
    """
    try:
        # TODO: not safe to evaluate string
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


# TODO: add function in utilities
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
            return parser.get(section, option)
    except NoSectionError:
        print_exception()
        return None
    except NoOptionError:
        print_exception()
        return None


def print_exception(error=None):
    """
    For a given exception, print filename, line number, the line itself, and
    exception description.

    ref.: https://stackoverflow.com/a/20264059

    :return: None
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
        err_desc = "{}: {}".format(error, exc_obj)
    # TODO: find a way to add the error description (e.g. AttributeError) without
    # having to provide the error description as input to the function
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), err_desc))


def read_config(config_path):
    parser = ConfigParser()
    found = parser.read(config_path)
    if config_path not in found:
        print("ERROR: {} is empty".format(config_path))
        return None
    options = {}
    for section in parser.sections():
        options.setdefault(section, {})
        for option in parser.options(section):
            options[section].setdefault(option, None)
            value = get_option_value(parser, section, option)
            if value is None:
                print("ERROR: The option '{}' could not be retrieved from {}".format(option, config_path))
                return None
            options[section][option] = value
    return options