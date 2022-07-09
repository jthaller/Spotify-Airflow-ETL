import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import os
from airflow.models import Variable
import sqlalchemy
from .token_manager import token


class PostrgresDB():

    def __init__(self):
        self.database_location = 'postgresql+psycopg2://airflow:airflow@postgres/airflow' #Variable.get("DATABASE_LOCATION")
        self.engine = sqlalchemy.create_engine(self.database_location, executemany_mode='batch') # connect_args={'sslmode': 'require'}
    
    def establish_connection(self):
        conn = self.engine.connect()
        return conn

    def execute_query(self, sql_query: str):
        conn = self.establish_connection()
        results = conn.execute(sql_query)
        conn.close()
        print("Close database successfully")
        return results
    
    def create_pandas_table(self, query: str):
        conn = self.establish_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


if __name__ == "__main__":
    query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """