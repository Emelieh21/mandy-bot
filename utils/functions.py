"""
Functions for Mandy Bot & noise tracker
"""

import os
import psycopg2
import uuid
import pandas as pd
import math
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

def connect_db():
    conn = psycopg2.connect(
        host="free-tier5.gcp-europe-west1.cockroachlabs.cloud",
        database="kindly-possum-2518.defaultdb",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PW"),
        port=26257)
    return conn
  
def create_table_if_needed(conn, delete_current = False):
    cur = conn.cursor()
    if (delete_current):
        query = "drop table mandy_noise"
        cur.execute(query)
    # Insert the DataFrame into PostgreSQL
    query = """
            CREATE table if not exists mandy_noise (
                uuid varchar,
                start_time varchar,
                end_time varchar,
                silent_count int,
                noise_count int
            )
            """
    cur.execute(query)
    conn.commit()
    cur.close()

# Add a row
def add_row_to_table(conn, uuid, start_time, end_time, silent_count, noise_count):
    cur = conn.cursor()
    current_uuid = uuid
    cur.execute(f"INSERT INTO mandy_noise (uuid, start_time, end_time, silent_count, noise_count) VALUES ('{current_uuid}', '{start_time}', '{end_time}', {silent_count}, {noise_count})")
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
    min_time = df['start_time'].min()
    max_time = df['end_time'].max()
    # I am using x[:-10] to cut off the (milli)seconds from the timestamp 
    result = f"I have been noisy {math.ceil(noise_share*100)}% of the time between {min_time[:-10]} and {max_time[:-10]}"
    return(result)

def generate_latest_plot():
    conn = connect_db()
    df = pd.read_sql('SELECT * from mandy_noise', conn)
    # make up some data
    x = pd.to_datetime(df['end_time']) 
    y = df['noise_count']/(df['silent_count']+df['noise_count'])
    
    # plot
    plt.plot(x,y)

    # Customize x-axis date and time format
    date_format = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.title('Time I have spend barking')
    plt.tight_layout()

    # Save the plot as a JPG file
    plt.savefig('plot.jpg', format='jpg')
    plt.close()

def is_invalid_user(update):
    print(update.message.chat.id)
    if str(update.message.chat.id) != os.environ.get('ALLOWED_CHAT_IDS'):
        update.message.reply_text("Sorry... I can't update you, because I don't know you.")
        return True
    else:
        return False