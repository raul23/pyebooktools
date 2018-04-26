import ipdb
import ast
from configparser import ConfigParser, NoOptionError, NoSectionError
import linecache
import os
import sys
import tempfile

from lib import fetch_metadata, move_or_link_ebook_file_and_metadata, remove_file, search_file_for_isbns


# Environment variables
SETTINGS_PATH = os.path.expanduser('~/PycharmProjects/digital_library/config.ini')


global config_ini


# TODO: add function in utilities
def print_exception(error=None):
    """
    For a given exception, PRINTS filename, line number, the line itself, and
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


# TODO: add function in utilities
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


def check_file_for_corruption():
    return ''


def skip_file(file_path, reason):
    raise NotImplementedError('skip_file is not implemented!')


def ok_file(old_path, new_path):
    return ''


# Arguments: path, reason (optional)
def organize_by_filename_and_meta(file_path, reason=''):
    raise NotImplementedError('organize_by_filename_and_meta is not implemented!')


# Sequentially tries to fetch metadata for each of the supplied ISBNs; if any
# is found, writes it to a tmp .txt file and calls organize_known_ebook()
# Arguments: path, isbns (coma-separated)
# TODO: in their description, they refer to `organize_known_ebook` but it should
# be `move_or_link_ebook_file_and_metadata`, ref.: https://bit.ly/2HNv3x0
def organize_by_isbns(file_path, isbns):
    isbn_sources = config_ini['general-options']['isbn_metadata_fetch_order']
    isbn_sources = isbn_sources.split(',')
    for isbn in isbns.split(','):
        tmp_file = tempfile.mkstemp(suffix='.txt')[1]
        print('STDERR: Trying to fetch metadata for ISBN {} into temp file {}...'.format(isbn, tmp_file))

        for isbn_source in isbn_sources:
            print('STDERR: Fetching metadata from {} sources...'.format(isbn_source))
            ipdb.set_trace()
            options = '--verbose --isbn={}'.format(isbn)
            metadata = fetch_metadata(isbn_source, options)
            ipdb.set_trace()
            if metadata:
                with open(tmp_file, 'w') as f:
                    f.write(metadata)
                # TODO: is it necessary to sleep after fetching the metadata from
                # online sources like they do? The code is run sequentially, so
                # we are executing the rest of the code here once fetch_metadata()
                # is done, ref.: https://bit.ly/2vV9MfU
                print('STDERR: Successfully fetched metadata: ')
                print(metadata)
                # TODO: add debug_prefixer

                print('Adding additional metadata to the end of the metadata file...')
                more_metadata = 'ISBN                : {}\n' \
                                'All found ISBNs     : {}\n' \
                                'Old file path       : {}\n' \
                                'Metadata source     : {}'.format(isbn, isbns, file_path, isbn_source)
                print(more_metadata)
                with open(tmp_file, 'a') as f:
                    f.write(more_metadata)

                ipdb.set_trace()
                print('STDERR: Organizing {} (with {})...'.format(file_path, tmp_file))
                output_folder = config_ini['organize-ebooks']['output_folder']
                new_path = move_or_link_ebook_file_and_metadata(output_folder, file_path, tmp_file)
                ok_file(file_path, new_path)
                # TODO: they have a `return`, but we should just break from the
                # two for loops to then be able to remove temp file

        # TODO 1: after fetching, writing metadata, and organizing, they return
        # but then the temp file are not removed, ref.: https://bit.ly/2r0sUV8
        # TODO 2: see if the removal of the temp file is done at the right
        # place, i.e. at the end of the first for loop
        print('Removing temp file {}...'.format(tmp_file))
        remove_file(tmp_file)


def organize_file(file_path):
    file_err = check_file_for_corruption()
    if file_err:
        print('STDERR: File {} is corrupt with error {}'.format(file_path, file_err))
    elif config_ini['organize-ebooks']['corruption_check_only']:
        print('STDERR: We are only checking for corruption, do not continue organising...')
        skip_file(file_path, 'File appears OK')
    else:
        print('STDERR: File passed the corruption test, looking for ISBNs...')
        isbns = search_file_for_isbns(file_path)
        if isbns:
            print('Organizing {} by ISBNs {}!'.format(file_path, isbns))
            organize_by_isbns(file_path, isbns)
        elif config_ini['organize-ebooks']['organize_without_isbn']:
            print('No ISBNs found for {}, organizing by filename and metadata...'.format(file_path))
            organize_by_filename_and_meta(file_path, 'No ISBNs found')
        else:
            skip_file(file_path, 'No ISBNs found; Non-ISBN organization disabled')
    print('STDERR: =====================================================')


if __name__ == '__main__':
    # Read configuration file
    config_ini = read_config(SETTINGS_PATH)
    if config_ini is None:
        # TODO: exit script
        print("ERROR: {} could not be read".format(SETTINGS_PATH))

    ebook_folders = config_ini['organize-ebooks']['ebook_folders'].split(',')
    for fpath in ebook_folders:
        # strip() in case there are spaces around the folder path
        fpath = fpath.strip()
        print('Recursively scanning {} for files'.format(fpath))
        # TODO: They make use of sorting flags for walking through the files [FILE_SORT_FLAGS]
        # ref.: https://bit.ly/2HuI3YS
        for path, dirs, files in os.walk(fpath):
            for file in files:
                # TODO: add debug_prefixer
                organize_file(file_path=os.path.join(path, file))
