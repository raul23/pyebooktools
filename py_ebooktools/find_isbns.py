"""Try to find valid ISBNs inside a file or in a string if no file was specified.

Searching for ISBNs in files uses progressively more resource-intensive methods
until some ISBNs are found. See the `documentation`_.

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

from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.lib import find_isbns, search_file_for_isbns
from py_ebooktools.utils.genutils import init_log

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
ISBN_BLACKLIST_REGEX = default_cfg.isbn_blacklist_regex
ISBN_DIRECT_GREP_FILES = default_cfg.isbn_direct_grep_files
ISBN_GREP_REORDER_FILES = default_cfg.isbn_grep_reorder_files
ISBN_GREP_RF_REVERSE_LAST = default_cfg.isbn_grep_rf_reverse_last
ISBN_GREP_RF_SCAN_FIRST = default_cfg.isbn_grep_rf_scan_first
ISBN_IGNORED_FILES = default_cfg.isbn_ignored_files
ISBN_REGEX = default_cfg.isbn_regex
ISBN_RET_SEPARATOR = default_cfg.isbn_ret_separator
OCR_COMMAND = default_cfg.ocr_command
OCR_ENABLED = default_cfg.ocr_enabled
OCR_ONLY_FIRST_LAST_PAGES = default_cfg.ocr_only_first_last_pages


def find(input_data, isbn_blacklist_regex=ISBN_BLACKLIST_REGEX,
         isbn_direct_grep_files=ISBN_DIRECT_GREP_FILES,
         isbn_grep_reorder_files=ISBN_GREP_REORDER_FILES,
         isbn_grep_rf_reverse_last=ISBN_GREP_RF_REVERSE_LAST,
         isbn_grep_rf_scan_first=ISBN_GREP_RF_SCAN_FIRST,
         isbn_ignored_files=ISBN_IGNORED_FILES,
         isbn_regex=ISBN_REGEX, isbn_ret_separator=ISBN_RET_SEPARATOR,
         ocr_command=OCR_COMMAND, ocr_enabled=OCR_ENABLED,
         ocr_only_first_last_pages=OCR_ONLY_FIRST_LAST_PAGES, **kwargs):
    # ipdb.set_trace()
    # Check if input data is a file path or a string
    if Path(input_data).is_file():
        logger.debug(f'The input data is a file path: {input_data}')
        search_file_for_isbns(input_data, isbn_direct_grep_files,
                              isbn_grep_reorder_files, isbn_grep_rf_reverse_last,
                              isbn_grep_rf_scan_first, isbn_ignored_files,
                              isbn_regex, isbn_ret_separator, ocr_command,
                              ocr_enabled, ocr_only_first_last_pages)
    else:
        logger.debug(f'The input data is a string: {input_data}')
        isbns = find_isbns(input_data, isbn_blacklist_regex, isbn_regex,
                           isbn_ret_separator)
        print(isbns)
