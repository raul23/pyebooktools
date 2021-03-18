"""Library that has useful functions for building other ebook management scripts.

This is a Python port of lib.sh from ebook-tools by na--. See
https://github.com/na--/ebook-tools/blob/master/lib.sh
"""
# ==============
# Default values
# ==============
# Options related to the input and output files
OUTPUT_FILENAME_TEMPLATE = "${d[AUTHORS]// & /, } - ${d[SERIES]:+[${d[SERIES]}] " \
                           "- }${d[TITLE]/:/ -}${d[PUBLISHED]:+ (${d[PUBLISHED]%%-*})}" \
                           "${d[ISBN]:+ [${d[ISBN]}]}.${d[EXT]}"
OUTPUT_METADATA_EXTENSION = 'meta'
# Misc options
FILE_SORT_FLAGS = None
