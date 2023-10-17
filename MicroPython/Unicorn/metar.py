import urequests
import secrets

def getMetar(airport):
    
    url = ("https://api.checkwx.com/metar/" + airport + "?x-api-key=" + secrets.checkWxAPI)
    #print(url)
    checkWx = urequests.get(url)
    #print(checkWx)
    metar = checkWx.json()['data']
    return(str(metar).strip("[']"))