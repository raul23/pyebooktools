"""Convert the supplied file to a text file.

It can optionally also use *OCR* for `.pdf`, `.djvu` and image files.

This is a Python port of `convert-to-txt.sh`_ from `ebook-tools`_ written in
Shell by `na--`_.

References
----------
* `ebook-tools`_

.. external links
.. _convert-to-txt.sh: https://github.com/na--/ebook-tools/blob/master/convert-to-txt.sh
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
"""
import os
import tempfile
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import (convert_to_txt, get_hash, get_mime_type,
                              isalnum_in_file, ocr_file, remove_file)
from pyebooktools.utils.genutils import touch
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)

# =====================
# Default config values
# =====================
# We want the whole book to be converted
OCR_ONLY_FIRST_LAST_PAGES = False


def convert(input_file, output_file=None, cache=None,
            cache_folder=default_cfg.cache_folder,
            cache_size_limit=default_cfg.cache_size_limit,
            djvu_convert_method=default_cfg.djvu_convert_method,
            epub_convert_method=default_cfg.epub_convert_method,
            eviction_policy=default_cfg.eviction_policy,
            msword_convert_method=default_cfg.msword_convert_method,
            ocr_command=default_cfg.ocr_command,
            ocr_enabled=default_cfg.ocr_enabled,
            pdf_convert_method=default_cfg.pdf_convert_method,
            use_cache=default_cfg.use_cache, **kwargs):
    # TODO: urgent, remove use_calibre and use search_method
    # also setup cache outside
    func_params = locals().copy()
    statuscode = 0
    check_conversion = True
    file_hash = None
    mime_type = get_mime_type(input_file)
    if mime_type == 'text/plain':
        logger.debug('The file is already in .txt')
        with open(input_file, 'r') as f:
            text = f.read()
        return text
    if use_cache and cache is not None:
        file_hash = get_hash(input_file)
        cache_result = cache.get(file_hash)
        if cache_result is None:
            logger.debug('Text conversion was not found in cache. Converting'
                         'the file to text...')
        elif cache_result and cache_result['text'] is not None:
            logger.debug('Text conversion was found in cache!')
            return cache_result['text']
        else:
            if ocr_enabled == cache_result['ocr_enabled'] \
                    and ocr_enabled == 'false':
                logger.warning('Text conversion found in cache is '
                               'defective (last conversion failed without OCR) '
                               'and you are trying to convert the same file '
                               'without OCR which will result in the same '
                               'failed conversion. Skipping this file...')
                return 1
            elif ocr_enabled in ['always', 'true'] \
                    and cache_result['ocr_enabled'] in ['always', 'true']:
                logger.warning('Text conversion found in cache is defective '
                               '(last conversion failed with OCR) and you are '
                               'trying to convert the same file AGAIN with OCR '
                               'which will result in the same failed '
                               'conversion. Skipping this file...')
                return 1
            elif cache_result['ocr_enabled'] == 'false':
                assert ocr_enabled != 'false'
                logger.debug('Text conversion found in cache is defective '
                             '(last conversion failed without OCR) but the same '
                             'file is now being converted with OCR...')
            else:
                assert ocr_enabled == 'false'
                logger.warning('Text conversion found in cache is defective '
                               '(last conversion failed with OCR) but the same '
                               'file is now being converted without OCR...')
    else:
        logger.debug("Cache won't be used")
    # TODO: Path(input_file)
    # TODO: check that input_file exists
    return_txt = False
    if output_file is None:
        return_txt = True
        output_file = tempfile.mkstemp(suffix='.txt')[1]
    else:
        output_file = Path(output_file)
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
            touch(output_file)
    func_params['mime_type'] = mime_type
    func_params['output_file'] = output_file
    # check_conversion = False
    if ocr_enabled == 'always':
        logger.info("OCR=always, first try OCR then conversion")
        # TODO: important, use **vars()?
        if ocr_file(input_file, output_file, mime_type, ocr_command,
                    OCR_ONLY_FIRST_LAST_PAGES):
            logger.warning("OCR failed! Will try conversion...")
            result = convert_to_txt(**func_params)
            statuscode = result.returncode
        else:
            logger.info("OCR successful!")
            statuscode = 0
    elif ocr_enabled == 'true':
        logger.info("OCR=true, first try conversion and then OCR...")
        # Check if valid converted text file
        result = convert_to_txt(**func_params)
        statuscode = result.returncode
        if statuscode == 0 and isalnum_in_file(output_file):
            logger.info("Conversion successful, will not try OCR")
            check_conversion = False
        else:
            logger.warning("Conversion failed! Will try OCR...")
            # TODO: important, use **vars()?
            if ocr_file(input_file, output_file, mime_type, ocr_command,
                        OCR_ONLY_FIRST_LAST_PAGES):
                logger.warning("OCR failed!")
                logger.warning(f"File couldn't be converted to txt: {input_file}")
                remove_file(output_file)
                # TODO: important, make an API for cache (other places), i.e. factorize
                if use_cache:
                    cache_result = cache.get(file_hash)
                    data = {'file_path': input_file,
                            'text': None,
                            'ocr_enabled': ocr_enabled}
                    if cache_result:
                        cache_result.update(data)
                    else:
                        cache.set(file_hash, data)
                return 1
            else:
                logger.info("OCR successful!")
                statuscode = 0
    else:
        # ocr_enabled = 'false'
        logger.info("OCR=false, try only conversion...")
        result = convert_to_txt(**func_params)
        statuscode = result.returncode
        if statuscode == 0:
            logger.info('Conversion successful!')
    # Check conversion
    logger.debug('Checking converted text...')
    if check_conversion:
        if statuscode == 0 and isalnum_in_file(output_file):
            logger.debug("Converted text is valid!")
        else:
            logger.warning("Conversion failed!")
            if not isalnum_in_file(output_file):
                logger.info('The converted txt with size '
                            f'{os.stat(output_file).st_size} bytes does not '
                            'seem to contain text')
            remove_file(output_file)
            if use_cache:
                cache_result = cache.get(file_hash)
                data = {'file_path': input_file,
                        'text': None,
                        'ocr_enabled': ocr_enabled}
                if cache_result:
                    cache_result.update(data)
                else:
                    cache.set(file_hash, data)
            return 1
    assert statuscode == 0
    if return_txt:
        with open(output_file, 'r') as f:
            text = f.read()
        assert text
        if use_cache:
            assert file_hash
            cache_result = cache.get(file_hash)
            data = {'file_path': input_file,
                    'text': text,
                    'ocr_enabled': ocr_enabled}
            if cache_result:
                cache_result.update(data)
                cache.set(file_hash, cache_result)
            else:
                cache.set(file_hash, data)
        remove_file(output_file)
        return text
    else:
        return 0
