from typing import Callable

from .context import Context


def _EmptyFunc(ctx):
    pass


class Command:
    __invoked = False
    def __init__(self,func):
        self._func: Callable[[Context],None] = func
        self.name = self._func.__name__ # function name
        self.__orginal_name:str = ... # defined later; see __call__

    @property
    def orginal_name(self) -> str:
        return self.__orginal_name # command name

    @orginal_name.setter
    def orginal_name(self,*args,**kwargs):
        raise AttributeError("You cannot change orginal name")


    def before_invoke(self,ctx:Context):
        return _EmptyFunc(ctx)


    def invoke(self,ctx:Context):
        return self._func(ctx)


    def after_invoke(self,ctx:Context):
        return _EmptyFunc(ctx)


    def __call__(self, name):
        if not self.__invoked:
            self.__invoked = True
            self.__orginal_name = name
            return self
        raise AttributeError('function `__call__` can be invoke once')


    def __eq__(self, other:"Command"):
        if not hasattr(other,'_func'):
            return self._func == other
        return self._func == other._func

    def __ne__(self, other):
        return not self.__eq__(other)


    def __repr__(self):
        name = self.name
        return "Command(name={})".format(name)







