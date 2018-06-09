import struct

class Response:

    def __init__(self, *args):
        self.args = []
        for name, fmt in args:
            to_read = struct.calcsize(fmt)
            self.args.append((name, fmt, to_read))

    def decode(self, serial):
        a = {}
        for name, fmt, to_read in self.args:
            a[name] = struct.unpack(fmt, serial.read(to_read))
        return a

    def encode(self, **kwargs):
        if len(kwargs) != len(self.args):
            raise Exception("Lenght is not the same")
        v = b''
        for name, fmt, _ in self.args:
            v = struct.pack('<'+fmt, kwargs[name])
        return v

_R_ = Response

class Command:
    _response = _R_()
    _arguments = 0
    def __init__(self, request, *payload):
        self.request = request
        self.payload = payload

    def __bytes__(self):
        v = self.request
        for x in self.payload:
            v += x
        return v

class ChecksummedCommand(Command):
    def __init__(self, *args):
        super(ChecksummedCommand, self).__init__(*args)

    def checksum(self):
        payload = b''
        for x in self.payload:
            payload += x
        msg = self.request + payload
        s = sum(struct.unpack('<'+'B'*len(msg), msg))
        return s & 0xFF

class Speedometer(Command):
    _response = _R_(("value", 'H'), ("checksum", 'B'))
    def __init__(self):
        super(Speedometer, self).__init__(b'\x11\x20')

class Battery(Command):
    _response = _R_(("value", 'B'), ("checksum", 'B'))
    def __init__(self):
        super(Battery, self).__init__(b'\x11\x11')

class Information1(ChecksummedCommand):
    def __init__(self):
        super(Information1, self).__init__(b'\x11\x60')

class Information2(ChecksummedCommand):
    _response = Response(("crap", 'B'*15), ("checksum", 'B'))
    def __init__(self):
        super(Information2, self).__init__(b'\x11\x61')
### UNKNOWN STUFF ####
class MaybeBrakeSensor(Command):
    def __init__(self):
        super(MaybeBrakeSensor, self).__init__(b'\x11\x08')

class MaybeAmpsSensors(Command):
    def __init__(self):
        super(MaybeAmpsSensors, self).__init__(b'\x11\x0a')
        
class HasChecksum11(ChecksummedCommand):
    def __init__(self):
        super(HasChecksum11, self).__init__(b'\x11\x24')

class NeverReturns(Command):
    def __init__(self):
        super(NeverReturns, self).__init__(b'\x11\x31')

class RunsOnStartup(Command):
    _response = _R_(('Hello', 'B'*2))
    def __init__(self):
        super(RunsOnStartup, self).__init__(b'\x11\x90')



class Gear(ChecksummedCommand):
    INV_MODES = {
        '0/5'       : b'\x00',
        '1/5'       : b'\x0b',
        '2/5'       : b'\x0d',
        '3/5'       : b'\x15',
        '4/5'       : b'\x17',
        '5/5'       : b'\x03'
     }
    MODES = {y: x for (x, y) in INV_MODES.items()}
    _arguments = 1
    def __init__(self, gear):
        try:
            g_ = self.MODES[gear]
        except:
            msg = "%s, only %s allowed" \
                % (gear, str(list(self.MODES.keys())))
            raise GearNotAllowed(msg)
        super(Gear, self).__init__(b'\x16\x0b', gear)

class Light(Command):
    INV_MODES = {
        'on': b'\xf0',
        'off': b'\xf1'
    }
    MODES = {y:x for (x,y) in INV_MODES.items()}
    _arguments = 1
    def __init__(self, mode):
        try:
            state = self.MODES[mode]
        except:
            msg = "%s, only %s allowed" \
                  % (mode, str(list(self.MODES.keys())))
            raise LightModeNotAllowed(msg)
        super(Light, self).__init__(b'\x16\x1a', mode)



class HasChecksum16(ChecksummedCommand):
    def __init__(self):
        super(HasChecksum16, self).__init__(b'\x16\x1f\x00\xc1')


class Sniffer:
    # TODO I think something is a keepalive
    def __init__(self, screen, motor):
        self.screen = screen
        self.motor  = motor
        self.current_command = None
        self.current_response = None

    def listen_to_motor(self):
        """
        return a dictionary with the command's payload
        :return:
        """
        self.current_response = self.current_command._response.decode(self.motor)
        return self.current_response

    def forward_to_screen(self, response=None, **kwargs):
        if response is None:
            e = self.current_command._response.encode(**self.current_response)
        else:
            e = response.encode(**kwargs)
        self.screen.write(e)

    def listen_to_screen(self):
        # recognize the action by parsing it with PARSER
        # read one byte
        p = self.screen.read(2)
        cmd = PARSER[p[0]][p[1]]
        if cmd in (Light, Gear):
            arg = self.screen.read(1)
            inst_cmd = cmd(arg)
        else:
            inst_cmd = cmd()
        return cmd

    def forward_to_motor(self, command=None):
        if command is None:
            cmd = self.current_command
        else:
            cmd = command
            # TODO stack of commands, contexts etc etc
            self.current_command = command
        self.motor.write(bytes(cmd))



PARSER = {
    b'\x11' : {
        b'\x20' : Speedometer,
        b'\x11' : Battery,
        b'\x60' : Information1,
        b'\x61' : Information2,
        b'\x08' : MaybeBrakeSensor,
        b'\x0a' : MaybeAmpsSensors,
        b'\x24\x35' : HasChecksum11,
        b'\x31' : NeverReturns,
        b'\x90' : RunsOnStartup,
    },
    b'\x16' : {
        b'\x0b' : Gear,
        b'\x1a' : Light,
        b'\x1f\x00\xc1\xf6' : HasChecksum16
    }
}
