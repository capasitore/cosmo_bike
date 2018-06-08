#!/usr/bin/env python
#
# Redirect data from a TCP/IP connection to a serial port and vice versa.
#
# (C) 2002-2016 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause


from __future__ import absolute_import

import sys
from struct import *
import socket
import serial
import serial.threaded
import serial
from serial.tools.list_ports import comports
from serial.tools import hexlify_codec
import time
import cosmo_bike.utils as utils



class BikeComm():
    def __init__(self):
        self.serial = None
        self.quiet = True

    def __call__(self):
        return self

    def _debug(self, msg):
        if not self.quiet:
            sys.stderr.write(msg)

    def connect(self, port=''):
        # connect to serial port
        ser = serial.Serial(port, 19200, timeout=1)
        self.serial = ser

        if not self.quiet:
            self._debug(
                '--- Serial configuration {p.name}  {p.baudrate},{p.bytesize},'
                '{p.parity},{p.stopbits} ---\n'.format(p=self.serial))

        try:
            ser.open()
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
            sys.exit(1)

    def disconnect(self):
        sys.stderr.write('\n--- exit ---\n')
        self.serial.close()
        # TODO: how to stop it

    def write_bytes(self, byte_string, use_checksum=True):
        """Write bytes (already encoded)"""
        data = str(byte_string)
        n = 0
        if use_checksum:
            data += utils.calc_checksum(data)
        # retry 3 times
        for i in range(0, 3):
            n = self.serial.write(byte_string + utils.calc_checksum(byte_string))
            if n == len(data):
                break
        if n is not len(data):
            return 0
        return n

    def read_bytes_with_checksum(self):
        """read bytes (already encoded)"""
        resp = []
        data = []
        try:
            resp = self.serial.read(100)
            _data = '0x20' + resp[:2]
            ch = utils.calc_checksum(_data)
            # validate checksum
            if ch == resp[2]:
                data = resp[:2]

        except serial.SerialTimeoutException:
            resp = None
        finally:
            self.serial.flush()
        return resp

    def speed(self):
        cmd = '\x11\x20'
        speed = 0
        if self.write_bytes(cmd, False):
            bytes = self.read_bytes_with_checksum()
            # get unsigned integer 16-bit
            values = unpack('H', bytes)
            #interpolate
            speed = values[0] * 33.0 / 256.0
        return speed

    def set_gear(self, level= 0):
        gears = ['\x00', '\x0b', '\x0d', '\x15', '\x17', '\x03']
        if level >= len(gears):
            return
        gear = gears[level]
        cmd = '\x16\x0b' + gears[level]
        if self.write_bytes(cmd, True):
            # it does not receives a response
            pass

    def battery_level(self):
        cmd = '\x11\x11'
        level = 0
        if self.write_bytes(cmd, False):
            bytes = self.read_bytes_with_checksum()
            # get unsigned integer 16-bit
            values = unpack('B', bytes)
            #interpolate
            level = values[0]
        return level



