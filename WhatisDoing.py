import os
import csv
from datetime import datetime
import pytz
import requests
from timezonefinder import TimezoneFinder

# Function to get local time and timezone
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

# Function to input current activity from caregiver/parent
def get_current_activity_from_input():
    current_activity = input("What is the infant doing right now? ")
    return current_activity

# Function to save the current activity to a CSV file
def save_activity_to_csv(current_activity, current_time):
    # Prepare data to save
    activity_data = {
        'Date': current_time.strftime('%Y-%m-%d'),
        'Time': current_time.strftime('%H:%M'),
        'Activity': current_activity
    }

    # Check if the CSV file exists
    file_path = '/content/activity_log.csv'  # Update with your desired path
    file_exists = os.path.exists(file_path)

    # If file doesn't exist, create it and write headers
    with open(file_path, mode='a', newline='') as file:
        fieldnames = ['Date', 'Time', 'Activity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Write header only if file is new

        writer.writerow(activity_data)
    print(f"Activity saved: {activity_data}")

# Main process
def log_activity():
    # Get the current activity from caregiver/parent
    current_activity_input = get_current_activity_from_input()
    print(f"The caregiver/parent reports that the infant is currently doing: {current_activity_input}")
    
    # Get the local time
    current_time, _ = get_local_time()
    
    # Save the activity to the CSV file
    save_activity_to_csv(current_activity_input, current_time)

# Call the main function to log activity
log_activity()
