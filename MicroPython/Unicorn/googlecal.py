import urequests
import secrets
import utime

year = 2023
month = 11 #placeholders for rtc in the main
day = 18
minTime = "00:00:00Z"
maxTime = "23:59:59Z"

def extract_event_info(event):
    start_time = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
    end_time = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
    description = event.get('description', '')
    
    # Convert start and end times to a more readable format
    #start_time = utime.mktime(utime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ"))
    #end_time = utime.mktime(utime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ"))

    return start_time, end_time, description

response = urequests.get(f'https://www.googleapis.com/calendar/v3/calendars/{secrets.googleCalLink}/events?key={secrets.googleApi}&timeMin={year}-{month}-{day}T{minTime}&timeMax={year}-{month}-{day+1}T{maxTime}')

print(response.status_code)

json_data = response.json()

events = json_data.get('items', [])

for event in events:
    start_time, end_time, description = extract_event_info(event)
    print(f"Start Time: {start_time}, End Time: {end_time}, Description: {description}")