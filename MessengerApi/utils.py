from dataclasses import dataclass


@dataclass()
class UserData:
    first_name: str
    last_name: str
    name: str
    profile_pic: str
    id: str
    locale: str
    timezone: int
    gender:str = None # optional


@dataclass()
class MessageData:
    id_sender :str
    created_time: str
    message_context: str
    name: str
    from_: str
    message_token_sender: str


@dataclass()
class Persona:
    name:str
    profile_picture_url:str
    id:str




