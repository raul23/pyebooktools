=========================
README [Work-In-Progress]
=========================

.. raw:: html

  <p align="center">
    <img src="https://raw.githubusercontent.com/raul23/py-ebooktools/master/docs/logo/py_ebooktools.png">
    <br> 🚧 &nbsp;&nbsp;&nbsp;<b>Work-In-Progress</b>
  </p>

This project (**version 0.1.0a3**) is a Python port of `ebook-tools`_ which is
written in Shell by `na--`_. The Python script `ebooktools.py`_ is a collection
of tools for automated and semi-automated organization and management of large
ebook collections.

`:warning:`

  * For the moment, the script ``ebooktools.py`` is only tested on **macOS**.
    Eventually, I will test it on linux.
  * **More to come!** Check the `Roadmap <#roadmap>`_ to know what is coming
    soon.

.. contents:: **Contents**
   :depth: 4
   :local:
   :backlinks: top
   
Project description
===================
The `ebooktools.py`_ script is a Python port of the `shell scripts`_ from
`ebook-tools`_ and makes use of the following modules:

- ``edit_config.py`` edits a configuration file which can either be the main
  config file that contains all the options defined
  `below <#usage-options-and-configuration>`__ or the logging config file whose
  default values is defined in `default_logging.py`_. The `edit`_ subcommand
  from the ``ebook-tools.py`` script uses this module.
- ``convert_to_txt.py`` converts the supplied file to a text file. It can
  optionally also use *OCR* for ``.pdf``, ``.djvu`` and image files. The `convert`_
  subcommand from the ``ebook-tools.py`` script uses this module.
- ``find_isbns.py`` tries to find `valid ISBNs`_ inside a file or in a
  ``string`` if no file was specified. Searching for ISBNs in files uses
  progressively more resource-intensive methods until some ISBNs are found, for
  more details see
  
  - the `documentation for ebook-tools`_ (shell scripts) or
  - `search_file_for_isbns()`_ from ``lib.py`` (Python function where ISBNs
    search in files is implemented).
  
  The `find`_ subcommand from the ``ebook-tools.py`` script uses this module.
  
- ``split_into_folders.py`` splits the supplied ebook files (and the
  accompanying metadata files if present) into folders with consecutive names
  that each contain the specified number of files. The `split`_ subcommand
  from the ``ebook-tools.py`` script uses this module.

Thus, from within the ``ebooktools.py`` script, you have access to various
`subcommands`_.

Installation and dependencies
=============================
To install and use the script ``ebooktools.py``, follow these steps:

1. Install the dependencies `below <#install-dependencies>`__. 
2. Install the package ``py_ebooktools`` `below <#install-py-ebooktools>`__.

Install dependencies
--------------------
As explained in the documentation for `ebook-tools 
<https://github.com/na--/ebook-tools#shell-scripts>`__ (shell scripts), you
need recent versions of:

  * `calibre`_ for fetching metadata from online sources, conversion to txt (for
    ISBN searching) and ebook metadata extraction. Versions **2.84** and above
    are preferred because of their ability to manually specify from which
    specific online source we want to fetch metadata. For earlier versions you
    have to set ``isbn_metadata_fetch_order`` and
    ``organize_without_isbn_sources`` to empty strings.
  * `p7zip`_ for ISBN searching in ebooks that are in archives.
  * `Tesseract`_ for running OCR on books - version 4 gives better results even
    though it's still in alpha. OCR is disabled by default and another engine can
    be configured if preferred.
  * **Optionally** `poppler`_, `catdoc`_ and `DjVuLibre`_ can be installed for
    faster than calibre's conversion of ``.pdf``, ``.doc`` and ``.djvu`` files
    respectively to ``.txt``.
  * **Optionally** the `Goodreads`_ and `WorldCat xISBN`_ calibre plugins can be
    installed for better metadata fetching.
  
`:warning:`

  For the moment, the script ``ebooktools.py`` is only tested on **macOS**.
  Eventually, I will test it on linux.

Install ``py_ebooktools``
-------------------------
The package ``py_ebooktools`` contains the script ``ebooktools.py`` which
consists of various subcommands (e.g. ``find`` and ``organize``) for
automated and semi-automated organization and management of large ebook
collections as explained in the `Usage, options and configuration`_ section.

1. It is highly recommended to install the package ``py_ebooktools`` in a
   virtual environment using for example `venv`_ or `conda`_.

2. Make sure to update *pip*::

   $ pip install --upgrade pip

3. Install the package ``py_ebooktools`` (**bleeding-edge version**) with
   *pip*::

   $ pip install git+https://github.com/raul23/py-ebooktools#egg=py-ebooktools

`:warning:`

   Make sure that *pip* is working with the correct Python version. It might be
   the case that *pip* is using Python 2.x You can find what Python version
   *pip* uses with the following::

      $ pip -V

   If *pip* is working with the wrong Python version, then try to use *pip3*
   which works with Python 3.x
   
**Test installation**

1. Test your installation by importing ``py_ebooktools`` and printing its
   version::

   $ python -c "import py_ebooktools; print(py_ebooktools.__version__)"

2. You can also test that you have access to the ``ebooktools.py`` script by
   showing the program's version::

   $ ebooktools --version

Usage, options and configuration
================================
All of the options documented below can either be passed to the
`ebooktools.py`_ script via command-line parameters or via the configuration
file ``config.py`` which is created along with the logging config file
``logging.py`` when the script ``ebooktools.py`` is run the first time with any
of the subcommands defined `below`_. The default values for these config files
are taken from `default_config.py`_ and `default_logging.py`_, respectively.

Command-line parameters supersede variables defined in the configuration file.
Most parameters are not required and if nothing is specified, the default value
defined in the default config file ``default_config.py`` will be used.

The ``ebooktools.py`` script consists of various subcommands for the
organization and management of ebook collections. The usage pattern for running
one of the subcommands is as follows:

.. code-block:: terminal

  ebooktools {edit,convert,find,split} [<OPTIONS>]
  
Where ``[<OPTIONS>``] include general options (as defined in the
`General options`_ section) and options specific to the subcommand (as defined
in the `Script usage, subcommands and options`_ section).

`:warning:`
 
   In order to avoid data loss, use the option ``dry-run`` or ``symlink-only`` when
   running some of the subcommands (e.g. ``rename`` and ``split``) to make sure that
   they would do what you expect them to do, as explained in the
   `Security and safety`_ section.

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

* ``-q``, ``--quiet``; config variable ``quiet``; default value ``False``

  Enable quiet mode, i.e. nothing will be printed.

* ``--verbose``; config variable ``verbose``; default value ``False``

  Print various debugging information, e.g. print traceback when there is an
  exception.

* ``-d``, ``--dry-run``; config variable ``dry_run``; default value ``False``

  If this is enabled, no file rename/move/symlink/etc. operations will actually
  be executed.

* ``--sl``, ``--symlink-only``; config variable ``symlink_only``; default value
  ``False``
  
  Instead of moving the ebook files, create symbolic links to them.

* ``--km``, ``--keep-metadata``; config variable ``keep_metadata``; default
  value ``False``
  
  Do not delete the gathered metadata for the organized ebooks, instead save it
  in an accompanying file together with each renamed book. It is very useful
  for semi-automatic verification of the organized files with
  ``interactive_organizer.py`` or for additional verification, indexing or
  processing at a later date. [KM]_

Options related to extracting ISBNs from files and finding metadata by ISBN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``-i <value>``, ``--isbn-regex <value>``; config variable ``isbn_regex``; see
  default value in `default_config.py#L59`_
  
  This is the regular expression used to match ISBN-like numbers in the supplied
  books.

* ``--isbn-blacklist-regex <value>``; config variable ``isbn_blacklist_regex``;
  default value ``^(0123456789|([0-9xX])\2{9})$``
  
  Any ISBNs that were matched by the ``isbn_regex`` above and pass the ISBN
  validation algorithm are normalized and passed through this regular
  expression. Any ISBNs that successfully match against it are discarded. The
  idea is to ignore technically valid but probably wrong numbers like
  ``0123456789``, ``0000000000``, ``1111111111``, etc. [IBR]_
  
* ``--isbn-direct-grep-files <value>``; config variable
  ``isbn_direct_grep_files``; default value ``^text/(plain|xml|html)$``
  
  This is a regular expression that is matched against the MIME type of the
  searched files. Matching files are searched directly for ISBNs, without
  converting or OCR-ing them to ``.txt`` first. [IDGF]_
  
* ``--isbn-ignored-files <value>``; config variable ``isbn_ignored_files``; see
  default value in `default_config.py#L62`_
  
  This is a regular expression that is matched against the MIME type of the
  searched files. Matching files are not searched for ISBNs beyond their
  filename. The default value is a bit long because it tries to make the
  scripts ignore ``.gif`` and ``.svg`` images, audio, video and executable
  files and fonts. [IIF]_
  
* ``--reorder-files-for-grep <value>``; config variable
  ``isbn_grep_reorder_files``, ``isbn_grep_rf_scan_first``,
  ``isbn_grep_rf_reverse_last``; default value ``400``, ``50``
  
  These options specify if and how we should reorder the ebook text before
  searching for ISBNs in it. By default, the first 400 lines of the text are
  searched as they are, then the last 50 are searched in reverse and finally
  the remainder in the middle. This reordering is done to improve the odds that
  the first found ISBNs in a book text actually belong to that book (ex. from
  the copyright section or the back cover), instead of being random ISBNs
  mentioned in the middle of the book. No part of the text is searched twice,
  even if these regions overlap. If you use the command-line option, the format
  for ``<value>`` is ``False`` to disable the functionality or
  ``first_lines,last_lines`` to enable it with the specified values. [RFFG]_
  
* ``--mfo <value>``, ``--metadata-fetch-order <value>``; config variable
  ``isbn_metadata_fetch_order``; default value
  ``Goodreads,Amazon.com,Google,ISBNDB,WorldCat xISBN,OZON.ru``
  
  This option allows you to specify the online metadata sources and order in
  which the scripts will try searching in them for books by their ISBN. The
  actual search is done by calibre's ``fetch-ebook-metadata`` command-line
  application, so any custom calibre metadata `plugins`_ can also be used. To
  see the currently available options, run ``fetch-ebook-metadata --help`` and
  check the description for the ``--allowed-plugin`` option. [MFO]_
  
  *If you use Calibre versions that are older than 2.84, it's required to
  manually set this option to an empty string.*

Options for OCR
^^^^^^^^^^^^^^^
* ``--ocr <value>``, ``--ocr-enabled <value>``; config variable
  ``ocr_enabled``; default value ``False``
  
  Whether to enable OCR for ``.pdf``, ``.djvu`` and image files. It is disabled
  by default and can be used differently in two scripts [OCR]_:
  
  * ``organize_ebooks.py`` can use OCR for finding ISBNs in scanned books.
    Setting the value to ``True`` will cause it to use OCR for books that
    failed to be converted to ``.txt`` or were converted to empty files by the
    simple conversion tools (``ebook-convert``, ``pdftotext``, ``djvutxt``).
    Setting the value to ``always`` will cause it to use OCR even when the
    simple tools produced a non-empty result, if there were no ISBNs in it.
    
  * ``convert_to_txt.py`` can use OCR for the conversion to ``.txt``. Setting
    the value to ``True`` will cause it to use OCR for books that failed to be
    converted to ``.txt`` or were converted to empty files by the simple
    conversion tools. Setting it to ``always`` will cause it to first try
    OCR-ing the books before trying the simple conversion tools.
  
* ``--ocrop <value>``, ``--ocr-only-first-last-pages <value>``; config variable 
  ``ocr_only_first_last_pages``; default value ``(7,3)`` (except for
  `convert_to_txt.py`_ where it's ``False``)
  
  Value ``n,m`` instructs the scripts to convert only the first ``n`` and last
  ``m`` pages when OCR-ing ebooks. This is done because OCR is a slow
  resource-intensive process and ISBN numbers are usually at the beginning or
  at the end of books. Setting the value to ``False`` disables this
  optimization and is the default for ``convert_to_txt.sh``, where we probably
  want the whole book to be converted. [OCROP]_
  
* ``--ocrc <value>``, ``--ocr-command <value>``; config variable
  ``ocr_command``; default value ``tesseract_wrapper``
  
  This allows us to define a hook for using custom OCR settings or software.
  The default value is just a wrapper that allows us to use both tesseract 3
  and 4 with some predefined settings. You can use a custom bash function or
  shell script - the first argument is the input image (books are OCR-ed page
  by page) and the second argument is the file you have to write the output
  text to. [OCRC]_

Options related to extracting and searching for non-ISBN metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``--token-min-length <value>``; config variable token_min_length; default
  value ``3``

  When files and file metadata are parsed, they are split into words (or more
  precisely, either alpha or numeric tokens) and ones shorter than this value
  are ignored. By default, single and two character number and words are
  ignored. [TML]_
  
* ``--tokens-to-ignore <value>``; env. variable ``tokens_to_ignore``; see
  default value in `default_config.py#L80`_

  A regular expression that is matched against the filename/author/title tokens
  and matching tokens are ignored. The default regular expression includes
  common words that probably hinder online metadata searching like ``book``,
  ``novel``, ``series``, ``volume`` and others, as well as probable publication
  years (so ``1999`` is ignored while ``2033`` is not). [TI]_
  
* ``--owis <value>``, ``--organize-without-isbn-sources <value>``; config
  variable ``organize_without_isbn_sources``; default value
  ``Goodreads,Amazon.com,Google``
  
  This option allows you to specify the online metadata sources in which the
  scripts will try searching for books by non-ISBN metadata (i.e. author and
  title). The actual search is done by calibre's ``fetch-ebook-metadata``
  command-line application, so any custom calibre metadata `plugins`_ can also
  be used. To see the currently available options, run
  ``fetch-ebook-metadata --help`` and check the description for the
  ``--allowed-plugin`` option. *Because Calibre versions older than 2.84 don't
  support the --allowed-plugin option, if you want to use such an old Calibre
  version you should manually set ORGANIZE_WITHOUT_ISBN_SOURCES to an empty
  string.*
  
  In contrast to searching by ISBNs, searching by author and title is done
  concurrently in all of the allowed online metadata sources. The number of
  sources is smaller because some metadata sources can be searched only by ISBN
  or return many false-positives when searching by title and author. [OWIS]_

Options related to the input and output files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* ``--oft <value>``, ``--output-filename-template <value>``; config variable
  ``output_filename_template``; default value:
  
  .. code-block:: bash
  
     "${d[AUTHORS]// & /, } - ${d[SERIES]:+[${d[SERIES]}] - }${d[TITLE]/:/ -}${d[PUBLISHED]:+ (${d[PUBLISHED]%%-*})}${d[ISBN]:+ [${d[ISBN]}]}.${d[EXT]}"
  
  By default the organized files start with the comma-separated author name(s),
  followed by the book series name and number in square brackets (if present),
  followed by the book title, the year of publication (if present), the ISBN(s)
  (if present) and the original extension. [OFT]_
  
* ``--ome <value>``, ``--output-metadata-extension <value>``; config variable
  ``output_metadata_extension``; default value ``meta``
  
  If ``keep_metadata`` is enabled, this is the extension of the additional
  metadata file that is saved next to each newly renamed file. [OME]

Miscellaneous options
^^^^^^^^^^^^^^^^^^^^^
* ``--log-level <value>``; config variable ``logging_level``; default value
  ``info``

  Set logging level for all loggers. Choices are
  ``{debug,info,warning,error}``.

* ``--log-format <value>``; config variable ``logging_formatter``; default
  value ``simple``

  Set logging formatter for all loggers. Choices are
  ``{console,simple,only_msg}``.

* ``-r``, ``--reverse``; config variable ``reverse``; default value ``False``

  If this is enabled, the files will be sorted in reverse (i.e. descending)
  order. By default, they are sorted in ascending order.
  
  *NOTE: more sort options will eventually be implemented, such as random sort.*

Script usage, subcommands and options
------------------------------------
The usage pattern for running a given **subcommand** is the following:

.. code-block:: terminal

  ebooktools {edit,convert,find,split} [<OPTIONS>]
  
Where ``[<OPTIONS>]`` include general options and options specific to the
subcommand as shown below.

`:information_source:`

  Don't forget the name of the Python script ``ebooktools`` before the
  subcommand.

All subcommands are affected by the following global options:

* `-h, --help`_
* `-v, --verbose`_
* `-q, --quiet`_
* `--verbose`_
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

|

In the subsections below, you will find a definition for each of the
supported subcommands for automated and semi-automated organization and
management of large ebook collections.

edit [<OPTIONS>] {main,log}
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: terminal

   usage: ebooktools edit [-h] [-v] [-q] [--verbose]
                          [--log-level {debug,info,warning,error}]
                          [--log-format {console,simple,only_msg}] [-a [NAME] | -r]
                          {main,log}

Description
"""""""""""
Edits a configuration file, either the main configuration file (``main``) or
the logging configuration file (``log``). The configuration file can be opened
by a user-specified application (``app``) or a default program associated with
this type of file (when ``app`` is ``None``).

Options
"""""""
* ``-a <value>``, ``--app <value>``; config variable ``app``; 
  default value ``None``
* ``-r``, ``--reset``; no config variable; default value ``False``

Input argument
""""""""""""""
* ``{main,log}``; no config variable; **required**
  
  The config file to edit which can either be the main configuration file
  (``main``) or the logging configuration file (``log``).

convert [<OPTIONS>] input_file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: terminal

   usage: ebooktools convert [-h] [-v] [-q] [--verbose]
                             [--log-level {debug,info,warning,error}]
                             [--log-format {console,simple,only_msg}]
                             [--ocr {always,true,false}] [--ocrop PAGES PAGES]
                             [--ocrc CMD] [-o OUTPUT]
                             input_file

Description
"""""""""""
Converts the supplied file to a **text** file. It can optionally also use OCR for
``.pdf``, ``.djvu`` and image files.

Global options
""""""""""""""
Some of the global options affect this script's behavior a lot, especially the
`OCR ones`_.

Input and output arguments
""""""""""""""""""""""""""
* ``input_file``; no config variable; **required**
  
  The input file to be converted to a text file.
  
* ``-o <value>``, ``--output-file <value>``; config variable ``output_file``;
  default values is ``output.txt``
  
  The output file text. By default, it is saved in the current working
  directory.


find [<OPTIONS>] input_data
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: terminal

   usage: ebooktools find [-h] [-v] [-q] [--verbose]
                          [--log-level {debug,info,warning,error}]
                          [--log-format {console,simple,only_msg}]
                          [-i ISBN_REGEX] [--isbn-blacklist-regex REGEX]
                          [--isbn-direct-grep-files REGEX]
                          [--isbn-ignored-files REGEX]
                          [--reorder-files-for-grep LINES [LINES ...]]
                          [--ocr {always,true,false}] [--ocrop PAGES PAGES]
                          [--ocrc CMD] [--irs SEPARATOR]
                          input_data
                         
Description
"""""""""""                       
Tries to find `valid ISBNs`_ inside a file or in a ``string`` if no file was 
specified. Searching for ISBNs in files uses progressively more
resource-intensive methods until some ISBNs are found, for more details see

- the `documentation for ebook-tools`_ (shell scripts) or
- `search_file_for_isbns()`_ from ``lib.py`` (Python function where ISBNs
  search in files is implemented).

Global options
""""""""""""""
The global options that especially affect this script are the ones `related to
extracting ISBNs from files`_ and the `OCR ones`_.

Local options
"""""""""""""
The only subcommand-specific option is:

* ``--irs <value>``, ``--isbn-return-separator <value>``; config variable
  ``isbn_ret_separator``; default value ``\n`` (a new line)
  
  This specifies the separator that will be used when returning any found
  ISBNs.

Input argument
""""""""""""""
* ``input_data``; no config variable; **required**

  Can either be the path to a file or a string. The input will be searched for
  ISBNs.

split [<OPTIONS>] folder_with_books
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: terminal

   usage: ebooktools split [-h] [-v] [-q] [--verbose] [-d] [-r]
                           [--log-level {debug,info,warning,error}]
                           [--log-format {console,simple,only_msg}]
                           [--ome EXTENSION] [-s START_NUMBER] [-f PATTERN]
                           [--fpf FILES_PER_FOLDER] [-o PATH]
                           folder_with_books

Description
"""""""""""
Splits the supplied ebook files (and the accompanying metadata files if
present) into folders with consecutive names that each contain the specified
number of files.

Global options
""""""""""""""
In particular, the following global options are especially important for the
``split`` subcommand:

* ``-d``, ``--dry-run`` found in the `General control flags`_ section

* ``-r``, ``--reverse`` found in the `Miscellaneous options`_ section

* ``--ome``, ``--output-metadata-extension`` found in the
  `Options related to the input and output files`_ section

Local options
"""""""""""""
* ``-s <value>``, ``--start-number <value>``; config variable ``start_number``;
  default value ``0``

  The number of the first folder. 

* ``-f <value>``, ``--folder-pattern <value>``; config variable
  ``folder_pattern``; default value ``%05d000``
  
  The print format string that specifies the pattern with which new folders
  will be created. By default it creates folders like
  ``00000000, 00001000, 00002000, ...``.
  
* ``--fpf <value>``, ``--files-per-folder <value>``; config variable 
  ``files_per_folder``; default value ``1000``

  How many files should be moved to each folder.
  
Input and output arguments
""""""""""""""""""""""""""
* ``input_file``; no config variable; **required**
  
  Folder with books which will be recursively scanned for files.

* ``-o <value>``, ``--output-folder <value>``; config variable
  ``output_folder``; **default value is the current working directory** (check
  with ``pwd``)
  
  The output folder in which all the new consecutively named folders will be
  created.
  
Examples
========
Example 1: edit the main config file
------------------------------------
To edit the **main** config file with PyCharm:

.. code-block:: terminal

   $ ebooktools edit -a charm main
   
A tab with the main config file will be opened in PyCharm's Editor window.

Example 2: reset the main config file
-------------------------------------
To reset the **main** config file with factory settings:

.. code-block:: terminal
   
   $ ebooktools edit -r main

Example 3: convert a pdf file to text **with** OCR
--------------------------------------------------
To convert a pdf file (``pdf_to_convert.pdf``) to text
(``converted.txt``) **with OCR**:

.. code-block:: terminal

   $ ebooktools convert --ocr always -o converted.txt pdf_to_convert.pdf
   
By setting ``--ocr`` to ``always``, the pdf file will first be OCRed before
trying the simple conversion tools (``pdftotext`` or calibre's 
``ebook-convert`` if the former command is not found).

Example 4: convert a pdf file to text **without** OCR
-----------------------------------------------------
To convert a pdf file (``pdf_to_convert.pdf``) to text
(``converted.txt``) **without OCR**:

.. code-block:: terminal

   $ ebooktools convert -o converted.txt pdf_to_convert.pdf
    
If ``pdftotext`` is present, it is used to convert the pdf file to text.
Otherwise, calibre's ``ebook-convert`` is used for the conversion.

Example 5: find ISBNs in a string
---------------------------------
Find ISBNs in the string ``'978-159420172-1 978-1892391810 0000000000 
0123456789 1111111111'``:

.. code-block:: terminal

   $ ebooktools find '978-159420172-1 978-1892391810 0000000000 0123456789 1111111111'

Note the input string is enclosed within single quotes.

**Output:**

.. code-block:: terminal

   INFO     Running py_ebooktools v0.1.0a3
   INFO     Verbose option disabled
   INFO     Extracted ISBNs:
   9781594201721
   9781892391810

The other sequences ``'0000000000 0123456789 1111111111'`` are rejected because
they are matched with the regular expression ``isbn_blacklist_regex``.

By default, the extracted ISBNs are separated by newlines, ``\n``.

Example 6: find ISBNs in a pdf file
-----------------------------------
Find ISBNs in a pdf file:

.. code-block:: terminal

   $ ebooktools find pdf_file.pdf
   
**Output:**

.. code-block:: terminal

   INFO     Running py_ebooktools v0.1.0a3
   INFO     Verbose option disabled
   INFO     Searching file 'pdf_file.pdf' for ISBN numbers...
   INFO     Trying to decompress 'pdf_file.pdf' and recursively scan the contents
   INFO     Error extracting the file (probably not an archive)! Removing tmp dir...
   INFO     Converting ebook to text format...
   INFO     The file looks like a pdf, using pdftotext to extract the text
   INFO     Reordering input file (if possible), read first 400 lines normally, then read last 50 lines in reverse and then read the rest
   INFO     Extracted ISBNs:
   9781594201721
   1000100111

The first extracted ISBN is the correct one. The last sequence ``1000100111``
is not an ISBN even though it is a technically valid but wrong ISBN that the
regular expression ``isbn_blacklist_regex`` didn't catch.

Example 7: split a folder
-------------------------
We have a folder containing four ebooks and their corresponding metadata:

.. image:: https://raw.githubusercontent.com/raul23/images/master/py_ebooktools/v0.1.0a3/example_07_content_folder_with_books.png
   :target: https://raw.githubusercontent.com/raul23/images/master/py_ebooktools/v0.1.0a3/example_07_content_folder_with_books.png
   :align: left
   :alt: Example 07: content of folder_with_books/

Note that two ebook files don't have metadata files associated with them.

|

We want to split these ebook files into folders containing two files each and
their numbering should start at 1:

.. code-block:: terminal
   
   $ ebooktools split -s 1 --fpf 2 ~/folder_with_books/ -o ~/output_folder/

**Output:** content of ``output_folder``

.. image:: https://raw.githubusercontent.com/raul23/images/master/py_ebooktools/v0.1.0a3/example_07_content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/py_ebooktools/v0.1.0a3/example_07_content_output_folder.png
   :align: left
   :alt: Example 07: content of output_folder/

|

Note that the metadata folders contain only one file each as expected.

`:warning:`
 
   In order to avoid data loss, use the option ``dry-run`` to test that
   ``split`` would do what you expect it to do, as explained in the
   `Security and safety`_ section.

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

Limitations
===========
Same limitations as for `ebook-tools`_ apply to this project too:

  * Automatic organization can be slow - all the scripts are synchronous
    and single-threaded and metadata lookup by ISBN is not done
    concurrently. This is intentional so that the execution can be easily
    traced and so that the online services are not hammered by requests.
    If you want to optimize the performance, run multiple copies of the
    script **on different folders**.
    
  * The default setting for ``ISBN_METADATA_FETCH_ORDER`` includes two
    non-standard metadata sources: Goodreads and WorldCat xISBN. For
    best results, install the plugins (`1`_, `2`_) for them in calibre and
    fine-tune the settings for metadata sources in the calibre GUI.


Roadmap
=======
- Port all of `ebook-tools`_ shell scripts into Python

  - ``organize-ebooks.sh``: **working on it**
  - ``interactive-organizer.sh``: **not started yet**
  - ``find-isbns.sh``: **done**, *see* `find_isbns.py`_
  - ``convert-to-txt.sh``: **done**, *see* `convert_to_txt.py`_
  - ``rename-calibre-library.sh``: **working on it**
  - ``split-into-folders.sh``: **done**, *see* `split_into_folders.py`_
- Test on linux
- Add tests on `Travis CI`_
- Eventually add documentation on `Read the Docs`_

Security and safety
===================
Important security and safety tips from the `ebook-tools documentation`_:

  Please keep in mind that this is beta-quality software. To avoid data loss, make
  sure that you have a backup of any files you want to organize. You may also want
  to run the scripts with the ``--dry-run`` or ``--symlink-only`` option the first
  time to make sure that they would do what you expect them to do.
  
  Also keep in mind that these shell scripts parse and extract complex arbitrary
  media and archive files and pass them to other external programs written in
  memory-unsafe languages. This is not very safe and specially-crafted malicious ebook
  files can probably compromise your system when you use these scripts. If you are
  cautious and want to organize untrusted or unknown ebook files, use something like
  `QubesOS`_ or at least do it in a separate VM/jail/container/etc.

**NOTE:** the subcommands that you can use ``--dry-run`` or ``--symlink-only`` are:

* `interact`_
* `organize`_
* `rename`_
* `split`_: only ``dry-run`` is applicable

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
.. [OWIS] https://github.com/na--/ebook-tools#options-related-to-extracting-and-searching-for-non-isbn-metadata
.. [RFFG] https://github.com/na--/ebook-tools#options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. [TI] https://github.com/na--/ebook-tools#options-related-to-extracting-and-searching-for-non-isbn-metadata
.. [TML] https://github.com/na--/ebook-tools#options-related-to-extracting-and-searching-for-non-isbn-metadata

* `ebook-tools`_: This is the **original** Shell scripts I ported to Python. I referenced
  its documentation a lot here since I tried to follow the shell script options as much
  as possible (such as their names) so that if you used the shell scripts, you will
  easily know how to run the corresponding Python script.

Credits
=======
* Special thanks to `na--`_, the developer of `ebook-tools`_, for having made these very
  useful tools. I learned a lot (specially ``bash``) while porting them to Python.

License
=======
This program is licensed under the GNU General Public License v3.0. For more
details see the `LICENSE`_ file in the repository.

.. URLs
.. _1: https://www.mobileread.com/forums/showthread.php?t=130638
.. _2: https://github.com/na--/calibre-worldcat-xisbn-metadata-plugin
.. _calibre: https://calibre-ebook.com/
.. _catdoc: http://www.wagner.pp.ru/~vitus/software/catdoc/
.. _conda: https://docs.conda.io/en/latest/
.. _convert_to_txt.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/convert_to_txt.py
.. _default_config.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/configs/default_config.py
.. _default_logging.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/configs/default_logging.py
.. _documentation for ebook-tools: https://github.com/na--/ebook-tools#searching-for-isbns-in-files
.. _DjVuLibre: http://djvu.sourceforge.net/
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _ebook-tools documentation: https://github.com/na--/ebook-tools#security-and-safety
.. _ebooktools.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/scripts/ebooktools.py
.. _find_isbns.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/find_isbns.py
.. _Goodreads: https://www.mobileread.com/forums/showthread.php?t=130638
.. _lib.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/lib.py
.. _LICENSE: https://github.com/raul23/py-ebooktools/blob/master/LICENSE
.. _na--: https://github.com/na--
.. _p7zip: https://sourceforge.net/projects/p7zip/
.. _plugins: https://plugins.calibre-ebook.com/
.. _poppler: https://poppler.freedesktop.org/
.. _QubesOS: https://www.qubes-os.org/
.. _Read the Docs: https://readthedocs.org/
.. _shell scripts: https://github.com/na--/ebook-tools#script-usage-and-options
.. _split_into_folders.py: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/split_into_folders.py
.. _Tesseract: https://github.com/tesseract-ocr/tesseract
.. _Travis CI: https://travis-ci.com/
.. _valid ISBNs: https://en.wikipedia.org/wiki/International_Standard_Book_Number#Check_digits
.. _venv: https://docs.python.org/3/library/venv.html#module-venv
.. _WorldCat xISBN: https://github.com/na--/calibre-worldcat-xisbn-metadata-plugin

.. URLs: default values
.. _default_config.py#L59: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/configs/default_config.py#L59
.. _default_config.py#L62: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/configs/default_config.py#L62
.. _default_config.py#L80: https://github.com/raul23/py-ebooktools/blob/master/py_ebooktools/configs/default_config.py#L80
.. _search_file_for_isbns(): https://github.com/raul23/py-ebooktools/blob/0a3f7ceb5fb3e77a480a489d1a43d3346521e685/py_ebooktools/lib.py#L555

.. URLs: local
.. _below: #script-usage-and-options
.. _convert: #convert-options-input-file
.. _edit: #edit-options-main-log
.. _find: #find-options-input-data
.. _General control flags: #general-control-flags
.. _General options: #general-options
.. _interact: #security-and-safety
.. _Miscellaneous options: #miscellaneous-options
.. _OCR ones: #options-for-ocr
.. _Options related to the input and output files: #options-related-to-the-input-and-output-files
.. _organize: #security-and-safety
.. _related to extracting ISBNs from files: #options-related-to-extracting-isbns-from-files-and-finding-metadata-by-isbn
.. _rename: #security-and-safety
.. _Script usage, subcommands and options: #script-usage-subcommands-and-options
.. _Security and safety: #security-and-safety
.. _split: #split-options-folder-with-books
.. _subcommands: #script-usage-subcommands-and-options
.. _Usage, options and configuration: #usage-options-and-configuration
.. _-h, --help: #general-control-flags
.. _-v, --verbose: #general-control-flags
.. _-q, --quiet: #general-control-flags
.. _--verbose: #general-control-flags
.. _--log-level: #miscellaneous-options
.. _--log-format: #miscellaneous-options

.. TODOs
.. explain log-level and log-format choices of values
.. check ocr-command option (including description)
.. add more to description (+ examples of output filenames) for the output-filename-template option
.. add more to description for isbn-regex option
.. IMPORTANT: change internal url for subcommands in #security-and-safety
