import requests
import json
from datetime import date
import datetime
import os
from airflow.models import Variable
from spotify_etl import refresh_api_token


def create_playlist(self):
    database_location = 'postgresql+psycopg2://airflow:airflow@postgres/airflow'

    token = refresh_api_token()

    
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {}".format(token)
    }

    # Create a new playlist
    print("Trying to create playlist...")

    today = date.today()

    todayFormatted = today.strftime("%d/%m/%Y")

    spotify_user_id = Variable.get("SPOTIFY_CLIENT_ID")


    query = "https://api.spotify.com/v1/users/{}/playlists".format(
        spotify_user_id)

    request_body = json.dumps({
        "name": todayFormatted + " discover weekly", "description": "Discover weekly rescued once again from the brink of destruction by your friendly neighbourhood python script", "public": True
    })

    response = requests.post(query, data=request_body, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token)
    })

    response_json = response.json()

    return response_json["id"]

def add_to_playlist(self):
    # add all songs to new playlist
    print("Adding songs...")

    self.new_playlist_id = self.create_playlist()

    query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(
        self.new_playlist_id, self.tracks)

    response = requests.post(query, headers={"Content-Type": "application/json",
                                                "Authorization": "Bearer {}".format(self.spotify_token)})


def create_spotify_playlist():
    print("creating spotify playlist")