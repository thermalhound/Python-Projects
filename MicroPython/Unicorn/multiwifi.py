# multiple known networks connection

import network
import time
import secrets # include list knownNetworks with tuples formatted ('SSID', 'Password')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def connect():   
    
    scanResult = wlan.scan()
    availNetworks = []
    
    for x in scanResult:
        availNetworks.append(x[0].decode('UTF-8'))
    
    print(availNetworks)
    
    ssidFound = False
    ssidIndex = []
    
    for seenSSIDs in availNetworks:
        for knownSSIDs in secrets.knownNetworks:
            ssidToCheck = knownSSIDs[0]
            if ssidToCheck in seenSSIDs:
                ssidToUse = knownSSIDs
                ssidFound = True
                break
        if ssidFound:
            break
        
    if ssidFound:
        print("Known SSID found ... connecting to ", ssidToUse[0])
        wlan.connect(ssidToUse[0], ssidToUse[1])
        max_wait = 20
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
    else:
        print("No Known SSIDs found")
        
def checkWifiStatus():
    
    if wlan.status() != 3:
        return(False)
    else:
        return(True)
    
def getIP():
    status = wlan.ifconfig()
    return( status[0] )