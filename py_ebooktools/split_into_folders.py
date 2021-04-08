"""Split the supplied ebook files (and the accompanying metadata files if
present) into folders with consecutive names that each contain the specified
number of files.

This is a Python port of `split-into-folders.sh`_ from `ebook-tools`_ written
in Shell by `na--`_.

References
----------
* `ebook-tools`_

.. URLs

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
.. _split-into-folders.sh: https://github.com/na--/ebook-tools/blob/master/split-into-folders.sh
"""
import math
import os
# import ipdb
from pathlib import Path

from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.utils.genutils import init_log, mkdir, move

logger = init_log(__name__, __file__)


def split(folder_with_books=Path.cwd(),
          folder_pattern=default_cfg.folder_pattern,
          start_number=default_cfg.start_number,
          output_folder=default_cfg.output_folder,
          files_per_folder=default_cfg.files_per_folder,
          output_metadata_extension=default_cfg.output_metadata_extension,
          dry_run=default_cfg.dry_run,
          reverse=default_cfg.file_sort_reverse, **kwargs):
    files = []
    for fp in Path(folder_with_books).rglob('*'):
        # File extension
        # ipdb.set_trace()
        ext = fp.suffix.split('.')[-1]
        # Ignore directory, metadata and hidden files
        if Path.is_file(fp) and ext != output_metadata_extension and \
                not fp.name.startswith('.'):
            # TODO: debug logging
            # print(fp)
            files.append((fp))
        # TODO: debug logging skip directory/file
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
        logger.debug(f"Found {len(chunk)} number of files...")
        current_folder_basename = '{0:0{width}}'.format(
            current_folder_num, width=width)
        current_folder = os.path.join(output_folder, current_folder_basename)
        current_folder_metadata = os.path.join(
            output_folder, current_folder_basename + '.' + output_metadata_extension)
        current_folder_num += 1
        logger.debug(f"Creating folders '{current_folder}' and "
                     f"'{current_folder_metadata}'...")
        if not dry_run:
            mkdir(current_folder)
            mkdir(current_folder_metadata)
        logger.debug(f"Moving files...")
        if not dry_run:
            for file_to_move in chunk:
                file_dest = os.path.join(current_folder, file_to_move.name)
                move(file_to_move, file_dest)
                # Move metadata file if found
                metadata_name = f'{file_to_move.stem}.{output_metadata_extension}'
                metada_file_to_move = file_to_move.parent.joinpath(metadata_name)
                if metada_file_to_move.exists():
                    logger.debug(f"Found metadata file: {metada_file_to_move}")
                    metadata_dest = os.path.join(current_folder_metadata,
                                                 metadata_name)
                    move(metada_file_to_move, metadata_dest)
    return 0
