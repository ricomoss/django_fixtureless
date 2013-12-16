import itertools
import inspect

from django.db.models import Model

import exceptions
from generator import create_instance
from utils import list_get


class Factory(object):
    def _handle_kwargs(self, vals, count):
        pass

    def _resolve_args(self, *args):
        try:
            if inspect.isclass(args[0]) and issubclass(args[0], Model):
                model = args[0]
            else:
                raise exceptions.InvalidArguments()
        except (IndexError, exceptions.InvalidArguments):
            msg = 'The fixtureless factory expects a Django model ({}) as' \
                  ' the first argument.'
            raise exceptions.InvalidArguments(msg.format(type(Model)))
        count = list_get(args, 1, 1)
        vals = list_get(args, 2)
        kwargs = self._handle_kwargs(vals, count)
        return model, count, kwargs

    def _handle_build(self, *args, objs=None, create=False):
        model, count, kwargs = self._resolve_args(*args)
        for _ in itertools.repeat(None, count):
            if kwargs is not None:
                obj = create_instance(model, **kwargs)
            else:
                obj = create_instance(model)
            if create:
                obj.save()
            if objs is not None:
                objs.append(obj)
            else:
                return obj

    def create(self, *args):
        if issubclass(args[0], Model):
            return self._handle_build(*args, create=True)
        objs = list()
        for sub_args in args:
            self._handle_build(*sub_args, objs=objs, create=True)
        return objs

    def build(self, *args):
        if issubclass(args[0], Model):
            obj = self._handle_build(*args)
            return obj
        objs = list()
        for sub_args in args:
            objs = self._handle_build(*sub_args, objs=objs)
        return objs

