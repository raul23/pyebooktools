========
EXAMPLES
========
Examples to show how to execute the different subcommands
from the ``ebooktools.py`` script.

.. contents:: **Contents**
   :depth: 2
   :local:
   :backlinks: top

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

   $ ebooktools convert --ocr always pdf_to_convert.pdf -o converted.txt
   
By setting ``--ocr`` to ``always``, the pdf file will first be OCRed before
trying the simple conversion tools (``pdftotext`` or calibre's 
``ebook-convert`` if the former command is not found).

Example 4: convert a pdf file to text **without** OCR
-----------------------------------------------------
To convert a pdf file (``pdf_to_convert.pdf``) to text
(``converted.txt``) **without OCR**:

.. code-block:: terminal

   $ ebooktools convert pdf_to_convert.pdf -o converted.txt
    
If ``pdftotext`` is present, it is used to convert the pdf file to text.
Otherwise, calibre's ``ebook-convert`` is used for the conversion.

Example 5: find ISBNs in a string
---------------------------------
Find ISBNs in the string ``'978-159420172-1 978-1892391810 0000000000 
0123456789 1111111111'``:

.. code-block:: terminal

   $ ebooktools find '978-159420172-1 978-1892391810 0000000000 0123456789 1111111111'

The input string can be enclosed within single or double quotes.

**Output:**

.. code-block:: terminal

   INFO     Running pyebooktools v0.1.0a3
   INFO     Verbose option disabled
   INFO     Extracted ISBNs:
   9781594201721
   9781892391810

The other sequences ``'0000000000 0123456789 1111111111'`` are rejected because
they are matched with the regular expression ``isbn_blacklist_regex``.

By default, the extracted ISBNs are separated by newlines, ``\n``.

`:information_source:`

  If you want to search ISBNs in a **multiple-lines string**, e.g. you
  copied-pasted many pages from a document, you must follow the
  ``find`` subcommand with a backslash ``\`` and enclose the string
  within **double quotes**, like so:
  
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

Example 6: find ISBNs in a pdf file
-----------------------------------
Find ISBNs in a pdf file:

.. code-block:: terminal

   $ ebooktools find pdf_file.pdf
   
**Output:**

.. code-block:: terminal

   INFO     Running pyebooktools v0.1.0a3
   INFO     Verbose option disabled
   INFO     Searching file 'pdf_file.pdf' for ISBN numbers...
   INFO     Extracted ISBNs:
   9783672388737
   1000100111

The search for ISBNs starts in the first pages of the document to increase
the likelihood that the first extracted ISBN is the correct one. Then the
last pages are analyzed in reverse. Finally, the rest of the pages are
searched.

Thus, in this example, the first extracted ISBN is the correct one
associated with the book since it was found in the first page. 

The last sequence ``1000100111`` was found in the middle of the document
and is not an ISBN even though it is a technically valid but wrong ISBN
that the regular expression ``isbn_blacklist_regex`` didn't catch. Maybe
it is a binary sequence that is part of a problem in a book about digital
system. 

Example 7: rename book files from calibre library folder
--------------------------------------------------------
Rename book files from a calibre library folder and save their symlinks
along with their copied ``metadata.opf`` files into an output folder:

.. code-block:: terminal

   $ ebooktools rename --sm opfcopy --sl ~/calibre_folder/ -o ~/output_folder/
   
**Output:**

.. code-block:: terminal

   INFO     Running pyebooktools v0.1.0a3
   INFO     Verbose option disabled
   INFO     Files sorted in asc
   INFO     Parsing metadata for 'Title1 (2017).epub'...
   INFO     Saving book file and metadata...
   INFO     Parsing metadata for 'Title2 - Author1.epub'...
   INFO     Saving book file and metadata...
   INFO     Parsing metadata for 'Title3 - Author2.pdf'...
   INFO     Saving book file and metadata...
   INFO     Parsing metadata for 'Title4 - Author3.pdf'...
   INFO     Saving book file and metadata...

Example 8: split a folder
-------------------------
We have a folder containing four ebooks and their corresponding metadata:

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/v0.1.0a3/example_07_content_folder_with_books.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/v0.1.0a3/example_07_content_folder_with_books.png
   :align: left
   :alt: Example 07: content of folder_with_books/

Note that two ebook files don't have metadata files associated with them.

|

We want to split these ebook files into folders containing two files each and
their numbering should start at 1:

.. code-block:: terminal
   
   $ ebooktools split -s 1 --fpf 2 ~/folder_with_books/ -o ~/output_folder/

**Output:** content of ``output_folder``

.. image:: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/v0.1.0a3/example_07_content_output_folder.png
   :target: https://raw.githubusercontent.com/raul23/images/master/pyebooktools/v0.1.0a3/example_07_content_output_folder.png
   :align: left
   :alt: Example 07: content of output_folder/

|

Note that the metadata folders contain only one file each as expected.

`:warning:`
 
   In order to avoid data loss, use the option ``dry-run`` to test that
   ``split`` would do what you expect it to do, as explained in the
   `Security and safety`_ section.
   
.. URLs
.. _Security and safety: ./README.rst#security-and-safety
