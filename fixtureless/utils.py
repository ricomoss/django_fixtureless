"""
Utility functions
"""
import functools
import random
import warnings

from fixtureless.constants import CHARFIELD_CHARSET_ASCII


def random_str(val_len, char_set):
    """
    Random string generator

    :param val_len: The length required
    :param char_set: The character set to choose from
    :return: A random string
    """
    return ''.join(map(random.choice, (char_set,) * val_len))


def list_get(array, index, default=None):
    """
    A dict.get() style helper method.

    :param array: Array to extract from
    :param index: Index to extract
    :param default: The value to default to, if the index isn't available.
    :return: The array value, if available; the default value otherwise.
    """
    try:
        return array[index]
    except IndexError:
        return default


def get_random_dict():
    """
    Generate a random dictionary object.

    :return: A random dictionary object
    """
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
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    :param func: Function to have the deprecation warning.
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        """
        Wrapper for the func

        :param args: Arguments passed to the function
        :param kwargs: Keyword arguments passed to the function.
        :return: The results of calling the function.
        """
        # turn off filter
        warnings.simplefilter('always', DeprecationWarning)
        warnings.warn(
            f'Call to deprecated function {func.__name__}.', category=DeprecationWarning,
            stacklevel=2)

        # reset filter
        warnings.simplefilter('default', DeprecationWarning)
        return func(*args, **kwargs)

    return new_func
