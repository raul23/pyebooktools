=========================
README [Work-In-Progress]
=========================

.. raw:: html

  <p align="center">
   <br> 🚧 &nbsp;&nbsp;&nbsp;<b>Work-In-Progress</b>
   </p>

This project is a Python port of `ebook-tools`_ which is written in shell by
na--. The Python script `ebooktools`_ is a collection of tools for automated
and semi-automated organization and management of large ebook collections.

`ebooktools`_ makes use of the following tools:

- **edit**: to edit a configuration file which can either be the main config
  file that contains all the options defined below or the logging config file.
- **split**: to split the supplied ebook files (and the accompanying metadata
  files if present) into folders with consecutive names that each contain the
  specified number of files.

`:warning:`

  **More to come!** Check the `Roadmap <#roadmap>`_ to know what is coming.

.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top

Installation
============

Usage, options and configuration
================================
All of the options documented below can either be passed to the `ebooktools`_
script via command-line parameters or via the configuration file ``config.py``.
Command-line parameters supersede variables defined in the configuration file.
Most parameters are not required and if nothing is specified, the default value
defined in the default config file `default_config.py`_ will be used.

General options
---------------
General control flags
^^^^^^^^^^^^^^^^^^^^^
* ``-v``, ``--verbose``; config variable ``verbose``; default value ``False``
* ``-d``, ``--dry-run``; config variable ``dry_run``; default value ``False``
* ``--sl``, ``--symlink-only``; config variable ``symlink_only``; default value
  ``False``

Options related to extracting ISBNs from files and finding metadata by ISBN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``-i <value>``, ``--isbn-regex <value>``; config variable ``isbn_regex``; see
  default value in `lib.py`_

Options for OCR
^^^^^^^^^^^^^^^
* ``--ocr <value>``, ``--ocr-enabled <value>``; config variable ``ocr_enabled``;
  default value ``False``
* ``--ocrop <value>``, ``--ocr-only-first-last-pages <value>``; config variable 
  ``ocr_only_first_last_pages``; default value ``(7,3)`` (except for
  `convert-to-txt.py`_ where it's ``False``)

Options related to extracting and searching for non-ISBN metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Options related to the input and output files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Miscellaneous options
^^^^^^^^^^^^^^^^^^^^^

Script usage and options
------------------------
edit [<OPTIONS>] cfg_type {main,log}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description
"""""""""""
Edit a configuration file, either the main configuration file (``main``) or the 
logging configuration file (``log``). The configuration file can be opened by a 
user-specified application (``app``) or a default program associated with this
type of file (when ``app`` is ``None``).

Options
"""""""
* ``-a <value>``, ``--app <value>``; config variable; config variable ``app``; 
  default value ``None``
* ``-r``, ``--reset``; no config variable; default value ``None``; default value 
  ``False``

split [<OPTIONS>] folder_with_books
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description
"""""""""""
Split the supplied ebook files (and the accompanying metadata files if present)
into folders with consecutive names that each contain the specified number of
files.

Options
"""""""
* ``-o <value>``, ``--output-folder <value>``; config variable ``output_folder``; 
  the default value is the current working directory (check with pwd)
  
  The output folder in which all the new consecutively named folders will be created.
  
* ``-s <value>``, ``--start-number <value>``; config variable ``start_number``; 
  default value ``0``
  
  The number of the first folder. 
  
* ``-f <value>``, ``--folder-pattern <value>``; config variable
  ``folder_pattern``; default value ``%05d000``
  
  The print format string that specifies the pattern with which new folders will be 
  created. By default it creates folders like 00000000, 00001000, 00002000, ..... 
  
* ``--fpf <value>``, ``--files-per-folder <value>``; env. variable 
  ``files_per_folder``; default value ``1000``

  How many files should be moved to each folder.

Roadmap
=======
- Port all of `ebook-tools`_ scripts into Python

  - ``organize-ebooks.sh``
  - ``interactive-organizer.sh``
  - ``find-isbns.sh``: **working on it**
  - ``convert-to-txt.sh``: **working on it**
  - ``rename-calibre-library.sh``
  - ``split-into-folders.sh``: **done**, see `split_into_folders.py`_
- Add tests
- Eventually add documentation on `readthedocs <https://readthedocs.org/>`__

License
=======
This program is licensed under the GNU General Public License v3.0. For more
details see the `LICENSE`_ file in the repository.

.. URLs
.. _convert-to-txt.py: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/convert_to_txt.py
.. _convert-to-txt.sh: https://github.com/na--/ebook-tools/blob/master/convert-to-txt.sh
.. _default_config.py: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/configs/default_config.py
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _ebooktools: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/scripts/ebooktools
.. _find-isbns.sh: https://github.com/na--/ebook-tools/blob/master/find-isbns.sh
.. _interactive-organizer.sh: https://github.com/na--/ebook-tools/blob/master/interactive-organizer.sh
.. _lib.py: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/lib.py
.. _LICENSE: https://github.com/raul23/python-ebook-tools/blob/master/LICENSE
.. _organize-ebooks.sh: https://github.com/na--/ebook-tools/blob/master/organize-ebooks.sh
.. _rename-calibre-library.sh: https://github.com/na--/ebook-tools/blob/master/rename-calibre-library.sh
.. _split-into-folders.sh: https://github.com/na--/ebook-tools/blob/master/split-into-folders.sh
.. _split_into_folders.py: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/split_into_folders.py
