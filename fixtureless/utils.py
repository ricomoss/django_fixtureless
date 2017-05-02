import functools
import random
import warnings

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


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        # turn off filter
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn(
            "Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning,
            stacklevel=2)

        # reset filter
        warnings.simplefilter('default', DeprecationWarning)
        return func(*args, **kwargs)

    return new_func
