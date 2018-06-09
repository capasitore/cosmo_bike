import time
import serial
import io
from struct import *
import time
import RPi.GPIO as GPIO
from threading import Event , Thread

#HELLO DEMO
interrupt=0
event=Event()
screen = serial.Serial(
        port='/dev/ttyUSB1',
        baudrate = 1200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout= 0.1
)

motor = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=1200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.1
)

bike_status ={}
bike_control ={'gear': 0, 'light': False}

def destroy():
    motor.close()
    screen.close()
    pass

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

def motor_read_write(s):
    screen.write(bytes(s))
    motordata = motor.readline()
    print("Motor Data   : " + repr(motordata))
    return motordata

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

def set_gear(level=0):
    gears = ['\x00', '\x0b', '\x0d', '\x15', '\x17', '\x03']
    if level >= len(gears):
        return
    gear = gears[level]
    cmd = '\x16\x0b' + gear
    cmd += calc_checksum(cmd)
    motor.write(string_as_bytes(cmd))
    if n == len(cmd):
        bike_status['gear'] = level

def update():
    if bike_control['light'] != bike_status['light']:
        set_ligths(bike_control['light'])
    if bike_control['gear'] != bike_status['gear']:
        set_gear(bike_control['gear'])

def set_ligths(on:bool):
    screen.write(bytes(on))
    cmd = b'\x16\x1A'
    cmd += ['\xf0' if on else '\xf1']
    n = motor.write(string_as_bytes(cmd))
    if n == len(cmd):
        bike_status['light'] = on


def parse_data(send_data, rcv_data):
    if not len(send_data) > 1:
        return

    if send_data[0] == '\x11':
        if send_data[1] == '\x20':
            # speedometer
            speed = 0
            if validate_response(rcv_data, bytearray(b'\x20')):
                values = unpack('H', rcv_data)
                # interpolate
                speed = values[0] * 33.0 / 256.0
                bike_status['speed'] = speed
        elif send_data[1] == '\x11':
            # speedometer
            speed = 0
            if validate_response(rcv_data):
                values = unpack('B', rcv_data)
                # interpolate
                bike_status['battery'] = values[0]


class SniffThread(Thread):

    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)

    def run(self):
        # Read Screen Data
        screendata = screen.readline()
        moreBytes = screen.inWaiting()
        while moreBytes:
            screendata = screendata + screen.read(moreBytes)
            moreBytes = screen.inWaiting()
        # Write to motor
        motor.write(screendata)
        # Read Motor Data
        moreBytes = 0
        motordata = motor.readline()
        moreBytes = motor.inWaiting()
        while moreBytes:
            motordata = motordata + motor.read(moreBytes)
            moreBytes = motor.inWaiting()
        print(moreBytes)
        # Write to screen
        screen.write(motordata)
        print("Motor Data   : " + repr(motordata))
        print("Screen Data   : " + repr(screendata))
        print(len(motordata))
        print(len(screendata))
        parse_data(motordata, screen)
        update()
        # interrupt for thread
        if interrupt == 1:
            event.set()
            # time.sleep(0.1)



if __name__ == '__main__':
        try:
                # Declare objects of MyThread class
                myThreadOb1 = SniffThread()
                myThreadOb1.start()
                myThreadOb1.join()
        except KeyboardInterrupt:
                destroy()



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








