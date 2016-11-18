import optparse
import os

parser = optparse.OptionParser(usage="python voltagescan.py [options] <temperature>")
parser.add_option("--v", default=62.5, type=float)
parser.add_option("--tmin", default=0.0, type=float)
parser.add_option("--tmax", default=2.5, type=float)
parser.add_option("--deltat", default=0.05, type=float)
parser.add_option("-n", "--nevt", default=1000, type=int)
parser.add_option("-B", "--Board", default="SoLidFPGA")
parser.add_option("--settemp", default=None, type=float)
(opts, args) = parser.parse_args()

assert len(args) == 0

t = opts.tmin
while t < opts.tmax:
    cmd = "python sipmcalibrationrun.py %g -B %s -n %d -t %g"
    cmd = cmd % (opts.v, opts.Board, opts.nevt, t)
    if opts.settemp is not None:
        cmd += " --settemp %f" % opts.settemp
    os.system(cmd)
    t += opts.deltat
