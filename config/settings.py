import pyaudio

BOT_NAME='Mandy'
TABLE_NAME='mandy_noise'
CHUNK = 1024  # Record in chunks of 1024 samples
SAMPLE_FORMAT = pyaudio.paInt16  # 16 bits per sample
CHANNELS = 2
FS = 8000  # Record at 44100 samples per second
# I want small sound clips only
SECONDS_TO_RECORD = 6
# I do not want to spam the database too much, so only adding data each X minutes
SECONDS_TO_DB_UPLOAD = 1*60
FILENAME = 'output.wav'
