'''
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
import iconsTest

gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)
ORANGE = graphics.create_pen(255,191,0)
CYAN = graphics.create_pen(0,0,255)
BLUE = graphics.create_pen(64,0,255)
YELLOW = graphics.create_pen(255,255,0)
'''
#01d - clear day

def clearDay(graphics):
    graphics.set_pen(graphics.create_pen(255,191,0))
    graphics.circle(5,5,3) # centre x / y and radius
    graphics.line(1,1,10,10) # x/y start x/y stop
    graphics.line(9,1,1,10)
    graphics.line(5,0,5,11)
    graphics.line(0,5,11,5)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.circle(5,5,2)

#01n - clear night

def clearNight(graphics):
    graphics.set_pen(graphics.create_pen(0,0,255))
    graphics.circle(5,5,4)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.circle(8,3,4)

#02d - light cloud day

def lightCloud(graphics):
    graphics.set_pen(graphics.create_pen(255, 255, 255))
    graphics.line(0,9,8,9)
    graphics.line(1,8,7,8)
    graphics.line(2,7,6,7)
    graphics.line(3,6,5,6)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.line(2,8,6,8)
    graphics.line(3,7,5,7)

def lightCloudDay(graphics):
    graphics.set_pen(graphics.create_pen(255,191,0))
    graphics.circle(6,5,3) # centre x / y and radius
    graphics.line(2,1,11,10) # x/y start x/y stop
    graphics.line(10,1,8,3)
    graphics.line(6,0,6,2)
    graphics.line(1,5,11,5)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.circle(6,5,2)
    lightCloud(graphics)

#02n - light cloud night

def lightCloudNight(graphics):
    graphics.set_pen(graphics.create_pen(0,0,255))
    graphics.circle(6,4,4)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.circle(9,2,4)
    lightCloud(graphics)

#03d - heavy cloud day

def heavyCloud(graphics):
    graphics.set_pen(graphics.create_pen(255, 255, 255))
    graphics.line(0,9,10,9)
    graphics.line(1,8,9,8)
    graphics.line(1,7,10,7)
    graphics.line(2,6,9,6)
    graphics.line(3,5,8,5)
    graphics.line(5,4,7,4)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.rectangle(3,6,5,3)
    graphics.line(5,5,7,5)
    graphics.line(2,7,2,9)
    graphics.pixel(8,7)
    
def heavyCloudDay(graphics):
    graphics.set_pen(graphics.create_pen(255,191,0))
    graphics.circle(7,4,2) # centre x / y and radius
    graphics.line(4,1,11,8) # x/y start x/y stop
    graphics.line(10,1,8,3)
    graphics.line(7,0,7,2)
    graphics.line(3,4,11,4)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.circle(7,4,1)
    heavyCloud(graphics)

#03n - heavy cloud night

def heavyCloudNight(graphics):
    graphics.set_pen(graphics.create_pen(0,0,255))
    graphics.circle(7,3,3)
    graphics.pixel(9,6)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.circle(9,2,3)
    heavyCloud(graphics)

#04 - cloudy

def cloudy(graphics):
    graphics.set_pen(graphics.create_pen(255, 255, 255))
    graphics.line(0,7,10,7)
    graphics.line(1,6,9,6)
    graphics.line(1,5,10,5)
    graphics.line(2,4,9,4)
    graphics.line(3,3,8,3)
    graphics.line(5,2,7,2)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.rectangle(3,4,5,3)
    graphics.line(5,3,7,3)
    graphics.line(2,5,2,7)
    graphics.pixel(8,5)

#09 -  light rain

def rainCloud(graphics):
    graphics.set_pen(graphics.create_pen(255, 255, 255))
    graphics.line(0,6,10,6)
    graphics.line(1,5,9,5)
    graphics.line(1,4,10,4)
    graphics.line(2,3,9,3)
    graphics.line(3,2,8,2)
    graphics.line(5,1,7,1)
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.rectangle(3,3,5,3)
    graphics.line(5,2,7,2)
    graphics.line(2,4,2,6)
    graphics.pixel(8,4)
    
def lightRain(graphics):
    rainCloud(graphics)
    graphics.set_pen(graphics.create_pen(64,0,255))
    graphics.line(3,6,0,9)
    graphics.line(7,6,4,9)

#10 -  heavy rain

def heavyRain(graphics):
    rainCloud(graphics)
    graphics.set_pen(graphics.create_pen(64,0,255))
    graphics.line(3,6,0,10)
    graphics.line(5,6,2,10)
    graphics.line(7,6,4,10)

#11 - lightning

def lightning(graphics):
    rainCloud(graphics)
    graphics.set_pen(graphics.create_pen(64,0,255))
    graphics.line(2,6,0,9)
    graphics.line(8,6,5,9)
    #lightning bolt
    graphics.set_pen(graphics.create_pen(255,255,0))
    graphics.line(5,6,3,10)

#13 - snow and ice

def snowIce(graphics):
    graphics.set_pen(graphics.create_pen(0,0,255))
    graphics.line(2,5,9,5)
    graphics.line(5,2,5,9)
    graphics.line(1,1,10,10)
    graphics.line(1,9,10,1)
    #horizontal and vertical accents
    graphics.pixel(4,1)
    graphics.pixel(6,1)
    graphics.pixel(4,9)
    graphics.pixel(6,9)
    graphics.pixel(1,4)
    graphics.pixel(1,6)
    graphics.pixel(9,4)
    graphics.pixel(9,6)
    #diagonal accents
    graphics.pixel(1,0)
    graphics.pixel(0,1)
    graphics.pixel(9,0)
    graphics.pixel(10,1)
    graphics.pixel(0,9)
    graphics.pixel(1,10)
    graphics.pixel(10,9)
    graphics.pixel(9,10)

#50 - foggy

def foggy(graphics):
    graphics.set_pen(graphics.create_pen(255, 255, 255))
    graphics.line(0,2,3,0)
    graphics.line(3,0,8,5)
    graphics.line(8,4,11,2)
    graphics.line(0,5,3,3)
    graphics.line(3,3,8,8)
    graphics.line(8,7,11,5)
    graphics.line(0,8,3,6)
    graphics.line(3,6,8,11)
    graphics.line(8,10,11,8)
