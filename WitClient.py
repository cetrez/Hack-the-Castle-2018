import requests


class HttpClient:
    base_url = 'http://httpbin.org/post'

    @staticmethod
    def print_request(req):
        print('HTTP/1.1 {method} {url}\n{headers}\n\n{body}'.format(
            method=req.method,
            url=req.url,
            headers='\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            body=req.body,
        ))

    @staticmethod
    def print_response(res):
        print('HTTP/1.1 {status_code}\n{headers}\n\n{body}'.format(
            status_code=res.status_code,
            headers='\n'.join('{}: {}'.format(k, v) for k, v in res.headers.items()),
            body=res.content,
        ))


class WitClient(HttpClient):
    base_url = 'https://api.wit.ai'
    version = '20170307'

    def __init__(self, token):
        self.token = token

    def _get_header(self):
        hed = {'Authorization': 'Bearer ' + self.token,
               'Content-Type': 'application/json'}
        return hed

    @staticmethod
    def _apply_version(url):
        return url + '?v=' + WitClient.version

    def create_entity(self, entity_id):
        url = WitClient._apply_version(WitClient.base_url + '/entities')
        data = {'id': entity_id}
        header = self._get_header()
        response = requests.post(url=url, json=data, headers=header)
        WitClient.print_response(response)
        return response.status_code

    def create_sample(self, entity_id, exprs):
        value = entity_id

        data = []
        for text in exprs:
            data.append({
                'text': text,
                'entities': [{
                    'entity': entity_id,
                    'value': value
                }]
            })
        url = WitClient._apply_version(WitClient.base_url + '/samples')
        header = self._get_header()
        response = requests.post(url=url, json=data, headers=header)
        WitClient.print_response(response)
        return response.status_code

