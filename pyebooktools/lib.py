"""Library that has useful functions for building other ebook management tools.

This is a Python port of `lib.sh`_ from `ebook-tools`_ written in Shell by
`na--`_.

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _lib.sh: https://github.com/na--/ebook-tools/blob/master/lib.sh
.. _na--: https://github.com/na--
"""
import ast
import mimetypes
import os
import re
import shlex
import shutil
import string
import subprocess
import tempfile
from lxml.etree import parse
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.utils.genutils import move
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
DRY_RUN = default_cfg.dry_run
ISBN_BLACKLIST_REGEX = default_cfg.isbn_blacklist_regex
ISBN_DIRECT_GREP_FILES = default_cfg.isbn_direct_grep_files
ISBN_GREP_REORDER_FILES = default_cfg.isbn_grep_reorder_files
ISBN_GREP_RF_REVERSE_LAST = default_cfg.isbn_grep_rf_reverse_last
ISBN_GREP_RF_SCAN_FIRST = default_cfg.isbn_grep_rf_scan_first
ISBN_IGNORED_FILES = default_cfg.isbn_ignored_files
ISBN_REGEX = default_cfg.isbn_regex
ISBN_RET_SEPARATOR = default_cfg.isbn_ret_separator
OCR_COMMAND = default_cfg.ocr_command
OCR_ENABLED = default_cfg.ocr_enabled
OCR_ONLY_FIRST_LAST_PAGES = default_cfg.ocr_only_first_last_pages
OUTPUT_FILENAME_TEMPLATE = default_cfg.output_filename_template
SYMLINK_ONLY = default_cfg.symlink_only
TESTED_ARCHIVE_EXTENSIONS = default_cfg.tested_archive_extensions

GREEN = '\033[0;32m'
RED = '\033[0;31m'
BOLD = '\033[1m'
NC = '\033[0m'

# TODO: move some functions to genutils, e.g.
# is_dir_empty, isalnum_in_file, remove_file, remove_tree remove_file


# For macOS use the built-in textutil,
# see https://stackoverflow.com/a/44003923/14664104
# TODO: important implement it
def catdoc(input_file, output_file):
    raise NotImplementedError('catdoc is not implemented')


# Checks the supplied file for different kinds of corruption:
#  - If it's zero-sized or contains only \0
#  - If it has a pdf extension but different mime type
#  - If it's a pdf and `pdfinfo` returns an error
#  - If it has an archive extension but `7z t` returns an error
# ref.: https://bit.ly/2JLpqgf
def check_file_for_corruption(file_path,
                              tested_archive_extensions=TESTED_ARCHIVE_EXTENSIONS):
    file_err = ''
    logger.info(f"Testing '{Path(file_path).name}' for corruption...")
    logger.debug(f"Full path: {file_path}")

    # TODO: test that it is the same as
    # if [[ "$(tr -d '\0' < "$file_path" | head -c 1)" == "" ]]; then
    # Ref.: https://bit.ly/2jpX0xf
    if is_file_empty(file_path):
        file_err = 'The file is empty or contains only zeros!'
        logger.debug(file_err)
        return file_err

    ext = Path(file_path).suffix[1:]  # Remove the dot from extension
    mime_type = get_mime_type(file_path)

    if mime_type == 'application/octet-stream' and \
            re.match('^(pdf|djv|djvu)$', mime_type):
        file_err = f"The file has a {ext} extension but '{mime_type}' MIME type!"
        logger.debug(file_err)
        return file_err
    elif mime_type == 'application/pdf':
        logger.info('Checking pdf file for integrity...')
        if not command_exists('pdfinfo'):
            file_err = 'pdfinfo does not exist, could not check if pdf is OK'
            logger.debug(file_err)
            return file_err
        else:
            pdfinfo_output = pdfinfo(file_path)
            if pdfinfo_output.stderr:
                logger.info('pdfinfo returned an error!')
                logger.debug(f'Error:\n{pdfinfo_output.stderr}')
                file_err = 'Has pdf MIME type or extension, but pdfinfo ' \
                           'returned an error!'
                logger.debug(file_err)
                return file_err
            else:
                logger.info('pdfinfo returned successfully')
                logger.debug(f'Output of pdfinfo:\n{pdfinfo_output.stdout}')
                if re.search('^Page size:\s*0 x 0 pts$', pdfinfo_output.stdout):
                    logger.info('pdf is corrupt anyway, page size property is '
                                'empty!')
                    file_err = 'pdf can be parsed, but page size is 0 x 0 pts!'
                    logger.debug(file_err)
                    return file_err

    if re.match(tested_archive_extensions, ext):
        logger.info(f"The file has a '{ext}' extension, testing with 7z...")
        log = test_archive(file_path)
        if log.stderr:
            logger.info('Test failed!')
            logger.debug(log.stderr)
            file_err = 'Looks like an archive, but testing it with 7z failed!'
            return file_err
        else:
            logger.info('Test succeeded!')
            logger.debug(log.stdout)

    if file_err == '':
        logger.info('Corruption not detected!')
    else:
        logger.warning(f'We are at the end of the function and '
                       f'file_err="{file_err}"; it should be empty!')
    return file_err


# Ref.: https://stackoverflow.com/a/28909933
def command_exists(cmd):
    return shutil.which(cmd) is not None


def convert_result_from_shell_cmd(old_result):
    class Result:
        def __init__(self):
            self.stdout = ''
            self.stderr = ''
            self.returncode = None
            self.args = None

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return f'stdout={self.stdout}, stderr={self.stderr}, ' \
                   f'returncode={self.returncode}, args={self.args}'

    new_result = Result()

    for attr_name, new_val in new_result.__dict__.items():
        old_val = getattr(old_result, attr_name)
        if old_val is None:
            shell_args = getattr(old_result, 'args', None)
            # logger.debug(f'result.{attr_name} is None. Shell args: {shell_args}')
        else:
            if isinstance(new_val, str):
                try:
                    new_val = old_val.decode('UTF-8')
                except AttributeError as e:
                    # TODO: add logger.debug?
                    # `old_val` already a string
                    # logger.debug('Error decoding old value: {}'.format(old_val))
                    # logger.debug(e.__repr__())
                    # logger.debug('Value already a string. No decoding necessary')
                    new_val = old_val
                try:
                    new_val = ast.literal_eval(new_val)
                # TODO: two errors on the same line
                except (SyntaxError, ValueError) as e:
                    # TODO: add logger.debug?
                    # NOTE: ValueError might happen if value consists of [A-Za-z]
                    # logger.debug('Error evaluating the value: {}'.format(old_val))
                    # logger.debug(e.__repr__())
                    # logger.debug('Aborting evaluation of string. Will consider
                    # the string as it is')
                    pass
            else:
                new_val = old_val
        setattr(new_result, attr_name, new_val)
    return new_result


# Tries to convert the supplied ebook file into .txt. It uses calibre's
# ebook-convert tool. For optimization, if present, it will use pdftotext
# for pdfs, catdoc for word files and djvutxt for djvu files.
# Ref.: https://bit.ly/2HXdf2I
def convert_to_txt(input_file, output_file, mime_type):
    result = None
    if mime_type == 'application/pdf' and command_exists('pdftotext'):
        logger.debug('The file looks like a pdf, using pdftotext to extract '
                     'the text')
        result = pdftotext(input_file, output_file)
    elif mime_type == 'application/msword' and command_exists('catdoc'):
        logger.debug('The file looks like a doc, using catdoc to extract the text')
        result = catdoc(input_file, output_file)
    # TODO: not need to specify the full path to djvutxt if you set correctly
    # the right env. variables
    elif mime_type.startswith('image/vnd.djvu') and \
            command_exists('/Applications/DjView.app/Contents/bin/djvutxt'):
        # TODO: important remove path to djvutxt in command_exists()
        logger.debug('The file looks like a djvu, using djvutxt to extract the '
                     'text')
        result = djvutxt(input_file, output_file)
    elif (not mime_type.startswith('image/vnd.djvu')) \
            and mime_type.startswith('image/'):
        logger.debug(f'The file looks like a normal image ({mime_type}), skipping '
                     'ebook-convert usage!')
    else:
        logger.debug("Trying to use calibre's ebook-convert to convert the "
                     f"{mime_type} file to .txt")
        result = ebook_convert(input_file, output_file)
    return result


def djvutxt(input_file, output_file):
    # TODO: explain that you need to softlink djvutxt in /user/local/bin (or
    # add in $PATH?)
    cmd = f'/Applications/DjView.app/Contents/bin/djvutxt "{input_file}" ' \
          f'"{output_file}"'
    # TODO: use genutils.run_cmd() [fix problem with 3.<6] and in other places?
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def ebook_convert(input_file, output_file):
    # TODO: explain that you need to softlink convert in /user/local/bin (or
    # add in $PATH?)
    cmd = f'ebook-convert "{input_file}" "{output_file}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def extract_archive(input_file, output_file):
    cmd = f'7z x -o "{output_file}" "{input_file}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Searches the input string for ISBN-like sequences and removes duplicates and
# finally validates them using is_isbn_valid() and returns them separated by
# `isbn_ret_separator`
# ref.: https://bit.ly/2HyLoSQ
def find_isbns(input_str, isbn_blacklist_regex=ISBN_BLACKLIST_REGEX,
               isbn_regex=ISBN_REGEX, isbn_ret_separator=ISBN_RET_SEPARATOR):
    isbns = []
    # TODO: they are using grep -oP
    # ref.: https://bit.ly/2HUbnIs
    # Remove spaces
    # input_str = input_str.replace(' ', '')
    matches = re.finditer(isbn_regex, input_str)
    for i, match in enumerate(matches):
        match = match.group()
        # Remove everything except numbers [0-9], 'x', and 'X'
        # NOTE: equivalent to UNIX command `tr -c -d '0-9xX'`
        # TODO 1: they don't remove \n in their code
        # TODO 2: put the following in a function
        del_tab = string.printable[10:].replace('x', '').replace('X', '')
        tran_tab = str.maketrans('', '', del_tab)
        match = match.translate(tran_tab)
        # Only keep unique ISBNs
        if match not in isbns:
            # Validate ISBN
            if is_isbn_valid(match):
                if re.match(isbn_blacklist_regex, match):
                    logger.debug(f'Wrong ISBN (blacklisted): {match}')
                else:
                    logger.debug(f'Valid ISBN found: {match}')
                    isbns.append(match)
            else:
                logger.debug(f'Invalid ISBN found: {match}')
        else:
            logger.debug(f'Non-unique ISBN found: {match}')
    if not isbns:
        msg = f'"{input_str}"' if len(input_str) < 100 else ''
        logger.debug(f'No ISBN found in the input string {msg}')
    return isbn_ret_separator.join(isbns)


def get_all_isbns_from_archive(file_path, isbn_ret_separator=ISBN_RET_SEPARATOR,
                               isbn_direct_grep_files=ISBN_DIRECT_GREP_FILES,
                               isbn_ignored_files=ISBN_IGNORED_FILES,
                               ocr_enabled=OCR_ENABLED):
    all_isbns = []
    tmpdir = tempfile.mkdtemp()

    logger.debug(f"Trying to decompress '{os.path.basename(file_path)}' and "
                 "recursively scan the contents")
    logger.debug(f"Decompressing '{file_path}' into tmp folder '{tmpdir}'")
    result = extract_archive(file_path, tmpdir)
    if result.stderr:
        logger.debug('Error extracting the file (probably not an archive)! '
                     'Removing tmp dir...')
        logger.debug(result.stderr)
        remove_tree(tmpdir)
        # TODO: return None?
        return ''

    logger.debug(f"Archive extracted successfully in '{tmpdir}', scanning "
                 f"contents recursively...")
    # TODO: ref.: https://stackoverflow.com/a/2759553
    # TODO: ignore .DS_Store
    for path, dirs, files in os.walk(tmpdir, topdown=False):
        # TODO: they use flag options for sorting the directory contents
        # see https://github.com/na--/ebook-tools#miscellaneous-options [FILE_SORT_FLAGS]
        for file_to_check in files:
            # TODO: add debug_prefixer
            file_to_check = os.path.join(path, file_to_check)
            isbns = search_file_for_isbns(file_to_check, isbn_direct_grep_files,
                                          isbn_ignored_files, ocr_enabled)
            if isbns:
                logger.debug(f"Found ISBNs '{isbns}'!")
                # TODO: two prints, one for stderror and the other for stdout
                logger.debug(isbns.replace(isbn_ret_separator, '\n'))
                for isbn in isbns.split(','):
                    if isbn not in all_isbns:
                        all_isbns.append(isbn)
            logger.debug(f'Removing {file_to_check}...')
            remove_file(file_to_check)
        if len(os.listdir(path)) == 0 and path != tmpdir:
            os.rmdir(path)
        elif path == tmpdir:
            if len(os.listdir(tmpdir)) == 1 and '.DS_Store' in tmpdir:
                remove_file(os.path.join(tmpdir, '.DS_Store'))
    logger.debug(f"Removing temporary folder '{tmpdir}' (should be empty)...")
    if is_dir_empty(tmpdir):
        remove_tree(tmpdir)
    return isbn_ret_separator.join(all_isbns)


def get_ebook_metadata(file_path):
    # TODO: add `ebook-meta` in PATH, right now it is only working for mac
    cmd = f'/Applications/calibre.app/Contents/MacOS/ebook-meta "{file_path}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Ref.: https://bit.ly/3txo53J
def get_metadata(source_data, xpath):
    return (u'\\n'.join(parse(source_data).xpath(xpath))).encode('utf-8')


# Using Python built-in module mimetypes
def get_mime_type(file_path):
    return mimetypes.guess_type(file_path)[0]


# Run shell command
# TODO: change function name
def get_mime_type_version2(file_path):
    # TODO: get MIME type with a python package, see the magic package
    # but dependency, ref.: https://stackoverflow.com/a/2753385
    cmd = f'file --brief --mime-type "{file_path}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.stdout.decode('UTF-8').split()[0]


# Return number of pages in djvu document
def get_pages_in_djvu(file_path):
    # TODO: To access the djvu command line utilities and their documentation,
    # you must set the shell variable PATH and MANPATH appropriately. This can
    # be achieved by invoking a convenient shell script hidden inside the
    # application bundle:
    #    $ eval `/Applications/DjView.app/Contents/setpath.sh`
    # ref.: ReadMe from DjVuLibre
    # TODO: not need to specify the full path to djvused if you set correctly
    # the right env. variables
    cmd = f'/Applications/DjView.app/Contents/bin/djvused -e "n" "{file_path}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Return number of pages in pdf document
def get_pages_in_pdf(file_path):
    # TODO: IMPORTANT add also the option to use `pdfinfo` (like in the
    # original shell script) since mdls is for macOS
    # TODO: see if you can find the number of pages using a python module
    # (e.g. PyPDF2) but dependency
    cmd = f'mdls -raw -name kMDItemNumberOfPages "{file_path}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Checks if directory is empty
# Ref.: https://stackoverflow.com/a/47363995
def is_dir_empty(path):
    return next(os.scandir(path), None) is None


# Ref.: https://stackoverflow.com/a/15924160
def is_file_empty(file_path):
    # TODO: test when file doesn't exist
    # TODO: see if the proposed solution @ https://stackoverflow.com/a/15924160
    # is equivalent to using try and catch the `OSError`
    try:
        return not os.path.getsize(file_path) > 0
    except OSError as e:
        print(f'Error: {e.filename} - {e.strerror}')
        return False


# Validates ISBN-10 and ISBN-13 numbers
# Ref.: https://bit.ly/2HO2lMD
def is_isbn_valid(isbn):
    # TODO: there is also a Python package for validating ISBNs (but dependency)
    # Remove whitespaces (space, tab, newline, and so on), '-', and capitalize all
    # characters (ISBNs can consist of numbers [0-9] and the letters [xX])
    isbn = ''.join(isbn.split())
    isbn = isbn.replace('-', '')
    isbn = isbn.upper()

    sum = 0
    # Case 1: ISBN-10
    if len(isbn) == 10:
        for i in range(len(isbn)):
            number = int(isbn[i])
            if i == 9 and isbn[i] == 'X':
                number = 10
            sum += (number * (10 - i))
        if sum % 11 == 0:
            return True
    # Case 2: ISBN-13
    elif len(isbn) == 13:
        if isbn[0:3] in ['978', '979']:
            for i in range(0, len(isbn), 2):
                sum += int(isbn[i])
            for i in range(1, len(isbn), 2):
                sum += (int(isbn[i])*3)
            if sum % 10 == 0:
                return True
    return False


def isalnum_in_file(file_path):
    with open(file_path, 'r') as f:
        isalnum = False
        for line in f:
            for ch in line:
                if ch.isalnum():
                    isalnum = True
                    break
            if isalnum:
                break
    return isalnum


def move_or_link_file(current_path, new_path, dry_run=DRY_RUN,
                      symlink_only=SYMLINK_ONLY):
    new_folder = Path(new_path).parent
    if dry_run:
        logger.debug('DRY RUN! No file rename/move/symlink/etc. operations '
                     'will actually be executed')

    # Create folder
    if not new_folder.exists():
        logger.debug(f'Creating folder {new_folder}')
        if not dry_run:
            new_folder.mkdir()

    # Symlink or move file
    if symlink_only:
        logger.debug(f"Symlinking file '{current_path}' to '{new_path}'...")
        if not dry_run:
            Path(new_path).symlink_to(current_path)
    else:
        logger.debug(f"Moving file '{current_path}' to '{new_path}'...")
        if not dry_run:
            move(current_path, new_path, clobber=False)
            # TODO: important, remove next
            """
            if not Path(new_path).exists():
                shutil.move(current_path, new_path)
            else:
                logger.debug(f'File already exists: {new_path}')
            """


# OCR on a pdf, djvu document or image
# NOTE: If pdf or djvu document, then first needs to be converted to image and
# then OCR
def ocr_file(input_file, output_file, mime_type,
             ocr_command=OCR_COMMAND,
             ocr_only_first_last_pages=OCR_ONLY_FIRST_LAST_PAGES):
    def convert_pdf_page(page, input_file, output_file):
        # Convert pdf to png image
        cmd = f'gs -dSAFER -q -r300 -dFirstPage={page} -dLastPage={page} ' \
              '-dNOPAUSE -dINTERPOLATE -sDEVICE=png16m ' \
              f'-sOutputFile="{output_file}" "{input_file}" -c quit'
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return convert_result_from_shell_cmd(result)

    # Convert djvu to tif image
    def convert_djvu_page(page, input_file, output_file):
        # TODO: IMPORTANT not need to specify the full path to djvused if you
        # set correctly the right env. variables
        cmd = f'/Applications/DjView.app/Contents/bin/ddjvu -page={page} ' \
              f'-format=tif {input_file} {output_file}'
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return convert_result_from_shell_cmd(result)

    if mime_type.startswith('application/pdf'):
        # TODO: they are using the `pdfinfo` command but it might not be present;
        # in check_file_for_corruption(), they are testing if this command exists
        # but not in ocr_file()
        result = get_pages_in_pdf(input_file)
        num_pages = result.stdout
        logger.debug(f"Result of '{get_pages_in_pdf.__repr__()}' on "
                     f"'{input_file}':\n{result}")
        page_convert_cmd = convert_pdf_page
    elif mime_type.startswith('image/vnd.djvu'):
        result = get_pages_in_djvu(input_file)
        num_pages = result.stdout
        logger.debug(f"Result of '{get_pages_in_djvu.__repr__()}' on "
                     f"'{input_file}':\n{result}")
        page_convert_cmd = convert_djvu_page
    elif mime_type.startswith('image/'):
        # TODO: in their code, they don't initialize num_pages
        logger.debug(f"Running OCR on file '{input_file}' and with mime type "
                     f"'{mime_type}'...")
        # TODO: find out if you can call the ocr_command function without `eval`
        if ocr_command in globals():
            result = eval(f'{ocr_command}("{input_file}", "{output_file}")')
            logger.debug("Result of '{ocr_command.__repr__()}':\n{result}")
        else:
            logger.debug(f"Function '{ocr_command}' doesn't exit. Ending ocr.")
            return 1
        # TODO: they don't return anything
        return 0
    else:
        logger.info(f"Unsupported mime type '{mime_type}'!")
        return 2

    if ocr_command not in globals():
        logger.debug(f"Function '{ocr_command}' doesn't exit. Ending ocr.")
        return 1

    logger.info(f"Will run OCR on file '{input_file}' with {num_pages} "
                f"page{'s' if num_pages > 1 else ''}...")
    logger.debug(f'mime type: {mime_type}')

    # TODO: ? assert on ocr_only_first_last_pages (should be tuple or False)
    # Pre-compute the list of pages to process based on ocr_first_pages and
    # ocr_last_pages
    if ocr_only_first_last_pages:
        ocr_first_pages, ocr_last_pages = \
            [int(i) for i in ocr_only_first_last_pages.split(',')]
        pages_to_process = [i for i in range(1, ocr_first_pages+1)]
        pages_to_process.extend(
            [i for i in range(num_pages+1-ocr_last_pages, num_pages+1)])
    else:
        # `ocr_only_first_last_pages` is False
        logger.debug('ocr_only_first_last_pages is False')
        pages_to_process = [i for i in range(1, num_pages+1)]
    logger.debug(f'Pages to process: {pages_to_process}')

    text = ''
    for page in pages_to_process:
        # Make temporary files
        tmp_file = tempfile.mkstemp()[1]
        tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
        logger.debug(f'Running OCR of page {page} ...')
        logger.debug(f'Using tmp files {tmp_file} and {tmp_file_txt}')
        # doc(pdf, djvu) --> image(png, tiff)
        result = page_convert_cmd(page, input_file, tmp_file)
        logger.debug(f"Result of {page_convert_cmd.__repr__()}:\n{result}")
        # image --> text
        logger.debug(f"Running the '{ocr_command}' ...")
        result = eval(f'{ocr_command}("{tmp_file}", "{tmp_file_txt}")')
        logger.debug(f"Result of '{ocr_command.__repr__()}':\n{result}")
        with open(tmp_file_txt, 'r') as f:
            data = f.read()
            # TODO: remove this debug eventually; too much data printed
            logger.debug(f"Text content of page {page}:\n{data}")
        text += data
        # Remove temporary files
        logger.debug('Cleaning up tmp files')
        remove_file(tmp_file)
        remove_file(tmp_file_txt)

    # Everything on the stdout must be copied to the output file
    logger.debug('Saving the text content')
    with open(output_file, 'w') as f:
        f.write(text)
    # TODO: they don't return anything
    return 0


def pdfinfo(file_path):
    cmd = 'pdfinfo "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def pdftotext(input_file, output_file):
    cmd = f'pdftotext "{input_file}" "{output_file}"'
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# TODO: place it (and other path-related functions) in genutils
def remove_file(file_path):
    # TODO add reference: https://stackoverflow.com/a/42641792
    try:
        os.remove(file_path)
        return 0
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        return 1


# Recursively delete a directory tree, including the parent directory
# ref.: https://stackoverflow.com/a/186236
def remove_tree(file_path):
    # TODO:
    try:
        shutil.rmtree(file_path)
        return 0
    except Exception as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        return 1


# If `isbn_grep_reorder_files` is enabled, reorders the specified file
# according to the values of `isbn_grep_rf_scan_first` and
# `isbn_grep_rf_reverse_last`
# ref.: https://bit.ly/2JuaEKw
# TODO: order params and other places
def reorder_file_content(
        file_path,
        isbn_grep_reorder_files=ISBN_GREP_REORDER_FILES,
        isbn_grep_rf_scan_first=ISBN_GREP_RF_SCAN_FIRST,
        isbn_grep_rf_reverse_last=ISBN_GREP_RF_REVERSE_LAST):
    if isbn_grep_reorder_files:
        logger.debug('Reordering input file (if possible), read first '
                     f'{isbn_grep_rf_scan_first} lines normally, then read '
                     f'last {isbn_grep_rf_reverse_last} lines in reverse and '
                     'then read the rest')
        # TODO: try out with big file, more than 800 pages (approx. 73k lines)
        # TODO: see alternatives for reading big file @
        # https://stackoverflow.com/a/4999741 (mmap),
        # https://stackoverflow.com/a/24809292 (linecache),
        # https://stackoverflow.com/a/42733235 (buffer)
        with open(file_path, 'r') as f:
            # Read whole file as a list of lines
            # TODO: do we remove newlines? e.g. with f.read().rstrip("\n")
            data = f.readlines()
            # Read the first ISBN_GREP_RF_SCAN_FIRST lines of the file text
            first_part = data[:isbn_grep_rf_scan_first]
            del data[:isbn_grep_rf_scan_first]
            # Read the last part and reverse it
            last_part = data[-isbn_grep_rf_reverse_last:]
            if last_part:
                last_part.reverse()
                del data[-isbn_grep_rf_reverse_last:]
            # Read the middle part of the file text
            middle_part = data
            # TODO: try out with large lists, if efficiency is a concern then
            # check itertools.chain
            # ref.: https://stackoverflow.com/a/4344735
            # Concatenate the three parts: first, last part (reversed), and
            # middle part
            data = first_part + last_part + middle_part
            data = "".join(data)
    else:
        logger.debug('Since isbn_grep_reorder_files is False, input file will '
                     'not be reordered')
        with open(file_path, 'r') as f:
            # TODO: do we remove newlines? e.g. with f.read().rstrip("\n")
            # Read whole content of file as a string
            data = f.read()
    return data


# Tries to find ISBN numbers in the given ebook file by using progressively
# more "expensive" tactics.
# These are the steps:
# 1. Check the supplied file name for ISBNs (the path is ignored)
# 2. If the MIME type of the file matches `isbn_direct_grep_files`, search the
#    file contents directly for ISBNs
# 3. If the MIME type matches `isbn_ignored_files`, the function returns early
#    with no results
# 4. Check the file metadata from calibre's `ebook-meta` for ISBNs
# 5. Try to extract the file as an archive with `7z`; if successful,
#    recursively call search_file_for_isbns for all the extracted files
# 6. If the file is not an archive, try to convert it to a .txt file
#    via convert_to_txt()
# 7. If OCR is enabled and convert_to_txt() fails or its result is empty,
#    try OCR-ing the file. If the result is non-empty but does not contain
#    ISBNs and OCR_ENABLED is set to "always", run OCR as well.
# ref.: https://bit.ly/2r28US2
def search_file_for_isbns(file_path,
                          isbn_blacklist_regex=ISBN_BLACKLIST_REGEX,
                          isbn_direct_grep_files=ISBN_DIRECT_GREP_FILES,
                          isbn_grep_reorder_files=ISBN_GREP_REORDER_FILES,
                          isbn_grep_rf_reverse_last=ISBN_GREP_RF_REVERSE_LAST,
                          isbn_grep_rf_scan_first=ISBN_GREP_RF_SCAN_FIRST,
                          isbn_ignored_files=ISBN_IGNORED_FILES,
                          isbn_regex=ISBN_REGEX,
                          isbn_ret_separator=ISBN_RET_SEPARATOR,
                          ocr_command=OCR_COMMAND, ocr_enabled=OCR_ENABLED,
                          ocr_only_first_last_pages=OCR_ONLY_FIRST_LAST_PAGES):
    basename = os.path.basename(file_path)
    logger.info(f"Searching file '{basename}' for ISBN numbers...")
    # Step 1: check the filename for ISBNs
    # TODO: make sure that we return an empty string when we can't find ISBNs
    logger.debug('check the filename for ISBNs')
    isbns = find_isbns(basename, isbn_blacklist_regex, isbn_regex,
                       isbn_ret_separator)
    if isbns:
        logger.debug("Extracted ISBNs '{}' from the file name!".format(
            isbns.replace('\n', '; ')))
        return isbns

    # Steps 2-3: (2) if valid MIME type, search file contents for isbns and
    # (3) if invalid MIME type, exit without results
    mime_type = get_mime_type(file_path)
    if re.match(isbn_direct_grep_files, mime_type):
        logger.debug('Ebook is in text format, trying to find ISBN directly')
        data = reorder_file_content(file_path, isbn_grep_reorder_files,
                                    isbn_grep_rf_scan_first,
                                    isbn_grep_rf_reverse_last)
        isbns = find_isbns(data, isbn_blacklist_regex, isbn_regex,
                           isbn_ret_separator)
        if isbns:
            logger.debug(f"Extracted ISBNs '{isbns}' from the text file contents!")
        else:
            logger.debug('Did not find any ISBNs')
        return isbns
    elif re.match(isbn_ignored_files, mime_type):
        logger.info('The file type is in the blacklist, ignoring...')
        return isbns

    # Step 4: check the file metadata from calibre's `ebook-meta` for ISBNs
    logger.debug("check the file metadata from calibre's `ebook-meta` for ISBNs")
    ebookmeta = get_ebook_metadata(file_path)
    logger.debug(f'Ebook metadata:\n{ebookmeta.stdout}')
    isbns = find_isbns(ebookmeta.stdout, isbn_blacklist_regex, isbn_regex,
                       isbn_ret_separator)
    if isbns:
        logger.debug(f"Extracted ISBNs '{isbns}' from calibre ebook metadata!")
        return isbns

    # Step 5: decompress with 7z
    logger.debug('decompress with 7z')
    isbns = get_all_isbns_from_archive(file_path, isbn_ret_separator,
                                       isbn_direct_grep_files,
                                       isbn_ignored_files, ocr_enabled)
    if isbns:
        logger.debug(f"Extracted ISBNs '{isbns}' from the archive file")
        return isbns

    # Step 6: convert file to .txt
    try_ocr = False
    tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
    logger.debug(f"Converting ebook to text format...")
    logger.debug(f"Temp file: {tmp_file_txt}")

    result = convert_to_txt(file_path, tmp_file_txt, mime_type)
    if result.returncode == 0:
        logger.debug('Conversion to text was successful, checking the result...')
        with open(tmp_file_txt, 'r') as f:
            data = f.read()
        # TODO: debug, to remove
        # data = '*'
        if not re.search('[A-Za-z0-9]+', data):
            logger.debug('The converted txt with size '
                         f'{os.stat(tmp_file_txt).st_size} bytes does not seem '
                         'to contain text')
            logger.debug(f'First 1000 characters:\n{data[:1000]}')
            try_ocr = True
        else:
            data = reorder_file_content(tmp_file_txt, isbn_grep_reorder_files,
                                        isbn_grep_rf_scan_first,
                                        isbn_grep_rf_reverse_last)
            isbns = find_isbns(data, isbn_blacklist_regex, isbn_regex,
                               isbn_ret_separator)
            if isbns:
                logger.debug(f"Text output contains ISBNs '{isbns}'!")
            elif ocr_enabled == 'always':
                logger.debug('We will try OCR because the successfully converted '
                             'text did not have any ISBNs')
                try_ocr = True
            else:
                logger.debug('Did not find any ISBNs and will NOT try OCR')
    else:
        logger.info('There was an error converting the book to txt format')
        try_ocr = True

    # Step 7: OCR the file
    if not isbns and ocr_enabled and try_ocr:
        logger.debug('Trying to run OCR on the file...')
        if ocr_file(file_path, tmp_file_txt, mime_type, ocr_command,
                    ocr_only_first_last_pages) == 0:
            logger.debug('OCR was successful, checking the result...')
            data = reorder_file_content(tmp_file_txt, isbn_grep_reorder_files,
                                        isbn_grep_rf_scan_first,
                                        isbn_grep_rf_reverse_last)
            isbns = find_isbns(data, isbn_blacklist_regex, isbn_regex,
                               isbn_ret_separator)
            if isbns:
                logger.debug(f"Text output contains ISBNs {isbns}!")
            else:
                logger.debug('Did not find any ISBNs in the OCR output')
        else:
            logger.info('There was an error while running OCR!')

    logger.debug(f'Removing {tmp_file_txt}...')
    remove_file(tmp_file_txt)

    if isbns:
        logger.debug(f"Returning the found ISBNs '{isbns}'!")
    else:
        logger.debug(f'Could not find any ISBNs in {file_path} :(')

    return isbns


def substitute_params(hashmap, output_filename_template=OUTPUT_FILENAME_TEMPLATE):
    array = ''
    for k, v in hashmap.items():
        if isinstance(v, bytes):
            v = v.decode('UTF-8')
        # logger.debug(f'{hashmap[k]}')
        array += ' ["{}"]="{}" '.format(k, v)

    cmd = 'declare -A d=( {} )'  # debug: `echo "${d[TITLE]}"`
    cmd = cmd.format(array)
    # TODO: make it safer; maybe by removing single/double quotes marks from
    # OUTPUT_FILENAME_TEMPLATE
    # TODO: explain what's going
    cmd += f'; OUTPUT_FILENAME_TEMPLATE=\'"{output_filename_template}"\'; ' \
           'eval echo "$OUTPUT_FILENAME_TEMPLATE"'
    result = subprocess.Popen(['/usr/local/bin/bash', '-c', cmd],
                              stdout=subprocess.PIPE)
    return result.stdout.read().decode('UTF-8').strip()


def substitute_with_sed(regex, replacement, text):
    # Remove trailing whitespace, including tab
    text = text.strip()
    p1 = subprocess.Popen(['echo', text], stdout=subprocess.PIPE)
    # TODO: explain what's going on with this replacement code
    cmd = f"sed -e 's/{regex}/{replacement}/g'"
    args = shlex.split(cmd)
    p2 = subprocess.Popen(args, stdin=p1.stdout, stdout=subprocess.PIPE)
    replaced_text = p2.communicate()[0].decode('UTF-8').strip()
    # Get only the first 100 characters
    return replaced_text[:100]


# OCR: convert image to text
def tesseract_wrapper(input_file, output_file):
    # cmd = 'tesseract INPUT_FILE stdout --psm 12 > OUTPUT_FILE || exit 1
    cmd = f'tesseract "{input_file}" stdout --psm 12'
    args = shlex.split(cmd)
    result = subprocess.run(args,
                            stdout=open(output_file, 'w'),
                            stderr=subprocess.PIPE,
                            encoding='utf-8',
                            bufsize=4096)
    return convert_result_from_shell_cmd(result)


def test_archive(file_path):
    cmd = '7z t "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Return "folder_path/basename" if no file exists at this path. Otherwise,
# sequentially insert " ($n)" before the extension of `basename` and return the
# first path for which no file is present.
# ref.: https://bit.ly/3n1JNuk
def unique_filename(folder_path, basename):
    stem = Path(basename).stem
    ext = Path(basename).suffix
    new_path = Path(Path(folder_path).joinpath(basename))
    counter = 0
    while new_path.is_file():
        counter += 1
        logger.debug(f"File '{new_path.name}' already exists in destination "
                     f"'{folder_path}', trying with counter {counter}!")
        new_stem = f'{stem} {counter}'
        new_path = Path(Path(folder_path).joinpath(new_stem + ext))
    return new_path.as_posix()
