import sys
import numpy as np
import time
import threading

from cosmo_bike.bike_comm import *

class CommThread (threading.Thread):
   def __init__(self):
       threading.Thread.__init__(self)
       self.comm = BikeComm()
       self.comm.connect('/dev/ttyACM0')

   def run(self):
       comm = self.comm
       while (1):
           comm.speed()
           comm.battery_level()
           time.sleep(0.2)

   def __del__(self):
       self.comm.disconnect()

if __name__ == '__main__':

    time.sleep(3)


    commThread = CommThread()
    commThread.run()



