import itertools
import inspect

from django.db.models import Model

import exceptions
from generator import create_instance
from utils import list_get


class Factory(object):
    def _verify_kwargs(self, vals, count):
        if isinstance(vals, (list, tuple)):
            if count != len(vals):
                msg = 'The fixtureless factory cannot build {} objects with' \
                      ' {} kwargs values.'.format(count, len(vals))
                raise exceptions.InvalidArguments(msg)
            for val in vals:
                if isinstance(val, dict) or val is None:
                    continue
                msg = 'The fixturless factory expected kwargs of type dict' \
                      ' and was given type {}'.format(type(val))
                raise exceptions.InvalidArguments(msg)
        elif not isinstance(vals, dict) and vals is not None:
            msg = 'The fixturless factory expected kwargs of type dict' \
                  ' and was given type {}'.format(type(vals))
            raise exceptions.InvalidArguments(msg)

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
        count = list_get(args, 1, 1)
        kwargs = list_get(args, 2)
        self._verify_kwargs(kwargs, count)
        return model, count, kwargs

    def _build_instance(self, model, kwargs, objs, create):
        if kwargs is not None:
            obj = create_instance(model, **kwargs)
        else:
            obj = create_instance(model)
        if create:
            obj.save()
        objs.append(obj)

    def _handle_build(self, *args, objs=None, create=False):
        model, count, kwargs = self._resolve_args(*args)
        if isinstance(kwargs, (list, tuple)):
            for sub_kwargs in kwargs:
                self._build_instance(model, sub_kwargs, objs, create)
        else:
            for _ in itertools.repeat(None, count):
                self._build_instance(model, kwargs, objs, create)
        return objs

    def create(self, *args):
        objs = list()
        if inspect.isclass(args[0]) and issubclass(args[0], Model):
            models = self._handle_build(*args, objs=objs, create=True)
            if len(models) == 1:
                return models[0]
            else:
                return models
        for sub_args in args:
            self._handle_build(*sub_args, objs=objs, create=True)
        return objs

    def build(self, *args):
        objs = list()
        if inspect.isclass(args[0]) and issubclass(args[0], Model):
            models = self._handle_build(*args, objs=objs)
            if len(models) == 1:
                return models[0]
            else:
                return models
        for sub_args in args:
            self._handle_build(*sub_args, objs=objs)
        return objs

