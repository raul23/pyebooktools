"""
Port ebooks-managing shell scripts to Python
ref.: https://github.com/na--/ebook-tools
"""
# import PyPDF2
import ipdb
import os
import shlex
import subprocess
import tempfile


def tesseract_wrapper(input_file, output_file):
    # cmd = 'tesseract INPUT_FILE stdout --psm 12 > OUTPUT_FILE || exit 1
    cmd = 'tesseract %s stdout --psm 12'
    args = shlex.split(cmd)
    subprocess.run(args, stdout=open(output_file, 'w'), encoding='utf-8', bufsize=4096)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    if result.returncode == 1:
        return 1  # command failed
    else:
        return 0  # command succeeded


# Environment variables with default values
OCR_ENABLED = False
OCR_ONLY_FIRST_LAST_PAGES = (7, 3)
OCR_COMMAND = tesseract_wrapper


# Returns non-zero status if the supplied command does not exist
def command_exists(test_cmd):
    cmd = 'command -v %s >/dev/null 2>&1' % test_cmd
    return cmd


def decho():
    pass


def cat(file):
    cmd = 'cat {}'.format(file)
    args = shlex.split(cmd)
    result = subprocess.run(args)
    return result


def get_pages_in_pdf(file):
    # TODO: add also the option to use pdfinfo (like in the original shell script)
    # TODO: see if you can find the number of pages using a python module (e.g. PyPDF2)
    cmd = 'mdls -raw -name kMDItemNumberOfPages %s' % file
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE)
    return int(result.stdout)


def get_pages_in_djvu(input_file):
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


def ocr_file(input_file, output_file, mime_type):
    def convert_pdf_page(page, input_file, output_file):
        cmd = 'gs -dSAFER -q -r300 -dFirstPage=%s -dLastPage=%s dNOPAUSE ' \
              '-dINTERPOLATE -sDEVICE=png16m -sOutputFile=%s %s -c quit' % (page, page, output_file, input_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE)
        return result.returncode

        return args

    def convert_djvu_page(page, input_file, output_file):
        cmd = 'ddjvu -page=%s -format=tif %s %s' % (page, input_file, output_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE)
        return result.returncode

    ipdb.set_trace()

    page_convert_cmd = ''
    num_pages = 1
    if mime_type in 'application/pdf':
        # TODO: they are using the pdfinfo command but it might not be present; in check_file_for_corruption(), they
        # are testing if this command exists but not in ocr_file()
        num_pages = get_pages_in_pdf(input_file)
        page_convert_cmd = convert_pdf_page
    elif mime_type in 'image/vnd.djvu':
        num_pages = get_pages_in_djvu(input_file)
        page_convert_cmd = convert_djvu_page
    elif mime_type in 'image/':
        # TODO: in their code, they don't initialize num_pages
        print('Running OCR on file %s %s pages and with mimetype %s...' % (input_file, num_pages, mime_type))
        OCR_COMMAND(input_file, output_file)
        # TODO: run > command
        cmd = '> %s' % output_file
    else:
        # TODO: decho
        print('Unsupported mimetype %s!' % mime_type)
        return 4

    # TODO: decho
    print('Running OCR on file %s %s pages and with mimetype %s...' % (input_file, num_pages, mime_type))

    # TODO: if ocr_first_pages or ocr_last_pages, set them to 0
    ocr_first_pages = OCR_ONLY_FIRST_LAST_PAGES[0]
    ocr_last_pages = OCR_ONLY_FIRST_LAST_PAGES[1]
    page = 1
    # TODO: pre-compute the list of page to process based on ocr_first_pages and ocr_last_pages
    while page <= num_pages:
        if not OCR_ONLY_FIRST_LAST_PAGES or page <= ocr_first_pages or page > num_pages - ocr_last_pages:
            # Make temporary files
            # TODO: make tmp_file and tmp_file_txt
            tmp_file = tempfile.mkstemp()[1]
            # TODO: on mac, --suffix option is not present for the command mktemp
            # mktemp --suffix='.txt'
            tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
            # TODO: decho
            print('Running OCR of page %s, using tmp files %s and %s ...' % (page, tmp_file, tmp_file_txt))

            # TODO: do something with the returned values, or better raise errors instead and log
            # the errors
            page_convert_cmd(input_file, tmp_file, page)
            OCR_COMMAND(tmp_file, tmp_file_txt)
            cat(tmp_file_txt)

            # TODO: decho
            print('Cleaning up tmp files %s and %s' % (tmp_file, tmp_file_txt))
            remove_file(tmp_file)
            remove_file(tmp_file_txt)
        page += 1

        # TODO: run > command
        # TODO: is it necessary
        # cmd = '> %s' %output_file


if __name__ == '__main__':
    # OCR
    ocr_file('input', 'output', 'application/pdf')
