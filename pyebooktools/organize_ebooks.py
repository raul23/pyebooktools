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
import re
import tempfile
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import (BOLD, GREEN, NC, RED, check_file_for_corruption,
                              fetch_metadata, find_isbns, get_ebook_metadata,
                              get_file_size, get_mime_type, get_pages_in_pdf,
                              move_or_link_ebook_file_and_metadata,
                              move_or_link_file, remove_file,
                              search_file_for_isbns, search_meta_val,
                              unique_filename)
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
CORRUPTION_CHECK_ONLY = default_cfg.corruption_check_only
DRY_RUN = default_cfg.dry_run
ISBN_METADATA_FETCH_ORDER = default_cfg.isbn_metadata_fetch_order
ISBN_RET_SEPARATOR = default_cfg.isbn_ret_separator
ORGANIZE_WITHOUT_ISBN = default_cfg.organize_without_isbn
ORGANIZE_WITHOUT_ISBN_SOURCES = default_cfg.organize_without_isbn_sources
OUTPUT_FOLDER = default_cfg.output_folder
OUTPUT_FOLDER_CORRUPT = default_cfg.output_folder_corrupt
OUTPUT_FOLDER_PAMPHLETS = default_cfg.output_folder_pamphlets
OUTPUT_FOLDER_UNCERTAIN = default_cfg.output_folder_uncertain
OUTPUT_METADATA_EXTENSION = default_cfg.output_metadata_extension
PAMPHLET_EXCLUDED_FILES = default_cfg.pamphlet_excluded_files
PAMPHLET_INCLUDED_FILES = default_cfg.pamphlet_included_files
PAMPHLET_MAX_FILESIZE_KIB = default_cfg.pamphlet_max_filesize_kib
PAMPHLET_MAX_PDF_PAGES = default_cfg.pamphlet_max_pdf_pages
REVERSE = default_cfg.reverse
SYMLINK_ONLY=default_cfg.symlink_only
TESTED_ARCHIVE_EXTENSIONS = default_cfg.tested_archive_extensions
WITHOUT_ISBN_IGNORE = default_cfg.without_isbn_ignore


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


def is_pamphlet(file_path, pamphlet_excluded_files=PAMPHLET_EXCLUDED_FILES,
                pamphlet_included_files=PAMPHLET_INCLUDED_FILES,
                pamphlet_max_filesize_kib=PAMPHLET_MAX_FILESIZE_KIB,
                pamphlet_max_pdf_pages=PAMPHLET_MAX_PDF_PAGES):
    logger.info(f"Checking whether '{file_path}' looks like a pamphlet...")
    # TODO: check that it does the same as to_lower() @ https://bit.ly/2w0O5LN
    lowercase_name = os.path.basename(file_path).lower()
    # TODO: check that it does the same as
    # `if [[ "$lowercase_name" =~ $PAMPHLET_INCLUDED_FILES ]];`
    # ref.: https://bit.ly/2I5nvFW
    if re.search(pamphlet_included_files, lowercase_name):
        parts = []
        # TODO: check that it does the same as
        # `matches="[$(echo "$lowercase_name" | grep -oE "$PAMPHLET_INCLUDED_FILES" | paste -sd';')]"`
        # TODO: they are using grep -oE
        # ref.: https://bit.ly/2w2PeCo
        matches = re.finditer(pamphlet_included_files, lowercase_name)
        for i, match in enumerate(matches):
            parts.append(match.group())
        matches = ';'.join(parts)
        logger.info('Parts of the filename match the pamphlet include '
                    f'regex: [{matches}]')
        return True
    logger.info('The file does not match the pamphlet include regex, '
                'continuing...')
    # TODO: check that it does the same as
    # `if [[ "$lowercase_name" =~ $PAMPHLET_EXCLUDED_FILES ]]; then`
    # ref.: https://bit.ly/2KscBZj
    if re.search(pamphlet_excluded_files, lowercase_name):
        parts = []
        # TODO: check that it does the same as
        # `matches="[$(echo "$lowercase_name" | grep -oE "$PAMPHLET_EXCLUDED_FILES" | paste -sd';')]"`
        # TODO: they are using grep -oE
        # ref.: https://bit.ly/2JHhlZJ
        matches = re.finditer(pamphlet_excluded_files, lowercase_name)
        for i, match in enumerate(matches):
            parts.append(match.group())
        matches = ';'.join(parts)
        logger.info('Parts of the filename match the pamphlet exclude '
                    f'regex: [{matches}]')
        # TODO: [ERROR] they are returning 1, but it should be returning 0
        # because the file is considered as a pamphlet
        return True
    logger.info('The file does not match the pamphlet exclude regex, continuing...')
    mime_type = get_mime_type(file_path)
    file_size_KiB = get_file_size(file_path, unit='KiB')
    if file_size_KiB is None:
        logger.error(f'Could not get the file size (KiB) for {file_path}')
        return None
    if mime_type == 'application/pdf':
        logger.info('The file looks like a pdf, checking if the number of '
                    f'pages is larger than {pamphlet_max_pdf_pages} ...')
        result = get_pages_in_pdf(file_path)
        pages = result.stdout
        if pages is None:
            logger.error(f'Could not get the number of pages for {file_path}')
            return None
        elif pages > pamphlet_max_pdf_pages:
            logger.info(f'The file has {pages} pages, too many for a pamphlet')
            return False
        else:
            logger.info(f'The file has only {pages} pages, looks like a '
                        'pamphlet')
            return True
    elif file_size_KiB < pamphlet_max_filesize_kib:
        logger.info(f"The file has a type '{mime_type}' and a small size "
                    f'({file_size_KiB} KiB), looks like a pamphlet')
        return True
    else:
        logger.info(f"The file has a type '{mime_type}' and a large size "
                    '({file_size_KiB} KB), does NOT look like a pamphlet')
        return False


# Arguments: path, reason (optional)
def organize_by_filename_and_meta(
        old_path, prev_reason,
        organize_without_isbn_sources=ORGANIZE_WITHOUT_ISBN_SOURCES,
        output_folder_pamphlets=OUTPUT_FOLDER_PAMPHLETS,
        output_folder_uncertain=OUTPUT_FOLDER_UNCERTAIN,
        without_isbn_ignore=WITHOUT_ISBN_IGNORE):
    prev_reason = f'{prev_reason}; '
    logger.info(f"Organizing '{old_path}' by non-ISBN metadata and filename...")
    # TODO: check that it does the same as to_lower() @ https://bit.ly/2w0O5LN
    lowercase_name = os.path.basename(old_path).lower()
    # TODO: check that it does the same as
    # `if [[ "$WITHOUT_ISBN_IGNORE" != "" && "$lowercase_name" =~ $WITHOUT_ISBN_IGNORE ]]`
    # ref.: https://bit.ly/2HJTzfg
    if without_isbn_ignore and re.match(without_isbn_ignore, lowercase_name):
        parts = []
        # TODO: check that it does the same as
        # `matches="[$(echo "$lowercase_name" | grep -oE "$WITHOUT_ISBN_IGNORE" | paste -sd';')]`
        # TODO: they are using grep -oE
        # ref.: https://bit.ly/2jj2Vnz
        matches = re.finditer(without_isbn_ignore, lowercase_name)
        for i, match in enumerate(matches):
            parts.append(match.group())
        matches = ';'.join(parts)
        logger.info(f'Parts of the filename match the ignore regex: [{matches}]')
        skip_file(old_path,
                  f'{prev_reason}File matches the ignore regex ({matches})')
        return
    else:
        logger.info('File does not match the ignore regex, continuing...')
    is_p = is_pamphlet(old_path)
    if is_p is True:
        logger.info(f"File '{old_path}' looks like a pamphlet!")
        if output_folder_pamphlets:
            dirname = os.path.dirname(old_path)
            basename = os.path.basename(old_path)
            new_path = unique_filename(os.path.join(output_folder_pamphlets, dirname), basename)
            logger.info(f"Moving file '{old_path}' to '{new_path}'!")
            ok_file(old_path, new_path)
            move_or_link_file(old_path, new_path)
        else:
            logger.info('Output folder for pamphlet files is not set, skipping...')
            skip_file(old_path, 'No pamphlet folder specified')
        return
    elif is_p is False:
        logger.debug(f"File '{old_path}' doesn't look like a pamphlet")
    else:
        logger.debug(f"Couldn't determine if file '{old_path}' is a pamphlet")
    if not output_folder_uncertain:
        logger.info('No uncertain folder specified, skipping...')
        skip_file(old_path, 'No uncertain folder specified')
        return
    result = get_ebook_metadata(old_path)
    if result.stderr:
        logger.error(f'`ebook-meta` returns an error: {result.error}')
    ebookmeta = result.stdout
    logger.info('Ebook metadata:')
    logger.info(ebookmeta)
    tmpmfile = tempfile.mkstemp(suffix='.txt')[1]
    logger.info(f'Created temporary file for metadata downloads {tmpmfile}')

    def finisher(fetch_method):
        logger.info('Successfully fetched metadata: ')
        logger.info('Adding additional metadata to the end of the metadata '
                    'file...')
        more_metadata = 'Old file path       : {}\n' \
                        'Meta fetch method   : {}\n'.format(old_path,
                                                            fetch_method)
        lines = ''
        for line in ebookmeta.splitlines():
            # TODO: remove next line if simpler version does the same thing
            # lines.append(re.sub('^(.+[^ ]) ([ ]+):', 'OF \1 \2', line))
            lines.append(re.sub('^(.+)( +):', 'OF \1 \2', line))
        ebookmeta = '\n'.join(lines)
        with open(tmpmfile, 'a') as f:
            f.write(more_metadata)
            f.write(ebookmeta)
        isbn = find_isbns(more_metadata)
        if isbn:
            with open(tmpmfile, 'a') as f:
                f.write(f'ISBN                : {isbn}')
        else:
            logger.debug(f'No isbn found for file {old_path}')
        logger.info(f'Organizing {old_path} (with {tmpmfile})...')
        new_path = move_or_link_ebook_file_and_metadata(output_folder_uncertain,
                                                        old_path, tmpmfile)
        ok_file(old_path, new_path)

    # TODO: get title and author from `ebook-meta`
    title = search_meta_val(ebookmeta, 'Title')
    author = search_meta_val(ebookmeta, 'Author')
    # Equivalent to (in bash):
    # if [[ "${title//[^[:alpha:]]/}" != "" && "$title" != "unknown" ]]
    # ref.: https://bit.ly/2HDHZGm
    if re.sub(r'[^A-Za-z]', '', title) != '' and title != 'unknown':
        logger.info('There is a relatively normal-looking title, searching for '
                    'metadata...')
        # TODO: complete condition for author
        cond = ''
        if cond and author != 'unknown':
            logger.info(f'Trying to fetch metadata by title {title} and '
                        f'author {author}...')
            options = f'--verbose --title="{title}" --author="{author}"'
            # TODO: check that fetch_metadata() can also return an empty string
            metadata = fetch_metadata(organize_without_isbn_sources, options)
            if metadata:
                # TODO: they are writing outside the if, https://bit.ly/2FyIiwh
                with open(tmpmfile, 'a') as f:
                    # TODO: do we write even if metadata can be empty?
                    f.write(metadata)
                finisher('title&author')
                return
            logger.info(f'Trying to swap places - author {title} and title '
                        f'{author}...')
            options = f'--verbose --title="{author}" --author="{title}"'
            metadata = fetch_metadata(organize_without_isbn_sources, options)
            if metadata:
                # TODO: they are writing outside the if, https://bit.ly/2Kt78kX
                with open(tmpmfile, 'a') as f:
                    # TODO: do we write even if metadata can be empty?
                    f.write(metadata)
                finisher('rev-title&author')
                return

            logger.info(f'Trying to fetch metadata only by title {title}...')
            options = f'--verbose --title="{title}"'
            metadata = fetch_metadata(organize_without_isbn_sources, options)
            if metadata:
                # TODO: they are writing outside the if, https://bit.ly/2vZeFES
                with open(tmpmfile, 'a') as f:
                    # TODO: do we write even if metadata can be empty?
                    f.write(metadata)
                finisher('title')
                return
    # TODO: tokenize basename
    # filename="$(basename "${old_path%.*}" | tokenize)"
    # ref.: https://bit.ly/2jlyBIR
    filename = os.path.splitext(os.path.basename(old_path))[0]
    logger.info(f'Trying to fetch metadata only the filename {filename}...')
    options = f'--verbose --title="{filename}"'
    metadata = fetch_metadata(organize_without_isbn_sources, options)
    if metadata:
        # TODO: they are writing outside the if, https://bit.ly/2I3GH6X
        with open(tmpmfile, 'a') as f:
            # TODO: do we write even if metadata can be empty?
            f.write(filename)
        finisher('title')
        return
    logger.info(f'Could not find anything, removing the temp file {tmpmfile}...')
    remove_file(tmpmfile)
    skip_file(old_path, f'{prev_reason}Insufficient or wrong file name/metadata')


# Sequentially tries to fetch metadata for each of the supplied ISBNs; if any
# is found, writes it to a tmp.txt file and calls organize_known_ebook()
# Arguments: path, isbns (comma-separated)
# TODO: in their description, they refer to `organize_known_ebook` but it should
# be `move_or_link_ebook_file_and_metadata`, Ref.: https://bit.ly/2HNv3x0
def organize_by_isbns(file_path, isbns, output_folder=OUTPUT_FOLDER,
                      isbn_metadata_fetch_order=ISBN_METADATA_FETCH_ORDER,
                      isbn_ret_separator=ISBN_RET_SEPARATOR,
                      organize_without_isbn=ORGANIZE_WITHOUT_ISBN):
    import ipdb
    ipdb.set_trace()
    isbn_sources = isbn_metadata_fetch_order
    for isbn in isbns.split(isbn_ret_separator):
        tmp_file = tempfile.mkstemp(suffix='.txt')[1]
        logger.info(f'Trying to fetch metadata for ISBN {isbn} into temp file '
                    f'{tmp_file}...')
        for isbn_source in isbn_sources:
            # Check if there are spaces in the arguments, and if it is the case
            # enclose the arguments in quotation marks
            if ' ' in isbn_source:
                isbn_source = f'"{isbn_source}"'
            # Remove whitespaces around the isbn source
            isbn_source = isbn_source.strip()
            logger.info(f"Fetching metadata from '{isbn_source}' sources...")
            options = f'--verbose --isbn={isbn}'
            result = fetch_metadata(isbn_source, options)
            metadata = result.stdout
            if metadata:
                with open(tmp_file, 'w') as f:
                    f.write(metadata)
                # TODO: is it necessary to sleep after fetching the metadata from
                # online sources like they do? The code is run sequentially, so
                # we are executing the rest of the code here once fetch_metadata()
                # is done, ref.: https://bit.ly/2vV9MfU
                logger.info('Successfully fetched metadata: ')
                logger.info(metadata)

                logger.info('Adding additional metadata to the end of the metadata '
                            'file...')
                more_metadata = 'ISBN                : {}\n' \
                                'All found ISBNs     : {}\n' \
                                'Old file path       : {}\n' \
                                'Metadata source     : {}'.format(isbn, isbns,
                                                                  file_path,
                                                                  isbn_source)
                logger.info(more_metadata)
                with open(tmp_file, 'a') as f:
                    f.write(more_metadata)

                logger.info(f"Organizing '{file_path}' (with {tmp_file})...")
                new_path = move_or_link_ebook_file_and_metadata(
                    new_folder=output_folder, current_ebook_path=file_path,
                    current_metadata_path=tmp_file)

                ok_file(file_path, new_path)
                # NOTE: `tmp_file` was already removed in move_or_link_ebook_file_and_metadata()
                return

        logger.info(f'Removing temp file {tmp_file}...')
        remove_file(tmp_file)

    if organize_without_isbn:
        logger.info('Could not organize via the found ISBNs, organizing by '
                    'filename and metadata instead...')
        organize_by_filename_and_meta(
            file_path, f'Could not fetch metadata for ISBNs {isbns}')
    else:
        logger.info('Organization by filename and metadata is not turned on, '
                    'giving up...')
        skip_file(file_path, f'Could not fetch metadata for ISBNs {isbns}; '
                             f'Non-ISBN organization disabled')


def organize_file(file_path, output_folder=OUTPUT_FOLDER,
                  output_folder_corrupt=OUTPUT_FOLDER_CORRUPT,
                  corruption_check_only=CORRUPTION_CHECK_ONLY, dry_run=DRY_RUN,
                  isbn_metadata_fetch_order=ISBN_METADATA_FETCH_ORDER,
                  isbn_ret_separator=ISBN_RET_SEPARATOR,
                  organize_without_isbn=ORGANIZE_WITHOUT_ISBN,
                  output_metadata_extension=OUTPUT_METADATA_EXTENSION,
                  symlink_only=SYMLINK_ONLY,
                  tested_archive_extensions=TESTED_ARCHIVE_EXTENSIONS):
    import ipdb
    file_err = check_file_for_corruption(file_path, tested_archive_extensions)
    if file_err:
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
        ipdb.set_trace()
        logger.info('File passed the corruption test, looking for ISBNs...')
        isbns = search_file_for_isbns(file_path)
        if isbns:
            logger.info(f"Organizing '{file_path}' by ISBNs\n{isbns}")
            organize_by_isbns(file_path, isbns, output_folder,
                              isbn_metadata_fetch_order, isbn_ret_separator,
                              organize_without_isbn)
        elif organize_without_isbn:
            logger.info(f"No ISBNs found for '{file_path}', organizing by "
                        'filename and metadata...')
            organize_by_filename_and_meta(file_path, 'No ISBNs found')
        else:
            skip_file(file_path,
                      'No ISBNs found; Non-ISBN organization disabled')
    logger.info('=====================================================')


def organize(folder_to_organize, output_folder=OUTPUT_FOLDER,
             output_folder_corrupt=OUTPUT_FOLDER_CORRUPT,
             corruption_check_only=CORRUPTION_CHECK_ONLY, dry_run=DRY_RUN,
             isbn_metadata_fetch_order=ISBN_METADATA_FETCH_ORDER,
             isbn_ret_separator=ISBN_RET_SEPARATOR,
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
                      corruption_check_only, dry_run, isbn_metadata_fetch_order,
                      isbn_ret_separator, organize_without_isbn,
                      output_metadata_extension, symlink_only,
                      tested_archive_extensions)
