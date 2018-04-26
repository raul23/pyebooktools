"""
A Python port of ebooks-managing shell scripts from https://github.com/na--/ebook-tools
"""
# TODO: python3 compatible only, e.g. print('', end='') [use from __future__ import print_function for python 2]
# ref.: https://stackoverflow.com/a/5071123
# import PyPDF2
import ipdb
import os
import re
import shlex
import shutil
import string
import subprocess
import tempfile


# OCR: converts image to text
def tesseract_wrapper(input_file, output_file):
    # cmd = 'tesseract INPUT_FILE stdout --psm 12 > OUTPUT_FILE || exit 1
    cmd = 'tesseract {} stdout --psm 12'.format(input_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=open(output_file, 'w'), encoding='utf-8', bufsize=4096)
    return result.returncode


# Horizontal whitespace and dash-like ASCII and Unicode characters that are
# used for better matching of ISBNs in (badly) OCR-ed books. Gathered from:
# - https://en.wikipedia.org/wiki/Whitespace_character
# - https://en.wikipedia.org/wiki/Dash#Similar_Unicode_characters
# - https://en.wikipedia.org/wiki/Dash#Common_dashes
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L31
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
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L46
ISBN_REGEX = r"(?<![0-9])(-?9-?7[789]-?)?((-?[0-9]-?){9}[0-9xX])(?![0-9])"
ISBN_DIRECT_GREP_FILES = "^(text/(plain|xml|html)|application/xml)$"
ISBN_IGNORED_FILES = "^(image/(gif|svg.+)|application/(x-shockwave-flash|CDFV2|vnd.ms-opentype|x-font-ttf|x-dosexec|vnd.ms-excel|x-java-applet)|audio/.+|video/.+)$"
ISBN_RET_SEPARATOR = ','

# These options specify if and how we should reorder ISBN_DIRECT_GREP files
# before passing them to find_isbns(). If true, the first
# ISBN_GREP_RF_SCAN_FIRST lines of the files are passed as is, then we pass
# the last ISBN_GREP_RF_REVERSE_LAST in reverse order and finally we pass the
# remainder in the middle. There is no issue if files have fewer lines, there
# will be no duplicate lines passed to grep.
ISBN_GREP_REORDER_FILES = True
ISBN_GREP_RF_SCAN_FIRST = 400
ISBN_GREP_RF_REVERSE_LAST = 50

# Whether to use OCR on image files, pdfs and djvu files for ISBN searching
# and conversion to txt
OCR_ENABLED = False
OCR_ONLY_FIRST_LAST_PAGES = (4, 3)
OCR_COMMAND = tesseract_wrapper


# TODO: place all the bash wrappers in a module in the utilities package
def cat(file_path):
    cmd = 'cat {}'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args)
    return result


def get_ebook_metadata(file_path):
    # TODO: add `ebook-meta` in PATH
    cmd = '/Applications/calibre.app/Contents/MacOS/ebook-meta {}'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.stdout.decode('UTF-8')


# Returns number of pages in pdf document
def get_pages_in_pdf(file_path):
    # TODO: add also the option to use `pdfinfo` (like in the original shell script)
    # TODO: see if you can find the number of pages using a python module (e.g. PyPDF2)
    cmd = 'mdls -raw -name kMDItemNumberOfPages %s' % file_path
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return int(result.stdout)


# Returns number of pages in djvu document
def get_pages_in_djvu(file_path):
    # TODO: To access the djvu command line utilities and their documentation,
    # you must set the shell variable PATH and MANPATH appropriately. This can
    # be achieved by invoking a convenient shell script hidden inside the application bundle:
    #    $ eval `/Applications/DjView.app/Contents/setpath.sh`
    # ref.: ReadMe from DjVuLibre
    # TODO: not need to specify the full path to djvused if you set correctly the right env. variables
    cmd = '/Applications/DjView.app/Contents/bin/djvused -e "n" %s' % file_path
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return int(result.stdout)


# TODO: place it in path module
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


# OCR on a pdf, djvu document and image to extract ISBN
# NOTE: If pdf or djvu document: first needs to be converted to image and then OCR
def ocr_file(input_file, output_file, mime_type):
    def convert_pdf_page(page, input_file, output_file):
        # Converts pdf to png image
        cmd = 'gs -dSAFER -q -r300 -dFirstPage=%s -dLastPage=%s -dNOPAUSE ' \
              '-dINTERPOLATE -sDEVICE=png16m -sOutputFile=%s %s -c quit' \
              % (page, page, output_file, input_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE)
        return result.returncode

    # Converts djvu to tif image
    def convert_djvu_page(page, input_file, output_file):
        # TODO: not need to specify the full path to djvused if you set correctly the right env. variables
        cmd = '/Applications/DjView.app/Contents/bin/ddjvu -page=%s -format=tif %s %s' % (page, input_file, output_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE)
        return result.returncode

    num_pages = 1
    page_convert_cmd = ''
    if mime_type.startswith('application/pdf'):
        # TODO: they are using the pdfinfo command but it might not be present; in check_file_for_corruption(), they
        # are testing if this command exists but not in ocr_file()
        num_pages = get_pages_in_pdf(input_file)
        page_convert_cmd = convert_pdf_page
    elif mime_type.startswith('image/vnd.djvu'):
        num_pages = get_pages_in_djvu(input_file)
        page_convert_cmd = convert_djvu_page
    elif mime_type.startswith('image/'):
        # TODO: in their code, they don't initialize num_pages
        print('Running OCR on file %s and with mimetype %s...'
              % (input_file, mime_type))
        OCR_COMMAND(input_file, output_file)
        # TODO: run > command
        # cmd = '> %s' % output_file
        # TODO: they don't return anything
        return 0
    else:
        print('STDERR: Unsupported mimetype %s!' % mime_type)
        return 4

    print('STDERR: Running OCR on file %s %s pages and with mimetype %s...'
          % (input_file, num_pages, mime_type))

    # TODO: if ocr_first_pages or ocr_last_pages, set them to 0
    ocr_first_pages = OCR_ONLY_FIRST_LAST_PAGES[0]
    ocr_last_pages = OCR_ONLY_FIRST_LAST_PAGES[1]
    # Pre-compute the list of pages to process based on ocr_first_pages and ocr_last_pages
    if OCR_ONLY_FIRST_LAST_PAGES:
        pages_to_process = [i+1 for i in range(0, ocr_first_pages)]
        pages_to_process.extend([i+1 for i in range(num_pages-ocr_last_pages, num_pages)])
    else:
        # OCR_ONLY_FIRST_LAST_PAGES is False
        pages_to_process = [i for i in range(0, num_pages)]

    text = ''
    for page in pages_to_process:
        # Make temporary files
        tmp_file = tempfile.mkstemp()[1]
        # TODO: on mac, --suffix option is not present for the command mktemp
        # mktemp --suffix='.txt'
        tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
        print('STDERR: Running OCR of page %s, using tmp files %s and %s ...'
              % (page, tmp_file, tmp_file_txt))

        # TODO: do something with the returned values, or better raise errors and log
        # the errors
        # doc(pdf, djvu) --> image(png, tiff)
        page_convert_cmd(page, input_file, tmp_file)
        # image --> text
        OCR_COMMAND(tmp_file, tmp_file_txt)
        with open(tmp_file_txt, 'r') as f:
            data = f.read()
            print(data)
        text += data
        # Remove temporary files
        print('STDERR: Cleaning up tmp files %s and %s' % (tmp_file, tmp_file_txt))
        remove_file(tmp_file)
        remove_file(tmp_file_txt)

    # Everything on the stdout must be copied to the output file
    with open(output_file, 'w') as f:
        f.write(text)
    # TODO: they don't return anything
    return 0


# Validates ISBN-10 and ISBN-13 numbers
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L215
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
# $ISBN_RET_SEPARATOR
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L274
def find_isbns(input_str):
    isbns = []
    matches = re.finditer(ISBN_REGEX, input_str)
    for i, match in enumerate(matches):
        match = match.group()
        # Remove everything except numbers [0-9], 'x', and 'X'
        # NOTE: equivalent to UNIX command `tr -c -d '0-9xX'`
        # TODO: they don't remove \n in their code
        # TODO: do the following in a function
        del_tab = string.printable[10:].replace('x', '').replace('X', '')
        tran_tab = str.maketrans('', '', del_tab)
        match = match.translate(tran_tab)
        # TODO: keep two lists, one for storing valid isbns and the other will store all the unique ISBNs tested so far
        # so that you don't have to call is_isbn_valid on ISBN already seen
        # Only keep unique ISBNs
        if not match in isbns:
            # Validate ISBN
            if is_isbn_valid(match):
                isbns.append(match)
    return ISBN_RET_SEPARATOR.join(isbns)


def get_mimetype(file_path):
    # TODO: handle errors in functions with returncode, check other functions
    # where don't use returncode
    # TODO: get MIME type with a python package, see the magic package
    # ref.: https://stackoverflow.com/a/2753385
    cmd = 'file --brief --mime-type {}'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.stdout.decode('UTF-8').split()[0]


def extract_archive(input_file, output_file):
    cmd = '7z x -o"{}" {}'.format(output_file, input_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.returncode


# If ISBN_GREP_REORDER_FILES is enabled, reorders the specified file according
# to the values of ISBN_GREP_RF_SCAN_FIRST and ISBN_GREP_RF_REVERSE_LAST
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L261
def reorder_file_content(file_path):
    if ISBN_GREP_REORDER_FILES:
        print('Reordering input file (if possible), read first ISBN_GREP_RF_SCAN_FIRST '
              'lines normally, then read last ISBN_GREP_RF_REVERSE_LAST lines '
              'in reverse and then read the rest')
        # TODO: try out with big file, more than 800 pages (approx. 73k lines)
        # TODO: see alternatives for reading big file @ https://stackoverflow.com/a/4999741 (mmap),
        # https://stackoverflow.com/a/24809292 (linecache), https://stackoverflow.com/a/42733235 (buffer)
        with open(file_path, 'r') as f:
            # Read whole file as a list of lines
            # TODO: do we remove newlines?
            data = f.readlines()
            # Read the first ISBN_GREP_RF_SCAN_FIRST lines of the file text
            first_part = data[:ISBN_GREP_RF_SCAN_FIRST]
            del data[:ISBN_GREP_RF_SCAN_FIRST]
            # Read the last part and reverse it
            last_part = data[-ISBN_GREP_RF_REVERSE_LAST:]
            if last_part:
                last_part.reverse()
                del data[-ISBN_GREP_RF_REVERSE_LAST:]
            # Read the middle part of the file text
            middle_part = data
            # TODO: try out with large lists, if efficiency is a concern then check itertools.chain
            # ref.: https://stackoverflow.com/a/4344735
            # Concatenate the three parts: first, last part (reversed), and middle part
            data = first_part + last_part + middle_part
            data = "".join(data)
    else:
        print('Since ISBN_GREP_REORDER_FILES is False, input file will not be reordered')
        with open(file_path, 'r') as f:
            # TODO: do we remove newlines? with f.read().rstrip("\n")
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

    print('Trying to decompress {} into tmp folder {} and recursively scan the contents'.format(file_path, tmpdir))
    # TODO: add debug_prefixer
    if extract_archive(file_path, tmpdir):
        print('Error extracting the file (probably not an archive)! Removing tmp dir...')
        remove_tree(tmpdir)
        return ''

    print('Archive extracted successfully in {}, scanning contents recursively...'.format(tmpdir))
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
                print('STDERR: Found ISBNs {}!'.format(isbns))
                # TODO: two prints, one for stderror and the other for stdout
                print(isbns.replace(ISBN_RET_SEPARATOR, '\n'))
                for isbn in isbns.split(','):
                    if isbn not in all_isbns:
                        all_isbns.append(isbn)
            print('STDERR: Removing {}...'.format(file_to_check))
            remove_file(file_to_check)
        if len(os.listdir(path)) == 0 and path != tmpdir:
            os.rmdir(path)
        elif path == tmpdir:
            if len(os.listdir(tmpdir)) == 1 and '.DS_Store' in tmpdir:
                remove_file(os.path.join(tmpdir, '.DS_Store'))
    print('Removing temporary folder {} (should be empty)...'.format(tmpdir))
    if is_dir_empty(tmpdir):
        remove_tree(tmpdir)
    return ISBN_RET_SEPARATOR.join(all_isbns)


# ref.: https://stackoverflow.com/a/28909933
def command_exists(cmd):
    return shutil.which(cmd) is not None


def pdftotext(input_file, output_file):
    cmd = 'pdftotext {} {}'.format(input_file, output_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.returncode


def catdoc(input_file, output_file):
    raise NotImplementedError('catdoc is not implemented')


def djvutxt(input_file, output_file):
    cmd = '/Applications/DjView.app/Contents/bin/djvutxt {} {}'.format(input_file, output_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.returncode


def ebook_convert(input_file, output_file):
    # TODO: add `ebook-convert` in PATH
    cmd = '/Applications/calibre.app/Contents/MacOS/ebook-convert {} {}'.format(input_file, output_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return result.returncode


# Tries to convert the supplied ebook file into .txt. It uses calibre's
# ebook-convert tool. For optimization, if present, it will use pdftotext
# for pdfs, catdoc for word files and djvutxt for djvu files.
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L393
def convert_to_txt(input_file, output_file, mimetype):
    if mimetype == 'application/pdf' and command_exists('pdftotext'):
        print('The file looks like a pdf, using pdftotext to extract the text')
        pdftotext(input_file, output_file)
    elif mimetype == 'application/msword' and command_exists('catdoc'):
        print('The file looks like a doc, using catdoc to extract the text')
        catdoc(input_file, output_file)
    # TODO: not need to specify the full path to djvutxt if you set correctly the right env. variables
    elif mimetype.startswith('image/vnd.djvu') and command_exists('/Applications/DjView.app/Contents/bin/djvutxt'):
        print('The file looks like a djvu, using djvutxt to extract the text')
        djvutxt(input_file, output_file)
    elif (not mimetype.startswith('image/vnd.djvu')) and mimetype.startswith('image/'):
        print('The file looks like a normal image ({}), skipping ebook-convert usage!'.format(mimetype))
        return 1
    else:
        print("Trying to use calibre's ebook-convert to convert the {} file to .txt".format(mimetype))
        ebook_convert(input_file, output_file)
    return 0


# Tries to find ISBN numbers in the given ebook file by using progressively
# more "expensive" tactics.
# These are the steps:
# 1. Check the supplied file name for ISBNs (the path is ignored)
# 2. If the MIME type of the file matches ISBN_DIRECT_GREP_FILES, search the
#    file contents directly for ISBNs
# 3. If the MIME type matches ISBN_IGNORED_FILES, the function returns early
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
    print('STDERR: Searching file {} for ISBN numbers...'.format(file_path))
    # Step 1: check the filename for ISBNs
    basename = os.path.basename(file_path)
    # TODO: make sure that we return an empty string when we can't find ISBNs
    isbns = find_isbns(basename)
    if isbns:
        print('STDERR: Extracted ISBNs {} from the file name!'.format(isbns))
        return isbns

    # Steps 2-3: (2) if valid MIME type, search file contents for isbns and
    # (3) if invalid MIME type, exit without results
    mimetype = get_mimetype(file_path)
    if re.match(ISBN_DIRECT_GREP_FILES, mimetype):
        print('STDERR: Ebook is in text format, trying to find ISBN directly')
        data = reorder_file_content(file_path)
        isbns = find_isbns(data)
        if isbns:
            print('STDERR: Extracted ISBNs {} from the text file contents!'.format(isbns))
        else:
            print('STDERR: Did not find any ISBNs')
        return isbns
    elif re.match(ISBN_IGNORED_FILES, mimetype):
        print('The file type in the blacklist, ignoring...')
        return isbns

    # Step 4: check the file metadata from calibre's `ebook-meta` for ISBNs
    print('STDERR: Ebook metadata:')
    # TODO: add the following
    # echo "$ebookmeta" | debug_prefixer "	" 0 --width=80 -t
    ebookmeta = get_ebook_metadata(file_path)
    isbns = find_isbns(ebookmeta)
    if isbns:
        print('STDERR: Extracted ISBNs {} from calibre ebook metadata!'.format(isbns))
        return isbns

    # Step 5: decompress with 7z
    isbns = get_all_isbns_from_archive(file_path)
    if isbns:
        print('STDERR: Extracted ISBNs {} from the archive file'.format(isbns))
        return isbns

    # Step 6: convert file to .txt
    try_ocr = False
    tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
    print('Converting ebook to text format in file {}...'.format(tmp_file_txt))

    # TODO: add debug_prefixer
    if convert_to_txt(file_path, tmp_file_txt, mimetype) == 0:
        print('Conversion to text was successful, checking the result...')
        with open(tmp_file_txt, 'r') as f:
            data = f.read()
        if not re.match('[A-Za-z0-9]+', data):
            print('The converted txt with size {} bytes does not seem to contain text:'
                  .format(os.stat(tmp_file_txt).st_size))
            try_ocr = True
        else:
            data = reorder_file_content(tmp_file_txt)
            isbns = find_isbns(data)
            if isbns:
                print('STDERR: Text output contains ISBNs {}!'.format(isbns))
            elif OCR_ENABLED == 'always':
                print('STDERR: We will try OCR because the successfully converted text did not have any ISBNs')
                try_ocr = True
            else:
                print('STDERR: Did not find any ISBNs and will NOT try OCR')
    else:
        print('There was an error converting the book to txt format')
        try_ocr = True

    # Step 7: OCR the file
    if not isbns and OCR_ENABLED is not False and try_ocr:
        print('Trying to run OCR on the file...')
        # TODO: add debug_prefixer
        if ocr_file(file_path, tmp_file_txt, mimetype) == 0:
            print('OCR was successful, checking the result...')
            data = reorder_file_content(tmp_file_txt)
            isbns = find_isbns(data)
            if isbns:
                print('STDERR: Text output contains ISBNs {}!'.format(isbns))
            else:
                print('Did not find any ISBNs in the OCR output')
        else:
            print('STDERR: There was an error while running OCR!')

    print('Removing {}...'.format(tmp_file_txt))
    remove_file(tmp_file_txt)

    if isbns:
        print('STDERR: Returning the found ISBNs {}!'.format(isbns))
    else:
        print('STDERR: Could not find any ISBNs in {} :('.format(file_path))

    return isbns


# Arguments: new_folder, current_ebook_path, current_metadata_path
# ref.: https://bit.ly/2HxYEaw
def move_or_link_ebook_file_and_metadata():
    pass


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
        # TODO: check if there are spaces in the arguments, and if it is the case
        # enclose the arguments in quotation marks. This testing should be done
        # in a separate function so that it can be called in other places.
        if ' ' in isbn_source:
            isbn_source = '"{}"'.format(isbn_source)
        args += ' --allowed-plugin={} '.format(isbn_source)
    # Remove trailing whitespace
    args = args.strip()
    print('Calling `{}`'.format(args))
    args = shlex.split(args)
    # NOTE: `stderr` contains the log from running the fetch-data query from the
    # specified online sources. Thus, `stderr` is a superset of `stdout` which
    # only contains the ebook metadata for those fields that have the pattern
    # '[a-zA-Z()]+ +: .*'
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('UTF-8')


if __name__ == '__main__':
    # NOTE: to find file's mimetype
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
    
    # Test 4: if valid mimetype, get ISBNs from file content (txt only) [step 4]
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
