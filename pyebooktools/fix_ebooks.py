"""Tries to fix corrupted ebook files.

For the moment, only PDF files are supported.

References
----------
* `Some user tested first three pdf-checking methods 
  <https://superuser.com/a/1546294>`__ (results: ``pdfinfo`` fastest 
  and ``qpdf`` slowest)
* `Some user tested jhove <https://superuser.com/a/1204692>`__
* `Some user provides gs command for linux <https://superuser.com/a/282056>`__
* `Some user provides pdftocairo command <https://superuser.com/a/608862>`__
* `Some user proposes mutool on Ubuntu (can also be installed on macOS with 
  brew) <https://superuser.com/a/923800>`__
* `Some user used cpdf to fix broken files <https://superuser.com/a/1228662>`__
* `Official website for cpdf <https://community.coherentpdf.com/>`__
* `Install qpdf with Homebrew <https://formulae.brew.sh/formula/qpdf>`__
* `Install qpdf with MacPorts <https://ports.macports.org/port/qpdf/summary>`__
"""
from pathlib import Path

from pyebooktools.configs import default_config as default_cfg
from pyebooktools.lib import (color_msg as c, check_input_data,
                              fix_file_for_corruption, get_parts_from_path)
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)


class FixEbooks:
    def __init__(self):
        self.input_data = None
        self.output_folder = default_cfg.output_folder
        self.output_folder_corrupt = default_cfg.output_folder_corrupt
        self.corruption_check_only = default_cfg.corruption_check_only
        self.dry_run = default_cfg.dry_run
        self.reverse = default_cfg.reverse
        self.symlink_only = default_cfg.symlink_only

    def _fix_file(self, file_path):
        file_err = fix_file_for_corruption(file_path, self.output_folder)

    def fix(self, input_data, **kwargs):
        # TODO: add debug message about update attributes
        self.__dict__.update(kwargs)
        input_data = Path(input_data)
        if check_input_data(input_data):
            return 0
        found_pdf = False
        files = []
        # NOTE: only PDF files supported
        # TODO: important, use get_mime_type?
        if input_data.is_file() and input_data.suffix == '.pdf':
            files = [input_data]
        else:
            # TODO: important, use get_mime_type for each file found?
            for fp in input_data.rglob('*.pdf'):
                found_pdf = True
                # logger.debug(get_parts_from_path(fp))
                files.append(fp)
            # TODO: important sort within glob?
            logger.debug("Files sorted {}".format("in desc" if self.reverse else "in asc"))
            files.sort(key=lambda x: x.name, reverse=self.reverse)
        for fp in files:
            self._fix_file(fp)
        if not found_pdf:
            logger.warning(f"{c('No PDF files found:')} {input_data}")
            logger.warning(f"{c('Only PDF files are supported!', bold=True)}")
        return 0


fixer = FixEbooks()
