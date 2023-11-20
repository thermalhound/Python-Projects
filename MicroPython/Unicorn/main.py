"""

Micropython code for the Pimoroni Galactic Unicorn

Building on top of the supplied demo clock code this version now
adds several features:

* ability to connect to multiple known networks with ssid and pwd in a secrets file
* drawDisplay passes string to either a static or scrolling function depending on
  string length
* connects to various APIs to display various information at different times, with
  the schedule for displaying and accessing the APIs set in the cycles.py file

To Do ...

* Decide what local weather parts I want to see and write the string generator,
  then remove the 'pass' from the if statement so the local weather is actually
  displayed
* Add an alarm function that sends a push notification (link in secrets.py working)
  if the river height gets to a certain level
* Add calendar events to display to replace the 'facts' section. The googlecal.py
  file has basic functionality but needs better parsing
* Add button monitoring so I can display things on press instead of having to wait.
  A headline replay button would be good. To facilitate move the headline increment
  function to the start rather than the end (so then if replaying the index is
  already correct)
* Better code comments (ha ha ha!!)
* Deal with bad API responses from openweathermap, newsdata.io, api-ninjas and
  checkwx
* Change the scrolling text code so that it returns to the main loop in between
  display updates?
* Move apiChecked and displayCycleChecked to their own functions so make the main
  loop easier to read

"""

import time
import math
import machine
import network
import ntptime
import secrets
import urequests
import cycles
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY

# initial variables and constants

# constants for controlling the background colour throughout the day
MIDDAY_HUE = 1.1
MIDNIGHT_HUE = 0.8
HUE_OFFSET = -0.1
MIDDAY_SATURATION = 1.0
MIDNIGHT_SATURATION = 1.0
MIDDAY_VALUE = 0.8
MIDNIGHT_VALUE = 0.3
hue = 0
sat = 0
val = 0

# constants for display / graphics

PADDING = 5
HOLD_TIME = 2.0
STEP_TIME = 0.055
STATE_PRE_SCROLL = 0
STATE_SCROLLING = 1
STATE_POST_SCROLL = 2

# create galactic object and graphics surface for drawing
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# set up some pens to use later
WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)

gu.set_brightness(0.5)
graphics.set_font("bitmap8")

# air quality state returns a number so this translates to actual condition
aqiState = {1 : "Good", 2 : "Fair", 3 : "Moderate", 4 : "Poor", 5 : "Very Poor"}

# create the rtc object
rtc = machine.RTC()
year, month, day, wd, hour, minute, second, _ = rtc.datetime()
last_second = second

@micropython.native  # noqa: F821
def from_hsv(h, s, v):

    i = math.floor(h * 6.0)
    f = h * 6.0 - i
    v *= 255.0
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)

    i = int(i) % 6
    if i == 0:
        return int(v), int(t), int(p)
    if i == 1:
        return int(q), int(v), int(p)
    if i == 2:
        return int(p), int(v), int(t)
    if i == 3:
        return int(p), int(q), int(v)
    if i == 4:
        return int(t), int(p), int(v)
    if i == 5:
        return int(v), int(p), int(q)
    
# function for drawing a gradient background
def gradient_background(start_hue, start_sat, start_val, end_hue, end_sat, end_val):

    half_width = width // 2
    for x in range(0, half_width):
        hue = ((end_hue - start_hue) * (x / half_width)) + start_hue
        sat = ((end_sat - start_sat) * (x / half_width)) + start_sat
        val = ((end_val - start_val) * (x / half_width)) + start_val
        colour = from_hsv(hue, sat, val)
        graphics.set_pen(graphics.create_pen(int(colour[0]), int(colour[1]), int(colour[2])))
        for y in range(0, height):
            graphics.pixel(x, y)
            graphics.pixel(width - x - 1, y)

    colour = from_hsv(end_hue, end_sat, end_val)
    graphics.set_pen(graphics.create_pen(int(colour[0]), int(colour[1]), int(colour[2])))
    for y in range(0, height):
        graphics.pixel(half_width, y)

# function for drawing outlined text
def outline_text(text, x, y):

    # Draw the background based on spacing around the letters, ie. remove the gradient background that has aleary been drawn
    # Format is graphics.text(text, x co-ord, y co-ord, max line width, scale)
    graphics.set_pen(BLACK)
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)
    graphics.rectangle(x-1, y, graphics.measure_text(text, 1) + 1, 7)
    graphics.rectangle(x, y-1, graphics.measure_text(text, 1) - 1, 9)
    # Set pen to white and now write the actual text to the graphics object
    graphics.set_pen(WHITE)
    graphics.text(text, x, y, -1, 1)

# turn on wifi and put it in station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# function to connect to a known wifi network
# networks should be listed in secrets.py as a list of tuples knownMNetworks = [('ssid1','pass1'),('ssid2','pass2')]
def connect():   
    
    scanResult = wlan.scan()
    availNetworks = []
    ssidFound = False
    
    # List all the available SSIDs so they can be checked against the known list
    for x in scanResult:
        availNetworks.append(x[0].decode('UTF-8'))
    
    # Check scanned list against known list and if a match is found add it to a variable and break
    for seenSSIDs in availNetworks: # Iterates through the number of seen SSIDs
        for knownSSIDs in secrets.knownNetworks: # Iterates through the list of known SSIDs
            ssidToCheck = knownSSIDs[0]
            if ssidToCheck in seenSSIDs: # Checks if current iteration of known SSID is present in the list of ones seen
                ssidToUse = knownSSIDs # Sets the SSID name we know AND can see into this variable
                ssidFound = True # Drives the next if statement to break out of for loop
                break
        if ssidFound:
            break
    
    # If we found an SSID that matches we now attempt a connection
    if ssidFound:
        drawDisplay("Known SSID found ... connecting to " + ssidToUse[0]) # Just for debug info but also can see when Wifi has dropped out etc
        wlan.connect(ssidToUse[0], ssidToUse[1]) # ssidToUse will contain but the SSID and Password at the 0 and 1 index respectively
        max_wait = 20
        while max_wait > 0:
            if wlan.status() != 3: # Status other than 3 suggests no connection has been made
                print ("Waiting for network")
                time.sleep(1)
                max_wait -=1
                if max_wait == 0:
                    drawDisplay("Connection time out")
            else: # Status 3 means connection is established
                status = wlan.ifconfig()
                print( 'ip = ' + status[0] ) # Just outputting to serial as seems overkill to send to display but could be useful debug
                max_wait = 0 # Ends while loop
    else:
        drawDisplay("No Known SSIDs found")
        
#function to check if the wifi is connected
def checkWifiStatus():
    
    # Status 3 means Wifi is connected
    if wlan.status() != 3:
        return(False)
    else:
        return(True)
    
#function to rerurn the current IP address
def getIP():
    
    status = wlan.ifconfig()
    return( status[0] )

def getLocalWeather():
    
    # Get current weather conditions from openweathermap and format the return JSON object
    url = (f'https://api.openweathermap.org/data/3.0/onecall?lat={secrets.latitude}&lon={secrets.longitude}&units=metric&exclude=minutely,hourly&appid={secrets.openWeatherAPI}')
    response = urequests.get(url)
    data = response.json()

    # Extract data from the "current" object
    current_data = data.get('current', {})
    current_temperature = current_data.get('temp')
    dew_point = current_data.get('dew_point')
    pressure = current_data.get('pressure')
    humidity = current_data.get('humidity')
    wind_speed = current_data.get('wind_speed')
    wind_gust = current_data.get('wind_gust')
    weather_description = current_data.get('weather', [{}])[0].get('description')
    weather_icon = current_data.get('weather', [{}])[0].get('icon')

    # Extract daily min and max temperatures from the first entry in "daily"
    daily_data = data.get('daily', [{}])[0]
    daily_min_temp = daily_data.get('temp', {}).get('min')
    daily_max_temp = daily_data.get('temp', {}).get('max')

    # Check for data in the "alerts" object
    alerts_data = data.get('alerts', [])
    alerts_present = bool(alerts_data)

    #Return a dict of all values collected
    return {
        'current_temperature': current_temperature,
        'dew_point': dew_point,
        'pressure': pressure,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'wind_gust': wind_gust,
        'weather_description': weather_description,
        'weather_icon': weather_icon,
        'daily_min_temp': daily_min_temp,
        'daily_max_temp': daily_max_temp,
        'alerts_present': alerts_present
    }

def getAirQuality():

    # Also using the openweathermap api, but a different end point to the main data, to get the current air quality
    url = (f'http://api.openweathermap.org/data/2.5/air_pollution?lat={secrets.latitude}&lon={secrets.longitude}&appid={secrets.openWeatherAPI}')
    response = urequests.get(url)
    aqiData = response.json()
    # Extract the value from the returned data
    aqiValue = aqiData['list'][0]['main']['aqi']
    return(aqiValue)

#function to get a random fact
def getFact():

    response = urequests.get('https://api.api-ninjas.com/v1/facts?limit=1', headers={'X-Api-Key': secrets.apiNinjasKey})
    fact = response.json()
    return(fact[0]['fact'])

#function to get a random "Dad Joke"
def getDadJoke():

    # Use the api-ninjas api to get a random "Dad Joke"
    response = urequests.get('https://api.api-ninjas.com/v1/dadjokes?limit=1', headers={'X-Api-Key': secrets.apiNinjasKey})
    joke = response.json()
    return(joke[0]['joke'])

#function to get the METAR of a supplied airport from the checkWx api
def getMetar(airport):
    
    # Use the checkwx api to get the METAR for a supplied airport
    url = (f"https://api.checkwx.com/metar/{airport}?x-api-key={secrets.checkWxAPI}")
    checkWx = urequests.get(url)
    metar = checkWx.json()['data']
    return(str(metar).strip("[']"))

# function to get the latest bbc headlines from the newsdataio api
def getNews():

    # Use the newsdataio api to get the latest 5 headlines, no content, from the BBC in English
    newsUrl = (f'https://newsdata.io/api/1/news?apikey={secrets.newsdataioKey}&domain=bbc&full_content=0&image=0&video=0&size=5&language=en')
    response = urequests.get(newsUrl)
    headlines = response.json()
    topStories = []
    for story in headlines['results']: # Create a list of the headlines to be returned
        topStories.append(story['title'])
    return(topStories)

#function to get the latest river level from the environment agency at a certain station
def getRiverLevel():

    # Use the environment agency API to retrieve the current river level
    try:
        response = urequests.get(secrets.river_url)

        if response.status_code == 200: # Code 200 means success
            data = response.json()
            
            # Extract the value from the JSON response
            latest_reading = data.get("items", {}).get("latestReading")
            if latest_reading:
                value = latest_reading.get("value")

                if value is not None: # Resonse valid and has a value for river height
                    #urequests.post(secrets.pushsafer_url)
                    #Use above call to send push notification when river level is above threshold value
                    return(value)
                
                else: # Response valid but no value found
                    print("Value not found in the response.")

            else: # Response valid but no value present
                print("Latest reading data not found in the response.")

        else: # Response invalid
            print(f"Failed to retrieve data. Status code: {response.status_code}")

    except urequests.exceptions.RequestException as e: # Some other failure
        print(f"Error: {e}")
        
#function to synchronize the RTC time from NTP
def syncTime():
    
    try:
        ntptime.settime()
        print("Time set")
        
    except OSError:
        pass

#function to update the rtc variables
def updateTime():
    
    # Need to call regularly to update the time variables
    global year, month, day, wd, hour, minute, second, last_second
    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    
#function to calculate the % to midday for the grad backgrond feature
def percentToMid():

    time_through_day = (((hour * 60) + minute) * 60) + second
    percent_through_day = time_through_day / 86400
    percent_to_midday = 1.0 - ((math.cos(percent_through_day * math.pi * 2) + 1) / 2)
    return(percent_to_midday)

#function to calculate the hue, sat and val global values
def gradBackgroundColours():

    global hue, sat, val
    percent_to_midday = percentToMid()
    hue = ((MIDDAY_HUE - MIDNIGHT_HUE) * percent_to_midday) + MIDNIGHT_HUE
    sat = ((MIDDAY_SATURATION - MIDNIGHT_SATURATION) * percent_to_midday) + MIDNIGHT_SATURATION
    val = ((MIDDAY_VALUE - MIDNIGHT_VALUE) * percent_to_midday) + MIDNIGHT_VALUE

#fuction to draw to the display
def drawDisplay(message):

    # Need to first work out if message is too long to be static
    messageWidth = graphics.measure_text(message, 1)
    
    # Decide whether to send to static display or scroll functions
    if messageWidth <= (width - 2): #message does not need to scroll
        
        # Set background
        gradBackgroundColours()
        gradient_background(hue, sat, val, hue + HUE_OFFSET, sat, val)
        # Work out where to start the text in x position so it is centered
        xPos = int(width / 2 - messageWidth / 2 + 1)
        outline_text(message, xPos, 2) #y position is always 2 with the bitmap8 font
        gu.update(graphics)

    else:
        #message is longer than display so needs to scroll
        textToScroll(message)
        
#function for drawing scrolling text on the display
def textToScroll(message):
    
    #print("Text to scroll")
    shift = 0
    state = STATE_PRE_SCROLL

    # calculate the message width so scrolling can happen
    msg_width = graphics.measure_text(message, 1)
    last_time = time.ticks_ms()
    scrolling = True

    while scrolling:

        # Modified from the Pimoroni example code so that it can work with a gradient background
        # rather than a fixed colour one
        time_ms = time.ticks_ms()

        if state == STATE_PRE_SCROLL and time_ms - last_time > HOLD_TIME * 1000:
            if msg_width + PADDING * 2 >= width:
                state = STATE_SCROLLING
            last_time = time_ms

        if state == STATE_SCROLLING and time_ms - last_time > STEP_TIME * 1000:
            shift += 1
            if shift >= (msg_width + PADDING * 2) - width - 1:
                state = STATE_POST_SCROLL
            last_time = time_ms

        if state == STATE_POST_SCROLL and time_ms - last_time > HOLD_TIME * 1000:
            state = STATE_PRE_SCROLL
            shift = 0
            last_time = time_ms
            scrolling = False
            return

        gradBackgroundColours()
        gradient_background(hue, sat, val, hue + HUE_OFFSET, sat, val)
        outline_text(message, x=PADDING - shift, y=2)

        # update the display
        gu.update(graphics)

        # pause for a moment (important or the USB serial device will fail)
        time.sleep(0.001)

#function for drawing the clock and current temp on the display
def drawClock():
    clock = "{:02}:{:02}z".format(hour, minute)
    tempDisplay = ("{:.{}f}".format(localWx['current_temperature'], 0) + chr(176))
    clockWidth = graphics.measure_text(clock, 1)
    tempWidth = graphics.measure_text(tempDisplay, 1)
    xSpace = int((width - (clockWidth + tempWidth))/2)
    gradBackgroundColours()
    gradient_background(hue, sat, val, hue + HUE_OFFSET, sat, val)
    outline_text(clock, xSpace -2 , 2)
    outline_text(tempDisplay, width - (xSpace + tempWidth) + 2, 2)
    gu.update(graphics)

#connect to wifi before main loop can begin
while checkWifiStatus() == False:
    connect()

#sync the time with ntp
if checkWifiStatus() == True:
    syncTime()

lastMinute = minute - 1 # updates the display every minute so can monitor when the minute changes
apisChecked = False
displayCycleChecked = False
headlineToDisplay = 0

#get all APIs pre-loaded
localWx = getLocalWeather()
#need weather before drawing clock for temp display so writing clock now so display not empty
drawClock()
joke = getDadJoke()
fact = getFact()
metar = getMetar('EGCC')
headlines = getNews()
riverLevel = getRiverLevel()
airQuality = getAirQuality()

while True:# main loop
    
    updateTime()
    if minute != lastMinute: # new minute so redraw clock and need to set chek flags to false
        drawClock()
        displayCycleChecked = False
        apisChecked = False
        lastMinute = minute
    
    if second == 10 and apisChecked == False:#check if there is an API to call scheduled for this minute
        if minute in cycles.apiFetchCycle:#been found so there is something to do
            # 1 = local weather , 2 = news , 3 = river , 4 = facts , 5 = air quality , 6 = METAR , 7 = joke
            if cycles.apiFetchCycle[minute] == 1:
                localWx = getLocalWeather()
            elif cycles.apiFetchCycle[minute] == 2:
                headlines = getNews()
            elif cycles.apiFetchCycle[minute] == 3:
                riverLevel = getRiverLevel()
            elif cycles.apiFetchCycle[minute] == 4:
                fact = getFact()
            elif cycles.apiFetchCycle[minute] == 5:
                airQuality = getAirQuality()
            elif cycles.apiFetchCycle[minute] == 6:
                metar = getMetar('EGCC')
            elif cycles.apiFetchCycle[minute] == 7:
                joke = getDadJoke()
            else:
                print("Unknown number in apiFetchCycle. Check cycles.py file")
        apisChecked = True
    
    if second > 20 and displayCycleChecked == False:#check if there is to display for this minute
        if minute in cycles.displayCycle:#minute has been found so there is something to do
            # 1 = local weather , 2 = news , 3 = river , 4 = facts , 5 = air quality , 6 = METAR , 7 = joke
            if cycles.displayCycle[minute] == 1:
                #place holder until decided what I want to see
                pass
            elif cycles.displayCycle[minute] == 2:
                drawDisplay(headlines[headlineToDisplay])
                headlineToDisplay = headlineToDisplay + 1 #increment so see next headline next time
                if headlineToDisplay == 5:#it got too big to cycle back to 0
                    headlineToDisplay = 0
            elif cycles.displayCycle[minute] == 3:
                drawDisplay(f'River Rother is currently at {riverLevel}m')
            elif cycles.displayCycle[minute] == 4:
                #placeholder as not going to use facts as too long
                pass
            elif cycles.displayCycle[minute] == 5:
                drawDisplay(f'Air quality is {aqiState[airQuality]}')
            elif cycles.displayCycle[minute] == 6:
                drawDisplay(metar)
            elif cycles.displayCycle[minute] == 7:
                drawDisplay(joke)
            else:
                print('Unknown number in displayCycle. Check cycles.py file')
        drawClock() # Need to draw clock again once the other information has been displayed
        displayCycleChecked = True