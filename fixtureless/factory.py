"""
File for handling factory and build/create
"""
import inspect
import itertools

from django.db.models import Model
from django.forms import Form

from fixtureless import exceptions
from fixtureless import generator
from fixtureless.utils import list_get


class Factory:
    """
    Factory for building objects
    """
    def __init__(self, obj_type):
        self.obj_type = obj_type

    @staticmethod
    def _verify_kwargs(arguments):
        """
        Verify the kwargs are as expected

        :param arguments: The values passed in
        """
        def _error_nondict(arg_0):
            if not isinstance(arg_0, dict) and arg_0 is not None:
                raise exceptions.InvalidArguments(
                    f'The fixtureless factory expected kwargs of type dict'
                    f' and was given type {type(arg_0)}')

        if isinstance(arguments, (list, tuple)):
            for arg in arguments:
                _error_nondict(arg)
        else:
            _error_nondict(arguments)

    @staticmethod
    def _handle_second_arg(*args):
        """
        Handle the second argument based on type

        :param args: Arguments passed in
        :return: The arguments as expected by the create/build
        """
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
        """
        Resolve the arguments passed

        :param args: Arguments passed
        :return: A tuple with the model and kwargs iterator
        """
        try:
            if inspect.isclass(args[0]) and issubclass(args[0], self.obj_type):
                model = args[0]
            else:
                raise exceptions.InvalidArguments()
        except (IndexError, exceptions.InvalidArguments):
            msg = f'The fixtureless factory expects a Django model ({type(self.obj_type)}) as' \
                  ' the first argument.'
            raise exceptions.InvalidArguments(msg)
        kwargs_iter = self._handle_second_arg(*args)
        self._verify_kwargs(kwargs_iter)
        return model, kwargs_iter

    def _create_instance(self, *args, **kwargs):
        """
        Creates a list of objects

        :param args: Arguments passed
        :param kwargs: Keyword arguments passed
        :return: An instance of the object created
        """
        name = self.obj_type.__name__.lower()
        func = getattr(generator, f'create_{name}_instance')
        if func:
            return func(*args, **kwargs)
        raise NotImplementedError(
            f'There are no generator create methods for {name} type')

    def _handle_build(self, *args):
        """
        Creates a list of objects

        :param args: Arguments passed
        :return: A list of the objects created and kwargs
        """
        instance, kwargs_iter = self._resolve_args(*args)
        return (self._create_instance(instance, **(kwargs if kwargs else {}))
                for kwargs in kwargs_iter)

    def _order_and_build(self, *args):
        """
        Orders the work and kicks off the build

        :param args: Arguments passed
        :return: A list of the instances of the object created
        """
        if inspect.isclass(args[0]) and issubclass(args[0], self.obj_type):
            args = (args,)
        builds = itertools.starmap(self._handle_build, args)
        return itertools.chain.from_iterable(builds)

    def _deliver(self, *args, **kwargs):
        """
        Handler for create or build operations.

        :param args: Arguments passed
        :param kwargs: Keyword arguments passed
        :return: The objects created (can be a list).
        """
        pipeline = self._order_and_build(*args)
        objs = tuple(self.save_instances(pipeline) if kwargs['save'] else pipeline)
        return objs if len(objs) > 1 else objs[0]

    def create(self, *args):
        """
        Entrypoint for creating objects and saving them to the DB.

        :param args: Arguments passed
        :return: The objects created (can be a list).
        """
        return self._deliver(*args, save=True)

    def build(self, *args):
        """
        Entrypoint for creating objects without saving them to the DB.

        :param args: Arguments passed
        :return: The objects created (can be a list).
        """
        return self._deliver(*args, save=False)

    @staticmethod
    def save_instances(iterable):
        """
        Generator for saving instances to the DB

        :param iterable: An iterable of object types with a well defined save method
        :return: The instance of the current object.
        """
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
