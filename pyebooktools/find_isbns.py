"""Try to find valid ISBNs inside a file or in `stdin` if no file was specified.

Searching for ISBNs in files uses progressively more resource-intensive methods
until some ISBNs are found, see the `documentation`_.

This is a Python port of `find-isbns.sh`_ from `ebook-tools`_ written in Shell
by `na--`_.

References
----------
* `ebook-tools`_

.. URLs

.. external links
.. _documentation: https://github.com/na--/ebook-tools#searching-for-isbns-in-files
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _find-isbns.sh: https://github.com/na--/ebook-tools/blob/master/find-isbns.sh
.. _na--: https://github.com/na--
"""
