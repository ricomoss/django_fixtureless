from decimal import Decimal

from django.test import TestCase

from factory import Factory
from exceptions import InvalidArguments
from test_app.models import ModelOne, ModelTwo


class FactoryTest(TestCase):
    def test_create_trivial(self):
        factory = Factory()
        count = 1
        kwargs = {
            'decimal_field': Decimal('10.00')
        }
        args = (ModelOne, count, kwargs)
        model = factory.create(*args)
        self.assertIsInstance(model, ModelOne)
        self.assertEqual(model.decimal_field, kwargs['decimal_field'])

    def test_resolve_args(self):
        factory = Factory()
        with self.assertRaises(InvalidArguments) as _:
            factory._resolve_args()

        with self.assertRaises(InvalidArguments) as _:
            factory._resolve_args('wrong_val')

        model, count, kwargs = factory._resolve_args(ModelOne)
        self.assertEqual(model, ModelOne)
        self.assertIsInstance(count, int)
        self.assertIsNone(kwargs)

    # Only model
    def test_handle_build_trivial(self):
        factory = Factory()
        model = factory._handle_build(ModelOne)
        self.assertIsInstance(model, ModelOne)

    # Model w/ single count
    def test_handle_build_with_count(self):
        factory = Factory()
        count = 1
        args = (ModelOne, count)
        model = factory._handle_build(*args)
        self.assertIsInstance(model, ModelOne)

    # Model w/ multiple count
    def test_handle_build_with_multi_count(self):
        factory = Factory()
        count = 2
        args = (ModelOne, count)
        models = list()
        factory._handle_build(*args, objs=models)
        self.assertEqual(len(models), 2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)
        self.assertNotEqual(models[0], models[1])

    # Model /w single count and kwargs
    def test_handle_build_with_count_and_kwargs(self):
        factory = Factory()
        count = 1
        kwargs = {
            'decimal_field': Decimal('10.00')
        }
        args = (ModelOne, count, kwargs)
        model = factory._handle_build(*args)
        self.assertIsInstance(model, ModelOne)
        self.assertEqual(model.decimal_field, kwargs['decimal_field'])

    # Model /w multi count and single kwargs
    def test_handle_build_with_multi_count_and_single_kwargs(self):
        factory = Factory()
        count = 2
        kwargs1 = {
            'decimal_field': Decimal('10.00')
        }
        kwargs2 = {
            'decimal_field': Decimal('8.00')
        }
        args = ((ModelOne, count, kwargs1))
        models = list()
        factory._handle_build(*args, objs=models)
        self.assertEqual(len(models), 4)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, kwargs1['decimal_field'])
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[1].decimal_field, kwargs1['decimal_field'])

    # Model /w multi count and multi kwargs
    def test_handle_build_with_multi_count_and_multi_kwargs(self):
        factory = Factory()
        count = 2
        kwargs1_1 = {
            'decimal_field': Decimal('10.00')
        }
        kwargs1_2 = {
            'decimal_field': Decimal('8.00')
        }
        args = ((ModelOne, count, [kwargs1_1, kwargs1_2]))
        models = list()
        factory._handle_build(*args, objs=models)
        self.assertEqual(len(models), 4)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, kwargs1_1['decimal_field'])
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[1].decimal_field, kwargs1_2['decimal_field'])
