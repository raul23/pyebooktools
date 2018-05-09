import os


def file_exists(path):
    """
    Checks if both a file exists and it is a file. Returns True if it is the
    case (can be a file or file symlink).

    ref.: http://stackabuse.com/python-check-if-a-file-or-directory-exists/

    :param path: path to check if it points to a file
    :return bool: True if it file exists and is a file. False otherwise.
    """
    path = os.path.expanduser(path)
    return os.path.isfile(path)
