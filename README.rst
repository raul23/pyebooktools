.. raw:: html

  <p align="center">
    <img src="https://raw.githubusercontent.com/raul23/pyebooktools/master/docs/logo/pyebooktools.png">
    <br> 🚧 &nbsp;&nbsp;&nbsp;<b>Work-In-Progress</b>
  </p>

This project (**version 0.1.0a3**) is a Python port of `ebook-tools`_ which is
written in Shell by `na--`_. The Python script `ebooktools.py`_ is a collection
of tools for automated organization and management of large ebook collections.

Check also my other project `search-ebooks`_ which is based on `pyebooktools`_
for searching through the content and metadata of ebooks.

`:warning:`

  Check `organize-ebooks <https://github.com/raul23/organize-ebooks>`_ which is the Python port of `organize-ebooks.sh 
  <https://github.com/na--/ebook-tools/blob/master/organize-ebooks.sh>`_ and includes a `Docker image 
  <https://hub.docker.com/repository/docker/raul23/organize/general>`_ for easy installation of all needed dependencies and Python package.
   
About
=====
The `ebooktools.py`_ script is a Python port of the `shell scripts`_ from
`ebook-tools`_ and makes use of the following modules:

- ``edit_config.py`` edits a configuration file which can either be the main
  config file that contains all the options defined
  `below <#usage-options-and-configuration>`__ or the logging config file whose
  default values is defined in `default_logging.py`_. The `edit`_ subcommand
  from the ``ebooktools.py`` script uses this module.
- ``convert_to_txt.py`` converts the supplied file to a text file. It can
  optionally also use *OCR* for ``.pdf``, ``.djvu`` and image files. The
  `convert`_ subcommand from the ``ebooktools.py`` script uses this module.
- ``find_isbns.py`` tries to find `valid ISBNs`_ inside a file or in a
  ``string`` if no file was specified. Searching for ISBNs in files uses
  progressively more resource-intensive methods until some ISBNs are found, for
  more details see
  
  - the `documentation for ebook-tools`_ (shell scripts) or
  - `search_file_for_isbns()`_ from ``lib.py`` (Python function where ISBNs
    search in files is implemented).
  
  The `find`_ subcommand from the ``ebooktools.py`` script uses this module.
- ``organize_ebooks.py`` is used to automatically organize folders with
  potentially huge amounts of unorganized ebooks. This is done by renaming
  the files with proper names and moving them to other folders:
  
    * By default it `searches`_ the supplied ebook files for `ISBNs`_,
      downloads the book metadata (author, title, series, publication date,
      etc.) from online sources like Goodreads, Amazon and Google Books and
      renames the files according to a specified template.
    * If no ISBN is found, the script can optionally search for the ebooks
      online by their title and author, which are extracted from the filename
      or file metadata.
    * Optionally an additional file that contains all the gathered ebook
      metadata can be saved together with the renamed book so it can later
      be used for additional verification, indexing or processing.
    * Most ebook types are supported: ``.epub``, ``.mobi``, ``.azw``,
      ``.pdf``, ``.djvu``, ``.chm``, ``.cbr``, ``.cbz``, ``.txt``, ``.lit``,
      ``.rtf``, ``.doc``, ``.docx``, ``.pdb``, ``.html``, ``.fb2``, ``.lrf``, 
      ``.odt``, ``.prc`` and potentially others. Even compressed ebooks in 
      arbitrary archive files are supported. For example a ``.zip``, ``.rar`` 
      or other archive file that contains the ``.pdf`` or ``.html`` chapters 
      of an ebook can be organized without a problem.
    * Optical character recognition (`OCR [Wikipedia]
      <https://en.wikipedia.org/wiki/Optical_character_recognition>`_) can be
      automatically used for ``.pdf``, ``.djvu`` and image files when no ISBNs 
      were found in them by the fast and straightforward conversion to 
      ``.txt``. This is very useful for scanned ebooks that only contain
      images or were badly OCR-ed in the first place.
    * Files are checked for corruption (zero-filled files, broken pdfs,
      corrupt archive, etc.) and corrupt files can optionally be moved to
      another folder.
    * Non-ebook documents, pamphlets and pamphlet-like documents like saved
      webpages, short pdfs, etc. can also be detected and optionally moved to
      another folder.
      
    **Ref.:** [ORG]_
      
  The `organize`_ subcommand from the ``ebooktools.py`` script uses this
  module.
  
- ``rename_calibre_library.py`` traverses a calibre library folder, renames
  all the book files in it by reading their metadata from calibre's
  ``metadata.opf`` files. Then the book files are either moved or symlinked
  to an output folder along with their corresponding metadata files.
  The `rename`_ subcommand from the ``ebooktools.py`` script uses this module.
- ``split_into_folders.py`` splits the supplied ebook files (and the
  accompanying metadata files if present) into folders with consecutive names
  that each contain the specified number of files. The `split`_ subcommand
  from the ``ebooktools.py`` script uses this module.

Thus, you have access to various `subcommands`_ from within the
``ebooktools.py`` script.

`:star:`

  * `ebook-tools`_ is the **original** Shell project I ported to Python. I 
    used the same names for the script options (short and longer versions) so
    that if you used the shell scripts, you will easily know how to run the
    corresponding `subcommand`_ with the given options.
  * `ebooktools.py`_ is the name of the Python script which will always be
    referred that way in this document (i.e. no hyphen and ending with ``.py``)
    to distinguish from the original Shell project ``ebook-tools``.
  * `pyebooktools`_ is the name of the Python package that you need to
    `install <#install-pyebooktools>`__ to have access to the ``ebooktools.py``
    script.

Installation and dependencies
=============================
To install the script ``ebooktools.py``, follow these steps:

1. Install the dependencies `below <#other-dependencies>`__. 
2. Install the ``pyebooktools`` package `below <#install-pyebooktools>`__.

Python dependencies
-------------------
* **Platforms:** macOS [soon linux]
* **Python**: >= 3.6
* ``lxml`` >= 4.4 for parsing Calibre's ``metadata.opf`` files.

`:information_source:`

  When installing the ``pyebooktools`` package 
  `below <#install-pyebooktools>`__, the ``lxml`` library is automatically 
  installed if it is not found or upgraded to the correct supported version.

Other dependencies
--------------------
As explained in the documentation for `ebook-tools 
<https://github.com/na--/ebook-tools#shell-scripts>`__, you need recent
versions of:

  * `calibre`_ for fetching metadata from online sources, conversion to txt
    (for ISBN searching) and ebook metadata extraction. Versions **2.84** and
    above are preferred because of their ability to manually specify from which
    specific online source we want to fetch metadata. For earlier versions you
    have to set ``isbn_metadata_fetch_order`` and
    ``organize_without_isbn_sources`` to empty strings.
  * `p7zip`_ for ISBN searching in ebooks that are in archives.
  * `Tesseract`_ for running OCR on books - version 4 gives better results even
    though it's still in alpha. OCR is disabled by default and another engine
    can be configured if preferred.
  * **Optionally** `poppler`_, `catdoc`_ and `DjVuLibre`_ can be installed for
    faster than calibre's conversion of ``.pdf``, ``.doc`` and ``.djvu`` files
    respectively to ``.txt``.
    
    `:warning:`
    
       On macOS, you don't need `catdoc`_ since it has the built-in `textutil`_
       command-line tool that converts any ``txt``, ``html``, ``rtf``, 
       ``rtfd``, ``doc``, ``docx``, ``wordml``, ``odt``, or ``webarchive`` file.
    
  * **Optionally** the `Goodreads`_ and `WorldCat xISBN`_ calibre plugins can
    be installed for better metadata fetching.

|

`:star:`

  If you only install **calibre** among these dependencies, you can still have
  a functioning program that will organize and manage your ebook
  collections: 
  
  * fetching metadata from online sources will work: by `default 
    <https://manual.calibre-ebook.com/generated/en/fetch-ebook-metadata.html#
    cmdoption-fetch-ebook-metadata-allowed-plugin>`__
    **calibre** comes with Amazon and Google sources among others
  * conversion to txt will work: `calibre`'s own `ebook-convert`_ tool
    will be used
    
  All `subcommands`_ should work but accuracy and performance will be
  affected as explained in the list of dependencies above.

Install ``pyebooktools``
-------------------------
To install the `pyebooktools`_ package:

1. It is highly recommended to install the ``pyebooktools`` package in a
   virtual environment using for example `venv`_ or `conda`_.

2. Make sure to update *pip*::

   $ pip install --upgrade pip

3. Install the ``pyebooktools`` package (**bleeding-edge version**) with
   *pip*::

   $ pip install git+https://github.com/raul23/pyebooktools#egg=pyebooktools

`:warning:`

   Make sure that *pip* is working with the correct Python version. It might be
   the case that *pip* is using Python 2.x You can find what Python version
   *pip* uses with the following::

      $ pip -V

   If *pip* is working with the wrong Python version, then try to use *pip3*
   which works with Python 3.x
   
**Test installation**

1. Test your installation by importing ``pyebooktools`` and printing its
   version::

   $ python -c "import pyebooktools; print(pyebooktools.__version__)"

2. You can also test that you have access to the ``ebooktools.py`` script by
   showing the program's version::

   $ ebooktools --version

Usage, options and configuration
================================
All of the options documented below can either be passed to the
`ebooktools.py`_ script via command-line arguments or via the configuration
file ``config.py`` which is created along with the logging config file
``logging.py`` when the ``ebooktools.py`` script is run the first time with any
of the subcommands defined `below`_. The default values for these config files
are taken from `default_config.py`_ and `default_logging.py`_, respectively.

In order to use the parameters found in the configuration file ``config.py``, 
use the `--use-config`_ flag. Hence, you don't need to specify a long command-line
in the terminal by using this flag. See the `edit`_ subcommand to know how to
edit this configuration file.

Most arguments are not required and if nothing is specified, the default values
defined in the default config file ``default_config.py`` will be used.

The ``ebooktools.py`` script consists of various subcommands for the
organization and management of ebook collections. The usage pattern for running
one of the subcommands is as followed:

.. code-block:: terminal

  ebooktools {edit,convert,find,organize,rename,split} [OPTIONS]
  
where ``[OPTIONS]`` includes general options (as defined in the
`General options <#general-options>`__ section) and options specific to the 
subcommand (as defined in the `Script usage, subcommands and options`_ section).

`:warning:`
 
   In order to avoid data loss, use the `--dry-run`_ or `--symlink-only`_
   option when running some of the subcommands (e.g. ``rename`` and ``split``)
   to make sure that they would do what you expect them to do, as explained in
   the `Security and safety`_ section.

General options
---------------
Most of these options are part of the common library `lib.py`_ and may affect
some or all of the subcommands.

General control flags
^^^^^^^^^^^^^^^^^^^^^
* ``-h``, ``--help``; no config variable; default value ``False``

  Show the help message and exit.

* ``-v``, ``--version``; no config variable; default value ``False``

  Show program's version number and exit.

.. _quiet-label:

* ``-q``, ``--quiet``; config variable ``quiet``; default value ``False``

  Enable quiet mode, i.e. nothing will be printed.

.. _verbose-label:

* ``--verbose``; config variable ``verbose``; default value ``False``

  Print various debugging information, e.g. print traceback when there is an
  exception.
  
.. _use-config-label:

* ``-u``, ``--use-config``; no config variable; default value ``False``

  If this is enabled, the parameters found in the main config file `config.py`_ 
  will be used instead of the command-line arguments. 
  
  `:information_source:`
  
    Note that any other command-line argument that you use in the terminal with 
    the ``--use-config`` flag is ignored, i.e. only the parameters defined in 
    the main config file `config.py`_ will be used.

.. _dry-run-label:

* ``-d``, ``--dry-run``; config variable ``dry_run``; default value ``False``

  If this is enabled, no file rename/move/symlink/etc. operations will actually
  be executed.

.. _symlink-only-label:

* ``--sl``, ``--symlink-only``; config variable ``symlink_only``; default value
  ``False``
  
  Instead of moving the ebook files, create symbolic links to them.

.. _keep-metadata-label:

* ``--km``, ``--keep-metadata``; config variable ``keep_metadata``; default
  value ``False``
  
  Do not delete the gathered metadata for the organized ebooks, instead save it
  in an accompanying file together with each renamed book. It is very useful
  or for additional verification, indexing or processing at a later date. [KM]_
  
  .. TODO
  .. for semi-automatic verification of the organized files with `interactive_organizer.py`_

Script usage, subcommands and options
-------------------------------------
The usage pattern for running a given **subcommand** is the following:

.. code-block:: terminal

  ebooktools {edit,convert,find,organize,rename,split} [OPTIONS]
  
where ``[OPTIONS]`` includes `general options <#general-options>`__ and 
options specific to the subcommand as shown below.

`:information_source:`

  Don't forget the name of the Python script ``ebooktools`` before the
  subcommand.

All subcommands are affected by the following global options:

* `-h, --help`_
* `-q, --quiet`_
* `-v, --verbose`_
* `-u, --use-config`_
* `--log-level`_
* `--log-format`_

The `-h, --help`_ option can be applied specifically to each subcommand or
to the  ``ebooktools.py`` script (when called without the subcommand). Thus
when you want the help message for a specific subcommand, you do:

.. code-block:: terminal

  ebooktools {edit,convert,find,split} -h
 
which will show you the options that affect the choosen subcommand. 

|

And if you want the help message for the whole ``ebooktools.py`` script:

.. code-block:: terminal

  ebooktools -h
  
which will show you the project description and description
of each subcommand without showing the subcommand options.

Examples
========
More examples can be found at `examples.rst`_.

Example 1: convert a pdf file to text **with** OCR
--------------------------------------------------
To convert a pdf file to text **with OCR**:

.. code-block:: terminal

   $ ebooktools convert --ocr always -o converted.txt pdf_to_convert.pdf
   
By setting `--ocr`_ to ``always``, the pdf file will be first OCRed before
trying the simple conversion tools (``pdftotext`` or calibre's 
``ebook-convert`` if the former command is not found).

.. code-block:: terminal

   Running pyebooktools v0.1.0a3
   Verbose option disabled
   OCR=always, first try OCR then conversion
   Will run OCR on file 'pdf_to_convert.pdf' with 1 page...
   OCR successful!

Example 2: find ISBNs in a pdf file
-----------------------------------
Find ISBNs in a pdf file:

.. code-block:: terminal

   $ ebooktools find pdf_file.pdf

**Output:**

.. code-block:: terminal

   Running pyebooktools v0.1.0a3
   Verbose option disabled
   Searching file 'pdf_file.pdf' for ISBN numbers...
   Extracted ISBNs:
   9789580158448
   1000100111

The search for ISBNs starts in the first pages of the document to increase
the likelihood that the first extracted ISBN is the correct one. Then the
last pages are analyzed in reverse. Finally, the rest of the pages are
searched.

Thus, in this example, the first extracted ISBN is the correct one
associated with the book since it was found in the first page. 

The last sequence ``1000100111`` was found in the middle of the document
and is not an ISBN even though it is a technically valid but wrong ISBN
that the regular expression `isbn_blacklist_regex`_ didn't catch. Maybe
it is a binary sequence that is part of a problem in a book about digital
system. 

Uninstall
=========
To uninstall the `pyebooktools`_ package::

   $ pip uninstall pyebooktools
   
`:information_source:`

   When uninstalling the ``pyebooktools`` package, you might be informed
   that the configuration files *logging.py* and *config.py* won't be
   removed by *pip*. You can remove those files manually by noting their paths
   returned by *pip*. Or you can leave them so your saved settings can be
   re-used the next time you re-install the package.

   **Example:** uninstall the package and remove the config files

   .. code-block:: console

      $ pip uninstall pyebooktools
      Found existing installation: pyebooktools 0.1.0a3
      Uninstalling pyebooktools-0.1.0a3:
        Would remove:
          /Users/test/miniconda3/envs/ebooktools_py37/bin/ebooktools
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/pyebooktools-0.1.0a3.dist-info/*
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/pyebooktools/*
        Would not remove (might be manually added):
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/pyebooktools/configs/config.py
          /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/pyebooktools/configs/logging.py
      Proceed (y/n)? y
        Successfully uninstalled pyebooktools-0.1.0a3
      $ rm -r /Users/test/miniconda3/envs/ebooktools_py37/lib/python3.7/site-packages/pyebooktools/

Limitations
===========
Same `limitations`_ as for ``ebook-tools`` apply to this project too:

  * Automatic organization can be slow - all the scripts are synchronous
    and single-threaded and metadata lookup by ISBN is not done
    concurrently. This is intentional so that the execution can be easily
    traced and so that the online services are not hammered by requests.
    If you want to optimize the performance, run multiple copies of the
    script **on different folders**.
    
  * The default setting for `isbn_metadata_fetch_order`_ includes two
    non-standard metadata sources: Goodreads and WorldCat xISBN. For
    best results, install the plugins (`1`_, `2`_) for them in calibre and
    fine-tune the settings for metadata sources in the calibre GUI.

Security and safety
===================
Important security and safety tips from the `ebook-tools documentation`_:

  Please keep in mind that this is beta-quality software. To avoid data loss,
  make sure that you have a backup of any files you want to organize. You may
  also want to run the scripts with the `--dry-run`_ or `--symlink-only`_
  option the first time to make sure that they would do what you expect them to
  do.
  
  Also keep in mind that these shell scripts parse and extract complex
  arbitrary media and archive files and pass them to other external programs
  written in memory-unsafe languages. This is not very safe and
  specially-crafted malicious ebook files can probably compromise your system
  when you use these scripts. If you are cautious and want to organize
  untrusted or unknown ebook files, use something like `QubesOS`_ or at least
  do it in a separate VM/jail/container/etc.

**NOTE:** ``--dry-run`` and ``--symlink-only`` can be applied to the following
subcommands:

.. TODO
.. `interact`_
* `organize`_
* `rename`_
* `split`_: only ``--dry-run`` is applicable

Roadmap
=======
Starting from first priority tasks

Short-term
----------
1. Port all `ebook-tools`_ shell scripts into Python

   - |ss| ``organize-ebooks.sh`` |se|: **done**, *see* `organize_ebooks.py`_
   - ``interactive-organizer.sh``
   - |ss| ``find-isbns.sh`` |se|: **done**, *see* `find_isbns.py`_
   - |ss| ``convert-to-txt.sh`` |se|: **done**, *see* `convert_to_txt.py`_
   - |ss| ``rename-calibre-library.sh`` |se|: **done**, *see* `rename_calibre_library.py`_
   - |ss| ``split-into-folders.sh`` |se|: **done**, *see* `split_into_folders.py`_

   **Status:** only ``interactive-organizer.sh`` remaining, will port later

2. Add `cache`_ support when converting files to txt

   **Status:** working on it since it is also needed for my other project
   `search-ebooks <https://github.com/raul23/search-ebooks#cache>`__ 
   which makes heavy use of `pyebooktools`_
   
3. Test on linux
4. Create a `docker`_ image for this project

Medium-term
-----------
1. Add tests on `Travis CI`_

2. Eventually add documentation on `Read the Docs`_
3. Add a ``fix`` subcommand that will try to fix corrupted PDF files based on
   one of the following utilities:
  
   * |ss| ``gs``: Ghostscript |se|; done, *see* `fix_file_for_corruption()`_
   * ``pdftocairo``: from Poppler
   * ``mutool``: it does not "print" the PDF file
   * ``cpdf``
  
   It will also check PDF files based on one of the following utilities:
  
   * ``pdfinfo``
   * ``pdftotext``
   * ``qpdf``
   * ``jhove``
   
4. Add a ``remove`` subcommand that can remove annotations (incl. highlights, 
   comments, notes, arrows), bookmarks, attachments and metadata from PDF files 
   based on the `cpdf`_ utility
   
   **NOTE:** `pdftk`_ can also remove annotations 

Credits
=======
* Special thanks to `na--`_, the developer of `ebook-tools`_, for having made
  these very useful tools. I learned a lot (specially ``bash``) while porting
  them to Python.
* Thanks to all the developers of the different programs used by this project
  such as ``calibre``, ``Tesseract``, text converters (``djvutxt`` and
  ``pdftotext``) and many other utilities!

License
=======
This program is licensed under the GNU General Public License v3.0. For more
details see the `LICENSE`_ file in the repository.

References
==========
.. [IBR] https://github.com/na--/ebook-tools#options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. [IDGF] https://github.com/na--/ebook-tools#options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. [IIF] https://github.com/na--/ebook-tools#options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. [KM] https://github.com/na--/ebook-tools#general-control-flags
.. [MFO] https://github.com/na--/ebook-tools#options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. [OCR] https://github.com/na--/ebook-tools#options-for-ocr
.. [OCRC] https://github.com/na--/ebook-tools#options-for-ocr
.. [OCROP] https://github.com/na--/ebook-tools#options-for-ocr
.. [OFT] https://github.com/na--/ebook-tools#options-related-to-the-input-and-output-files
.. [OME] https://github.com/na--/ebook-tools#options-related-to-the-input-and-output-files
.. [ORG] https://github.com/na--/ebook-tools#ebook-tools
.. [ORGD] https://github.com/na--/ebook-tools#description
.. [OWI] https://github.com/na--/ebook-tools#specific-options-for-organizing-files
.. [OWIS] https://github.com/na--/ebook-tools#options-related-to-extracting-and-searching-for-non-isbn-metadata
.. [PIF] https://github.com/na--/ebook-tools#specific-options-for-organizing-files
.. [RCL] https://bit.ly/3sPJ9kT
.. [RFFG] https://github.com/na--/ebook-tools#options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. [SM] https://bit.ly/3sPJ9kT
.. [TI] https://github.com/na--/ebook-tools#options-related-to-extracting-and-searching-for-non-isbn-metadata
.. [TML] https://github.com/na--/ebook-tools#options-related-to-extracting-and-searching-for-non-isbn-metadata
.. [WII] https://github.com/na--/ebook-tools#specific-options-for-organizing-files

.. URLs
.. _1: https://www.mobileread.com/forums/showthread.php?t=130638
.. _2: https://github.com/na--/calibre-worldcat-xisbn-metadata-plugin
.. _cache: https://github.com/grantjenks/python-diskcache
.. _calibre: https://calibre-ebook.com/
.. _catdoc: http://www.wagner.pp.ru/~vitus/software/catdoc/
.. _conda: https://docs.conda.io/en/latest/
.. _cpdf: https://community.coherentpdf.com
.. _docker: https://docs.docker.com/
.. _documentation for ebook-tools: https://github.com/na--/ebook-tools#searching-for-isbns-in-files
.. _DjVuLibre: http://djvu.sourceforge.net/
.. _ebook-convert: https://manual.calibre-ebook.com/generated/en/ebook-convert.html
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _ebook-tools documentation: https://github.com/na--/ebook-tools#security-and-safety
.. _Goodreads: https://www.mobileread.com/forums/showthread.php?t=130638
.. _ISBNs: https://en.wikipedia.org/wiki/International_Standard_Book_Number
.. _limitations: https://github.com/na--/ebook-tools#limitations
.. _na--: https://github.com/na--
.. _p7zip: https://sourceforge.net/projects/p7zip/
.. _pdftk: https://stackoverflow.com/a/49614525/14664104
.. _plugins: https://plugins.calibre-ebook.com/
.. _poppler: https://poppler.freedesktop.org/
.. _QubesOS: https://www.qubes-os.org/
.. _Read the Docs: https://readthedocs.org/
.. _search-ebooks: https://github.com/raul23/search-ebooks
.. _searches: https://github.com/na--/ebook-tools#searching-for-isbns-in-files
.. _shell scripts: https://github.com/na--/ebook-tools#script-usage-and-options
.. _Tesseract: https://github.com/tesseract-ocr/tesseract
.. _textutil: https://ss64.com/osx/textutil.html
.. _Travis CI: https://travis-ci.com/
.. _valid ISBNs: https://en.wikipedia.org/wiki/International_Standard_Book_Number#Check_digits
.. _venv: https://docs.python.org/3/library/venv.html#module-venv
.. _WorldCat xISBN: https://github.com/na--/calibre-worldcat-xisbn-metadata-plugin

.. URLs: pyebooktools project
.. _convert_to_txt.py: ./pyebooktools/convert_to_txt.py
.. _default_config.py: ./pyebooktools/configs/default_config.py
.. _default_logging.py: ./pyebooktools/configs/default_logging.py
.. _ebooktools.py: ./pyebooktools/scripts/ebooktools.py
.. _examples.rst: ./docs/examples.rst
.. _find_isbns.py: ./pyebooktools/find_isbns.py
.. _fix_file_for_corruption(): https://github.com/raul23/pyebooktools/blob/1067ce48a250404bf6225d36dd3e1defd05f751b/pyebooktools/lib.py#L461
.. _interactive_organizer.py: ./pyebooktools/interactive_organizer.py
.. _lib.py: ./pyebooktools/lib.py
.. _LICENSE: ./LICENSE
.. _organize_ebooks.py: ./pyebooktools/organize_ebooks.py
.. _pyebooktools: ./pyebooktools
.. _rename_calibre_library.py: ./pyebooktools/rename_calibre_library.py
.. _search_file_for_isbns(): https://github.com/raul23/pyebooktools/blob/52795d9d45d5ae0e666a45cbafb6e4919343dfda/pyebooktools/lib.py#L880
.. _split_into_folders.py: ./pyebooktools/split_into_folders.py

.. URLs: local
.. _all the ocr-related options: #options-for-ocr
.. _below: #script-usage-and-options
.. _config.py: #edit-description-label
.. _convert: #convert-options-input-file
.. _edit: #edit-options-main-log
.. _find: #find-options-input-data
.. _General control flags: #general-control-flags
.. _interact: #security-and-safety
.. _isbn_blacklist_regex: #isbn-blacklist-regex-label
.. _isbn_metadata_fetch_order: #metadata-fetch-order-label
.. _keep_metadata: #keep-metadata-label
.. _Miscellaneous options: #miscellaneous-options
.. _OCR ones: #options-for-ocr
.. _Options related to the input and output files: #options-related-to-the-input-and-output-files
.. _organize: #organize-options-folder-to-organize
.. _organize_without_isbn: #organize-without-isbn-label
.. _organize_without_isbn_sources: #organize-without-isbn-sources-label
.. _output_folder_corrupt: #output-folder-corrupt-label
.. _output_folder_pamphlets: #output-folder-pamphlets-label
.. _output_metadata_extension: #output-metadata-extension-label
.. _related to extracting ISBNs from files: #options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. _rename: #rename-options-calibre-folder
.. _Script usage, subcommands and options: #script-usage-subcommands-and-options
.. _Security and safety: #security-and-safety
.. _split: #split-options-folder-with-books
.. _subcommand: #script-usage-subcommands-and-options
.. _subcommands: #script-usage-subcommands-and-options
.. _Usage, options and configuration: #usage-options-and-configuration
.. _without_isbn_ignore: #without-isbn-ignore-label
.. _-h, --help: #general-control-flags
.. _-v, --verbose: #verbose-label
.. _-q, --quiet: #quiet-label
.. _--verbose: #verbose-label
.. _--use-config: #use-config-label
.. _-u, --use-config: #use-config-label
.. _-d, --dry-run: #dry-run-label
.. _--dry-run: #dry-run-label
.. _--sl, --symlink-only: #symlink-only-label
.. _--symlink-only: #symlink-only-label
.. _--km, --keep-metadata: #keep-metadata-label
.. _-r, --reverse: #reverse-label
.. _--log-level: #log-level-label
.. _--log-format: #log-format-label
.. _-i, --isbn-regex: #isbn-regex-label
.. _--isbn-blacklist-regex: #isbn-blacklist-regex-label
.. _---mfo, ---metadata-fetch-order: #metadata-fetch-order-label
.. _--ocr: #options-for-ocr
.. _--owis, --organize-without-isbn-sources: #organize-without-isbn-sources-label
.. _--oft, --output-filename-template: #output-filename-template-label
.. _--ome, --output-metadata-extension: #output-metadata-extension-label

.. |ss| raw:: html

   <strike>

.. |se| raw:: html

   </strike>

.. TODOs
.. explain log-level and log-format choices of values
.. check ocr-command option (including description)
.. add more to description (+ examples of output filenames) for the output-filename-template option
.. add more to description for isbn-regex option
.. IMPORTANT: change internal url for subcommands in #security-and-safety
.. IMPORTANT: don't forget see default value
