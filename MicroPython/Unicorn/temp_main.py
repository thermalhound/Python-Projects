# Main code for running on the Galactic unicorn

import multiwifi

if (multiwifi.checkWifiStatus() == False): #if wifi isn't already connected connect it
    multiwifi.connect()
