import requests
import json


class Client:

    def __init__(self, args):
        self.webhook = args['webhook']

    def send_text(self, text):
        requests.post(self.webhook,
                      headers={'Content-Type': 'application/json'},
                      data=json.dumps({
                          'msg_type': 'text',
                          'content': {
                              'text': text
                          }
                      }))
