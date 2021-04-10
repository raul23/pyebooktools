=========================
README [Work-In-Progress]
=========================

.. raw:: html

  <p align="center">
    <img src="https://raw.githubusercontent.com/raul23/py-ebooktools/master/docs/logo/py_ebooktools.png">
    <br> 🚧 &nbsp;&nbsp;&nbsp;<b>Work-In-Progress</b>
  </p>

This project (**version 0.3**) is a Python port of `ebook-tools`_ which is written in Shell by
`na--`_. The Python script `ebooktools.py`_ is a collection of tools for automated
and semi-automated organization and management of large ebook collections.

`ebooktools.py`_ makes use of the following tools:

- **edit**: to edit a configuration file which can either be the main config
  file that contains all the options defined below or the logging config file.
- **split**: to split the supplied ebook files (and the accompanying metadata
  files if present) into folders with consecutive names that each contain the
  specified number of files.

`:warning:`

  **More to come!** Check the `Roadmap <#roadmap>`_ to know what is coming soon.

.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top

Installation
============
1. It is highly recommended to install the package ``py_ebooktools`` in a virtual
   environment using for example `venv`_ or `conda`_.

2. Make sure to update *pip*::

   $ pip install --upgrade pip

3. Install the package ``py_ebooktools`` (**bleeding-edge version**) with *pip*::

   $ pip install git+https://github.com/raul23/py-ebooktools#egg=py-ebooktools

`:warning:`

   Make sure that *pip* is working with the correct Python version. It might be
   the case that *pip* is using Python 2.x You can find what Python version
   *pip* uses with the following::

      $ pip -V

   If *pip* is working with the wrong Python version, then try to use *pip3*
   which works with Python 3.x
   
**Test installation**

1. Test your installation by importing ``py_ebooktools`` and printing its version::

   $ python -c "import py_ebooktools; print(py_ebooktools.__version__)"

2. You can also test that you have access to the ``ebooktools.py`` script by showing
   the program's version::

   $ ebooktools --version

Usage, options and configuration
================================
All of the options documented below can either be passed to the `ebooktools.py`_
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
* ``-r``, ``--reverse``; config variable ``file_sort_reverse``; default value
  ``False``

  If this is enabled, the files will be sorted in reverse (i.e. descending) order. 
  By default, they are sorted in ascending order.

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
* ``-a <value>``, ``--app <value>``; config variable ``app``; 
  default value ``None``
* ``-r``, ``--reset``; no config variable; default value ``False``

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
  **default value is the current working directory** (check with ``pwd``)
  
  The output folder in which all the new consecutively named folders will be
  created.
  
* ``-s <value>``, ``--start-number <value>``; config variable ``start_number``;
  default value ``0``

  The number of the first folder. 

* ``-f <value>``, ``--folder-pattern <value>``; config variable
  ``folder_pattern``; default value ``%05d000``
  
  The print format string that specifies the pattern with which new folders
  will be created. By default it creates folders like
  ``00000000, 00001000, 00002000, ...``.
  
* ``--fpf <value>``, ``--files-per-folder <value>``; env. variable 
  ``files_per_folder``; default value ``1000``

  How many files should be moved to each folder.

Uninstall
=========
To uninstall the package ``py_ebooktools``::

   $ pip uninstall py_ebooktools
   
`:information_source:`

   When uninstalling the ``py_ebooktools`` package, you might be informed
   that the configuration files *logging.py* and *config.py* won't be
   removed by *pip*. You can remove those files manually by noting their paths
   returned by *pip*. Or you can leave them so your saved settings can be
   re-used the next time you re-install the package.

   **Example:** uninstall the package and remove the config files

   .. code-block:: console

      $ pip uninstall py_ebooktools
      Found existing installation: py-ebooktools 0.1.0
      Uninstalling py-ebooktools-0.1.0:
        Would remove:
          /Users/test/miniconda3/envs/ebooktools_py37/bin/ebooktools
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/py_ebooktools-0.1.0.dist-info/*
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/py_ebooktools/*
        Would not remove (might be manually added):
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/py_ebooktools/configs/config.py
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/py_ebooktools/configs/logging.py
      Proceed (y/n)? y
        Successfully uninstalled py-ebooktools-0.1.0
      $ rm -r /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/py_ebooktools/

Roadmap
=======
- Port all of `ebook-tools`_ shell scripts into Python

  - ``organize-ebooks.sh``: **not started yet**
  - ``interactive-organizer.sh``: **not started yet**
  - ``find-isbns.sh``: **working on it**
  - ``convert-to-txt.sh``: **done**, *see* `convert_to_txt.py`_
  - ``rename-calibre-library.sh``: **not started yet**
  - ``split-into-folders.sh``: **done**, *see* `split_into_folders.py`_
- Add tests
- Eventually add documentation on `readthedocs <https://readthedocs.org/>`__

References
==========
* `ebook-tools`_: Shell scripts for organizing and managing ebook collections.

License
=======
This program is licensed under the GNU General Public License v3.0. For more
details see the `LICENSE`_ file in the repository.

.. URLs
.. _conda: https://docs.conda.io/en/latest/
.. _convert_to_txt.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/convert_to_txt.py
.. _default_config.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/configs/default_config.py
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _ebooktools.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/scripts/ebooktools.py
.. _lib.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/lib.py
.. _LICENSE: https://github.com/raul23/py-ebooktools/blob/master/LICENSE
.. _na--: https://github.com/na--
.. _split_into_folders.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/split_into_folders.py
.. _venv: https://docs.python.org/3/library/venv.html#module-venv
