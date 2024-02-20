from typing import List,Dict,Set,Union


def Buttons(titles:Union[List[str],Set[str]]) -> List[Dict[str,str]]:

    if not isinstance(titles,(list,set)):
        raise TypeError("Argument `titles` must be a list or set")

    result = []
    for name in titles:
        msg = {"type":"postback","title":name,"payload":"payload"}
        result.append(msg)

    return result

def QuicklyRieplies(titles:Union[List[str],Set[str]]):

    if not isinstance(titles,(list,set)):
        raise TypeError("Argument `titles` must be a list or set")

    result = []

    for name in titles:
        msg = {"content_type":"text","title":name,"payload":"<POSTBACK_PAYLOAD>",}
        result.append(msg)

    return result



