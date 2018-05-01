import ipdb
import ast
from configparser import ConfigParser, NoOptionError, NoSectionError
import linecache
import os
import re
import sys
import tempfile

from lib import fetch_metadata, get_mimetype, move_or_link_ebook_file_and_metadata, \
    remove_file, search_file_for_isbns, unique_filename


global config_ini
# TODO: add as an environment variable
SETTINGS_PATH = os.path.expanduser('~/PycharmProjects/digital_library/config.ini')


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


def is_pamphlet(file_path):
    print('STDERR: Checking whether {} looks like a pamphlet...'.format(file_path))
    # TODO: check that it does the same as to_lower() @ https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L184
    lowercase_name = os.path.basename(file_path).lower()

    pamphlet_included_files = config_ini['organize-ebooks']['pamphlet_included_files']
    # TODO: check that it does the same as `if [[ "$lowercase_name" =~ $PAMPHLET_INCLUDED_FILES ]];`
    # ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/organize-ebooks.sh#L73
    if re.match(pamphlet_included_files, lowercase_name):
        parts = []
        # TODO: check that it does the same as `matches="[$(echo "$lowercase_name" | grep -oE "$PAMPHLET_INCLUDED_FILES" | paste -sd';')]"`
        # TODO: they are using grep -oE
        # ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/organize-ebooks.sh#L74
        matches = re.finditer(pamphlet_included_files, lowercase_name)
        for i, match in enumerate(matches):
            parts.append(match.group())
        matches = ';'.join(parts)
        print('Parts of the filename match the pamphlet include regex: [{}]'.format(matches))
        return True

    print('STDERR: The file does not match the pamphlet include regex, continuing...')

    pamphlet_excluded_files = config_ini['organize-ebooks']['pamphlet_excluded_files']
    # TODO: check that it does the same as `if [[ "$lowercase_name" =~ $PAMPHLET_EXCLUDED_FILES ]]; then`
    # ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/organize-ebooks.sh#L79
    if re.match(pamphlet_excluded_files, lowercase_name):
        parts = []
        # TODO: check that it does the same as `matches="[$(echo "$lowercase_name" | grep -oE "$PAMPHLET_EXCLUDED_FILES" | paste -sd';')]"`
        # TODO: they are using grep -oE
        # ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/organize-ebooks.sh#L80
        matches = re.finditer(pamphlet_excluded_files, lowercase_name)
        for i, match in enumerate(matches):
            parts.append(match.group())
        matches = ';'.join(parts)
        print('Parts of the filename match the pamphlet exclude regex: [{}]'.format(matches))
        # TODO: [ERROR] they are returning 1, but it should be returning 0
        # because the file is considered as a pamphlet
        return True

    print('STDERR: The file does not match the pamphlet exclude regex, continuing...')

    mimetype = get_mimetype(file_path)


# Arguments: path, reason (optional)
def organize_by_filename_and_meta(old_path, prev_reason):
    prev_reason = '{}; '.format(prev_reason)
    print('STDERR: Organizing {} by non-ISBN metadata and filename...'.format(old_path))
    # TODO: check that it does the same as to_lower() @ https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L184
    lowercase_name = os.path.basename(old_path).lower()
    without_isbn_ignore = config_ini['organize-ebooks']['without_isbn_ignore']
    # TODO: check that it does the same as `if [[ "$WITHOUT_ISBN_IGNORE" != "" && "$lowercase_name" =~ $WITHOUT_ISBN_IGNORE ]]`
    # ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/organize-ebooks.sh#L161
    if without_isbn_ignore and re.match(without_isbn_ignore, lowercase_name):
        parts = []
        # TODO: check that it does the same as `matches="[$(echo "$lowercase_name" | grep -oE "$WITHOUT_ISBN_IGNORE" | paste -sd';')]`
        # TODO: they are using grep -oE
        # ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/organize-ebooks.sh#L163
        matches = re.finditer(without_isbn_ignore, lowercase_name)
        for i, match in enumerate(matches):
            parts.append(match.group())
        matches = ';'.join(parts)
        print('Parts of the filename match the ignore regex: [{}]'.format(matches))
        skip_file(old_path, '{}File matches the ignore regex ({})'.format(prev_reason, matches))
        return
    else:
        print('STDERR: File does not match the ignore regex, continuing...')


# Sequentially tries to fetch metadata for each of the supplied ISBNs; if any
# is found, writes it to a tmp .txt file and calls organize_known_ebook()
# Arguments: path, isbns (coma-separated)
# TODO: in their description, they refer to `organize_known_ebook` but it should
# be `move_or_link_ebook_file_and_metadata`, ref.: https://bit.ly/2HNv3x0
def organize_by_isbns(file_path, isbns):
    ipdb.set_trace()
    organize_by_filename_and_meta('/Users/nova/test/ebook-tools', 'Could not fetch metadata for ISBNs')

    ipdb.set_trace()
    new_path = unique_filename(folder_path=config_ini['organize-ebooks']['output_folder'],
                               basename='Cory Doctorow - [Little Brother #1] - Little Brother (2008) [0765319853].pdf')
    print(new_path)
    ipdb.set_trace()

    isbn_sources = config_ini['general-options']['isbn_metadata_fetch_order']
    isbn_sources = isbn_sources.split(',')
    for isbn in isbns.split(','):
        tmp_file = tempfile.mkstemp(suffix='.txt')[1]
        print('STDERR: Trying to fetch metadata for ISBN {} into temp file {}...'.format(isbn, tmp_file))

        for isbn_source in isbn_sources:
            print('STDERR: Fetching metadata from {} sources...'.format(isbn_source))
            options = '--verbose --isbn={}'.format(isbn)
            metadata = fetch_metadata(isbn_source, options)
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

                print('STDERR: Organizing {} (with {})...'.format(file_path, tmp_file))
                output_folder = config_ini['organize-ebooks']['output_folder']
                new_path = move_or_link_ebook_file_and_metadata(new_folder=output_folder,
                                                                current_ebook_path=file_path,
                                                                current_metadata_path=tmp_file,
                                                                config_ini=config_ini)
                ok_file(file_path, new_path)
                # TODO: they have a `return`, but we should just break from the
                # two for loops to then be able to remove temp file

        # TODO 1: after fetching, writing metadata, and organizing, they return
        # but then the temp files are not removed, ref.: https://bit.ly/2r0sUV8
        # TODO 2: see if the removal of the temp file is done at the right
        # place, i.e. at the end of the first for loop
        print('STDERR: Removing temp file {}...'.format(tmp_file))
        remove_file(tmp_file)

    if config_ini['organize-ebooks']['organize_without_isbn']:
        print('STDERR: Could not organize via the found ISBNs, organizing by filename and metadata instead...')
        organize_by_filename_and_meta(file_path, 'Could not fetch metadata for ISBNs {}'.format(isbns))
    else:
        print('STDERR: Organization by filename and metadata is not turned on, giving up...')
        skip_file(file_path, 'Could not fetch metadata for ISBNs {}; Non-ISBN organization disabled'.format(isbns))


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


# If an option is given as comma-separated arguments, check that each argument
# is enclosed with double quotes and remove any trailing whitespace
def check_comma_options(section_name, option):
    new_option = []
    for s in config_ini[section_name][option].split(','):
        s = s.strip()
        if ' ' in s:
            s = '"{}"'.format(s)
        new_option.append(s)
    config_ini[section_name][option] = ','.join(new_option)


def expand_folder_paths(section_name, option):
    new_option = []
    for s in config_ini[section_name][option].split(','):
        if s:
            new_option.append(os.path.expanduser(s))
    config_ini[section_name][option] = ','.join(new_option)


def add_cwd(section_name, option):
    if not config_ini[section_name][option]:
        config_ini[section_name][option] = os.getcwd()


# Checks and fixes configuration options
# TODO: this function and al. should be in lib.py because it might be used by other scripts
def check_config_ini():
    all_actions = {'general-options/isbn_metadata_fetch_order': ['comma'],
                   'general-options/organize_without_isbn_sources': ['comma'],
                   'general-options/file_sort_flags': ['comma'],
                   'organize-ebooks/ebook_folders': ['comma', 'expand'],
                   'organize-ebooks/output_folder': ['expand', 'cwd'],
                   'organize-ebooks/output_folder_uncertain': ['expand'],
                   'organize-ebooks/output_folder_corrupt': ['expand'],
                   'organize-ebooks/output_folder_pamphlets': ['expand'],
                   'interactive-organizer/output_folders': ['comma', 'expand'],
                   'interactive-organizer/custom_move_base_dir': ['expand'],
                   'interactive-organizer/restore_original_base_dir': ['expand'],
                   'rename-calibre-library/output_folder': ['expand', 'cwd'],
                   'split-into-folders/output_folder': ['expand', 'cwd']
                   }

    for option, actions in all_actions.items():
        section_name, option_name = option.split('/')
        for action in actions:
            # TODO: add a try except if KeyError in config_ini
            if action == 'comma':
                check_comma_options(section_name, option_name)
            elif action == 'expand':
                expand_folder_paths(section_name, option_name)
            elif action == 'cwd':
                add_cwd(section_name, option_name)
            else:
                print('STDERR: action ({}) not recognized'.format(action))
    return 0


if __name__ == '__main__':
    # Read configuration file
    config_ini = read_config(SETTINGS_PATH)
    if config_ini is None:
        # TODO: exit script
        print('ERROR: {} could not be read'.format(SETTINGS_PATH))

    # Check configuration options
    if check_config_ini() == 1:
        # TODO: even if there are invalid options, we will continue in case these
        # options are not necessary for what the user wants to do
        print('ERROR: {} contains invalid options.'.format(SETTINGS_PATH))

    ebook_folders = config_ini['organize-ebooks']['ebook_folders'].split(',')
    for fpath in ebook_folders:
        # Remove white spaces around the folder path
        fpath = os.path.expanduser(fpath).strip()
        print('Recursively scanning {} for files'.format(fpath))
        # TODO: They make use of sorting flags for walking through the files [FILE_SORT_FLAGS]
        # ref.: https://bit.ly/2HuI3YS
        for path, dirs, files in os.walk(fpath):
            for file in files:
                # TODO: add debug_prefixer
                organize_file(file_path=os.path.join(path, file))
