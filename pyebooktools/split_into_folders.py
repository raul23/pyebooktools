"""Splits the supplied ebook files (and the accompanying metadata files if
present) into folders with consecutive names that each contain the specified
number of files.

This is a Python port of `split-into-folders.sh`_ from `ebook-tools`_ written
in Shell by `na--`_.

References
----------
* `ebook-tools`_

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
.. _split-into-folders.sh: https://github.com/na--/ebook-tools/blob/master/split-into-folders.sh
"""
import math
import os
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.utils.genutils import mkdir, move
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)


def split(folder_with_books,
          output_folder=default_cfg.split['output_folder'],
          dry_run=default_cfg.dry_run,
          files_per_folder=default_cfg.split['files_per_folder'],
          folder_pattern=default_cfg.split['folder_pattern'],
          output_metadata_extension=default_cfg.output_metadata_extension,
          reverse=default_cfg.reverse,
          start_number=default_cfg.split['start_number'],
          **kwargs):
    files = []
    for fp in Path(folder_with_books).rglob('*'):
        # File extension
        ext = fp.suffix.split('.')[-1]
        # Ignore directory, metadata and hidden files
        if Path.is_file(fp) and ext != output_metadata_extension and \
                not fp.name.startswith('.'):
            # TODO: debug logging
            # print(fp)
            files.append(fp)
        # TODO: debug logging skip directory/file
    # TODO: important sort within glob?
    logger.info("Files sorted {}".format("in desc" if reverse else "in asc"))
    files.sort(key=lambda x: x.name, reverse=reverse)
    current_folder_num = start_number
    start_index = 0
    # Get width of zeros for folder format pattern
    left, right = folder_pattern.split('%')[-1].split('d')
    width = int(left) + len(right)
    total_files = len(files)
    logger.info(f"Total number of files to be split into folders: {total_files}")
    logger.info(f"Number of files per folder: {files_per_folder}")
    number_splits = math.ceil(total_files / files_per_folder)
    logger.info(f"Number of splits: {number_splits}")
    logger.info("Starting splits...")
    while True:
        if start_index >= len(files):
            # TODO: debug logging
            logger.info(f"End of splits!")
            break
        chunk = files[start_index:start_index+files_per_folder]
        start_index += files_per_folder
        logger.debug(f"Found {len(chunk)} files...")
        current_folder_basename = '{0:0{width}}'.format(
            current_folder_num, width=width)
        current_folder = os.path.join(output_folder, current_folder_basename)
        current_folder_metadata = os.path.join(
            output_folder, current_folder_basename + '.' + output_metadata_extension)
        current_folder_num += 1
        if dry_run:
            logger.debug(f"Creating folder '{current_folder}'...")
        else:
            mkdir(current_folder)
        for file_to_move in chunk:
            # TODO: important, explain that files skipped if already exist (not overwritten)
            file_dest = os.path.join(current_folder, file_to_move.name)
            if dry_run:
                logger.debug(f"Moving file '{file_to_move}'...")
            else:
                move(file_to_move, file_dest, clobber=False)
            # Move metadata file if found
            # TODO: important, extension of metadata (other places too)
            # metadata_name = f'{file_to_move.stem}.{output_metadata_extension}'
            metadata_name = f'{file_to_move.name}.{output_metadata_extension}'
            metada_file_to_move = file_to_move.parent.joinpath(metadata_name)
            if metada_file_to_move.exists():
                logger.debug(f"Found metadata file: {metada_file_to_move}")
                # Create metadata folder only if there is at least a
                # metadata file
                if dry_run:
                    logger.debug(f"Creating folder '{current_folder_metadata}'...")
                    logger.debug(f"Moving file '{metadata_name}'...")
                else:
                    mkdir(current_folder_metadata)
                    metadata_dest = os.path.join(current_folder_metadata,
                                                 metadata_name)
                    move(metada_file_to_move, metadata_dest, clobber=False)
    return 0
