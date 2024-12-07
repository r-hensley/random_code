import sqlite3
from datetime import timezone, datetime, timedelta
import pytz

pacific_tz = pytz.timezone('America/Los_Angeles')
fixed_timezone = timezone(timedelta(hours=-8))
japan_to_us_offset = 16 * 60 * 60 * 1000  # move all timestamps by 16 hours (came back from Japan to US)
us_to_japan_offset = -japan_to_us_offset
offset = us_to_japan_offset
offset = offset + 1  #  i was getting a UNIQUE constraint failed: revlog.id error, so this makes it work
# lower_range = 1722750615000  # august 3rd
# upper_range = 1729013415000  # october 17th
lower_range = 0
upper_range = 99999999999999

# Path to your Anki collection database file (modify the path as needed)
db_path = 'C:\\Users\\ryry0\\AppData\\Roaming\\Anki2\\1) Ryan\\collection.anki2'
backup = 'C:\\Users\\ryry0\\AppData\\Roaming\\Anki2\\1) Ryan\\collection_backup.anki2'

# first, overwrite the main database with the backup
if False:
    with open(backup, 'rb') as f:
        backup_data = f.read()

    with open(db_path, 'wb') as f:
        f.write(backup_data)

# raise Exception("This is a test")

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# perform the sqlite action
# shift ID by offset for all timestamps between the specified range
cursor.execute(f"UPDATE revlog SET id = id + {offset} WHERE id > {lower_range} AND id < {upper_range}")
conn.commit()

# Query to get the list of IDs (timestamps) from the revlog table
cursor.execute("SELECT id FROM revlog ORDER BY id ASC")

# Fetch all the results (this will be a list of tuples)
timestamps = cursor.fetchall()

# Convert list of tuples to a list of integers (IDs)
timestamp_ids = [row[0] for row in timestamps]

# convert timestamps from timestamps_ids to local time
local_time_timestamps = []
for ts in timestamp_ids:  # Converting only the first 10 to make it manageable
    # Convert from milliseconds to seconds and create a datetime object
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    local_dt = dt.astimezone(pacific_tz)
    local_time_timestamps.append(local_dt)

# Print the first few timestamp IDs in local time
print("First few timestamp IDs in local time:")
for ts in local_time_timestamps[:10]:
    print(ts)

# Extract unique days from August, September, and October
days = [{}, {}, {}]

for dt in local_time_timestamps:
    # Check if the month is August, September, or October
    if dt.month in [8, 9, 10] and dt.year == 2024:  # Assuming we are interested in 2024
        if dt.month == 10:
            print(dt)
        month_index = dt.month - 8
        if dt.day not in days[month_index]:
            days[month_index][dt.day] = 1
        else:
            days[month_index][dt.day] += 1

# Calculate the number of unique days
unique_days_count = [len(day_set) for day_set in days]
total_reviews_last_30 = 0

for i, month in enumerate(["August", "September", "October"]):
    for j in range(1, 31):
        if month == "October" and j == 17:
            break
        if month == "October":
            days_ago = 17 - j
        elif month == "September":
            days_ago = 30 + 17 - j
        else:
            days_ago = 31 + 30 + 17 - j
        if j not in days[i]:
            print(f"No reviews {days_ago} days ago on {month} {j}, 2024")
        else:
            if days_ago <= 30:
                total_reviews_last_30 += days[i][j]
            print(f"Reviews {days_ago} days ago on {month} {j}, 2024: {days[i][j]}")

# Print the number of days reviews were done in the specified months
print(f"Number of unique days with reviews in August, September, and October 2024: {unique_days_count}")
print(f"Total reviews in the last 30 days: {total_reviews_last_30}")


# Close the database connection
conn.close()

print("finished")
