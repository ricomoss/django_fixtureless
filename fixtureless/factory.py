import inspect
import itertools

from django.db.models import Model

from fixtureless import exceptions
from fixtureless.generator import create_instance
from fixtureless.utils import list_get


class Factory(object):

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

    def _handle_build(self, *args):
        model, kwargs_iter = self._resolve_args(*args)
        return (create_instance(model, **(kwargs if kwargs else {}))
                for kwargs in kwargs_iter)

    def _order_and_build(self, *args):
        if inspect.isclass(args[0]) and issubclass(args[0], Model):
            args = (args,)
        builds = itertools.starmap(self._handle_build, args)
        return itertools.chain.from_iterable(builds)

    def _deliver(self, *args, **kwargs):
        pipeline = self._order_and_build(*args)
        objs = tuple(save_instances(pipeline) if kwargs['save'] else pipeline)
        return objs if len(objs) > 1 else objs[0]

    def create(self, *args):
        return self._deliver(*args, save=True)

    def build(self, *args):
        return self._deliver(*args, save=False)


def save_instances(iterable):
    for instance in iterable:
        instance.save()
        yield instance
