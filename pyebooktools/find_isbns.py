"""Tries to find valid ISBNs inside a file or in a string if no file was
specified.

Searching for ISBNs in files uses progressively more resource-intensive methods
until some ISBNs are found, see the `documentation`_ for more details.

This is a Python port of `find-isbns.sh`_ from `ebook-tools`_ written in Shell
by `na--`_.

References
----------
* `ebook-tools`_

.. URLs

.. external links
.. _documentation: https://github.com/na--/ebook-tools#searching-for-isbns-in-files
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _find-isbns.sh: https://github.com/na--/ebook-tools/blob/master/find-isbns.sh
.. _na--: https://github.com/na--
"""
from pathlib import Path
# TODO: remove
# import ipdb

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import find_isbns, search_file_for_isbns
from pyebooktools.utils.genutils import init_log

logger = init_log(__name__, __file__)


def find(input_data, isbn_blacklist_regex=default_cfg.isbn_blacklist_regex,
         isbn_direct_grep_files=default_cfg.isbn_direct_grep_files,
         isbn_grep_reorder_files=default_cfg.isbn_grep_reorder_files,
         isbn_grep_rf_reverse_last=default_cfg.isbn_grep_rf_reverse_last,
         isbn_grep_rf_scan_first=default_cfg.isbn_grep_rf_scan_first,
         isbn_ignored_files=default_cfg.isbn_ignored_files,
         isbn_regex=default_cfg.isbn_regex,
         isbn_ret_separator=default_cfg.isbn_ret_separator,
         ocr_command=default_cfg.ocr_command,
         ocr_enabled=default_cfg.ocr_enabled,
         ocr_only_first_last_pages=default_cfg.ocr_only_first_last_pages,
         **kwargs):
    # ipdb.set_trace()
    # Check if input data is a file path or a string
    if Path(input_data).is_file():
        logger.debug(f'The input data is a file path: {input_data}')
        isbns = search_file_for_isbns(input_data, isbn_blacklist_regex,
                                      isbn_direct_grep_files,
                                      isbn_grep_reorder_files,
                                      isbn_grep_rf_reverse_last,
                                      isbn_grep_rf_scan_first,
                                      isbn_ignored_files, isbn_regex,
                                      isbn_ret_separator, ocr_command,
                                      ocr_enabled, ocr_only_first_last_pages)
    else:
        logger.debug(f'The input data is a string: {input_data}')
        isbns = find_isbns(input_data, isbn_blacklist_regex, isbn_regex,
                           isbn_ret_separator)
    if isbns:
        logger.info(f"Extracted ISBNs:\n{isbns}")
    else:
        logger.info("No ISBNs could be found!")
