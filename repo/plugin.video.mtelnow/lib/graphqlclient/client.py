#from lib.six.moves import urllib
import requests
import json

class GraphQLClient:
    def __init__(self, endpoint, session = None):
        self.endpoint = endpoint
        self.session = session
        if session is None:
            self.session = requests.Session()
            

    def execute(self, query, variables=None, headers={}):
        return self._send(query, variables, headers)

    def _send(self, query, variables, headers):
        data = {'query': query,
                'variables': variables}
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'

        try:
            req = self.session.post(url = self.endpoint, data = json.dumps(data).encode('utf-8'), headers=headers)
            return req.json()
        except Exception as e:
            raise e
