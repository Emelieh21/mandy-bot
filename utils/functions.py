"""
Functions for Mandy Bot & noise tracker
"""

import os
import psycopg2
from datetime import datetime
import uuid
import pandas as pd
import math

def connect_db():
    conn = psycopg2.connect(
        host="free-tier5.gcp-europe-west1.cockroachlabs.cloud",
        database="kindly-possum-2518.defaultdb",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PW"),
        port=26257)
    return conn
  
def create_table_if_needed(conn):
    cur = conn.cursor()
    # Insert the DataFrame into PostgreSQL
    query = """
            CREATE table if not exists mandy_noise (
                uuid varchar,
                timestamp varchar,
                silent_count int,
                noise_count int
            )
            """
    cur.execute(query)
    conn.commit()
    cur.close()

# Add a row
def add_row_to_table(conn, uuid, silent_count, noise_count):
    cur = conn.cursor()
    current_uuid = uuid
    current_time = str(datetime.now())
    cur.execute(f"INSERT INTO mandy_noise (uuid, timestamp, silent_count, noise_count) VALUES ('{current_uuid}', '{current_time}', {silent_count}, {noise_count})")
    conn.commit()
    cur.close()

def generate_uuid():
    return str(uuid.uuid4())

# Print this beautiful new table...
def get_update():
    conn = connect_db()
    df = pd.read_sql('SELECT * from mandy_noise', conn)
    conn.close()
    silent_count_sum = df['silent_count'].sum()
    noise_count_sum = df['noise_count'].sum()
    noise_share = noise_count_sum/(noise_count_sum+silent_count_sum)
    min_time = df['timestamp'].min()
    max_time = df['timestamp'].max()
    result = f"I have been noisy {math.ceil(noise_share*100)}% of the time between {min_time} and {max_time}"
    return(result)
