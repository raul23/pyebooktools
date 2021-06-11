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
import time
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import (check_file_for_corruption, fail_file,
                              fetch_metadata, find_isbns, get_ebook_metadata,
                              get_file_size, get_mime_type, get_pages_in_pdf,
                              # get_parts_from_path as g,
                              is_dir_empty,
                              move_or_link_ebook_file_and_metadata,
                              move_or_link_file, remove_file, ok_file,
                              search_file_for_isbns, search_meta_val,
                              skip_file, unique_filename)
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)


# TODO: important, do the same for others
class OrganizeEbooks:
    def __init__(self):
        self.folder_to_organize = None
        self.output_folder = default_cfg.organize['output_folder']
        self.output_folder_corrupt = default_cfg.organize['output_folder_corrupt']
        self.output_folder_pamphlets = default_cfg.organize['output_folder_pamphlets']
        self.output_folder_uncertain = default_cfg.organize['output_folder_uncertain']
        self.corruption_check_only = default_cfg.organize['corruption_check_only']
        self.dry_run = default_cfg.dry_run
        self.isbn_blacklist_regex = default_cfg.isbn_blacklist_regex
        self.isbn_direct_grep_files = default_cfg.isbn_direct_grep_files
        self.isbn_grep_reorder_files = default_cfg.isbn_grep_reorder_files
        self.isbn_grep_rf_reverse_last = default_cfg.isbn_grep_rf_reverse_last
        self.isbn_grep_rf_scan_first = default_cfg.isbn_grep_rf_scan_first
        self.isbn_ignored_files = default_cfg.isbn_ignored_files
        self.isbn_metadata_fetch_order = default_cfg.isbn_metadata_fetch_order
        self.isbn_regex = default_cfg.isbn_regex
        self.isbn_ret_separator = default_cfg.isbn_ret_separator
        self.keep_metadata = default_cfg.keep_metadata
        self.ocr_command = default_cfg.ocr_command
        self.ocr_enabled = default_cfg.ocr_enabled
        self.ocr_only_first_last_pages = default_cfg.ocr_only_first_last_pages
        self.organize_without_isbn = default_cfg.organize['organize_without_isbn']
        self.organize_without_isbn_sources = default_cfg.organize_without_isbn_sources
        self.output_filename_template = default_cfg.output_filename_template
        self.output_metadata_extension = default_cfg.output_metadata_extension
        self.pamphlet_excluded_files = default_cfg.organize['pamphlet_excluded_files']
        self.pamphlet_included_files = default_cfg.organize['pamphlet_included_files']
        self.pamphlet_max_filesize_kib = default_cfg.organize['pamphlet_max_filesize_kib']
        self.pamphlet_max_pdf_pages = default_cfg.organize['pamphlet_max_pdf_pages']
        self.reverse = default_cfg.reverse
        self.symlink_only = default_cfg.symlink_only
        self.tested_archive_extensions = default_cfg.organize['tested_archive_extensions']
        self.without_isbn_ignore = default_cfg.organize['without_isbn_ignore']

    def _is_pamphlet(self, file_path):
        logger.debug(f"Checking whether '{file_path}' looks like a pamphlet...")
        # TODO: check that it does the same as to_lower() @ https://bit.ly/2w0O5LN
        lowercase_name = os.path.basename(file_path).lower()
        # TODO: check that it does the same as
        # `if [[ "$lowercase_name" =~ $PAMPHLET_INCLUDED_FILES ]];`
        # ref.: https://bit.ly/2I5nvFW
        if re.search(self.pamphlet_included_files, lowercase_name):
            parts = []
            # TODO: check that it does the same as
            # `matches="[$(echo "$lowercase_name" |
            # grep -oE "$PAMPHLET_INCLUDED_FILES" | paste -sd';')]"`
            # TODO: they are using grep -oE
            # ref.: https://bit.ly/2w2PeCo
            matches = re.finditer(self.pamphlet_included_files, lowercase_name)
            for i, match in enumerate(matches):
                parts.append(match.group())
            matches = ';'.join(parts)
            logger.debug('Parts of the filename match the pamphlet include '
                         f'regex: [{matches}]')
            return True
        logger.debug('The file does not match the pamphlet include regex, '
                     'continuing...')
        # TODO: check that it does the same as
        # `if [[ "$lowercase_name" =~ $PAMPHLET_EXCLUDED_FILES ]]; then`
        # ref.: https://bit.ly/2KscBZj
        if re.search(self.pamphlet_excluded_files, lowercase_name):
            parts = []
            # TODO: check that it does the same as
            # `matches="[$(echo "$lowercase_name" | grep -oE "$PAMPHLET_EXCLUDED_FILES" | paste -sd';')]"`
            # TODO: they are using grep -oE
            # ref.: https://bit.ly/2JHhlZJ
            matches = re.finditer(self.pamphlet_excluded_files, lowercase_name)
            for i, match in enumerate(matches):
                parts.append(match.group())
            matches = ';'.join(parts)
            logger.debug('Parts of the filename match the pamphlet ignore '
                         f'regex: [{matches}]')
            return False
        logger.debug('The file does not match the pamphlet exclude regex, '
                     'continuing...')
        mime_type = get_mime_type(file_path)
        file_size_KiB = get_file_size(file_path, unit='KiB')
        if file_size_KiB is None:
            logger.error(f'Could not get the file size (KiB) for {file_path}')
            return None
        if mime_type == 'application/pdf':
            logger.debug('The file looks like a pdf, checking if the number of '
                         f'pages is larger than {self.pamphlet_max_pdf_pages} ...')
            result = get_pages_in_pdf(file_path)
            pages = result.stdout
            if pages is None:
                logger.error(f'Could not get the number of pages for {file_path}')
                return None
            elif pages > self.pamphlet_max_pdf_pages:
                logger.debug(f'The file has {pages} pages, too many for a '
                             'pamphlet')
                return False
            else:
                logger.debug(f'The file has only {pages} pages, looks like a '
                             'pamphlet')
                return True
        elif file_size_KiB < self.pamphlet_max_filesize_kib:
            logger.debug(f"The file has a type '{mime_type}' and a small size "
                         f'({file_size_KiB} KiB), looks like a pamphlet')
            return True
        else:
            logger.debug(f"The file has a type '{mime_type}' and a large size "
                         '({file_size_KiB} KB), does NOT look like a pamphlet')
            return False

    def _organize_by_filename_and_meta(self, old_path, prev_reason):
        # TODO: important, return nothing?
        prev_reason = f'{prev_reason}; '
        logger.debug(f"Organizing '{old_path}' by non-ISBN metadata and "
                     "filename...")
        # TODO: check that it does the same as to_lower() @ https://bit.ly/2w0O5LN
        lowercase_name = os.path.basename(old_path).lower()
        # TODO: check that it does the same as
        # `if [[ "$WITHOUT_ISBN_IGNORE" != "" &&
        # "$lowercase_name" =~ $WITHOUT_ISBN_IGNORE ]]`
        # Ref.: https://bit.ly/2HJTzfg
        if self.without_isbn_ignore and re.match(self.without_isbn_ignore,
                                                 lowercase_name):
            parts = []
            # TODO: check that it does the same as
            # `matches="[$(echo "$lowercase_name" |
            # grep -oE "$WITHOUT_ISBN_IGNORE" | paste -sd';')]`
            # TODO: they are using grep -oE
            # ref.: https://bit.ly/2jj2Vnz
            matches = re.finditer(self.without_isbn_ignore, lowercase_name)
            for i, match in enumerate(matches):
                parts.append(match.group())
            matches = ';'.join(parts)
            logger.debug('Parts of the filename match the ignore regex: '
                         f'[{matches}]')
            skip_file(old_path,
                      f'{prev_reason}File matches the ignore regex ({matches})')
            return
        else:
            logger.debug('File does not match the ignore regex, continuing...')
        is_p = self._is_pamphlet(file_path=old_path)
        if is_p is True:
            logger.debug(f"File '{old_path}' looks like a pamphlet!")
            if self.output_folder_pamphlets:
                new_path = unique_filename(self.output_folder_pamphlets,
                                           os.path.basename(old_path))
                logger.debug(f"Moving file '{old_path}' to '{new_path}'!")
                ok_file(old_path, new_path)
                move_or_link_file(old_path, new_path)
            else:
                logger.debug('Output folder for pamphlet files is not set, '
                             'skipping...')
                skip_file(old_path, 'No pamphlet folder specified')
            return
        elif is_p is False:
            logger.debug(f"File '{old_path}' doesn't look like a pamphlet")
        else:
            logger.debug(f"Couldn't determine if file '{old_path}' is a pamphlet")
        if not self.output_folder_uncertain:
            # logger.debug('No uncertain folder specified, skipping...')
            skip_file(old_path, 'No uncertain folder specified')
            return
        result = get_ebook_metadata(old_path)
        if result.stderr:
            logger.error(f'`ebook-meta` returns an error: {result.error}')
        ebookmeta = result.stdout
        logger.debug('Ebook metadata:')
        logger.debug(ebookmeta)
        tmpmfile = tempfile.mkstemp(suffix='.txt')[1]
        logger.debug(f'Created temporary file for metadata downloads {tmpmfile}')

        # NOTE: tmp file is removed in move_or_link_ebook_file_and_metadata()
        def finisher(fetch_method, ebookmeta, metadata):
            logger.debug('Successfully fetched metadata: ')
            logger.debug('Adding additional metadata to the end of the metadata '
                         'file...')
            more_metadata = '\nOld file path       : {}\n' \
                            'Meta fetch method   : {}\n'.format(old_path,
                                                                fetch_method)
            lines = []
            for line in ebookmeta.splitlines():
                # TODO: remove next line if simpler version does the same thing
                # lines.append(re.sub('^(.+[^ ]) ([ ]+):', 'OF \1 \2', line))
                lines.append(re.sub('^(.+)( +):', 'OF \1 \2', line))
            ebookmeta = '\n'.join(lines)
            with open(tmpmfile, 'a') as f:
                f.write(more_metadata)
                f.write(ebookmeta)
            isbns = find_isbns(metadata + ebookmeta, **self.__dict__)
            if isbns:
                # TODO: important, there can be more than one isbn
                isbn = isbns.split(self.isbn_ret_separator)[0]
                with open(tmpmfile, 'a') as f:
                    f.write(f'\nISBN                : {isbn}')
            else:
                logger.debug(f'No isbn found for file {old_path}')
            logger.debug(f"Organizing '{old_path}' (with '{tmpmfile}')...")
            new_path = move_or_link_ebook_file_and_metadata(
                new_folder=self.output_folder_uncertain,
                current_ebook_path=old_path,
                current_metadata_path=tmpmfile, **self.__dict__)
            ok_file(old_path, new_path)

        title = search_meta_val(ebookmeta, 'Title')
        author = search_meta_val(ebookmeta, 'Author(s)')
        # Equivalent to (in bash):
        # if [[ "${title//[^[:alpha:]]/}" != "" && "$title" != "unknown" ]]
        # Ref.: https://bit.ly/2HDHZGm
        if re.sub(r'[^A-Za-z]', '', title) != '' and title != 'unknown':
            logger.debug('There is a relatively normal-looking title, '
                         'searching for metadata...')
            if re.sub(r'\s', '', author) != '' and author != 'unknown':
                logger.debug(f'Trying to fetch metadata by title "{title}" '
                             f'and author "{author}"...')
                options = f'--verbose --title="{title}" --author="{author}"'
                # TODO: check that fetch_metadata() can also return an empty string
                metadata = fetch_metadata(self.organize_without_isbn_sources,
                                          options)
                if metadata.returncode == 0:
                    # TODO: they are writing outside the if, https://bit.ly/2FyIiwh
                    with open(tmpmfile, 'a') as f:
                        # TODO: do we write even if metadata can be empty?
                        # TODO: important, stdout (only one 1 result) or stderr (all results)
                        f.write(metadata.stdout)
                    finisher('title&author', ebookmeta, metadata.stdout)
                    return
                logger.debug(f"Trying to swap places - author '{title}' and "
                             f"title '{author}'...")
                options = f'--verbose --title="{author}" --author="{title}"'
                metadata = fetch_metadata(self.organize_without_isbn_sources,
                                          options)
                if metadata.returncode == 0:
                    # TODO: they are writing outside the if, https://bit.ly/2Kt78kX
                    with open(tmpmfile, 'a') as f:
                        # TODO: do we write even if metadata can be empty?
                        f.write(metadata.stdout)
                    finisher('rev-title&author', ebookmeta, metadata.stdout)
                    return
                logger.debug(f'Trying to fetch metadata only by title {title}...')
                options = f'--verbose --title="{title}"'
                metadata = fetch_metadata(self.organize_without_isbn_sources,
                                          options)
                if metadata.returncode == 0:
                    # TODO: they are writing outside the if, https://bit.ly/2vZeFES
                    with open(tmpmfile, 'a') as f:
                        # TODO: do we write even if metadata can be empty?
                        f.write(metadata.stdout)
                    finisher('title', ebookmeta, metadata.stdout)
                    return
        # TODO: tokenize basename
        # filename="$(basename "${old_path%.*}" | tokenize)"
        # Ref.: https://bit.ly/2jlyBIR
        filename = os.path.splitext(os.path.basename(old_path))[0]
        logger.debug(f'Trying to fetch metadata only by filename {filename}...')
        options = f'--verbose --title="{filename}"'
        metadata = fetch_metadata(self.organize_without_isbn_sources, options)
        if metadata.returncode == 0:
            # TODO: they are writing outside the if, https://bit.ly/2I3GH6X
            with open(tmpmfile, 'a') as f:
                # TODO: do we write even if metadata can be empty?
                f.write(filename)
            finisher('title', ebookmeta, filename)
            return
        logger.debug('Could not find anything, removing the temp file '
                     f'{tmpmfile}...')
        remove_file(tmpmfile)
        skip_file(old_path, f'{prev_reason}Insufficient or wrong file '
                            'name/metadata')

    def _organize_by_isbns(self, file_path, isbns):
        # TODO: important, returns nothing?
        isbn_sources = self.isbn_metadata_fetch_order
        if not isbn_sources:
            # NOTE: If you use Calibre versions that are older than 2.84, it's
            # required to manually set the following option to an empty string.
            isbn_sources = []
        for isbn in isbns.split(self.isbn_ret_separator):
            tmp_file = tempfile.mkstemp(suffix='.txt')[1]
            logger.debug(f"Trying to fetch metadata for ISBN '{isbn}' into "
                         f"temp file '{tmp_file}'...")

            # IMPORTANT: as soon as we find metadata from one source, we return
            for isbn_source in isbn_sources:
                # Remove whitespaces around the isbn source
                isbn_source = isbn_source.strip()
                # Check if there are spaces in the arguments, and if it is the
                # case enclose the arguments in quotation marks
                # e.g. WorldCat xISBN --> "WorldCat xISBN"
                if ' ' in isbn_source:
                    isbn_source = f'"{isbn_source}"'
                logger.debug(f"Fetching metadata from '{isbn_source}' sources...")
                options = f'--verbose --isbn={isbn}'
                result = fetch_metadata(isbn_source, options)
                metadata = result.stdout
                if metadata:
                    with open(tmp_file, 'w') as f:
                        f.write(metadata)

                    # TODO: is it necessary to sleep after fetching the
                    # metadata from online sources like they do? The code is
                    # run sequentially, so we are executing the rest of the
                    # code here once fetch_metadata() is done
                    # Ref.: https://bit.ly/2vV9MfU
                    time.sleep(0.1)
                    logger.debug('Successfully fetched metadata')
                    logger.debug(f'Fetched metadata:{metadata}')

                    logger.debug('Adding additional metadata to the end of the '
                                 'metadata file...')
                    more_metadata = 'ISBN                : {}\n' \
                                    'All found ISBNs     : {}\n' \
                                    'Old file path       : {}\n' \
                                    'Metadata source     : {}'.format(
                        isbn, isbns.replace('\n', ','), file_path, isbn_source)
                    logger.debug(more_metadata)
                    with open(tmp_file, 'a') as f:
                        f.write(more_metadata)

                    logger.debug(f"Organizing '{file_path}' (with {tmp_file})...")
                    new_path = move_or_link_ebook_file_and_metadata(
                        new_folder=self.output_folder,
                        current_ebook_path=file_path,
                        current_metadata_path=tmp_file, **self.__dict__)

                    ok_file(file_path, new_path)
                    # NOTE: `tmp_file` was already removed in
                    # move_or_link_ebook_file_and_metadata()
                    return

            logger.debug(f'Removing temp file {tmp_file}...')
            remove_file(tmp_file)

        if self.organize_without_isbn:
            logger.debug('Could not organize via the found ISBNs, organizing '
                         'by filename and metadata instead...')
            self._organize_by_filename_and_meta(
                old_path=file_path,
                prev_reason=f'Could not fetch metadata for ISBNs {isbns}')
        else:
            logger.debug('Organization by filename and metadata is not turned '
                         'on, giving up...')
            skip_file(file_path, f'Could not fetch metadata for ISBNs {isbns}; '
                                 f'Non-ISBN organization disabled')

    def _organize_file(self, file_path):
        logger.info(f'Processing {Path(file_path).name} ...')
        file_err = check_file_for_corruption(file_path,
                                             self.tested_archive_extensions)
        if file_err:
            logger.debug(f"File '{file_path}' is corrupt with error: {file_err}")
            if self.output_folder_corrupt:
                new_path = unique_filename(self.output_folder_corrupt,
                                           file_path.name)
                move_or_link_file(file_path, new_path, self.dry_run,
                                  self.symlink_only)
                # TODO: do we add the meta extension directly to new_path (which
                # already has an extension); thus if new_path='/test/path/book.pdf'
                # then new_metadata_path='/test/path/book.pdf.meta' or should it be
                # new_metadata_path='/test/path/book.meta'
                # Ref.: https://bit.ly/2I6K3pW
                """
                new_metadata_path = f'{os.path.splitext(new_path)[0]}.' \
                                    f'{self.output_metadata_extension}'
                """
                # NOTE: no unique name for matadata path (and other places)
                new_metadata_path = f'{new_path}.{self.output_metadata_extension}'
                logger.debug(f'Saving original filename to {new_metadata_path}...')
                if not self.dry_run:
                    metadata = f'Corruption reason   : {file_err}\n' \
                               f'Old file path       : {file_path}'
                    with open(new_metadata_path, 'w') as f:
                        f.write(metadata)
                fail_file(file_path, f'File is corrupt: {file_err}', new_path)
            else:
                logger.debug('Output folder for corrupt files is not set, doing '
                             'nothing')
                fail_file(file_path, f'File is corrupt: {file_err}')
        elif self.corruption_check_only:
            logger.debug('We are only checking for corruption, do not continue '
                         'organising...')
            skip_file(file_path, 'File appears OK')
        else:
            # TODO: important, if html has ISBN it will be considered as an ebook
            # self._is_pamphlet() needs to be called before search...()
            logger.debug('File passed the corruption test, looking for ISBNs...')
            logger.debug(f"Searching file '{Path(file_path).name}' for ISBN "
                         "numbers...")
            isbns = search_file_for_isbns(file_path, **self.__dict__)
            if isbns:
                logger.debug(f"Organizing '{file_path}' by ISBNs\n{isbns}")
                self._organize_by_isbns(file_path, isbns)
            elif self.organize_without_isbn:
                logger.debug(f"No ISBNs found for '{file_path}', organizing by "
                             'filename and metadata...')
                self._organize_by_filename_and_meta(
                    old_path=file_path, prev_reason='No ISBNs found')
            else:
                skip_file(file_path,
                          'No ISBNs found; Non-ISBN organization disabled')
        logger.debug('=====================================================')

    # TODO: important, do the same for others
    def _update(self, **kwargs):
        logger.debug('Updating attributes for organize...')
        for k, v in self.__dict__.items():
            new_val = kwargs.get(k)
            if new_val and v != new_val:
                logger.debug(f'{k}: {v} -> {new_val}')
                self.__setattr__(k, new_val)

    def organize(self, folder_to_organize, **kwargs):
        # TODO: important, factorize (other places, e.g. rename)
        # TODO: important, add red color to error message (other places too)
        if folder_to_organize is None:
            logger.error("\nerror: the following arguments are required: folder_to_organize")
            return 1
        self._update(**kwargs)
        self.folder_to_organize = folder_to_organize
        files = []
        # TODO: important, other places too
        if is_dir_empty(folder_to_organize):
            logger.warning(f'Folder is empty: {folder_to_organize}')
        if self.corruption_check_only:
            logger.info('We are only checking for corruption\n')
        else:
            logger.info('')
        logger.debug(f"Recursively scanning '{folder_to_organize}' for files...")
        for fp in Path(folder_to_organize).rglob('*'):
            # Ignore directory and hidden files
            if Path.is_file(fp) and not fp.name.startswith('.'):
                logger.debug(f"{fp.name}")
                files.append(fp)
        if not files:
            logger.warning(f'No ebooks found in folder: {folder_to_organize}')
        # TODO: important sort within glob?
        logger.debug("Files sorted {}".format("in desc" if self.reverse else "in asc"))
        files.sort(key=lambda x: x.name, reverse=self.reverse)
        logger.debug('=====================================================')
        for fp in files:
            self._organize_file(fp)
        return 0


organizer = OrganizeEbooks()
