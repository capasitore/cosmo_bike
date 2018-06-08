import sys
import numpy as np
import time

from cosmo_bike.bike_comm import *

if __name__ == '__main__':

    time.sleep(3)

    comm = BikeComm()
    comm.connect('/dev/ttyACM0')

    comm.speed()
    comm.battery_level()

    comm.disconnect()

