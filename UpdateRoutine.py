import pandas as pd
from datetime import datetime, timedelta
import requests
import pytz
from timezonefinder import TimezoneFinder

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
        # Fallback to UTC if automatic detection fails
        current_time = datetime.utcnow()
        return current_time, "UTC"

# Get local time based on location
current_time, timezone_str = get_local_time()
print(f"Current local time is {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({timezone_str})")

# Load the activity log CSV into a pandas DataFrame
activity_log_path = '/content/activity_log.csv'  # Update this with the actual path to the activity log CSV file
activity_log_df = pd.read_csv(activity_log_path)

# Convert time to minutes for easier comparison
def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

activity_log_df['Time_Minutes'] = activity_log_df['Time'].apply(time_to_minutes)

# Group data by time intervals to find the most frequent activity at each time
activity_time_groups = activity_log_df.groupby('Time_Minutes')['Activity'].apply(lambda x: x.mode()[0]).reset_index()

# Function to get predicted activity based on the current time
def predict_activity_for_time(current_time_minutes):
    # Find the closest matching time interval in the past data
    closest_activity_row = activity_time_groups.loc[(activity_time_groups['Time_Minutes'] - current_time_minutes).abs().idxmin()]
    predicted_activity = closest_activity_row['Activity']
    return predicted_activity

# Function to update the schedule with predicted activities
def update_schedule_with_prediction():
    # Load the schedule CSV
    schedule_path = '/content/routine_data.csv'  # Update with the path to your schedule CSV file
    schedule_df = pd.read_csv(schedule_path)

    # Convert the schedule timestamps to minutes
    schedule_df['Timestamp_Minutes'] = schedule_df['Timestamp'].apply(time_to_minutes)

    # Convert the current local time to minutes
    current_time_minutes = current_time.hour * 60 + current_time.minute

    # Predict the most likely activity for this time
    predicted_activity = predict_activity_for_time(current_time_minutes)

    # Update the closest timestamp activity in the schedule
    closest_schedule_row_index = (schedule_df['Timestamp_Minutes'] - current_time_minutes).abs().idxmin()
    schedule_df.at[closest_schedule_row_index, 'Activity'] = predicted_activity

    # Save the updated schedule back to CSV
    updated_schedule_path = '/content/routine_data.csv'  # Update with desired output path
    schedule_df.to_csv(updated_schedule_path, index=False)
    print(f"Predicted activity '{predicted_activity}' updated in schedule for timestamp closest to {current_time.strftime('%H:%M')}.")

# Run the function to update the schedule with the prediction
update_schedule_with_prediction()
