"""Splits the supplied ebook files (and the accompanying metadata files if
present) into folders with consecutive names that each contain the specified
number of files.

This is a Python port of split-into-folders.sh from ebook-tools by na--. See
https://github.com/na--/ebook-tools/blob/master/split-into-folders.sh

Ref.: https://github.com/na--/ebook-tools
"""
import math
import os
import ipdb
from pathlib import Path

from pyebooktools.lib import FILE_SORT_FLAGS, OUTPUT_METADATA_EXTENSION
from pyebooktools.utils.genutils import init_log, mkdir, move

logger = init_log(__name__, __file__)

# ==============
# Default values
# ==============
FOLDER_PATTERN = '%05d000'
START_NUMBER = 0
OUTPUT_FOLDER = Path.cwd()
FILES_PER_FOLDER = 1000


def split(folder_with_books, folder_pattern=FOLDER_PATTERN,
          start_number=START_NUMBER, output_folder=OUTPUT_FOLDER,
          files_per_folder=FILES_PER_FOLDER,
          output_metadata_extension=OUTPUT_METADATA_EXTENSION,
          file_sort_flags=FILE_SORT_FLAGS, **kwargs):
    # TODO: ignore hidden files
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
            files.append(fp)
        # TODO: debug logging skip directory/file
    # Sort
    # files.sort(reverse=True)
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
        # current_folder = Path.joinpath(output_folder, current_folder_basename)
        current_folder = os.path.join(output_folder, current_folder_basename)
        # TODO: not working with Path.joinpath if output_folder is not absolute
        """
        current_folder_metadata = Path.joinpath(
            output_folder, current_folder_basename+'.'+output_metadata_extension)
        """
        current_folder_metadata = os.path.join(
            output_folder, current_folder_basename + '.' + output_metadata_extension)
        current_folder_num += 1
        logger.debug(f"Creating folders '{current_folder}' and "
                     f"'{current_folder_metadata}'...")
        mkdir(current_folder)
        mkdir(current_folder_metadata)

        logger.debug(f"Moving files...")
        for file_to_move in chunk:
            file_dest = os.path.join(current_folder, file_to_move.name)
            move(file_to_move, file_dest)
