import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from utils.functions import connect_db
import pandas as pd

conn = connect_db()
df = pd.read_sql('SELECT * from mandy_noise', conn)

# make up some data
x = pd.to_datetime(df['end_time']) #datetime.datetime.strptime(df['end_time'], input_format)
y = df['noise_count']/(df['silent_count']+df['noise_count'])

print(x)
print(y)

# plot
plt.plot(x,y)

# Customize x-axis date and time format
date_format = mdates.DateFormatter('%H:%M')
plt.gca().xaxis.set_major_formatter(date_format)

min_time = df['start_time'].min()
max_time = df['end_time'].max()
plt.title(f'{min_time[:10]} - {max_time[:10]}')
plt.tight_layout()

# Save the plot as a JPG file
plt.savefig('plot.jpg', format='jpg')

plt.show()
