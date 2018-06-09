from struct import *

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
