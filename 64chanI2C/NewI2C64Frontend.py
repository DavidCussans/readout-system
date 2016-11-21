
/*##############################################################################

██      ███    ███  █████  ██████      ████████ ███████ ███    ███ ██████
██      ████  ████ ██   ██      ██        ██    ██      ████  ████ ██   ██
██      ██ ████ ██  █████   █████         ██    █████   ██ ████ ██ ██████
██      ██  ██  ██ ██   ██ ██             ██    ██      ██  ██  ██ ██
███████ ██      ██  █████  ███████        ██    ███████ ██      ██ ██

*/##############################################################################



class TempLM82:
    """Temp chip on 64 chan board"""

    regTempLM82 =  0x00 #the registry for the temp read on the chip
    regSetCritLM82 =  0x5A #the registry for the critical temp setpoint on the chip
    regReadCritLM82 = 0x42 # the reg for reading whatthe crit is set to

    def __init__(self, i2ccore, addr=0b011000):#<-- 7 bit chip address. nb do I add MSB as 0?
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f #<< bitwise and validates chip address

# This needs to be globally callable
    def readReg(self, regaddr, n): # <- generic write and read of register
        """read a given register"""
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 1) #< n = 1 byte?
        assert n == 1 #check n is 8 bits
        assert len(data) == 1 # ensure that data has a length of one byte?
        val = data[0]
        return val
# This needs to be globally callable
    def u8binToDec(self, val):
        # feed val the reg address byte data, NOT address...
        # val = regaddr # which should be passed from readreg I hope...
        neg = val & 0b10000000 > 0 # test if msb is 1
        if neg > 0:
            val = ~val + 1 #invert the bits, add one
            return -(int(val)+256) # convert from unsigned 8bit to signed dec
        else:
            return int(val)

# in case we get a board over temp and wish to monitor it, or the ones next to it?
    def readTempLocal(self): # reads the current local temperature
    """read the current chip temp"""
        val = self.readreg(TempLM82.regTempLM82) #<- I'm assuming that this passes correctly
        return self.u8binToDec(val)


    def readTCrit(self): # reads the set point for T_CRIT
        """ read T_CRIT setting from chip """
        val = self.readreg(TempLM82.regReadCritLM82)
        return self.u8binToDec(val)

#-------------------------------------------------------------------------------

/*
██     ██    ██    ██████
██     ██    ██    ██   ██
██  █  ██    ██    ██████
██ ███ ██    ██    ██
 ███ ███  ██ ██ ██ ██
*/




    def setTCrit(self, threshold):
        """set critical temp alarm threshold """
        #this needs to have the setpoint passed as an argument?
        # or as a while loop an test for errors
        while True:
            try:
                threshold = int(raw_input('Specify Critical Temperatre set point:'))
                # If we fail we ask again user to enter binary number
            except ValueError: # ie not being passed an int.
    #        number out of range needs adding too?
                print "Something went wrong here..."
            else:

    #convert from dec to binary
    # if positive can i just pass this straight across?
    #
    # test if neg
    # if neg do:
    #     bit inversion add one
    #     pass this up
    # else:
    #     pass the number as is.


            #format threshold as binary
        # return threshold
        # get user input, convert to binary

        # set D3 and 5 to one to allow T_CRIT to be lowered
# this has to be a writeread function to write to d5 and 3 to set them both true and then to write t crit
# then run the read T_CRIT function.
        #     regSetCritLM82 =  0x5A
        # set T_CRIT to user inputself.
        # read the set point
        # pass
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


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

/*##############################################################################

███████ ██    ██ ██ ██████      ██   ██  █████      ██████  ██ ████████
██      ██    ██ ██ ██   ██     ██   ██ ██   ██     ██   ██ ██    ██
█████   ██    ██ ██ ██   ██     ███████  █████      ██████  ██    ██
██      ██    ██ ██ ██   ██          ██ ██   ██     ██   ██ ██    ██
███████  ██████  ██ ██████           ██  █████      ██████  ██    ██

*/##############################################################################




class EUI_24AA025E48:
    """Unique ID chip with 48 bit node address """
# adr0, 1 and 2 all pulled to gnd ie set to zero
    regMemory = 0x00:0x80 # again is it enough to specify just the start point?
    # like the line below?
    #regMemory = 0x00
    # also from 0xfa onwards the area should be write protected at chip level.

    def __init__(self, i2ccore, data, addr=0b1010000):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f

    #    regaddr is six bytes from 0xFA to 0xFF
    def read48bitUID(self, n, data): # reads the set point for T_CRIT
        """ read 48 bit UID from chip """
        # as this is write protected must send only read? not writeread? check i2c functions.
        n, data = self.i2ccore.read(self.slaveaddr, [0xfa:0xff], 6) # can i fix the reg address this way?
        # then read the next six bytes, ie from 0xfa to 0xff? or is it enough to just have [oxfa]?
        #n, data = self.i2ccore.read(self.slaveaddr, [0xfa], 6) #like this?
        assert n == 6 # six bytes
        assert len(data) == 6 # set data to six bytes
        val = data[:6] # this is from 0:6 bytes yes?
        return val # do i need to worry about big/little endian?
        # we can debug as we know 0:3 are pre-set by factory to 0x00 0x04 and 0xa3.


#     read generic random bitstream to mem from 0x00 to 0x7f (although random read from anywhere?)


            /*
            ██     ██    ██    ██████
            ██     ██    ██    ██   ██
            ██  █  ██    ██    ██████
            ██ ███ ██    ██    ██
             ███ ███  ██ ██ ██ ██
            */



################################################################################
############### THIS IS EXTRA FOR READING/WRITING TO THE ONCHIP MEMORY #########
################################################################################

    def writeread(self, addr, data, n):
        """Write data to device, then read n bytes back from it."""
        nwritten = self.write(addr, data, stop=False)
        readdata = []
        if nwritten == len(data):
            readdata = self.read(addr, n)
        return nwritten, readdata

    def readReg(self, regaddr, n): # <- generic write and read of register
        """read a given memory register"""
        #nota bene we have up to six bytes to be able to read.
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 1) #< n = 1 byte?
        assert n == 1 #check n is 8 bits
        assert len(data) == 1 # ensure that data has a length of one byte?
        val = data[0]
        return val

    def readMemory(self): # only reads from the first byte
    """read from memory """
        val = self.readreg(EUI_24AA025E48.regMemory)
        return val

    def writeMemory(self, addr, data):
    """Writes to memory"""
        val = self.writereg(EUI_24AA025E48.regMemory)
        return val

    def memoryTest(self, n, data, addr):
        """write then read a given block of data"""

     def writeread(self, addr, data, n):
        """Write data to device, then read n bytes back from it."""
        nwritten = self.write(addr, data, stop=False) # calls the write function
        readdata = []
        if nwritten == len(data):
            readdata = self.read(addr, n) #and the read function.
        return nwritten, readdata

#         self.i2ccore.write(self.slaveaddr, data)


#     write gen bit stream from mem  again to 0x00 to 0x7f
#
# nb only half of the array can be written to as
# the other half is write protected writeable range is 0x00 to 0x7f
# 6 byte node address is in 0xFA to 0xFF the first three bytes are
# factory set to 0x0004A3, the remaining are the UID of the chip.
#


/*###############################################################################

██   ████████  ██████ ██████   █████   █████   ██████      ██    ██    ██  ██████
██      ██    ██           ██ ██   ██ ██   ██ ██  ████     ██    ██   ██  ██
██      ██    ██       █████   ██████  ██████ ██ ██ ██     ██    ██  ██   ██
██      ██    ██      ██           ██      ██ ████  ██      ██  ██  ██    ██
███████ ██     ██████ ███████  █████   █████   ██████        ████  ██      ██████

*/###############################################################################


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
class VoltageLTC2990:
"""Voltage/Current sensor that can also do temperature"""

## Nota Bene: If running in continuous monitoring mode ie repeated acquisition
# will this keep the channel open all the time? ie lock the chip to
# constantly talk to the master?
# If so we can set this to get only one acquisition.

# Current conversion for 2's comp from D13:0 changes
# if sign bit (bit 6) of MSByte is 1 we have negative and 0 we have positive.
# current = D[13:0]* 19.42 uV/R_sense for sign = 0
# current = (D[13:0]+1)*-19.42 uV/R_sense for sign = 1

# for V3 and V4 pins LSB is 305.18uV
# for diff between V1 and V2 LSB = 19.42uV

    reg1v8LTC2990 =  0x0c and 0x0d #the registry for the 1.8V rail
    reg3v3LTC2990 =  0x0a and 0x0b #the registry for the 3.3V rail
    regCurrentLTC2990 = 0x06 and 0x07 to 0x08 and 0x09 # the reg for the current across V3 and V4 pins
    regControlLTC2990 = 0x01 # can use this to set the mode that the chip runs in.

    def __init__(self, i2ccore, addr=0b1001111):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f

     def readreg(self, regaddr):
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 2)
        assert n == 1
        assert len(data) == 2
        val = data[0] << 8
        val |= data[1]
        return val

    def u16binToDec(self, val): #this is for generic conversion.
        neg = val & 0x8000 > 0 # test if msb is 1 OR 0x8000 bin 0b1000000000000000
        if neg > 0:
            val = ~val + 1 #invert the bits, add one
            print -(float(val)+0xffff) - 1 # convert from unsigned 8bit to signed dec
        else:
            print float(val)


            /*
            ██     ██    ██    ██████
            ██     ██    ██    ██   ██
            ██  █  ██    ██    ██████
            ██ ███ ██    ██    ██
             ███ ███  ██ ██ ██ ██
            */



################################################################################
################################################################################
#### NICKS EXAMPLES
####
################################################################################
################################################################################

    def writeread(self, addr, data, n):
        """Write data to device, then read n bytes back from it."""
        nwritten = self.write(addr, data, stop=False)
        readdata = []
        if nwritten == len(data):
            readdata = self.read(addr, n)
        return nwritten, readdata

    def readReg(self, regaddr, n): # <- generic write and read of register
        """read a given memory register"""
        #nota bene we have up to six bytes to be able to read.
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 1) #< n = 1 byte?
        assert n == 1 #check n is 8 bits
        assert len(data) == 1 # ensure that data has a length of one byte?
        val = data[0]
        return val

    def readMemory(self): # only reads from the first byte
    """read from memory """
        val = self.readreg(EUI_24AA025E48.regMemory)
        return val

    def writeMemory(self, addr, data):
    """Writes to memory"""
        val = self.writereg(EUI_24AA025E48.regMemory)
        return val

    def memoryTest(self, n, data, addr):
        """write then read a given block of data"""
################################################################################
##############################      END       ##################################
################################################################################

    def setControlMode(self, regaddr):
        # this needs to be passed a string to set it to the correct operational mode.
        # D5 to D7 set to default. 0,0, reserved.
        # D4 and D3 set to 1, 1, to set all measurements as per D2- D0
        # D2 - D0 set to 0,1,0 respectively. this will collect V1-V2 and V3 and V4
        # hence we need to pass 0b00?11010  bit 5 is



    #  functions to write-------------------------------------------------------
#     read 1.8v
#     read 3.3v
#     read current across pins 1 and 2 with 0.05 ohm resistor
#     V3 and V4 are 3v3 and 1v8
#     convert and pass to user

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

/*##############################################################################

██ ███    ██  █████  ██████   ██  █████       ██████     ██ ██████
██ ████   ██ ██   ██      ██ ███ ██   ██     ██         ██  ██   ██
██ ██ ██  ██ ███████  █████   ██  ██████     ██        ██   ██████
██ ██  ██ ██ ██   ██ ██       ██      ██     ██       ██    ██
██ ██   ████ ██   ██ ███████  ██  █████       ██████ ██     ██

*/##############################################################################

/*
███████ ██ ███    ██ ██████
██      ██ ████   ██      ██
█████   ██ ██ ██  ██   ▄███
██      ██ ██  ██ ██   ▀▀
██      ██ ██   ████   ██
*/




class Current2v5INA219:
"""2.5V Current and power chip """

##### POWER ON RESETS chip so current and power reg's will read zero, BUT...
# shunt voltage will still read the shunt voltage and Bus voltage will still read.

    regCurrent2v5INA219 =  0x01 #the registry for 2.5V shunt current
    regBusVoltage2v5INA219 = 0x02 # the reg for the 2.5V bus voltage

    def __init__(self, i2ccore, addr=0b1000001):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f


    # assuming the resistor is known and calibrated we can obtain power from
    # V^2/R and current from V/R with R in Ohms... ie 0.05 from diagram?

    ## Bus voltage is NOT right aligned and needs >> 3 to shift BD0 into LSB.
    # id est this is 13 bit resolution... ie a byte and a nibble AND a bit...
    ## ALSO the bus and shunt voltages are temperature dependant!
    # AND... this assumes the shunt is set to PGA /8 which will give the greatest range of values.
    # if we are setting PGA NOT to /8 we will have to amend the sign bits...

     def readreg(self, regaddr):
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 2)
        assert n == 1
        assert len(data) == 2
        val = data[0] << 8
        val |= data[1]
        return val

# FTAO Nick: I couldn't get your temp u16bin to dec function to work correctly
# when testing...
# So I had to write my own. I've been testing on the codeacademy notebook page to execute the scripts.
# http://labs.codecademy.com/#:workspace I trust this is a suitable environment?

    def u16binToDec(self, val): #this is for generic conversion.
        neg = val & 0x8000 > 0 # test if msb is 1 OR 0x8000 bin 0b1000000000000000
        if neg > 0:
            val = ~val + 1 #invert the bits, add one
            print -(float(val)+0xffff) - 1 # convert from unsigned 16bit to signed dec
        else:
            print float(val)

    def read2v5Current(self):
        """read the shunt current from the 2v5 chip"""
        val = self.readreg(Current2v5INA219.regCurrent2v5INA219)
        #return self.binToDec(val) # if the below won't work, modify this.
        return self.u16binToDec(float(val)/100) # will this work for the return?
        # and then use the voltage to calc power and/or current.
        # This will retrun mV as lsb is 10uV

    def read2v5BusVoltage(self):
        """read the bus voltage for shunt calculation"""
        val = self.readreg(Current2v5INA219.regBusVoltage2v5INA219)
        val = val >> 3 # shift the registry three bits right to align lsb.
        # nota bene this will NOT give negative voltages...
        return self.u16binToDec(float(val)*4) # lsb is 4mV


class Current3v3INA219:
"""3.3V Current and power chip """

    regCurrent3v3INA219 =  0x01 #the registry for 3.3V shunt current
    regBusVoltage3v3INA219 = 0x02 #reg for the bus voltage.

    def __init__(self, i2ccore, addr=0b1000000):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f

    def readreg(self, regaddr):
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 2)
        assert n == 1
        assert len(data) == 2
        val = data[0] << 8 # D0-D7 contain MSB then left shift 8 bits
        val |= data[1] # fills D0 - D7 with the LSB
        return val

    def u16binToDec(self, val):
        neg = val & 0x8000 > 0 # test if msb is 1 OR 0x8000 bin 0b1000000000000000
        if neg > 0:
            val = ~val + 1 #invert the bits, add one
            print -(float(val)+0xffff) - 1 # convert from unsigned 16bit to signed dec
        else:
            print float(val)

    def read3v3Current(self):
        """read the shunt current from the 3v3 chip"""
        val = self.readreg(Current3v3INA219.regCurrent3v3INA219)
        return self.u16binToDec(float(val)/100) # returns the shunt voltage in mV.
        #whci hshoul be the same units as the bus voltage.
        # which we can then convert to power or current

    def read2v5BusVoltage(self):
        """read the bus voltage for shunt calculation"""
        val = self.readreg(Current3v3INA219.regBusVoltage3v3INA219)
        val = val >> 3 # shift the registry three bits right to align lsb.
        # nota bene this will NOT give negative voltages...
        return self.u16binToDec(float(val)*4) # lsb is 4mV
