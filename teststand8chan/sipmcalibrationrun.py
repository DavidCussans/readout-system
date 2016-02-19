import optparse

import uhal

import biasboard
import storedata

parser = optparse.OptionParser()
parser.add_option("-n", "--nevt", type=int, default=10000)
parser.add_option("-m", "--measbias", default=False, action="store_true")
(opts, args) = parser.parse_args()
assert len(args) == 2, "Must provide bias voltage and temperature."
bias = float(args[0])
temp = float(args[1])

assert temp > 0.0 and temp < 30.0
assert bias > 50.0 and bias < 75.0

biascontrol = biasboard.BiasControlBoard()
biascontrol.bias(bias)
measbias = 0.0
if opts.measbias:
    measbias = float(raw_input("Measured bias voltage:\n"))

target = uhal.getDevice("trenz", "ipbusudp-2.0://192.168.235.0:50001", "file://addr_table/top.xml")
triggerblock = storedata.TriggerBlock(target)
fn = "data/sipmcalib_%0.2fV_%0.2fC.root" % (bias, temp)
outp = storedata.ROOTFile(fn)
outp.conditions(bias, measbias, temp)
print "Using %d triggers." % opts.nevt
nevt = opts.nevt
for i in range(nevt):
    if i % (nevt / 10) == 0:
        print "%d of %d" % (i, nevt)
    outp.fill(triggerblock.trigger())
outp.close()
