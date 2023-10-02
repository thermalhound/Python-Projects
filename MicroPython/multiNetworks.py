# multiple known networks connection

import network
import time
import secrets # include list knownNetworks with tuples formatted ('SSID', 'Password')

def connect_wifi():   
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    #wlan.connect(secrets.homeSSID, secrets.homePwd)
    #print(wlan.status())
    
    scanResult = wlan.scan()
    availNetworks = []
    for x in scanResult:
        availNetworks.append(x[0].decode('UTF-8'))
    
    print(availNetworks)
    
    for y in secrets.knownNetworks:
        try:
            print(availNetworks.index(y[0]))
            print (y[0],y[1])
            wlan.connect(y[0], y[1])
            print(wlan.status())
            #return
            
        except ValueError:
            pass
        
    max_wait = 10
    while max_wait > 0:
        if wlan.status() != 3:
            print ("Waiting for network")
            time.sleep(1)
            max_wait -=1
            if max_wait == 0:
                print ("Connection time out")
        else:
            print('connected')
            status = wlan.ifconfig()
            print( 'ip = ' + status[0] )
            max_wait = 0 # ends while loop