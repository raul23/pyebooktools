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
from pathlib import Path

import ipdb

from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.utils.genutils import init_log, touch

logger = init_log(__name__, __file__)


def convert(input_file, output_file=default_cfg.output_file, **kwargs):
    # Check first that the output text file is valid
    if Path(output_file).suffix != '.txt':
        # TODO: ? raise error and catch exception in ebooktools
        logger.error('The output file needs to have a .txt extension!')
        return 1
    # Create output file text if it doesn't exist
    ipdb.set_trace()
    if Path(output_file).exists():
        logger.info(f"Output text file already exists: {output_file}")
        logger.debug("Full path of output text file: "
                     f"{Path(output_file).absolute()}")
    else:
        # Create output text file
        touch(output_file)
    ipdb.set_trace()
    return 0
