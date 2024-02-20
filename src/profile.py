from typing import Dict,Any


"""
https://developers.facebook.com/docs/messenger-platform/discovery/welcome-screen
https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/
https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/commands
"""



def Profile(greeting:str=None,commands:Dict[str,str]=None) -> Dict[str,Any]:
    output = dict()

    if type(greeting) is not str and greeting is not None:
        raise TypeError("`greeting` must be a str")

    if type(commands) is not dict and commands is not None:
        raise TypeError("`commands` must be a Dict[str,str]")

    _greeting = []
    _commands = []

    if greeting is not None:
        msg = {"locale":"default","text":greeting}
        _greeting.append(msg)

    if commands is not None:
        for name,desc in commands.items():
            if not isinstance(name,str) or not isinstance(desc,str):
                raise SyntaxError("Argument `name` and `desc` must be a str")
            msg = {"name":name,"description": desc}
            _commands.append(msg)

    if _greeting != []:
        output['greeting'] = _greeting
    if _commands != []:
        output['commands'] = _commands

    return output
