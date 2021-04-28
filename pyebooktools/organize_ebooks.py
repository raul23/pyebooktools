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
import os
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import (BOLD, GREEN, NC, RED, check_file_for_corruption,
                              move_or_link_file, search_file_for_isbns,
                              unique_filename)
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
CORRUPTION_CHECK_ONLY = default_cfg.corruption_check_only
DRY_RUN = default_cfg.dry_run
ORGANIZE_WITHOUT_ISBN = default_cfg.organize_without_isbn
OUTPUT_FOLDER = default_cfg.output_folder
OUTPUT_FOLDER_CORRUPT = default_cfg.output_folder_corrupt
OUTPUT_METADATA_EXTENSION = default_cfg.output_metadata_extension
REVERSE = default_cfg.reverse
SYMLINK_ONLY=default_cfg.symlink_only
TESTED_ARCHIVE_EXTENSIONS = default_cfg.tested_archive_extensions


def fail_file(old_path, reason, new_path=None):
    # More info about printing in terminal with color:
    # https://stackoverflow.com/a/21786287
    logger.info(f'{RED}ERR{NC}\t: {old_path}')
    second_line = f'REASON\t: {reason}'
    if new_path:
        logger.info(second_line)
        logger.info(f'TO\t: {new_path}\n')
    else:
        logger.info(second_line + '\n')


def ok_file(file_path, reason):
    logger.info(f'{GREEN}OK{NC}\t: {file_path}\nTO\t: {reason}\n')


def skip_file(old_path, new_path):
    # TODO: https://bit.ly/2rf38f5
    logger.info(f'{BOLD}SKIP{NC}\t: {old_path}')
    logger.info(f'REASON\t: {new_path}\n')


def organize_by_filename_and_meta(old_path, prev_reason):
    pass


def organize_by_isbns(file_path, isbns):
    pass


def organize_file(file_path, output_folder=OUTPUT_FOLDER,
                  output_folder_corrupt=OUTPUT_FOLDER_CORRUPT,
                  corruption_check_only=CORRUPTION_CHECK_ONLY, dry_run=DRY_RUN,
                  organize_without_isbn=ORGANIZE_WITHOUT_ISBN,
                  output_metadata_extension=OUTPUT_METADATA_EXTENSION,
                  symlink_only=SYMLINK_ONLY,
                  tested_archive_extensions=TESTED_ARCHIVE_EXTENSIONS):
    import ipdb
    file_err = check_file_for_corruption(file_path, tested_archive_extensions)
    if file_err:
        # ipdb.set_trace()
        logger.debug(f"File '{file_path}' is corrupt with error: {file_err}")
        if output_folder_corrupt:
            new_path = unique_filename(output_folder_corrupt,
                                       file_path.name)
            move_or_link_file(file_path, new_path, dry_run, symlink_only)
            # TODO: do we add the meta extension directly to new_path (which
            # already has an extension); thus if new_path='/test/path/book.pdf'
            # then new_metadata_path='/test/path/book.pdf.meta' or should it be
            # new_metadata_path='/test/path/book.meta' (which is what I'm doing
            # here)
            # ref.: https://bit.ly/2I6K3pW
            new_metadata_path = f'{os.path.splitext(new_path)[0]}.' \
                                f'{output_metadata_extension}'
            logger.debug(f'Saving original filename to {new_metadata_path}...')
            if not dry_run:
                metadata = f'Corruption reason   : {file_err}\n' \
                           f'Old file path       : {file_path}'
                with open(new_metadata_path, 'w') as f:
                    f.write(metadata)
            fail_file(file_path, f'File is corrupt: {file_err}', new_path)
        else:
            logger.info('Output folder for corrupt files is not set, doing '
                        'nothing')
            fail_file(file_path, f'File is corrupt: {file_err}')
    elif corruption_check_only:
        logger.info('We are only checking for corruption, do not continue '
                    'organising...')
        skip_file(file_path, 'File appears OK')
    else:
        logger.info('File passed the corruption test, looking for ISBNs...')
        isbns = search_file_for_isbns(file_path)
        if isbns:
            logger.info(f'Organizing {file_path} by ISBNs {isbns}!')
            organize_by_isbns(file_path, isbns)
        elif organize_without_isbn:
            logger.info(f'No ISBNs found for {file_path}, organizing by '
                        'filename and metadata...')
            organize_by_filename_and_meta(file_path, 'No ISBNs found')
        else:
            skip_file(file_path,
                      'No ISBNs found; Non-ISBN organization disabled')
    logger.info('=====================================================')


def organize(folder_to_organize, output_folder=OUTPUT_FOLDER,
             output_folder_corrupt=OUTPUT_FOLDER_CORRUPT,
             corruption_check_only=CORRUPTION_CHECK_ONLY, dry_run=DRY_RUN,
             organize_without_isbn=ORGANIZE_WITHOUT_ISBN,
             output_metadata_extension=OUTPUT_METADATA_EXTENSION,
             symlink_only=SYMLINK_ONLY,
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
    logger.info('=====================================================')
    for fp in files:
        organize_file(fp, output_folder, output_folder_corrupt,
                      corruption_check_only, dry_run, organize_without_isbn,
                      output_metadata_extension, symlink_only,
                      tested_archive_extensions)
