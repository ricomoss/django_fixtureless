import itertools
from decimal import Decimal

import pytest
from django.db.models import Model

from fixtureless.factory import Factory
from fixtureless.exceptions import InvalidArguments
from fixtureless.factory import create, build
from test_app.models import ModelOne, ModelTwo


def _check_models(models, count, initial1):
    assert len(models) == count
    assert isinstance(models[0], ModelOne)
    assert models[0].decimal_field == initial1['decimal_field']
    assert isinstance(models[1], ModelOne)
    assert models[1].decimal_field == initial1['decimal_field']


class TestFactory:
    @staticmethod
    def test_resolve_args():
        factory = Factory(Model)
        with pytest.raises(InvalidArguments) as _:
            factory._resolve_args()

        with pytest.raises(InvalidArguments) as _:
            factory._resolve_args('wrong_val')

        model, initial = factory._resolve_args(ModelOne)
        assert model == ModelOne
        assert isinstance(initial, tuple)
        assert initial[0] is None

    @staticmethod
    def test_verify_kwargs():
        factory = Factory(Model)

        # invalid kwarg type
        val = 'invalid type'
        with pytest.raises(InvalidArguments):
            factory._verify_kwargs(val)

        # invalid kwarg type in list
        val = ['invalid type']
        with pytest.raises(InvalidArguments):
            factory._verify_kwargs(val)

        # valid kwarg type no list
        val = {'valid': 'type'}
        factory._verify_kwargs(val)

        # valid type
        val = [{'valid': 'type'}]
        factory._verify_kwargs(val)

        # valid type, invalid type, correct length
        val = [{'valid': 'type'}, 'invalid type']
        with pytest.raises(InvalidArguments):
            factory._verify_kwargs(val)

    # Model trivial
    @staticmethod
    def test_build_trivial():
        model = build(ModelOne)
        assert isinstance(model, ModelOne)

    # Model w/ single count
    @staticmethod
    def test_build_with_single_count():
        count = 1
        args = (ModelOne, count)
        model = build(*args)
        assert isinstance(model, ModelOne)

    # Model w/ multiple count
    @staticmethod
    def test_build_with_multi_count():
        count = 2
        models = build(ModelOne, count)
        assert len(models) == count
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)
        assert models[0] != models[1]

    # Model w/ single count and initial
    @staticmethod
    def test_build_with_count_and_initial():
        initial = {
            'decimal_field': Decimal('10.00')
        }
        args = (ModelOne, initial)
        model = build(*args)
        assert isinstance(model, ModelOne)
        assert model.decimal_field == initial['decimal_field']

    # Model w/ multi count and single initial
    @staticmethod
    def test_build_with_multi_count_and_single_initial(self):
        count = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial_list = list()
        for _ in itertools.repeat(None, count):
            initial_list.append(initial1)
        args = (ModelOne, initial_list)
        models = build(*args)
        _check_models(models, count, initial1)

    # Model w/ multi count and multi initial
    @staticmethod
    def test_build_with_multi_count_and_multi_initial():
        count = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'decimal_field': Decimal('8.00')
        }
        args = (ModelOne, [initial1, initial2])
        models = build(*args)
        _check_models(models, count, initial1)

    # Multi Model Trivial
    @staticmethod
    def test_build_with_multi_model_trivial():
        models = build((ModelOne, ), (ModelTwo, ))
        assert len(models) == 2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelTwo)

    # Multi Model w/ single count
    @staticmethod
    def test_build_with_multi_model_and_single_count():
        count1 = 1
        count2 = 1
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = build(*args)
        assert len(models) == count1 + count2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelTwo)

    # Multi Model w/ multiple count
    @staticmethod
    def test_build_with_multi_model_and_multi_count():
        count1 = 2
        count2 = 3
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = build(*args)
        assert len(models) == count1 + count2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)

        assert isinstance(models[2], ModelTwo)
        assert isinstance(models[3], ModelTwo)
        assert isinstance(models[4], ModelTwo)

    # Multi Model w/ single count and initial
    @staticmethod
    def test_build_with_multi_model_and_single_count_and_single_initial():
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'char_field': 'test value'
        }
        args = ((ModelOne, initial1), (ModelTwo, initial2))
        models = build(*args)
        assert isinstance(models[0], ModelOne)
        assert models[0].decimal_field == initial1['decimal_field']

        assert isinstance(models[1], ModelTwo)
        assert models[1].char_field == initial2['char_field']

    # Multi Model w/ multi count and single initial
    @staticmethod
    def test_build_with_multi_model_and_multi_count_and_single_initial():
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
        models = build(*args)
        assert len(models) == count1 + count2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)
        assert models[0].decimal_field == initial1['decimal_field']
        assert models[1].decimal_field == initial1['decimal_field']

        assert isinstance(models[2], ModelTwo)
        assert isinstance(models[3], ModelTwo)
        assert isinstance(models[4], ModelTwo)
        assert models[2].char_field == initial2['char_field']
        assert models[3].char_field == initial2['char_field']
        assert models[4].char_field == initial2['char_field']

    # Multi Model w/ multi count and multi initial
    @staticmethod
    def test_build_with_multi_model_and_multi_count_and_multi_initial():
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
        models = build(*args)
        assert len(models) == 4
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)
        assert models[0].decimal_field == initial1_1['decimal_field']
        assert models[1].decimal_field == initial1_2['decimal_field']
        assert isinstance(models[2], ModelTwo)
        assert isinstance(models[3], ModelTwo)
        assert models[2].char_field == initial2_1['char_field']
        assert models[3].char_field == initial2_2['char_field']

    # Model trivial
    @staticmethod
    def test_create_trivial():
        models = ModelOne.objects.all()
        assert len(models) == 0

        model = create(ModelOne)
        assert isinstance(model, ModelOne)

        models = ModelOne.objects.all()
        assert len(models) == 1

    # Model w/ single count
    @staticmethod
    def test_create_with_single_count():
        models = ModelOne.objects.all()
        assert len(models) == 0

        count = 1
        args = (ModelOne, count)
        model = create(*args)
        assert isinstance(model, ModelOne)

        models = ModelOne.objects.all()
        assert len(models) == count

    # Model w/ multiple count
    @staticmethod
    def test_create_with_multi_count():
        models = ModelOne.objects.all()
        assert len(models) == 0

        count = 2
        args = (ModelOne, count)
        models = create(*args)
        assert len(models) == count
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)
        assert models[0] != models[1]

        models = ModelOne.objects.all()
        assert len(models) == count

    # Model w/ single count and initial
    @staticmethod
    def test_create_with_count_and_initial():
        models = ModelOne.objects.all()
        assert len(models) == 0

        initial = {
            'decimal_field': Decimal('10.00')
        }
        args = (ModelOne, initial)
        model = create(*args)
        assert isinstance(model, ModelOne)
        assert model.decimal_field == initial['decimal_field']

        models = ModelOne.objects.all()
        assert len(models) == 1

    # Model w/ multi count and single initial
    @staticmethod
    def test_create_with_multi_count_and_single_initial():
        models = ModelOne.objects.all()
        assert len(models) == 0

        count = 2
        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial_list = list()
        for _ in itertools.repeat(None, count):
            initial_list.append(initial1)

        args = (ModelOne, initial_list)
        models = create(*args)
        assert len(models) == count
        assert isinstance(models[0], ModelOne)
        assert models[0].decimal_field == initial1['decimal_field']
        assert isinstance(models[1], ModelOne)
        assert models[1].decimal_field == initial1['decimal_field']

        models = ModelOne.objects.all()
        assert len(models) == count

    # Model w/ multi count and multi initial
    @staticmethod
    def test_create_with_multi_count_and_multi_initial():
        models = ModelOne.objects.all()
        assert len(models) == 0

        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'decimal_field': Decimal('8.00')
        }
        args = (ModelOne, [initial1, initial2])
        models = create(*args)
        assert len(models) == 2
        assert isinstance(models[0], ModelOne)
        assert models[0].decimal_field == initial1['decimal_field']
        assert isinstance(models[1], ModelOne)
        assert models[1].decimal_field == initial2['decimal_field']

        models = ModelOne.objects.all()
        assert len(models) == 2

    # Multi Model Trivial
    @staticmethod
    def test_create_with_multi_model_trivial():
        models = ModelOne.objects.all()
        assert len(models) == 0
        models = ModelTwo.objects.all()
        assert len(models) == 0

        models = create((ModelOne, ), (ModelTwo, ))
        assert len(models) == 2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelTwo)

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect 2
        models = ModelOne.objects.all()
        assert len(models) == 2
        models = ModelTwo.objects.all()
        assert len(models) == 1

    # Multi Model w/ single count
    @staticmethod
    def test_create_with_multi_model_and_single_count():
        models = ModelOne.objects.all()
        assert len(models) == 0
        models = ModelTwo.objects.all()
        assert len(models) == 0

        count1 = 1
        count2 = 1
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = create(*args)
        assert len(models), count1 + count2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelTwo)

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect 2
        models = ModelOne.objects.all()
        assert len(models) == count1 + count2
        models = ModelTwo.objects.all()
        assert len(models) == 1

    # Multi Model w/ multiple count
    @staticmethod
    def test_create_with_multi_model_and_multi_count():
        models = ModelOne.objects.all()
        assert len(models) == 0
        models = ModelTwo.objects.all()
        assert len(models) == 0

        count1 = 2
        count2 = 3
        args = ((ModelOne, count1), (ModelTwo, count2))
        models = create(*args)
        assert len(models) == count1 + count2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)

        assert isinstance(models[2], ModelTwo)
        assert isinstance(models[3], ModelTwo)
        assert isinstance(models[4], ModelTwo)

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models (count1)
        # 1 for each OneToOne fields (count2)
        models = ModelOne.objects.all()
        assert len(models) == count1 + count2
        models = ModelTwo.objects.all()
        assert len(models) == count2

    # Multi Model w/ single count and initial
    @staticmethod
    def test_create_with_multi_model_and_single_count_and_single_initial():
        models = ModelOne.objects.all()
        assert len(models) == 0
        models = ModelTwo.objects.all()
        assert len(models) == 0

        initial1 = {
            'decimal_field': Decimal('10.00')
        }
        initial2 = {
            'char_field': 'test value'
        }
        args = ((ModelOne, initial1), (ModelTwo, initial2))
        models = create(*args)
        assert isinstance(models[0], ModelOne)
        assert models[0].decimal_field == initial1['decimal_field']

        assert isinstance(models[1], ModelTwo)
        assert models[1].char_field == initial2['char_field']

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models
        # 1 for each OneToOne fields
        models = ModelOne.objects.all()
        assert len(models) == 2
        models = ModelTwo.objects.all()
        assert len(models) == 1

    # Multi Model w/ multi count and single initial
    @staticmethod
    def test_create_with_multi_model_and_multi_count_and_single_initial():
        models = ModelOne.objects.all()
        assert len(models) == 0
        models = ModelTwo.objects.all()
        assert len(models) == 0

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
        models = create(*args)
        assert len(models) == count1 + count2
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)
        assert models[0].decimal_field == initial1['decimal_field']
        assert models[1].decimal_field == initial1['decimal_field']

        assert isinstance(models[2], ModelTwo)
        assert isinstance(models[3], ModelTwo)
        assert isinstance(models[4], ModelTwo)
        assert models[2].char_field == initial2['char_field']
        assert models[3].char_field == initial2['char_field']
        assert models[4].char_field == initial2['char_field']

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models (count1)
        # 1 for each OneToOne fields (count2)
        models = ModelOne.objects.all()
        assert len(models) == count1 + count2
        models = ModelTwo.objects.all()
        assert len(models) == count2

    # Multi Model w/ multi count and multi initial
    @staticmethod
    def test_create_with_multi_model_and_multi_count_and_multi_initial():
        models = ModelOne.objects.all()
        assert len(models) == 0
        models = ModelTwo.objects.all()
        assert len(models) == 0

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
        models = create(*args)
        assert len(models) == 4
        assert isinstance(models[0], ModelOne)
        assert isinstance(models[1], ModelOne)
        assert models[0].decimal_field == initial1_1['decimal_field']
        assert models[1].decimal_field == initial1_2['decimal_field']
        assert isinstance(models[2], ModelTwo)
        assert isinstance(models[3], ModelTwo)
        assert models[2].char_field == initial2_1['char_field']
        assert models[3].char_field == initial2_2['char_field']

        # Since ModelTwo has a FK and OneToOne to ModelOne we expect:
        # 1 for the count in the factory models (count1)
        # 1 for each OneToOne fields (count2)
        models = ModelOne.objects.all()
        assert len(models) == 4
        models = ModelTwo.objects.all()
        assert len(models) == 2
