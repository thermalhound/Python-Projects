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

# initial variables


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

PADDING = 5
HOLD_TIME = 2.0
STEP_TIME = 0.055
STATE_PRE_SCROLL = 0
STATE_SCROLLING = 1
STATE_POST_SCROLL = 2

aqiState = {1 : "Good", 2 : "Fair", 3 : "Moderate", 4 : "Poor", 5 : "Very Poor"}

# create galactic object and graphics surface for drawing
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

# create the rtc object
rtc = machine.RTC()
year, month, day, wd, hour, minute, second, _ = rtc.datetime()
last_second = second

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# set up some pens to use later
WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)

gu.set_brightness(0.5)
graphics.set_font("bitmap8")

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
    
    # list all the available SSIDs so they can be checked against the known list
    for x in scanResult:
        availNetworks.append(x[0].decode('UTF-8'))
    
    print(availNetworks)
    
    ssidFound = False
    #ssidIndex = []
    
    for seenSSIDs in availNetworks: # check scanned list against known list and if a match is found add it to a variable and break
        for knownSSIDs in secrets.knownNetworks:
            ssidToCheck = knownSSIDs[0]
            if ssidToCheck in seenSSIDs:
                ssidToUse = knownSSIDs
                ssidFound = True
                break
        if ssidFound:
            break
        
    if ssidFound:
        drawDisplay("Known SSID found ... connecting to " + ssidToUse[0])
        wlan.connect(ssidToUse[0], ssidToUse[1])
        max_wait = 20
        while max_wait > 0:
            if wlan.status() != 3:
                print ("Waiting for network")
                time.sleep(1)
                max_wait -=1
                if max_wait == 0:
                    drawDisplay("Connection time out")
            else:
                status = wlan.ifconfig()
                print( 'ip = ' + status[0] ) #just outputting to serial as seems overkill to send to display but could be useful debug
                max_wait = 0 # ends while loop
    else:
        drawDisplay("No Known SSIDs found")
        
#function to check if the wifi is connected
def checkWifiStatus():
    
    if wlan.status() != 3:
        return(False)
    else:
        return(True)
    
#function to rerurn the current IP address
def getIP():
    status = wlan.ifconfig()
    return( status[0] )

def getLocalWeather():
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

    #return a dict of values
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
    url = (f'http://api.openweathermap.org/data/2.5/air_pollution?lat={secrets.latitude}&lon={secrets.longitude}&appid={secrets.openWeatherAPI}')
    response = urequests.get(url)
    aqiData = response.json()
    aqiValue = aqiData['list'][0]['main']['aqi']
    return(aqiValue)

#function to get a random fact
def getFact():
    response = urequests.get('https://api.api-ninjas.com/v1/facts?limit=1', headers={'X-Api-Key': secrets.apiNinjasKey})
    fact = response.json()
    return(fact[0]['fact'])

def getDadJoke():
    response = urequests.get('https://api.api-ninjas.com/v1/dadjokes?limit=1', headers={'X-Api-Key': secrets.apiNinjasKey})
    joke = response.json()
    return(joke[0]['joke'])

#function to get the METAR of a supplied airport from the checkWx api
def getMetar(airport):
    
    url = (f"https://api.checkwx.com/metar/{airport}?x-api-key={secrets.checkWxAPI}")
    #print('Getting weather')
    checkWx = urequests.get(url)
    #print('Formatting weather')
    metar = checkWx.json()['data']
    return(str(metar).strip("[']"))

# function to get the latest bbc headlines from the newsdataio api
def getNews():
    newsUrl = (f'https://newsdata.io/api/1/news?apikey={secrets.newsdataioKey}&domain=bbc&full_content=0&image=0&video=0&size=5&language=en')
    response = urequests.get(newsUrl)
    headlines = response.json()
    topStories = []
    for story in headlines['results']:
        topStories.append(story['title'])
    return(topStories)

#function to get the latest river level from the environment agency at a certain station
def getRiverLevel():
    try:
        response = urequests.get(secrets.river_url)

        if response.status_code == 200:
            data = response.json()
            
            # Extract the value from the JSON response
            latest_reading = data.get("items", {}).get("latestReading")
            if latest_reading:
                value = latest_reading.get("value")
                if value is not None:
                    #urequests.post(secrets.pushsafer_url)
                    #Use above call to send push notification when river level is above threshold value
                    return(value)
                else:
                    print("Value not found in the response.")
            else:
                print("Latest reading data not found in the response.")

        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")

    except urequests.exceptions.RequestException as e:
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
    global year, month, day, wd, hour, minute, second, last_second
    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    
#function to calculate the % to midday for the grad backgrond feature
def percentToMid():
    time_through_day = (((hour * 60) + minute) * 60) + second
    percent_through_day = time_through_day / 86400
    percent_to_midday = 1.0 - ((math.cos(percent_through_day * math.pi * 2) + 1) / 2)
    return(percent_to_midday)

def gradBackgroundColours():
    global hue, sat, val
    percent_to_midday = percentToMid()
    hue = ((MIDDAY_HUE - MIDNIGHT_HUE) * percent_to_midday) + MIDNIGHT_HUE
    sat = ((MIDDAY_SATURATION - MIDNIGHT_SATURATION) * percent_to_midday) + MIDNIGHT_SATURATION
    val = ((MIDDAY_VALUE - MIDNIGHT_VALUE) * percent_to_midday) + MIDNIGHT_VALUE

#fuction to draw to the display
def drawDisplay(message):
    messageWidth = graphics.measure_text(message, 1)
    
    if messageWidth <= (width - 2): #message does not need to scroll
        #set background
        gradBackgroundColours()
        gradient_background(hue, sat, val, hue + HUE_OFFSET, sat, val)
        #work out where to start the text in x position so it is centered
        xPos = int(width / 2 - messageWidth / 2 + 1)
        outline_text(message, xPos, 2) #y position is always 2 with the bitmap8 font
        gu.update(graphics)
    else:
        #message is longer than display so needs to scroll
        textToScroll(message)
        
def textToScroll(message):
    
    #print("Text to scroll")
    shift = 0
    state = STATE_PRE_SCROLL

    # calculate the message width so scrolling can happen
    msg_width = graphics.measure_text(message, 1)

    last_time = time.ticks_ms()
    
    scrolling = True

    while scrolling:
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
            #graphics.clear()
            #gu.update(graphics)
            scrolling = False
            return

        gradBackgroundColours()
        gradient_background(hue, sat, val, hue + HUE_OFFSET, sat, val)
        outline_text(message, x=PADDING - shift, y=2)

        # update the display
        gu.update(graphics)

        # pause for a moment (important or the USB serial device will fail)
        time.sleep(0.001)
        
#if gu.is_pressed(GalacticUnicorn.SWITCH_A):

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

while checkWifiStatus() == False:
    connect()

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
        drawClock()
        displayCycleChecked = True