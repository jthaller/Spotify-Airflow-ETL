from secrets import refresh_token, base_64
import requests
import json
from airflow.models import Variable

class Refresh:

    def __init__(self):
        self.refresh_token = Variable.get("REFRESH_TOKEN")
        self.base_64_id_secret = Variable.get("BASE_64_ID:SECRET")

        query = "https://accounts.spotify.com/api/token"

        response = requests.post(query,
                                 data={"grant_type": "refresh_token",
                                       "refresh_token": refresh_token},
                                 headers={"Authorization": "Basic " + self.base_64_id_secret})

        response_json = response.json()
        print(response_json)


a = Refresh()
a.refresh()