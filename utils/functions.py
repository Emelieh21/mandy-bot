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
import pyaudio
import wave
import config.settings as settings

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
        query = f"drop table {settings.TABLE_NAME}"
        cur.execute(query)
    # Insert the DataFrame into PostgreSQL
    query = f"""
            CREATE table if not exists {settings.TABLE_NAME} (
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


def add_row_to_table(conn, uuid, start_time, end_time, silent_count, noise_count):
    cur = conn.cursor()
    current_uuid = uuid
    cur.execute(f"INSERT INTO {settings.TABLE_NAME} (uuid, start_time, end_time, silent_count, noise_count) VALUES ('{current_uuid}', '{start_time}', '{end_time}', {silent_count}, {noise_count})")
    conn.commit()
    cur.close()


def generate_uuid():
    return str(uuid.uuid4())


def get_latest_session_data():
    conn = connect_db()
    # Check what was the uuid of the latest timestamp
    df = pd.read_sql(f"""
                     with current_session_uuid as (
                        select uuid 
                        from {settings.TABLE_NAME}
                        order by end_time desc
                        limit 1
                     )
                     SELECT * from {settings.TABLE_NAME}
                     where uuid IN (select uuid from current_session_uuid)
                     """, conn)
    conn.close()
    return(df)


def get_update():
    df = get_latest_session_data()
    silent_count_sum = df['silent_count'].sum()
    noise_count_sum = df['noise_count'].sum()
    noise_share = noise_count_sum/(noise_count_sum+silent_count_sum)
    min_time = df['start_time'].min()
    max_time = df['end_time'].max()
    # I am using x[:-10] to cut off the (milli)seconds from the timestamp 
    result = f"I have been noisy {math.ceil(noise_share*100)}% of the time between {min_time[:-10]} and {max_time[:-10]}"
    return(result)


def generate_latest_plot():
    df = get_latest_session_data()
    # make up some data
    x = pd.to_datetime(df['end_time']) 
    y = df['noise_count']/(df['silent_count']+df['noise_count'])
    
    # plot
    plt.plot(x,y)

    # Customize x-axis date and time format
    date_format = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(date_format)
    # TODO: the y-axis would look better as % and title % of time I have spend barking
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


def save_recording(p, frames, filename = settings.FILENAME):
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(settings.CHANNELS)
    wf.setsampwidth(p.get_sample_size(settings.SAMPLE_FORMAT))
    wf.setframerate(settings.FS)
    wf.writeframes(b''.join(frames))
    wf.close()


def record_audio(filename = settings.FILENAME, seconds_to_record = settings.SECONDS_TO_RECORD):
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format=settings.SAMPLE_FORMAT,
                    channels=settings.CHANNELS,
                    rate=settings.FS,
                    frames_per_buffer=settings.CHUNK,
                    input=True)
    print('Started recording...')
    frames = []  # Initialize array to store frames
    # Store data in chunks for X seconds
    for i in range(0, int(settings.FS / settings.CHUNK * seconds_to_record)):
        data = stream.read(settings.CHUNK)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()
    save_recording(p, frames, filename)
    print(f'Recording stored as {filename}')