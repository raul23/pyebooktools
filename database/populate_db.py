"""
Populate library database
"""
import os
import sys
import ipdb
try:
    from utils import database
except ImportError:
    sys.path.insert(0, os.path.expanduser("../"))
    from utils import database


SOURCE_PATH = '~/test/ebooks'
DOC_EXTENSIONS = ['.pdf', '.epub', '.djvu']
DB_FILENAME = 'library.sqlite'


if __name__ == '__main__':
    # Expand ~ in path
    SOURCE_PATH = os.path.expanduser(SOURCE_PATH)

    dict_docs = {}
    ipdb.set_trace()
    for (dir_path, dir_names, filenames) in os.walk(SOURCE_PATH):
        for f in filenames:
            ext = os.path.splitext(f)[1]
            if ext in DOC_EXTENSIONS:
                dict_docs.setdefault(ext, [])
                dict_docs[ext].append(os.path.join(dir_path, f))

    ipdb.set_trace()

    db = database.SqliteDatabase(DB_FILENAME)
    with db.conn:
        for k, v in dict_docs.items():
            values = list(zip([None]*len(v), v))
            db.insert_many('books', values)

