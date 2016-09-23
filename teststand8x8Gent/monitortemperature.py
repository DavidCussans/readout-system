import optparse
import sys
import time

import uhal

import envchamber
import frontend
import storedata

usage = "python setvoltages.py [options] <bias voltage [V]>"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-p", "--period", type=float, default=10.0)
(opts, args) = parser.parse_args()

assert bias >= 0.0 and bias < 75.0

fpgas = {}
for arg in args:
    fpga = frontend.SoLidFPGA(arg, 1)
    fpga.reset()
    fpgas[arg] = fpga
while True:
    for arg in args:
        print "%s: %g C" % (arg, fpgas[arg].temp.temp())
    time.sleep(opts.period)
