from typing import Union, Optional
import requests
import requests_toolbelt
from .view import Buttons, QuicklyRieplies

class Context:
    def __init__(self, **kwargs):
        self._token: str = kwargs.get("token")  # token
        self.sender: str = kwargs.get("sender_id")  # PSID of username
        self.command: str = kwargs.get("command")  # name of command
        self.username: str = kwargs.get("username")
        self.context: str = kwargs.get("context")  # message context
        self.created_time: str = kwargs.get("created_time")
        self.message_token_sender: str = kwargs.get("message_token_sender")  # useless ?
        self._api: str = kwargs.get("api")  # api version

    def sendRequest(self, method: str, path: str, **kwargs) -> requests.Response:
        url = "https://graph.facebook.com" + path
        req = requests.request(method, url, **kwargs)
        # req.raise_for_status()
        return req

    def send(self,
             text: str,
             buttons: Optional[Buttons] = None,
             quicklyRieplies: Optional[QuicklyRieplies] = None,
             ):
        """
        :param text: Must be less than 2000
        :param quicklyRieplies: An array of quick replies to be sent in a message
        """

        if not isinstance(text, str):
            raise TypeError("Argument `text` must be a str")

        if text == '':
            raise SyntaxError("Argument `text` cannot be empty")

        if not isinstance(buttons, list) and buttons is not None:
            raise TypeError("Argument `buttons` must be a List[Dict[str, str]] or None")

        if not isinstance(quicklyRieplies, list) and quicklyRieplies is not None:
            raise TypeError("Argument `quicklyButton` must be a List[Dict[str, str]] or None")

        if quicklyRieplies and buttons:
            raise AttributeError("Argument `quicklyButton` and `buttons` cannot be used in the same time")

        if buttons:
            dataJSON = {"recipient": {"id": self.sender}, "message": {"attachment": {"type": "template", "payload":
                {"template_type": "button", "text": text, "buttons": buttons}}}}
        elif quicklyRieplies:
            dataJSON = {"recipient": {'id': self.sender}, "message": {"text": text, "quick_replies": quicklyRieplies}}
        else:
            dataJSON = {"recipient": {"id": self.sender}, "message": {"text": text}}

        params = {"access_token": self._token}

        req = self.sendRequest("POST", "/me/messages", json=dataJSON, params=params)
        return req.json()

    def send_image(self, url:str):
        if not isinstance(url,str):
            raise TypeError('Argument `url` must be str')

        dataJSON = {"recipient": {"id": self.sender},
                    "message": {"attachment": {"type": "image", "payload": {"url": url, "is_reusable": False}}}}
        params = {"access_token": self._token}


        req = self.sendRequest("POST", "/me/messages", json=dataJSON, params=params)
        return req.json()



    def __eq__(self, other) -> bool:
        """ Return self==value.
        this function check attr: `sender`, `context` and `created_time`
        """
        if not hasattr(other, 'sender'):
            raise AttributeError("Value `other` must contain variable `sender`, `context` and `created_time`")

        if not hasattr(other, 'context'):
            raise AttributeError("Value `other` must contain variable `sender`, `context` and `created_time`")

        if not hasattr(other, 'created_time'):
            raise AttributeError("Value `other` must contain variable `sender`, `context` and `created_time`")

        return (self.sender == other.sender and
                self.context == other.context and
                self.created_time == other.created_time
                )

    def __ne__(self, other) -> bool:
        """ Return self!=value. """
        return not self.__eq__(other)

    def __repr__(self):
        sender = self.sender
        return f"Context({sender=})"
