import unittest
import os, sys, importlib


import cosmo_bike.utils as utils



class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def testChecksum(self):
        # Cast bytes to bytearray
        expected_value = ord('\x24')
        data = str('\x16\x0b\x03')
        s = str(data)
        checksum = utils.calc_checksum(data)
        self.assertEqual(expected_value, checksum)

