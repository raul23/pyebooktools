"""Convert the supplied file to a text file.

It can optionally also use *OCR* for `.pdf`, `.djvu` and image files.

This is a Python port of `convert-to-txt.sh`_ from `ebook-tools`_ written in
Shell by `na--`_.

References
----------
* `ebook-tools`_

.. URLs

.. external links
.. _convert-to-txt.sh: https://github.com/na--/ebook-tools/blob/master/convert-to-txt.sh
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
"""
import os
from pathlib import Path

from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.lib import convert_to_txt, get_mime_type, isalnum_in_file
from py_ebooktools.utils.genutils import init_log, touch

logger = init_log(__name__, __file__)


def convert(input_file, output_file=default_cfg.output_file,
            ocr_enabled=default_cfg.ocr_enabled, **kwargs):
    # TODO: Path(input_file)
    # TODO: check that input_file exists
    output_file = Path(output_file)
    import ipdb
    mime_type = get_mime_type(input_file)
    # Check first that the output text file is valid
    if output_file.suffix != '.txt':
        # TODO: ? raise error and catch exception in ebooktools
        logger.error("The output file needs to have a .txt extension!")
        return 1
    # Create output file text if it doesn't exist
    if output_file.exists():
        logger.info(f"Output text file already exists: {output_file.name}")
        logger.debug("Full path of output text file: "
                     f"{output_file.absolute()}")
    else:
        # Create output text file
        # TODO: as tmp file?
        touch(output_file)
    if ocr_enabled == 'always':
        logger.debug("OCR=always, first try OCR then conversion")
        # TODO: call lib.ocr_file() and then convert_to_txt()
        print("ocr_file()")
        print("convert_to_txt()")
    elif ocr_enabled == 'true':
        logger.debug("OCR=true, first try conversion and then OCR")
        # Check if valid converted text file
        result = convert_to_txt(input_file, output_file, mime_type)
        ipdb.set_trace()
        if result.returncode == 0 and isalnum_in_file(output_file):
            logger.debug("conversion successful, will not try OCR")
        else:
            # TODO: call lib.ocr_file()
            print("ocr_file()")
    else:
        logger.debug("OCR=false, try only conversion")
        result = convert_to_txt(input_file, output_file, mime_type)
        if result.returncode == 0 and isalnum_in_file(output_file):
            logger.debug("conversion successful")
        else:
            logger.warning('The converted txt with size '
                           f'{os.stat(output_file).st_size} bytes does not'
                           'seem to contain text')
    # TODO: ? remove tmp output text file
    return 0
