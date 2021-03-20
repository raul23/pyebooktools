=========================
README [Work-In-Progress]
=========================
This project is a Python port of `ebook-tools`_ written in shell by na--.
The Python script `ebooktools`_ is a collection of tools for automated and 
semi-automated organization and management of large ebook collections.

`ebooktools`_ makes use of the following tools:

- **edit**: to edit a configuration file which can either be the main config
  file that contains all the options defined below or the logging config file.
- **split**: to split the supplied ebook files (and the accompanying metadata 
  files if present) into folders with consecutive names that each contain the specified
  number of files.

.. contents:: **Contents**
   :depth: 3
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

.. URLs
.. _`default_config.py`: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/configs/default_config.py
.. _ebook-tools: https://github.com/na--/ebook-tools
.. _ebooktools: https://github.com/raul23/python-ebook-tools/blob/master/pyebooktools/scripts/ebooktools
