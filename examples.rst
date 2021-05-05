========
EXAMPLES
========
Examples to show how to execute the different `subcommands`_
from the ``ebooktools.py`` script.

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
Edit the main config file
-------------------------
To edit the **main** config file with **PyCharm**:

.. code-block:: terminal

   $ ebooktools edit -a charm main

|

A tab with the main config file will be opened in PyCharm's Editor window:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_edit_pycharm_tab.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_edit_pycharm_tab.png
   :align: left
   :alt: Example: opened tab with config file in PyCharm

Reset the main config file
--------------------------
To reset the **main** config file with factory settings:

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

  If you want to search ISBNs in a **multiple-lines string**, e.g. you
  copied many pages from a document, you must follow the ``find``
  subcommand with a backslash ``\`` and enclose the string within
  **double quotes**, like so:
  
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

``organize`` examples
=====================

Organize ebook files with corrupted folder
------------------------------------------

Organize ebook files with pamphlets folder
------------------------------------------

Organize ebook files with uncertain folder
------------------------------------------
We want to organize ebook files, some of which do not contain any ISBNs:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_content_folder_to_organize.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_content_folder_to_organize.png
   :align: left
   :alt: Example: content of ``folder_to_organize``

|

This is the command to organize these books as wanted:

.. code-block:: terminal

   $ ebooktools organize --owi ~/folder_to_organize/ -o ~/output_folder --ofu ~/output_folder_uncertain/ 

where 

- `--owi`_ is to enable the organization of ebook files without ISBNs
- `output_folder`_ will contain all the *renamed* ebook files 
  for which an ISBN was found in it
- `output_folder_uncertain`_ will contain all the *renamed*
  ebook files for which no ISBNs could be found in them

**Output:**

.. code-block:: terminal

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_output_terminal.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_output_terminal.png
   :align: left
   :alt: Example: output terminal

|

Content of ``output_folder``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``
|

Content of ``folder_uncertain``:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_content_folder_uncertain.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_organize_with_uncertain_content_folder_uncertain.png
   :align: left
   :alt: Example: content of ``output_folder_uncertain``

``rename`` examples
===================

Rename book files from calibre library folder
---------------------------------------------
Rename book files from a calibre library folder and save their symlinks
along with their copied ``metadata.opf`` files into an output folder:

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

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_rename_content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_rename_content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``

|

**NOTES:**

* The book files are renamed based on the content of their associated
  ``metadata.opf`` files and the new filenames follow the
  `output_filename_template`_ format.
* The ``metadata.opf`` files are copied with the ``meta`` extension (`default 
  <./README.rst#output-metadata-extension-label>`__) beside the
  symlinks to the book files.

``split`` examples
==================

Split a folder
--------------
We have a folder containing four ebooks and their corresponding metadata:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_split_content_folder_with_books.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_split_content_folder_with_books.png
   :align: left
   :alt: Example: content of ``folder_with_books``

Note that two ebook files don't have metadata files associated with them.

|

We want to split these ebook files into folders containing two files each and
their numbering should start at 1:

.. code-block:: terminal
   
   $ ebooktools split -s 1 --fpf 2 ~/folder_with_books/ -o ~/output_folder/

**Output:** content of ``output_folder``

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_split_content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/examples/example_split_content_output_folder.png
   :align: left
   :alt: Example: content of ``output_folder``

|

Note that the metadata folders contain only one file each as expected.

`:warning:`
 
   In order to avoid data loss, use the ``--dry-run`` option to test that
   ``split`` would do what you expect it to do, as explained in the
   `Security and safety`_ section.
   
.. URLs
.. _isbn_blacklist_regex: ./README.rst#isbn-blacklist-regex-label
.. _output_filename_template: ./README.rst#options-related-to-the-input-and-output-files
.. _output_folder: ./README.rst#organize-output-folder-label
.. _output_folder_uncertain: ./README.rst#output-folder-uncertain-label
.. _--owi: ./README.rst#organize-without-isbn-label
.. _Security and safety: ./README.rst#security-and-safety
.. _subcommands: ./README.rst#script-usage-subcommands-and-options
