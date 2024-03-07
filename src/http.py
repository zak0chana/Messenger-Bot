import requests


class HttpClient:
    def sendRequest(self, method: str, path: str, **kwargs) -> requests.Response:
        url = "https://graph.facebook.com" + path

        try:
            req = requests.request(method, url, **kwargs)
            req.raise_for_status()
            return req
        except KeyboardInterrupt: # sometimes this error while exiting program
            raise SystemExit
        except Exception as err:
            raise err
