import time
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
import network
import urequests

'''
Display scrolling wisdom, quotes or greetz.
You can adjust the brightness with LUX + and -.
'''

# constants for controlling scrolling text
PADDING = 5
MESSAGE_COLOUR = (255, 255, 255)
OUTLINE_COLOUR = (0, 0, 0)
BACKGROUND_COLOUR = (10, 0, 96)
MESSAGE = ""
HOLD_TIME = 3.0
STEP_TIME = 0.120

# create galactic object and graphics surface for drawing
gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

# function for drawing outlined text
def outline_text(text, x, y):
    graphics.set_pen(graphics.create_pen(int(OUTLINE_COLOUR[0]), int(OUTLINE_COLOUR[1]), int(OUTLINE_COLOUR[2])))
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)

    graphics.set_pen(graphics.create_pen(int(MESSAGE_COLOUR[0]), int(MESSAGE_COLOUR[1]), int(MESSAGE_COLOUR[2])))
    graphics.text(text, x, y, -1, 1)

def connectWifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('VM2023F8', '3bBtbcmsw5Kv')
    print(wlan.status())

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() == 0: # seems to error out so try again ...
            print('Have you tried turning it on and off again?')
            wlan.disconnect()
            time.sleep(1)
            max_wait = 10 # reset to allow 10 seconds connection time for new SSID
            wlan.connect('PLUSNET-M9WR', '48b4ea3c53')
            print(wlan.status())
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

connectWifi()

gu.set_brightness(0.5)

# state constants
STATE_PRE_SCROLL = 0
STATE_SCROLLING = 1
STATE_POST_SCROLL = 2

shift = 0
state = STATE_PRE_SCROLL

# set the font
graphics.set_font("bitmap8")

checkWx = urequests.get('https://api.checkwx.com/metar/EGCC?x-api-key=5e9cbb90f62444498528bc667b')
print(checkWx)
metar = checkWx.json()['data']
MESSAGE = str(metar)


# calculate the message width so scrolling can happen
msg_width = graphics.measure_text(MESSAGE, 1)

last_time = time.ticks_ms()

while True:
    time_ms = time.ticks_ms()

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        gu.adjust_brightness(+0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        gu.adjust_brightness(-0.01)

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

    graphics.set_pen(graphics.create_pen(int(BACKGROUND_COLOUR[0]), int(BACKGROUND_COLOUR[1]), int(BACKGROUND_COLOUR[2])))
    graphics.clear()

    outline_text(MESSAGE, x=PADDING - shift, y=2)

    # update the display
    gu.update(graphics)

    # pause for a moment (important or the USB serial device will fail)
    time.sleep(0.001)