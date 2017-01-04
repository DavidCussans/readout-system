class TempLM82:
    """Temp chip on 64 chan board"""

    regTemp =  0x00 #the registry for the temp read on the chip
    regSetCrit =  0x5A #the registry for writing to critical setpoint on chip
    regReadCrit = 0x42 # the reg for reading what the crit is set to
    regWriteConfig = 0x09 # reg for setting config to set T_CRIT.

    def __init__(self, i2ccore, addr=0b011000):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f

# unless this is the last address in the register it needs a writeread.
# this chip only sends one byte of data.
    def readReg(self, regaddr, n): # <- generic write and read of register
        """read a given register"""
        n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 1)
        assert n == 1
        assert len(data) == 1
        val = data[0]
        return val

    def u8binToDec(self, val):
        neg = val & 0b10000000 > 0 # test if msb is 1
        if neg:
            val = ~val + 1 #invert the bits, add one
            return -(int(val)+256) # convert from unsigned 8bit to signed dec
        else:
            return int(val)

    def readTempLocal(self): # reads the current local temperature
    """read the current chip temp"""
        val = self.readreg(TempLM82.regTemp)
        return self.u8binToDec(val)


    def readTCrit(self): # reads the set point for T_CRIT
        """ read T_CRIT setting from chip """
        val = self.readreg(TempLM82.regReadCrit)
        return self.u8binToDec(val)


    def setTCrit(self, threshold):
        """set critical temp alarm threshold """
        # power on defaults to 127 C
        # set config reg to accept change
        data = 0b00101000 # sets config D5 and D3 to one. Allows crit set <127 C
        self.i2ccore.write(self.regWriteConfig, data)

        #setTCrit to XX deg C
        #data = 0x0f # 15
        #data = 0x14 # 20
        #data = 0x19 # 25
        #data = 0x1e # 30
        #data = 0x23 # 35
        #data = 0x28 # 40
        data = 0x3c # 60 etc.
        self.i2ccore.write(self.regSetCrit, data)

        # w/r crit to check right temp set
        # Do we want this to print to screen for user or just return?
        #print "Critical Temp set to %g C" % (self.readTCrit(self))
        return self.readTCrit(self)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


class EUI_24AA025E48:
    """Unique ID chip with 48 bit node address """
    regUID = 0xfa
    #regMemory = 0x00 in case we need to write to the mem?
    # also from 0xfa onwards the area is write protected at chip level.

    def __init__(self, i2ccore, data, addr=0b1010000):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f

    #    regaddr is six bytes from 0xFA to 0xFF
    def read48bitUID(self, n, data):
        """ read 48 bit UID from chip """
        # as this is write protected must send only read? not writeread?
        # datasheet is less than helpful... assume w/r.
        n, data = self.i2ccore.writeread(self.slaveaddr, regUID, 6)
        assert n == 1 # The address byte - not UID bytes?
        assert len(data) == 6 # set data to six bytes
        val = data[:6] # this is from 0:6 bytes from 0xfa.
        return val
        # can debug as we know 0:3 are pre-set by factory to 0x00 0x04 and 0xa3.
        # should return 00-04-a3-rnd-rnd-rnd format.


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

class VoltageLTC2990:
"""Voltage/Current sensor that could also do temperature"""

# Current conversion for 2's comp from D13:0 changes
# sign bit is (bit 6) of MSByte ie D14
# current = D[13:0]* 19.42 uV/R_sense for sign = 0
# current = (D[13:0]+1)*-19.42 uV/R_sense for sign = 1

# the chip can perform a currnet calculation but David C has mentioned it's best
# to do this off chip. hence reading voltage drop across pins only.

# for V3 and V4 pins LSB is 305.18uV
# for diff between V1 and V2 LSB = 19.42uV

    # reg1v8 =  0x0c #and 0x0d #the registry for the 1.8V rail
    # reg3v3 =  0x0a #and 0x0b #the registry for the 3.3V rail
    # regCurrent = 0x06 #and 0x07 to 0x08 and 0x09 # the reg for the current
    # # across V3 and V4 pins
    regControl = 0x01 # must use this to set the mode that the chip runs in.

    def __init__(self, i2ccore, addr=0b1001111):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f

    def readConfig(self, n, data):
        """Read the config for the chip"""
        n, data = self.i2ccore.writeread(self.slaveaddr, regControl, 1)
        assert n == 1
        assert len(data) == 1
        val = data[0]
        return val

    def setControlMode(self, regaddr):
        """Set the config of the chip"""
        data = 0b01011111 # single read mode for V1,2,3&4
        #data = 0b00011111 # continuous read mode
        self.i2ccore.write(self.regControl, data)
        return self.readConfig(self)

    def u15binToDec(self, val): #this is for generic conversion.
        val &= 0x7fff # should set D15 to zero
        neg = val & 0x4000 > 0 # test if msb(D14) is one
        if neg:
        	val = ~val - 0x7fff #invert the bits, remove the introduced D15
        	print -((val)+0xffff) # convert to dec
        else:
        	print (val)

# From the data sheet: "The register pointer is automatically incremented after
# each byte is read" which I have taken to mean that it will read byta A from
# 0x06 then read byte B from 0x07 etc.
# If so: can i read out the all bytes for the four pins in one writeread, as the
# bytes are at 0x06...0x09...0x0d and sequential. Then can I split them into the two
# pins and utilise for calculation  of current and have voltage of busses from the
# other two?

# eg:
    #  def readAll(self, regaddr):
    #     n, data = self.i2ccore.writeread(self.slaveaddr, 0x06, 8)
    #     assert n == 1
    #     assert len(data) == 4
    #     val = data[0] << 8
    #     val |= data[1]
    #     val = data[1] << 8
    #     val |= data[2]
    #     val = data[2] << 8
    #     val |= data[3]
    #     val = data[3] << 8
    #     val |= data[4]
    #     val = data[4] << 8
    #     val |= data[5]
    #     val = data[5] << 8
    #     val |= data[6]
    #     val = data[6] << 8
    #     val |= data[7]
    #     return val

    #four register bytes for the current across two pins. two bytes per pin
    # then two bytes per voltage.
    #perform all byte manipulation local to user?
    #these are all 14 bit values... with 2msb needing to be cut.
###############################################################################

    def readCurrent(self, regaddr):
        n, dataA = self.i2ccore.writeread(self.slaveaddr, 0x06, 2), dataB = self.i2ccore.writeread(self.slaveaddr, 0x08, 2)
        # Get V1 bytes
        assert n == 1
        assert len(dataA) == 2
        valA = dataA[0] << 8
        valA |= dataA[1]
        return valA
        # Get V2 bytes
        assert len(dataB) == 2
        valB = dataB[0] << 8
        valB |= dataB[1]
        # Will this perform a valid subtraction given the way python handles numbers,
        # or will I need to convert to dec first?
        valCurrent = valA - valB # check if current is V1-V2 or vice versa.
        return self.u15binToDec(valCurrent)


    def read1V8(self, regaddr):
        n, data = self.i2ccore.writeread(self.slaveaddr, 0x0a, 2)
        assert n == 1
        assert len(data) == 2
        val = data[0] << 8
        val |= data[1]
        return self.u15binToDec(val)

# OR Can I just pass the 2 bytes of data to the conversion? LIke this?

    def read3V3(self, regaddr):
        n, data = self.i2ccore.writeread(self.slaveaddr, 0x0c, 2)
        return self.u15binToDec(data)

# If not resort to this.
    # def read3V3(self, regaddr):
    #     n, data = self.i2ccore.writeread(self.slaveaddr, 0x0c, 2)
    #     assert n == 1
    #     assert len(data) == 2
    #     val = data[0] << 8
    #     val |= data[1]
    #     return self.u15binToDec(val)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------


class PowerCurrentINA219(object): # Parent class for the chip classes
    """Power and Current chip for 3v3 and 2v5 rails"""
    ##common parts

    def __init__(self, i2ccore, addr):
        self.i2ccore = i2ccore
        self.slaveaddr = addr & 0x7f
        # regaddr's
        self.regCurrent =  0x01
        self.regBusVoltage = 0x02
        # pass these common reg's to the 2v5 and 3v3 rail chips

    def readreg(self, regaddr): # Both reg require writeread to read.
       n, data = self.i2ccore.writeread(self.slaveaddr, [regaddr], 2)
       assert n == 1
       assert len(data) == 2
       val = data[0] << 8
       val |= data[1]
       return val

   def u16binToDec(self, val): #this is for generic conversion.
       neg = val & 0x8000 > 0 # test if msb is 1 OR 0x8000 bin 0b1000000000000000
       if neg: # this tests if neg is True
           val = ~val + 1 #invert the bits, add one
           return -(float(val)+0xffff) - 1 # convert from u16bit to signed dec
       else:
           return float(val)


    def readCurrent(self, addr, val):
         """read the shunt current """
         val = self.readreg(self.regCurrent)
         val = self.u16binToDec(val)
         return val /100


    def readBus(self, addr, val):
         """read the bus voltage for shunt calculation"""
         val = self.readreg(self.regBusVoltage)
         val = val >> 3 # shift the registry three bits right to align lsb.
         val = self.u16binToDec(val)
         return val * 4
              # nota bene this will NOT give negative voltage
              # as a neg bus voltage means we've wired the chip wrong

chip2v5 = PowerCurrentINA219(i2ccore, 0b1000001)
chip3v3 = PowerCurrentINA219(i2ccore, 0b1000000)
