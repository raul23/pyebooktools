#!/usr/bin/env python
"""This script is a Python port of `ebook-tools`_ which is written in Shell by
`na--`_.

References
----------
* `ebook-tools`_

.. URLs

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
"""
import argparse
import codecs
import sys

# TODO: remove
# import ipdb

import pyebooktools
from pyebooktools import (convert_to_txt, edit_config, find_isbns,
                          rename_calibre_library, split_into_folders)
from pyebooktools.configs import default_config as default_cfg
from pyebooktools.utils.genutils import (get_config_dict, init_log,
                                         namespace_to_dict,
                                         override_config_with_args, setup_log)

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
FILES_PER_FOLDER = default_cfg.files_per_folder
FOLDER_PATTERN = default_cfg.folder_pattern
ISBN_BLACKLIST_REGEX = default_cfg.isbn_blacklist_regex
ISBN_DIRECT_GREP_FILES = default_cfg.isbn_direct_grep_files
ISBN_GREP_REORDER_FILES = default_cfg.isbn_grep_reorder_files
ISBN_IGNORED_FILES = default_cfg.isbn_ignored_files
ISBN_METADATA_FETCH_ORDER = default_cfg.isbn_metadata_fetch_order
ISBN_REGEX = default_cfg.isbn_regex
ISBN_RET_SEPARATOR = default_cfg.isbn_ret_separator
LOGGING_FORMATTER = default_cfg.logging_formatter
LOGGING_LEVEL = default_cfg.logging_level
OCR_COMMAND = default_cfg.ocr_command
OCR_ENABLED = default_cfg.ocr_enabled
OCR_ONLY_FIRST_LAST_PAGES = default_cfg.ocr_only_first_last_pages
OUTPUT_FILE = default_cfg.output_file
OUTPUT_FILENAME_TEMPLATE = default_cfg.output_filename_template
OUTPUT_FOLDER = default_cfg.output_folder
OUTPUT_METADATA_EXTENSION = default_cfg.output_metadata_extension
SAVE_METADATA = default_cfg.save_metadata
START_NUMBER = default_cfg.start_number

# ====================
# Other default values
# ====================
_LOG_CFG = 'log'
_MAIN_CFG = 'main'
_DEFAULT_MSG = ' (default: {})'


# TODO: important mention options are grouped in each function
# TODO: important should be called general control flags
# General options
def add_general_options(parser, remove_opts=None):
    remove_opts = init_list(remove_opts)
    parser_general_group = parser.add_argument_group(title='general arguments')
    if not remove_opts.count('help'):
        parser_general_group.add_argument('-h', '--help', action='help',
                            help='Show this help message and exit.')
    # TODO: package name too? instead of program name
    if not remove_opts.count('version'):
        parser_general_group.add_argument(
            '-v', '--version', action='version',
            version=f'%(prog)s v{pyebooktools.__version__}',
            help="Show program's version number and exit.")
    if not remove_opts.count('quiet'):
        parser_general_group.add_argument(
            "-q", "--quiet", action="store_true",
            help="Enable quiet mode, i.e. nothing will be printed.")
    if not remove_opts.count('verbose'):
        # TODO: important test traceback
        parser_general_group.add_argument(
            "--verbose", action="store_true",
            help='''Print various debugging information, e.g. print
            traceback when there is an exception.''')
    if not remove_opts.count('dry-run'):
        parser_general_group.add_argument(
            "-d", "--dry-run", dest='dry_run', action="store_true",
            help='''If this is enabled, no file rename/move/symlink/etc.
                operations will actually be executed.''')
    # TODO: important remove symlink-only and other options for some subcommands
    if not remove_opts.count('symlink-only'):
        parser_general_group.add_argument(
            "--sl", "--symlink-only", dest='symlink_only', action="store_true",
            help='''Instead of moving the ebook files, create symbolic links
            to them.''')
    if not remove_opts.count('keep-metadata'):
        parser_general_group.add_argument(
            "--km", "--keep-metadata", dest='keep_metadata',
            action="store_true",
            help='''Do not delete the gathered metadata for the organized
            ebooks, instead save it in an accompanying file together with each
            renamed book. It is very useful for semi-automatic verification of
            the organized files with interactive-organizer.sh or for additional
            verification, indexing or processing at a later date.''')
    # TODO: important move reverse and 2 others after into misc
    # TODO: implement more sort options, e.g. random sort
    if not remove_opts.count('reverse'):
        parser_general_group.add_argument(
            "-r", "--reverse", dest='reverse', action="store_true",
            help='''If this is enabled, the files will be sorted in reverse
                (i.e. descending) order. By default, they are sorted in ascending
                order.''')
    if not remove_opts.count('log-level'):
        parser_general_group.add_argument(
            '--log-level', dest='logging_level',
            choices=['debug', 'info', 'warning', 'error'],
            help='Set logging level for all loggers.'
                 + _DEFAULT_MSG.format(LOGGING_LEVEL))
    if not remove_opts.count('log-format'):
        # TODO: explain each format
        parser_general_group.add_argument(
            '--log-format', dest='logging_formatter',
            choices=['console', 'simple', 'only_msg'],
            help='Set logging formatter for all loggers.'
                 + _DEFAULT_MSG.format(LOGGING_FORMATTER))
    return parser_general_group


# Options related to the input and output files
def add_input_output_options(parser, remove_opts=None, add_as_group=True):
    remove_opts = init_list(remove_opts)
    if add_as_group:
        parser_input_output = parser.add_argument_group(
            title='arguments related to the input and output files')
    else:
        parser_input_output = parser
    if not remove_opts.count('output-filename-template'):
        parser_input_output.add_argument(
            '--oft', '--output-filename-template', dest='output_filename_template',
            metavar='TEMPLATE',
            help='''This specifies how the filenames of the organized files will
            look. It is a bash string that is evaluated so it can be very flexible
            (and also potentially unsafe).''' +
                 _DEFAULT_MSG.format(OUTPUT_FILENAME_TEMPLATE))
    if not remove_opts.count('output-metadata-extension'):
        parser_input_output.add_argument(
            '--ome', '--output-metadata-extension', dest='output_metadata_extension',
            metavar='EXTENSION',
            help='''If keep_metadata is enabled, this is the extension of the
            additional metadata file that is saved next to each newly renamed file.'''
                 + _DEFAULT_MSG.format(OUTPUT_METADATA_EXTENSION))
    return parser_input_output


def add_isbn_return_separator(parser):
    # TODO: note down that escape other characters in ISBN_RET_SEPARATOR,
    # e.g. \r, \t, \a, \f, \v, \b, \n
    # TODO: see https://stackoverflow.com/a/31624058/14664104 for repr() [print '\n']
    # TODO: problems with \x and \u
    # codecs.decode(value, 'unicode_escape')
    parser.add_argument(
        '--irs', '--isbn-return-separator', dest='isbn_ret_separator',
        metavar='SEPARATOR', type=decode,
        help='''This specifies the separator that will be used when returning
            any found ISBNs.''' +
             _DEFAULT_MSG.format(repr(codecs.encode(ISBN_RET_SEPARATOR).decode('utf-8'))))


# Options related to extracting ISBNs from files and finding metadata by ISBN
def add_isbns_options(parser, remove_opts=None):
    remove_opts = init_list(remove_opts)
    parser_isbns_group = parser.add_argument_group(
        title='arguments related to extracting ISBNS from files and finding '
              'metadata by ISBN')
    if not remove_opts.count('isbn-regex'):
        # TODO: add look-ahead and look-behind info, see https://bit.ly/2OYsY76
        parser_isbns_group.add_argument(
            "-i", "--isbn-regex", dest='isbn_regex',
            help='''This is the regular expression used to match ISBN-like
            numbers in the supplied books.''' + _DEFAULT_MSG.format(ISBN_REGEX))
    if not remove_opts.count('isbn-blacklist-regex'):
        parser_isbns_group.add_argument(
            "--isbn-blacklist-regex", dest='isbn_blacklist_regex', metavar='REGEX',
            help='''Any ISBNs that were matched by the ISBN_REGEX above and pass
            the ISBN validation algorithm are normalized and passed through this
            regular expression. Any ISBNs that successfully match against it are
            discarded. The idea is to ignore technically valid but probably wrong
            numbers like 0123456789, 0000000000, 1111111111, etc..'''
                 + _DEFAULT_MSG.format(ISBN_BLACKLIST_REGEX))
    if not remove_opts.count('isbn-direct-grep-files'):
        # TODO: important don't use grep in name of option
        parser_isbns_group.add_argument(
            "--isbn-direct-grep-files", dest='isbn_direct_grep_files',
            metavar='REGEX',
            help='''This is a regular expression that is matched against the MIME
            type of the searched files. Matching files are searched directly for
            ISBNs, without converting or OCR-ing them to .txt first.'''
                 + _DEFAULT_MSG.format(ISBN_DIRECT_GREP_FILES))
    if not remove_opts.count('isbn-ignored-files'):
        parser_isbns_group.add_argument(
            "--isbn-ignored-files", dest='isbn_ignored_files', metavar='REGEX',
            help='''This is a regular expression that is matched against the MIME
            type of the searched files. Matching files are not searched for ISBNs
            beyond their filename. By default, it tries to make the scripts ignore
            .gif and .svg images, audio, video and executable files and fonts.'''
                 + _DEFAULT_MSG.format(ISBN_IGNORED_FILES))
    if not remove_opts.count('reorder-files-for-grep'):
        # TODO: important don't use grep in name of option since we are searching w/o it
        # TODO: test this option (1 or 2 args)
        parser_isbns_group.add_argument(
            "--reorder-files-for-grep", dest='isbn_grep_reorder_files', nargs='+',
            action=required_length(1, 2), metavar='LINES',
            help='''These options specify if and how we should reorder the ebook
            text before searching for ISBNs in it. By default, the first 400 lines
            of the text are searched as they are, then the last 50 are searched in
            reverse and finally the remainder in the middle. This reordering is
            done to improve the odds that the first found ISBNs in a book text
            actually belong to that book (ex. from the copyright section or the
            back cover), instead of being random ISBNs mentioned in the middle of
            the book. No part of the text is searched twice, even if these regions
            overlap. Set it to False to disable the functionality of
            first_lines,last_lines to enable it with the specified values.'''
                 + _DEFAULT_MSG.format(ISBN_GREP_REORDER_FILES))
    if not remove_opts.count('metadata-fetch-order'):
        parser_isbns_group.add_argument(
            "---mfo", "---metadata-fetch-order", dest='isbn_metadata_fetch_order',
            metavar='METADATA_SOURCES',
            help='''This option allows you to specify the online metadata sources
            and order in which the scripts will try searching in them for books by
            their ISBN. The actual search is done by calibre's fetch-ebook-metadata
            command-line application, so any custom calibre metadata plugins can
            also be used. To see the currently available options, run
            fetch-ebook-metadata --help and check the description for the
            --allowed-plugin option. If you use Calibre versions that are older than
            2.84, it's required to manually set this option to an empty string.'''
                 + _DEFAULT_MSG.format(ISBN_METADATA_FETCH_ORDER))
    # TODO: return parser for other functions too?
    return parser_isbns_group


# Options for OCR
def add_ocr_options(parser, remove_opts=None):
    remove_opts = init_list(remove_opts)
    parser_convert_group = parser.add_argument_group(title='arguments for OCR')
    if not remove_opts.count('ocr-enabled'):
        parser_convert_group.add_argument(
            "--ocr", "--ocr-enabled", dest='ocr_enabled',
            choices=['always', 'true', 'false'],
            help='''Whether to enable OCR for .pdf, .djvu and image files. It is
                disabled by default.''')
    if not remove_opts.count('ocr-only-first-last-pages'):
        parser_convert_group.add_argument(
            "--ocrop", "--ocr-only-first-last-pages",
            dest='ocr_only_first_last_pages', metavar='PAGES', nargs=2,
            help='''Value n,m instructs the scripts to convert only the first n
                and last m pages when OCR-ing ebooks.'''
                 + _DEFAULT_MSG.format(OCR_ONLY_FIRST_LAST_PAGES))
    if not remove_opts.count('ocr-command'):
        # TODO: test ocrc option or drop it
        parser_convert_group.add_argument(
            "--ocrc", "--ocr-command",
            dest='ocr_command', metavar='CMD',
            help='''This allows us to define a hook for using custom OCR settings
            or software. The default value is just a wrapper that allows us to use
            both tesseract 3 and 4 with some predefined settings. You can use a
            custom bash function or shell script - the first argument is the input
            image (books are OCR-ed page by page) and the second argument is the
            file you have to write the output text to.'''
                 + _DEFAULT_MSG.format(OCR_COMMAND))


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


# Ref.: https://stackoverflow.com/a/5187097/14664104
def decode(value):
    return codecs.decode(value, 'unicode_escape')


def init_list(list_):
    return [] if list_ is None else list_


def parse_edit_args(main_cfg):
    if main_cfg.reset:
        return edit_config.reset_file(main_cfg.cfg_type)
    else:
        return edit_config.edit_file(main_cfg.cfg_type, main_cfg.app)


def process_returned_values(returned_values):
    def log_opts_overriden(opts_overriden, msg, log_level='info'):
        nb_items = len(opts_overriden)
        for i, (cfg_name, old_v, new_v) in enumerate(opts_overriden):
            msg += f'\t {cfg_name}: {old_v} --> {new_v}'
            if i + 1 < nb_items:
                msg += "\n"
        getattr(logger, log_level)(msg)

    # Process 1st returned values: default args overriden by config options
    if returned_values.default_args_overriden:
        msg = 'Default arguments overridden by config options:\n'
        log_opts_overriden(returned_values.default_args_overriden, msg)
    # Process 2nd returned values: config options overriden by args
    if returned_values.config_opts_overridden:
        msg = 'Config options overridden by command-line arguments:\n'
        log_opts_overriden(returned_values.config_opts_overridden, msg, 'debug')
    # Process 3rd returned values: arguments not found in config file
    """
    if args_not_found_in_config:
        msg = 'Command-line arguments not found in config file: ' \
              f'\n\t{args_not_found_in_config}'
        logger.debug(msg)
    """


# Ref.: https://stackoverflow.com/a/4195302/14664104
def required_length(nmin,nmax):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                msg='argument "{f}" requires between {nmin} and {nmax}' \
                    'arguments'.format(f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


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
    parser.add_argument(
        '-v', '--version', action='version',
        version=f'%(prog)s v{pyebooktools.__version__}')
    # ===========
    # Subcommands
    # ===========
    if sys.version_info >= (3, 7):
        subparsers = parser.add_subparsers(
            title='subcommands', description=None, dest='subcommand', required=True,
            help=None)
    else:
        # No arg 'required' supported for <= 3.6
        subparsers = parser.add_subparsers(
            title='subcommands', description=None, dest='subcommand', help=None)
    # TODO: add aliases, see https://bit.ly/3s2fq87
    # ==========
    # Edit files
    # ==========
    # create the parser for the "edit" command
    parser_edit = subparsers.add_parser(
        'edit', add_help=False, help='''Edit a configuration file, either the main
        configuration file (`{}`) or the logging configuration file
        (`{}`).'''.format(_MAIN_CFG, _LOG_CFG))
    add_general_options(parser_edit, remove_opts=['dry-run', 'keep-metadata',
                                                  'reverse', 'symlink-only'])
    parser_edit_group = parser_edit.add_argument_group(
        title='specific arguments for the subcommand `test`')
    parser_edit_mutual_group = parser_edit_group.add_mutually_exclusive_group()
    parser_edit_mutual_group.add_argument(
        '-a', '--app', metavar='NAME', nargs='?',
        help='''Name of the application to use for editing the config file. If
        no name is given, then the default application for opening this type of
        file will be used.''')
    parser_edit_mutual_group.add_argument(
        "-r", "--reset", action="store_true",
        help='''Reset a configuration file (`{}` or `{}`) with factory
        default values.'''.format(_MAIN_CFG, _LOG_CFG))
    parser_edit_input_group = parser_edit.add_argument_group(
        title='input argument')
    parser_edit_input_group.add_argument(
        'cfg_type', choices=[_MAIN_CFG, _LOG_CFG],
        help='''The config file to edit which can either be the main
                configuration file (`{}`) or the logging configuration file
                (`{}`).'''.format(_MAIN_CFG, _LOG_CFG))
    parser_edit.set_defaults(func=parse_edit_args)
    # ==============
    # Convert to txt
    # ==============
    # create the parser for the "convert" command
    parser_convert = subparsers.add_parser(
        'convert', add_help=False,
        help='''Convert the supplied file to a text file. It can optionally
        also use *OCR* for .pdf, .djvu and image files.''')
    add_general_options(parser_convert, remove_opts=['dry-run', 'keep-metadata',
                                                     'reverse', 'symlink-only'])
    add_ocr_options(parser_convert)
    parser_convert_group = parser_convert.add_argument_group(
        title='input and output arguments')
    parser_convert_group.add_argument(
        'input_file',
        help='''The input file to be converted to a text file.''')
    parser_convert_group.add_argument(
        '-o', '--output-file', dest='output_file', metavar='OUTPUT',
        help='''The output file text. By default, it is saved in the current
            working directory.''' + _DEFAULT_MSG.format(OUTPUT_FILE))
    parser_convert.set_defaults(func=convert_to_txt.convert)
    # ==========
    # Find ISBNs
    # ==========
    # create the parser for the "find" command
    parser_find = subparsers.add_parser(
        'find', add_help=False,
        help='''Find valid ISBNs inside a file or in a string if no file
        was specified. Searching for ISBNs in files uses progressively more
        resource-intensive methods until some ISBNs are found.''')
    add_general_options(parser_find, remove_opts=['dry-run', 'keep-metadata',
                                                  'reverse', 'symlink-only'])
    add_isbns_options(parser_find, remove_opts=['metadata-fetch-order'])
    add_ocr_options(parser_find)
    parser_find_group = parser_find.add_argument_group(
        title='specific arguments for the subcommand `find`')
    add_isbn_return_separator(parser_find_group)
    parser_find_input_group = parser_find.add_argument_group(
        title='input argument')
    parser_find_input_group.add_argument(
        'input_data',
        help='''Can either be the path to a file or a string. The input will
            be searched for ISBNs.''')
    parser_find.set_defaults(func=find_isbns.find)
    # ======================
    # rename-calibre-library
    # ======================
    # create the parser for the "rename-calibre-library" command
    parser_rename = subparsers.add_parser(
        'rename', add_help=False,
        help='''Traverses a calibre library folder and renames all the book
        files in it by reading their metadata from calibre's metadata.opf
        files. The book files along with their corresponding metadata can
        either be moved or symlinked (if the flag `--symlink-only` is enabled).
        Also, activate the flag `--dry-run` for testing purposes since no file
        rename/move/symlink/etc. operations will actually be executed.''')
    add_general_options(parser_rename, remove_opts=['keep-metadata'])
    add_isbns_options(parser_rename, remove_opts=['isbn-direct-grep-files',
                                                  'isbn-ignored-files',
                                                  'reorder-files-for-grep',
                                                  'metadata-fetch-order'])
    add_input_output_options(parser_rename)
    parser_rename_group = parser_rename.add_argument_group(
        title='specific arguments for the subcommand `rename`')
    parser_rename_group.add_argument(
        '--sm', '--save-metadata', dest='save_metadata',
        choices=['disable', 'opfcopy', 'recreate'],
        help='''This specifies whether metadata files will be saved together
        with the renamed ebooks. Value `opfcopy` just copies calibre's
        metadata.opf next to each renamed file with a
        OUTPUT_METADATA_EXTENSION extension, while `recreate` saves a metadata
        file that is similar to the one organize_ebooks.py creates. `disable`
        disables this function.'''
             + _DEFAULT_MSG.format(SAVE_METADATA))
    parser_rename_input_output_group = parser_rename.add_argument_group(
        title='input and output arguments')
    parser_rename_input_output_group.add_argument(
        'calibre_folder',
        help='''Calibre library folder which will be traversed and all its book
            files will be renamed. The renamed files will either be moved or
            symlinked (if the flag `--symlink-only` is enabled) within the folder
            `output-folder`. NOTE: activate the flag `--dry-run` if you just want
            to test without moving or symlinking files.''')
    parser_rename_input_output_group.add_argument(
        '-o', '--output-folder', dest='output_folder', metavar='PATH',
        help='''This is the output folder the renamed books will be moved to.
        The default value is the current working directory.''' +
             _DEFAULT_MSG.format(OUTPUT_FOLDER))
    parser_rename.set_defaults(func=rename_calibre_library.rename)
    # ==================
    # split-into-folders
    # ==================
    # create the parser for the "split-into-folders" command
    parser_split = subparsers.add_parser(
        'split', add_help=False,
        help='''Split the supplied ebook files (and the accompanying metadata
        files if present) into folders with consecutive names that each contain
        the specified number of files.''')
    parser_general = add_general_options(parser_split,
                                         remove_opts=['symlink-only',
                                                      'keep-metadata'])
    add_input_output_options(parser_general,
                             remove_opts=['output-filename-template'],
                             add_as_group=False)
    parser_split_group = parser_split.add_argument_group(
        title='specific arguments for the subcommand `split`')
    parser_split_group.add_argument(
        '-s', '--start-number', dest='start_number', type=int,
        help='''The number of the first folder.'''
             + _DEFAULT_MSG.format(START_NUMBER))
    # TODO: important explain why we don't use default arg in add_argument()
    parser_split_group.add_argument(
        '-f', '--folder-pattern', dest='folder_pattern', metavar='PATTERN',
        help='''The print format string that specifies the pattern with which
        new folders will be created. By default it creates folders like
        00000000, 00001000, 00002000, .....'''
             + _DEFAULT_MSG.format(FOLDER_PATTERN).replace('%', '%%'))
    parser_split_group.add_argument(
        '--fpf', '--files-per-folder', dest='files_per_folder',
        type=check_positive,
        help='''How many files should be moved to each folder.'''
             + _DEFAULT_MSG.format(FILES_PER_FOLDER))
    parser_split_input_output_group = parser_split.add_argument_group(
        title='input and output arguments')
    parser_split_input_output_group.add_argument(
        'folder_with_books',
        help='''Folder with books which will be recursively scanned for files.
            The found files (and the accompanying metadata files if present) will
            be split into folders with consecutive names that each contain the
            specified number of files.''')
    # TODO: important update README because args moved from places
    parser_split_input_output_group.add_argument(
        '-o', '--output-folder', dest='output_folder', metavar='PATH',
        help='''The output folder in which all the new consecutively named
            folders will be created. The default value is the current working
            directory.''' + _DEFAULT_MSG.format(OUTPUT_FOLDER))
    parser_split.set_defaults(func=split_into_folders.split)
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
                  logging_formatter=main_cfg.logging_formatter,
                  subcommand=main_cfg.subcommand)
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
    # Convert
    # ebooktools convert -o ~/test/_ebooktools/output.txt ~/test/_ebooktools/convert_to_txt/pdf_to_convert.pdf
    #
    # Convert with debug and ocr=always
    # ebooktools convert --log-level debug --ocr always -o ~/test/_ebooktools/output.txt ~/test/_ebooktools/convert_to_txt/pdf_to_convert.pdf
    #
    # Edit
    # ebooktools edit -a charm log
    #
    # Find
    # ebooktools find "978-159420172-1 978-1892391810 0000000000 0123456789 1111111111" --log-level debug --log-format console
    # ebooktools find --log-level debug --log-format console ~/test/_ebooktools/find_isbns/Title
    #
    # Rename
    # ebooktools rename
    #
    # Split
    # ebooktools split --fpf 2 -s 1 ~/test/_ebooktools/folder_with_books/ -o ~/test/_ebooktools/output_folder/
    # ebooktools split -o output_folder/ folder_with_books/ --log-level debug --log-format simple
    retcode = main()
    msg = f'Program exited with {retcode}'
    if retcode == 1:
        logger.error(msg)
    else:
        logger.info(msg)
