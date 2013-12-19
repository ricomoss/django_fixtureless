from django.test import TestCase

from fixtureless.utils import list_get


class ListGetTest(TestCase):
    def test_list_get(self):
        array = list()
        index = 0
        val = list_get(array, index)
        self.assertIsNone(val)

        val = list_get(array, index, 'test')
        self.assertEqual(val, 'test')

        array = [1, 2]
        val = list_get(array, index)
        self.assertEqual(val, 1)
