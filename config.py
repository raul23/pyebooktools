import ipdb
import logging
import os

# from utils.gen import read_config_from_ini
from utils.gen import read_config_from_yaml


# Build logger name based on module's package and module name
# i.e. package_name.module_name
# NOTE: all loggers that start with `package_name` will inherit from the same
# logger named `package_name` that is defined in the logging configuration file 'log_conf.json'
logger = logging.getLogger('{}.{}'.format(os.path.basename(os.path.dirname(__file__)), __name__))


# If an option is given as comma-separated arguments, check that each argument
# is enclosed with double quotes and remove any trailing whitespace
def check_comma_options(value):
    new_option = []
    for s in value.split(','):
        s = s.strip()
        if ' ' in s:
            s = '"{}"'.format(s)
        new_option.append(s)
    return ','.join(new_option)


def expand_folder_paths(value):
    new_option = []
    for s in value.split(','):
        if s:
            new_option.append(os.path.expanduser(s))
    return ','.join(new_option)


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
                section_name not in config_dict:
            logger.debug('Invalid section name: {}'.format(section_name))
            continue
        # Get the options for the given ArgumentGroup
        options = group.__dict__['_group_actions']
        for opt in options:
            # Is it a valid option?
            if opt.dest in config_dict[section_name]:
                # Update option if necessary
                if args[opt.dest] != config_dict[section_name][opt.dest]:
                    old_value = config_dict[section_name][opt.dest]
                    new_value = args[opt.dest]
                    config_dict[section_name][opt.dest] = new_value
                    logger.info('Option {}/{} is updated: {}  -->  {}'.format(section_name, opt.dest, old_value, new_value))
            else:
                # Invalid option name, e.g. the program version is not added in `config_ini`
                logger.debug('Invalid option name: {}'.format(opt.dest))
    ipdb.set_trace()


def init(config_path):
    global config_dict
    # config_dict = read_config_from_ini(config_path)
    config_dict = read_config_from_yaml(config_path)

    if config_dict is None:
        # TODO: exit script
        logger.critical('{} could not be read'.format(config_path))
