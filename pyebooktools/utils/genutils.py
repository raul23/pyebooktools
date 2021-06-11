"""General utilities
"""
import codecs
import importlib
import json
import logging.config
import os
import shlex
import shutil
import subprocess
import sys
import unicodedata
from argparse import Namespace
from collections import namedtuple, OrderedDict
from logging import NullHandler
from pathlib import Path
from runpy import run_path
from types import SimpleNamespace

from pyebooktools.utils.logutils import (init_log, set_logging_field_width,
                                         set_logging_formatter, set_logging_level)

logger = init_log(__name__, __file__)
# TODO: is next necessary? already done in init_log
logger.addHandler(NullHandler())

CFG_TYPES = ['main', 'log']
CONFIGS_DIRNAME = 'configs'


def copy(src, dst, clobber=True):
    dst = Path(dst)
    if dst.exists():
        logger.debug(f'{dst}: file already exists')
        if clobber:
            logger.debug(f'{dst}: overwriting the file')
            shutil.copy(src, dst)
        else:
            logger.debug(f'{dst}: cannot overwrite existing file')
    else:
        logger.debug(f'Copying the file')
        shutil.copy(src, dst)


def get_config_dict(cfg_type='main', configs_dirpath=None):
    return load_cfg_dict(get_config_filepath(cfg_type, configs_dirpath), cfg_type)


def get_config_filepath(cfg_type='main', configs_dirpath=None):
    if cfg_type == 'main':
        cfg_filepath = get_main_config_filepath(configs_dirpath)
    elif cfg_type == 'log':
        cfg_filepath = get_logging_filepath(configs_dirpath)
    else:
        raise ValueError(f"Invalid cfg_type: {cfg_type}")
    return cfg_filepath


def get_settings(conf, cfg_type):
    if cfg_type == 'log':
        # set_logging_field_width(conf['logging'])
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


def load_cfg_dict(cfg_filepath, cfg_type):

    def _load_cfg_dict(cfg_filepath, cfg_type):
        if file_ext == '.py':
            cfg_dict = run_path(cfg_filepath)
            cfg_dict = get_settings(cfg_dict, cfg_type)
        elif file_ext == '.json':
            cfg_dict = load_json(cfg_filepath)
        else:
            raise TypeError("Config file extension not supported: "
                            f"{cfg_filepath}")
        return cfg_dict

    configs_dirpath = Path(cfg_filepath).parent
    assert cfg_type in CFG_TYPES, f"Invalid cfg_type: {cfg_type}"
    _, file_ext = os.path.splitext(cfg_filepath)
    try:
        cfg_dict = _load_cfg_dict(cfg_filepath, cfg_type)
    except FileNotFoundError as e:
        print(f"WARNING: Config file '{os.path.basename(cfg_filepath)}' will "
              "be created")
        # Copy it from the default one
        # TODO: IMPORTANT destination with default?
        if cfg_type == 'main':
            src = get_main_config_filepath(configs_dirpath, default_config=True)
        else:
            src = get_logging_filepath(configs_dirpath, default_config=True)
        shutil.copy(src, cfg_filepath)
        cfg_dict = _load_cfg_dict(cfg_filepath, cfg_type)
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
        logger.debug(f"Folder already exits: {path}")
        logger.debug(f"Skipping it!")
    else:
        logger.debug(f"Creating folder '{dirname}': {path}")
        os.mkdir(path)
        logger.debug("Folder created!")


def move(src, dst, clobber=True):
    # TODO: necessary?
    # Since path can be relative to the cwd
    # src = os.path.abspath(src)
    # filename = os.path.basename(src)
    src = Path(src)
    dst = Path(dst)
    if dst.exists():
        logger.debug(f'{dst.name}: file already exists')
        logger.debug(f"Destination folder path: {dst.parent}")
        if clobber:
            logger.debug(f'{dst.name}: overwriting the file')
            shutil.move(src, dst)
            logger.debug("File moved!")
        else:
            logger.debug(f'{dst.name}: cannot overwrite existing file')
            logger.debug(f"Skipping it!")
    else:
        logger.debug(f"Moving '{src.name}'...")
        logger.debug(f"Destination folder path: {dst.parent}")
        shutil.move(src, dst)
        logger.debug("File moved!")


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


def override_config_with_args(main_config, args, default_config, use_config=False):

    def process_user_args(user_args):

        def get_opt_val(opt_name, cfg_dict, default=False):
            default_val = 'not_found' if default else None
            opt_val = cfg_dict.get(opt_name, 'not_found')
            if opt_val == 'not_found' and args.get('subcommand'):
                    opt_val = cfg_dict.get(args['subcommand'], {}).get(
                        opt_name, default_val)
            return opt_val

        for arg_name, arg_val in list(user_args.items()):
            """
            if arg_name in ignored_args:
                continue
            """
            if isinstance(arg_val, dict):
                if args['subcommand'] == arg_name:
                    process_user_args(arg_val)
                    del config[args['subcommand']]
                else:
                    del config[arg_name]
                continue
            arg_val = get_opt_val(arg_name, user_args)
            default_val = get_opt_val(arg_name, default_config, default=True)
            if arg_val is not None:
                if arg_val != default_val:
                    # User specified a value in the command-line/config file
                    config[arg_name] = arg_val
                    if default_val == 'not_found':
                        results.args_not_found_in_config.append((arg_name, default_val, arg_val))
                    else:
                        results.default_args_overridden.append((arg_name, default_val, arg_val))
                else:
                    # User didn't change the config value (same as default one)
                    # TODO: factorize
                    if config.get(arg_name, 'not_found') != 'not_found':
                        config[arg_name] = arg_val
                    else:
                        config.setdefault(arg_name, arg_val)
            else:
                if default_val != 'not_found':
                    if config.get(arg_name, 'not_found') != 'not_found':
                        config[arg_name] = default_val
                    else:
                        config.setdefault(arg_name, default_val)
                else:
                    # import ipdb
                    # ipdb.set_trace()
                    raise AttributeError("No value could be found for the "
                                         f"argument '{arg_name}'")

    # ignored_args = ['func', 'subparser_name']
    # If config is Namespace
    main_config = vars(main_config)
    args = args.__dict__
    results = namedtuple("results", "args_not_found_in_config default_args_overridden msg")
    results.args_not_found_in_config = []
    results.default_args_overridden = []
    if use_config:
        results.msg = 'Default arguments overridden by config options:\n'
        config_keys = set()
        for k, v in main_config.items():
            if isinstance(v, dict):
                config_keys.update(list(v.keys()))
        for k, v in args.items():
            if k not in config_keys:
                main_config.setdefault(k, v)
        config = main_config
        user_args = main_config
    else:
        results.msg = 'Default arguments overridden by command-line arguments:\n'
        config = args.copy()
        user_args = config
        # Remove subdicts (e.g. fix or organize)
        for k, v in list(main_config.items()):
            if isinstance(v, dict):
                del main_config[k]
    process_user_args(user_args)
    main_config.update(config)
    return results


# Ref.: https://bit.ly/3tTMlNF
def remove_accents(text):
    text = unicodedata.normalize('NFKD', text)
    return "".join([c for c in text if not unicodedata.combining(c)])


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


def setup_log(package=None, configs_dirpath=None, quiet=False, verbose=False,
              logging_level=None, logging_formatter=None, subcommand=None):
    package_path = os.getcwd()
    log_filepath = get_logging_filepath(configs_dirpath)
    main_cfg_msg = f"Main config path: {get_main_config_filepath(configs_dirpath)}"
    main_log_msg = f'Logging path: {log_filepath}'
    # Get logging cfg dict
    log_dict = load_cfg_dict(log_filepath, cfg_type='log')
    # NOTE: if quiet and verbose are both activated, only quiet will have an effect
    # TODO: get first cfg_dict to setup log (same in train_models.py)
    if not quiet:
        if verbose:
            # verbose supercedes logging_level
            set_logging_level(log_dict, level='DEBUG')
        else:
            if logging_level:
                logging_level = logging_level.upper()
                # TODO: add console_for_users at the top
                set_logging_level(log_dict, level=logging_level)
        if logging_formatter:
            set_logging_formatter(log_dict, formatter=logging_formatter)
        if subcommand:
            size_longest_name = len('scripts.ebooktools')
            for log_name, _ in log_dict['loggers'].items():
                if log_name.startswith('pyebooktools') and subcommand in log_name:
                    size_longest_name = max(size_longest_name, len(log_name))
        else:
            size_longest_name = None
        set_logging_field_width(log_dict, size_longest_name)
        # Load logging config dict
        logging.config.dictConfig(log_dict)
    # =============
    # Start logging
    # =============
    if package:
        if type(package) == str:
            package = importlib.import_module(package)
        logger.info("Running {} v{}".format(package.__name__,
                                            package.__version__))
    logger.info("Verbose option {}".format(
        "enabled" if verbose else "disabled"))
    logger.debug("Working directory: {}".format(package_path))
    logger.debug(main_cfg_msg)
    logger.debug(main_log_msg)


def touch(path, mode=0o666, exist_ok=True):
    logger.debug(f"Creating file: '{path}'")
    Path(path).touch(mode, exist_ok)
    logger.debug("File created!")


# -------------------------------
# Configs: dirpaths and filepaths
# -------------------------------
def get_configs_dirpath():
    from pyebooktools.configs import __path__
    return __path__[0]


def get_logging_filepath(configs_dirpath=None, default_config=False):
    configs_dirpath = get_configs_dirpath() if configs_dirpath is None else configs_dirpath
    if default_config:
        return os.path.join(configs_dirpath, 'default_logging.py')
    else:
        return os.path.join(configs_dirpath, 'logging.py')


def get_main_config_filepath(configs_dirpath=None, default_config=False):
    configs_dirpath = get_configs_dirpath() if configs_dirpath is None else configs_dirpath
    if default_config:
        return os.path.join(configs_dirpath, 'default_config.py')
    else:
        return os.path.join(configs_dirpath, 'config.py')
