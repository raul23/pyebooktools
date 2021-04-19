"""Traverses a calibre library folder and renames all the book files in it by
reading their metadata from calibre's metadata.opf files.

This is a Python port of `rename-calibre-library.sh`_ from `ebook-tools`_
written in Shell by `na--`_.

References
----------
* `ebook-tools`_

.. TODO: add description to reference (and other places too)
.. URLs

.. external links
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _na--: https://github.com/na--
.. _rename-calibre-library.sh: https://github.com/na--/ebook-tools/blob/master/rename-calibre-library.sh
"""
from py_ebooktools.configs import default_config as default_cfg
from py_ebooktools.utils.genutils import init_log

logger = init_log(__name__, __file__)


def rename(calibre_folder, output_folder=default_cfg.output_folder,
           dry_run=default_cfg.dry_run, reverse=default_cfg.file_sort_reverse,
           **kwargs):
    logger.info('test')
