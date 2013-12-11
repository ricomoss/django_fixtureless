import sys
import datetime
from decimal import *


from django.test import TestCase

from test_app.models import ModelOne, ModelTwo
import fixtureless
from fixtureless import POSTGRES_SMALLINT_MAX, POSTGRES_INT_MAX

PY3 = True
if sys.version_info.major == 2:
    PY3 = False


class ModelOneTest(TestCase):
    def setUp(self):
        self.model_one = fixtureless.create_instance(ModelOne)

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

    def test_char_field(self):
        self.assertIsInstance(self.model_one.char_field, self.basestring)
        exp = 0 <= len(self.model_one.char_field) <= 255
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


class ModelTwoTest(TestCase):
    def setUp(self):
        self.model_one = fixtureless.create_instance(ModelOne)
        self.model_two_rand = fixtureless.create_instance(ModelTwo)
        self.model_two_kwarg = fixtureless.create_instance(
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
