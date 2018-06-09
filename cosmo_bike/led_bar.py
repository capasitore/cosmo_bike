import time
import RPi.GPIO as GPIO
from neopixel import *
import _rpi_ws281x as ws

# LED configuration.
LED_CHANNEL    = 0
LED_COUNT      = 22         # How many LEDs to light.
LED_FREQ_HZ    = 800000     # Frequency of the LED signal.  Should be 800khz or 400khz.
LED_DMA        = 10         # DMA channel to use, can be 0-14.
LED_GPIO       = 18         # GPIO connected to the LED signal line.  Must support PWM!
LED_BRIGHTNESS = 255        # Set to 0 for darkest and 255 for brightest
LED_INVERT     = 0          # Set to 1 to invert the LED signal, good if using NPN
                            # transistor as a 3.3V->5V level converter.  Keep at 0
                            # for a normal/non-inverted signal.

# Define colors which will be used by the example.  Each color is an unsigned
# 32-bit value where the lower 24 bits define the red, green, blue data (each
# being 8 bits long).
DOT_COLORS = [  0x200000,   # red
                0x201000,   # orange
                0x202000,   # yellow
                0x002000,   # green
                0x002020,   # lightblue
                0x000020,   # blue
                0x100010,   # purple
                0x200010 ]  # pink

class LedBar():
    def __init__(self):

        #LEDs
        # Create a ws2811_t structure from the LED configuration.
        # Note that this structure will be created on the heap so you need to be careful
        # that you delete its memory by calling delete_ws2811_t when it's not needed.
        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(
            LED_COUNT, LED_GPIO, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, strip_type=ws.WS2812_STRIP)
        # Intialize the library (must be called once before other functions).
        strip.begin()
        self.strip = strip
        self.timestamp = int(round(time.time() * 1000))
        self.min_t = 250



    def set_brightness(self, value):
        self.strip.setBrightness(value)

    def update(self, values=[]):
        # Wrap following code in a try/finally to ensure cleanup functions are called
        # after library is initialized.
        if len(values) != LED_COUNT:
            raise ValueError

        t = int(round(time.time() * 1000))
        delta_t = t - self.timestamp
        self.timestamp = t
        if delta_t > self.min_t:
            # Update each LED color in the buffer.
            for i in range(0, LED_COUNT):
                # Pick a color based on LED position and an offset for animation.
                color = values[i]

                # Set the LED color buffer value.
                self.strip.setPixelColor(i, color)



    def finalyze(self):
        pass
