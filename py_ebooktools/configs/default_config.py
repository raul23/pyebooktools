"""Options for the script ebooktools

ebooktools is a Python port of the shell scripts developed by na-- for
organizing and managing ebook collections. See
https://github.com/na--/ebook-tools.

The options are described in full detail in the project's README @
https://github.com/raul23/python-ebook-tools

IMPORTANT: these options can also be passed to the script ebooktools via
command-line parameters (Run `ebooktools -h` for a detailed list of the options).
Also, command-line parameters supersede the variables defined in this
configuration file. Most parameters are not required and if nothing is
specified, the default value will be used.

The options are separated based on sections:
1. General options
  1.1 General control flags
  1.2 Options related to extracting ISBNs from files and finding metadata by ISBN
  1.3 Options for OCR
  1.4 Options related to extracting and searching for non-ISBN metadata
  1.5 Options related to the input and output files
  1.6 Miscellaneous options
2. Script options
  2.1 edit-config-files
  2.2 organize-ebooks
    2.2.1 Specific options for organizing files
    2.2.2 Output options
  2.3 interactive-organizer
  2.4 find-isbns
  2.5 convert-to-txt
  2.6 rename-calibre-library
  2.7 split-into-folders
"""
import os

# ==================
# 1. General options
# ==================
# All of these options are part of the common library and may affect some or
# all of the scripts.

# 1.1 General control flags
# =========================
quiet = False
verbose = False
dry_run = False
# symlink_only = False
# keep_metadata = False
logging_level = 'info'
logging_formatter = 'only_msg'

# 1.2 Options related to extracting ISBNs from files and finding metadata by ISBN
# ===============================================================================
# isbn_regex = ?
# isbn_blacklist_regex = '^(0123456789|([0-9xX])\2{9})$'
# isbn_direct_grep_files = '^text/(plain|xml|html)$'
# isbn_ignored_files = ?
# isbn_grep_reorder_files = True
# isbn_grep_rf_scan_first = 400
# isbn_grep_rf_reverse = 50
# reorder-files-for-grep = (isbn_grep_reorder_files, isbn_grep_rf_scan_first, isbn_grep_rf_reverse
# NOTE: If you use Calibre versions that are older than 2.84, it's required to
# manually set the following option to an empty string.
# metadata_fetch_order = ['Goodreads', 'Amazon.com', 'Google', 'ISBNDB', 'WorldCat xISBN', 'OZON.ru']

# 1.3 Options for OCR
# ===================
# ocr_enabled = False
# ocr_only_first_last_pages = (7, 3)
# ocr_command = 'tesseract_wrapper'

# 1.4 Options related to extracting and searching for non-ISBN metadata
# =====================================================================
# token_min_length = 3
# tokens_to_ignore = ?
# organize_without_isbn_sources = ['Goodreads' ,'Amazon.com', 'Google']

# 1.5 Options related to the input and output files
# =================================================
output_filename_template = "${d[AUTHORS]// & /, } - ${d[SERIES]:+[${d[SERIES]}] " \
                           "- }${d[TITLE]/:/ -}${d[PUBLISHED]:+ (${d[PUBLISHED]%%-*})}" \
                           "${d[ISBN]:+ [${d[ISBN]}]}.${d[EXT]}"
# If keep_metadata is enabled, this is the extension of the additional
# metadata file that is saved next to each newly renamed file.
output_metadata_extension = 'meta'

# 1.6 Miscellaneous options
# =========================
# file_sort_flags = []
file_sort_reverse = False
# debug_prefix_length = 40

# =================
# 2. Script options
# =================

# 2.1 edit-config-files
# =====================
# Name of the application to use for editing the config file.
# If no name is given, then the default application for opening this type of
# file will be used.
app = None

# 2.2 organize-ebooks
# ===================
# 2.2.1 Specific options for organizing files
# -------------------------------------------
# corruption_check_only = False
# tested_archive_extensions = '^(7z|bz2|chm|arj|cab|gz|tgz|gzip|zip|rar|xz|tar|epub|docx|odt|ods|cbr|cbz|maff|iso)$'
# organize_without_isbn = False
# without_isbn_ignore = ?
# pamphlet_included_files = '\.(png|jpg|jpeg|gif|bmp|svg|csv|pptx?)$'
# pamphlet_excluded_files = '\.(chm|epub|cbr|cbz|mobi|lit|pdb)$'
# pamphlet_max_pdf_pages = 50
# pamphlet_max_filesize_kb = 250

# 2.2.2 Output options
# --------------------
# output_folder = os.getcwd()
# If organize_without_isbn is enabled, this is the folder to which all ebooks
# that were renamed based on non-ISBN metadata will be moved to.
# output_folder_uncertain = None
# output_folder_corrupt = None
# output_folder_pamphlets = None

# 2.3 interactive-organizer
# =========================
# output_folder = []
# quick_mode = False
# custom_move_base_dir = None
# restore_original_base_dir = None
# diacritic_difference_masking = ?
# match_partial_words = False

# 2.4 find-isbns
# ==============
# Some general options affect this script (especially the ones related to
# extracting ISBNs from files, see above section 1.4).
# isbn_return_separator = "$'\n'"

# 2.5 convert-to-txt
# ==================
# There are no local options, but some of the general options affect this
# script's behavior a lot, especially the OCR ones (see '1.3 Options for OCR').

# 2.6 rename-calibre-library
# ==========================
# output_folder = os.getcwd()
# save_metadata = 'recreate'

# 2.7 split-into-folders
# ======================
output_folder = os.getcwd()
start_number = 0
folder_pattern = '%05d000'
files_per_folder = 1000
