from datetime import datetime


def get_re_year():
    # In bash: (19[0-9]|20[0-$(date '+%Y' | cut -b 3)])[0-9]"
    # output: (19[0-9]|20[0-1])[0-9]
    regex = '(19[0-9]|20[0-{}])[0-9]'.format(str(datetime.now())[2])
    return regex


# TODO: test it
def get_without_isbn_ignore():
    re_year = get_re_year()
    regex = ''
    # Periodicals with filenames that contain something like 2010-11, 199010, 2015_7, 20110203:
    regex += '(^|[^0-9]){}[ _\.-]*(0?[1-9]|10|11|12)([0-9][0-9])?($|[^0-9])'.format(re_year)
    # Periodicals with month numbers before the year
    regex += '|(^|[^0-9])([0-9][0-9])?(0?[1-9]|10|11|12)[ _\.-]*{}($|[^0-9])'.format(re_year)
    # Periodicals with months or issues
    regex += '|((^|[^a-z])(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?|mag(azine)?|issue|#[ _\.-]*[0-9]+)+($|[^a-z]))'
    # Periodicals with seasons and years
    regex += '|((spr(ing)?|sum(mer)?|aut(umn)?|win(ter)?|fall)[ _\.-]*{})'.format(re_year)
    regex += '|({}[ _\.-]*(spr(ing)?|sum(mer)?|aut(umn)?|win(ter)?|fall))'.format(re_year)
    # Remove newlines
    # TODO: is it necessary?
    regex = regex.replace('\n', '')
    return regex
