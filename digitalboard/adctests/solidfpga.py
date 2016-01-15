"""
solidfpa.py provides functionality to control the front end boards currently
being prototyped.

For the ADC:
    One or more LTM9007 ADCs can be controlled via the IPbus SPI block.
    Each chip is really two four channel ADCs, with each controlled with a 
    separate chip select line. Bank A is channels 1, 4, 5, 8. 
    Bank B is 2, 3, 6, 7.

    Control is via a simple SPI interface where 16 bits are transferred.
    b0 is read/!write
    b7:1 are the register address
    b15:b8 are the data sent to/from the ADC

    If the ADC.cehckwrite flag is True then all write commands will immediately
    be confirmed by a read command to the same address.
"""

import uhal

class SoLidFPGA:

    def __init__(self, nadc=4, verbose=False):
        cm = uhal.ConnectionManager("file://solidfpga.xml")
        self.device = cm.getDevice("SoLidFPGA")
        self.verbose = verbose
        self.config()
        self.offsets = TimingOffsets(self.device)
        self.trigger = Trigger(self.device)
        self.databuffer = OutputBuffer(self.device)
        self.spi = SPICore(self.device)
        self.i2c = I2CCore(self.device, "clk_i2c")
        self.adcs = []
        for i in range(1):
            self.adcs.append(ADCLTM9007(self.spi, 2 * i, 2 * i + 1))
        self.analogid = IDXXXChip(self.i2c)
        self.voltagetrimdac = DACXXXChip(self.i2c)

        self.firmwareversion = None

    def config(self):
        val = self.device.getNode("id.magic").read()
        self.device.dispatch()
        assert val == 0xdeadbeef, "Incorrect firmware?"
        self.firmwareversion = self.device.getNode("id.version").read()
        self.device.dispatch()
        if self.verbose:
            print "SoLid FPGA: Firmware version = %d." % self.firmwareversion

# IPbus blocks
class TimingOffsets:
    """Timing offsets for the ADC data deserialisation."""

    def __init__(self, device):
        self.device = device

class Trigger:
    """Trigger configuration block."""
    
    def __init__(self, device):
        self.device = device

class OutputBuffer:
    """Output data block."""
    
    def __init__(self, device):
        self.device = device
        
"""
I2C core XML:

<node description="I2C master controller" fwinfo="endpoint;width=3">
    <node id="ps_lo" address="0x0" description="Prescale low byte"/>
    <node id="ps_hi" address="0x1" description="Prescale low byte"/>
    <node id="ctrl" address="0x2" description="Control"/>
    <node id="data" address="0x3" description="Data"/>
    <node id="cmd_stat" address="0x4" description="Command / status"/>
</node>

"""
class I2CCore:
    """I2C communication block."""

    def __init__(self, device, wclk, i2clck, name="i2c"):
        self.device = device
        self.name = name
        self.prescale_low = self.device.getNode("%s.ps_lo" % name)
        self.prescale_high = self.device.getNode("%s.ps_hi" % name)
        self.ctrl = self.device.getNode("%s.ctrl" % name)
        self.data = self.device.getNode("%s.data" % name)
        self.cmd_stat = self.device.getNode("%s.cmd_stat" % name)
        self.config(wclk, i2clck)

    def state(self):
        status = {}
        status["ps_low"] = self.prescale_low.read()
        status["ps_hi"] = self.prescale_high.read()
        status["ctrl"] = self.ctrl.read()
        status["data"] = self.data.read()
        status["cmd_stat"] = self.cmd_stat.read()
        self.device.dispatch()
        status["prescale"] = status["ps_hi"] << 8
        status["prescale"] |= status["ps_low"]
        for reg in status:
            val = status[reg]
            bval = bin(int(val))
            print "reg %s = %d, 0x%x, %s" % (reg, val, val, bval)

    def clearint(self):
        self.ctrl.write(0x1)
        self.device.dispatch()

    def config(self, wishboneclock, i2cclock):
        self.ctrl.write(0x1 << 7)
        self.device.dispatch()
        prescale = int(wishboneclock / 5.0 / i2cclock) - 1
        self.prescale_low.write(prescale & 0xff)
        self.prescale_high.write((prescale & 0xff00) >> 8)
        self.ctrl.write(0x1 << 7)
        self.device.dispatch()

    def write(self, addr, data):
        """Write data to the device with the given address."""
        # Start transfer with 7 bit address and write bit (0)
        nwritten = -1
        addr &= 0x7f
        addr = addr << 1
        startcmd = 0x1 << 7
        stopcmd = 0x1 << 6
        writecmd = 0x1 << 4
        self.data.write(addr)
        self.cmd_stat.write(startcmd)
        self.cmd_stat.write(writecmd)
        self.device.dispatch()
        inprogress = True
        ack = False
        while inprogress:
            cmd_stat = self.cmd_stat.read()
            self.device.dispatch()
            print "cmd_stat = 0x%08x = %s" % (cmd_stat, bin(int(cmd_stat)))
            inprogress = cmd_stat & 0b10 > 0
            ack = cmd_stat & (0x1 << 7) == 0
        if ack:
            nwritten += 1
        else:
            return nwritten
        n = len(data)
        for i in range(n):
            self.data.write(b & 0xff)
            if i == n - 1:
                self.cmd_stat.write(stopcmd | writecmd)
            else:
                self.cmd_stat.write(writecmd)
            inprogress = True
            ack = False
            while inprogress:
                cmd_stat = self.cmd_stat.read()
                self.device.dispatch()
                inprogress = cmd_stat & 0b10 > 0
                ack = cmd_stat & (0x1 << 7) == 0
            if ack:
                nwritten += 1
            else:
                return nwritten
        return nwritten

    def read(self, addr, n):
        """Read n bytes of data from the device with the given address."""
        # Start transfer with 7 bit address and read bit (1)
        data = []
        startcmd = 0x1 << 7
        stopcmd = 0x1 << 6
        readcmd = 0x1 << 5
        writecmd = 0x1 << 4
        nackcmd = 0x1 << 3
        addr &= 0x7f
        addr = addr << 1
        addr |= 0x1 # read bit
        self.data.write(addr)
        self.cmd_stat.write(startcmd | writecmd)
        self.device.dispatch()
        inprogress = True
        ack = False
        while inprogress:
            cmd_stat = self.cmd_stat.read()
            self.device.dispatch()
            inprogress = cmd_stat & 0b10 > 0
            ack = cmd_stat & (0x1 << 7) == 0
        if not ack:
            return data
        for i in range(n):
            self.cmd_stat.write(readcmd)
            self.device.dispatch()
            inprogress = True
            while inprogress:
                cmd_stat = self.cmd_stat.read()
                self.device.dispatch()
                inprogress = cmd_stat & 0b10 > 0
            val = self.data.read()
            self.device.dispatch()
            data.append(val & 0xff)
        self.cmd_stat.write(nackcmd)
        self.device.dispatch()
        self.cmd_stat.write(stopcommand)
        self.device.dispatch()

    def writeread(self, addr, data, n):
        """Write data to device, then read n bytes back from it."""
        outdata = []
        nwritten = -1
        addr &= 0x7f
        addr = addr << 1
        startcmd = 0x1 << 7
        stopcmd = 0x1 << 6
        readcmd = 0x1 << 5
        writecmd = 0x1 << 4
        nackcmd = 0x1 << 3
        self.data.write(addr)
        self.cmd_stat.write(startcmd | writecmd)
        #self.cmd_stat.rmwbits(0x0, startcmd)
        #self.cmd_stat.rmwbits(0xffffff, writecmd)
        self.device.dispatch()
        inprogress = True
        ack = False
        while inprogress:
            cmd_stat = self.cmd_stat.read()
            self.device.dispatch()
            print "cmd_stat = %s" % bin(int(cmd_stat))
            inprogress = cmd_stat & 0b10 > 0
            ack = cmd_stat & (0x1 << 7) == 0
        if ack:
            print "Write acknowledged."
            nwritten += 1
        else:
            print "Write not acknowledged."
            return nwritten, outdata
        nout = len(data)
        for i in range(nout):
            self.data.write(b & 0xff)
            if i == nout - 1:
                self.cmd_stat.write(stopcmd | writecmd)
            else:
                self.cmd_stat.write(writecmd)
            inprogress = True
            ack = False
            while inprogress:
                cmd_stat = self.cmd_stat.read()
                self.device.dispatch()
                inprogress = cmd_stat & 0b10 > 0
                ack = cmd_stat & (0x1 << 7) == 0
            if ack:
                nwritten += 1
            else:
                return nwritten, outdata
        addr |= 0x1 # read bit
        addr |= 0x1 # read bit
        self.data.write(addr)
        self.cmd_stat.write(startcmd | writecmd)
        self.device.dispatch()
        inprogress = True
        ack = False
        while inprogress:
            cmd_stat = self.cmd_stat.read()
            self.device.dispatch()
            inprogress = cmd_stat & 0b10 > 0
            ack = cmd_stat & (0x1 << 7) == 0
        if not ack:
            return data
        for i in range(n):
            self.cmd_stat.write(readcmd)
            if i == n - 1:
                self.cmd_stat.write(nackcmd | stopcmd)
            self.device.dispatch()
            inprogress = True
            while inprogress:
                cmd_stat = self.cmd_stat.read()
                self.device.dispatch()
                inprogress = cmd_stat & 0b10 > 0
            val = self.data.read()
            self.device.dispatch()
            data.append(val & 0xff)
        self.cmd_stat.write(nackcmd | stopcmd)
        self.device.dispatch()
        return nwritten, outdata

"""
SPI core XML:

<node description="SPI master controller" fwinfo="endpoint;width=3">
    <node id="d0" address="0x0" description="Data reg 0"/>
    <node id="d1" address="0x1" description="Data reg 1"/>
    <node id="d2" address="0x2" description="Data reg 2"/>
    <node id="d3" address="0x3" description="Data reg 3"/>
    <node id="ctrl" address="0x4" description="Control reg"/>
    <node id="divider" address="0x5" description="Clock divider reg"/>
    <node id="ss" address="0x6" description="Slave select reg"/>
</node>
"""
class SPICore:

    def __init__(self, device, basename="spi"):
        self.device = device
        # Only a single data register is required since all transfers are
        # 16 bit long
        self.data= device.getNode("%s.d0" % basename)
        self.control = device.getNode("%s.ctrl" % basename)
        self.divider = device.getNode("%s.divider" % basename)
        self.slaveselect = device.getNode("%s.ss" % basename)
        self.config()

    def config(self):
        "Configure SPI interace for communicating with ADCs."
        value = 0x0
        value |= 0x1 << 13 # Automatic slave select
        value |= 0x0 << 12 # No interrupt
        value |= 0x0 << 11 # MSB first
        # ADC samples data on rising edge of SCK
        value |= 0x1 << 10 # change ouput on falling edge of SCK
        # ADC changes output shortly after falling edge of SCK
        value |= 0x0 << 9 # read input on rising edge
        value |= 0x0f # 16 bit transfers
        self.control.write(value)
        self.device.dispatch()
        # Need to configure the divider to run at X MHz

    def transmit(self, chip, value):
        assert chip >= 0 and chip < 8
        self.data.write(value & 0xff)
        self.slaveselect.write(0x1 << chip)
        self.control.rmwbits(0xffffffff, 0x1 << 8)
        self.device.dispatch()
        finished = False
        while not finished:
            ctrl = self.control.read()
            data = self.data.read()
            self.device.dispatch()
            # Check if transfer is complete by reading the GO_BSY bit of CTRL
            finished = ctrl & (0x1 << 8) > 0
        return data

# External chips

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

class ADCLTM9007:

    def __init__(self, spicore, csA, csB, checkwrite=False):
        self.checkwrite = checkwrite
        self.spicore = spicore
        self.csA = csA
        self.csB = csB

    def writereg(self, bank, addr, data):
        value = 0x0
        value |= 0x1 << 15
        value |= (addr & 0x7f) << 8
        value |= data & 0xff
        assert bank in ["A", "B"]
        if bank == "A":
            reply = self.spicore.transmit(self.csA, value)
        else:
            reply = self.spicore.transmit(self.csB, value)
        if self.checkwrite:
            readdata = self.readreg(bank, addr)
            msg = "Incorrect data from bank %s register 0x%x: " (bank, addr)
            msg += " after writing 0x%x, read 0x%x.\n" % (data, readdata)
            assert readdata == data, msg

    def writerega(self, addr, data):
        self.writereg("A", addr, data)

    def writeregb(self, addr, data):
        self.writereg("B", addr, data)

    def readreg(self, bank, addr):
        value = 0x0
        value |= 0x1 << 15
        value |= (addr & 0x7f) << 8
        assert bank in ["A", "B"]
        if bank == "A":
            reply = self.spicore.transmit(self.csA, value)
        else:
            reply = self.spicore.transmit(self.csB, value)
        return reply & 0xff

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
        pattern = pattern & 0x3fff
        msb = 0x0
        if on:
            msb = 0x1 << 7
        msb |= ((pattern & 0x3f00) >> 8)
        lsb = pattern & 0xff
        if bank is None or bank == "A":
            self.writerega(0x4, lsb)
            self.writerega(0x3, msb)
        if bank is None or bank == "B":
            self.writeregb(0x4, lsb)
            self.writeregb(0x3, msb)

    def setoutputmode(self, lvdscurrent, lvdstermination, outenable, lanes, bits, bank=None):
        """Configure bank(s)'s output mode."""
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
        if lvdstermination:
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
            if sleep:
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

class DACXXXChip:

    def __init__(self, i2ccore):
        self.i2ccore = i2ccore

class IDXXXChip:

    def __init__(self, i2ccore):
        self.i2ccore = i2ccore
