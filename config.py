import ipdb
import os

from utils.gen import read_config


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
        if not(section_name in config_ini and option_name in config_ini[section_name]):
            continue
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


def init(config_path):
    global config_ini
    config_ini = read_config(config_path)

    if config_ini is None:
        # TODO: exit script
        print('ERROR: {} could not be read'.format(config_path))

    # Check configuration options
    if check_config_ini() == 1:
        # NOTE: even if there are invalid options, we will continue in case
        # these invalid options are not necessary for what the user wants to do next
        print('ERROR: {} contains invalid options.'.format(config_path))
