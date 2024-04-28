import json
import os
from typing import Optional, Dict, Any

from requests_toolbelt import MultipartEncoder

from .http import HttpClient
from .view import Buttons, QuicklyRieplies


class Context(HttpClient):
    def __init__(self, **kwargs):
        self._token: str = kwargs.get("token")  # page access token
        self.sender: str = kwargs.get("sender_id")  # PSID of username
        self.command: str = kwargs.get("command")  # name of command or first word before whitespace
        self.username: str = kwargs.get("username")
        self.context: str = kwargs.get("context")  # message context
        self.created_time: str = kwargs.get("created_time")
        self.prefix:str = kwargs.get('prefix') # prefix command; useless ?
        self.message_token_sender: str = kwargs.get("message_token_sender")  # useless ?
        self._api: str = kwargs.get("api")  # api version
        self._page_id: str = kwargs.get("page_id")  # page_id

    def send(self,
             text: str,
             buttons: Optional[Buttons] = None,
             quicklyRieplies: Optional[QuicklyRieplies] = None,
             ) -> Dict[str,str]:
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


    def sendMessegeAsPersona(self, text: str, id: str) -> Dict[str, Any]:  # TODO
        """
        :param text: text to send
        :param id: persona id
        :return: Dict[str,Any]
        """
        if not isinstance(text, str):
            raise TypeError("Argument `text` must be str")
        dataJSON = {'recipient': {'id': self.sender}, 'message': {'text': text}, 'persona_id': id,
                    'access_token': self._token}
        req = self.sendRequest('POST', f'/{self._api}/{self._page_id}/messages', json=dataJSON)
        return req.json()

    def send_image(self, url: str) -> Dict[str, Any]:
        if not isinstance(url, str):
            raise TypeError('Argument `url` must be str')

        dataJSON = {"recipient": {"id": self.sender},
                    "message": {"attachment": {"type": "image", "payload": {"url": url, "is_reusable": False}}}}
        params = {"access_token": self._token}

        req = self.sendRequest("POST", "/me/messages", json=dataJSON, params=params)
        return req.json()

    def send_local_file(self, filename: str):
        if not isinstance(filename, str):
            raise TypeError("Argument `filename` must be str")

        request_body = MultipartEncoder({
            "recipient": json.dumps({"id": self.sender}),
            "message": json.dumps(
                {
                    "attachment": {
                        "type": 'file',
                        "payload": {
                            "is_reusable": True,
                        },
                    }
                }
            ),
            "filedata": (
                os.path.basename(filename),
                open(filename, "rb"),
                f"file/{filename.split('.')[-1]}",
            ),
        })

        headers = {"content-type": request_body.content_type}
        params = {"access_token": self._token}
        req = self.sendRequest("POST", '/me/messages', data=request_body, params=params, headers=headers)
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
