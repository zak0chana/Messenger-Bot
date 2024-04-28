from typing import List,Union

from .utils import Persona as _Persona
from .http import HttpClient

_imgUrl = 'https://cdn.icon-icons.com/icons2/2428/PNG/512/facebook_black_logo_icon_147136.png'



class Persona(HttpClient):
    def __init__(self,**kwargs):
        self._token = kwargs.get('token')
        self._page_id = kwargs.get('page_id')
        self._api_version = kwargs.get('api_version')


    def GetaListofPersonas(self) -> List[_Persona]:
        """ https://developers.facebook.com/docs/messenger-platform/send-messages/personas """
        params = {'access_token':self._token}
        req = self.sendRequest('GET',f'/{self._api_version}/{self._page_id}/personas',params=params)
        data:dict = req.json()
        result = []
        for _dict in data['data']:
            prepared = {'name':_dict['name'],'profile_picture_url':_dict['profile_picture_url'],'id':_dict['id']}
            result.append(_Persona(**prepared))
        return result


    def CreateaPersona(self, name: str, profile_picture_url: str = _imgUrl) -> str:
        if not isinstance(name, str):
            raise TypeError("Argument `name` must be str")

        if not isinstance(profile_picture_url, str):
            raise TypeError("Argument `profile_picture_url` must be str")

        params = {'name': name, 'profile_picture_url': profile_picture_url, 'access_token': self._token}

        req = self.sendRequest("POST", f'/{self._page_id}/personas', params=params)
        return req.json()['id']

    def GetaSpecificPersona(self,id:Union[str,int]) -> _Persona:

        if not isinstance(id,(str,int)):
            raise TypeError("Argument `id` must be Union[str,int]")

        params = {'access_token': self._token}
        req = self.sendRequest("GET",f'/{self._api_version}/'+str(id),params=params)
        data = req.json()
        return _Persona(**data)


