import random

from fixtureless.constants import CHARFIELD_CHARSET_ASCII


def random_str(val_len, char_set):
    return ''.join(map(random.choice, (char_set,) * val_len))

def list_get(array, index, default=None):
    try:
        return array[index]
    except IndexError:
        return default


def get_random_dict():
    random_dict = {}
    more_keys = True
    while more_keys:
        key = random_str(5, CHARFIELD_CHARSET_ASCII)
        value = random_str(5, CHARFIELD_CHARSET_ASCII)
        random_dict[key] = value
        if random.choice([True, False]):
            more_keys = False
    return random_dict