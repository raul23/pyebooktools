#!/usr/bin/env python
"""This script is a Python port of `ebook-tools`_ which is written in Shell by
`na--`_.

It is a collection of tools for automated and semi-automated organization and
management of large ebook collections.

References
----------
* `ebook-tools`_

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
"""
import argparse
import codecs
import os
import sys

import pyebooktools
from pyebooktools import (convert_to_txt, edit_config, find_isbns, fix_ebooks,
                          rename_calibre_library, split_into_folders)
from pyebooktools.configs import default_config as default_cfg
from pyebooktools.organize_ebooks import organizer
from pyebooktools.utils.genutils import (get_config_dict, namespace_to_dict,
                                         override_config_with_args, setup_log)
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
CORRUPTION_CHECK_ONLY = default_cfg.corruption_check_only
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
PAMPHLET_EXCLUDED_FILES = default_cfg.pamphlet_excluded_files
PAMPHLET_INCLUDED_FILES = default_cfg.pamphlet_included_files
PAMPHLET_MAX_FILESIZE_KIB = default_cfg.pamphlet_max_filesize_kib
PAMPHLET_MAX_PDF_PAGES = default_cfg.pamphlet_max_pdf_pages
OCR_COMMAND = default_cfg.ocr_command
OCR_ENABLED = default_cfg.ocr_enabled
OCR_ONLY_FIRST_LAST_PAGES = default_cfg.ocr_only_first_last_pages
ORGANIZE_WITHOUT_ISBN = default_cfg.organize_without_isbn
ORGANIZE_WITHOUT_ISBN_SOURCES = default_cfg.organize_without_isbn_sources
OUTPUT_FILE = default_cfg.output_file
OUTPUT_FILENAME_TEMPLATE = default_cfg.output_filename_template
OUTPUT_FOLDER = default_cfg.output_folder
OUTPUT_FOLDER_CORRUPT = default_cfg.output_folder_corrupt
OUTPUT_FOLDER_PAMPHLETS = default_cfg.output_folder_pamphlets
OUTPUT_FOLDER_UNCERTAIN = default_cfg.output_folder_uncertain
OUTPUT_METADATA_EXTENSION = default_cfg.output_metadata_extension
SAVE_METADATA = default_cfg.save_metadata
START_NUMBER = default_cfg.start_number
TESTED_ARCHIVE_EXTENSIONS = default_cfg.tested_archive_extensions
TOKEN_MIN_LENGTH = default_cfg.token_min_length
TOKENS_TO_IGNORE = default_cfg.tokens_to_ignore
WITHOUT_ISBN_IGNORE = default_cfg.without_isbn_ignore

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
    parser_general_group = parser.add_argument_group(title='General options')
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
            '-q', '--quiet', action='store_true',
            help='Enable quiet mode, i.e. nothing will be printed.')
    if not remove_opts.count('verbose'):
        # TODO: important test traceback
        parser_general_group.add_argument(
            '--verbose', action='store_true',
            help='Print various debugging information, e.g. print traceback '
                 'when there is an exception.')
    if not remove_opts.count('dry-run'):
        parser_general_group.add_argument(
            '-d', '--dry-run', dest='dry_run', action='store_true',
            help='If this is enabled, no file rename/move/symlink/etc. '
                 'operations will actually be executed.')
    # TODO: important remove symlink-only and other options for some subcommands
    if not remove_opts.count('symlink-only'):
        parser_general_group.add_argument(
            '--sl', '--symlink-only', dest='symlink_only', action='store_true',
            help='Instead of moving the ebook files, create symbolic links to '
                 'them.')
    if not remove_opts.count('keep-metadata'):
        parser_general_group.add_argument(
            '--km', '--keep-metadata', dest='keep_metadata', action='store_true',
            help='Do not delete the gathered metadata for the organized ebooks, '
                 'instead save it in an accompanying file together with each'
                 'renamed book. It is very useful for semi-automatic '
                 'verification of the organized files with '
                 '`interactive-organizer.sh` or for additional verification, '
                 'indexing or processing at a later date.')
    # TODO: important move reverse and 2 others after into misc
    # TODO: implement more sort options, e.g. random sort
    if not remove_opts.count('reverse'):
        parser_general_group.add_argument(
            '-r', '--reverse', dest='reverse', action='store_true',
            help='If this is enabled, the files will be sorted in reverse (i.e. '
                 'descending) order. By default, they are sorted in ascending '
                 'order.')
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
            title='Options related to the input and output files')
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
            help='''If `keep_metadata` is enabled, this is the extension of the
            additional metadata file that is saved next to each newly renamed file.'''
                 + _DEFAULT_MSG.format(OUTPUT_METADATA_EXTENSION))
    return parser_input_output


# TODO: important, should be in add_isbns_options
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
        title='Options related to extracting ISBNS from files and finding '
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
            beyond their filename. By default, it tries to make the subcommands
            ignore .gif and .svg images, audio, video and executable files and
            fonts.''' + _DEFAULT_MSG.format(ISBN_IGNORED_FILES))
    if not remove_opts.count('reorder-files-for-grep'):
        # TODO: important don't use grep in name of option since we are searching w/o it
        # TODO: test this option (1 or 2 args)
        parser_isbns_group.add_argument(
            "--reorder-files-for-grep", dest='isbn_grep_reorder_files', nargs='+',
            action=required_length(2, 2), metavar='LINES',
            help='''These options specify if and how we should reorder the ebook
            text before searching for ISBNs in it. By default, the first 400 lines
            of the text are searched as they are, then the last 50 are searched in
            reverse and finally the remainder in the middle. This reordering is
            done to improve the odds that the first found ISBNs in a book text
            actually belong to that book (ex. from the copyright section or the
            back cover), instead of being random ISBNs mentioned in the middle of
            the book. No part of the text is searched twice, even if these regions
            overlap. Set it to `False` to disable the functionality and
            `first_lines last_lines` to enable it with the specified values.'''
                 + _DEFAULT_MSG.format(ISBN_GREP_REORDER_FILES))
    if not remove_opts.count('metadata-fetch-order'):
        parser_isbns_group.add_argument(
            "---mfo", "---metadata-fetch-order", nargs='+',
            dest='isbn_metadata_fetch_order', metavar='METADATA_SOURCE',
            help='''This option allows you to specify the online metadata
            sources and order in which the subcommands will try searching in
            them for books by their ISBN. The actual search is done by
            calibre's `fetch-ebook-metadata` command-line application, so any
            custom calibre metadata plugins can also be used. To see the
            currently available options, run `fetch-ebook-metadata --help` and
            check the description for the `--allowed-plugin` option. If you use
            Calibre versions that are older than 2.84, it's required to
            manually set this option to an empty string.'''
                 + _DEFAULT_MSG.format(ISBN_METADATA_FETCH_ORDER))
    # TODO: return parser for other functions too?
    return parser_isbns_group


def add_non_isbn_options(parser):
    parser_non_isbn_group = parser.add_argument_group(
        title='Options for extracting and searching non-ISBN metadata')
    parser_non_isbn_group.add_argument(
        '--token-min-length', dest='token_min_length', metavar='LENGTH',
        type=int,
        help='''When files and file metadata are parsed, they are split into
        words (or more precisely, either alpha or numeric tokens) and ones
        shorter than this value are ignored. By default, single and two
        character number and words are ignored.'''
             + _DEFAULT_MSG.format(TOKEN_MIN_LENGTH))
    parser_non_isbn_group.add_argument(
        '--tokens-to-ignore', dest='tokens_to_ignore', metavar='TOKENS',
        help='''A regular expression that is matched against the
        filename/author/title tokens and matching tokens are ignored. The
        default regular expression includes common words that probably hinder
        online metadata searching like book, novel, series, volume and others,
        as well as probable publication years like (so 1999 is ignored while
        2033 is not). You can see it in lib.py.'''
             + _DEFAULT_MSG.format(TOKENS_TO_IGNORE))
    parser_non_isbn_group.add_argument(
        '--owis', '--organize-without-isbn-sources', nargs='+',
        dest='organize_without_isbn_sources', metavar='METADATA_SOURCE',
        help='''This option allows you to specify the online metadata sources
        in which the subcommands will try searching for books by non-ISBN
        metadata (i.e. author and title). The actual search is done by
        calibre's `fetch-ebook-metadata` command-line application, so any
        custom calibre metadata plugins can also be used. To see the currently
        available options, run `fetch-ebook-metadata --help` and check the
        description for the `--allowed-plugin` option. Because Calibre versions
        older than 2.84 don't support the `--allowed-plugin` option, if you
        want to use such an old Calibre version you should manually set
        `organize_without_isbn_sources` to an empty string.'''
             + _DEFAULT_MSG.format(ORGANIZE_WITHOUT_ISBN_SOURCES))


# Options for OCR
def add_ocr_options(parser, remove_opts=None):
    remove_opts = init_list(remove_opts)
    parser_convert_group = parser.add_argument_group(title='Options for OCR')
    if not remove_opts.count('ocr-enabled'):
        parser_convert_group.add_argument(
            "--ocr", "--ocr-enabled", dest='ocr_enabled',
            choices=['always', 'true', 'false'],
            help='''Whether to enable OCR for .pdf, .djvu and image files. It is
                disabled by default.''')
    if not remove_opts.count('ocr-only-first-last-pages'):
        # TODO: improve presentation of default values (and other places)
        # e.g. right now: (7,3)
        # what we want: 7 3
        parser_convert_group.add_argument(
            "--ocrop", "--ocr-only-first-last-pages",
            dest='ocr_only_first_last_pages', metavar='PAGES', nargs=2,
            help='''Value n,m instructs the subcommands to convert only the
            first n and last m pages when OCR-ing ebooks.'''
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
def required_length(nmin, nmax):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) <= nmax:
                if nmin == nmax:
                    msg = 'argument "{f}" requires {nmin} arguments'.format(
                        f=self.dest, nmin=nmin, nmax=nmax)
                else:
                    msg='argument "{f}" requires between {nmin} and {nmax} ' \
                        'arguments'.format(f=self.dest, nmin=nmin, nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength


# Ref.: https://stackoverflow.com/a/32891625/14664104
class MyFormatter(argparse.HelpFormatter):
    """
    Corrected _max_action_length for the indenting of subactions
    """

    def add_argument(self, action):
        if action.help is not argparse.SUPPRESS:

            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            current_indent = self._current_indent
            for subaction in self._iter_indented_subactions(action):
                # compensate for the indent that will be added
                indent_chg = self._current_indent - current_indent
                added_indent = 'x' * indent_chg
                invocations.append(added_indent + get_invocation(subaction))
            # print('inv', invocations)

            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length,
                                          action_length)

            # add the item to the list
            self._add_item(self._format_action, [action])

    # Ref.: https://stackoverflow.com/a/23941599/14664104
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    #parts.append('%s %s' % (option_string, args_string))
                    parts.append('%s' % option_string)
                parts[-1] += ' %s'%args_string
            return ', '.join(parts)


def setup_argparser():
    """Setup the argument parser for the command-line script.

    Returns
    -------
    parser : argparse.ArgumentParser
        Argument parser.

    """
    width = os.get_terminal_size().columns - 5
    # Setup the parser
    parser = argparse.ArgumentParser(
        description='This program is a Python port of ebook-tools written in '
                    'Shell by na-- (See https://github.com/na--/ebook-tools). '
                    'It is a collection of tools for automated and '
                    'semi-automated organization and management of large ebook '
                    'collections. See subcommands below for a list of the tools '
                    'that can be used.',
        # RawDescriptionHelpFormatter
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=30, width=width))
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
        # TODO: important, test without subcommand
        subparsers = parser.add_subparsers(
            title='subcommands', description=None, dest='subcommand', help=None)
    # TODO: add aliases, see https://bit.ly/3s2fq87
    # ==========
    # Edit files
    # ==========
    # create the parser for the "edit" command
    desc = 'Edit a configuration file, either the main configuration file ' \
           f'(`{_MAIN_CFG}`) or the logging configuration file (`{_LOG_CFG}`).'
    parser_edit = subparsers.add_parser(
        'edit', add_help=False,
        usage=f'%(prog)s [OPTIONS] {{{_MAIN_CFG}, {_LOG_CFG}}}\n\n{desc}',
        help='Edit a configuration file.',
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=50, width=width))
    add_general_options(parser_edit, remove_opts=['dry-run', 'keep-metadata',
                                                  'reverse', 'symlink-only'])
    parser_edit_group = parser_edit.add_argument_group(
        title='Specific options for the subcommand `test`')
    parser_edit_mutual_group = parser_edit_group.add_mutually_exclusive_group()
    parser_edit_mutual_group.add_argument(
        '-a', '--app', metavar='NAME', nargs='?',
        help='Name of the application to use for editing the config file. If '
             'no name is given, then the default application for opening this '
             'type of file will be used.')
    parser_edit_mutual_group.add_argument(
        '-r', '--reset', action='store_true',
        help=f'Reset a configuration file (`{_MAIN_CFG}` or `{_LOG_CFG}`) '
             'with factory default values.')
    parser_edit_input_group = parser_edit.add_argument_group(
        title='input argument')
    parser_edit_input_group.add_argument(
        'cfg_type', choices=[_MAIN_CFG, _LOG_CFG],
        help='The config file to edit which can either be the main '
             f'configuration file (`{_MAIN_CFG}`) or the logging configuration '
             f'file (`{_LOG_CFG}`).')
    parser_edit.set_defaults(func=parse_edit_args)
    # ==============
    # Convert to txt
    # ==============
    # create the parser for the "convert" command
    name_input = 'input_file'
    desc = 'Convert the supplied ebook file to a text file. It can optionally ' \
           'also use *OCR* for .pdf, .djvu and image files.'
    parser_convert = subparsers.add_parser(
        'convert', add_help=False,
        usage=f'%(prog)s [OPTIONS] {name_input}\n\n{desc}',
        help='Convert the supplied file to a text file.',
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=40, width=width))
    add_general_options(parser_convert, remove_opts=['dry-run', 'keep-metadata',
                                                     'reverse', 'symlink-only'])
    add_ocr_options(parser_convert)
    parser_convert_group = parser_convert.add_argument_group(
        title='Input and output options')
    parser_convert_group.add_argument(
        name_input,
        help='''The input file to be converted to a text file.''')
    parser_convert_group.add_argument(
        '-o', '--output-file', dest='output_file', metavar='OUTPUT',
        help='The output file text. By default, it is saved in the current '
             'working directory.' + _DEFAULT_MSG.format(OUTPUT_FILE))
    parser_convert.set_defaults(func=convert_to_txt.convert)
    # ==========
    # Find ISBNs
    # ==========
    # create the parser for the "find" command
    name_input = 'input_data'
    desc = 'Find valid ISBNs inside a file or in a string if no file was ' \
           'specified. \nSearching for ISBNs in files uses progressively more ' \
           'resource-intensive methods until some ISBNs are found.'
    parser_find = subparsers.add_parser(
        'find', add_help=False,
        usage=f'%(prog)s [OPTIONS] {name_input}\n\n{desc}',
        help='Find valid ISBNs inside a file or in a string.',
        formatter_class=lambda prog: MyFormatter(
            prog, max_help_position=52, width=width))
    add_general_options(parser_find, remove_opts=['dry-run', 'keep-metadata',
                                                  'reverse', 'symlink-only'])
    add_isbns_options(parser_find, remove_opts=['metadata-fetch-order'])
    add_ocr_options(parser_find)
    parser_find_group = parser_find.add_argument_group(
        title='Specific options for the subcommand `find`')
    add_isbn_return_separator(parser_find_group)
    parser_find_input_group = parser_find.add_argument_group(
        title='input argument')
    parser_find_input_group.add_argument(
        name_input,
        help='Can either be the path to a file or a string. The input will be '
             'searched for ISBNs.')
    parser_find.set_defaults(func=find_isbns.find)
    # ==========
    # fix-ebooks
    # ==========
    # create the parser for the "fix-ebooks" command
    name_input = 'input_data'
    desc = 'Not implemented yet!'
    parser_fix = subparsers.add_parser(
        'fix', add_help=False,
        usage=f'%(prog)s [OPTIONS] {name_input}\n\n{desc}',
        # Tries to fix corrupted ebook files. For the moment, only PDF files
        # are supported.
        help=desc,
        formatter_class=lambda prog: MyFormatter(prog, max_help_position=52,
                                                 width=width))
    add_general_options(parser_fix, remove_opts=['dry-run', 'symlink-only',
                                                 'keep-metadata'])
    parser_fix_input_output_group = parser_fix.add_argument_group(
        title='Input and output options')
    parser_fix_input_output_group.add_argument(
        'input_data',
        help='Can either be a corrupted file or a folder containing the '
             'corrupted ebook files that need to be fixed.')
    parser_fix.set_defaults(func=fix_ebooks.fix)
    # ===============
    # organize-ebooks
    # ===============
    # create the parser for the "organize-ebooks" command
    name_input = 'folder_to_organize'
    desc = 'Automatically organize folders with potentially huge amounts of ' \
           'unorganized ebooks.\nThis is done by renaming the files with ' \
           'proper names and moving them to other folders.'
    parser_organize = subparsers.add_parser(
        'organize', add_help=False,
        usage=f'%(prog)s [OPTIONS] {name_input}\n\n{desc}',
        help='Automatically organize folders.',
        formatter_class=lambda prog: MyFormatter(prog, max_help_position=52,
                                                 width=width))
    add_general_options(parser_organize)
    add_isbns_options(parser_organize)
    add_ocr_options(parser_organize)
    add_non_isbn_options(parser_organize)
    add_input_output_options(parser_organize)
    parser_organize_group = parser_organize.add_argument_group(
        title='Specific options for the subcommand `organize`')
    parser_organize_group.add_argument(
        "--cco", "--corruption-check-only", dest='corruption_check_only',
        action="store_true",
        help='Do not organize or rename files, just check them for corruption '
             '(ex. zero-filled files, corrupt archives or broken .pdf files). '
             'Useful with the `output-folder-corrupt` option.')
    parser_organize_group.add_argument(
        '--tested-archive-extensions', dest='tested_archive_extensions',
        metavar='REGEX',
        help='A regular expression that specifies which file extensions will '
             'be tested with `7z t` for corruption.'
             + _DEFAULT_MSG.format(TESTED_ARCHIVE_EXTENSIONS))
    parser_organize_group.add_argument(
        '--owi', '--organize-without-isbn', dest='organize_without_isbn',
        action="store_true",
        help='Specify whether the script will try to organize ebooks if there '
             'were no ISBN found in the book or if no metadata was found '
             'online with the retrieved ISBNs. If enabled, the script will '
             'first try to use calibre\'s `ebook-meta` command-line tool to '
             'extract the author and title metadata from the ebook file. The '
             'script will try searching the online metadata sources '
             '(`organize_without_isbn_sources`) by the extracted author & '
             'title and just by title. If there is no useful metadata or '
             'nothing is found online, the script will try to use the filename '
             'for searching.')
    parser_organize_group.add_argument(
        '--wii', '--without-isbn-ignore', dest='without_isbn_ignore',
        metavar='REGEX',
        help='This is a regular expression that is matched against lowercase'
             'filenames. All files that do not contain ISBNs are matched '
             'against it and matching files are ignored by the script, even if '
             '`organize-without-isbn` is true. The default value is calibrated '
             'to match most periodicals (magazines, newspapers, etc.) so the '
             'script can ignore them.'
             + _DEFAULT_MSG.format('complex default value, see the main config '
                                   'file'))
    # + _DEFAULT_MSG.format(WITHOUT_ISBN_IGNORE))
    parser_organize_group.add_argument(
        '--pamphlet-included-files', dest='pamphlet_included_files',
        metavar='REGEX',
        help='This is a regular expression that is matched against lowercase'
             'filenames. All files that do not contain ISBNs and do not match'
             '`without_isbn_ignore` are matched against it and matching files '
             'are considered pamphlets by default. They are moved to '
             '`output_folder_pamphlets` if set, otherwise they are ignored.'
             + _DEFAULT_MSG.format(PAMPHLET_INCLUDED_FILES))
    parser_organize_group.add_argument(
        '--pamphlet-excluded-files', dest='pamphlet_excluded_files',
        metavar='REGEX',
        help='This is a regular expression that is matched against lowercase'
             'filenames. If files do not contain ISBNs and match against it, '
             'they are NOT considered as pamphlets, even if they have a small '
             'size or number of pages.'
             + _DEFAULT_MSG.format(PAMPHLET_EXCLUDED_FILES))
    parser_organize_group.add_argument(
        '--pamphlet-max-pdf-pages', dest='pamphlet_max_pdf_pages', type=int,
        metavar='PAGES',
        help='.pdf files that do not contain valid ISBNs and have a lower'
             'number pages than this are considered pamplets/non-ebook '
             'documents.' + _DEFAULT_MSG.format(PAMPHLET_MAX_PDF_PAGES))
    parser_organize_group.add_argument(
        '--pamphlet-max-filesize-kb', dest='pamphlet_max_filesize_kib', type=int,
        metavar='SIZE',
        help='Other files that do not contain valid ISBNs and are below this'
             'size in KBs are considered pamplets/non-ebook documents.'
             + _DEFAULT_MSG.format(PAMPHLET_MAX_FILESIZE_KIB))
    add_isbn_return_separator(parser_organize_group)
    parser_organize_input_output_group = parser_organize.add_argument_group(
        title='Input and output options')
    parser_organize_input_output_group.add_argument(
        name_input,
        help='Folder containing the ebook files that need to be organized.')
    parser_organize_input_output_group.add_argument(
        '-o', '--output-folder', dest='output_folder', metavar='PATH',
        help='The folder where ebooks that were renamed based on the ISBN'
             'metadata will be moved to.' + _DEFAULT_MSG.format(OUTPUT_FOLDER))
    parser_organize_input_output_group.add_argument(
        '--ofu', '--output-folder-uncertain', dest='output_folder_uncertain',
        metavar='PATH',
        help='If `organize_without_isbn` is enabled, this is the folder to'
             'which all ebooks that were renamed based on non-ISBN metadata '
             'will be moved to.' + _DEFAULT_MSG.format(OUTPUT_FOLDER_UNCERTAIN))
    parser_organize_input_output_group.add_argument(
        '--ofc', '--output-folder-corrupt', dest='output_folder_corrupt',
        metavar='PATH',
        help='If specified, corrupt files will be moved to this folder.'
             + _DEFAULT_MSG.format(OUTPUT_FOLDER_CORRUPT))
    parser_organize_input_output_group.add_argument(
        '--ofp', '--output-folder-pamphlets', dest='output_folder_pamphlets',
        metavar='PATH',
        help='If specified, pamphlets will be moved to this folder.'
             + _DEFAULT_MSG.format(OUTPUT_FOLDER_PAMPHLETS))
    parser_organize.set_defaults(func=organizer.organize)
    # =============
    # Remove-extras
    # =============
    # create the parser for the "remove-ebooks" command
    name_input = 'input_data'
    desc = 'Not implemented yet!'
    parser_fix = subparsers.add_parser(
        'remove', add_help=False,
        usage=f'%(prog)s [OPTIONS] {name_input}\n\n{desc}',
        # Removes extras (e.g. annotations and bookmarks) from ebook files.
        # For the moment, only PDF files are supported.
        help=desc,
        formatter_class=lambda prog: MyFormatter(prog, max_help_position=52,
                                                 width=width))
    add_general_options(parser_fix, remove_opts=['dry-run', 'symlink-only',
                                                 'keep-metadata'])
    parser_fix_input_output_group = parser_fix.add_argument_group(
        title='Input and output options')
    parser_fix_input_output_group.add_argument(
        'input_data',
        help='Can either be a file or a folder containing the ebook files '
             'whose extras will be removed.')
    # ======================
    # rename-calibre-library
    # ======================
    # create the parser for the "rename-calibre-library" command
    name_input = 'folder_to_organize'
    desc = 'Traverse a calibre library folder and rename all the book files ' \
           'in it by reading their metadata from calibre\'s metadata.opf ' \
           'files.\nThe book files are then either moved or symlinked (if ' \
           'the `--symlink-only` flag is enabled) to the output folder along ' \
           'with their corresponding metadata files.\nAlso, activate the ' \
           '`--dry-run` flag for testing purposes since no file ' \
           'rename/move/symlink/etc. operations will actually be executed.'
    parser_rename = subparsers.add_parser(
        'rename', add_help=False,
        usage=f'%(prog)s [OPTIONS] {name_input}\n\n{desc}',
        help='Traverse a calibre library folder and rename all the book files '
             'in it.',
        formatter_class=lambda prog: MyFormatter(prog, max_help_position=52,
                                                 width=width))
    add_general_options(parser_rename, remove_opts=['keep-metadata'])
    add_isbns_options(parser_rename, remove_opts=['isbn-direct-grep-files',
                                                  'isbn-ignored-files',
                                                  'reorder-files-for-grep',
                                                  'metadata-fetch-order'])
    add_input_output_options(parser_rename)
    parser_rename_group = parser_rename.add_argument_group(
        title='Specific options for the subcommand `rename`')
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
        title='Input and output options')
    parser_rename_input_output_group.add_argument(
        'calibre_folder',
        help='''Calibre library folder which will be traversed and all the book
            files in it will be renamed. The renamed files will either be moved
            or symlinked (if the flag `--symlink-only` is enabled) to the
            output folder along with their corresponding metadata files. NOTE:
            activate the `--dry-run` flag if you just want to test without
            moving or symlinking files.''')
    parser_rename_input_output_group.add_argument(
        '-o', '--output-folder', dest='output_folder', metavar='PATH',
        help='''This is the output folder the renamed books will be moved to.
        The default value is the current working directory.'''
             + _DEFAULT_MSG.format(OUTPUT_FOLDER))
    parser_rename.set_defaults(func=rename_calibre_library.rename)
    # ==================
    # split-into-folders
    # ==================
    # create the parser for the "split-into-folders" command
    name_input = 'folder_with_books'
    desc = 'Split the supplied ebook files (and the accompanying metadata' \
           'files if present) into folders with consecutive names that each ' \
           'contain the specified number of files.'
    parser_split = subparsers.add_parser(
        'split', add_help=False,
        usage=f'%(prog)s [OPTIONS] {name_input}\n\n{desc}',
        help='Split the supplied ebook files into folders.',
        formatter_class=lambda prog: MyFormatter(prog, max_help_position=52,
                                                 width=width))
    parser_general = add_general_options(parser_split,
                                         remove_opts=['symlink-only',
                                                      'keep-metadata'])
    add_input_output_options(parser_general,
                             remove_opts=['output-filename-template'],
                             add_as_group=False)
    parser_split_group = parser_split.add_argument_group(
        title='Specific options for the subcommand `split`')
    parser_split_group.add_argument(
        '-s', '--start-number', dest='start_number', type=int,
        help='The number of the first folder.'
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
        title='Input and output options')
    parser_split_input_output_group.add_argument(
        name_input,
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
        if args.subcommand is None:
            # NOTE: this happens for py <= 3.6 (no required arg found)
            # TODO: important, find way to get usage msg already
            # TODO: important, update subcommands in usage msg
            msg = 'usage: ebooktools [-h] [-v] {edit,convert,find,rename,' \
                  'split}... \nebooktools: error: the following arguments ' \
                  'are required: subcommand'
            print(msg)
            sys.exit(1)
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
    # ebooktools convert ~/test/_ebooktools/convert_to_txt/pdf_to_convert.pdf -o ~/test/_ebooktools/output.txt
    #
    # Convert with debug and ocr=always
    # ebooktools convert --log-level debug --ocr always ~/test/_ebooktools/convert_to_txt/pdf_to_convert.pdf -o ~/test/_ebooktools/output.txt
    #
    # Edit
    # ebooktools edit -a charm log
    #
    # Find in a string
    # ebooktools find "978-159420172-1 978-1892391810 0000000000 0123456789 1111111111" --log-level debug --log-format console
    #
    # Find in a PDF file
    # ebooktools find --log-level debug --log-format console ~/test/_ebooktools/find_isbns/Title
    #
    # Organize
    # ebooktools organize ~/test/_ebooktools/organize/folder_to_organize/ --log-format only_msg -o ~/test/_ebooktools/organize/output_folder
    # --ofu ~/test/_ebooktools/oranize/output_folder_uncertain/ --pamphlet-max-pdf-pages 10 --owi
    #
    # Organize with output folder (no corrupted files) with dry-run (no metadata copied)
    # ebooktools organize ~/test/_ebooktools/organize/folder_to_organize/ --log-format only_msg
    # -o ~/test/_ebooktools/organize/output_folder -d
    #
    # ebooktools organize ~/test/_ebooktools/organize/folder_to_organize/ --log-format only_msg
    #
    # Organize with corrupted files
    # ebooktools organize ~/test/_ebooktools/organize/corrupted_files/ --log-level debug -o ~/test/_ebooktools/organize/output_folder/
    #
    # Organize with corrupted files and corrupted folder
    # ebooktools organize ~/test/_ebooktools/organize/folder_to_organize -o ~/test/_ebooktools/organize/output_folder/
    # --log-format only_msg --ofc ~/test/_ebooktools/organize/output_folder_corrupt/
    #
    # -d, --dry-run
    # --sl, --symlink-only
    # Keep metadata: --km
    #
    # Organize with uncertain folder
    # ebooktools organize ~/test/_ebooktools/organize/folder_to_organize/ --log-format only_msg
    # -o ~/test/_ebooktools/organize/output_folder --ofu ~/test/_ebooktools/oganize/output_folder_uncertain/
    # --pamphlet-max-pdf-pages 10 --owi --log-level info --km
    #
    # Rename using own calibre library
    # ebooktools rename --sm opfcopy --sl --log-format console ~/test/_ebooktools/rename_calibre_library/example_07/
    # -o ~/test/_ebooktools/rename_calibre_library/output_folder/
    #
    # Rename using real calibre library
    # ebooktools rename --sm opfcopy --sl --log-format console ~/Calibre\ Library/ -o ~/test/_ebooktools/rename_calibre_library/output_folder/
    #
    # Split
    # ebooktools split --fpf 2 -s 1 ~/test/_ebooktools/folder_with_books/ -o ~/test/_ebooktools/output_folder/
    # ebooktools split --log-level debug --log-format simple folder_with_books/ -o output_folder/
    retcode = main()
    msg = f'Program exited with {retcode}'
    if retcode == 1:
        logger.error(msg)
    else:
        logger.info(msg)
