"""Traverses a calibre library folder and renames all the book files in it by
reading their metadata from calibre's metadata.opf files.

Then the book files are either moved or symlinked (if the flag
``--symlink-only`` is enabled) to the output folder along with their
corresponding metadata files.

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

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import (find_isbns, get_metadata, move_or_link_file,
                              substitute_params, substitute_with_sed,
                              unique_filename)
from pyebooktools.utils.genutils import copy, init_log, remove_accents

logger = init_log(__name__, __file__)


def rename(calibre_folder, output_folder=default_cfg.output_folder,
           dry_run=default_cfg.dry_run,
           isbn_blacklist_regex=default_cfg.isbn_blacklist_regex,
           isbn_regex=default_cfg.isbn_regex,
           output_filename_template=default_cfg.output_filename_template,
           output_metadata_extension=default_cfg.output_metadata_extension,
           reverse=default_cfg.reverse, save_metadata=default_cfg.save_metadata,
           symlink_only=default_cfg.symlink_only, **kwargs):
    number_ebooks = 0
    file_paths = []
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
        elif book_path.name in ['metadata.db', 'metadata_db_prefs_backup.json']:
            logger.debug("Rejected! Calibre's metadata db files")
            continue
        elif book_path.parent.parent.name == 'calibre':
            logger.debug("Rejected! File is part of calibre/")
            continue
        else:
            logger.debug('We found a book file!')
        logger.debug('Checking if the book file has a metadata file')
        metadata_path = book_path.parent.joinpath('metadata.opf')
        if not metadata_path.exists():
            logger.warning(f"Skipping file '{book_path.name}' - no "
                           f"metadata.opf present!")
            logger.debug(f'Full path: {book_path}')
            continue
        logger.debug(f"Found file '{book_path.name}' with metadata.opf "
                     "present")
        logger.debug(f'Full path: {book_path}')
        number_ebooks += 1
        file_paths.append((book_path, metadata_path))
    # TODO: important sort within glob?
    logger.debug(f"Found {number_ebooks} ebooks with metadata.opf")
    logger.info("Files sorted {}".format("in desc" if reverse else "in asc"))
    file_paths.sort(key=lambda paths: paths[0].name, reverse=reverse)
    metadata = {'EXT': '', 'TITLE': '', 'AUTHORS': '', 'SERIES': '',
                'PUBLISHED': '', 'ISBN': ''}
    for book_path, metadata_path in file_paths:
        logger.info(f"Parsing metadata for '{book_path.name}'...")
        logger.debug(f'Full path: {book_path}')
        metadata['EXT'] = book_path.suffix.split('.')[-1]
        metadata['TITLE'] = get_metadata(metadata_path.as_posix(),
                                         '//*[local-name()="title"]/text()')
        authors = get_metadata(metadata_path.as_posix(),
                               '//*[local-name()="creator"]/text()')
        # e.g. b'John Doe\\nJane Doe' -> 'John Doe\nJane Doe'
        # e.g. 'John Doe\nJane Doe' -> 'John Doe, Jane Doe'
        metadata['AUTHORS'] = ', '.join(authors.decode().split('\\n')).encode('utf-8')
        metadata['SERIES'] = get_metadata(
            metadata_path.as_posix(),
            '//*[local-name()="meta"][@name="calibre:series"]/@content')
        if metadata['SERIES']:
            series_index = get_metadata(
                metadata_path.as_posix(),
                '//*[local-name()="meta"][@name="calibre:series_index"]/@content')
            metadata['SERIES'] = f"{metadata['SERIES'].decode()} " \
                                 f"#{series_index.decode()}".encode('utf-8')
        metadata['PUBLISHED'] = get_metadata(metadata_path.as_posix(),
                                             '//*[local-name()="date"]/text()')
        metadata['ISBN'] = get_metadata(
            metadata_path.as_posix(),
            '//*[local-name()="identifier"][@*[local-name()="scheme" and .="ISBN"]]/text()')
        if not metadata['ISBN']:
            with open(metadata_path.as_posix(), mode='rb') as f:
                content_metadata_file = f.read().decode()
            # comma-separated isbn(s)
            isbn = find_isbns(content_metadata_file, isbn_blacklist_regex,
                              isbn_regex, ', ')
            if not isbn:
                logger.debug(f"No ISBN found for {book_path}")
            # else:
                # TODO: important better isbn validator since one wrong ISBN is found
                # in the metadata file in the the uuid field (but only one case)
        logger.debug('Parsed metadata:')
        for k, v in metadata.items():
            v = substitute_with_sed('[\\/\*\?<>\|\x01-\x1F\x7F\x22\x24\x60]', '_', v)
            logger.debug(f'{k}: {v}')
        new_name = substitute_params(metadata, output_filename_template)
        # Remove accents
        new_name = remove_accents(new_name)
        new_path = unique_filename(output_folder, new_name)
        logger.info('Saving book file and metadata...')
        logger.debug(f"Moving file to '{new_path}'")
        move_or_link_file(book_path, new_path, dry_run, symlink_only)
        new_metadata_path = f'{new_path.split(Path(new_path).suffix)[0]}.' \
                            f'{output_metadata_extension}'
        if save_metadata == 'recreate':
            new_metadata = f"""Title               : {metadata['TITLE'].decode()}
Author(s)           : {metadata['AUTHORS'].decode()}
Series              : {metadata['SERIES'].decode()}
Published           : {metadata['PUBLISHED'].decode()}
ISBN                : {metadata['ISBN'].decode()}
Old file path       : {book_path}
Metadata source     : metadata.opf"""
            with open(new_metadata_path, mode='w') as f:
                f.write(new_metadata)
        elif save_metadata == 'opfcopy':
            copy(metadata_path, new_metadata_path, clobber=False)
        else:
            logger.debug('Metadata was not copied or recreated')
