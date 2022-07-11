import requests
from airflow.models import Variable

class Token:

    def __init__(self):
        self.refresh_token = Variable.get("REFRESH_TOKEN")
        self.base_64_id_secret = Variable.get("BASE_64_ID:SECRET")
        self.access_token = None


    def refresh(self):
        query = "https://accounts.spotify.com/api/token"

        response = requests.post(query,
                                 data={"grant_type": "refresh_token",
                                       "refresh_token": self.refresh_token},
                                 headers={"Authorization": "Basic " + self.base_64_id_secret})

        response_json = response.json()
        self.access_token = response_json["access_token"]
    


token = Token()
token.refresh()