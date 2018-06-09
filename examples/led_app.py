import time
import serial
import io
from struct import *
import time
import RPi.GPIO as GPIO
import _rpi_ws281x as ws
from threading import Event , Thread
import cosmo_bike.led_bar as lb




bike_status = {'gear': 0, 'light': False}
bike_control ={'gear': 0, 'light': False}

def calc_checksum(s):
    """
    Calculates checksum for sending commands to the ELKM1.
    Sums the ASCII character values mod256 and returns
    the lower byte of the two's complement of that value.
    """
    #return '%2X' % (-(sum(ord(c) for c in s) % 256) & 0xFF)
    total = 0
    if isinstance(s, str):
        for c in s:
            total += ord(c)
        result = total % 256
        return result
    elif isinstance(bytearray):
        for c in s:
            total += c
        result = total % 256
        return pack('B', result)

def bytes_as_string(b):
    if not isinstance(b, bytearray):
        raise ValueError("Expecting bytearray")
    return "".join(map(chr, b))

def string_as_bytes(s):
    return str.encode(s)

#def motor_read_write(s):
#    screen.write(bytes(s))
#    motordata = motor.readline()
#    print("Motor Data   : " + repr(motordata))
#    return motordata

def validate_response(self, resp, extra_bytes=None):
    """read bytes (already encoded)"""
    _data = []
    try:
        _data = resp[:-1]
        if extra_bytes:
            _data = extra_bytes + resp[:-1]
        ch = calc_checksum(_data)
        # validate checksum
        if ch == resp[-1]:
            data = resp[:-1]
            return True
    except serial.SerialTimeoutException:
        resp = None
    return False

led_bar = lb.LedBar()
led_bar.set_brightness(128)


class SniffThread(Thread):

    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)

    def run(self):
        value = 0
        while(1):

            colors = [lb.DOT_COLORS[value]] * 22
            led_bar.update(colors)
            value = (value + 1) % len(lb.DOT_COLORS)
            print(colors[0])


            # interrupt for thread
            time.sleep(1)



if __name__ == '__main__':
        try:
                # Declare objects of MyThread class
                myThreadOb1 = SniffThread()
                myThreadOb1.start()
                myThreadOb1.join()
        except KeyboardInterrupt:
                pass



#####################################################
def motor_read_write(str):
                interrupt=1
                event.wait()
                motor.write(str)
                motordata = motor.read(1)
                moreBytes = motor.inWaiting()
                if moreBytes:
                        motordata = motordata + motor.read(moreBytes)
                #print  "Motor Data   : "  + repr(motordata)
                event.clear()
                interrupt=0
                return motordata;

def screen_read_write(str):
                interrupt=1
                event.wait()
                screen.write(str)
                screendata = screen.read(1)
                moreBytes = screen.inWaiting()
                if moreBytes:
                        screendata = screendata + screen.read(moreBytes)
                #print  "Screen Data   : " + repr(screendata)
                event.clear()
                interrupt=0
                return screendata;








