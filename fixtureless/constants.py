import sys
import unicodedata as ud
import string


PY3 = sys.version_info.major == 3
MYSQL = 'mysql'

DEFAULT_CHARFIELD_MAX_LEN = 255
DEFAULT_TEXTFIELD_MAX_LEN = DEFAULT_CHARFIELD_MAX_LEN

CHARFIELD_CHARSET_ASCII = string.ascii_letters + string.digits \
    + string.punctuation + ' '
EMAIL_CHARSET = string.ascii_letters + string.digits

# Make a subset of unicode chars to use for unicode test data.
# Changed from 120779 to 65536 to support narrow python build
# (brew standard for osx)
_MAX_UNICODE = 65536

_UNICODE_CHARSET_CATEGORIES = ['Lu', 'Ll', 'Pc', 'Pi', 'Pf', 'Sm', 'Sc']
if PY3:
    all_unicode = [chr(i) for i in range(_MAX_UNICODE)]
    unicode_letters = [c for c in all_unicode
                       if ud.category(c) in _UNICODE_CHARSET_CATEGORIES]
    unicode_letters.append(' ')
    CHARFIELD_CHARSET_UNICODE = ''.join(unicode_letters)
else:
    all_unicode = [unichr(i) for i in xrange(_MAX_UNICODE)]
    unicode_letters = [c for c in all_unicode
                       if ud.category(c) in _UNICODE_CHARSET_CATEGORIES]
    unicode_letters.append(u' ')
    CHARFIELD_CHARSET_UNICODE = u''.join(unicode_letters)

# see http://docs.python.org/3.3/library/stdtypes.html#numeric-types-int-float-long-complex
INTFIELD_MAX = sys.maxsize
INTFIELD_MIN = -sys.maxsize - 1

# see https://docs.python.org/3.4/library/sys.html#sys.float%5Finfo
FLOATFIELD_MAX = sys.float_info.max
FLOATFIELD_MIN = -sys.float_info.min

# see http://www.postgresql.org/docs/8.2/static/datatype-numeric.html
POSTGRES_INT_MAX = 2147483647
POSTGRES_INT_MIN = -2147483648
POSTGRES_SMALLINT_MAX = 32767
POSTGRES_SMALLINT_MIN = -32768
POSTGRES_BIGINT_MAX = 9223372036854775807
POSTGRES_BIGINT_MIN = -9223372036854775808

BOOLEAN_FIELD_NAME = 'boolean_field'
AUTO_FIELD_NAME = 'auto_field'
# Django does not allow these fields to be "blank" but for the purposes of
# django-fixtureless we need to be able to generate values for these fields.
SPECIAL_FIELDS = (BOOLEAN_FIELD_NAME, AUTO_FIELD_NAME)


