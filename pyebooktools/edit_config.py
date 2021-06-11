"""Edits a configuration file, either the main configuration file (`main`) or
the logging configuration file (`log`).

The configuration file can be opened by a user-specified application (``app``)
or a default program associated with this type of file (when ``app`` is `None`).
"""
import platform
import os
import shutil

from pyebooktools.utils.genutils import (get_config_filepath,
                                         get_logging_filepath,
                                         get_main_config_filepath, run_cmd)
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)


# NOTE: https://stackoverflow.com/a/27163648 [launch PyCharm from terminal]
def edit_file(cfg_type, app=None, configs_dirpath=None):
    """Edit a configuration file.

    The user chooses what type of config file (`cfg_type`) to edit: 'log' for
    the `logging config file`_ and 'main' for the `main config file`_.

    The configuration file can be opened by a user-specified application (`app`)
    or a default program associated with this type of file (when `app` is
    :obj:`None`).

    Parameters
    ----------
    cfg_type : str, {'log', 'main'}
        The type of configuration file to edit. 'log' refers to the
        `logging config file`_ and 'main' to the `main config file`_.
    app : str, optional
        Name of the application to use for opening the config file, e.g.
        `TextEdit` (the default value is :obj:`None` which implies that the
        default application will be used to open the config file).
    configs_dirpath: str, optional
        TODO: writeme

    Returns
    -------
    retcode : int
        If there is a `subprocess
        <https://docs.python.org/3/library/subprocess.html#subprocess.CalledProcessError>`_
        -related error, the return code is non-zero. Otherwise, it is 0 if the
        file can be successfully opened with an external program.

    """
    # Get path to the config file
    filepath = get_config_filepath(cfg_type, configs_dirpath)
    # Command to open the config file with the default application in the
    # OS or the user-specified app, e.g. `open filepath` in macOS opens the
    # file with the default app (e.g. atom)
    default_cmd_dict = {'Darwin': 'open {filepath}',
                        'Linux': 'xdg-open {filepath}',
                        'Windows': 'cmd /c start "" "{filepath}"'}
    # NOTE: check https://bit.ly/31htaOT (pymotw) for output from
    # platform.system on three OSes
    default_cmd = default_cmd_dict.get(platform.system())
    # NOTES:
    # - `app is None` implies that the default app will be used
    # - Otherwise, the user-specified app will be used
    cmd = default_cmd if app is None else app + " " + filepath
    retcode = 1
    result = None
    try:
        # IMPORTANT: if the user provided the name of an app, it will be used as
        # a command along with the file path, e.g. ``$ atom {filepath}``.
        # However, this case might not work if the user provided an app name
        # that doesn't refer to an executable, e.g. ``$ TextEdit {filepath}``
        # won't work. The failed case is further processed in the except block.
        result = run_cmd(cmd.format(filepath=filepath))
        retcode = result.returncode
    except FileNotFoundError:
        # This error happens if the name of the app can't be called as an
        # executable in the terminal
        # e.g. `TextEdit` can't be run in the terminal but `atom` can since the
        # latter refers to an executable.
        # To open `TextEdit` from the terminal, the command ``open -a TextEdit``
        # must be used on macOS.
        # TODO: IMPORTANT add the open commands for the other OSes
        specific_cmd_dict = {'Darwin': 'open -a {app}'.format(app=app)}
        # Get the command to open the file with the user-specified app
        cmd = specific_cmd_dict.get(platform.system(), app) + " " + filepath
        # TODO: explain DEVNULL, suppress stderr since we will display the error
        # TODO: IMPORTANT you might get a FileNotFoundError again?
        result = run_cmd(cmd)  # stderr=subprocess.DEVNULL)
        retcode = result.returncode
    if retcode == 0:
        logger.info("Opening the file {}...".format(
            os.path.basename(filepath)))
        logger.debug(f"Filepath: {filepath}")
    else:
        if result:
            err = result.stderr.decode().strip()
            logger.error(err)
    return retcode


def reset_file(cfg_type, configs_dirpath=None):
    # Get path to the config file
    filepath = get_config_filepath(cfg_type, configs_dirpath)
    logger.info("Resetting the file {}...".format(
        os.path.basename(filepath)))
    logger.debug(f"Filepath: {filepath}")
    # Copy it from the default one
    if cfg_type == 'main':
        src = get_main_config_filepath(configs_dirpath, default_config=True)
    else:
        src = get_logging_filepath(configs_dirpath, default_config=True)
    shutil.copy(src, filepath)
    logger.info("File was reset!")
    return 0
