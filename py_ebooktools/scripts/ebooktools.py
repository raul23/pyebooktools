#!/usr/bin/env python
"""This script is a Python port of `ebook-tools`_ written in Shell by `na--`_.

References
----------
* `ebook-tools`_

.. URLs

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
"""
import argparse

# import ipdb

import py_ebooktools
from py_ebooktools import edit, split_into_folders
from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.utils.genutils import (get_config_dict, init_log,
                                          namespace_to_dict,
                                          override_config_with_args, setup_log)

logger = init_log(__name__, __file__)

# ==============
# Default values
# ==============
_LOG_CFG = "log"
_MAIN_CFG = "main"


# Ref.: https://stackoverflow.com/a/14117511/14664104
def check_positive(value):
    try:
        # TODO: 2.0 rejected
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{value} is an invalid positive int value")
    else:
        return ivalue


def parse_edit_args(main_cfg):
    if main_cfg.reset:
        return edit.reset_file(main_cfg.cfg_type, main_cfg.app)
    else:
        return edit.edit_file(main_cfg.cfg_type, main_cfg.app)


def process_returned_values(returned_values):
    # ================================
    # Process previous returned values
    # ================================

    def log_opts_overriden(opts_overriden, msg, log_level='info'):
        nb_items = len(opts_overriden)
        for i, (cfg_name, old_v, new_v) in enumerate(opts_overriden):
            msg += "\t {}: {} --> {}".format(cfg_name, old_v, new_v)
            if i + 1 < nb_items:
                msg += "\n"
        getattr(logger, log_level)(msg)

    # Process 1st returned values: default args overriden by config options
    if returned_values.default_args_overriden:
        msg = "Default arguments overridden by config options:\n"
        log_opts_overriden(returned_values.default_args_overriden, msg)
    # Process 2nd returned values: config options overriden by args
    if returned_values.config_opts_overridden:
        msg = "Config options overridden by command-line arguments:\n"
        log_opts_overriden(returned_values.config_opts_overridden, msg, 'debug')
    # Process 3rd returned values: arguments not found in config file
    """
    if args_not_found_in_config:
        msg = "Command-line arguments not found in config file: " \
              "\n\t{}".format(args_not_found_in_config)
        logger.debug(msg)
    """


def setup_argparser():
    """Setup the argument parser for the command-line script.

    Returns
    -------
    parser : argparse.ArgumentParser
        Argument parser.

    """
    # Setup the parser
    parser = argparse.ArgumentParser(
        description='''\
This program is a Python port of ebook-tools written in Shell by na-- (See
https://github.com/na--/ebook-tools).

This program is a collection of tools for automated and
semi-automated organization and management of large ebook collections.

See subcommands below for a list of the tools that can be used.
''',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    default_msg = " (default: {})"
    # ===============
    # General options
    # ===============
    # TODO: package name too? instead of program name
    parser.add_argument('--version', action='version',
                        version='%(prog)s v{}'.format(py_ebooktools.__version__))
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Enable quiet mode, i.e. nothing will be printed.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help='''Print various debugging information, e.g. print
                        traceback when there is an exception.''')
    parser.add_argument(
        "-d", "--dry-run", dest='dry_run', action="store_true",
        help='''If this is enabled, no file rename/move/symlink/etc.
        operations will actually be executed.''')
    parser.add_argument(
        "-r", "--reverse", dest='file_sort_reverse', action="store_true",
        help='''If this is enabled, the files will be sorted in reverse
        (i.e. descending) order. By default, they are sorted in ascending
        order.''')
    parser.add_argument(
        '--loglvl', dest='logging_level',
        choices=['debug', 'info', 'warning', 'error'],
        help='Set logging level for all loggers.'
             + default_msg.format(default_cfg.logging_level))
    parser.add_argument(
        '--logfmt', dest='logging_formatter',
        choices=['console', 'simple', 'only_msg'],
        help='Set logging formatter for all loggers.'
             + default_msg.format(default_cfg.logging_formatter))
    # =============================================
    # Options related to the input and output files
    # =============================================
    parser_input_output_group = parser.add_argument_group(
        title='Options related to the input and output files')
    parser_input_output_group.add_argument(
        '--oft', '--output-filename-template', dest='output_filename_template',
        metavar='TEMPLATE',
        help='''This specifies how the filenames of the organized files will
        look. It is a bash string that is evaluated so it can be very flexible
        (and also potentially unsafe).''' +
             default_msg.format(default_cfg.output_filename_template))
    parser_input_output_group.add_argument(
        '--ome', '--output-metadata-extension', dest='output_metadata_extension',
        metavar='EXTENSION',
        help='''If keep_metadata is enabled, this is the extension of the
        additional metadata file that is saved next to each newly renamed file.'''
             + default_msg.format(default_cfg.output_metadata_extension))
    # ===========
    # Subcommands
    # ===========
    subparsers = parser.add_subparsers(
        title='subcommands', description=None, dest='subcommand', required=True,
        help=None)
    # TODO: add aliases, see https://bit.ly/3s2fq87
    # ==========
    # Edit files
    # ==========
    # create the parser for the "edit" command
    parser_edit = subparsers.add_parser(
        'edit', help='''Edit a configuration file.''')
    parser_edit.add_argument(
        'cfg_type', choices=[_MAIN_CFG, _LOG_CFG],
        help='''The config file to edit which can either be the main
            configuration file ('{}') or the logging configuration file
            ('{}').'''.format(_MAIN_CFG, _LOG_CFG))
    group_edit = parser_edit.add_mutually_exclusive_group()
    group_edit.add_argument(
        '-a', '--app', metavar='NAME', nargs='?',
        help='''Name of the application to use for editing the config file. If
        no name is given, then the default application for opening this type of
        file will be used.''')
    group_edit.add_argument(
        "-r", "--reset", action="store_true",
        help='''Reset a configuration file ('config' or 'log') with factory
        default values.''')
    parser_edit.set_defaults(func=parse_edit_args)
    # ==============
    # Convert to txt
    # ==============
    # create the parser for the "convert" command
    parser_convert = subparsers.add_parser(
        'convert',
        help='''Convert the supplied file to a text file. It can optionally
        also use *OCR* for `.pdf`, `.djvu` and image files.''')
    # ==================
    # split-into-folders
    # ==================
    # create the parser for the "split-into-folders" command
    parser_split_into_folders = subparsers.add_parser(
        'split',
        help='''Split the supplied ebook files (and the accompanying metadata
        files if present) into folders with consecutive names that each contain
        the specified number of files.''')
    parser_split_into_folders.add_argument(
        'folder_with_books',
        help='''Folder with books which will be recursively scanned for files.
        The found files (and the accompanying metadata files if present) will
        be split into folders with consecutive names that each contain the
        specified number of files. The default value is the current working
        directory.''')
    parser_split_into_folders.add_argument(
        '-o', '--output-folder', dest='output_folder', metavar='PATH',
        help='''The output folder in which all the new consecutively named
        folders will be created. The default is the current working
        directory.''' + default_msg.format(default_cfg.output_folder))
    parser_split_into_folders.add_argument(
        '-s', '--start-number', dest='start_number', type=int,
        help='''The number of the first folder.'''
             + default_msg.format(default_cfg.start_number))
    parser_split_into_folders.add_argument(
        '-f', '--folder-pattern', dest='folder_pattern', metavar='PATTERN',
        help='''The print format string that specifies the pattern with which
        new folders will be created. By default it creates folders like
        00000000, 00001000, 00002000, .....'''
             + default_msg.format(default_cfg.folder_pattern).replace('%', '%%'))
    parser_split_into_folders.add_argument(
        '--fpf', '--files-per-folder', dest='files_per_folder', type=check_positive,
        help='''How many files should be moved to each folder.'''
             + default_msg.format(default_cfg.files_per_folder))
    parser_split_into_folders.set_defaults(func=split_into_folders.split)
    return parser


def main():
    try:
        parser = setup_argparser()
        args = parser.parse_args()
        # Get main cfg dict
        main_cfg = argparse.Namespace(**get_config_dict('main'))
        returned_values = override_config_with_args(main_cfg, parser)
        setup_log(main_cfg.quiet, main_cfg.verbose,
                  logging_level=main_cfg.logging_level,
                  logging_formatter=main_cfg.logging_formatter)
        # Override main configuration from file with command-line arguments
        process_returned_values(returned_values)
    except AssertionError as e:
        # TODO (IMPORTANT): use same logic as in Darth-Vader-RPi
        # TODO: add KeyboardInterruptError
        logger.error(e)
        return 1
    else:
        if args.subcommand == 'edit':
            return args.func(main_cfg)
        else:
            return args.func(**namespace_to_dict(main_cfg))


if __name__ == '__main__':
    # ebooktools --loglvl debug --logfmt simple split --fpf 3
    retcode = main()
    msg = "Program exited with {}".format(retcode)
    if retcode == 1:
        logger.error(msg)
    else:
        logger.info(msg)
