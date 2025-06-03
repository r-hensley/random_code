import sqlite3
from datetime import timezone, datetime, timedelta
import pytz

# __Example logic__
# Move from CA to Chicago (+2 hours)
# Anki day shifts at 4am
# If you did a review at 3:30am in California, it would read as a review at 5:30am in Chicago
# So, you need to shift all timestamps back by two hours, since your clock moved forward by two hours
# So that 5:30am review would read as 3:30am again.

# __How to use__
# 1) Scroll down to find "offset" variable and set that properly
# 2) Let code make a backup of the database first if necessary
# 3) Start the rest of the code with restoring *from* backup each time
# 4) Make sure code ends with "finished" comment at end of console

# Nothing here should need to be touched
pacific_tz = pytz.timezone('America/Los_Angeles')
japan_tz = pytz.timezone("Asia/Tokyo")
chicago_tz = pytz.timezone("America/Chicago")
taiwan_tz = pytz.timezone("Asia/Taipei")
fixed_timezone = timezone(timedelta(hours=-8))

now = datetime.now()

# # Convert the current time to the specified timezones
# pacific_now = now.astimezone(pacific_tz)
# japan_now = now.astimezone(japan_tz)
# chicago_now = now.astimezone(chicago_tz)

# #########################
# #########################
# SET THESE LINES PROPERLY
START_TZ = taiwan_tz
END_TZ = pacific_tz
# #########################
# #########################

start_time_now = now.astimezone(START_TZ)
end_time_now = now.astimezone(END_TZ)

# hours_difference = (japan_now.utcoffset().total_seconds() - pacific_now.utcoffset().total_seconds()) / 3600
offset_hours = (start_time_now.utcoffset().total_seconds() - end_time_now.utcoffset().total_seconds()) / 3600
print(f"Calculated difference from {START_TZ} to {END_TZ} is {-offset_hours} hours")

offset_seconds = offset_hours * 60 * 60 * 1000  # move all timestamps by 16/17 hours (going from Japan --> CA)
print(f"Moving timestamps {offset_hours} hours ({offset_seconds} seconds). "
      f"Use this if your clocks have moved {-offset_hours} hours.")
offset_seconds = offset_seconds + 1  #  i was getting a UNIQUE constraint failed: revlog.id error, so this makes it work

# __Setting custom date range__
# To only shift dates in a certain range
# (i.e., everything before coming to where you are if you forgot to shift prev. dates when you arrived)
# (or, everything from the dates when you were at a place, if you never shifted them while you were there)
# lower_range = 1722750615000  # august 3rd
# upper_range = 1729013415000  # october 17th
# upper_range = 1729013415000  # october 17th
# upper_range = 1741536000000  # Sunday, March 9, 2025 11:00:00 AM GMT-05:00
# https://www.epochconverter.com/
max_timestamp = 5999999999
lower_range = 0
upper_range = max_timestamp
# assert that you're using ms and not seconds
if lower_range < 10_000_000_000:
    lower_range *= 1000  # convert to milliseconds
if upper_range < 10_000_000_000:
    upper_range *= 1000  # convert to milliseconds

# Path to your Anki collection database file (modify the path as needed)
db_path = 'C:\\Users\\ryry0\\AppData\\Roaming\\Anki2\\1) Ryan\\collection.anki2'
backup = 'C:\\Users\\ryry0\\AppData\\Roaming\\Anki2\\1) Ryan\\collection_backup.anki2'

# make backup if necessary before changing anything
if False:
    # open main database
    with open(db_path, 'rb') as f:
        data = f.read()
        
    # write to back up
    with open(backup, 'wb') as f:
        f.write(data)
        
    print("[SUCCESS] Backup created")

# first, overwrite the main database with the backup
# this is for if you're testing multiple times
if True:
    # read backup
    with open(backup, 'rb') as f:
        backup_data = f.read()

    # write to main db file
    with open(db_path, 'wb') as f:
        f.write(backup_data)
        
    print("[SUCCESS] Restored from backup")

# can enable the below exit with above backup restore if you want to just restore backup
# exit("Exiting after restoring backup")
# comment out above exit after you're sure you want to continue

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# perform the sqlite action
# shift ID by offset for all timestamps between the specified range
if offset_seconds != 1:
    print("Shifting timestamps...")
    cursor.execute(f"UPDATE revlog SET id = id + {offset_seconds} WHERE id > {lower_range} AND id < {upper_range}")
    conn.commit()
else:
    print("No need to shift timestamps.")

# Query to get the list of IDs (timestamps) from the revlog table
cursor.execute(f"SELECT id FROM revlog WHERE id > {lower_range} AND id < {upper_range} ORDER BY id ASC ")

# Fetch all the results (this will be a list of tuples)
timestamps = cursor.fetchall()
print(f"Found {len(timestamps)} timestamps in the specified range.")


# Convert list of tuples to a list of integers (IDs)
timestamp_ids = [row[0] for row in timestamps]

# Close the database connection
conn.close()

# convert timestamps from timestamps_ids to local time
local_time_timestamps = []
utc_time_timestamps = []
print_counter = 0
# Converting only the first and last 10 to make it manageable
for ts in timestamp_ids[:10][::-1] + timestamp_ids[-10:][::-1]:
    # Convert from milliseconds to seconds and create a datetime object
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    utc_time_timestamps.append(dt)
    local_dt = dt.astimezone(END_TZ)
    local_time_timestamps.append(local_dt)
    print(f"ts: {ts}: {dt} -> {local_dt}")

# Print the first few timestamp IDs in local time
print("Last few timestamp IDs in local time:")
for ts in local_time_timestamps[:10]:
    print(ts)
    
# print("Last ten timestamp IDs")
# for ts in timestamp_ids[:10]:
#     print(ts)
    
day_set = set()

ninety_days_period = end_time_now - timedelta(days=90)
print(f"90 days period started: {ninety_days_period.date()}")
for dt in local_time_timestamps:
    # anki day shifts at 4am, so subtract four hours from all dates
    dt = dt - timedelta(hours=4)
    # days_ago = (end_time_now - dt).days
    if dt.date() > ninety_days_period.date():
        day_set.add((dt.year, dt.month, dt.day))
    # Check if the month is August, September, or October
    # if dt.month in [8, 9, 10] and dt.year == 2024:  # Assuming we are interested in 2024
    #     if dt.month == 10:
    #         print(dt)
    #     month_index = dt.month - 8
    #     if dt.day not in days[month_index]:
    #         days[month_index][dt.day] = 1
    #     else:
    #         days[month_index][dt.day] += 1
    
day_set = sorted(day_set, key=lambda x: (x[0], x[1], x[2]))
print(f"With current offset adjustment, last {len(day_set)}/90 days studied!")
# print('\n'.join([f"{x[1]}/{x[2]}/{x[0]}" for x in day_set]))
counter = 0
search_time = end_time_now
for _ in range(90):
    if (search_time.year, search_time.month, search_time.day) not in day_set:
        print(f"No reviews {counter} days ago on {search_time.month}/{search_time.day}/{search_time.year}")
    search_time -= timedelta(days=1)
    counter += 1



# Calculate the number of unique days
# unique_days_count = [len(day_set) for day_set in days]
# total_reviews_last_30 = 0
#
# for i, month in enumerate(["August", "September", "October"]):
#     for j in range(1, 31):
#         if month == "October" and j == 17:
#             break
#         if month == "October":
#             days_ago = 17 - j
#         elif month == "September":
#             days_ago = 30 + 17 - j
#         else:
#             days_ago = 31 + 30 + 17 - j
#         if j not in days[i]:
#             print(f"No reviews {days_ago} days ago on {month} {j}, 2024")
#         else:
#             if days_ago <= 30:
#                 total_reviews_last_30 += days[i][j]
#             print(f"Reviews {days_ago} days ago on {month} {j}, 2024: {days[i][j]}")

# Print the number of days reviews were done in the specified months
# print(f"Number of unique days with reviews in August, September, and October 2024: {unique_days_count}")
# print(f"Total reviews in the last 30 days: {total_reviews_last_30}")

print("finished")
