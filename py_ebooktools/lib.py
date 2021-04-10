"""Library that has useful functions for building other ebook management tools.

This is a Python port of `lib.sh`_ from `ebook-tools`_ written in Shell by
`na--`_.

.. URLs

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _lib.sh: https://github.com/na--/ebook-tools/blob/master/lib.sh
.. _na--: https://github.com/na--
"""
import ast
import mimetypes
import os
import shlex
import shutil
import subprocess
import tempfile

from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.utils.genutils import init_log

logger = init_log(__name__, __file__)


# For macOS use the built-in textutil,
# see https://stackoverflow.com/a/44003923/14664104
def catdoc(input_file, output_file):
    raise NotImplementedError('catdoc is not implemented')


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
            return 'stdout={}, stderr={}, returncode={}, args={}'.format(
                self.stdout, self.stderr, self.returncode, self.args)

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
        logger.info('The file looks like a pdf, using pdftotext to extract '
                    'the text')
        result = pdftotext(input_file, output_file)
    elif mime_type == 'application/msword' and command_exists('catdoc'):
        logger.info('The file looks like a doc, using catdoc to extract the text')
        result = catdoc(input_file, output_file)
    # TODO: not need to specify the full path to djvutxt if you set correctly
    # the right env. variables
    elif mime_type.startswith('image/vnd.djvu') and \
            command_exists('/Applications/DjView.app/Contents/bin/djvutxt'):
        logger.info('The file looks like a djvu, using djvutxt to extract the '
                    'text')
        result = djvutxt(input_file, output_file)
    elif (not mime_type.startswith('image/vnd.djvu')) \
            and mime_type.startswith('image/'):
        logger.info('The file looks like a normal image ({}), skipping '
                    'ebook-convert usage!'.format(mime_type))
    else:
        logger.info("Trying to use calibre's ebook-convert to convert the {} "
                    "file to .txt".format(mime_type))
        result = ebook_convert(input_file, output_file)
    return result


def djvutxt(input_file, output_file):
    # TODO: explain that you need to softlink djvutxt in /user/local/bin (or
    # add in $PATH?)
    cmd = '/Applications/DjView.app/Contents/bin/djvutxt "{}" "{}"'.format(
        input_file, output_file)
    # TODO: use genutils.run_cmd() [fix problem with 3.<6] and in other places?
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


def ebook_convert(input_file, output_file):
    # TODO: explain that you need to softlink convert in /user/local/bin (or
    # add in $PATH?)
    cmd = 'ebook-convert "{}" "{}"'.format(input_file, output_file)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Using Python built-in module mimetypes
def get_mime_type(file_path):
    return mimetypes.guess_type(file_path)[0]


# Run shell command
def get_mime_type_version2(file_path):
    # TODO: get MIME type with a python package, see the magic package
    # but dependency, ref.: https://stackoverflow.com/a/2753385
    cmd = 'file --brief --mime-type "{}"'.format(file_path)
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
    cmd = '/Applications/DjView.app/Contents/bin/djvused -e "n" "{}"'.format(
        file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


# Return number of pages in pdf document
def get_pages_in_pdf(file_path):
    # TODO: IMPORTANT add also the option to use `pdfinfo` (like in the
    # original shell script) since mdls is for macOS
    # TODO: see if you can find the number of pages using a python module
    # (e.g. PyPDF2) but dependency
    cmd = 'mdls -raw -name kMDItemNumberOfPages "{}"'.format(file_path)
    args = shlex.split(cmd)
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return convert_result_from_shell_cmd(result)


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


# OCR on a pdf, djvu document or image
# NOTE: If pdf or djvu document, then first needs to be converted to image and
# then OCR
def ocr_file(input_file, output_file, mime_type,
             ocr_command=default_cfg.ocr_command,
             ocr_only_first_last_pages=default_cfg.ocr_only_first_last_pages):
    def convert_pdf_page(page, input_file, output_file):
        # Convert pdf to png image
        cmd = 'gs -dSAFER -q -r300 -dFirstPage={} -dLastPage={} -dNOPAUSE ' \
              '-dINTERPOLATE -sDEVICE=png16m -sOutputFile="{}" "{}" -c quit'.format(
            page, page, output_file, input_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return convert_result_from_shell_cmd(result)

    # Convert djvu to tif image
    def convert_djvu_page(page, input_file, output_file):
        # TODO: not need to specify the full path to djvused if you set
        # correctly the right env. variables
        cmd = '/Applications/DjView.app/Contents/bin/ddjvu -page={} ' \
              '-format=tif {} {}'.format(page, input_file, output_file)
        args = shlex.split(cmd)
        result = subprocess.run(args, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        return convert_result_from_shell_cmd(result)

    # TODO: remove
    import ipdb
    if mime_type.startswith('application/pdf'):
        # TODO: they are using the `pdfinfo` command but it might not be present;
        # in check_file_for_corruption(), they are testing if this command exists
        # but not in ocr_file()
        result = get_pages_in_pdf(input_file)
        num_pages = result.stdout
        logger.debug('Result of {} on {}:\n{}'.format(
            get_pages_in_pdf.__repr__(), input_file, result))
        page_convert_cmd = convert_pdf_page
    elif mime_type.startswith('image/vnd.djvu'):
        result = get_pages_in_djvu(input_file)
        num_pages = result.stdout
        logger.debug('Result of {} on {}:\n{}'.format(
            get_pages_in_djvu.__repr__(), input_file, result))
        page_convert_cmd = convert_djvu_page
    elif mime_type.startswith('image/'):
        # TODO: in their code, they don't initialize num_pages
        logger.info('Running OCR on file %s and with mime type %s...'
                    % (input_file, mime_type))
        # TODO: find out if you can call the ocr_command function without `eval`
        if ocr_command in globals():
            result = eval('{}("{}", "{}")'.format(
                ocr_command, input_file, output_file))
            logger.debug('Result of {}:\n{}'.format(
                ocr_command.__repr__(), result))
        else:
            logger.debug("Function {} doesn't exit. Ending ocr.".format(
                ocr_command))
            return 1
        # TODO: they don't return anything
        return 0
    else:
        logger.info('Unsupported mime type %s!' % mime_type)
        return 2

    if ocr_command not in globals():
        logger.debug("Function {} doesn't exit. Ending ocr.".format(ocr_command))
        return 1

    logger.info(f"Will run OCR on file '{input_file}' with {num_pages} "
                f"page{'s' if num_pages > 1 else ''}")
    logger.debug(f'mime type: {mime_type}')

    # TODO: ? assert on ocr_only_first_last_pages (should be tuple or False)
    # Pre-compute the list of pages to process based on ocr_first_pages and
    # ocr_last_pages
    # ipdb.set_trace()
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
    logger.debug('Pages to process: {}'.format(pages_to_process))

    text = ''
    for page in pages_to_process:
        # Make temporary files
        tmp_file = tempfile.mkstemp()[1]
        tmp_file_txt = tempfile.mkstemp(suffix='.txt')[1]
        logger.info(f'Running OCR of page {page} ...')
        logger.debug(f'Using tmp files {tmp_file} and {tmp_file_txt}')
        # doc(pdf, djvu) --> image(png, tiff)
        result = page_convert_cmd(page, input_file, tmp_file)
        logger.debug('Result of {}:\n{}'.format(
            page_convert_cmd.__repr__(), result))
        # image --> text
        logger.debug(f"Running the '{ocr_command}' ...")
        result = eval('{}("{}", "{}")'.format(
            ocr_command, tmp_file, tmp_file_txt))
        logger.debug('Result of {}:\n{}'.format(ocr_command.__repr__(), result))
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


def pdftotext(input_file, output_file):
    cmd = 'pdftotext "{}" "{}"'.format(input_file, output_file)
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


# OCR: convert image to text
def tesseract_wrapper(input_file, output_file):
    # cmd = 'tesseract INPUT_FILE stdout --psm 12 > OUTPUT_FILE || exit 1
    cmd = 'tesseract "{}" stdout --psm 12'.format(input_file)
    args = shlex.split(cmd)
    result = subprocess.run(args,
                            stdout=open(output_file, 'w'),
                            stderr=subprocess.PIPE,
                            encoding='utf-8',
                            bufsize=4096)
    return convert_result_from_shell_cmd(result)
