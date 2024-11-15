import pandas as pd
from datetime import datetime
import pytz
import requests
from timezonefinder import TimezoneFinder

# Load the CSV file into a pandas DataFrame
file_path = '/content/routine_data.csv'  # Update this with the actual path to your CSV file
schedule_df = pd.read_csv(file_path)

# Convert time strings in the CSV to minutes from midnight
def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

# Convert Timestamp column to minutes from midnight
schedule_df['Timestamp_Minutes'] = schedule_df['Timestamp'].apply(time_to_minutes)

# Function to detect local time using IP-based geolocation
def get_local_time():
    try:
        # Get the user's location data from ipinfo.io
        response = requests.get("https://ipinfo.io/json")
        data = response.json()

        # Extract latitude and longitude from the location data
        location = data.get('loc', '0,0').split(',')
        latitude, longitude = float(location[0]), float(location[1])

        # Determine the timezone using TimezoneFinder
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=longitude, lat=latitude)

        if timezone_str is None:
            raise ValueError("Could not determine timezone automatically.")

        # Get the current time in the detected timezone
        user_tz = pytz.timezone(timezone_str)
        current_time = datetime.now(user_tz)
        return current_time, user_tz.zone
    except Exception as e:
        print(f"Automatic timezone detection failed: {e}")
        # Fallback to manual input if automatic detection fails
        user_timezone = input("Enter your timezone (e.g., 'Asia/Colombo'): ")
        user_tz = pytz.timezone(user_timezone)
        current_time = datetime.now(user_tz)
        return current_time, user_tz.zone

# Function to get the scheduled activity based on the current time
def get_scheduled_activity():
    # Get the local time and timezone
    current_time, timezone_str = get_local_time()
    current_minutes = current_time.hour * 60 + current_time.minute

    # Find the closest previous timestamp
    previous_activities = schedule_df[schedule_df['Timestamp_Minutes'] <= current_minutes]
    if not previous_activities.empty:
        closest_activity = previous_activities.iloc[-1]  # Get the last row within the range
        return closest_activity['Activity'], current_time.strftime('%H:%M'), timezone_str
    else:
        return "No scheduled activity at this time", current_time.strftime('%H:%M'), timezone_str

# Get the current activity
scheduled_activity, local_time_str, timezone_str = get_scheduled_activity()
print(f"At {local_time_str} ({timezone_str}), the scheduled activity is: {scheduled_activity}")
