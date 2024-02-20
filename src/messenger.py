import inspect
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Callable, List, Union, Type
import requests

from .cog import Cog
from .context import Context
from .utils import MessageData, UserData
from .command import Command as _Command


logging.basicConfig(level=logging.INFO, format='%(message)s - %(name)s - %(asctime)s')
_logger = logging.getLogger(__name__)



class Messenger:
    def __init__(self, token, prefix='', api_version="v19.0"):
        self.token = token
        self.api_version = api_version
        self.url = f"https://graph.facebook.com"

        self._prefix: str = prefix

        self._before_inv: Callable[[Context], None] = None
        self._after_inv: Callable[[Context], None] = None
        self._event: Callable[[Context], None] = None
        self._on_start: Callable[[None], Dict[str, Any]] = None
        self._function: Dict[str, Callable] = dict()
        self._cogs: Dict[str, Cog] = dict()

        self._page_name: str = ...  # defined later / see function `page_name`
        self._page_id: str = ...  # defined later / see function `page_id`

        if self._prefix:
            self.__check_prefix()

    def sendRequest(self, method: str, path: str = '', **kwargs) -> requests.Response:
        url = self.url + path

        try:
            req = requests.request(method, url, **kwargs)
            req.raise_for_status()
            return req
        except KeyboardInterrupt:
            raise SystemExit
        except Exception as err:
            raise err

    @property
    def page_name(self) -> str:
        if self._page_name is Ellipsis:
            self.__getPageIdAndName()
        return self._page_name

    @property
    def page_id(self) -> str:
        if self._page_id is Ellipsis:
            self.__getPageIdAndName()
        return self._page_id

    def __getPageIdAndName(self) -> None:
        """
        This method is used to get the page id/name of the facebook page
        """
        req = self.sendRequest("GET", f'/{self.api_version}/me', params={"access_token": self.token})
        data = req.json()
        self._page_id: str = data['id']
        self._page_name: str = data['name']

    def subscribed_apps(self, obj: str) -> Dict[str, Any]:  # TODO chyba dziala
        """ https://developers.facebook.com/docs/pages-api/webhooks-for-pages """
        if not isinstance(obj, str):
            raise TypeError("Argument `obj` must be a str")

        params = {"access_token": self.token, 'subscribed_fields': obj}
        req = self.sendRequest("GET", f'/{self.page_id}/subscribed_apps', params=params)
        return req.json()


    def get_label(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Argument `text` must be a str")
        dataJSON = {"page_label_name": text}
        params = {"access_token": self.token}
        req = self.sendRequest("POST", f"/{self.api_version}/me/custom_labels", json=dataJSON, params=params)
        return req.json()['id']

    def set_label(self, sender:Union[str, int] ,id: Union[str, int]) -> None:
        if not isinstance(sender, (str, int)):
            raise TypeError("Argument `sender` must be Union[str,int]")
        if not isinstance(id, (str, int)):
            raise TypeError("Argument `id` must be Union[str,int]")

        params = {"access_token": self.token}
        dataJSON = {"user": sender}
        req = self.sendRequest("POST", f"/{self.api_version}/{id}/label", json=dataJSON, params=params)

    def remove_label(self, sender: Union[str, int], id: Union[str, int]) -> None:
        if not isinstance(sender, (str, int)):
            raise TypeError("Argument `sender` must be Union[str,int]")
        if not isinstance(id, (str, int)):
            raise TypeError("Argument `id` must be Union[str,int]")
        params = {"access_token": self.token, 'user': self.sender}
        req = self.sendRequest("DELETE", f"/{self.api_version}/{id}/label", params=params)


    def _get_conversations_id(self) -> List[str]:
        params = {"access_token": self.token}
        req = self.sendRequest("GET", f'/{self.api_version}/{self.page_id}/conversations', params=params)

        data = req.json()['data']
        conversationsID = [i['id'] for i in data]

        return conversationsID

    def _get_messages_from_convesation(self, id: Union[str,int]) -> dict:
        params = {"access_token": self.token, 'fields': 'messages'}
        req = self.sendRequest("GET", f'/{self.api_version}/{id}', params=params)
        data = req.json()
        return data

    def _get_message_id(self, id: Union[str,int]) -> dict:
        params = {"access_token": self.token, 'fields': 'id,created_time,from,to,message'}
        req = self.sendRequest("GET", f'/{self.api_version}/{id}', params=params)
        return req.json()

    def __getmessages__(self) -> List[MessageData]:
        res = []
        _result = []
        conversationsID = self._get_conversations_id()
        for message in conversationsID:
            result = self._get_messages_from_convesation(message)
            res.append(result['messages']['data'][0]['id'])
        for id_sender in res:
            data = self._get_message_id(id_sender)
            # print(data)
            y = {"id_sender": data['from']['id'], "message_context": data['message'],
                 "created_time": data['created_time'], "name": data['to']['data'][0]['name'],
                 "from_": data['from']['name'], "message_token_sender": data['id']}
            output = MessageData(**y)
            _result.append(output)

        return _result

    def ListOfTokens(self) -> dict:  # TODO nie wiem co to robi ale chyba dziala
        params = {"access_token": self.token}
        req = self.sendRequest("GET", f"/{self.api_version}/{self.page_id}/notification_message_tokens", params=params)

        return req.json()

    def getUsername(self, PSID: Union[str,int] = '24805863585724940') -> UserData:
        """ https://developers.facebook.com/docs/messenger-platform/identity/user-profile """
        params = {"access_token": self.token,'fields': 'first_name,last_name,name,profile_pic,id,locale,timezone'}

        req = self.sendRequest("GET", f"/{PSID}", params=params)
        data = req.json()
        return UserData(**data)

    @property
    def commands(self) -> set:
        result = set()
        for k, v in self._function.items():
            if v is not None:
                result.add(k)
        return result

    @property
    def cogs(self) -> set:
        result = set()
        for k, v in self._cogs.items():
            if v is not None:
                result.add(k)
        return result

    def set_messenger_profile(self, **kwargs):  # TODO

        url = f'/{self.api_version}/me/messenger_profile?access_token={self.token}'

        greeting = kwargs.get("greeting", False)
        commands = kwargs.get("commands", False)

        if greeting and isinstance(greeting, list):
            dataJSON = {"greeting": greeting}
            req = self.sendRequest('POST', url, json=dataJSON)
            print(req.json())

        if commands and isinstance(commands, list):
            dataJSON = {"commands": [{"locale": "default", "commands": commands}]}
            req = self.sendRequest("POST", url, json=dataJSON)
            print(req.json())

    def get_messenger_profile(self) -> Dict[str, Any]:
        params = {"access_token": self.token, 'fields': 'whitelisted_domains,greeting,commands'}
        req = self.sendRequest("GET", f'/{self.api_version}/me/messenger_profile', params=params)
        return req.json()

    def run(self):
        if self.commands == set() and self._event is None and self.cogs == set():
            raise RuntimeError("no command/cog are added")

        if self._on_start is not None:
            _logger.info("Setup `on_start`")
            on_start_func = self._on_start()

            if isinstance(on_start_func, dict):
                self.set_messenger_profile(**on_start_func)

            elif on_start_func == None:
                dataJSON = {
                    'fields': ['GET_STARTED', 'PERSISTENT_MENU', 'TARGET_AUDIENCE', 'WHITELISTED_DOMAINS', 'GREETING',
                               'ACCOUNT_LINKING_URL', 'PAYMENT_SETTINGS', 'ICE_BREAKERS', 'PLATFORM',
                               'SUBJECT_TO_NEW_EU_PRIVACY_RULES', 'TITLE', 'DESCRIPTION', 'COMMANDS']}
                params = {"access_token": self.token}
                if self.get_messenger_profile()['data'] != []:
                    req = self.sendRequest('DELETE', f'/{self.api_version}/me/messenger_profile', json=dataJSON,
                                           params=params)
                    print(req.json())
            else:
                raise TypeError("function `on_start` must return `None` or `Dict[str,Any]`")

        _logger.info("Starting...")

        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')

        while True:
            for data in self.__getmessages__():

                command_name: str = data.message_context.split(' ')[0].removeprefix(self._prefix)

                preparedCtx = {"token": self.token, "sender_id": data.id_sender,"api":self.api_version,
                               "command": command_name, "context": data.message_context, "username": data.from_,
                               "created_time": data.created_time, "message_token_sender": data.message_token_sender}
                ctx = Context(**preparedCtx)

                check_data:bool = (datetime.strptime(current_date, "%Y-%m-%dT%H:%M:%S%z") < datetime.strptime(
                    data.created_time, "%Y-%m-%dT%H:%M:%S%z"))

                if self._prefix != '':
                    check_prefix = data.message_context.startswith(self._prefix)
                else:
                    check_prefix = True

                if (self._event is not None and data.from_ != self.page_name and check_data): # event
                    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
                    self._event(ctx)


                if (command_name in self.commands and data.from_ != self.page_name and check_data and check_prefix): # function

                    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')

                    func: Type[_Command] = self._function[command_name]

                    if self._before_inv:
                        self._before_inv(ctx)

                    func.before_invoke(ctx)
                    func.invoke(ctx)
                    func.after_invoke(ctx)

                    if self._after_inv:
                        self._after_inv(ctx)


                if (command_name in self.cogs and data.from_ != self.page_name and check_data and check_prefix): # cog
                    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')

                    cog_invoke: Type[Cog] = self._cogs[command_name]

                    cog = cog_invoke()

                    cog.before_invoke(ctx)
                    cog.invoke(ctx)
                    cog.after_invoke(ctx)


    def __check_prefix(self) -> None:
        if type(self._prefix) is not str:
            raise TypeError("`prefix` must be a str")

        if ' ' in self._prefix:
            raise SyntaxError("`space` is not allowed in prefix") #  a moze nie ?



    def on_start(self, cls=None, /) -> None:
        """
        no context in this function
        """

        def wrapper(func):
            if inspect.iscoroutinefunction(func):
                raise TypeError("Function cannot be a coroutine function")

            if not inspect.isfunction(func):
                raise TypeError("This decoration function can be use only for function")

            if self._on_start is not None:
                raise TypeError("decorator `on_start` is used")

            self._on_start = func

        if cls is None:
            return wrapper

        return wrapper(cls)

    def on_message(self, cls=None, /) -> None:
        """
        dekorator wtedy kiedy cokolwiek zostalo napisane

        """

        def wrapper(func):
            if inspect.iscoroutinefunction(func):
                raise TypeError("Function cannot be a coroutine function")

            if not inspect.isfunction(func):
                raise TypeError("This decoration function can be use only for function")

            if self._event is not None:
                raise TypeError("decorator `on_message` is used")

            self._event = func

        if cls is None:
            return wrapper

        return wrapper(cls)

    def after_invoke(self, cls=None, /) -> None:
        def wrapper(func):
            if inspect.iscoroutinefunction(func):
                raise TypeError("Function cannot be a coroutine function")

            if not inspect.isfunction(func):
                raise TypeError("This decoration function can be use only for function")

            if self._after_inv is not None:
                raise TypeError("decorator `after_invoke` is used")

            self._after_inv = func

        if cls is None:
            return wrapper

        return wrapper(cls)

    def before_invoke(self, cls=None, /) -> None:
        def wrapper(func):

            if inspect.iscoroutinefunction(func):
                raise TypeError("Function cannot be a coroutine")

            if not inspect.isfunction(func):
                raise TypeError("This decoration function can be use only for function")

            if self._before_inv is not None:
                raise TypeError("decorator `before_invoke` is used")

            self._before_inv = func

        if cls is None:
            return wrapper

        return wrapper(cls)


    def add_cog(self, name: str, cog: Cog) -> None:
        if ' ' in name:
            raise SyntaxError("`space` is not allowed in cog name")

        if not inspect.isclass(cog):
            raise TypeError("`cog` must be a class")

        if not issubclass(cog, Cog):
            raise TypeError("`cog` must be subclass of `Cog`")

        if name in self.cogs:
            raise TypeError("this name cog is reserved")

        self._cogs[name] = cog


    def add_command(self,command:_Command):
        if not isinstance(command,_Command):
            raise TypeError("Argument `command` must be a class of `Command`")

        name = command.orginal_name

        if name in self.commands:
            raise TypeError("this command name is reserved")

        self._function[name] = command


    def command(self, name) -> Type[_Command]:
        def wrapper(func):

            if ' ' in name:
                raise SyntaxError("`space` is not allowed in command name")

            if inspect.iscoroutinefunction(func):
                raise TypeError("Function cannot be a coroutine function")

            if not inspect.isfunction(func):
                raise TypeError("This decoration function can be use only for function")

            if name in self.commands:
                raise TypeError("this name is reserved")


            command = _Command(func)(name)
            self.add_command(command)
            return command

        return wrapper


    def cog(self, name: str) -> None:
        def wrapper(func):
            self.add_cog(name, func)

        return wrapper

    def remove_command(self, name: str) -> None:
        if ' ' in name:
            raise TypeError("`space` is not allowed in command name")

        if name not in self.commands:
            raise TypeError("command is not added")

        self._function[name] = None

    def remove_cog(self, name: str) -> None:
        if ' ' in name:
            raise TypeError("`space` is not allowed in cog name")

        if name not in self.cogs:
            raise TypeError("cog is not added")

        self._cogs[name] = None

    def __repr__(self):
        page_name = self.page_name
        return f"Messenger({page_name=})"

