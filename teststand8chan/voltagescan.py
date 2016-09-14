import optparse
import os

parser = optparse.OptionParser(usage="python voltagescan.py [options] <temperature>")
parser.add_option("--vmin", default=62.5, type=float)
parser.add_option("--vmax", default=66.0, type=float)
parser.add_option("--deltav", default=0.1, type=float)
parser.add_option("--trim", default=0.0, type=float)
parser.add_option("-n", "--nevt", default=1000, type=int)
parser.add_option("-B", "--Board", default="SoLidFPGA")
parser.add_option("--settemp", default=None, type=float)
(opts, args) = parser.parse_args()

assert len(args) == 0

v = opts.vmin
while v < opts.vmax:
    cmd = "python sipmcalibrationrun.py %g -B %s -n %d -t %g"
    cmd = cmd % (v, opts.Board, opts.nevt, opts.trim)
    if opts.settemp is not None:
        cmd += " --settemp %f" % opts.settemp
    os.system(cmd)
    v += opts.deltav
