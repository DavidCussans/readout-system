import argparse
import getpass
import os
import subprocess
import time

import ROOT

t = time.strftime("%d%b%y_%H%M")
user = getpass.getuser()

def auto_int(x):
    return int(x, 0)

parser = argparse.ArgumentParser()
parser.add_argument("ip", type=auto_int)
args = parser.parse_args()

ip = args.ip % 256

inp = open("solidfpgaqa.xml", "r")
data = inp.read()
inp.close()
outp = open("solidfpga.xml", "w")
outp.write(data % ip)
outp.close()

lvfn = None
# First run with low vo

cmd = ["./run64chtrig", "-hv", "55.0", "-periodic", "100.0", "qa64", "peds.json", "10.0", "data/"]
print cmd
outp = subprocess.check_output(cmd)
outp = outp.split("\n")
for line in outp:
    if "bytes written" in line:
        lvfn = line.split(":")[0]
        break
assert lvfn is not None
time.sleep(1)

# Then run above breakdown voltage
hvfn = None
cmd = ["./run64chtrig", "-hv", "69.0", "-periodic", "100.0", "qa64", "peds.json", "10.0", "data/"]
print cmd
outp = subprocess.check_output(cmd)
outp = outp.split("\n")
for line in outp:
    if "bytes written" in line:
        hvfn = line.split(":")[0]
        break
assert hvfn is not None
time.sleep(1)

FNULL = open(os.devnull, "w")
# Process data with saffron
cmd = ["./saffron", "safopsSiPMcheck.txt", "--AppendInputFiles=%s" % lvfn]
code = subprocess.call(cmd, stdout=FNULL)
assert code == 0

failure = False
nwarning = 0
# low voltage should have mean = pedestal, RMS ~3
lvmean = []
targetmean = 600
lvrms = []
targetrms = 2.5
lvstatus = []
inp = ROOT.TFile("S2-histos_cycleMode.root", "READ")
for ch in range(64):
    status = "success"
    h = inp.Get("SWaveformMon/SamplesPerChannel/SamplesPerChannel_SChannel%d" % ch)
    m = h.GetMean()
    if m < targetmean - 100 or m > targetmean + 100:
        status = "warning"
    if m < targetmean - 300 or m > targetmean + 300:
        status = "failure"
        failure = True
    r = h.GetRMS()
    if r / targetrms > 1.5:
        status = "warning"
        nwarning += 1
    if r / targetrms > 2.5:
        status = "failure"
        nwarning -= 1
        failure = True
    lvmean.append(m)
    lvrms.append(r)
    lvstatus.append(status)
    if status != "success":
        print "Low voltage: %d %s" % (ch, status)
inp.Close()


cmd = ["./saffron", "safopsSiPMcheck.txt", "--AppendInputFiles=%s" % hvfn]
code = subprocess.call(cmd, stdout=FNULL)
assert code == 0
FNULL.close()

# high voltage should have mean > pedestal, RMS > 5
hvstatus = []
targetrms = 50.0
inp = ROOT.TFile("S2-histos_cycleMode.root", "READ")
for ch in range(64):
    status = "success"
    h = inp.Get("SWaveformMon/SamplesPerChannel/SamplesPerChannel_SChannel%d" % ch)
    r = h.GetRMS()
    if r < targetrms:
        print "chan %d HV RMS = %g: FAILURE" % (ch, r)
        status = "failure"
        failure = True
    hvstatus.append(status)
inp.Close()

print hvfn
boardid = hvfn.split("_")[1].replace(".sbf", "")

fn = "reports/report_sipmpulse_%s_%s.txt" % (boardid, t)
outp = open(fn, "w")
outp.write("Time: %s\n" % t)
outp.write("Tester: %s\n" % user)
outp.write("Board: %s\n" % boardid)
outp.write("Below breakdown:\n")
for ch in range(64):
    outp.write("\tchan %d: %s\n" % (ch, lvstatus[ch]))
outp.write("Above breakdown:\n")
for ch in range(64):
    outp.write("\tchan %d: %s\n" % (ch, hvstatus[ch]))
outp.close()

print "Report written to %s" % fn
if failure:
    print "\nBoard %s: FAILURE\n" % boardid
else:
    if nwarning == 0:
        print "\nBoard %s: success\n" % boardid
    else:
        print "\nBoard %s: %d warnings\n" % (boardid, nwarning)
