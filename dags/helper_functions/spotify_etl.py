import psycopg2
import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import os
from airflow.models import Variable
import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# from spotipy.oauth2 import SpotifyClientCredentials
# from refresh import 


# Generate your token here:  https://developer.spotify.com/console/get-recently-played/

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False 

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")

    # Check that all timestamps are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') != yesterday:
            raise Exception("At least one of the returned songs does not have a yesterday's timestamp")
    return True


# def refresh_api_token():
#     _client_id = Variable.get("SPOTIFY_CLIENT_ID")
#     _client_secret = Variable.get("SPOTIFY_CLIENT_SECRET")
#     auth_url = 'https://accounts.spotify.com/api/token'
#     # client-credentials  'authorization-code', user-read-recently-played
#     auth_data = {'grant_type': 'authorization-code',
#                 'client_id': _client_id,
#                 'client_secret': _client_secret,
#                 'response_type': 'code'
#                 }
#     auth_response = requests.post(auth_url, data=auth_data)
#     access_token = auth_response.json().get('access_token')
#     print(access_token)
#     print("HERE")
#     return access_token

def refresh_api_token():
        refresh_token = Variable.get("REFRESH_TOKEN")
        base_64_id_secret = Variable.get("BASE_64_ID:SECRET")

        query = "https://accounts.spotify.com/api/token"

        response = requests.post(query,
                                 data={"grant_type": "refresh_token",
                                       "refresh_token": refresh_token},
                                 headers={"Authorization": "Basic " + base_64_id_secret})

        response_json = response.json()
        print(response_json)

        return response_json["access_token"]

def run_spotify_etl():
    database_location = 'postgresql+psycopg2://airflow:airflow@postgres/airflow'

    token = refresh_api_token()

    
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : "Bearer {}".format(token)
    }

    # Convert time to Unix timestamp in miliseconds      
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=30)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    # data = sp.current_user_recently_played(after=yesterday_unix_timestamp)
     # Download all songs you've listened to "after yesterday", which means in the last 24 hours      
    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers=headers)
    print(r)
    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object      
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])
        
    # Prepare a dictionary in order to turn it into a pandas dataframe below       
    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    for k, v in song_dict.items():
        print(k, v, sep=": ")

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
    
    # Validate
    # if check_if_valid_data(song_df):
    #     print("Data valid, proceed to Load stage")

    # Load

    # engine = sqlalchemy.create_engine(database_location)
    engine = sqlalchemy.create_engine(database_location, executemany_mode='batch') # connect_args={'sslmode': 'require'}
    # conn = psycopg2.connect('my_played_tracks.sqlite')
    conn = engine.connect()
    cursor = conn.cursor()
    

    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

    cursor.execute(sql_query)
    print("Opened database successfully")

    try:
        song_df.to_sql("my_played_tracks", engine, index=False, if_exists='append')
    except: # bad practice
        print("Data already exists in the database")

    
    # sql_query2 = """
    # SELECT * FROM MY_PLAYED_TRACKS LIMIT 100;
    # """

    # df = pd.read_sql_query(sql_query2, conn)
    # print(df.head())

    conn.close()
    print("Close database successfully")

    # if __name__ == "__main__":
    #     run_spotify_etl()
