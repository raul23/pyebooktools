"""setup.py file for the package ``py_ebooktools``.

The PyPi project name is ``py-ebooktools`` and the package name is
``py_ebooktools``.

"""

import os
import sys
from setuptools import find_packages, setup

from py_ebooktools import __version__, __test_version__


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
# NOTE: encoding for py3.6 and less, see https://stackoverflow.com/a/49131427
with open(os.path.join(dirpath, "README_pypi.rst"), encoding="utf-8") as f:
    README = f.read()

# The text of the requirements.txt file
# TODO: empty for now
with open(os.path.join(dirpath, "requirements.txt")) as f:
    REQUIREMENTS = f.read().splitlines()


setup(name='py-ebooktools',
      version=VERSION,
      description='''Program for organizing and managing ebook collections. It 
      is a Python port of ebook-tools (shell scripts).''',
      long_description=README,
      long_description_content_type='text/x-rst',
      classifiers=[
        'Development Status :: 3 - Alpha',  # TODO: change version to beta or stable
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
      ],
      keywords='ebook-manager calibre script',
      url='https://github.com/raul23/py-ebooktools',
      author='Raul C.',
      author_email='rchfe23@gmail.com',
      license='GPLv3',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=REQUIREMENTS,
      entry_points={
        'console_scripts': ['ebooktools=py_ebooktools.scripts.ebooktools:main']
      },
      project_urls={  # Optional
          'Bug Reports': 'https://github.com/raul23/py-ebooktools/issues',
          # TODO: 'Documentation': 'https://?.readthedocs.io/',
          'Source': 'https://github.com/raul23/py-ebooktools',
      },
      zip_safe=False)
