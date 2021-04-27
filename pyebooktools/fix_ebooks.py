"""Tries to fix corrupted ebook files.

For the moment, only PDF files are supported.
"""
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)


def fix(input_data, **kwargs):
    logger.warning('Not implemented yet!')
