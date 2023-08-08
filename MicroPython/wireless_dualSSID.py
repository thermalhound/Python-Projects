import network
import time
import secrets

def connect_wifi():   
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.homeSSID, secrets.homePwd)
    print(wlan.status())

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() == -2:
            print('Home SSID not found ... trying hackspace ...')
            wlan.disconnect()
            time.sleep(1)
            max_wait = 10 # reset to allow 10 seconds connection time for new SSID
            wlan.connect(secrets.hsSSID, secrets.hsPwd)
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
        
connect_wifi()
