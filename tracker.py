import pyaudio
import audioop
from datetime import datetime
from utils.functions import connect_db, create_table_if_needed, add_row_to_table, generate_uuid
import config.settings as settings

# Initialize table the first time, if needed
conn = connect_db()
create_table_if_needed(conn)
conn.close()

tracking_counter = 0

# TODO: Only track and store, do not save recordings in between
# TODO: Store an ID from the tracking session
uuid = generate_uuid()

# We run this until we cancel the script
while True:
    # Keeping track of how far we got
    tracking_counter += 1
    print(f'Starting round {tracking_counter}')

    start_time = str(datetime.now())

    # Initialize counters for the upload
    noise_count = 0
    silent_count = 0

    # Initialize stream
    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    stream = p.open(format=settings.SAMPLE_FORMAT,
                channels=settings.CHANNELS,
                rate=settings.FS,
                frames_per_buffer=settings.CHUNK,
                input=True)
    # Store data in chunks for X seconds
    for i in range(0, int(settings.FS / settings.CHUNK * settings.SECONDS_TO_DB_UPLOAD)):
        data = stream.read(settings.CHUNK)
        rms = audioop.rms(data, 2)
        if rms > 50:
            noise_count += 1
        else:
            silent_count += 1

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()

    print("Overal noise level: ")
    print(noise_count/(noise_count+silent_count))
    end_time = str(datetime.now())
    
    # Connect to Cockroach
    conn = connect_db()
    add_row_to_table(conn, uuid, start_time, end_time, silent_count, noise_count)
    conn.close()
    print("Stored")

    print(f'Tracker active since {(settings.SECONDS_TO_DB_UPLOAD*tracking_counter)/60} minutes')
    
