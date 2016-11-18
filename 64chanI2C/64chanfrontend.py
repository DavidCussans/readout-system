class TempMCP9808:
    """Temperture chip on analog board."""

    regTemp = 0x5 #<<< 0b0001010 ie register for temp on the chip

    def __init__(self, i2ccore, addr=0b0011000):
    # this is the chip address right? ie the 7 bit 0011000 and a 0 for write in LSB
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f #<<< this verifies the address given is correct from internal error?
        # slave address is the chip address of the mcp9808 yes?

    def readreg(self, regaddr): #<- for generic reading to the reg provided
    # but which reg? can I set regaddr = e.g. 0x00
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 2)
# here I think that you're function is being told "use the i2cwriteread function
# on the slave address and then assign the variable n the value of the array at
# regaddr, then assign data to an array length of 2 bytes"?

        assert n == 1 #check n has bytes zero and one filled?
        assert len(data) == 2 # ensure that data has a length of two bytes ie byte 0 and 1
        val = data[0] << 8 #pushes the bits 8 places from byto 0 towards msb and leaves the
        # 8 bits towards lsb as 0's ?? does this not then fill byte 1?
        val |= data[1] # bitwise or takes the zeroed LSB bits and flips them if
        # either val or data[1] are 1
        # isnt this just duplicating byte 1 as byte 0?
        return val

    def temp(self):
        val = self.readreg(TempMCP9808.regTemp) ##<< this is pointing to the 0x5
        #  address and passing val the contents of 0x5 after performing the readreg function.
        return self.u16todeg(val) ##<< this is passing the contents of val to the
        # u16todeg function, which is then converting from bin to dec for 16 bits


# here can we not use dec(bin) or similar? ie the built in pyton functions,
# or is it better to perform the calculations on chip, ie bitwise manipulation
# via the code below
    def u16todeg(self, val): #val = 0011001110101010
        val &= 0x1fff # 0001111111111111 -> 0001001110101010 so again verifying the data?
        neg = val & 0x1000 > 0 #0001000000000000 ??
        val &= 0x0fff #0000111111111111
        if neg:
            return -float(0xfff - val) / 16.0
        return float(val) / 16.0



    def write(self, addr, data, stop=True):
        """Write data to the device with the given address."""
        # Start transfer with 7 bit address and write bit (0)
        nwritten = -1
        addr &= 0x7f
        addr = addr << 1
        startcmd = 0x1 << 7
        stopcmd = 0x1 << 6
        writecmd = 0x1 << 4
        self.data.write(addr)
        self.cmd_stat.write(I2CCore.startcmd | I2CCore.writecmd)
        self.target.dispatch()
        ack = self.delayorcheckack()
        if not ack:
            self.cmd_stat.write(I2CCore.stopcmd)
            self.target.dispatch()
            return nwritten
        nwritten += 1
        for val in data:
            val &= 0xff
            self.data.write(val)
            self.cmd_stat.write(I2CCore.writecmd)
            self.target.dispatch()
            ack = self.delayorcheckack()
            if not ack:
                self.cmd_stat.write(I2CCore.stopcmd)
                self.target.dispatch()
                return nwritten
            nwritten += 1
        if stop:
            self.cmd_stat.write(I2CCore.stopcmd)
            self.target.dispatch()
        return nwritten

    def read(self, addr, n):
        """Read n bytes of data from the device with the given address."""
        # Start transfer with 7 bit address and read bit (1)
        data = []
        addr &= 0x7f
        addr = addr << 1
        addr |= 0x1 # read bit
        self.data.write(addr)
        self.cmd_stat.write(I2CCore.startcmd | I2CCore.writecmd)
        self.target.dispatch()
        ack = self.delayorcheckack()
        if not ack:
            self.cmd_stat.write(I2CCore.stopcmd)
            self.target.dispatch()
            return data
        for i in range(n):
            self.cmd_stat.write(I2CCore.readcmd)
            self.target.dispatch()
            ack = self.delayorcheckack()
            val = self.data.read()
            self.target.dispatch()
            data.append(val & 0xff)
        self.cmd_stat.write(I2CCore.stopcmd)
        self.target.dispatch()
        return data

    def writeread(self, addr, data, n):
        """Write data to device, then read n bytes back from it."""
        nwritten = self.write(addr, data, stop=False)
        readdata = []
        if nwritten == len(data):
            readdata = self.read(addr, n)
        return nwritten, readdata




#-------------------------------------------------------------------------------
        #New from here down.
#-------------------------------------------------------------------------------


class TempLM82:
    """Temp chip on 64 chan board"""

    regTempLM82 =  0x00 #the registry for the temp read on the chip
    regSetCritLM82 =  0x5A #the registry for the critical temp setpoint on the chip
    regReadCritLM82 = 0x42 # the reg for reading whatthe crit is set to

    def __init__(self, i2ccore, addr=0b011000):#<-- 7 bit chip address. nb do I add MSB as 0?
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f #<< bitwise and validates chip address

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


    def readReg(self, regaddr, n): # <- generic write and read of register
        """read a given register"""
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 1) #< n = 1 byte?
        assert n == 1 #check n is 8 bits
        assert len(data) == 1 # ensure that data has a length of one byte?
        val = data[0]
        return val

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

    def binToDec:
        # feed temp the reg address byte data, NOT address...
        # val = regaddr # which should be passed from readreg I hope...
        neg = val & 0b10000000 > 0 # test if msb is 1
        if neg > 0:
            val = ~val + 1 #invert the bits, add one
            return -(int(val)+256) # convert from unsigned 8bit to signed dec
        else:
            return int(val)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

# in case we get a board over temp and wish to monitor it, or the ones next to it?
    def readTempLocal(self): # reads the current local temperature
    """read the current chip temp"""
        val = self.readreg(TempLM82.regTempLM82) #<- I'm assuming that this passes correctly
        return self.binToDec(val)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

    def readTCrit(self): # reads the set point for T_CRIT
        """ read T_CRIT setting from chip """
        val = self.readreg(TempLM82.regReadCritLM82)
        return self.binToDec(val)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

    def setTCrit(self, threshold):
        """set critical temp alarm threshold """
        #this needs to have the setpoint passed as an argument?
        # or as a while loop an test fro errors
        while True:
            try:
                threshold = int(raw_input('Specify Critical Temperatre set point:'))
                # If we fail we ask again user to enter binary number
            except ValueError: # ie not being passed an int.
                print "Something went wrong here..."
            else:
    #convert from dec to binary


                #format threshold as binary
        return threshold




        # get user input, convert to binary


        # set D3 and 5 to one to allow T_CRIT to be lowered

        #     regSetCritLM82 =  0x5A
        # set T_CRIT to user inputself.
        # read the set point



        pass
        # adr to SET T_CRIT is 0x5A for write, 0x42 for reading
        # Note! this needs the config reg to have D3 & D5 set to 1 before the T_CRIT
        # can be lowered below 127

        #  functions to write-------------------------------------------------------

        #   arg needs to be user input dec
        #   convert the dec to bin write address is 0x09 read address 0x03
        #   set the D5 and D3 pins to 1 (power up default to all 0's)
        #   pass this to the 0x5A address to set T_CRIT
        #   pass set value back to user and convert from bin to dec read 0x5A D0-D7
        #   retun t crit set point from 0x42 ie execute rtc command

        # TEST IF LT HAS TO BE SET ALSO OR IF T_CRIT IS ENOUGH AS IT LOOKS SO FROM THE CIRCUIT DIAGRAM
        # CONFIG REG details... address read/write  0x03 / 0x09
        # D5 AND D3 = 1 allows set temp below 127
        # D4 = 1 turns off the remote temp sensor attached to J14 (TSW-102-23-L-S)

        pass

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

class EUI_24AA025E48:
    """Unique ID chip with 48 bit node address """
# adr0, 1 and 2 all pulled to gnd ie set to zero
# has two blocks of 128 x 8 bit memory and can page write up to 16 bytes
# control bits are set to 1b010 for r/w operations next three bits are set by
# adr ie 000 final bit is r/w set ie read i 1 write is 0
# hence regADR is 1b0100001 to read
#
    #  functions to write-------------------------------------------------------
#     read id from eeprom ie the six bytes from 0xFA to 0xFF

  def __init__(self, data):
        assert len(data) == 6
        self.output = MCP4728ChanStatus(data[:3])
        self.EEPROM = MCP4728ChanStatus(data[3:])
        self.chan = self.EEPROM.chan
        #print self.output
#     read generic random bitstream to mem from 0x00 to 0x7f (although random read from anywhere?)
#     write gen bit stream from mem  again to 0x00 to 0x7f
#
# nb only half of the array can be written to as
# the other half is write protected writeable range is 0x00 to 0x7f
# 6 byte node address is in 0xFA to 0xFF the first three bytes are
# factory set to 0x0004A3, the remaining are the UID of the chip.
#



#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class VoltageLTC2990:
"""Voltage/Current sensor that can also do temperature"""
# adr0 and adr1 both pulled up to 1 on 3v3 rail

    #  functions to write-------------------------------------------------------
#     read 1.8v
#     read 3.3v
#     read current across pins 1 and 2 with 0.05 ohm resistor
#     V3 and V4 are 3v3 and 1v8
#     convert and pass to user

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class PowerINA219:
"""Current and power chip"""
#     There are two of these per board so each needs a different address
#     LHS VMON3V3 is pulled down to 00 RHS, VMON2V5 pulled to 10 for A0 and A1 respectively
#     (post the vmonxxx to user to indicate which is which with temp)
#     again these just go to a 0.05 ohm resistor (shunt) and measure current for J4 and J5
#

    #  functions to write-------------------------------------------------------
# read current from 3v3 and 2v5
# convert and pass to user
