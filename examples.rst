========
EXAMPLES
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

   INFO     Running pyebooktools v0.1.0a3
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

   INFO     Running pyebooktools v0.1.0a3
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
