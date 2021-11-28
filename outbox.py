import requests
import json
from datetime import datetime
from os import environ


_EVENT_URL = environ.get('EVENT_URL', 'http://localhost:8888') + '/produce'
_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=500, pool_maxsize=1000)
_session.mount('http://', adapter)


def produce_event(act_by, action, topic, value):
    response = _session.post(url=_EVENT_URL,
                             json={
                                   'topic': topic,
                                   'value': {
                                             'action': action,
                                             'act_by': act_by,
                                             'act_datetime': datetime.now().isoformat()
                                            } | value
                                  }
                            )
            
