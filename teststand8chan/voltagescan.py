import optparse
import os

parser = optparse.OptionParser(usage="python voltagescan.py [options] <temperature>")
parser.add_option("--vmin", default=62.0, type=float)
parser.add_option("--vmax", default=68.0, type=float)
parser.add_option("--deltav", default=0.2, type=float)
(opts, args) = parser.parse_args()

assert len(args) == 1
temp = float(args[0])

v = opts.vmin
while v < opts.vmax:
    os.system("python sipmcalibrationrun.py %g %g -n 1000" % (v, temp))
    v += opts.deltav
