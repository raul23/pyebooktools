"""
Port ebooks-managing shell scripts to Python
ref.: https://github.com/na--/ebook-tools
"""
# TODO: python3 compatible only, e.g. print('', end='') [use from __future__ import print_function for python 2]
# ref.: https://stackoverflow.com/a/5071123
# import PyPDF2
import ipdb
import os
import re
import shlex
import string
import subprocess
import tempfile


# OCR: converts image to text
def tesseract_wrapper(input_file, output_file):
    # cmd = 'tesseract INPUT_FILE stdout --psm 12 > OUTPUT_FILE || exit 1
    cmd = 'tesseract {} stdout --psm 12'.format(input_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=open(output_file, 'w'), encoding='utf-8', bufsize=4096)
    if result.returncode == 1:
        return 1  # command failed
    else:
        return 0  # command succeeded


# Environment variables with default values
OCR_ENABLED = False
OCR_ONLY_FIRST_LAST_PAGES = (4, 3)
OCR_COMMAND = tesseract_wrapper
# This regular expression should match most ISBN10/13-like sequences in
# texts. To minimize false-positives, matches should be passed through
# is_isbn_valid() or another ISBN validator
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L46
ISBN_REGEX = r"(?<![0-9])(-?9-?7[789]-?)?((-?[0-9]-?){9}[0-9xX])(?![0-9])"
ISBN_RET_SEPARATOR = ','


# Returns non-zero status if the supplied command does not exist
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L289
# TODO: complete its implementation
def command_exists(test_cmd):
    cmd = 'command -v %s >/dev/null 2>&1' % test_cmd
    return cmd


# TODO: complete its implementation
def decho():
    pass


# TODO: place all the bash wrappers in a module in the utilities package
def cat(file):
    cmd = 'cat {}'.format(file)
    args = shlex.split(cmd)
    result = subprocess.run(args)
    return result


# Returns number of pages in pdf document
def get_pages_in_pdf(file):
    # TODO: add also the option to use pdfinfo (like in the original shell script)
    # TODO: see if you can find the number of pages using a python module (e.g. PyPDF2)
    cmd = 'mdls -raw -name kMDItemNumberOfPages %s' % file
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return int(result.stdout)


# Returns number of pages in djvu document
def get_pages_in_djvu(file):
    # TODO: To access the djvu command line utilities and their documentation,
    # you must set the shell variable PATH and MANPATH appropriately. This can
    # be achieved by invoking a convenient shell script hidden inside the application bundle:
    #    $ eval `/Applications/DjView.app/Contents/setpath.sh`
    # ref.: ReadMe from DjVuLibre
    # TODO: not need to specify the full path to djvused if you set correctly the right env. variables
    cmd = '/Applications/DjView.app/Contents/bin/djvused -e "n" %s' % input_file
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return int(result.stdout)


# TODO: place it in path module
def remove_file(file):
    # TODO add reference: https://stackoverflow.com/a/42641792
    try:
        os.remove(file)
        return 0
    except OSError as e:
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
        return 0
    else:
        # TODO: decho
        print('Unsupported mimetype %s!' % mime_type)
        return 4

    # TODO: decho
    print('Running OCR on file %s %s pages and with mimetype %s...'
          % (input_file, num_pages, mime_type))

    # TODO: if ocr_first_pages or ocr_last_pages, set them to 0
    ocr_first_pages = OCR_ONLY_FIRST_LAST_PAGES[0]
    ocr_last_pages = OCR_ONLY_FIRST_LAST_PAGES[1]
    # TODO: pre-compute the list of page to process based on ocr_first_pages and ocr_last_pages
    if OCR_ONLY_FIRST_LAST_PAGES:
        pages_to_process = [i+1 for i in range(0, ocr_first_pages)]
        pages_to_process.extend([i+1 for i in range(num_pages-ocr_last_pages, num_pages)])
    else:
        # OCR_ONLY_FIRST_LAST_PAGES is False
        pages_to_process = [i for i in range(0, num_pages)]

    for page in pages_to_process:
        # Make temporary files
        tmp_file = tempfile.mkstemp()[1]
        # TODO: on mac, --suffix option is not present for the command mktemp
        # mktemp --suffix='.txt'
        tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
        # TODO: decho
        print('Running OCR of page %s, using tmp files %s and %s ...'
              % (page, tmp_file, tmp_file_txt))

        # TODO: do something with the returned values, or better raise errors and log
        # the errors
        # doc(pdf, djvu) --> image(png, tiff)
        page_convert_cmd(page, input_file, tmp_file)
        # image --> text
        OCR_COMMAND(tmp_file, tmp_file_txt)
        # TODO: use python copy instead of cat
        cat(tmp_file_txt)

        # TODO: decho
        # Remove temporary files
        print('Cleaning up tmp files %s and %s' % (tmp_file, tmp_file_txt))
        remove_file(tmp_file)
        remove_file(tmp_file_txt)

    # TODO: run > command, i.e. everything on the stdout must be copied to the output file
    # cmd = '> %s' %output_file
    return 0


# Validates ISBN-10 and ISBN-13 numbers
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L215
def is_isbn_valid(isbn):
    ipdb.set_trace()
    # Remove whitespaces (space, tab, newline, and so on), '-', and capitalize all
    # characters (ISBNs can consist of numbers [0-9] and the letters [xX])
    isbn = ''.join(isbn.split())
    isbn = isbn.replace('-', '')
    isbn = isbn.upper()

    sum = 0
    # Case 1: ISBN-10
    if len(isbn) == 10:
        for i in range(len(isbn)):
            number = isbn[i]
            if i == 9 and number == 'X':
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


# Searches the in_str for ISBN-like sequences and removes duplicates and finally
# validates them using is_isbn_valid() and returns them separated by
# $ISBN_RET_SEPARATOR
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L274
def find_isbns(in_str):
    ipdb.set_trace()
    isbns = []
    matches = re.finditer(ISBN_REGEX, in_str)
    for _, match in enumerate(matches):
        match = match.group()
        # Remove everything except numbers, 'x', 'X'
        # NOTE: equivalent to `tr -c -d '0-9xX'`
        # TODO: they don't remove \n in their code
        # TODO: do the following in a function
        del_tab = string.printable[10:].replace('x', '').replace('X', '')
        tran_tab = str.maketrans('', '', del_tab)
        match = match.translate(tran_tab)
        # Only keep unique ISBNs
        if not match in isbns:
            # Validate ISBN
            if is_isbn_valid(match):
                isbns.append(match)
    return ISBN_RET_SEPARATOR.join(isbns)


# Tries to find ISBN numbers in the given ebook file by using progressively
# more "expensive" tactics.
# These are the steps:
# - Check the supplied file name for ISBNs (the path is ignored)
# - If the MIME type of the file matches ISBN_DIRECT_GREP_FILES, search  the
#   file contents directly for ISBNs
# ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/lib.sh#L499
def search_file_for_isbns(file_path):
    # TODO: decho
    print('Searching file {} for ISBN numbers...'.format(file_path))
    # First step: check the filename for ISBNs
    basename = os.path.basename(file_path)
    isbns = find_isbns(basename)
    if isbns:
        pass
        # TODO: decho
        print('Extracted ISBNs {} from the file name!'.format(isbns))
        print(isbns)
        return

    # Second step: if valid mime type, search file contents for isbns
    pass


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
    # Test1: check the filename for ISBNs
    # test_strs = ['/Users/test/ebooks/9788175257665_93-9483-398-9.pdf',
    #              '/Users/test/ebooks/ISBN9788175257665.djvu']
    # Test2: check for duplicate ISBNs in filename
    test_strs = ['/Users/test/ebooks/9788175257665_9788-1752-57665_9789475237625.pdf',
                 '/Users/test/ebooks/ISBN9788175257665_9788175257665abcdef9788-1752-57665abcdef.pdf']
    ipdb.set_trace()
    for s in test_strs:
        search_file_for_isbns(s)
