import time
import serial
import io
import time
import RPi.GPIO as GPIO

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


def destroy():
    motor.close()
    pass


def motor_read_write(s):
    screen.write(bytes(s))
    motordata = motor.readline()
    print("Motor Data   : " + repr(motordata))
    return motordata


if __name__ == '__main__':
    try:
        done = True
        while 1:
            if done:
                b = b'\xf1'
                done = False
            else:
                b = b'\xf0 '
                done = True
            data = motor_read_write(b'\x16\x1a'+b)
            time.sleep(0.5)
            print(b)

    except KeyboardInterrupt:
        destroy()








