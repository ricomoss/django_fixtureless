"""
Generators for building instance field types.
"""
import decimal
import json
import math
import random
import string

from django.conf import settings
from django.db import models, connection
from django.db.models.fields import NOT_PROVIDED
from django.utils import timezone

from fixtureless import constants, utils


class Generator:  # pylint: disable=too-few-public-methods
    """
    Generator class for organizing the generator methods
    """
    def __init__(self, instance_type=None):
        self.is_model = instance_type == models.Model

    USE_TZ = getattr(settings, 'USE_TZ', False)

    def get_val(self, **kwargs):
        """
        Extracts info from kwargs to call the correct generator and return the value.

        :param kwargs: Keyword arguments passed in
        :return: Generated value
        """
        field = kwargs['field']
        if isinstance(field, str):
            callable_name = f'_generate_{field}'
        else:
            callable_name = f'_generate_{type(field).__name__.lower()}'
        try:
            func = getattr(self, callable_name)
        except AttributeError:
            if field.default != NOT_PROVIDED:
                func = self._generate_field_with_default
            else:
                msg = f'fixtureless does not support the field type {type(field).__name__} ' \
                      'without a default'
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

        :param val: Value to be checked
        :param field: Field object
        :return: True, if the value is unique; False otherwise.
        """
        if val is None:
            return False

        if not field.unique:
            return True

        field_name = field.name
        return field.model.objects.filter(**{field_name: val}).count() == 0

    @staticmethod
    def _generate_foreignkey(**kwargs):
        """
        Generate a FK

        :param kwargs: Keyword arguments
        :return: An instance of a FK field
        """
        field = kwargs['field']
        klass = field.remote_field.model

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
        """
        Generate a one to one field

        :param kwargs: Keyword arguments
        :return: An instance of a FK field (treated the same)
        """
        return self._generate_foreignkey(**kwargs)

    def _generate_dictionaryfield(self, **kwargs):
        """
        Generates a dictionary field type (postgres)

        :param kwargs: Keyword arguments
        :return: A dictionary field instance,
            if default values are provide; An empty dictionary otherwise.
        """
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        return {}

    def _generate_integerrangefield(self, **kwargs):
        """
        Generates an integer range field.

        :param kwargs: Keyword arguments
        :return: An integer range field instance
        """
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        return random.randint(field.min_value, field.max_value)

    def _generate_storefield(self, **kwargs):
        """
        Generate a store field

        :param kwargs: Keyword arguments
        :return: A dictionary field (treated the same)
        """
        return self._generate_dictionaryfield(**kwargs)

    def _generate_decimalfield(self, **kwargs):
        """
        Generate a decimal field

        :param kwargs: Keyword arguments
        :return: A decimal field
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        len_int_part = field.max_digits - field.decimal_places
        # Add a scaling factor here to help prevent overflowing the Decimal fields when doing
        # summing, etc. This still won't protect tiny dec fields (1 or 2 digits before the
        # decimal), but should cover most use cases.
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

    def _generate_genericipaddressfield(self, **kwargs):
        """
        Generate a random IP "looking" value  (currently only IPv4)

        :param kwargs: Keyword arguments
        :return: A string with an "IP" value
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        num_octets = 4
        octets = [str(random.randint(0, 255)) for _ in range(num_octets)]
        return '.'.join(octets)

    @staticmethod
    def _generate_choicefield(**kwargs):
        """
        Generate a choice field

        :param kwargs: Keyword arguments
        :return: A choice field
        """
        field = kwargs['field']
        return random.choice(field.choices)[0]

    def _generate_with_char_set(self, char_set, field):
        """
        Generate a character set

        :param char_set: Character set type
        :param field: Field object
        :return: A random string
        """
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(field=field)
        # Use a choice if this field has them defined.
        if self.is_model and field.choices:
            return random.choice(field.choices)[0]

        str_len = constants.DEFAULT_CHARFIELD_MAX_LEN
        if field.max_length is not None:
            str_len = random.randint(1, field.max_length)

        return utils.random_str(str_len, char_set)

    def _generate_charfield(self, **kwargs):
        """
        Generate a character field

        :param kwargs: Keyword arguments
        :return: A character field
        """
        field = kwargs['field']
        instance = kwargs['instance']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        # An issue with MySQL databases, which requires a manual modification
        # to the database, prevents unicode.
        if self.is_model and self._get_db_type(instance) == constants.MYSQL:
            return self._generate_with_char_set(
                constants.CHARFIELD_CHARSET_ASCII, field)
        return self._generate_with_char_set(
            constants.CHARFIELD_CHARSET_UNICODE, field)

    def _generate_imagefield(self, **kwargs):
        """
        Generate an image field

        :param kwargs: Keyword arguments
        :return: A generated character field (treated the same)
        """
        return self._generate_charfield(**kwargs)

    def _generate_filefield(self, **kwargs):
        """
        Generate a field field

        :param kwargs: Keyword arguments
        :return: A generated character field (treated the same)
        """
        return self._generate_charfield(**kwargs)

    def _generate_textfield(self, **kwargs):
        """
        Generate a text field

        :param kwargs: Keyword arguments
        :return: A generated character field (treated the same)
        """
        return self._generate_charfield(**kwargs)

    @staticmethod
    def _generate_urlfield(_):
        """
        Generate a random URL Field

        :param _: Necessary for signature
        :return: A random URL
        """
        subdomain = utils.random_str(10, string.ascii_letters)
        domain = utils.random_str(10, string.ascii_letters)
        return 'http://{}.{}.com'.format(subdomain, domain)

    def _generate_slugfield(self, **kwargs):
        """
        Generate a slug field

        :param kwargs: Keyword arguments
        :return: A random string
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        str_len = constants.DEFAULT_CHARFIELD_MAX_LEN
        if field.max_length is not None:
            str_len = random.randint(0, field.max_length)

        return utils.random_str(str_len, constants.SLUGFIELD_CHARSET)

    def _generate_datetimefield(self, **kwargs):
        """
        Generate a datetime field

        :param kwargs: Keyword arguments
        :return: A datetime field
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED and \
                hasattr(field.default, '__call__'):
            return self._generate_field_with_default(**kwargs)
        return timezone.now()

    def _generate_datefield(self, **kwargs):
        """
        Generate a date field

        :param kwargs: Keyword arguments
        :return: A date field
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED and \
                hasattr(field.default, '__call__'):
            return self._generate_field_with_default(**kwargs)
        return timezone.now().today()

    def _generate_timefield(self, **kwargs):
        """
        Generate a time field

        :param kwargs: Keyword arguments
        :return: A time field
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED and \
                hasattr(field.default, '__call__'):
            return self._generate_field_with_default(**kwargs)
        return timezone.now().time()

    def _get_integer_limits(self, field, connection_obj=connection):
        """
        Get integer limits for a given field

        :param field: Field to check
        :param connection_obj: The connection for determine DB type
        :return: A tuple of limit values
        """
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
        """
        Generate a small integer field

        :param kwargs: Keyword arguments
        :return: A "small" random number
        """
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        limits = self._get_integer_limits(field)
        return random.randint(*limits)

    def _generate_integerfield(self, **kwargs):
        """
        Generate an integer field

        :param kwargs: Keyword arguments
        :return: A random number
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        limits = self._get_integer_limits(field)
        return random.randint(*limits)

    def _generate_floatfield(self, **kwargs):
        """
        Generate a float field

        :param kwargs: Keyword arguments
        :return: A float field
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        limits = (constants.FLOATFIELD_MIN, constants.FLOATFIELD_MAX)
        return random.uniform(*limits)

    def _generate_positiveintegerfield(self, **kwargs):
        """
        Generate a positive integer field

        :param kwargs: Keyword arguments
        :return: A positive integer
        """
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_positivesmallintegerfield(self, **kwargs):
        """
        Generate a positive small integer field

        :param kwargs: Keyword arguments
        :return: A positive "small" integer
        """
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_autofield(self, **kwargs):
        """
        Generate an auto field

        :param kwargs: Keyword arguments
        :return: A random number
        """
        field = kwargs['field']
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_bigautofield(self, **kwargs):
        """
        Generate a big auto field

        :param kwargs: Keyword arguments
        :return: A "big" random number
        """
        field = kwargs['field']
        limits = self._get_integer_limits(field)
        return random.randint(0, limits[1])

    def _generate_booleanfield(self, **kwargs):
        """
        Generate a boolean field

        :param kwargs: Keyword arguments
        :return: A random boolean
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        if not self.is_model:
            return random.choice([True, None])
        return random.choice([True, False])

    def _generate_emailfield(self, **kwargs):
        """
        Generate an email field

        :param kwargs: Keyword arguments
        :return: A random email string
        """
        field = kwargs['field']
        if self.is_model and field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)

        max_length = field.max_length or 30
        val_len = random.randint(1, int(max_length/2 - 5))
        return '{}@{}.{}'.format(
            utils.random_str(val_len, constants.EMAIL_CHARSET),
            utils.random_str(val_len, constants.EMAIL_CHARSET),
            utils.random_str(3, constants.EMAIL_CHARSET))

    def _generate_jsonfield(self, **kwargs):
        """
        Generate a JSON field

        :param kwargs: Keyword arguments
        :return: A JSON object
        """
        field = kwargs['field']
        if field.default != NOT_PROVIDED:
            return self._generate_field_with_default(**kwargs)
        return json.dumps(utils.get_random_dict())

    @staticmethod
    def _generate_field_with_default(**kwargs):
        """
        Generate a field with defaults.  Only called if field.default != NOT_PROVIDED

        :param kwargs: Keyword arguments
        :return: The default value given
        """
        field = kwargs['field']
        if callable(field.default):
            return field.default()
        return field.default

    @staticmethod
    def _get_db_type(instance):
        """
        Get the DB type

        :param instance: The instance object
        :return: The DB engine being used.
        """
        db_name = 'default'
        if instance._state.db is not None:  # pylint: disable=protected-access
            db_name = instance._state.db  # pylint: disable=protected-access
        return settings.DATABASES[db_name]['ENGINE'].split('.')[-1]


def _should_autogen_data(field, kwargs):
    """
    Determine if a field should be auto generated.

    :param field: The field in question
    :param kwargs: Keyword arguments
    :return: True, if the field should be generated; False otherwise.
    """
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
    """
    Handler for creating the model instance

    :param klass: The model class to be used.
    :param kwargs: Keyword arguments
    :return: A model instance
    """
    instance = klass(**kwargs)
    # .local_fields:
    for field in instance._meta.fields:  # pylint: disable=protected-access
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
                try:
                    setattr(instance, field.name, val)
                except (FileNotFoundError, OSError):
                    pass
    return instance


def create_form_instance(klass, **kwargs):
    """
    Handler for creating a form instance

    :param klass: The form class to be used.
    :param kwargs: Keyword arguments
    :return: A form instance
    """
    instance = klass(kwargs)
    for field_name, field_type in instance.fields.items():
        if instance.data.get(field_name):
            continue
        val = Generator().get_val(instance=instance, field=field_type)
        instance.data[field_name] = val
    return instance
