import datetime
from decimal import Decimal

from django.test import TestCase
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.utils import six

from test_app.models import ModelOne, ModelTwo, ModelThree
from test_app.forms import FormOne
from fixtureless.generator import create_model_instance, create_form_instance
from fixtureless.constants import POSTGRES_SMALLINT_MAX, POSTGRES_INT_MAX, PY3, POSTGRES_BIGINT_MAX


class ModelOneTest(TestCase):
    def setUp(self):
        self.model_one = create_model_instance(ModelOne)

        if PY3:
            self.basestring = (str, bytes)
        else:
            self.basestring = basestring

    def test_decimal_field(self):
        self.assertIsInstance(self.model_one.decimal_field, Decimal)

    def test_ip_address_field(self):
        self.assertIsInstance(self.model_one.ip_address_field, self.basestring)
        octets = self.model_one.ip_address_field.split('.')
        self.assertEqual(len(octets), 4)
        for val in octets:
            int_val = int(val)
            exp = 0 <= int_val <= 255
            self.assertTrue(exp)

    def test_boolean_field(self):
        self.assertIsInstance(self.model_one.boolean_field, bool)
        self.assertEqual(self.model_one.boolean_field, False)

    def test_char_field(self):
        self.assertIsInstance(self.model_one.char_field, self.basestring)
        exp = 0 <= len(self.model_one.char_field) <= 255
        self.assertTrue(exp)

    def test_url_field(self):
        self.assertIsInstance(self.model_one.url_field, self.basestring)
        exp = 0 <= len(self.model_one.url_field) <= 255
        self.assertTrue(exp)

    def test_text_field(self):
        self.assertIsInstance(self.model_one.text_field, self.basestring)
        exp = 0 <= len(self.model_one.text_field) <= 255
        self.assertTrue(exp)

    def test_slug_field(self):
        self.assertIsInstance(self.model_one.slug_field, self.basestring)
        exp = 0 <= len(self.model_one.char_field) <= 255
        self.assertTrue(exp)

    def test_date_field(self):
        self.assertIsInstance(self.model_one.date_field, datetime.date)

    def test_datetime_field(self):
        self.assertIsInstance(self.model_one.datetime_field, datetime.datetime)

    def test_integer_field(self):
        self.assertIsInstance(self.model_one.integer_field, int)

    def test_small_integer_field(self):
        self.assertIsInstance(self.model_one.small_integer_field, int)

    def test_positive_integer_field(self):
        self.assertIsInstance(self.model_one.positive_integer_field, int)
        exp = 0 <= self.model_one.positive_integer_field <= \
            POSTGRES_INT_MAX
        self.assertTrue(exp)

    def test_positive_small_integer_field(self):
        self.assertIsInstance(self.model_one.positive_small_integer_field, int)
        exp = 0 <= self.model_one.positive_small_integer_field <= \
            POSTGRES_SMALLINT_MAX
        self.assertTrue(exp)

    def test_auto_field(self):
        self.assertIsInstance(self.model_one.auto_field, int)
        exp = 0 <= self.model_one.auto_field <= POSTGRES_INT_MAX
        self.assertTrue(exp)

    def test_time_field(self):
        self.assertIsInstance(self.model_one.time_field, datetime.time)

    def test_timezone_field(self):
        try:
            import pytz
            import timezone_field
        except ImportError:
            return
        self.assertEqual(
            self.model_one.timezone_field, pytz.timezone('America/Denver'))

    def test_email_field(self):
        self.assertIsInstance(self.model_one.email_field, self.basestring)
        exp = 0 < len(self.model_one.email_field) <= POSTGRES_INT_MAX
        self.assertTrue(exp)

        local, domain = self.model_one.email_field.split('@')
        exp = 0 < len(local) <= int(POSTGRES_INT_MAX/2 - 5)
        self.assertTrue(exp)

        exp = 0 < len(domain) <= int(POSTGRES_INT_MAX/2 - 2)
        self.assertTrue(exp)

        domain_1, domain_2 = domain.split('.')
        exp = len(domain_2) == 3
        self.assertTrue(exp)

    def test_float_field(self):
        self.assertIsInstance(self.model_one.float_field, float)

    def test_image_field(self):
        self.assertIsInstance(self.model_one.image_field, ImageFieldFile)

    def test_file_field(self):
        self.assertIsInstance(self.model_one.file_field, FieldFile)

    def test_auto_now_add_field(self):
        self.assertIsInstance(self.model_one.auto_now_add_field, datetime.datetime)

    def test_datetime_with_default(self):
        self.assertIsInstance(self.model_one.datetime_with_default, datetime.datetime)


class ModelTwoTest(TestCase):
    def setUp(self):
        self.model_one = create_model_instance(ModelOne)
        self.model_two_rand = create_model_instance(ModelTwo)
        self.model_two_kwarg = create_model_instance(
            ModelTwo, foreign_key=self.model_one)

    def test_foreign_key(self):
        self.assertIsInstance(self.model_two_rand.foreign_key, ModelOne)
        self.assertIsInstance(self.model_two_kwarg.foreign_key, ModelOne)

        self.assertEqual(self.model_two_kwarg.foreign_key, self.model_one)
        self.assertNotEqual(self.model_two_rand.foreign_key, self.model_one)

    def test_one_to_one_field(self):
        self.assertIsInstance(self.model_two_rand.one_to_one, ModelOne)
        self.assertIsInstance(self.model_two_kwarg.one_to_one, ModelOne)

        self.assertNotEqual(self.model_two_kwarg.one_to_one, self.model_one)
        self.assertNotEqual(self.model_two_rand.one_to_one, self.model_one)
        self.assertNotEqual(
            self.model_two_rand.one_to_one, self.model_two_kwarg.one_to_one)

    def test_big_auto_field(self):
        self.assertIsInstance(self.model_two_rand.big_auto_field, int)
        exp = 0 <= self.model_two_rand.big_auto_field <= POSTGRES_BIGINT_MAX
        self.assertTrue(exp)


class ModelThreeTest(TestCase):
    def setUp(self):
        self.model_three = create_model_instance(ModelThree)

    def test_jsonfield(self):
        self.assertIsInstance(self.model_three.json_field, six.string_types)
        self.assertIsInstance(self.model_three.json_field_list, list)
        self.assertIsInstance(self.model_three.json_field_dict, dict)
        self.assertIsInstance(self.model_three.json_field_callable, dict)


class FormOneTest(TestCase):
    def setUp(self):
        self.form_one = create_form_instance(FormOne)

        if PY3:
            self.basestring = (str, bytes)
        else:
            self.basestring = basestring

    def _get_val(self, name):
        return self.form_one.data[name]

    def test_decimal_field(self):
        self.assertIsInstance(self._get_val('decimal_field'), Decimal)

    def test_ip_address_field(self):
        self.assertIsInstance(self._get_val('ip_address_field'), self.basestring)
        octets = self._get_val('ip_address_field').split('.')
        self.assertEqual(len(octets), 4)
        for val in octets:
            int_val = int(val)
            exp = 0 <= int_val <= 255
            self.assertTrue(exp)

    def test_boolean_field(self):
        self.assertIn(self._get_val('boolean_field'), (True, None))

    def test_char_field(self):
        self.assertIsInstance(self._get_val('char_field'), self.basestring)
        exp = 0 <= len(self._get_val('char_field')) <= 255
        self.assertTrue(exp)

    def test_choice_field(self):
        choices = ('choice1', 'choice2')
        self.assertIn(self._get_val('choice_field'), choices)

    def test_url_field(self):
        self.assertIsInstance(self._get_val('url_field'), self.basestring)
        exp = 0 <= len(self._get_val('url_field')) <= 255
        self.assertTrue(exp)

    def test_slug_field(self):
        self.assertIsInstance(self._get_val('slug_field'), self.basestring)
        exp = 0 <= len(self._get_val('slug_field')) <= 255
        self.assertTrue(exp)

    def test_date_field(self):
        self.assertIsInstance(self._get_val('date_field'), datetime.date)

    def test_datetime_field(self):
        self.assertIsInstance(self._get_val('datetime_field'), datetime.datetime)

    def test_integer_field(self):
        self.assertIsInstance(self._get_val('integer_field'), int)

    def test_time_field(self):
        self.assertIsInstance(self._get_val('time_field'), datetime.time)

    def test_email_field(self):
        self.assertIsInstance(self._get_val('email_field'), self.basestring)
        exp = 0 < len(self._get_val('email_field')) <= POSTGRES_INT_MAX
        self.assertTrue(exp)

        local, domain = self._get_val('email_field').split('@')
        exp = 0 < len(local) <= int(POSTGRES_INT_MAX/2 - 5)
        self.assertTrue(exp)

        exp = 0 < len(domain) <= int(POSTGRES_INT_MAX/2 - 2)
        self.assertTrue(exp)

        domain_1, domain_2 = domain.split('.')
        exp = len(domain_2) == 3
        self.assertTrue(exp)

    def test_float_field(self):
        self.assertIsInstance(self._get_val('float_field'), float)

    def test_is_valid(self):
        self.assertTrue(self.form_one.is_valid())
