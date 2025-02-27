#################################################################################################
#
# This script interacts with the OPSWAT MetaDefender Core API to upload a file for analysis and fetch the analysis results.
#
# Global Configurations:
#  - METADEFENDER_CORE_BASE_URL: The base URL of the MetaDefender Core server.
#  - FILE_PATH: The path to the file to be analyzed.
#  - RULE_NAME: The rule name to be applied during the file analysis.
#  - IGNORE_SSL_CERTIFICATE_ERRORS: Flag to ignore SSL certificate errors (not recommended for production).
#
# Functions:
#  - analyze_file(): Uploads the file to the MetaDefender Core server for analysis and returns the data ID and received cookies.
#  - fetch_analysis_result(data_id, cookies): Polls the MetaDefender Core server for the analysis results using the data ID and cookies.
#
# Usage:
#  1. Set the global configurations as needed.
#  2. Run the script to upload the file and fetch the analysis results.
#
# Note:
# This is a sample code for testing purposes made by Bulwarx Ltd. Bulwarx does not take any responsibility for any damage caused by the use of this script.
# For production use, consider implementing error handling, logging, and security best practices.
#
#################################################################################################

import os
import time
import requests
import urllib.parse
import urllib3
import json

# Global Configurations
METADEFENDER_CORE_BASE_URL = "https://YOUR_OPSWAT_SERVER_URL:8008" 
FILE_PATH = "/path/to/your/file"
RULE_NAME = "File process"  
IGNORE_SSL_CERTIFICATE_ERRORS = False  # DO NOT SET 'True' IN PRODUCTION

# Suppress SSL warnings if ignoring SSL certificates
if IGNORE_SSL_CERTIFICATE_ERRORS:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_file():
    url = f"{METADEFENDER_CORE_BASE_URL}/file"
    
    filename = os.path.basename(FILE_PATH)
    encoded_filename = urllib.parse.quote(filename)

    headers = {
        "filename": encoded_filename,  # URL-encoded filename, important for Hebrew filenames
        "rule": RULE_NAME, 
    }    
    
    with open(FILE_PATH, "rb") as file:
        files = {"file": (filename, file)}
        response = requests.post(url, files=files, headers=headers, verify=not IGNORE_SSL_CERTIFICATE_ERRORS)

    if response.status_code == 200:
        data = response.json()
        data_id = data.get("data_id")
        received_cookies = response.cookies.get_dict()

        return data_id, received_cookies
    else:
        print(f"Error: {response.text}")
        return None, None

def fetch_analysis_result(data_id, cookies):
    url = f"{METADEFENDER_CORE_BASE_URL}/file/{data_id}"
    
    polling_interval = 0.25 
    progress_percentage = 0

    while progress_percentage < 100:
        response = requests.get(url, headers={}, cookies=cookies, verify=not IGNORE_SSL_CERTIFICATE_ERRORS)
        progress_percentage = response.json().get("process_info", {}).get("progress_percentage", 0)
        time.sleep(polling_interval)
        polling_interval = min(polling_interval * 2, 5)

    return response.json()

if __name__ == "__main__":
    print(f"Posting file: {FILE_PATH}")
    data_id, received_cookies = analyze_file()

    if not data_id:
        print("Error: Failed to upload file.")
        exit(1)

    print(f"File uploaded successfully. Data Id: {data_id}")
    if (received_cookies):
        print("Cookies received: " + json.dumps(received_cookies))

    print("Scan in progress...")
    scan_results = fetch_analysis_result(data_id, received_cookies)
    
    processing_results = scan_results.get("process_info", {}).get("result", "No result found")
    print(f"Scan completed. Results: {processing_results}")
    if (processing_results == "Blocked"):
        print("Blocked reason: " + scan_results.get("process_info", {}).get("blocked_reason", "No reason found"))