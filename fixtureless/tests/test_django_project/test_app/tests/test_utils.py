from fixtureless.utils import list_get


class ListGetTest:
    @staticmethod
    def test_list_get():
        array = list()
        index = 0
        val = list_get(array, index)
        assert val is None

        val = list_get(array, index, 'test')
        assert val == 'test'

        array = [1, 2]
        val = list_get(array, index)
        assert val == 1
