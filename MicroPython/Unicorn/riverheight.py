import urequests

# Replace this URL with the actual API endpoint
river_url = "https://environment.data.gov.uk/flood-monitoring/id/measures/L0303-level-stage-i-15_min-mAOD"

def check_river_level():
    try:
        response = urequests.get(river_url)

        if response.status_code == 200:
            data = response.json()
            
            # Extract the value from the JSON response
            latest_reading = data.get("items", {}).get("latestReading")
            if latest_reading:
                value = latest_reading.get("value")
                if value is not None:
                    return(f"Current river level: {value}m")
                else:
                    print("Value not found in the response.")
            else:
                print("Latest reading data not found in the response.")

        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


