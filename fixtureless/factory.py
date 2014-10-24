import inspect
import itertools

from django.db.models import Model

from fixtureless import exceptions
from fixtureless.generator import create_instance
from fixtureless.utils import list_get


class Factory(object):

    def _verify_kwargs(self, vals):
        def _error_nondict(x):
            if not isinstance(x, dict) and x is not None:
                raise exceptions.InvalidArguments(
                    'The fixtureless factory expected kwargs of type dict'
                    ' and was given type {}'.format(type(x)))

        if isinstance(vals, (list, tuple)):
            for x in vals:
                _error_nondict(x)
        else:
            _error_nondict(vals)

    def _handle_second_arg(self, *args):
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
            if inspect.isclass(args[0]) and issubclass(args[0], Model):
                model = args[0]
            else:
                raise exceptions.InvalidArguments()
        except (IndexError, exceptions.InvalidArguments):
            msg = 'The fixtureless factory expects a Django model ({}) as' \
                  ' the first argument.'.format(type(Model))
            raise exceptions.InvalidArguments(msg)
        kwargs_iter = self._handle_second_arg(*args)
        self._verify_kwargs(kwargs_iter)
        return model, kwargs_iter

    def _build_instance(self, model, kwargs, create):
        if kwargs is not None:
            obj = create_instance(model, **kwargs)
        else:
            obj = create_instance(model)
        if create:
            obj.save()
        return obj

    def _handle_build(self, *args, **kwargs):
        create = kwargs.get('create', False)
        model, kwargs_iter = self._resolve_args(*args)
        return (self._build_instance(model, kwargs, create)
                for kwargs in kwargs_iter)

    def create(self, *args):
        if inspect.isclass(args[0]) and issubclass(args[0], Model):
            args = (args,)
        builds = (self._handle_build(*sub_args, create=True)
                  for sub_args in args)
        objs = tuple(itertools.chain.from_iterable(builds))
        return objs if len(objs) > 1 else objs[0]

    def build(self, *args):
        if inspect.isclass(args[0]) and issubclass(args[0], Model):
            args = (args,)
        builds = itertools.starmap(self._handle_build, args)
        objs = tuple(itertools.chain.from_iterable(builds))
        return objs if len(objs) > 1 else objs[0]
