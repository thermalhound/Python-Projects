# Main code for running on the Galactic unicorn

import multiwifi
import scroll
import metar

while multiwifi.checkWifiStatus() == False:
    print("Wifi not connected")
    scroll.textToScroll("No Network Connected")
    multiwifi.connect()
    
scroll.textToScroll(multiwifi.getIP())
    
#scroll.textToScroll(metar.getMetar('EGCC'))

