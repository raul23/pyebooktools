import linecache
import sys


def test():
    pass


def print_exception(error=None):
    """
    For a given exception, print filename, line number, the line itself, and
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
