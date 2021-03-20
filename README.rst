=========================
README [Work-In-Progress]
=========================
This project is a Python port of `ebook-tools`_ which is written in shell by na--.
The Python script `ebooktools`_ is a collection of tools for automated and 
semi-automated organization and management of large ebook collections.

`ebooktools`_ makes use of the following tools:

- **edit**: to edit a configuration file which can either be the main config
  file that contains all the options defined below or the logging config file.
- **split**: to split the supplied ebook files (and the accompanying metadata 
  files if present) into folders with consecutive names that each contain the specified
  number of files.

.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top

Installation
============

Usage, options and configuration
================================
All of the options documented below can either be passed to the `ebooktools`_ script via 
command-line parameters or via the configuration file ``config.py``. Command-line parameters 
supersede variables defined in the configuration file. Most parameters are not required and 
if nothing is specified, the default value defined in the default config file 
`default_config.py`_ will be used.

General options
---------------
General control flags
^^^^^^^^^^^^^^^^^^^^^
* ``-v``, ``--verbose``; config variable ``verbose``; default value ``False``
* ``-d``, ``--dry-run``; config variable ``dry_run``; default value ``False``
* ``--sl``, ``--symlink-only``; config variable ``symlink_only``; default value ``False``

Options related to extracting ISBNs from files and finding metadata by ISBN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``-i=<value>``, ``--isbn-regex=<value>``; config variable ``isbn_regex``; see default value in `lib.py`_

Options for OCR
^^^^^^^^^^^^^^^
* ``--ocr=<value>``, ``--ocr-enabled=<value>``; config variable ``ocr_enabled``; default value ``False``
* ``--ocrop=<value>``, ``--ocr-only-first-last-pages=<value>``; config variable 
  ``ocr_only_first_last_pages``; default value ``(7,3)`` (except for `convert-to-txt.py`_ where it's ``False``)

Options related to extracting and searching for non-ISBN metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Options related to the input and output files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Miscellaneous options
^^^^^^^^^^^^^^^^^^^^^

Script usage and options
------------------------
edit [<OPTIONS>] cfg_type [...]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
organize [<OPTIONS>] folder_to_organize [...]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Description
"""""""""""
Specific options for organizing files
"""""""""""""""""""""""""""""""""""""
Output options
""""""""""""""
split [<OPTIONS>] folder_with_books [...]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Roadmap
=======

License
=======
This program is licensed under the GNU General Public License v3.0. For more details see the 
`LICENSE`_ file in the repository.

.. URLs
.. _convert-to-txt.py: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/convert_to_txt.py
.. _default_config.py: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/configs/default_config.py
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _ebooktools: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/scripts/ebooktools
.. _lib.py: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/lib.py
.. _LICENSE: https://github.com/raul23/python-ebook-tools/blob/master/LICENSE
