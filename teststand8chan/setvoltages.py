import optparse
import sys
import time

import uhal

import envchamber
import frontend
import storedata

usage = "python setvoltages.py [options] <bias voltage [V]>"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-d", "--dachv", default=None, type=float)
parser.add_option("-t", "--trim", default=None, type=float)
parser.add_option("-c", "--chantrim", default=[], action="append")
parser.add_option("-r", "--readonly", default=False, action="store_true")
(opts, args) = parser.parse_args()
assert len(args) == 1, "Must provide global bias voltage."
bias = float(args[0])

assert bias >= 0.0 and bias < 75.0

fpga = frontend.SoLidFPGA(1)
fpga.reset()

#target = uhal.getDevice("trenz", "ipbusudp-2.0://192.168.235.0:50001", "file://addr_table/top.xml")
#i2cbus = frontend.I2CCore(target, 31.2536, 40e3, "io.analog_i2c")
#dacbias = frontend.DACMCP4725(i2cbus)

#trim0 = frontend.DACMCP4728(i2cbus, 0b1100011)
#trim0.readvoltages()
#time.sleep(1.0)
#trim1 = frontend.DACMCP4728(i2cbus, 0b1100101)
#trim1.readvoltages()
#time.sleep(1.0)

#biascontrol.bias(bias)

print "Previous DAC settings:"
fpga.readvoltages()
if opts.readonly:
    sys.exit()
print "Setting bias voltage: %g V" % bias
if opts.dachv is None:
    fpga.bias(bias)
else:
    fpga.gdac.setvoltage(opts.dachv)
chantrims = []
trims = {}
trim = opts.trim
if trim is None:
    trim = 0.0
assert trim >= 0.0 and trim <= 5.0
for i in range(8):
    trims[i] = trim
    chantrims.append(trim)
for chantrim in opts.chantrim:
    chan, trim = chantrim.split(",")
    chan = int(chan)
    trim = float(trim)
    assert chan >= 0 and chan < 8
    assert trim >= 0.0 and trim <= 5.0
    trims[chan] = trim
    chantrims[i] = trim
print "Setting trim voltages: %s" % str(trims)
fpga.trims(trims)
print "Reading back DAC settings:"
fpga.readvoltages()
