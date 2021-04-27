"""Automatically organizes folders with potentially huge amounts of unorganized
ebooks.

This is done by renaming the files with proper names and moving them to other
folders.

This is a Python port of `organize-ebooks.sh`_ from `ebook-tools`_ written in
Shell by `na--`_.

References
----------
* `ebook-tools`_

.. TODO: add description to reference (and other places too)

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
.. _organize-ebooks.sh: https://github.com/na--/ebook-tools/blob/master/organize-ebooks.sh
"""
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import check_file_for_corruption
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
OUTPUT_FOLDER = default_cfg.output_folder
REVERSE = default_cfg.reverse
TESTED_ARCHIVE_EXTENSIONS = default_cfg.tested_archive_extensions


def organize_file(file_path,
                  tested_archive_extensions=TESTED_ARCHIVE_EXTENSIONS):
    import ipdb
    ipdb.set_trace()
    check_file_for_corruption(file_path, tested_archive_extensions)


def organize(folder_to_organize, output_folder=OUTPUT_FOLDER,
             tested_archive_extensions=TESTED_ARCHIVE_EXTENSIONS,
             reverse=REVERSE, **kwargs):
    files = []
    logger.info(f"Recursively scanning '{folder_to_organize}' for files...")
    for fp in Path(folder_to_organize).rglob('*'):
        # Ignore directory and hidden files
        if Path.is_file(fp) and not fp.name.startswith('.'):
            logger.debug(f"{fp.name}")
            files.append((fp))
    # TODO: important sort within glob?
    logger.info("Files sorted {}".format("in desc" if reverse else "in asc"))
    files.sort(key=lambda x: x.name, reverse=reverse)
    for fp in files:
        organize_file(fp, tested_archive_extensions)
