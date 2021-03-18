"""General utilities
"""
import codecs
import json
import logging.config
import os
import shlex
import shutil
import subprocess
import sys
from argparse import Namespace
from collections import OrderedDict
from logging import NullHandler
from runpy import run_path
from types import SimpleNamespace

import pyebooktools

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

CFG_TYPES = ['main', 'log']
CONFIGS_DIRNAME = 'custom_configs'


# TODO: adict can also be a list of dicts, see get_configs()
def dict_to_bunch(adict):
    # Lazy import
    from sklearn.utils import Bunch

    def bunchi(item):
        b = Bunch()
        b.update(item)
        return b

    return json.loads(json.dumps(adict), object_hook=lambda item: bunchi(item))


def get_config_dict(cfg_type='main'):
    if cfg_type == 'main':
        cfg_filepath = get_main_config_filepath()
    elif cfg_type == 'log':
        cfg_filepath = get_logging_filepath()
    else:
        raise ValueError(f"Invalid cfg_type: {cfg_type}")
    return load_cfg_dict(cfg_filepath, cfg_type)


# TODO: explain cases
def get_logger_name(module__name__, module___file__, package_name=None):
    if os.path.isabs(module___file__):
        # e.g. initcwd or editcfg
        module_name = os.path.splitext(os.path.basename(module___file__))[0]
        package_path = os.path.dirname(module___file__)
        package_name = os.path.basename(package_path)
        logger_name = "{}.{}".format(
            package_name,
            module_name)
    elif module__name__ == '__main__' or not module__name__.count('.'):
        # e.g. train_models.py or explore_data.py
        if package_name is None:
            package_name = os.path.basename(os.getcwd())
        logger_name = "{}.{}".format(
            package_name,
            os.path.splitext(module___file__)[0])
    elif module__name__.count('.') > 1:
        logger_name = '.'.join(module__name__.split('.')[-2:])
    else:
        # e.g. importing mlutils from train_models.py
        logger_name = module__name__
    return logger_name


def get_settings(conf, cfg_type):
    if cfg_type == 'log':
        set_logging_field_width(conf['logging'])
        return conf['logging']
    elif cfg_type == 'main':
        _settings = {}
        for opt_name, opt_value in conf.items():
            if opt_name.startswith('__') and opt_name.endswith('__'):
                continue
            elif isinstance(opt_value, type(os)):
                # e.g. import config
                continue
            else:
                _settings.setdefault(opt_name, opt_value)
        return _settings
    else:
        raise ValueError(f"Invalid cfg_type: {cfg_type}")


def init_log(module__name__, module___file__=None, package_name=None):
    if module___file__:
        logger_ = logging.getLogger(get_logger_name(module__name__,
                                                    module___file__,
                                                    package_name))
    elif module__name__.count('.') > 1:
        logger_name = '.'.join(module__name__.split('.')[-2:])
        logger_ = logging.getLogger(logger_name)
    else:
        logger_ = logging.getLogger(module__name__)
    logger_.addHandler(NullHandler())
    return logger_


def load_cfg_dict(cfg_filepath, cfg_type):
    assert cfg_type in CFG_TYPES, f"Invalid cfg_type: {cfg_type}"
    _, file_ext = os.path.splitext(cfg_filepath)
    try:
        if file_ext == '.py':
            cfg_dict = run_path(cfg_filepath)
            cfg_dict = get_settings(cfg_dict, cfg_type)
        elif file_ext == '.json':
            cfg_dict = load_json(cfg_filepath)
        else:
            raise FileNotFoundError(
                f"[Errno 2] No such file or directory: "
                f"{cfg_filepath}")
    except FileNotFoundError as e:
        raise e
    else:
        return cfg_dict


def load_json(filepath, encoding='utf8'):
    """Load JSON data from a file on disk.

    If using Python version betwee 3.0 and 3.6 (inclusive), the data is
    returned as :obj:`collections.OrderedDict`. Otherwise, the data is
    returned as :obj:`dict`.

    Parameters
    ----------
    filepath : str
        Path to the JSON file which will be read.
    encoding : str, optional
        Encoding to be used for opening the JSON file in read mode (the default
        value is '*utf8*').

    Returns
    -------
    data : dict or collections.OrderedDict
        Data loaded from the JSON file.

    Raises
    ------
    OSError
        Raised if any I/O related error occurs while reading the file, e.g. the
        file doesn't exist.

    References
    ----------
    `Are dictionaries ordered in Python 3.6+? (stackoverflow)`_

    """
    try:
        with codecs.open(filepath, 'r', encoding) as f:
            if sys.version_info.major == 3 and sys.version_info.minor <= 6:
                data = json.load(f, object_pairs_hook=OrderedDict)
            else:
                data = json.load(f)
    except OSError:
        raise
    else:
        return data


def mkdir(path):
    # Since path can be relative to the cwd
    path = os.path.abspath(path)
    dirname = os.path.basename(path)
    if os.path.exists(path):
        # TODO: logging
        # logger.info(f"'{dirname}' folder already exits: {path}")
        # logger.info(f"Skipping it!")
        print(f"'{dirname}' folder already exits: {path}")
    else:
        # TODO: logging
        # logger.info(f"Creating folder '{dirname}': {path}")
        print(f"Creating folder '{dirname}': {path}")
        os.mkdir(path)


def move(src, dest):
    # Since path can be relative to the cwd
    src = os.path.abspath(src)
    filename = os.path.basename(src)
    if os.path.exists(dest):
        # TODO: logging
        # logger.info(f"'{filename}' already exits: {dest}")
        # logger.info(f"Skipping it!")
        print(f"'{filename}' already exits: {dest}")
    else:
        # TODO: logging
        # logger.info(f"Moving '{filename}': {dest}")
        print(f"Moving '{filename}': {dest}")
        shutil.move(src, dest)


def namespace_to_dict(ns):
    namspace_classes = [Namespace, SimpleNamespace]
    # TODO: check why not working anymore
    # if isinstance(ns, SimpleNamespace):
    if type(ns) in namspace_classes:
        adict = vars(ns)
    else:
        adict = ns
    for k, v in adict.items():
        # if isinstance(v, SimpleNamespace):
        if type(v) in namspace_classes:
            v = vars(v)
            adict[k] = v
        if isinstance(v, dict):
            namespace_to_dict(v)
    return adict


def run_cmd(cmd):
    """Run a shell command with arguments.

    The shell command is given as a string but the function will split it in
    order to get a list having the name of the command and its arguments as
    items.

    Parameters
    ----------
    cmd : str
        Command to be executed, e.g. ::

            open -a TextEdit text.txt

    Returns
    -------
    retcode: int
        Returns code which is 0 if the command was successfully completed.
        Otherwise, the return code is non-zero.

    Raises
    ------
    FileNotFoundError
        Raised if the command ``cmd`` is not recognized, e.g.
        ``$ TextEdit {filepath}`` since `TextEdit` is not an executable.

    """
    try:
        if sys.version_info.major == 3 and sys.version_info.minor <= 6:
            # TODO: PIPE not working as arguments and capture_output new in
            # Python 3.7
            # Ref.: https://stackoverflow.com/a/53209196
            #       https://bit.ly/3lvdGlG
            result = subprocess.run(shlex.split(cmd))
        else:
            result = subprocess.run(shlex.split(cmd), capture_output=True)
    except FileNotFoundError:
        raise
    else:
        return result


# TODO: specify log_dict change inline
def set_logging_field_width(log_dict):
    names = log_dict['loggers'].keys()
    if sys.argv and os.path.basename(sys.argv[0]) == 'mlearn':
        names = [n for n in names if not n.startswith('default_')]
    size_longest_name = len(max(names, key=len))
    for k, v in log_dict['formatters'].items():
        try:
            # TODO: add auto_field_width at the top
            v['format'] = v['format'].format(auto_field_width=size_longest_name)
        except KeyError:
            continue


def set_logging_formatter(log_dict, handler_names, formatter='simple'):
    # TODO: assert hander_names and formatter
    for handler_name in handler_names:
        log_dict['handlers'][handler_name]['formatter'] = formatter


def set_logging_level(log_dict, handler_names=None, logger_names=None,
                      level='DEBUG'):
    # TODO: assert handler_names, logger_names and level
    handler_names = handler_names if handler_names else []
    logger_names = logger_names if logger_names else []
    keys = ['handlers', 'loggers']
    for k in keys:
        for name, val in log_dict[k].items():
            if (not handler_names and not logger_names) or \
                    (k == 'handlers' and name in handler_names) or \
                    (k == 'loggers' and name in logger_names):
                val['level'] = level


def setup_log(use_default_log=False, quiet=False, verbose=False,
              logging_level=None, logging_formatter=None):
    logging_level = logging_level.upper()
    package_path = os.getcwd()
    if use_default_log:
        log_filepath = get_default_logging_filepath()
        main_cfg_msg = f'Default config path: {get_default_main_config_filepath()}'
        main_log_msg = f'Default logging path: {log_filepath}'
    else:
        log_filepath = get_logging_filepath()
        main_cfg_msg = f"Main config path: {get_main_config_filepath()}"
        main_log_msg = f'Logging path: {log_filepath}'
    # Get logging cfg dict
    log_dict = load_cfg_dict(log_filepath, cfg_type='log')
    # NOTE: if quiet and verbose are both activated, only quiet will have an effect
    # TODO: get first cfg_dict to setup log (same in train_models.py)
    if not quiet:
        if verbose:
            set_logging_level(log_dict, level='DEBUG')
        if logging_level:
            # TODO: add console_for_users at the top
            set_logging_level(log_dict, handler_names=['console_for_users'],
                              logger_names=['data'], level=logging_level)
        if logging_formatter:
            set_logging_formatter(log_dict, handler_names=['console_for_users'],
                                  formatter=logging_formatter)
        # Load logging config dict
        logging.config.dictConfig(log_dict)
    # =============
    # Start logging
    # =============
    logger.info("Running {} v{}".format(pyebooktools.__name__,
                                        pyebooktools.__version__))
    logger.info("Verbose option {}".format(
        "enabled" if verbose else "disabled"))
    logger.debug("Working directory: {}".format(package_path))
    logger.debug(main_cfg_msg)
    logger.debug(main_log_msg)


# TODO (IMPORTANT): use a single function for all of these
# ------------------------------
# Default dirpaths and filepaths
# ------------------------------
def get_default_configs_dirpath():
    from pymlu.default_mlconfigs import __path__
    return __path__[0]


def get_default_logging_filepath():
    return os.path.join(get_default_configs_dirpath(), 'logging.py')


def get_default_main_config_filepath():
    return os.path.join(get_default_configs_dirpath(), 'config.py')


# --------------------------
# CWD dirpaths and filepaths
# --------------------------
def get_configs_dirpath():
    # from mlconfigs import __path__
    return os.path.join(os.getcwd(), CONFIGS_DIRNAME)


def get_logging_filepath():
    return os.path.join(get_configs_dirpath(), 'logging.py')


def get_main_config_filepath():
    return os.path.join(get_configs_dirpath(), 'config.py')
