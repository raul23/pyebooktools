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
from pyebooktools.lib import (GREEN, NC, color_msg as c, check_input_data,
                              fail_file, fix_file_for_corruption,
                              get_parts_from_path as g, move_or_link_file,
                              remove_file, unique_filename)
from pyebooktools.utils.logutils import init_log

logger = init_log(__name__, __file__)


def fixed_file(old_path, new_path):
    old_path = g(old_path)
    new_path = g(new_path)
    logger.info(f'{GREEN}FIXED{NC}:\t{old_path}\nIN:\t{new_path}\n')


class FixEbooks:
    def __init__(self):
        self.input_data = None
        self.output_folder = default_cfg.output_folder
        self.output_folder_corrupt = default_cfg.output_folder_corrupt
        self.corruption_check_only = default_cfg.corruption_check_only
        self.dry_run = default_cfg.dry_run
        self.reverse = default_cfg.reverse
        self.symlink_only = default_cfg.symlink_only
        self.output_metadata_extension = default_cfg.output_metadata_extension

    def _fix_file(self, file_path):
        file_err, output_tmp_file = fix_file_for_corruption(file_path)
        if file_err:
            logger.debug(f"File couldn't be fixed: {g(file_path)}"
                         f"\n{file_err}")
            if self.output_folder_corrupt:
                new_path = unique_filename(
                    Path(self.output_folder_corrupt).joinpath('not_fixed'),
                    file_path.name)
                move_or_link_file(file_path, new_path, self.dry_run,
                                  self.symlink_only)
                # TODO: do we add the meta extension directly to new_path?
                new_metadata_path = f'{new_path}.{self.output_metadata_extension}'
                logger.debug(f'Saving original filename to {new_metadata_path}...')
                if not self.dry_run:
                    file_err_tabs = file_err.replace('\n\t', '\n\t\t')
                    metadata = f'Error message:\t{file_err_tabs}\n' \
                               f'Old file path:\t{file_path}'
                    with open(new_metadata_path, 'w') as f:
                        f.write(metadata)
                fail_file(file_path, f"{file_err}", new_path)
            else:
                msg = c('Output folder for corrupt files is not set, doing nothing')
                logger.warning(f"{msg}")
        else:
            logger.debug('File was successfully fixed')
            new_path_fixed = unique_filename(self.output_folder, file_path.name)
            move_or_link_file(output_tmp_file, new_path_fixed, dry_run=False,
                              symlink_only=False)
            fixed_file(file_path, new_path_fixed)
            new_path_corrupted = unique_filename(
                Path(self.output_folder_corrupt).joinpath('fixed'),
                file_path.name)
            move_or_link_file(file_path, new_path_corrupted, self.dry_run,
                              self.symlink_only)
            # TODO: do we add the meta extension directly to new_path?
            # TODO: important, add next in a func in lib (other places)
            new_metadata_path = f'{new_path_corrupted}.{self.output_metadata_extension}'
            logger.debug(f'Saving original filename to {new_metadata_path}...')
            if not self.dry_run:
                metadata = f'Fixed file path:\t{new_path_fixed}\n' \
                           f'Old file path:\t{file_path}'
                with open(new_metadata_path, 'w') as f:
                    f.write(metadata)
        if output_tmp_file and Path(output_tmp_file).exists():
            logger.debug(f'Removing temp file {output_tmp_file}...')
            remove_file(output_tmp_file)
        logger.debug('=====================================================')
        return 0

    def _get_files(self):
        # NOTE: only pdf files supported
        # TODO: important, use get_mime_type?
        if self.input_data.is_file() and self.input_data.suffix == '.pdf':
            files = [self.input_data]
        else:
            # TODO: important, use get_mime_type for each file found?
            # you can have a pdf file with the wrong ext?
            files = [fp for fp in self.input_data.rglob('*.pdf')]
            # TODO: important sort within glob?
            logger.debug("Files sorted {}".format("in desc" if self.reverse else "in asc"))
            files.sort(key=lambda x: x.name, reverse=self.reverse)
        return files

    def fix(self, input_data, **kwargs):
        input_data = Path(input_data)
        # TODO: add debug message about update attributes
        self.__dict__.update(kwargs)
        self.input_data = input_data
        if check_input_data(input_data):
            # TODO: 0 or 1?
            return 0
        files = self._get_files()
        logger.debug('=====================================================')
        _ = list(map(lambda fp: self._fix_file(fp), files))
        if not files:
            if input_data.is_file():
                logger.warning(f"{c('Not a pdf file:')} {input_data}")
            else:
                logger.warning(f"{c('No pdf files found:')} {input_data}")
            logger.warning(f"{c('Only pdf files are supported!', bold=True)}")
        return 0


fixer = FixEbooks()
