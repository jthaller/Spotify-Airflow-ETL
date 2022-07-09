import requests
import json
from datetime import date
import datetime
import os
from airflow.models import Variable
from .token_manager import token
from .ai_song_recommender import uris

class SpotifyPlaylist:

    def __init__():
        self.new_playlist_id = None
        self.access_token = token.access_token
        self.user_id = Variable.get("SPOTIFY_CLIENT_ID")


    def create_playlist(self):
        database_location = 'postgresql+psycopg2://airflow:airflow@postgres/airflow'
        # spotify_user_id = Variable.get("SPOTIFY_CLIENT_ID")
        # access_token = token.access_token

        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json",
            "Authorization" : "Bearer {}".format(token)
        }

        # Create a new playlist
        print("Trying to create playlist...")

        today = date.today()
        todayFormatted = today.strftime("%d/%m/%Y")


        query = "https://api.spotify.com/v1/users/{}/playlists".format(spotify_user_id)

        request_body = json.dumps({
            "name": "AI Generated Playlist - {}".format(todayFormatted),
            "description": "An AI generated playlist based on the previous week's listening history",
            "public": True
            }
        )

        response = requests.post(query, data=request_body, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.access_token)
            }
        )

        response_json = response.json()
        return response_json["id"]

    def add_to_playlist(self, uris: list):
        # add all songs to new playlist
        print("Adding songs...")

        self.new_playlist_id = self.create_playlist()

        query = "https://api.spotify.com/v1/playlists/{}/tracks?uris={}".format(
            self.new_playlist_id, self.tracks)

        response = requests.post(query,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer {}".format(self.spotify_token)
                                          }
        )


def create_spotify_playlist():
    print("creating spotify playlist")
    playlist = SpotifyPlaylist()