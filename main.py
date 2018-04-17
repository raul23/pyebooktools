"""
Search for line containing
- ISBN + numbers
- Library of Congress Catalog Card Number: numbers (Old books)
"""
import PyPDF2
# TODO: requests is an external module (try with urllib/2)


if __name__ == '__main__':
    pdfFileObj = open('.pdf', 'rb')
