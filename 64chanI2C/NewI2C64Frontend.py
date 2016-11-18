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
        # feed val the reg address byte data, NOT address...
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
