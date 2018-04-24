import ipdb
import argparse
import os

from lib import search_file_for_isbns


# Environment variables
CORRUPTION_CHECK_ONLY = False
ORGANIZE_WITHOUT_ISBN = False


def check_file_for_corruption():
    return ''


def skip_file(file_path, reason):
    raise NotImplementedError('skip_file is not implemented!')


# Arguments: path, reason (optional)
def organize_by_filename_and_meta(file_path, reason=''):
    raise NotImplementedError('organize_by_filename_and_meta is not implemented!')


def organize_by_isbns(file_path, isbns):
    pass


def organize_file(file_path):
    file_err = check_file_for_corruption()
    if file_err:
        # TODO: decho
        print('File {} is corrupt with error {}'.format(file_path, file_err))
    elif CORRUPTION_CHECK_ONLY:
        # TODO: decho
        print('We are only checking for corruption, do not continue organising...')
        skip_file(file_path, 'File appears OK')
    else:
        # TODO: decho
        print('File passed the corruption test, looking for ISBNs...')
        isbns = search_file_for_isbns(file_path)
        if isbns:
            print('Organizing {} by ISBNs {}!'.format(file_path, isbns))
            organize_by_isbns(file_path, isbns)
        elif ORGANIZE_WITHOUT_ISBN:
            print('No ISBNs found for {}, organizing by filename and metadata...'.format(file_path))
            organize_by_filename_and_meta(file_path, 'No ISBNs found')
        else:
            skip_file(file_path, 'No ISBNs found; Non-ISBN organization disabled')
    # TODO: decho
    print('=====================================================')


if __name__ == '__main__':
    ebooks_directories = [os.path.expanduser('~/test/ebooks/folderB')]
    ipdb.set_trace()
    for fpath in ebooks_directories:
        print('Recursively scanning {} for files'.format(fpath))
        # TODO: They make use of sorting flags for walking through the files [FILE_SORT_FLAGS]
        # ref.: https://github.com/na--/ebook-tools/blob/0586661ee6f483df2c084d329230c6e75b645c0b/organize-ebooks.sh#L313
        for path, dirs, files in os.walk(fpath):
            for file in files:
                # TODO: add debug_prefixer
                organize_file(file)