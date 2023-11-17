import urequests
import secrets

def getMetar(airport):
    
    url = ("https://api.checkwx.com/metar/" + airport + "?x-api-key=" + secrets.checkWxAPI)
    print('Getting weather')
    checkWx = urequests.get(url)
    print('Formatting weather')
    metar = checkWx.json()['data']
    return(str(metar).strip("[']"))