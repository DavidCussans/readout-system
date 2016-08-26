import optparse
import time

import uhal

import envchamber
import frontend
import storedata

usage = "python sipmcalibrationrun.py [options] <bias voltage [V]> <temperature [C]>"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-n", "--nevt", type=int, default=10000)
parser.add_option("-m", "--measbias", default=False, action="store_true")
parser.add_option("-t", "--trim", default=None, type=float)
parser.add_option("-c", "--chantrim", default=[], action="append")
parser.add_option("-v", "--fwversion")
parser.add_option("-u", "--notemp", default=False, action="store_true")
(opts, args) = parser.parse_args()
assert len(args) == 2, "Must provide bias voltage and temperature."
bias = float(args[0])
temp = float(args[1])

assert temp > 0.0 and temp < 30.0
assert bias > 50.0 and bias < 75.0

# If the flag notemp is set then don't try to control the temperature.
if opts.notemp is False:
    ec = envchamber.EnvChamber()
    ec.setTempWait(temp)

fpga = frontend.SoLidFPGA(1, minversion=opts.fwversion)
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

fpga.readvoltages()
fpga.bias(bias)
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
fpga.trims(trims)
fpga.readvoltages()

measbias = 0.0
if opts.measbias:
    measbias = float(raw_input("Measured bias voltage:\n"))


#triggerblock = storedata.TriggerBlock(target)
fn = "data/sipmcalib_%0.2fV_%0.2fC_%s.root" % (bias, temp, time.strftime("%d%b%Y_%H%M"))
if opts.trim is not None:
    fn = fn.replace("V_", "V_trim%gV_" % opts.trim)
outp = storedata.ROOTFile(fn)
outp.conditions(bias, measbias, temp, chantrims)
print "Using %d triggers." % opts.nevt
nevt = opts.nevt
for i in range(nevt):
    if i % (nevt / 10) == 0:
        print "%d of %d" % (i, nevt)
    outp.fill(fpga.trigger.trigger())
outp.close()
