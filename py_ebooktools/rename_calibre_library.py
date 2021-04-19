"""Traverses a calibre library folder and renames all the book files in it by
reading their metadata from calibre's metadata.opf files.

This is a Python port of `rename-calibre-library.sh`_ from `ebook-tools`_
written in Shell by `na--`_.

References
----------
* `ebook-tools`_

.. TODO: add description to reference (and other places too)
.. URLs

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
.. _rename-calibre-library.sh: https://github.com/na--/ebook-tools/blob/master/rename-calibre-library.sh
"""
from pathlib import Path

from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.utils.genutils import init_log

logger = init_log(__name__, __file__)


def rename(calibre_folder, output_folder=default_cfg.output_folder,
           dry_run=default_cfg.dry_run, reverse=default_cfg.file_sort_reverse,
           save_metadata=default_cfg.save_metadata,
           symlink_only=default_cfg.symlink_only, **kwargs):
    # TODO: remove
    import ipdb
    number_ebooks = 0
    for book_path in Path(calibre_folder).rglob('*'):
        logger.debug(f'Processing {book_path}')
        if book_path.is_dir():
            logger.debug('Rejected! It is a folder')
            continue
        elif not book_path.suffix:
            logger.debug('Rejected! It is a hidden file')
            continue
        elif book_path.suffix == '.opf':
            logger.debug('Rejected! It is a metadata file')
            continue
        elif book_path.name == 'cover.jpg':
            logger.debug('Rejected! It is the cover image of the ebook')
            continue
        else:
            logger.debug('We found a book file!')
        logger.debug('Checking if the book file has a metadata file associated with')
        metadata_path = book_path.parent.joinpath('metadata.opf')
        if not metadata_path.exists():
            logger.warning(f"Skipping file '{book_path.name}' - no metadata.opf present!")
            logger.debug(f'Full path: {book_path}')
        number_ebooks += 1
        logger.info(f"Found file '{book_path.name}' with metadata.opf present, parsing metadata...")
        logger.debug(f'Full path: {book_path}')
        # ipdb.set_trace()
    logger.info(f"Number of ebook files found: {number_ebooks}")
