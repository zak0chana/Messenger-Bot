import requests


class HttpClient:
    def sendRequest(self, method: str, path: str, **kwargs) -> requests.Response:
        url:str = "https://graph.facebook.com" + path

        try:
            req: requests.Response = requests.request(method, url, **kwargs)
            # print(req.status_code)
            # print(req.content)
            # req.raise_for_status()
            return req
        except KeyboardInterrupt: # sometimes this error show up while exiting the program
            raise SystemExit
        except Exception as err:
            raise err





