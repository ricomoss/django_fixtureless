import itertools
from decimal import Decimal

from django.test import TestCase

from fixtureless import Factory
from fixtureless.exceptions import InvalidArguments
from test_app.models import ModelOne, ModelTwo


class FactoryTest(TestCase):
    def test_resolve_args(self):
        factory = Factory()
        with self.assertRaises(InvalidArguments) as _:
            factory._resolve_args()

        with self.assertRaises(InvalidArguments) as _:
            factory._resolve_args('wrong_val')

        model, initial = factory._resolve_args(ModelOne)
        self.assertEqual(model, ModelOne)
        self.assertIsInstance(initial, tuple)
        self.assertIsNone(initial[0])

    def test_verify_kwargs(self):
        factory = Factory()

        # invalid kwarg type
        val = 'invalid type'
        with self.assertRaises(InvalidArguments) as _:
            factory._verify_kwargs(val)

        # invalid kwarg type in list
        val = ['invalid type']
        with self.assertRaises(InvalidArguments) as _:
            factory._verify_kwargs(val)

        # valid kwarg type no list
        val = {'valid': 'type'}
        factory._verify_kwargs(val)

        # valid type
        val = [{'valid': 'type'}]
        factory._verify_kwargs(val)

        # valid type, invalid type, correct length
        val = [{'valid': 'type'}, 'invalid type']
        with self.assertRaises(InvalidArguments) as _:
            factory._verify_kwargs(val)

    # Model trivial
    def test_build_trivial(self):
        factory = Factory()
        model = factory.build(ModelOne)
        self.assertIsInstance(model, ModelOne)

    # Model w/ single count
    def test_build_with_single_count(self):
        factory = Factory()
        count = 1
        args = (ModelOne, count)
        model = factory.build(*args)
        self.assertIsInstance(model, ModelOne)

    # Model w/ multiple count
    def test_build_with_multi_count(self):
        factory = Factory()
        count = 2
        models = factory.build(ModelOne, count)
        self.assertEqual(len(models), count)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)
        self.assertNotEqual(models[0], models[1])

    # Model w/ single count and initial
    def test_build_with_count_and_initial(self):
        factory = Factory()
        count = 1
        initial = {
            'decimal_field': Decimal('10.00')
        }
        args = (ModelOne, initial)
        model = factory.build(*args)
        self.assertIsInstance(model, ModelOne)
        self.assertEqual(model.decimal_field, initial['decimal_field'])

    # Model w/ multi count and single initial
    def test_build_with_multi_count_and_single_initial(self):
        factory = Factory()
        count = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial_list = list()
        for _ in itertools.repeat(None, count):
            initial_list.append(initial1)
        args = (ModelOne, initial_list)
        models = factory.build(*args)
        self.assertEqual(len(models), count)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[1].decimal_field, initial1['decimal_field'])

    # Model w/ multi count and multi initial
    def test_build_with_multi_count_and_multi_initial(self):
        factory = Factory()
        count = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'decimal_field': Decimal('8.00')
        }
        args = (ModelOne, [initial1, initial2])
        models = factory.build(*args)
        self.assertEqual(len(models), count)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[1].decimal_field, initial2['decimal_field'])

    # Multi Model Trivial
    def test_build_with_multi_model_trivial(self):
        factory = Factory()
        models = factory.build((ModelOne, ), (ModelTwo, ))
        self.assertEqual(len(models), 2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelTwo)

    # Multi Model w/ single count
    def test_build_with_multi_model_and_single_count(self):
        factory = Factory()
        count1 = 1
        count2 = 1
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = factory.build(*args)
        self.assertEqual(len(models), 2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelTwo)

    # Multi Model w/ multiple count
    def test_build_with_multi_model_and_multi_count(self):
        factory = Factory()
        count1 = 2
        count2 = 3
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = factory.build(*args)
        self.assertEqual(len(models), count1 + count2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)

        self.assertIsInstance(models[2], ModelTwo)
        self.assertIsInstance(models[3], ModelTwo)
        self.assertIsInstance(models[4], ModelTwo)

    # Multi Model w/ single count and initial
    def test_build_with_multi_model_and_single_count_and_single_initial(self):
        factory = Factory()
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'char_field': 'test value'
        }
        args = ((ModelOne, initial1), (ModelTwo, initial2))
        models = factory.build(*args)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])

        self.assertIsInstance(models[1], ModelTwo)
        self.assertEqual(models[1].char_field, initial2['char_field'])

    # Multi Model w/ multi count and single initial
    def test_build_with_multi_model_and_multi_count_and_single_initial(self):
        factory = Factory()
        count1 = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial_list1 = list()
        for _ in itertools.repeat(None, count1):
            initial_list1.append(initial1)
        count2 = 3
        initial2 = {
            'char_field': 'test value'
        }
        initial_list2 = list()
        for _ in itertools.repeat(None, count2):
            initial_list2.append(initial2)
        args = ((ModelOne, initial_list1), (ModelTwo, initial_list2))
        models = factory.build(*args)
        self.assertEqual(len(models), count1 + count2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])
        self.assertEqual(models[1].decimal_field, initial1['decimal_field'])

        self.assertIsInstance(models[2], ModelTwo)
        self.assertIsInstance(models[3], ModelTwo)
        self.assertIsInstance(models[4], ModelTwo)
        self.assertEqual(models[2].char_field, initial2['char_field'])
        self.assertEqual(models[3].char_field, initial2['char_field'])
        self.assertEqual(models[4].char_field, initial2['char_field'])

    # Multi Model w/ multi count and multi initial
    def test_build_with_multi_model_and_multi_count_and_multi_initial(self):
        factory = Factory()
        initial1_1 = {
            'decimal_field': Decimal('10.00')
        }
        initial1_2 = {
            'decimal_field': Decimal('8.00')
        }
        initial2_1 = {
            'char_field': 'test value 1'
        }
        initial2_2 = {
            'char_field': 'test value 2'
        }
        args = ((ModelOne, [initial1_1, initial1_2]),
                (ModelTwo, [initial2_1, initial2_2]))
        models = factory.build(*args)
        self.assertEqual(len(models), 4)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1_1['decimal_field'])
        self.assertEqual(models[1].decimal_field, initial1_2['decimal_field'])
        self.assertIsInstance(models[2], ModelTwo)
        self.assertIsInstance(models[3], ModelTwo)
        self.assertEqual(models[2].char_field, initial2_1['char_field'])
        self.assertEqual(models[3].char_field, initial2_2['char_field'])

    # Model trivial
    def test_create_trivial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        model = factory.create(ModelOne)
        self.assertIsInstance(model, ModelOne)

        models = ModelOne.objects.all()
        self.assertEqual(len(models), 1)

    # Model w/ single count
    def test_create_with_single_count(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        count = 1
        args = (ModelOne, count)
        model = factory.create(*args)
        self.assertIsInstance(model, ModelOne)

        models = ModelOne.objects.all()
        self.assertEqual(len(models), count)

    # Model w/ multiple count
    def test_create_with_multi_count(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        count = 2
        args = (ModelOne, count)
        models = factory.create(*args)
        self.assertEqual(len(models), count)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)
        self.assertNotEqual(models[0], models[1])

        models = ModelOne.objects.all()
        self.assertEqual(len(models), count)

    # Model w/ single count and initial
    def test_create_with_count_and_initial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        initial = {
            'decimal_field': Decimal('10.00')
        }
        args = (ModelOne, initial)
        model = factory.create(*args)
        self.assertIsInstance(model, ModelOne)
        self.assertEqual(model.decimal_field, initial['decimal_field'])

        models = ModelOne.objects.all()
        self.assertEqual(len(models), 1)

    # Model w/ multi count and single initial
    def test_create_with_multi_count_and_single_initial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        count = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial_list = list()
        for _ in itertools.repeat(None, count):
            initial_list.append(initial1)

        args = (ModelOne, initial_list)
        models = factory.create(*args)
        self.assertEqual(len(models), count)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[1].decimal_field, initial1['decimal_field'])

        models = ModelOne.objects.all()
        self.assertEqual(len(models), count)

    # Model w/ multi count and multi initial
    def test_create_with_multi_count_and_multi_initial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'decimal_field': Decimal('8.00')
        }
        args = (ModelOne, [initial1, initial2])
        models = factory.create(*args)
        self.assertEqual(len(models), 2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[1].decimal_field, initial2['decimal_field'])

        models = ModelOne.objects.all()
        self.assertEqual(len(models), 2)

    # Multi Model Trivial
    def test_create_with_multi_model_trivial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        models = factory.create((ModelOne, ), (ModelTwo, ))
        self.assertEqual(len(models), 2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelTwo)

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect 2
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 2)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 1)

    # Multi Model w/ single count
    def test_create_with_multi_model_and_single_count(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        count1 = 1
        count2 = 1
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = factory.create(*args)
        self.assertEqual(len(models), 2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelTwo)

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect 2
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 2)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 1)

    # Multi Model w/ multiple count
    def test_create_with_multi_model_and_multi_count(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        count1 = 2
        count2 = 3
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = factory.create(*args)
        self.assertEqual(len(models), count1 + count2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)

        self.assertIsInstance(models[2], ModelTwo)
        self.assertIsInstance(models[3], ModelTwo)
        self.assertIsInstance(models[4], ModelTwo)

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models (count1)
        # 1 for each OneToOne fields (count2)
        models = ModelOne.objects.all()
        self.assertEqual(len(models), count1 + count2)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), count2)

    # Multi Model w/ single count and initial
    def test_create_with_multi_model_and_single_count_and_single_initial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'char_field': 'test value'
        }
        args = ((ModelOne, initial1), (ModelTwo, initial2))
        models = factory.create(*args)
        self.assertIsInstance(models[0], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])

        self.assertIsInstance(models[1], ModelTwo)
        self.assertEqual(models[1].char_field, initial2['char_field'])

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models
        # 1 for each OneToOne fields
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 2)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 1)

    # Multi Model w/ multi count and single initial
    def test_create_with_multi_model_and_multi_count_and_single_initial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        count1 = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial_list1 = list()
        for _ in itertools.repeat(None, count1):
            initial_list1.append(initial1)
        count2 = 3
        initial2 = {
            'char_field': 'test value'
        }
        initial_list2 = list()
        for _ in itertools.repeat(None, count2):
            initial_list2.append(initial2)
        args = ((ModelOne, initial_list1), (ModelTwo, initial_list2))
        models = factory.create(*args)
        self.assertEqual(len(models), count1 + count2)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1['decimal_field'])
        self.assertEqual(models[1].decimal_field, initial1['decimal_field'])

        self.assertIsInstance(models[2], ModelTwo)
        self.assertIsInstance(models[3], ModelTwo)
        self.assertIsInstance(models[4], ModelTwo)
        self.assertEqual(models[2].char_field, initial2['char_field'])
        self.assertEqual(models[3].char_field, initial2['char_field'])
        self.assertEqual(models[4].char_field, initial2['char_field'])

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models (count1)
        # 1 for each OneToOne fields (count2)
        models = ModelOne.objects.all()
        self.assertEqual(len(models), count1 + count2)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), count2)

    # Multi Model w/ multi count and multi initial
    def test_create_with_multi_model_and_multi_count_and_multi_initial(self):
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 0)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 0)

        factory = Factory()
        initial1_1 = {
            'decimal_field': Decimal('10.00')
        }
        initial1_2 = {
            'decimal_field': Decimal('8.00')
        }
        initial2_1 = {
            'char_field': 'test value 1'
        }
        initial2_2 = {
            'char_field': 'test value 2'
        }
        args = ((ModelOne, [initial1_1, initial1_2]),
                (ModelTwo, [initial2_1, initial2_2]))
        models = factory.create(*args)
        self.assertEqual(len(models), 4)
        self.assertIsInstance(models[0], ModelOne)
        self.assertIsInstance(models[1], ModelOne)
        self.assertEqual(models[0].decimal_field, initial1_1['decimal_field'])
        self.assertEqual(models[1].decimal_field, initial1_2['decimal_field'])
        self.assertIsInstance(models[2], ModelTwo)
        self.assertIsInstance(models[3], ModelTwo)
        self.assertEqual(models[2].char_field, initial2_1['char_field'])
        self.assertEqual(models[3].char_field, initial2_2['char_field'])

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models (count1)
        # 1 for each OneToOne fields (count2)
        models = ModelOne.objects.all()
        self.assertEqual(len(models), 4)
        models = ModelTwo.objects.all()
        self.assertEqual(len(models), 2)
