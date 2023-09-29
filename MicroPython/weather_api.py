import network
import time
import urequests
import secrets

baseURL = "https://api.openweathermap.org/"
apiKeyURL = ("&appid=" + secrets.openWeatherAPI)
weatherURL = "data/3.0/onecall?lat=53.38066&lon=-1.470228&exclude=minutely" # lat long for Sheffield
checkWxURL = ('https://api.checkwx.com/metar/EGCC?x-api-key='+secrets.checkWxAPI)
newsapiURL = ('https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=' + secrets.newsapiAPI)
newsapiHeaders = {'User-Agent': 'MicroPython uRequests'}
numInSpaceURL = "http://api.open-notify.org/astros.json"
issPositionURL = "http://api.open-notify.org/iss-now.json"
spacexNextURL = "https://api.spacexdata.com/v5/launches/next"
roadsterInfoURL = "https://api.spacexdata.com/v4/roadster"

def connect_wifi():   
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.homeSSID, secrets.homePwd)
    print(wlan.status())

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() == 0: # seems to error out so try again ...
            print('Have you tried turning it on and off again?')
            wlan.disconnect()
            time.sleep(1)
            max_wait = 10 # reset to allow 10 seconds connection time for new SSID
            wlan.connect(secrets.homeSSID, secrets.homePwd)
            print(wlan.status())
        if wlan.status() == -2: # -2 is the no_net error
            print('Home SSID not found ... trying hackspace ...')
            wlan.disconnect()
            time.sleep(1)
            max_wait = 10 # reset to allow 10 seconds connection time for new SSID
            wlan.connect(secrets.hsSSID, secrets.hsPwd)
        if wlan.status() < -3 or wlan.status() >= 3: # outside of error message range
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        print(wlan.status())
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
    
#locale = urequests.get(baseURL + localeURL + apiKeyURL)
#print(locale.json())

connect_wifi()

weather = urequests.get(baseURL + weatherURL + apiKeyURL)
response = weather.json()

print("Ready...")
current_weather = response['current']['weather'][0]['main']
current_temp = round(response['current']['temp'] - 273.15, 1) # limit to 1 decimal place
current_feels = round(response['current']['feels_like'] - 273.15, 1) # limit to 1 decimal place
hourly_temp = round(response['hourly'][0]['temp'] - 273.15, 1)

print("The current weather is " + current_weather + " with a temperature of " + str(current_temp) + " which feels like " + str(current_feels) + ". In the next hour the temp will be " + str(hourly_temp))

#checkWx = urequests.get(checkWxURL)
#print(checkWx)
#checkWxResponse = checkWx.json()
#print(checkWxResponse)

headlines = urequests.get(newsapiURL, headers=newsapiHeaders)
print(headlines.json())

#numInSpace = urequests.get(numInSpaceURL)
#print(numInSpace.json())

#issPosition = urequests.get(issPositionURL)
#print(issPosition.json())

#spacexNext = urequests.get(spacexNextURL)
#print(spacexNext.json())

roadsterInfo = urequests.get(roadsterInfoURL)
print(roadsterInfo.json())