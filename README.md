# Messenger-Bot
Messenger bot wrote in python


How to add command?

    from MessengerApi import Messenger,Button,Context
    token = "YOUR-PAGE-TOKEN"
    mess = Messenger(token)
    
    @mess.command("help")
    def _help(ctx:Context):
        button = Button(mess.commands)
        ctx.send("All commands below,buttons=button)
        return None

How to add "Cog" command?

    from MessengerApi import Messenger,Cog,Context
    token = "YOUR-PAGE-TOKEN"
    mess = Messenger(token)

    @mess.cog("help")
    class _help(Cog):
    
        def before_invoke(self,ctx:Context) -> None:
            pass
            
        def invoke(self,ctx:Context) -> None:
            pass
            
        def after_invoke(self,ctx:Context) -> None:
            pass


Decorator "on_message" is activated when someone has written something

Decorator "on_start" the decorator is activated at the very beginning of the "run" function


tree of invoking commands and cog and "on_start"

-"on_start"

-"on_message"

-Command -> "before_invoke" decorator -> "before_invoke" -> "invoke" -> "after_invoke" -> "after_invoke" decorator

-Cog -> "before_invoke" -> "invoke" -> "after_invoke"
    



    
