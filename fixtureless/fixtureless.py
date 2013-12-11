import datetime
import decimal
import math
import random
import string
import sys
import itertools
import unicodedata as ud

from django.db import models
from django.db import connection

PY3 = True
if sys.version_info.major == 2:
    PY3 = False

DEFAULT_CHARFIELD_MAX_LEN = 255
DEFAULT_TEXTFIELD_MAX_LEN = DEFAULT_CHARFIELD_MAX_LEN

CHARFIELD_CHARSET_ASCII = string.ascii_letters + string.digits \
    + string.punctuation + ' '

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



def _val_is_unique(val, field):
    """
    Currently only checks the field's uniqueness, not the model validation.
    """
    if val is None:
        return False

    if not field.unique:
        return True

    field_name = field.name
    return field.model.objects.filter(**{field_name: val}).count() == 0


def _autogen_data_ForeignKey(instance, field):
    klass = field.related.parent_model
    instance = None
    if not field.unique:
        # Try to retrieve the last one
        try:
            instance = klass.objects.order_by('-pk')[0]
        except IndexError:
            instance = None
    if field.unique or instance is None:
        instance = create_instance(klass)
        instance.save()
    return instance


def _autogen_data_OneToOneField(instance, field):
    return _autogen_data_ForeignKey(instance, field)


def _autogen_data_DictionaryField(instance, field):
    return {}


def _autogen_data_DecimalField(instance, field):
    len_int_part = field.max_digits - field.decimal_places
    # Add a scaling factor here to help prevent overflowing the Decimal fields
    # when doing summming, etc. This still won't protect tiny dec fields (1 or
    # 2 digits before the decimal), but should cover most use cases.
    len_int_part = int(math.floor(math.sqrt(len_int_part)))
    max_intval = pow(10, len_int_part) - 2
    int_part = random.randint(-max_intval, max_intval)
    len_fractional_part = random.randint(0, field.decimal_places)
    if len_fractional_part > 0:
        # Turn into a string, and trim off the '0.' from the start.
        fractional_part = str(random.random())[2:len_fractional_part+2]
    else:
        fractional_part = ''
    # Val must be passed into Decimal constructor as a string, otherwise it
    # will be rounded!
    val = decimal.Decimal('{}.{}'.format(int_part, fractional_part))
    return val


def _autogen_data_IPAddressField(instance, field):
    """ Currently only IPv4 fields. """
    num_octets = 4
    octets = [str(random.randint(0, 255)) for n in range(num_octets)]
    return '.'.join(octets)


def _autogen_data_CharField(instance, field):
    # Use a choice if this field has them defined.
    if len(field.choices) > 0:
        return random.choice(field.choices)[0]

    str_len = DEFAULT_CHARFIELD_MAX_LEN
    if field.max_length is not None:
        str_len = random.randint(0, field.max_length)

    val = ''
    for _ in itertools.repeat(None, str_len):
        val += random.choice(CHARFIELD_CHARSET_UNICODE)
    return val


def _autogen_data_TextField(instance, field):
    return _autogen_data_CharField(instance, field)


def _autogen_data_SlugField(instance, field):
    str_len = DEFAULT_CHARFIELD_MAX_LEN
    if field.max_length is not None:
        str_len = random.randint(0, field.max_length)

    val = ''
    for _ in itertools.repeat(None, str_len):
        val += random.choice(CHARFIELD_CHARSET_ASCII)
    return val


def _autogen_data_DateTimeField(instance, field):
    return datetime.datetime.now()


def _autogen_data_DateField(instance, field):
    return datetime.date.today()


def _get_IntegerField_limits(field, connection=connection):
    # TODO: Currently this doesn't take non-pg DB engines into account. sigh.
    conn_type = field.db_type(connection)
    if conn_type.startswith('integer'):
        limits = (POSTGRES_INT_MIN, POSTGRES_INT_MAX)
    elif conn_type.startswith('bigint'):
        limits = (POSTGRES_BIGINT_MIN, POSTGRES_BIGINT_MAX)
    elif conn_type.startswith('smallint'):
        limits = (POSTGRES_SMALLINT_MIN, POSTGRES_SMALLINT_MAX)
    else:
        raise TypeError('unknown type for field {}: {}'.format(
            field.name, conn_type))
    return limits


def _autogen_data_IntegerField(instance, field):
    limits = _get_IntegerField_limits(field)
    return random.randint(*limits)


def _autogen_data_PositiveIntegerField(instance, field):
    limits = _get_IntegerField_limits(field)
    return random.randint(0, limits[1])


def _autogen_data_PositiveSmallIntegerField(instance, field):
    limits = _get_IntegerField_limits(field)
    return random.randint(0, limits[1])


def _autogen_data_AutoField(instance, field):
    limits = _get_IntegerField_limits(field)
    return random.randint(0, limits[1])


def _autogen_data_BooleanField(instance, field):
    return random.choice([True, False])


def _autogen_data_EmailField(instance, field):
    char_set = string.ascii_letters + string.digits

    local_part = ''
    val_len = random.randint(1, int(field.max_length/2 - 5))
    for _ in itertools.repeat(None, val_len):
        local_part += random.choice(char_set)
    domain_part_1 = '@'
    for _ in itertools.repeat(None, val_len):
        domain_part_1 += random.choice(char_set)
    domain_part_2 = '.'
    for _ in itertools.repeat(None, 3):
        domain_part_2 += random.choice(char_set)
    email_val = '{}{}{}'.format(local_part, domain_part_1, domain_part_2)
    return email_val


def create_instance(klass, **kwargs):
    instance = klass(**kwargs)
    # .local_fields:
    for field in instance._meta.fields:
        field_type_name = type(field).__name__
        field_name = field.name

        # Don't autogen data that's been provided or if the field can be blank
        if field_name not in kwargs and \
                (not field.blank or field_name in SPECIAL_FIELDS):
            # Don't set a OneToOneField if it is the pointer to a parent
            # class in multi-table inheritance. Its fields are taken into
            # account in the instance.fields list. (instance.local_fields
            # skips these.)
            if not (isinstance(field, models.OneToOneField) and
                    isinstance(instance, field.related.parent_model)):
                callable_name = '_autogen_data_{}'.format(field_type_name)
                func = globals()[callable_name]
                val = func(instance, field)
                if field.unique:
                    while not _val_is_unique(val, field):
                        val = func(instance, field)
                setattr(instance, field_name, val)
    return instance
