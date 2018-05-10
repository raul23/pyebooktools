"""
A Python port of ebooks-managing shell scripts from https://github.com/na--/ebook-tools
"""
# TODO: python3 compatible only, e.g. print('', end='') [use from __future__ import print_function for python 2]
# ref.: https://stackoverflow.com/a/5071123
# import PyPDF2
import argparse
import ast
from datetime import datetime
import ipdb
import logging
import os
from pathlib import Path
import re
import shlex
import shutil
import string
import subprocess
import tempfile


import config
from utils.path import file_exists


logger = logging.getLogger('{}.{}'.format(os.path.basename(os.path.dirname(__file__)), __name__))


VERSION = '0.5.1'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
BOLD = '\033[1m'
NC = '\033[0m'


# OCR: converts image to text
def tesseract_wrapper(input_file, output_file):
    # cmd = 'tesseract INPUT_FILE stdout --psm 12 > OUTPUT_FILE || exit 1
    cmd = 'tesseract "{}" stdout --psm 12'.format(input_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=open(output_file, 'w'), stderr=subprocess.PIPE, encoding='utf-8', bufsize=4096)
    return convert_result_from_shell_cmd(result)


# TODO: following variables should be checked first if they are set, if not
# then set with the specified value, like it is done in bash: ${FOO:=val}
# which means 'Set $FOO to val if not set'


# Horizontal whitespace and dash-like ASCII and Unicode characters that are
# used for better matching of ISBNs in (badly) OCR-ed books. Gathered from:
# - https://en.wikipedia.org/wiki/Whitespace_character
# - https://en.wikipedia.org/wiki/Dash#Similar_Unicode_characters
# - https://en.wikipedia.org/wiki/Dash#Common_dashes
# ref.: https://bit.ly/2r3C02G
"""
: "${WSD:="[\\x{0009}\\x{0020}\\x{00A0}\\x{1680}\\x{2000}\
\\x{2001}\\x{2002}\\x{2003}\\x{2004}\\x{2005}\\x{2006}\\x{2007}\\x{2008}\
\\x{2009}\\x{200A}\\x{202F}\\x{205F}\\x{3000}\\x{180E}\\x{200B}\\x{200C}\
\\x{200D}\\x{2060}\\x{FEFF}\\x{002D}\\x{005F}\\x{007E}\\x{00AD}\\x{00AF}\
\\x{02C9}\\x{02CD}\\x{02D7}\\x{02DC}\\x{2010}\\x{2011}\\x{2012}\\x{203E}\
\\x{2043}\\x{207B}\\x{208B}\\x{2212}\\x{223C}\\x{23AF}\\x{23E4}\\x{2500}\
\\x{2796}\\x{2E3A}\\x{2E3B}\\x{10191}\\x{2012}\\x{2013}\\x{2014}\\x{2015}\
\\x{2053}\\x{058A}\\x{05BE}\\x{1428}\\x{1B78}\\x{3161}\\x{30FC}\\x{FE63}\
\\x{FF0D}\\x{10110}\\x{1104B}\\x{11052}\\x{110BE}\\x{1D360}]?"}"
"""
# TODO: add ASCII and Unicode horizontal for whitespace and dash characters
WSD = []

# This regular expression should match most ISBN10/13-like sequences in
# texts. To minimize false-positives, matches should be passed through
# is_isbn_valid() or another ISBN validator
# ref.: https://bit.ly/2KgQ4yA
# TODO: remove the four next variables
# ISBN_REGEX = r"(?<![0-9])(-?9-?7[789]-?)?((-?[0-9]-?){9}[0-9xX])(?![0-9])"
# ISBN_DIRECT_GREP_FILES = "^(text/(plain|xml|html)|application/xml)$"
# ISBN_IGNORED_FILES = "^(image/(gif|svg.+)|application/(x-shockwave-flash|CDFV2|vnd.ms-opentype|x-font-ttf|x-dosexec|vnd.ms-excel|x-java-applet)|audio/.+|video/.+)$"
# ISBN_RET_SEPARATOR = ','

# These options specify if and how we should reorder ISBN_DIRECT_GREP files
# before passing them to find_isbns(). If true, the first
# ISBN_GREP_RF_SCAN_FIRST lines of the files are passed as is, then we pass
# the last ISBN_GREP_RF_REVERSE_LAST in reverse order and finally we pass the
# remainder in the middle. There is no issue if files have fewer lines, there
# will be no duplicate lines passed to grep.
# TODO: remove the three next variables
# ISBN_GREP_REORDER_FILES = True
# ISBN_GREP_RF_SCAN_FIRST = 400
# ISBN_GREP_RF_REVERSE_LAST = 50

# Whether to use OCR on image files, pdfs and djvu files for ISBN searching
# and conversion to txt
# TODO: remove the three next variables
# OCR_ENABLED = False
# OCR_ONLY_FIRST_LAST_PAGES = (4, 3)
# OCR_COMMAND = tesseract_wrapper


def get_re_year():
    # In bash: (19[0-9]|20[0-$(date '+%Y' | cut -b 3)])[0-9]"
    # output: (19[0-9]|20[0-1])[0-9]
    regex = '(19[0-9]|20[0-{}])[0-9]'.format(str(datetime.now())[2])
    return regex


def get_without_isbn_ignore():
    re_year = get_re_year()
    regex = ''
    # Perdiodicals with filenames that contain something like 2010-11, 199010, 2015_7, 20110203:
    regex += '(^|[^0-9]){}[ _\\.-]*(0?[1-9]|10|11|12)([0-9][0-9])?(\$|[^0-9])'.format(re_year)
    # Periodicals with month numbers before the year
    regex += '|(^|[^0-9])([0-9][0-9])?(0?[1-9]|10|11|12)[ _\\.-]*${RE_YEAR}(\$|[^0-9])'
    # Periodicals with months or issues
    regex += '|((^|[^a-z])(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?|mag(azine)?|issue|#[ _\\.-]*[0-9]+)+(\$|[^a-z]))'
    # Periodicals with seasons and years
    regex += '|((spr(ing)?|sum(mer)?|aut(umn)?|win(ter)?|fall)[ _\\.-]*${RE_YEAR})'
    regex += '|(${RE_YEAR}[ _\\.-]*(spr(ing)?|sum(mer)?|aut(umn)?|win(ter)?|fall))'
    # Remove newlines
    regex.split()
    return regex


# Should be matched against a lowercase filename.ext, lines that start with
# and newlines are removed. The default value should filter out most periodicals
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L74
WITHOUT_ISBN_IGNORE = get_without_isbn_ignore()


def convert_bytes_binary(num, unit):
    """
    this function will convert bytes to MiB.... GiB... etc

    ref.: https://stackoverflow.com/a/39988702
    """
    for x in ['bytes', 'KiB', 'MiB', 'GiB', 'TiB']:
        if num < 1024.0 or x == unit:
            # return "%3.1f %s" % (num, x)
            return num
        num /= 1024.0


def convert_bytes_decimal(num, unit):
    """
    this function will convert bytes to MB.... GB... etc

    ref.: https://stackoverflow.com/a/39988702
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1000.0 or x == unit:
            # return "%3.1f %s" % (num, x)
            return num
        num /= 1000.0


# NOTE: the original function was returning the file size in MB... GB... but it
# was actually returning the file in MiB... GiB... etc (dividing by 1024, not 1000)
# see the comment @ https://bit.ly/2HL5RnI
# TODO: call this function when computing file size here in lib.py
# TODO: unit can be given with binary prefix as {'bytes', 'KiB', 'MiB', 'GiB', TiB'}
# or decimal prefix as {'bytes', 'KB', 'MB', 'GB', TB'}
def get_file_size(file_path, unit):
    """
    This function will return the file size

    ref.: https://stackoverflow.com/a/39988702
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        if unit[1] == 'i':
            return convert_bytes_binary(file_info.st_size, unit=unit)
        else:
            return convert_bytes_decimal(file_info.st_size, unit=unit)


def get_ebook_metadata(file_path):
    # TODO: add `ebook-meta` in PATH, right now it is only working for mac
    cmd = '/Applications/calibre.app/Contents/MacOS/ebook-meta "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Returns number of pages in pdf document
def get_pages_in_pdf(file_path):
    # TODO: add also the option to use `pdfinfo` (like in the original shell script)
    # TODO: see if you can find the number of pages using a python module (e.g. PyPDF2)
    cmd = 'mdls -raw -name kMDItemNumberOfPages "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Returns number of pages in djvu document
def get_pages_in_djvu(file_path):
    # TODO: To access the djvu command line utilities and their documentation,
    # you must set the shell variable PATH and MANPATH appropriately. This can
    # be achieved by invoking a convenient shell script hidden inside the application bundle:
    #    $ eval `/Applications/DjView.app/Contents/setpath.sh`
    # ref.: ReadMe from DjVuLibre
    # TODO: not need to specify the full path to djvused if you set correctly the right env. variables
    cmd = '/Applications/DjView.app/Contents/bin/djvused -e "n" "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def pdfinfo(file_path):
    cmd = 'pdfinfo "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


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
            return 'stdout={}, stderr={}, returncode={}, args={}'.format(self.stdout, self.stderr, self.returncode, self.args)

    new_result = Result()

    for attr_name, new_val in new_result.__dict__.items():
        old_val = getattr(old_result, attr_name)
        if old_val is None:
            shell_args = getattr(old_result, 'args', None)
            logger.debug('result.{} is None. Shell args: {}'.format(attr_name, shell_args))
        else:
            if isinstance(new_val, str):
                try:
                    new_val = old_val.decode('UTF-8')
                except AttributeError as e:
                    # `old_val` already a string
                    # logger.debug('Error decoding old value: {}'.format(old_val))
                    # logger.debug(e.__repr__())
                    # logger.debug('Value already a string. No decoding necessary')
                    new_val = old_val
                try:
                    new_val = ast.literal_eval(new_val)
                # TODO: two errors on the same line
                except (SyntaxError, ValueError) as e:
                    # NOTE: ValueError might happen if value consists of [A-Za-z]
                    # logger.debug('Error evaluating the value: {}'.format(old_val))
                    # logger.debug(e.__repr__())
                    # logger.debug('Aborting evaluation of string. Will consider the string as it is')
                    pass
            else:
                new_val = old_val
        setattr(new_result, attr_name, new_val)
    return new_result


# TODO: place it (and other path-related functions) in the path module
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


# ref.: https://stackoverflow.com/a/15924160
def is_file_empty(file_path):
    # TODO: test when file doesn't exist
    # TODO: see if the proposed solution @ https://stackoverflow.com/a/15924160
    # is equivalent to using try and catch the `OSError`
    try:
        return not os.path.getsize(file_path) > 0
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        return False


# Checks the supplied file for different kinds of corruption:
#  - If it's zero-sized or contains only \0
#  - If it has a pdf extension but different mime type
#  - If it's a pdf and `pdfinfo` returns an error
#  - If it has an archive extension but `7z t` returns an error
# ref.: https://bit.ly/2JLpqgf
def check_file_for_corruption(file_path):
    file_err = ''
    logger.info('Testing {} for corruption...'.format(file_path))

    # TODO: test that it is the same as
    # if [[ "$(tr -d '\0' < "$file_path" | head -c 1)" == "" ]]; then
    # ref.: https://bit.ly/2jpX0xf
    if is_file_empty(file_path):
        file_err = 'The file {} is empty or contains only zeros!'.format(file_path)
        logger.debug(file_err)
        return file_err

    ext = Path(file_path).suffix[1:]  # Remove the dot from extension
    mime_type = get_mime_type(file_path)

    if mime_type == 'application/octet-stream' and re.match('^(pdf|djv|djvu)$', mime_type):
        file_err = 'The file has a {} extension but {} MIME type!'.format(ext, mime_type)
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
                logger.debug(pdfinfo_output.stderr)
                file_err = 'Has pdf MIME type or extension, but pdfinfo returned an error!'
                logger.debug(file_err)
                return file_err
            else:
                logger.info('pdfinfo returned successfully')
                logger.debug(pdfinfo_output.stdout)
                if re.search('^Page size:\s*0 x 0 pts$', pdfinfo_output.stdout):
                    logger.info('pdf is corrupt anyway, page size property is empty!')
                    file_err = 'pdf can be parsed, but page size is 0 x 0 pts!'
                    logger.debug(file_err)
                    return file_err

    if re.match(config.config_dict['organize-ebooks']['tested_archive_extensions'], ext):
        logger.info('The file has a {} extension, testing with 7z...'.format(ext))
        log = test_archive(file_path)
        if log.stderr:
            logger.info('Test failed!')
            logger.debug(log.stderr)
            file_err = 'Looks like an archive, but testing it with 7z failed!'
            return file_err
        else:
            logger.info('Test succeeded!')
            logger.debug(log.stdout)

    if file_err != '':
        logger.warning('We are at the end of the function and file_err="{}"; it '
                       'should be empty!'.format(file_err))
    return file_err


# OCR on a pdf, djvu document and image to extract ISBN
# NOTE: If pdf or djvu document: first needs to be converted to image and then OCR
def ocr_file(input_file, output_file, mime_type):
    def convert_pdf_page(page, input_file, output_file):
        # Converts pdf to png image
        cmd = 'gs -dSAFER -q -r300 -dFirstPage={} -dLastPage={} -dNOPAUSE ' \
              '-dINTERPOLATE -sDEVICE=png16m -sOutputFile="{}" "{}" -c quit'.format(page, page, output_file, input_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return convert_result_from_shell_cmd(result)

    # Converts djvu to tif image
    def convert_djvu_page(page, input_file, output_file):
        # TODO: not need to specify the full path to djvused if you set correctly the right env. variables
        cmd = '/Applications/DjView.app/Contents/bin/ddjvu -page={} ' \
              '-format=tif {} {}'.format(page, input_file, output_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return convert_result_from_shell_cmd(result)

    num_pages = 1
    page_convert_cmd = ''
    if mime_type.startswith('application/pdf'):
        # TODO: they are using the `pdfinfo` command but it might not be present;
        # in check_file_for_corruption(), they are testing if this command exists
        # but not in ocr_file()
        result = get_pages_in_pdf(input_file)
        num_pages = result.stdout
        logger.debug('Result of {} on {}:\n{}'.format(get_pages_in_pdf.__repr__(), input_file, result))
        logger.debug('{}'.format(result))
        page_convert_cmd = convert_pdf_page
    elif mime_type.startswith('image/vnd.djvu'):
        result = get_pages_in_djvu(input_file)
        num_pages = result.stdout
        logger.debug('Result of {} on {}:\n{}'.format(get_pages_in_djvu.__repr__(), input_file, result))
        page_convert_cmd = convert_djvu_page
    elif mime_type.startswith('image/'):
        # TODO: in their code, they don't initialize num_pages
        logger.info('Running OCR on file %s and with mime type %s...'
                    % (input_file, mime_type))
        # TODO: find out if you can call the ocr_command function without `eval`
        ocr_command = config.config_dict['general-options']['ocr_command']
        if ocr_command in globals():
            result = eval('{}("{}", "{}")'.format(ocr_command, input_file, output_file))
            logger.debug('Result of {}:\n{}'.format(ocr_command.__repr__(), result))
        else:
            logger.debug("Function {} doesn't exit. Ending ocr.".format(ocr_command))
            return 1
        # TODO: they don't return anything
        return 0
    else:
        logger.info('Unsupported mime type %s!' % mime_type)
        return 2

    ocr_command = config.config_dict['general-options']['ocr_command']
    if ocr_command not in globals():
        logger.debug("Function {} doesn't exit. Ending ocr.".format(ocr_command))
        return 1

    logger.info('Running OCR on file %s %s pages and with mime type %s...'
                % (input_file, num_pages, mime_type))

    ocr_only_first_last_pages = config.config_dict['general-options']['ocr_only_first_last_pages']
    ocr_first_pages, ocr_last_pages = [int(i) for i in ocr_only_first_last_pages.split(',')]
    # Pre-compute the list of pages to process based on ocr_first_pages and ocr_last_pages
    if ocr_only_first_last_pages:
        pages_to_process = [i for i in range(1, ocr_first_pages+1)]
        pages_to_process.extend([i for i in range(num_pages+1-ocr_last_pages, num_pages+1)])
    else:
        # `ocr_only_first_last_pages` is False
        logger.debug('ocr_only_first_last_pages is False')
        pages_to_process = [i for i in range(0, num_pages)]
    logger.debug('Pages to process: {}'.format(pages_to_process))

    text = ''
    for page in pages_to_process:
        # Make temporary files
        tmp_file = tempfile.mkstemp()[1]
        tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
        logger.info('Running OCR of page %s, using tmp files %s and %s ...'
                    % (page, tmp_file, tmp_file_txt))
        # doc(pdf, djvu) --> image(png, tiff)
        result = page_convert_cmd(page, input_file, tmp_file)
        logger.debug('Result of {}:\n{}'.format(page_convert_cmd.__repr__(), result))
        # image --> text
        result = eval('{}("{}", "{}")'.format(ocr_command, tmp_file, tmp_file_txt))
        logger.debug('Result of {}:\n{}'.format(ocr_command.__repr__(), result))
        with open(tmp_file_txt, 'r') as f:
            data = f.read()
            # TODO: remove this debug eventually; too much data printed
            logger.debug(data)
        text += data
        # Remove temporary files
        logger.info('Cleaning up tmp files %s and %s' % (tmp_file, tmp_file_txt))
        remove_file(tmp_file)
        remove_file(tmp_file_txt)

    # Everything on the stdout must be copied to the output file
    logger.info('Writing the reordered text')
    with open(output_file, 'w') as f:
        f.write(text)
    # TODO: they don't return anything
    return 0


# Validates ISBN-10 and ISBN-13 numbers
# ref.: https://bit.ly/2HO2lMD
def is_isbn_valid(isbn):
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


# Searches the input string for ISBN-like sequences and removes duplicates and
# finally validates them using is_isbn_valid() and returns them separated by
# `isbn_ret_separator`
# ref.: https://bit.ly/2HyLoSQ
def find_isbns(input_str):
    isbns = []
    # TODO: they are using grep -oP
    # ref.: https://bit.ly/2HUbnIs
    matches = re.finditer(config.config_dict['general-options']['isbn_regex'], input_str)
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
                isbns.append(match)
    return config.config_dict['find-isbns']['isbn_ret_separator'].join(isbns)


def get_mime_type(file_path):
    # TODO: get MIME type with a python package, see the magic package
    # ref.: https://stackoverflow.com/a/2753385
    cmd = 'file --brief --mime-type "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.stdout.decode('UTF-8').split()[0]


def extract_archive(input_file, output_file):
    cmd = '7z x -o"{}" {}'.format(output_file, input_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def test_archive(file_path):
    cmd = '7z t "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# If `isbn_grep_reorder_files` is enabled, reorders the specified file according
# to the values of `isbn_grep_rf_scan_first` and `isbn_grep_rf_reverse_last`
# ref.: https://bit.ly/2JuaEKw
def reorder_file_content(file_path):
    isbn_grep_rf_scan_first = config.config_dict['general-options']['isbn_grep_rf_scan_first']
    isbn_grep_rf_reverse_last = config.config_dict['general-options']['isbn_grep_rf_reverse_last']
    if config.config_dict['general-options']['isbn_grep_reorder_files']:
        logger.info('Reordering input file (if possible), read first '
                    'isbn_grep_rf_scan_first lines normally, then read last '
                    'isbn_grep_rf_reverse_last lines in reverse and then read '
                    'the rest')
        # TODO: try out with big file, more than 800 pages (approx. 73k lines)
        # TODO: see alternatives for reading big file @ https://stackoverflow.com/a/4999741 (mmap),
        # https://stackoverflow.com/a/24809292 (linecache), https://stackoverflow.com/a/42733235 (buffer)
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
            # Concatenate the three parts: first, last part (reversed), and middle part
            data = first_part + last_part + middle_part
            data = "".join(data)
    else:
        logger.info('Since isbn_grep_reorder_files is False, input file will not be reordered')
        with open(file_path, 'r') as f:
            # TODO: do we remove newlines? e.g. with f.read().rstrip("\n")
            # Read whole content of file as a string
            data = f.read()
    return data


# Checks if directory is empty
# ref.: https://stackoverflow.com/a/47363995
def is_dir_empty(path):
    return next(os.scandir(path), None) is None


def get_all_isbns_from_archive(file_path):
    all_isbns = []
    tmpdir = tempfile.mkdtemp()

    logger.info('Trying to decompress {} into tmp folder {} and recursively scan the contents'.format(file_path, tmpdir))
    result = extract_archive(file_path, tmpdir)
    if result.stderr:
        logger.info('Error extracting the file (probably not an archive)! Removing tmp dir...')
        logger.debug(result.stderr)
        remove_tree(tmpdir)
        return ''

    logger.info('Archive extracted successfully in {}, scanning contents recursively...'.format(tmpdir))
    # TODO: ref.: https://stackoverflow.com/a/2759553
    # TODO: ignore .DS_Store
    for path, dirs, files in os.walk(tmpdir, topdown=False):
        # TODO: they use flag options for sorting the directory contents
        # see https://github.com/na--/ebook-tools#miscellaneous-options [FILE_SORT_FLAGS]
        for file_to_check in files:
            # TODO: add debug_prefixer
            file_to_check = os.path.join(path, file_to_check)
            isbns = search_file_for_isbns(file_to_check)
            if isbns:
                logger.info('Found ISBNs {}!'.format(isbns))
                # TODO: two prints, one for stderror and the other for stdout
                logger.info(isbns.replace(config.config_dict['find-isbns']['isbn_ret_separator'], '\n'))
                for isbn in isbns.split(','):
                    if isbn not in all_isbns:
                        all_isbns.append(isbn)
            logger.info('Removing {}...'.format(file_to_check))
            remove_file(file_to_check)
        if len(os.listdir(path)) == 0 and path != tmpdir:
            os.rmdir(path)
        elif path == tmpdir:
            if len(os.listdir(tmpdir)) == 1 and '.DS_Store' in tmpdir:
                remove_file(os.path.join(tmpdir, '.DS_Store'))
    logger.info('Removing temporary folder {} (should be empty)...'.format(tmpdir))
    if is_dir_empty(tmpdir):
        remove_tree(tmpdir)
    return config.config_dict['find-isbns']['isbn_ret_separator'].join(all_isbns)


# ref.: https://stackoverflow.com/a/28909933
def command_exists(cmd):
    return shutil.which(cmd) is not None


def pdftotext(input_file, output_file):
    cmd = 'pdftotext "{}" "{}"'.format(input_file, output_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def catdoc(input_file, output_file):
    raise NotImplementedError('catdoc is not implemented')


def djvutxt(input_file, output_file):
    # TODO: add djvutxt in PATH
    cmd = '/Applications/DjView.app/Contents/bin/djvutxt "{}" "{}"'.format(input_file, output_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def ebook_convert(input_file, output_file):
    # TODO: add `ebook-convert` in $PATH
    cmd = '/Applications/calibre.app/Contents/MacOS/ebook-convert "{}" "{}"'.format(input_file, output_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Tries to convert the supplied ebook file into .txt. It uses calibre's
# ebook-convert tool. For optimization, if present, it will use pdftotext
# for pdfs, catdoc for word files and djvutxt for djvu files.
# ref.: https://bit.ly/2HXdf2I
def convert_to_txt(input_file, output_file, mime_type):
    result = None
    if mime_type == 'application/pdf' and command_exists('pdftotext'):
        logger.info('The file looks like a pdf, using pdftotext to extract the text')
        result = pdftotext(input_file, output_file)
    elif mime_type == 'application/msword' and command_exists('catdoc'):
        logger.info('The file looks like a doc, using catdoc to extract the text')
        result = catdoc(input_file, output_file)
    # TODO: not need to specify the full path to djvutxt if you set correctly the right env. variables
    elif mime_type.startswith('image/vnd.djvu') and command_exists('/Applications/DjView.app/Contents/bin/djvutxt'):
        logger.info('The file looks like a djvu, using djvutxt to extract the text')
        result = djvutxt(input_file, output_file)
    elif (not mime_type.startswith('image/vnd.djvu')) and mime_type.startswith('image/'):
        logger.info('The file looks like a normal image ({}), skipping ebook-convert usage!'.format(mime_type))
    else:
        logger.info("Trying to use calibre's ebook-convert to convert the {} file to .txt".format(mime_type))
        result = ebook_convert(input_file, output_file)
    return result


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
def search_file_for_isbns(file_path):
    logger.info('Searching file {} for ISBN numbers...'.format(file_path))
    # Step 1: check the filename for ISBNs
    basename = os.path.basename(file_path)
    # TODO: make sure that we return an empty string when we can't find ISBNs
    isbns = find_isbns(basename)
    if isbns:
        logger.info('Extracted ISBNs {} from the file name!'.format(isbns))
        return isbns

    # Steps 2-3: (2) if valid MIME type, search file contents for isbns and
    # (3) if invalid MIME type, exit without results
    mime_type = get_mime_type(file_path)
    if re.match(config.config_dict['general-options']['isbn_direct_grep_files'], mime_type):
        logger.info('Ebook is in text format, trying to find ISBN directly')
        data = reorder_file_content(file_path)
        isbns = find_isbns(data)
        if isbns:
            logger.info('STDERR: Extracted ISBNs {} from the text file contents!'.format(isbns))
        else:
            logger.info('STDERR: Did not find any ISBNs')
        return isbns
    elif re.match(config.config_dict['general-options']['isbn_ignored_files'], mime_type):
        logger.info('The file type in the blacklist, ignoring...')
        return isbns

    # Step 4: check the file metadata from calibre's `ebook-meta` for ISBNs
    logger.info('Ebook metadata:')
    ebookmeta = get_ebook_metadata(file_path)
    isbns = find_isbns(ebookmeta.stdout)
    if isbns:
        logger.info('Extracted ISBNs {} from calibre ebook metadata!'.format(isbns))
        return isbns

    # Step 5: decompress with 7z
    isbns = get_all_isbns_from_archive(file_path)
    if isbns:
        logger.info('Extracted ISBNs {} from the archive file'.format(isbns))
        return isbns

    # Step 6: convert file to .txt
    try_ocr = False
    tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
    logger.info('Converting ebook to text format in file {}...'.format(tmp_file_txt))

    result = convert_to_txt(file_path, tmp_file_txt, mime_type)
    if result.returncode == 0:
        logger.info('Conversion to text was successful, checking the result...')
        with open(tmp_file_txt, 'r') as f:
            data = f.read()
        # TODO: debug, to remove
        # data = '*'
        if not re.search('[A-Za-z0-9]+', data):
            logger.info('The converted txt with size {} bytes does not seem to '
                        'contain text'.format(os.stat(tmp_file_txt).st_size))
            logger.debug('First 1000 characters:\n{}'.format(data[:1000]))
            try_ocr = True
        else:
            data = reorder_file_content(tmp_file_txt)
            isbns = find_isbns(data)
            if isbns:
                logger.info('Text output contains ISBNs {}!'.format(isbns))
            elif config.config_dict['general-options']['ocr_enabled'] == 'always':
                logger.info('We will try OCR because the successfully converted '
                            'text did not have any ISBNs')
                try_ocr = True
            else:
                logger.info('Did not find any ISBNs and will NOT try OCR')
    else:
        logger.info('There was an error converting the book to txt format')
        try_ocr = True

    # Step 7: OCR the file
    # TODO: debug, to remove
    # config.config_dict['general-options']['ocr_enabled'] = True
    if not isbns and config.config_dict['general-options']['ocr_enabled'] and try_ocr:
        logger.info('Trying to run OCR on the file...')
        if ocr_file(file_path, tmp_file_txt, mime_type) == 0:
            logger.info('OCR was successful, checking the result...')
            data = reorder_file_content(tmp_file_txt)
            isbns = find_isbns(data)
            if isbns:
                logger.info('Text output contains ISBNs {}!'.format(isbns))
            else:
                logger.info('Did not find any ISBNs in the OCR output')
        else:
            logger.info('STDERR: There was an error while running OCR!')

    logger.info('Removing {}...'.format(tmp_file_txt))
    remove_file(tmp_file_txt)

    if isbns:
        logger.info('Returning the found ISBNs {}!'.format(isbns))
    else:
        logger.info('Could not find any ISBNs in {} :('.format(file_path))

    return isbns


# Return "folder_path/basename" if no file exists at this path. Otherwise,
# sequentially insert " ($n)" before the extension of `basename` and return the
# first path for which no file is present.
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L295
def unique_filename(folder_path, basename):
    stem = Path(basename).stem
    ext = Path(basename).suffix
    new_path = os.path.join(folder_path, basename)
    counter = 0
    while os.path.isfile(new_path):
        counter += 1
        logger.info('File {} already exists in destination {}, trying with counter {}!'.format(new_path, folder_path, counter))
        new_stem = '{} {}'.format(stem, counter)
        new_path = os.path.join(folder_path, new_stem) + ext
    return new_path


# TODO: all scripts should have access to `config.config_dict`
def move_or_link_file(current_path, new_path):
    new_folder = os.path.dirname(new_path)

    if config.config_dict['general-options']['dry_run']:
        logger.info('(DRY RUN! All operations except metadata deletion are skipped!)')

    if not os.path.isdir(new_folder):
        logger.info('Creating folder {}'.format(new_folder))
        if not config.config_dict['general-options']['dry_run']:
            os.makedirs(new_folder)

    if config.config_dict['general-options']['symlink_only']:
        logger.info('Symlinking file {} to {}...'.format(current_path, new_path))
        if not config.config_dict['general-options']['dry_run']:
            os.symlink(current_path, new_path)
    else:
        logger.info('Moving file {} to {}...'.format(current_path, new_path))
        if not config.config_dict['general-options']['dry_run']:
            # TODO: check if there are other places where you would need to expanduser()
            if not file_exists(new_path):
                shutil.move(current_path, new_path)
            else:
                logger.info('File already exists: {}'.format(new_path))


# ref.: https://bit.ly/2HxYEaw
# TODO: `output_filename_template` should be accessed from config.config_dict, all
# scripts should have access to config.config_dict
def move_or_link_ebook_file_and_metadata(new_folder, current_ebook_path, current_metadata_path):
    # Get ebook's file extension
    ext = Path(current_ebook_path).suffix
    ext = ext[1:] if ext[0] == '.' else ext
    d = {'EXT': ext}

    # Extract fields from metadata file
    with open(current_metadata_path, 'r') as f:
        for line in f:
            # Get field name and value separately, e.g.
            # 'Title  : A nice ebook' ---> field_name = 'Title  ' and field_value = ' A nice ebook'
            # Find the first colon and split on its position
            pos = line.find(':')
            field_name, field_value = line[:pos], line[pos+1:]

            # TODO: try to use subprocess.run instead of subprocess.Popen and
            # creating two processes
            # OR try to do it without subprocess, only with Python regex

            #########################
            # Processing field name #
            #########################
            #  Remove trailing whitespace, including tab
            field_name = field_name.strip()
            p1 = subprocess.Popen(['echo', field_name], stdout=subprocess.PIPE)
            # TODO: explain what's going on with this replacement code
            cmd = "sed -e 's/[ \t]*$//' -e 's/ /_/g' -e 's/[^a-zA-Z0-9_]//g'"
            args = shlex.split(cmd)
            p2 = subprocess.Popen(args, stdin=p1.stdout, stdout=subprocess.PIPE)
            # Remove '\n' at the end of `result`
            result = p2.communicate()[0].decode('UTF-8').strip()
            # TODO: converting characters to upper case with `-e 's/\(.*\)/\\U\1/'`
            # doesn't work on mac, \\U is not supported
            field_name = result.upper()

            ##########################
            # Processing field value #
            ##########################
            # Remove trailing whitespace, including tab
            field_value = field_value.strip()
            p1 = subprocess.Popen(['echo', field_value], stdout=subprocess.PIPE)
            # TODO: explain what's going on with this replacement code
            cmd = "sed -e 's/[\\/\*\?<>\|\x01-\x1F\x7F\x22\x24\x60]/_/g'"
            args = shlex.split(cmd)
            p2 = subprocess.Popen(args, stdin=p1.stdout, stdout=subprocess.PIPE)
            field_value = p2.communicate()[0].decode('UTF-8').strip()
            # Get only the first 100 characters
            field_value = field_value[:100]

            d[field_name] = field_value

    logger.info('Variables that will be used for the new filename construction:')
    array = ''
    for k, v in d.items():
        logger.debug('{}'.format(d[k]))
        array += ' ["{}"]="{}" '.format(k, v)

    cmd = 'declare -A d=( {} )'  # debug: `echo "${d[TITLE]}"`
    cmd = cmd.format(array)
    # TODO: make it safer; maybe by removing single/double quotation marks from `OUTPUT_FILENAME_TEMPLATE`
    # TODO: explain what's going
    cmd += '; OUTPUT_FILENAME_TEMPLATE=\'"{}"\'; eval echo "$OUTPUT_FILENAME_TEMPLATE"'.format(config.config_dict['general-options']['output_filename_template'])
    result = subprocess.Popen(['/usr/local/bin/bash', '-c', cmd], stdout=subprocess.PIPE)
    new_name = result.stdout.read().decode('UTF-8').strip()
    logger.info('The new file name of the book file/link {} will be: {}'.format(current_ebook_path, new_name))

    new_path = unique_filename(new_folder, new_name)
    logger.info('Full path: {}'.format(new_path))

    move_or_link_file(current_ebook_path, new_path)
    if config.config_dict['general-options']['keep_metadata']:
        logger.info('Removing metadata file {}...'.format(current_metadata_path))
        remove_file(current_metadata_path)
    else:
        new_metadata_path = '{}.{}'.format(new_path, config.config_dict['general-options']['output_metadata_extension'])
        logger.info('Moving metadata file {} to {}....'.format(current_metadata_path, new_metadata_path))
        if not config.config_dict['general-options']['dry_run']:
            if not file_exists(new_metadata_path):
                shutil.move(current_metadata_path, new_metadata_path)
            else:
                logger.info('File already exists: {}'.format(new_metadata_path))
        else:
            logger.debug('Removing current metadata file: {}'.format(current_metadata_path))
            remove_file(current_metadata_path)
    return new_path


# Uses Calibre's `fetch-ebook-metadata` CLI tool to download metadata from
# online sources. The first parameter is the comma-separated list of allowed
# plugins (e.g. 'Goodreads,Amazon.com,Google') and the second parameter is the
# remaining of the `fetch-ebook-metadata`'s options, e.g.
# options='--verbose --opf isbn=1234567890'
# Returns the ebook metadata as a string; if no metadata found, an empty string
# is returned
# ref.: https://bit.ly/2HS0iXQ
def fetch_metadata(isbn_sources, options=''):
    args = '{} {}'.format('fetch-ebook-metadata', options)
    isbn_sources = isbn_sources.split(',')
    for isbn_source in isbn_sources:
        args += ' --allowed-plugin={} '.format(isbn_source)
    # Remove trailing whitespace
    args = args.strip()
    logger.info('Calling `{}`'.format(args))
    args = shlex.split(args)
    # NOTE: `stderr` contains the whole log from running the fetch-data query
    # from the specified online sources. Thus, `stderr` is a superset of
    # `stdout` which only contains the ebook metadata for those fields that
    # have the pattern '[a-zA-Z()]+ +: .*'
    # TODO: make sure that you are getting only the fields that match the pattern
    # '[a-zA-Z()]+ +: .*' since you are not using a regex on the result
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


class ReorderFilesAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ReorderFilesAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        # print('%r %r %r' % (namespace, values, option_string))
        # `values` should be a string with one or three values separated by strings,
        # e.g. 'True, 400, 50' or 'False'
        # Each value corresponds to a specific option: isbn_grep_reorder_files,
        # isbn_grep_rf_scan_first, or isbn_grep_rf_reverse_last
        options_values = values.split(',')
        if len(options_values) not in [1, 3]:
            # TODO: exit
            # TODO: log instead of print, same also in other places
            print("[ERROR] `{}` doesn't have the required number of values: {}".format(self.dest, values))
        # Set each option with the corresponding value
        setattr(namespace, 'isbn_grep_reorder_files', options_values[0])
        if len(options_values) == 3:
            setattr(namespace, 'isbn_grep_rf_scan_first', options_values[1])
            setattr(namespace, 'isbn_grep_rf_reverse_last', options_values[2])
        setattr(namespace, self.dest, values)


# Handle parsing from arguments and setting all the common config vars
# ref.: https://bit.ly/2KwN54Z
# NOTE: in-place modification of parser
def handle_script_arg(parser):
    parser.add_argument('--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('-c', '--config-path', default=os.path.join(os.getcwd(), 'config.yaml'))
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--dry-run', action='store_true')
    parser.add_argument('-sl', '--symlink-only', action='store_true')
    parser.add_argument('-km', '--keep-metadata', action='store_true')

    parser.add_argument('-i', '--isbn-regex', default='(?<![0-9])(-?9-?7[789]-?)?((-?[0-9]-?){9}[0-9xX])(?![0-9])')
    parser.add_argument('--isbn-direct-grep-files', default='^(text/(plain|xml|html)|application/xml)$')
    parser.add_argument('--isbn-ignored-files', default='^(image/(gif|svg.+)|application/(x-shockwave-flash|CDFV2|vnd.ms-opentype|x-font-ttf|x-dosexec|vnd.ms-excel|x-java-applet)|audio/.+|video/.+)$')
    parser.add_argument('--reorder-files-for-grep', default='True, 400, 50', action=ReorderFilesAction)
    parser.add_argument('-ocr', '--ocr-enabled', action='store_true')
    parser.add_argument('-ocrop', '--ocr-only-first-last-pages', default='7,3')
    parser.add_argument('-ocrc', '--ocr-command', default='tesseract_wrapper')

    parser.add_argument('--token-min-length', default=3, type=int)
    parser.add_argument('--tokens-to-ignore', default='ebook|book|novel|series|ed(ition)?|vol(ume)?|${RE_YEAR}')

    parser.add_argument('-imfo', '--isbn-metadata-fetch-order', default='Goodreads,Amazon.com,Google,ISBNDB,WorldCat xISBN,OZON.ru')
    parser.add_argument('-owis', '--organize-without-isbn-sources', default='Goodreads,Amazon.com,Google')
    # TODO: add argument FILE_SORT_FLAGS
    # parser.add_argument('-fsf', '--file-sort-flags', default='')

    parser.add_argument('-oft', '--output-filename-template', default='${d[AUTHORS]// & /, } - ${d[SERIES]:+[${d[SERIES]}] - }${d[TITLE]/:/ -}${d[PUBLISHED]:+ (${d[PUBLISHED]%%-*})}${d[ISBN]:+ [${d[ISBN]}]}.${d[EXT]}')
    parser.add_argument('-ome', '--output-metadata-extension', default='meta')

    # TODO: add argument DEBUG_PREFIX_LENGTH
    # parser.add_argument('--debug-prefix-length', default=40, type=int)
    parser.add_argument('-dl', '--disable_logging', action='store_true')
    parser.add_argument('-lcp', '--logging_conf_path', default=os.path.join(os.getcwd(), 'logging_config.yaml'))


if __name__ == '__main__':
    # NOTE: to find file's mime type
    # file --brief --mime-type file.pdf

    # Testing ocr_file()
    # Test1: pdf document
    """
    ocr_file(input_file=os.path.expanduser('~/test/ebooks/book1.pdf'),
             output_file='out.txt',
             mime_type='application/pdf')

    # Test2: djvu document
    ocr_file(input_file=os.path.expanduser('~/test/ebooks/book2.djvu'),
             output_file='out.txt',
             mime_type='image/vnd.djvu')

    # Test3: image.png
    ocr_file(input_file=os.path.expanduser('~/test/ebooks/image.png'),
             output_file='out.txt',
             mime_type='image/')
    """

    # Testing search_file_for_isbns()
    # Test 1: check the filename for ISBNs
    # test_strs = ['/Users/test/ebooks/9788175257665_93-9483-398-9.pdf',
    #              '/Users/test/ebooks/ISBN9788175257665.djvu']
    # Test 2: check for duplicate ISBNs in filename
    # test_strs = ['/Users/test/ebooks/9788175257665_9788-1752-57665_9789475237625.pdf',
    #              '/Users/test/ebooks/ISBN9788175257665_9788175257665abcdef9788-1752-57665abcdef.pdf']
    # Test 3: validate ISBNs
    """
    valid_test_strs = ['/Users/test/ebooks/book_0-387-97812-7.pdf',
                       '/Users/test/ebooks/book_3-540-97812-7.pdf',
                       '/Users/test/ebooks/book_978-0-521-89806-5.djvu',
                       '/Users/test/ebooks/book9780198782926author.pdf'
                       '/Users/test/ebooks/image.png']
    invalid_test_strs = ['/Users/test/ebooks/book_977-0-521-89806-9.djvu',
                         '/Users/test/ebooks/book_978-0-521-28980-6.pdf',
                         '/Users/test/ebooks/book978-0-198-78292-4.pdf']
    # TODO: validate filenames with two and more ISBNs
    for s in valid_test_strs:
        search_file_for_isbns(s)
    for s in invalid_test_sts:
        search_file_for_isbns(s)
    
    # Test 4: if valid mime type, get ISBNs from file content (txt only) [step 4]
    test_strs = [os.path.expanduser('~/test/ebooks/book3.txt'),
                 os.path.expanduser('~/test/ebooks/book1.pdf'),
                 os.path.expanduser('~/test/ebooks/book2.djvu')]
    
    # Test 5: get ebook metadata with calibre's `ebook-meta`
    test_strs = [os.path.expanduser('~/test/ebooks/metadata.opf'),
                 os.path.expanduser('~/test/ebooks/book3.txt'),
                 os.path.expanduser('~/test/ebooks/book1.pdf')]
    """
    # Test 6: decompress with 7z [step 5]
    # test_strs = [os.path.expanduser('~/test/ebooks/books2.7z')]
    # Test 7: convert file to .txt
    # test_strs = [os.path.expanduser('~/test/ebooks/book1.pdf'),
    #              os.path.expanduser('~/test/ebooks/book2.djvu')]
    # Test 8: ocr the files
    OCR_ENABLED = True
    test_strs = [os.path.expanduser('~/test/ebooks/book2.djvu'),
                 os.path.expanduser('~/test/ebooks/book4.pdf')]
    for s in test_strs:
        search_file_for_isbns(s)
