from typing import Callable,Union,Type
import inspect

from .context import Context


def _EmptyFunc(ctx):
    pass


class Command:

    def __init__(self,func,name):
        self._func: Callable[[Context],None] = func # _FunctionType
        self.name = name # command name


    def before_invoke(self,ctx:Context):
        return _EmptyFunc(ctx)


    def invoke(self,ctx:Context):
        return self._func(ctx)


    def after_invoke(self,ctx:Context):
        return _EmptyFunc(ctx)


    def __eq__(self, other:Type["Command"]) -> bool:
        """ Return self==value.
        this function check attr: `name`, `_func`
        """
        if not hasattr(other, 'name'):
            return self.name == other
        return self.name == other.name


    def __ne__(self, other) -> bool:
        """ Return self!=value."""
        return not self.__eq__(other)


    def __repr__(self):
        name = self.name
        return f"Command{name=})"
