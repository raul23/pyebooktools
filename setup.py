"""setup.py file for the package ``pyebooktools``.

The PyPi project name is ``python-ebook-tools`` and the package name is
``pyebooktools``.

"""

import os
import sys
from setuptools import find_packages, setup

from pyebooktools import __version__, __test_version__


# Choose the correct version based on script's arg
if len(sys.argv) > 1 and sys.argv[1] == "testing":
    VERSION = __test_version__
    # Remove "testing" from args so setup doesn't process "testing" as a cmd
    sys.argv.remove("testing")
else:
    VERSION = __version__

# Directory of this file
dirpath = os.path.abspath(os.path.dirname(__file__))

# The text of the README file (used on PyPI)
with open(os.path.join(dirpath, "README.rst"), encoding="utf-8") as f:
    README = f.read()

# The text of the requirements.txt file
# TODO: empty for now
with open(os.path.join(dirpath, "requirements.txt")) as f:
    REQUIREMENTS = f.read().splitlines()


setup(name='python-ebook-tools',
      version=VERSION,
      description='''Program for organizing and managing ebook collections. It 
      is a Python port of ebook-tools (shell scripts).''',
      long_description=README,
      long_description_content_type='text/x-rst',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
      ],
      keywords='ebook-manager calibre script',
      url='https://github.com/raul23/python-ebook-tools',
      author='Raul C.',
      author_email='rchfe23@gmail.com',
      license='GPLv3',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=REQUIREMENTS,
      entry_points={
        'console_scripts': ['ebooktools=pyebooktools.scripts.ebooktools:main']
      },
      project_urls={  # Optional
          'Bug Reports': 'https://github.com/raul23/python-ebook-tools/issues',
          # TODO: 'Documentation': 'https://?.readthedocs.io/',
          'Source': 'https://github.com/raul23/python-ebook-tools',
      },
      zip_safe=False)