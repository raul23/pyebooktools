========
EXAMPLES
========
Examples to show how to execute the different `subcommands`_
from the ``ebooktools.py`` script.

`:star:`

  Sometimes, it might be more convenient to edit the configuration file
  ``config.py`` instead of building a long command in the terminal with all the
  options for a given subcommand (e.g. ``organize``).

  Run the following command to edit this configuration file:
  
  
  .. code-block:: terminal

     $ ebooktools edit main
     
  The ``config.py`` file will be opened by the default source code editor
  associated with this type of file and then you can modify the right
  configuration variables for the given subcommand.
  
  You can then run the given subcommand and all the updated options in the
  configuration file will be used. However, command-line parameters supersede
  variables defined in the configuration file.
   
  See `edit`_ for more info about this subcommand.

.. contents:: **Contents**
   :depth: 2
   :local:
   :backlinks: top

``convert`` examples
====================
Convert a pdf file to text **with** OCR
---------------------------------------
.. code-block:: terminal

   $ ebooktools convert --ocr always pdf_to_convert.pdf -o converted.txt
   
By setting ``--ocr`` to ``always``, the pdf file will be first OCRed before
trying the simple conversion tools (``pdftotext`` or calibre's
``ebook-convert`` if the former command is not found).

.. code-block:: terminal

   Running pyebooktools v0.1.0a3
   Verbose option disabled
   OCR=always, first try OCR then conversion
   Will run OCR on file 'pdf_to_convert.pdf' with 1 page...
   OCR successful!

Convert a pdf file to text **without** OCR
------------------------------------------
.. code-block:: terminal

   $ ebooktools convert pdf_to_convert.pdf -o converted.txt
    
If ``pdftotext`` is present, it is used to convert the pdf file to text.
Otherwise, calibre's ``ebook-convert`` is used for the conversion.

.. code-block:: terminal

   Running pyebooktools v0.1.0a3
   Verbose option disabled
   OCR=false, try only conversion...
   Conversion successful!

``edit`` examples
=================
The two config files that can be edited are the `main`_ and `logging`_ config
files. We will only focus in the main config file because it is the most
important one since it contains `all the options`_ for the ``ebooktools.py``
script.

Edit the main config file
-------------------------
To edit the **main** config file with **PyCharm**:

.. code-block:: terminal

   $ ebooktools edit -a charm main

|

A tab with the main config file will be opened in PyCharm's Editor window:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/edit/pycharm_tab.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/edit/pycharm_tab.png
   :align: left
   :alt: Example: opened tab with config file in PyCharm

Reset the main config file
--------------------------
To reset the **main** config file with factory settings as defined in the
`default_config.py`_:

.. code-block:: terminal
   
   $ ebooktools edit -r main

``find`` examples
=================

Find ISBNs in a string
----------------------
Find ISBNs in the string ``'978-159420172-1 978-1892391810 0000000000 
0123456789 1111111111'``:

.. code-block:: terminal

   $ ebooktools find '978-159420172-1 978-1892391810 0000000000 0123456789 1111111111'

The input string can be enclosed within single or double quotes.

**Output:**

.. code-block:: terminal

   Running pyebooktools v0.1.0a3
   Verbose option disabled
   Extracted ISBNs:
   9781594201721
   9781892391810

The other sequences ``'0000000000 0123456789 1111111111'`` are rejected because
they are matched with the regular expression `isbn_blacklist_regex`_.

By `default <./README.rst#specific-options-for-finding-isbns>`__, the extracted 
ISBNs are separated by newlines, ``\n``.

`:information_source:`

  If you want to search ISBNs in a **multiple-lines string**, e.g. you copied
  many pages from a document, you must follow the ``find`` subcommand with a
  backslash ``\`` and enclose the string within **double quotes**, like so:
  
  .. code-block:: terminal

     $ ebooktools find \
     "
     978-159420172-1
     
     blablabla
     blablabla
     blablabla
     
     978-1892391810
     0000000000 0123456789 
     
     blablabla
     blablabla
     blablabla
     
     1111111111
     blablabla
     blablabla
     "

Find ISBNs in a pdf file
------------------------
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

The search for ISBNs starts in the first pages of the document to increase the
likelihood that the first extracted ISBN is the correct one. Then the last
pages are analyzed in reverse. Finally, the rest of the pages are searched.

Thus, in this example, the first extracted ISBN is the correct one
associated with the book since it was found in the first page. 

The last sequence ``1000100111`` was found in the middle of the document and is
not an ISBN even though it is a technically valid but wrong ISBN that the
regular expression `isbn_blacklist_regex`_ didn't catch. Maybe it is a binary
sequence that is part of a problem in a book about digital system.

``organize`` examples
=====================
You can use ``organize`` to check ebooks for corruption without
organizing them by using the `--corruption-check-only`_ flag. See the
`Check ebooks for corruption only`_ example for more details.

The following examples show how to organize ebooks depending on different 
cases:

- `Organize ebooks with only output_folder`_: ignore ebooks without ISBNs
- `Organize ebooks with output_folder_corrupt`_: organize ebooks and check
  for corruption (e.g. zero-filled files or broken ``.pdf`` files)
- `Organize ebooks with output_folder_pamphlets`_: e.g. small pdfs or
  saved webpages
- `Organize ebooks with output_folder_uncertain`_: organize ebooks that
  don't have any ISBN in them.

`:information_source:`

  You can also combine all these cases by using all of the `output folders`_
  along with the `--owi`_ flag in the command-line when calling the 
  `organize`_ subcommand.
  
  Or better you can also do it through the config file ``config.py`` by running
  the following command:
  
  
  .. code-block:: terminal

     $ ebooktools edit main
     
  The ``config.py`` file will be opened by the default source code editor
  associated with this type of file and then you can modify the right
  configuration variables.
  
  Then run the ``organize`` subcommand and the updated options in the
  configuration file will be used.
   
  See `edit`_ for more info about this subcommand.

Check ebooks for corruption only
--------------------------------
**TODO**

Organize ebooks with only ``output_folder``
-------------------------------------------
We want to organize the following ebook files:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder/content_folder_to_organize.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder/content_folder_to_organize.png
   :align: left
   :alt: Example: content of ``folder_to_organize``

|

This is the command to organize these ebooks:

.. code-block:: terminal

   $ ebooktools organize ~/folder_to_organize/ -o ~/output_folder

**Output:**

.. code-block:: terminal

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder/output_terminal.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder/output_terminal.png
   :align: left
   :alt: Example: output terminal

|

Content of ``output_folder``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder/content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder/content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``

Organize ebooks with ``output_folder_corrupt``
----------------------------------------------
We want to organize the following ebook files, one of which is corrupted:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/content_folder_to_organize.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/content_folder_to_organize.png
   :align: left
   :alt: Example: content of ``folder_to_organize``

|

This is the command to organize these ebooks as wanted:

.. code-block:: terminal

   $ ebooktools organize --owi ~/folder_to_organize/ -o ~/output_folder --ofu ~/output_folder_corrupt/ 

where 

- `--owi`_ is a flag to enable the organization of ebooks without ISBNs
- `output_folder`_ will contain all the *renamed* ebooks for which an ISBN was
  found in it
- `output_folder_corrupt`_ will contain any corrupted ebook (e.g. zero-filled 
  files, corrupt archives or broken .pdf files)

**Output:**

.. code-block:: terminal

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/output_terminal.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/output_terminal.png
   :align: left
   :alt: Example: output terminal

|

Content of ``output_folder``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``
|

Content of ``output_folder_corrupt``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/content_folder_corrupt.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_corrupt/content_folder_corrupt.png
   :align: left
   :alt: Example: content of ``output_folder_corrupt``

|

`:information_source:`

  Along each corrupted file, a metadata file is saved containing information
  about the corruption reason and the ebook's old file path.

Organize ebooks with ``output_folder_pamphlets``
------------------------------------------------
We want to organize the following ebook files, some of which are pamphlets:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/content_folder_to_organize.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/content_folder_to_organize.png
   :align: left
   :alt: Example: content of ``folder_to_organize``

|

This is the command to organize these ebooks as wanted:

.. code-block:: terminal

   $ ebooktools organize --owi ~/folder_to_organize/ -o ~/output_folder --ofu ~/output_folder_pamphlets/ 

where 

- `--owi`_ is a flag to enable the organization of ebooks without ISBNs
- `output_folder`_ will contain all the *renamed* ebooks for which an ISBN was
  found in it
- `output_folder_pamphlets`_ will contain all the pamphlets-like documents

**Output:**

.. code-block:: terminal

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/output_terminal.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/output_terminal.png
   :align: left
   :alt: Example: output terminal

|

Content of ``output_folder``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``
|

Content of ``output_folder_pamphlets``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/content_folder_pamphlets.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_pamphlets/content_folder_pamphlets.png
   :align: left
   :alt: Example: content of ``output_folder_pamphlets``

|

`:information_source:`

  If no ISBN was found for a non-pdf file and the file size is less than
  `pamphlet_max_filesize_kib`_, then it is considered as a pamphlet.

Organize ebooks with ``output_folder_uncertain``
------------------------------------------------
We want to organize the following ebook files, some of which do not contain any
ISBNs:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/content_folder_to_organize.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/content_folder_to_organize.png
   :align: left
   :alt: Example: content of ``folder_to_organize``

|

This is the command to organize these ebooks as wanted:

.. code-block:: terminal

   $ ebooktools organize --owi ~/folder_to_organize/ -o ~/output_folder --ofu ~/output_folder_uncertain/ 

where 

- `--owi`_ is a flag to enable the organization of ebooks without ISBNs
- `output_folder`_ will contain all the *renamed* ebooks for which an ISBN was
  found in it
- `output_folder_uncertain`_ will contain all the *renamed* ebooks for which no
  ISBNs could be found in them

**Output:**

.. code-block:: terminal

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/output_terminal.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/output_terminal.png
   :align: left
   :alt: Example: output terminal

|

Content of ``output_folder``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``
|

Content of ``output_folder_uncertain``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/content_folder_uncertain.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/organize/output_folder_uncertain/content_folder_uncertain.png
   :align: left
   :alt: Example: content of ``output_folder_uncertain``

|

`:information_source:`

  For those ebooks for which no ISBNs could be found in them, the
  ``ebooktools.py`` script takes the following steps to organize them:
  
  1. Use calibre's ``ebook-meta`` to extract the author and title metadata from
     the ebook file
  2. Search the online metadata sources (``Goodreads,Amazon.com,Google``) by the 
     extracted author & title and just by title
  3. If there is no useful metadata or nothing is found online, the script will
     try to use the filename for searching.
  
  [OWI]_

``rename`` examples
===================

Rename book files from a calibre library folder
-----------------------------------------------
Rename book files from a calibre library folder and save their symlinks along
with their copied ``metadata.opf`` files in a separate folder:

.. code-block:: terminal

   $ ebooktools rename --sm opfcopy --sl ~/calibre_folder/ -o ~/output_folder/
   
**Output:**

.. code-block:: terminal

   Running pyebooktools v0.1.0a3
   Verbose option disabled
   Files sorted in asc
   Parsing metadata for 'Title1 - Author1.pdf'...
   Saving book file and metadata...
   Parsing metadata for 'Title2 - Author2.epub'...
   Saving book file and metadata...
   Parsing metadata for 'Title3 - Author3.pdf'...
   Saving book file and metadata...
   Parsing metadata for 'Title4 - Author4.epub'...
   Saving book file and metadata...

|

Content of ``output_folder``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/rename/content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/rename/content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``

|

`:information_source:`

  * The book files are renamed based on the content of their associated
    ``metadata.opf`` files and the new filenames follow the
    `output_filename_template`_ format.
  * The ``metadata.opf`` files are copied with the ``meta`` extension
    (`default <./README.rst#output-metadata-extension-label>`__) beside the
    symlinks to the book files.

``split`` examples
==================

Split a folder
--------------
We have a folder containing four ebooks and the metadata file for two of 
them:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/split/content_folder_with_books.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/split/content_folder_with_books.png
   :align: left
   :alt: Example: content of ``folder_with_books``

|

We want to split these ebook files into folders containing two files each and
their numbering should start at 1:

.. code-block:: terminal
   
   $ ebooktools split -s 1 --fpf 2 ~/folder_with_books/ -o ~/output_folder/

**Output:** content of ``output_folder``

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/split/content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/split/content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``

|

Note that the metadata folders contain only one file each as expected.

`:warning:`
 
   In order to avoid data loss, use the ``--dry-run`` option to test that
   ``split`` would do what you expect it to do, as explained in the
   `Security and safety`_ section.
   
References
==========
.. [OWI] https://github.com/raul23/pyebooktools#organize-without-isbn-label
   
.. URLs
.. _all the options: ../README.rst#usage-options-and-configuration
.. _--corruption-check-only: ../README.rst#specific-options-for-organizing-files
.. _default_config.py: ../pyebooktools/configs/default_config.py
.. _edit: ../README.rst#edit-options-main-log
.. _isbn_blacklist_regex: ../README.rst#isbn-blacklist-regex-label
.. _logging: ../pyebooktools/configs/default_logging.py
.. _main: ../pyebooktools/configs/default_config.py
.. _organize: ../README.rst#organize-options-folder_to_organize
.. _output_filename_template: ../README.rst#options-related-to-the-input-and-output-files
.. _output_folder: ../README.rst#organize-output-folder-label
.. _output_folder_corrupt: ../README.rst#output-folder-corrupt-label
.. _output_folder_pamphlets: ../README.rst#output-folder-pamphlets-label
.. _output_folder_uncertain: ../README.rst#output-folder-uncertain-label
.. _output folders: ../README.rst#input-and-output-options-for-organizing-files
.. _--owi: ../README.rst#organize-without-isbn-label
.. _pamphlet_max_filesize_kib: ../README.rst#pamphlet-max-filesize-kib-label
.. _Security and safety: ../README.rst#security-and-safety
.. _subcommands: ../README.rst#script-usage-subcommands-and-options

.. Local URLs
.. _Check ebooks for corruption only: #check-ebooks-for-corruption-only
.. _Organize ebooks with only output_folder: #organize-ebooks-with-only-output_folder
.. _Organize ebooks with output_folder_corrupt: #organize-ebooks-with-output-folder-corrupt
.. _Organize ebooks with output_folder_pamphlets: #organize-ebooks-with-output-folder-pamphlets
.. _Organize ebooks with output_folder_uncertain: #organize-ebooks-with-output-folder-uncertain
