import optparse
import os

parser = optparse.OptionParser(usage="python voltagescan.py [options] <temperature>")
parser.add_option("--vmin", default=62.5, type=float)
parser.add_option("--vmax", default=66.0, type=float)
parser.add_option("--deltav", default=0.1, type=float)
parser.add_option("--trim", default=0.0, type=float)
parser.add_option("-n", "--nevt", default=1000, type=int)
(opts, args) = parser.parse_args()

assert len(args) == 1
temp = float(args[0])

v = opts.vmin
while v < opts.vmax:
    os.system("python sipmcalibrationrun.py %g %g -n %d -t %g" % (v, temp, opts.nevt, opts.trim))
    v += opts.deltav
