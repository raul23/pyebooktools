import ipdb
import logging
import os

from utils.gen import read_config


# Build logger name based on module's package and module name
# i.e. package_name.module_name
# NOTE: all loggers that start with `package_name` will inherit from the same
# logger named `package_name` that is defined in the logging configuration file 'log_conf.json'
logger = logging.getLogger('{}.{}'.format(os.path.basename(os.path.dirname(__file__)), __name__))


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
    # Get all ArgumentGroups and arguments
    groups = parser.__dict__['_action_groups']
    args = parser.parse_args().__dict__

    # Iterate over all the ArgumentGroups and only process the correct ones
    # (they should be after the first two groups which are the 'positional arguments'
    # and 'optional arguments' ArgumentGroups)
    for group in groups:
        # Title should correspond to a section name from the config.ini file
        section_name = group.title
        if section_name in ['positional arguments', 'optional arguments'] or \
                section_name not in config_ini:
            print('[DEBUG] Invalid section name: {}'.format(section_name))
            continue
        # Get the options for the given ArgumentGroup
        options = group.__dict__['_group_actions']
        for opt in options:
            # Is it a valid option?
            if opt.dest in config_ini[section_name]:
                # Update option if necessary
                if args[opt.dest] != config_ini[section_name][opt.dest]:
                    old_value = config_ini[section_name][opt.dest]
                    new_value = args[opt.dest]
                    config_ini[section_name][opt.dest] = new_value
                    print('[INFO] Option {}/{} is updated: {}  -->  {}'.format(section_name, opt.dest, old_value, new_value))
            else:
                # Invalid option name, e.g. the program version is not added in `config_ini`
                print('[DEBUG] Invalid option name: {}'.format(opt.dest))
                ipdb.set_trace()
    ipdb.set_trace()


def init(config_path):
    global config_ini
    config_ini = read_config(config_path)

    if config_ini is None:
        # TODO: exit script
        print('[ERROR] {} could not be read'.format(config_path))

    # Check configuration options
    check_config_ini()
