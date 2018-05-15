import ipdb
import argparse
import logging
import os
import re
import tempfile
import textwrap
import sys

import config

from config import check_comma_options, expand_folder_paths, init_config, update_config_from_arg_groups
from lib import check_file_for_corruption, fetch_metadata, find_isbns, get_ebook_metadata, get_file_size, \
    get_mime_type, get_pages_in_pdf, get_without_isbn_ignore, handle_script_arg, move_or_link_ebook_file_and_metadata, \
    move_or_link_file, remove_file, search_file_for_isbns, unique_filename, BOLD, GREEN, NC, RED, VERSION
from utils.gen import get_full_exception, setup_logging


# Get the logger
if __name__ == '__main__':
    # When run as a script
    logger = logging.getLogger('{}.{}'.format(os.path.basename(os.getcwd()), os.path.splitext(__file__)[0]))
else:
    # When imported as a module
    # TODO: test this part when imported as a module
    logger = logging.getLogger('{}.{}'.format(os.path.basename(os.path.dirname(__file__)), __name__))


def fail_file(old_path, reason, new_path=None):
    # More info about printing in terminal with color: https://stackoverflow.com/a/21786287
    first_two_lines = '\n{}ERR{}\t: {}\n' \
                      'REASON\t: {}\n'.format(RED, NC, old_path, reason)
    if new_path is None:
        print(first_two_lines)
    else:
        third_line = 'TO\t: {}\n'.format( new_path)
        print(first_two_lines + third_line)


def ok_file(file_path, reason):
    print('\n{}OK{}\t: {}\n'
          'TO\t: {}\n'.format(GREEN, NC, file_path, reason))


def skip_file(old_path, new_path):
    # TODO: https://bit.ly/2rf38f5
    print('\nSKIP\t: {}\n'
          'REASON\t: {}\n'.format(old_path, new_path))


def is_pamphlet(file_path):
    logger.info('Checking whether {} looks like a pamphlet...'.format(file_path))
    # TODO: check that it does the same as to_lower() @ https://bit.ly/2w0O5LN
    lowercase_name = os.path.basename(file_path).lower()

    pamphlet_included_files = config.config_dict['organize-ebooks']['pamphlet_included_files']
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
        logger.info('Parts of the filename match the pamphlet include regex: [{}]'.format(matches))
        return True

    logger.info('The file does not match the pamphlet include regex, continuing...')

    pamphlet_excluded_files = config.config_dict['organize-ebooks']['pamphlet_excluded_files']
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
        logger.info('Parts of the filename match the pamphlet exclude regex: [{}]'.format(matches))
        # TODO: [ERROR] they are returning 1, but it should be returning 0
        # because the file is considered as a pamphlet
        return True

    logger.info('The file does not match the pamphlet exclude regex, continuing...')

    mime_type = get_mime_type(file_path)
    file_size_KiB = get_file_size(file_path, unit='KiB')
    if file_size_KiB is None:
        logger.error('Could not get the file size (KiB) for {}'.format(file_path))
        return None
    pamphlet_max_pdf_pages = config.config_dict['organize-ebooks']['pamphlet_max_pdf_pages']
    pamphlet_max_filesize_kib = config.config_dict['organize-ebooks']['pamphlet_max_filesize_kib']
    if mime_type == 'application/pdf':
        logger.info('The file looks like a pdf, checking if the number of pages '
                    'is larger than {} ...'.format(pamphlet_max_pdf_pages))
        result = get_pages_in_pdf(file_path)
        pages = result.stdout

        if pages is None:
            logger.error('Could not get the number of pages for {}'.format(file_path))
            return None
        elif pages > pamphlet_max_pdf_pages:
            logger.info('The file has {} pages, too many for a pamphlet'.format(pages))
            return False
        else:
            logger.info('The file has only {} pages, looks like a pamphlet'.format(pages))
            return True
    elif file_size_KiB < pamphlet_max_filesize_kib:
        logger.info('The file has a type {} and a small size ({} KiB), looks like a '
                    'pamphlet'.format(mime_type, file_size_KiB))
        return True
    else:
        logger.info('The file has a type {} and a large size ({} KB), does NOT look '
                    'like a pamphlet'.format(mime_type, file_size_KiB))
        return False


# Arguments: path, reason (optional)
def organize_by_filename_and_meta(old_path, prev_reason):
    prev_reason = '{}; '.format(prev_reason)
    logger.info('Organizing {} by non-ISBN metadata and filename...'.format(old_path))
    # TODO: check that it does the same as to_lower() @ https://bit.ly/2w0O5LN
    lowercase_name = os.path.basename(old_path).lower()
    without_isbn_ignore = config.config_dict['organize-ebooks']['without_isbn_ignore']
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
        logger.info('Parts of the filename match the ignore regex: [{}]'.format(matches))
        skip_file(old_path, '{}File matches the ignore regex ({})'.format(prev_reason, matches))
        return
    else:
        logger.info('File does not match the ignore regex, continuing...')

    is_p = is_pamphlet(old_path)
    if is_p is True:
        logger.info('File {} looks like a pamphlet!'.format(old_path))
        output_folder_pamphlets = config.config_dict['organize-ebooks']['output_folder_pamphlets']
        if output_folder_pamphlets:
            dirname = os.path.dirname(old_path)
            basename = os.path.basename(old_path)
            new_path = unique_filename(os.path.join(output_folder_pamphlets, dirname), basename)

            logger.info('Moving file {} to {}!'.format(old_path, new_path))
            ok_file(old_path, new_path)

            move_or_link_file(old_path, new_path)
        else:
            logger.info('Output folder for pamphlet files is not set, skipping...')
            skip_file(old_path, 'No pamphlet folder specified')
        return
    elif is_p is False:
        logger.debug("File {} doesn't look like a pamphlet".format(old_path))
    else:
        logger.debug("Couldn't determine if file {} is a pamphlet".format(old_path))

    ipdb.set_trace()
    output_folder_uncertain = config.config_dict['organize-ebooks']['output_folder_uncertain']
    if not output_folder_uncertain:
        logger.info('No uncertain folder specified, skipping...')
        skip_file(old_path, 'No uncertain folder specified')
        return

    result = get_ebook_metadata(old_path)
    if result.stderr:
        logger.error('`ebook-meta` returns an error: '.format(result.error))
    ebookmeta = result.stdout
    logger.info('Ebook metadata:')
    logger.info(ebookmeta)

    tmpmfile = tempfile.mkstemp(suffix='.txt')[1]
    logger.info('Created temporary file for metadata downloads {}'.format(tmpmfile))

    def finisher(fetch_method):
        logger.info('Successfully fetched metadata: ')
        logger.info('Adding additional metadata to the end of the metadata file...')
        more_metadata = 'Old file path       : {}\n' \
                        'Meta fetch method   : {}\n'.format(old_path, fetch_method)
        lines = ''
        for line in ebookmeta.splitlines():
            lines.append(re.sub('^(.+[^ ]) ([ ]+):', 'OF \1 \2', line))
        ebookmeta = '\n'.join(lines)
        with open(tmpmfile, 'a') as f:
            f.write(more_metadata)
            f.write(ebookmeta)

        isbn = find_isbns(more_metadata)
        if isbn:
            with open(tmpmfile, 'a') as f:
                f.write('ISBN                : {}'.format(isbn))
        else:
            logger.debug('No isbn found for file {}'.format(old_path))

        logger.info('Organizing {} (with {})...'.format(old_path, tmpmfile))
        new_path = move_or_link_ebook_file_and_metadata(output_folder_uncertain, old_path, tmpmfile)
        ok_file(old_path, new_path)

    # TODO: get title and author from `ebook-meta`
    title = ''
    author = ''
    # TODO: complete condition for title
    # if [[ "${title//[^[:alpha:]]/}" != "" && "$title" != "unknown" ]]
    # ref.: https://bit.ly/2HDHZGm
    cond = ''
    if cond and title != 'unknown':
        logger.info('There is a relatively normal-looking title, searching for metadata...')

        # TODO: complete condition for author
        cond = ''
        if cond and author != 'unknown':
            logger.info('Trying to fetch metadata by title {} and author {}...'.format(title, author))
            options = '--verbose --title="{}" --author="{}"'.format(title, author)
            # TODO: check that fetch_metadata() can also return an empty string
            metadata = fetch_metadata(config.config_dict['general-options']['organize_without_isbn_sources'], options)
            if metadata:
                # TODO: they are writing outside the if, https://bit.ly/2FyIiwh
                with open(tmpmfile, 'a') as f:
                    # TODO: do we write even if metadata can be empty?
                    f.write(metadata)
                finisher('title&author')
                return
            logger.info('Trying to swap places - author {} and title {}...'.format(title, author))
            options = '--verbose --title="{}" --author="{}"'.format(author, title)
            metadata = fetch_metadata(config.config_dict['general-options']['organize_without_isbn_sources'], options)
            if metadata:
                # TODO: they are writing outside the if, https://bit.ly/2Kt78kX
                with open(tmpmfile, 'a') as f:
                    # TODO: do we write even if metadata can be empty?
                    f.write(metadata)
                finisher('rev-title&author')
                return

            logger.info('Trying to fetch metadata only by title {}...'.format(title))
            options = '--verbose --title="{}"'.format(title)
            metadata = fetch_metadata(config.config_dict['general-options']['organize_without_isbn_sources'], options)
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
    logger.info('Trying to fetch metadata only the filename {}...'.format(filename))
    options = '--verbose --title="{}"'.format(filename)
    metadata = fetch_metadata(config.config_dict['general-options']['organize_without_isbn_sources'], options)
    if metadata:
        # TODO: they are writing outside the if, https://bit.ly/2I3GH6X
        with open(tmpmfile, 'a') as f:
            # TODO: do we write even if metadata can be empty?
            f.write(filename)
        finisher('title')
        return

    logger.info('Could not find anything, removing the temp file {}...'.format(tmpmfile))
    remove_file(tmpmfile)

    skip_file(old_path, '{}Insufficient or wrong file name/metadata'.format(prev_reason))


# Sequentially tries to fetch metadata for each of the supplied ISBNs; if any
# is found, writes it to a tmp.txt file and calls organize_known_ebook()
# Arguments: path, isbns (comma-separated)
# TODO: in their description, they refer to `organize_known_ebook` but it should
# be `move_or_link_ebook_file_and_metadata`, ref.: https://bit.ly/2HNv3x0
def organize_by_isbns(file_path, isbns):
    isbn_sources = config.config_dict['general-options']['isbn_metadata_fetch_order']
    isbn_sources = isbn_sources.split(',')
    for isbn in isbns.split(','):
        tmp_file = tempfile.mkstemp(suffix='.txt')[1]
        logger.info('Trying to fetch metadata for ISBN {} into temp file {}...'.format(isbn, tmp_file))

        for isbn_source in isbn_sources:
            # Check if there are spaces in the arguments, and if it is the case
            # enclose the arguments in quotation marks
            if ' ' in isbn_source:
                isbn_source = '"{}"'.format(isbn_source)
            # Remove whitespaces around the isbn source
            isbn_source = isbn_source.strip()
            logger.info('Fetching metadata from {} sources...'.format(isbn_source))
            options = '--verbose --isbn={}'.format(isbn)
            result = fetch_metadata(isbn_source, options)
            metadata = result.stdout
            # TODO: DEBUGGING to be removed
            # metadata = 'Title               : A Hilbert Space Problem Book\nAuthor(s)           : Paul R. Halmos\nPublisher           : Springer\nLanguages           : eng\nRating              : 2.5\nPublished           : 1967-01-01T00:00:00+00:00\nIdentifiers         : goodreads:851559, isbn:9780387906850\nComments            : <p>From the Preface: "This book was written for the active reader. The first part consists of problems, frequently preceded by definitions and motivation, and sometimes followed by corollaries and historical remarks... The second part, a very short one, consists of hints... The third part, the longest, consists of solutions: proofs, answers, or contructions, depending on the nature of the problem....  </p>\n<p>This is not an introduction to Hilbert space theory. Some knowledge of that subject is a prerequisite: at the very least, a study of the elements of Hilbert space theory should proceed concurrently with the reading of this book."</p>\n'
            if metadata:
                with open(tmp_file, 'w') as f:
                    f.write(metadata)
                # TODO: is it necessary to sleep after fetching the metadata from
                # online sources like they do? The code is run sequentially, so
                # we are executing the rest of the code here once fetch_metadata()
                # is done, ref.: https://bit.ly/2vV9MfU
                logger.info('Successfully fetched metadata: ')
                logger.info(metadata)

                logger.info('Adding additional metadata to the end of the metadata file...')
                more_metadata = 'ISBN                : {}\n' \
                                'All found ISBNs     : {}\n' \
                                'Old file path       : {}\n' \
                                'Metadata source     : {}'.format(isbn, isbns, file_path, isbn_source)
                logger.info(more_metadata)
                with open(tmp_file, 'a') as f:
                    f.write(more_metadata)

                logger.info('Organizing {} (with {})...'.format(file_path, tmp_file))
                output_folder = config.config_dict['organize-ebooks']['output_folder']
                new_path = move_or_link_ebook_file_and_metadata(new_folder=output_folder,
                                                                current_ebook_path=file_path,
                                                                current_metadata_path=tmp_file)

                ok_file(file_path, new_path)
                # NOTE: `tmp_file` was already removed in move_or_link_ebook_file_and_metadata()
                return

        logger.info('Removing temp file {}...'.format(tmp_file))
        remove_file(tmp_file)

    if config.config_dict['organize-ebooks']['organize_without_isbn']:
        logger.info('Could not organize via the found ISBNs, organizing by filename and metadata instead...')
        organize_by_filename_and_meta(file_path, 'Could not fetch metadata for ISBNs {}'.format(isbns))
    else:
        logger.info('Organization by filename and metadata is not turned on, giving up...')
        skip_file(file_path, 'Could not fetch metadata for ISBNs {}; Non-ISBN organization disabled'.format(isbns))


def organize_file(file_path):
    file_err = check_file_for_corruption(file_path)
    if file_err:
        logger.info('File {} is corrupt with error: {}'.format(file_path, file_err))
        output_folder_corrupt = config.config_dict['organize-ebooks']['output_folder_corrupt']
        if output_folder_corrupt:
            new_path = unique_filename(output_folder_corrupt, os.path.basename(file_path))

            fail_file(file_path, 'File is corrupt: {}'.format(file_err), new_path)

            move_or_link_file(file_path, new_path)

            # TODO: do we add the meta extension directly to new_path (which
            # already has an extension); thus if new_path='/test/path/book.pdf'
            # then new_metadata_path='/test/path/book.pdf.meta' or should it be
            # new_metadata_path='/test/path/book.meta' (which is what I'm doing here)
            # ref.: https://bit.ly/2I6K3pW
            output_metadata_extension = config.config_dict['general-options']['output_metadata_extension']
            new_metadata_path = '{}.{}'.format(os.path.splitext(new_path)[0], output_metadata_extension)
            logger.info('Saving original filename to {}...'.format(new_metadata_path))
            if not config.config_dict['general-options']['dry_run']:
                metadata = 'Corruption reason   : {}\nOld file path       : {}\n'.format(file_err, file_path)
                with open(new_metadata_path, 'w') as f:
                    f.write(metadata)
        else:
            logger.info('Output folder for corrupt files is not set, doing nothing')
            fail_file(file_path, 'File is corrupt: {}'.format(file_err))
    elif config.config_dict['organize-ebooks']['corruption_check_only']:
        logger.info('We are only checking for corruption, do not continue organising...')
        skip_file(file_path, 'File appears OK')
    else:
        logger.info('File passed the corruption test, looking for ISBNs...')
        isbns = search_file_for_isbns(file_path)
        ipdb.set_trace()
        # TODO: debugging, remove False
        if isbns and False:
            logger.info('Organizing {} by ISBNs {}!'.format(file_path, isbns))
            organize_by_isbns(file_path, isbns)
        # TODO: debugging, remove True
        elif config.config_dict['organize-ebooks']['organize_without_isbn'] or True:
            logger.info('No ISBNs found for {}, organizing by filename and metadata...'.format(file_path))
            organize_by_filename_and_meta(file_path, 'No ISBNs found')
        else:
            skip_file(file_path, 'No ISBNs found; Non-ISBN organization disabled')
    logger.info('=====================================================')


if __name__ == '__main__':
    # IMPORTANT: command-line parameters have precedence over options in
    # configuration file, i.e. command-line parameters will override
    # options specified in the configuration file

    # Parse arguments from command-line
    # TODO: add description for each options in README.md
    description = '''
    eBook Organizer v{}
    
    For more information about the possible options, see the README.md

    NOTE: This is a Python port of organize-ebooks.sh @ 
    https://github.com/na--/ebook-tools/blob/master/organize-ebooks.sh
    '''.format(VERSION)
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(description),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage='python %(prog)s [OPTIONS] EBOOK_FOLDERS')

    group1 = parser.add_argument_group('organize-ebooks', 'eBook Organizer')
    group2 = parser.add_argument_group('general-options', 'Library for building ebook management scripts')
    group1.add_argument('-cco', '--corruption-check-only', action='store_true')
    group1.add_argument('-owi', '--organize-without-isbn', action='store_true')
    group1.add_argument('-wii', '--without-isbn-ignore', default=get_without_isbn_ignore())
    group1.add_argument('--tested-archive-extensions', default='^(7z|bz2|chm|arj|cab|gz|tgz|gzip|zip|rar|xz|tar|epub|docx|odt|ods|cbr|cbz|maff|iso)$')

    group1.add_argument('-o', '--output-folder', default=os.getcwd())
    group1.add_argument('-ofu', '--output-folder-uncertain', default='')
    group1.add_argument('-ofc', '--output-folder-corrupt', default='')
    group1.add_argument('-ofp', '--output-folder-pamphlets', default='')

    group1.add_argument('--pamphlet-included-files', default='\.(png|jpg|jpeg|gif|bmp|svg|csv|pptx)$')
    group1.add_argument('--pamphlet-excluded-files', default='\.(chm|epub|cbr|cbz|mobi|lit|pdb)$')
    group1.add_argument('--pamphlet-max-pdf-pages', default=50, type=int)
    group1.add_argument('--pamphlet-max-filesize-kib', default=250, type=int)

    handle_script_arg(group2)
    args = parser.parse_args()

    if args.disable_logging:
        # In the reference, they were using 'maxint' but in Python 3,
        # 'sys' has no attribute 'maxint'; thus I'm using 'maxsize' instead
        # ref.: https://stackoverflow.com/a/44101013
        # See https://stackoverflow.com/a/13795777 for a solution that uses
        # float("inf") instead of sys.maxsize which could also work with legacy Python 2.7
        logging.disable(sys.maxsize)
        # To enable logging:
        # logging.disable(logging.NOTSET)

    # NOTE: there are two parts where we try to setup logging:
    # (1) right after parsing the command-line and
    # (2) right after parsing the configuration file
    logging_enabled = False
    # (1st try) Setup logging right after parsing the command-line
    if args.logging_conf_path:
        if setup_logging(args.logging_conf_path) is None:
            # TODO: log instead of print; and by default pipe log through console
            print('[ERROR] Logging could not be setup')
            sys.exit(1)
        else:
            logging_enabled = True

    # Read configuration file
    init_config(args.config_path)

    # (2nd try) Setup logging right after parsing configuration file
    if not logging_enabled:
        try:
            if setup_logging(config.config_dict['general-options']['logging_conf_path']) is None:
                print('[ERROR] Logging could not be setup')
                sys.exit(1)
            else:
                logging_enabled = True
        except KeyError as e:
            get_full_exception(e)
            print('[ERROR] Logging could not be setup')
            sys.exit(1)

    # Update options from configuration file with arguments from command-line
    update_config_from_arg_groups(parser)

    ebook_folders = config.config_dict['organize-ebooks']['ebook_folders'].split(',')
    for fpath in ebook_folders:
        # Do some preprocessing on the file path: expand the file path if it
        # starts with '~' and remove whitespaces around file paths
        fpath = expand_folder_paths(fpath)
        fpath = check_comma_options(fpath)
        logger.info('Recursively scanning {} for files'.format(fpath))
        # TODO: They make use of sorting flags for walking through the files [FILE_SORT_FLAGS]
        # ref.: https://bit.ly/2HuI3YS
        for path, dirs, files in os.walk(fpath):
            for file in files:
                # TODO: catch any error and continue with next filename, see https://stackoverflow.com/a/26199212
                try:
                    organize_file(file_path=os.path.join(path, file))
                except KeyError as e:
                    err_msg = get_full_exception(error=e, to_print=False)
                    logger.critical(err_msg)
                    sys.exit(1)
    sys.exit(0)
