class TempMCP9808:
    """Temperture chip on analog board."""

    regTemp = 0x5

    def __init__(self, i2ccore, addr=0b0011000):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f

    def readreg(self, regaddr):
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 2)
        assert n == 1
        assert len(data) == 2
        val = data[0] << 8
        val |= data[1]
        return val

    def temp(self):
        val = self.readreg(TempMCP9808.regTemp)
        return self.u16todeg(val)

    def u16todeg(self, val):
        val &= 0x1fff
        neg = val & 0x1000 > 0
        val &= 0x0fff
        if neg:
            return -float(0xfff - val) / 16.0
        return float(val) / 16.0

        #New from here down.
#-------------------------------------------------------------------------------
class LM82:
    """Temp chip on 64 chan board"""
    regLM82 = 0b011000 # 7 bit binary address with ADD0 and 1 set to 0
    #temp data is set in binary with LSB = 1 deg C

def rtc(self, regaddr):
    """ read T_CRIT from board """
    pass
    # address of T_CRIT to READ 0x42  set to 127 (0b1111111) default
    # convert local_temp from bin to dec
    # return local_temp

def set_tcrit(self, thresh):
    """set critical temp alarm threshold """
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
#     read generic random bitstream to mem from 0x00 to 0x7f (although random read from anywhere?)
#     write gen bit stream from mem  again to 0x00 to 0x7f
#
# nb only half of the array can be written to as
# the other half is write protected writeable range is 0x00 to 0x7f
# 6 byte node address is in 0xFA to 0xFF the first three bytes are
# factory set to 0x0004A3, the remaining are the UID of the chip.
#



#-------------------------------------------------------------------------------
class LTC2990:
"""Voltage/Current sensor that can also do temperature"""
# adr0 and adr1 both pulled up to 1 on 3v3 rail

    #  functions to write-------------------------------------------------------
#     read 1.8v
#     read 3.3v
#     read current across pins 1 and 2 with 0.05 ohm resistor
#     V3 and V4 are 3v3 and 1v8
#     convert and pass to user

#-------------------------------------------------------------------------------
class INA219:
"""Current and power chip"""
#     There are two of these per board so each needs a different address
#     LHS VMON3V3 is pulled down to 00 RHS, VMON2V5 pulled to 10 for A0 and A1 respectively
#     (post the vmonxxx to user to indicate which is which with temp)
#     again these just go to a 0.05 ohm resistor (shunt) and measure current for J4 and J5
#

    #  functions to write-------------------------------------------------------
# read current from 3v3 and 2v5
# convert and pass to user
