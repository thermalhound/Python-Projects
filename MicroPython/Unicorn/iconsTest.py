from time import sleep
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
import icons

gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

BLACK = graphics.create_pen(0, 0, 0)

def clearDisplay():
    graphics.set_pen(BLACK)
    graphics.clear()
    gu.update(graphics)
    
def clearGraphics():
    graphics.set_pen(BLACK)
    graphics.clear()
    
while True:
    icons.clearDay(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.clearNight(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.lightCloudDay(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.lightCloudNight(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.heavyCloudDay(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.heavyCloudNight(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.cloudy(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.lightRain(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.heavyRain(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.lightning(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.snowIce(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()
    icons.foggy(graphics)
    gu.update(graphics)
    sleep(2)
    clearDisplay()
    clearGraphics()