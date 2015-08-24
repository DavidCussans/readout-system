"""
adc.py provides functionality to control one or more LTM9007 ADCs via IPbus.
Each chip is really two four channel ADCs, with each controlled with a separate
chip select line. Bank A is channels 1, 4, 5, 8. Bank B is 2, 3, 6, 7.

Control is via a simple SPI interface where 16 bits are transferred.
b0 is read/!write
b7:1 are the register address
b15:b8 are the data sent to/from the ADC

If the ADC.cehckwrite flag is True then all write commands will immediately
be confirmed by a read command to the same address.
"""

lvdscurrents = {
        3.5: 0b000,
        4.0: 0b001,
        4.5: 0b010,
        3.0: 0b100,
        2.5: 0b101,
        2.1: 0b110,
        1.75: 0b111
}

napchannels = {
        1: 0b0001,
        2: 0b0001,
        3: 0b0010,
        4: 0b0010,
        5: 0b0100,
        6: 0b0100,
        7: 0b1000,
        8: 0b1000
}

class ADC:

    def __init__(self, checkwrite=False):
        self.checkwrite = checkwrite
        pass

    def writereg(self, bank, addr, data):
        if self.checkwrite:
            readdata = self.readreg(bank, addr)
            assert readdata == data, "Incorrect data from bank %s register 0x%x: after writing 0x%x, read 0x%x.\n" % (bank, addr, data, readdata)

    def writerega(self, addr, data):
        self.writereg("A", addr, data)

    def writeregb(self, addr, data):
        self.writereg("B", addr, data)

    def readreg(self, bank, addr):
        return 0x0

    def readrega(self, addr):
        return self.readreg("A", addr)

    def readregb(self, reg, addr):
        return self.readreg("B", addr)

    def reset(self, bank=None):
        """Reset ADC bank(s)."""
        rstcmd  = 0x1 << 7
        if bank == "A" or bank is None:
            self.writerega(0x0, rstcmd) 
        if bank == "B" or bank is None:
            self.writeregb(0x0, rstcmd) 

    def testpattern(self, on, pattern=0x0, bank=None):
        """Set bank(s)'s test pattern and en/disable it."""
        pattern = pattern & 0xfff
        msb = 0x0
        if on:
            msb = 0x1 << 7
        msb |= ((pattern & 0xf) >> 8)
        lsb = pattern & 0xff
        if bank is None or bank == "A":
            self.writerega(0x4, lsb)
            self.writerega(0x3, msb)
        if bank is None or bank == "B":
            self.writeregb(0x4, lsb)
            self.writeregb(0x3, msb)

    def setoutputmode(self, lvdscurrent, lvdstermination, outenable, lanes, bits, bank=None):
        """Conifgure bank(s)'s output mode."""
        mode = 0x0
        assert lanes in [1, 2] and bits in [12, 14, 16]
        if lanes == 1:
            if bits == 12:
                mode |= 0b110
            elif bits == 14:
                mode |= 0b101
            else: # bits = 16
                mode |= 0b111
        else:   # lanes = 2
            if bits == 12:
                mode |= 0b010
            elif bits == 14:
                mode |= 001
            else: # bits = 16
                mode |= 0b111
        if not outenable:
            mode |= 0b1000
        if termon:
            mode |= (0x1 << 4)
        mode |= (lvdscurrents[lvdscurrent] << 5)
        if bank is None or bank == "A":
            self.writerega(0x2, mode)
        if bank is None or bank == "B":
            self.writerega(0x2, mode)

    def setformat(self, randomiser, twoscomp, stabliser=True, bank=None):
        """Configure bank(s)'s output format."""
        if bank is None or bank == "A":
            data = self.readrega(0x1)
            if twoscomp:
                data |= (0x1 << 5)
            else:
                data &= 0xff & ~(0x1 << 5)
            if randomser:
                data |= (0x1 << 6)
            else:
                data &= 0xff & ~(0x1 << 6)
            if not stabiliser:
                data |= (0x1 << 7)
            else:
                data &= 0xff & ~(0x1 << 7)
            self.writerega(0x1, data)
        if bank is None or bank == "B":
            data = self.readregb(0x1)
            if twoscomp:
                data |= (0x1 << 5)
            else:
                data &= 0xff & ~(0x1 << 5)
            if randomser:
                data |= (0x1 << 6)
            else:
                data &= 0xff & ~(0x1 << 6)
            if not stabiliser:
                data |= (0x1 << 7)
            else:
                data &= 0xff & ~(0x1 << 7)
            self.writeregb(0x1, data)

    def setsleep(self, sleep, bank=None):
        """Put ADC bank(s) to sleep."""
        if bank is None or bank == "A":
            data = self.readrega(0x1)
            if:
                data |= (0x1 << 4)
            else:
                data &= 0xff & ~(0x1 << 4)
            self.writerega(0x1, data)
        if bank is None or bank == "B":
            data = self.readregb(0x1)
            if sleep:
                data |= (0x1 << 4)
            else:
                data &= 0xff & ~(0x1 << 4)
            self.writeregb(0x1, data)

    def nap(self, channels):
        """Provide a list of channels to put down for a nap, all others will be not napping."""
        dataa = self.readrega(0x1)
        dataa &= 0xf0
        datab = self.readregb(0x1)
        datab &= 0xf0
        for chan in channels:
            assert chan < 9 and chan > 0
            if chan in [1, 4, 5, 8]:
                dataa |= napchannels[chan]
            else:
                datab |= napchannels[chan]
        self.writerega(0x1, dataa)
        self.writeregb(0x1, datab)
