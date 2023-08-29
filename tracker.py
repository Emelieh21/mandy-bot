import pyaudio
import wave
import audioop
from datetime import datetime
from utils.functions import connect_db, create_table_if_needed, add_row_to_table, generate_uuid

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 8000  # Record at 44100 samples per second
# I want small sound clips only
seconds_to_record = 10
# I do not want to spam the database too much, so only adding data each X minutes
seconds_to_db_upload = 5*60
filename = "output.wav"

# Initialize table the first time, if needed
conn = connect_db()
create_table_if_needed(conn)
conn.close()

# We run this until we cancel the script
while True:
    start_time = str(datetime.now())
    # Connect to Cockroach
    conn = connect_db()

    # Initialize counters for the upload
    noise_count = 0
    silent_count = 0

    # We split the time that we want for each upload in chunks depending on the time for each recording
    for i in range(0, int(seconds_to_db_upload/seconds_to_record)):
        # Initiliaze counters for the recordings
        sub_noise_count = 0
        sub_silent_count = 0

        p = pyaudio.PyAudio()  # Create an interface to PortAudio
        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True)
        print(f'Started recording {i}')
        frames = []  # Initialize array to store frames
        # Store data in chunks for X seconds
        for ii in range(0, int(fs / chunk * seconds_to_record)):
            data = stream.read(chunk)
            rms = audioop.rms(data, 2)
            if rms > 50:
                noise_count += 1
                sub_noise_count +=1
            else:
                silent_count += 1
                sub_silent_count += 1
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        print(f'Finished recording {i}')
        avg_noise_count = sub_noise_count/(sub_noise_count+sub_silent_count)
        print(avg_noise_count)
        
        if (avg_noise_count > 0.5):
            # Save the recorded data as a WAV file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames))
            wf.close()

    print("Overal noise level: ")
    print(noise_count/(noise_count+silent_count))
    uuid = generate_uuid()
    end_time = str(datetime.now())
    add_row_to_table(conn, uuid, start_time, end_time, silent_count, noise_count)
    print("Stored")
    conn.close()
