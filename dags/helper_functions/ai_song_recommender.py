import requests
import json
from datetime import date
import datetime
import os
from airflow.models import Variable
from .token_manager import token
from .ai_song_recommender import uris
from .database_manager import *


class AISongRecommender():
    """This class is used to get the most recent songs, then use an embeddings song model
    to find song recommendations"""

    def __init__(self):
        self.access_token = token.access_token
        # self.model = load .model file
    
    def get_recent_songs(self)->list:
        """Return a list of URIs from the spotify listening history within the previous week"""
        today = datetime.datetime.now()
        one_week_ago = today - datetime.timedelta(days=30)
        one_week_ago_unix_timestamp = int(one_week_ago.timestamp()) * 1000

        db = PostrgresDB()
        
        query = """
        SELECT * LIMIT 10; 
        """ # CHANGE TO RETURN THE URIs
        df = db.create_pandas_table(query)
        return df
    



if __name__ == "__main__":
    pass