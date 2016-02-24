import optparse
import time

import uhal

import biasboard
import envchamber
import storedata

usage = "python sipmcalibrationrun.py [options] <bias voltage [V]> <temperature [C]>"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-n", "--nevt", type=int, default=10000)
parser.add_option("-m", "--measbias", default=False, action="store_true")
parser.add_option("-t", "--trim", default=None, type=float)
parser.add_option("-c", "--chantrim", default=[], action="append")
(opts, args) = parser.parse_args()
assert len(args) == 2, "Must provide bias voltage and temperature."
bias = float(args[0])
temp = float(args[1])

assert temp > 0.0 and temp < 30.0
assert bias > 50.0 and bias < 75.0

biascontrol = biasboard.BiasControlBoard()
biascontrol.bias(bias)
chantrims = []
if opts.trim is not None:
    trim = opts.trim
    assert trim >= 0.0 and trim <= 5.0
    for i in range(8):
        baiscontrol.trim(i, trim)
        chantrims.append(trim)
else:
    trim = 0.0
    for i in range(8):
        biascontrol.trim(i, trim)
        chantrims.append(trim)
for chantrim in opts.chantrim:
    chan, trim = chantrim.split(",")
    chan = int(chan)
    trim = float(trim)
    assert chan >= 0 and chan < 8
    assert trim >= 0.0 and trim <= 5.0
    biascontrol.trim(chan, trim)
    chantrims[i] = trim

measbias = 0.0
if opts.measbias:
    measbias = float(raw_input("Measured bias voltage:\n"))


ec = envchamber.EnvChamber()
ec.setTempWait(temp)

target = uhal.getDevice("trenz", "ipbusudp-2.0://192.168.235.0:50001", "file://addr_table/top.xml")
triggerblock = storedata.TriggerBlock(target)
fn = "data/sipmcalib_%0.2fV_%0.2fC_%s.root" % (bias, temp, time.strftime("%d%b%Y_%H%M"))
outp = storedata.ROOTFile(fn)
outp.conditions(bias, measbias, temp, chantrims)
print "Using %d triggers." % opts.nevt
nevt = opts.nevt
for i in range(nevt):
    if i % (nevt / 10) == 0:
        print "%d of %d" % (i, nevt)
    outp.fill(triggerblock.trigger())
outp.close()
