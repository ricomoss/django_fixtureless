

def list_get(array, index, default=None):
    try:
        return array[index]
    except IndexError:
        return default
