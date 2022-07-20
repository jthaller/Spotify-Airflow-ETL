from socket import SO_LINGER
from pandas import DataFrame
import requests
import json
from datetime import date
import pickle
from .token_manager import token
from .database_manager import *


class AISongRecommender():
    """This class is used to get the most recent songs, then use an embeddings song model
    to find song recommendations"""

    def __init__(self):
        self.access_token = token.access_token
        with open('dags/helper_functions/DATA/model_spotify_word2vec.pickle', 'rb') as f:
            self.model = pickle.load(f)
        with open('dags/helper_functions/DATA/track_map_dict.pickle', 'rb') as f:
            self.song_title_dict = pickle.load(f)
        self.reverse_titles_dict = {v:k for k,v in self.song_title_dict.items()}
        with open('dags/helper_functions/DATA/artist_map_dict.pickle', 'rb') as f:
            self.artists_dict = pickle.load(f)
    
    def get_uri(self, title:str, artist=None) -> str:
        """Return the uri of the song as a string"""
        
        headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json",
            "Authorization" : "Bearer {}".format(self.access_token)
        }

        query = f"track:{title}"

        r = requests.get("https://api.spotify.com/v1/search?type=track&include_external=audio&q={q}&limit=1".format(q=query), headers=headers)
        data = r.json()

        try:
            uri = data['tracks']['items'][0]['uri']
            print(data['tracks']['items'][0]['artists'])
        except KeyError:
            print(f"No match for song: {title}")
            print(f"response JSON: {data}")
            return ""
        return uri
    
    def get_recent_songs(self) -> DataFrame:
        """ Return a list of URIs from the spotify listening history within the previous week """

        db = PostrgresDB()

        query = """
        SELECT
            song_name,
            artist_name
        FROM
            my_played_tracks
        WHERE
            timestamp::timestamp > 'now'::timestamp - '7 days'::interval; 
        """
        df = db.create_pandas_table(query)
        return df


    def similar_songs(self, song:tuple, n:int) -> list:
        """ Gets the songname from user and return the n similar songs """

        song_name = song[0]
        song_id = song[1]
        print ("Searching for songs similar to :", song_name)
        try:
            similar = self.model.most_similar(song_id, topn=n)
        except KeyError:
            print(f"couldn't find {song_name}, {song_id} for some reason")
            return [] #['56248', '564085'] #TODO: JUST A TEMPORTARY RETURN TO

        print ("Similar songs are as follow:")
        for id, _ in similar:
            print (self.reverse_titles_dict[id])
        return [self.reverse_titles_dict[id] for id, _ in similar]


    def create_recommendations(self) -> list:
        """
        No inputs. Get recent songs. Filter to just ones we have embeddings for.
        Get the 2 most similar songs for each. Return the URIs as a list of strings.
        """

        songs_df = self.get_recent_songs()

        # match the listening history to song embeddings
        matched_songs_ids = []
        for song in songs_df.song_name.values:
            try: # try to match and see if we have an embedding for the
                matched_songs_ids.append((song, self.song_title_dict[song.lower()]))
                print(song, '--', self.song_title_dict[song.lower()])
            except KeyError:
                print(f"{song} -- not found")
        
        print("Found {}/{} songs".format(len(matched_songs_ids), songs_df.shape[0]))

        similar_songs = [self.similar_songs(song=song_tuple, n=2) for song_tuple in matched_songs_ids]
        similar_songs =  [y for x in similar_songs for y in x]
        print(similar_songs)
        uris = [self.get_uri(song) for song in similar_songs]
        print(uris)
        return uris
    
        

if __name__ == "__main__":
    pass