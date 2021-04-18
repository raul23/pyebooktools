import logging
import os
import sys
from logging import NullHandler


# TODO: explain cases
def get_logger_name(module__name__, module___file__, package_name=None):
    if os.path.isabs(module___file__):
        # e.g. initcwd or editcfg
        module_name = os.path.splitext(os.path.basename(module___file__))[0]
        package_path = os.path.dirname(module___file__)
        package_name = os.path.basename(package_path)
        logger_name = "{}.{}".format(
            package_name,
            module_name)
    elif module__name__ == '__main__' or not module__name__.count('.'):
        # e.g. train_models.py or explore_data.py
        if package_name is None:
            package_name = os.path.basename(os.getcwd())
        logger_name = "{}.{}".format(
            package_name,
            os.path.splitext(module___file__)[0])
    elif module__name__.count('.') > 1:
        logger_name = '.'.join(module__name__.split('.')[-2:])
    else:
        # e.g. importing mlutils from train_models.py
        logger_name = module__name__
    return logger_name


def init_log(module__name__, module___file__=None, package_name=None):
    if module___file__:
        logger_ = logging.getLogger(get_logger_name(module__name__,
                                                    module___file__,
                                                    package_name))
    elif module__name__.count('.') > 1:
        logger_name = '.'.join(module__name__.split('.')[-2:])
        logger_ = logging.getLogger(logger_name)
    else:
        logger_ = logging.getLogger(module__name__)
    logger_.addHandler(NullHandler())
    return logger_


# TODO: specify log_dict change inline
def set_logging_field_width(log_dict, size_longest_name=None):
    if not size_longest_name:
        names = log_dict['loggers'].keys()
        if sys.argv and os.path.basename(sys.argv[0]) == 'ebooktools':
            # TODO: why default_?
            names = [n for n in names if not n.startswith('default_')]
        size_longest_name = len(max(names, key=len))
    for k, v in log_dict['formatters'].items():
        try:
            # TODO: add auto_field_width at the top
            v['format'] = v['format'].format(auto_field_width=size_longest_name)
        except KeyError:
            continue


def set_logging_formatter(log_dict, handler_names=None, formatter='simple'):
    # TODO: assert handler_names and formatter
    """
    for handler_name in handler_names:
        log_dict['handlers'][handler_name]['formatter'] = formatter
    """
    handler_names = handler_names if handler_names else []
    for handler_name, handler_val in log_dict['handlers'].items():
        if not handler_names or handler_name in handler_names:
            handler_val['formatter'] = formatter


def set_logging_level(log_dict, handler_names=None, logger_names=None,
                      level='DEBUG'):
    # TODO: assert handler_names, logger_names and level
    handler_names = handler_names if handler_names else []
    logger_names = logger_names if logger_names else []
    keys = ['handlers', 'loggers']
    for k in keys:
        for name, val in log_dict[k].items():
            if (not handler_names and not logger_names) or \
                    (k == 'handlers' and name in handler_names) or \
                    (k == 'loggers' and name in logger_names):
                val['level'] = level
