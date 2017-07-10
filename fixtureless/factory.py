import inspect
import itertools

from django.db.models import Model
from django.forms import Form

from fixtureless import exceptions
from fixtureless import generator
from fixtureless.utils import list_get


class Factory(object):
    def __init__(self, obj_type):
        self.obj_type = obj_type

    @staticmethod
    def _verify_kwargs(vals):
        def _error_nondict(x_0):
            if not isinstance(x_0, dict) and x_0 is not None:
                raise exceptions.InvalidArguments(
                    'The fixtureless factory expected kwargs of type dict'
                    ' and was given type {}'.format(type(x_0)))

        if isinstance(vals, (list, tuple)):
            for x in vals:
                _error_nondict(x)
        else:
            _error_nondict(vals)

    @staticmethod
    def _handle_second_arg(*args):
        sec_arg = list_get(args, 1)
        count = 1
        kwargs = None
        if isinstance(sec_arg, int):
            count = sec_arg
        elif isinstance(sec_arg, (list, tuple)):
            return sec_arg
        elif isinstance(sec_arg, dict):
            kwargs = sec_arg
        return (kwargs,) * count

    def _resolve_args(self, *args):
        try:
            if inspect.isclass(args[0]) and issubclass(args[0], self.obj_type):
                model = args[0]
            else:
                raise exceptions.InvalidArguments()
        except (IndexError, exceptions.InvalidArguments):
            msg = 'The fixtureless factory expects a Django model ({}) as' \
                  ' the first argument.'.format(type(self.obj_type))
            raise exceptions.InvalidArguments(msg)
        kwargs_iter = self._handle_second_arg(*args)
        self._verify_kwargs(kwargs_iter)
        return model, kwargs_iter

    def _create_instance(self, *args, **kwargs):
        name = self.obj_type.__name__.lower()
        func = getattr(generator, 'create_{}_instance'.format(name))
        if func:
            return func(*args, **kwargs)
        raise NotImplemented('There are no generator create methods for {} type'.format(name))

    def _handle_build(self, *args):
        instance, kwargs_iter = self._resolve_args(*args)
        return (self._create_instance(instance, **(kwargs if kwargs else {}))
                for kwargs in kwargs_iter)

    def _order_and_build(self, *args):
        if inspect.isclass(args[0]) and issubclass(args[0], self.obj_type):
            args = (args,)
        builds = itertools.starmap(self._handle_build, args)
        return itertools.chain.from_iterable(builds)

    def _deliver(self, *args, **kwargs):
        pipeline = self._order_and_build(*args)
        objs = tuple(self.save_instances(pipeline) if kwargs['save'] else pipeline)
        return objs if len(objs) > 1 else objs[0]

    def create(self, *args):
        return self._deliver(*args, save=True)

    def build(self, *args):
        return self._deliver(*args, save=False)

    @staticmethod
    def save_instances(iterable):
        for instance in iterable:
            instance.save()
            yield instance


def create(*args):
    """
    This is the preferred interface for using fixtureless
    :param args: Arguments are parsed in the factory.
    :return: A (saved) model instance or list depending on the args
    """
    return Factory(Model).create(*args)


def build(*args):
    """
    This is the preferred interface for using fixtureless
    :param args: Arguments are parsed in the factory.
    :return: A model instance or list depending on the args
    """
    return Factory(Model).build(*args)


def create_form(*args):
    """
    This is the preferred interface for using fixtureless
    :param args: Arguments are parsed in the factory.
    :return: A form instance or list depending on the args
    """
    return Factory(Form).create(*args)


def build_form(*args):
    """
    This is the preferred interface for using fixtureless
    :param args: Arguments are parsed in the factory.
    :return: A form instance or list depending on the args
    """
    return Factory(Form).build(*args)
