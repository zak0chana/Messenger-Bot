from .context import Context

class Cog:
    def __init__(self):
        pass # self._ctx = context

    def before_invoke(self,ctx:Context) -> None:
        pass

    def invoke(self,ctx:Context) -> None:
        pass

    def after_invoke(self,ctx:Context) -> None:
        pass

    def __repr__(self): # useless but yes
        return self.__class__.__name__

