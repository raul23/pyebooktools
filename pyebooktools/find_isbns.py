"""Tries to find valid ISBNs inside a file or in a string if no file was
specified.

Searching for ISBNs in files uses progressively more resource-intensive methods
until some ISBNs are found, see the `documentation`_ for more details.

This is a Python port of `find-isbns.sh`_ from `ebook-tools`_ written in Shell
by `na--`_.

References
----------
* `ebook-tools`_

.. external links
.. _documentation: https://github.com/na--/ebook-tools#searching-for-isbns-in-files
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _find-isbns.sh: https://github.com/na--/ebook-tools/blob/master/find-isbns.sh
.. _na--: https://github.com/na--
"""
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import find_isbns, search_file_for_isbns
from pyebooktools.utils.logutils import init_log

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
    func_params = locals().copy()
    # Check if input data is a file path or a string
    try:
        if Path(input_data).is_file():
            logger.debug(f'The input data is a file path')
            logger.info(f"Searching file '{Path(input_data).name}' for "
                        "ISBN numbers...")
            isbns = search_file_for_isbns(input_data, **func_params)
        else:
            logger.debug(f'The input data is a string')
            isbns = find_isbns(input_data, **func_params)
    except OSError as e:
        # TODO: important, find case for this error; if not remove it
        if e.args[0]:
            logger.debug(f'{e.args[1]}: the input data might be a string')
            isbns = find_isbns(input_data, **func_params)
        else:
            raise e
    if isbns:
        logger.info(f"Extracted ISBNs:\n{isbns}")
    else:
        logger.info("No ISBNs could be found!")
    return 0
