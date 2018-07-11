import sys
import decimal
import math
import random
import json

from django.db import models
from django.db import connection
from django.db.models.fields import NOT_PROVIDED
from django.conf import settings
from django.utils import timezone

from django.core.exceptions import SuspiciousFileOperation

from fixtureless import constants
from fixtureless import utils

PY3 = sys.version_info.major == 3


class Generator(object):
    def __init__(self, instance_type=None):
        self.is_model = instance_type == models.Model

    USE_TZ = getattr(settings, 'USE_TZ', False)

    def get_val(self, **kwargs):
        field = kwargs['field']
        if isinstance(field, str):
            callable_name = '_generate_{}'.format(field)
        else:
            callable_name = '_generate_{}'.format(type(field).__name__.lower())
        try:
            func = getattr(self, callable_name)
        except AttributeError:
            msg = 'fixtureless does not support the field type: {}'.format(
                type(field).__name__)
            raise AttributeError(msg)
        val = func(**kwargs)
        if hasattr(field, 'unique') and field.unique:
            while not self._val_is_unique(val, field):
                val = func(**kwargs)
        return val

    @staticmethod
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

    @staticmethod
    @utils.deprecated
    def _generate_timezonefield(**kwargs):
        field = kwargs['field']
        import pytz
        if field.default != NOT_PROVIDED:
            return pytz.timezone(field.default)
        return pytz.UTC

    @staticmethod
    def _generate_foreignkey(**kwargs):
        field = kwargs['field']
        try:
            # Django >= 1.10
            klass = field.remote_field.model
        except AttributeError:
            # Django 1.8 - 1.9
            klass = field.related.model

        instance = None
        if not field.unique:
            # Try to retrieve the last one
            try:
                instance = klass.objects.order_by('-pk')[0]
            except IndexError:
                instance = None
        if field.unique or instance is None:
            instance = create_model_instance(klass)
            instance.save()
        return instance

    def _generate_onetoonefield(self, **kwargs):
        return self._generate_foreignkey(**kwargs)

    @staticmethod
    def _generate_dictionaryfield(**kwargs):
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return field.default
        return {}

    @staticmethod
    def _generate_integerrangefield(**kwargs):
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return field.default
        return random.randint(field.min_value, field.max_value)

    def _generate_storefield(self, **kwargs):
        return self._generate_dictionaryfield(**kwargs)

    def _generate_decimalfield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        len_int_part = field.max_digits - field.decimal_places
        # Add a scaling factor here to help prevent overflowing the
        # Decimal fields when doing summming, etc. This still won't
        # protect tiny dec fields (1 or 2 digits before the decimal),
        # but should cover most use cases.
        len_int_part = int(math.floor(math.sqrt(len_int_part)))
        if len_int_part == 0:
            len_fractional_part = random.randint(0, field.decimal_places)
            fractional_part = str(random.random())[2:len_fractional_part+2]
            return decimal.Decimal('0.{}'.format(fractional_part))

        max_intval = pow(10, len_int_part) - 2
        int_part = random.randint(-max_intval, max_intval)
        len_fractional_part = random.randint(0, field.decimal_places)
        if len_fractional_part > 0:
            # Turn into a string, and trim off the '0.' from the start.
            fractional_part = str(random.random())[2:len_fractional_part+2]
        else:
            fractional_part = ''
        # Val must be passed into Decimal constructor as a string,
        # otherwise it will be rounded!
        val = decimal.Decimal('{}.{}'.format(int_part, fractional_part))
        return val

    @staticmethod
    @utils.deprecated
    def _generate_ipaddressfield(**kwargs):
        """ Currently only IPv4 fields. """
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return field.default
        num_octets = 4
        octets = [str(random.randint(0, 255)) for n in range(num_octets)]
        return '.'.join(octets)

    def _generate_genericipaddressfield(self, **kwargs):
        """ Currently only IPv4 fields. """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        num_octets = 4
        octets = [str(random.randint(0, 255)) for n in range(num_octets)]
        return '.'.join(octets)

    @staticmethod
    def _generate_choicefield(**kwargs):
        field = kwargs['field']
        return random.choice(field.choices)[0]

    def _generate_with_char_set(self, char_set, field):
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        # Use a choice if this field has them defined.
        if self.is_model and len(field.choices) > 0:
            return random.choice(field.choices)[0]

        str_len = constants.DEFAULT_CHARFIELD_MAX_LEN
        if field.max_length is not None:
            str_len = random.randint(1, field.max_length)

        return utils.random_str(str_len, char_set)

    def _generate_charfield(self, **kwargs):
        field = kwargs['field']
        instance = kwargs['instance']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        # An issue with MySQL databases, which requires a manual modification
        # to the database, prevents unicode.
        if self.is_model and self._get_db_type(instance) == constants.MYSQL:
            return self._generate_with_char_set(
                constants.CHARFIELD_CHARSET_ASCII, field)
        return self._generate_with_char_set(
            constants.CHARFIELD_CHARSET_UNICODE, field)

    def _generate_imagefield(self, **kwargs):
        return self._generate_charfield(**kwargs)

    def _generate_filefield(self, **kwargs):
        return self._generate_charfield(**kwargs)

    def _generate_textfield(self, **kwargs):
        return self._generate_charfield(**kwargs)

    def _generate_urlfield(self, **kwargs):
        import string
        subdomain = utils.random_str(10, string.ascii_letters)
        domain = utils.random_str(10, string.ascii_letters)
        return 'http://{}.{}.com'.format(subdomain, domain)

    def _generate_slugfield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        str_len = constants.DEFAULT_CHARFIELD_MAX_LEN
        if field.max_length is not None:
            str_len = random.randint(0, field.max_length)

        return utils.random_str(str_len, constants.SLUGFIELD_CHARSET)

    def _generate_datetimefield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED and \
                hasattr(field.default, '__call__'):
            return field.default()
        return timezone.now()

    def _generate_datefield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED and \
                hasattr(field.default, '__call__'):
            return field.default()
        return timezone.now().today()

    def _generate_timefield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED and \
                hasattr(field.default, '__call__'):
            return field.default()
        return timezone.now().time()

    def _get_integer_limits(self, field, connection_obj=connection):
        if not self.is_model:
            return constants.POSTGRES_SMALLINT_MIN, constants.POSTGRES_SMALLINT_MAX

        conn_type = field.db_type(connection_obj)
        if conn_type.startswith('integer') or conn_type.startswith('serial'):
            limits = (constants.POSTGRES_INT_MIN, constants.POSTGRES_INT_MAX)
        elif conn_type.startswith('bigint') or conn_type.startswith('bigserial'):
            limits = (constants.POSTGRES_BIGINT_MIN,
                      constants.POSTGRES_BIGINT_MAX)
        elif conn_type.startswith('smallint'):
            limits = (constants.POSTGRES_SMALLINT_MIN,
                      constants.POSTGRES_SMALLINT_MAX)
        else:
            raise TypeError('unknown type for field {}: {}'.format(
                field.name, conn_type))
        return limits

    def _generate_smallintegerfield(self, **kwargs):
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return field.default
        limits = self._get_integer_limits(field)
        return random.randint(*limits)

    def _generate_integerfield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        limits = self._get_integer_limits(field)
        return random.randint(*limits)

    @staticmethod
    def _get_float_limits():
        return constants.FLOATFIELD_MIN, constants.FLOATFIELD_MAX

    def _generate_floatfield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        limits = self._get_float_limits()
        return random.uniform(*limits)

    def _generate_positiveintegerfield(self, **kwargs):
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return field.default
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_positivesmallintegerfield(self, **kwargs):
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return field.default
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_autofield(self, **kwargs):
        field = kwargs['field']
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_bigautofield(self, **kwargs):
        field = kwargs['field']
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_booleanfield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default
        if not self.is_model:
            return random.choice([True, None])
        return random.choice([True, False])

    def _generate_emailfield(self, **kwargs):
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return field.default

        max_length = field.max_length or 30
        val_len = random.randint(1, int(max_length/2 - 5))
        return '{}@{}.{}'.format(
            utils.random_str(val_len, constants.EMAIL_CHARSET),
            utils.random_str(val_len, constants.EMAIL_CHARSET),
            utils.random_str(3, constants.EMAIL_CHARSET))

    @staticmethod
    def _generate_jsonfield(**kwargs):
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return field.default() if callable(field.default) else field.default
        return json.dumps(utils.get_random_dict())

    @staticmethod
    def _get_db_type(instance):
        db_name = 'default'
        if instance._state.db is not None:
            db_name = instance._state.db
        return settings.DATABASES[db_name]['ENGINE'].split('.')[-1]


def _should_autogen_data(field, kwargs):
    if field.name in kwargs:
        return False

    if not (field.blank and field.null):
        return True

    if field.name in constants.SPECIAL_FIELDS:
        return True

    if hasattr(field, 'auto_now_add') and field.auto_now_add:
        return True

    return False


def create_model_instance(klass, **kwargs):
    instance = klass(**kwargs)
    # .local_fields:
    for field in instance._meta.fields:
        # Don't autogen data that's been provided or if the field can be blank
        if _should_autogen_data(field, kwargs):
            # Don't set a OneToOneField if it is the pointer to a parent
            # class in multi-table inheritance. Its fields are taken into
            # account in the instance.fields list. (instance.local_fields
            # skips these.)
            is_related_model = False
            if hasattr(field, 'related'):
                try:
                    # Django > 1.8
                    is_related_model = isinstance(
                        instance, field.related_model)
                except AttributeError:
                    # Django < 1.8
                    is_related_model = isinstance(
                        instance, field.related.parent_model)
            if not (isinstance(field, models.OneToOneField)
                    and is_related_model):
                val = Generator(models.Model).get_val(instance=instance, field=field)
                # Not worrying about creating file objects on disk
                if PY3:
                    try:
                        setattr(instance, field.name, val)
                    except (FileNotFoundError, OSError):
                        pass
                else:
                    try:
                        setattr(instance, field.name, val)
                    except (IOError, OSError, SuspiciousFileOperation):
                        pass
    return instance


def create_form_instance(klass, **kwargs):
    instance = klass(kwargs)
    for field_name, field_type in instance.fields.items():
        if instance.data.get(field_name):
            continue
        val = Generator().get_val(instance=instance, field=field_type)
        instance.data[field_name] = val
    return instance
