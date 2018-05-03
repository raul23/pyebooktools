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
        if section_name in config_ini and option_name in config_ini[section_name]:
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


def update_config_from_arg_groups(parser):
    ipdb.set_trace()



    for group in groups:
        section_name = group.title
        if section_name in config_ini:
            options = group.__dict__['_group_actions']
            for opt in options:
                if opt.dest in config_ini[section_name]:
                    #config_ini[section_name][opt.dest] =
                    pass



def init(config_path):
    global config_ini
    config_ini = read_config(config_path)

    if config_ini is None:
        # TODO: exit script
        print('ERROR: {} could not be read'.format(config_path))

    # Check configuration options
    check_config_ini()
