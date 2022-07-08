import psycopg2
import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime

from sqlalchemy import create_engine


if __name__ == "__main__":
    DATABASE_URI = 'postgresql+psycopg2://airflow:airflow@postgres/airflow'
    engine = create_engine(DATABASE_URI)
    
