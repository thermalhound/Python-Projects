import network
import time
import ntptime
import machine

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('CastNet', 'Donald>Mickey!')

steveEpoch = 378907200 

max_wait = 10
while max_wait > 0:
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

rtc = machine.RTC()

try:
    ntptime.settime()
    print("Time set")
except OSError:
    pass

wlan.disconnect()
wlan.active(False)

while True:
    
    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    styear, stmonth, stday, stwd, sthour, stminute, stsecond, st_ = time.gmtime(steveEpoch)
    clock = "{:02}:{:02}:{:02}".format(hour, minute, second)
    print(clock)
    print (str(year) + " / " + str(month) + " / " +  str(day) + " / " +  str(wd) + " / " +  str(hour) + " / " +  str(minute) + " / " +  str(second) + " / " +  str(_))
    print (str(styear) + " / " + str(stmonth) + " / " +  str(stday) + " / " +  str(stwd) + " / " +  str(sthour) + " / " +  str(stminute) + " / " +  str(stsecond) + " / " +  str(st_))
    time.sleep(100)
