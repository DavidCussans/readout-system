import argparse
import getpass
import os
import subprocess
import time

import ROOT

def auto_int(x):
    return int(x, 0)

t = time.strftime("%d%b%y_%H%M")

parser = argparse.ArgumentParser()
parser.add_argument("ip", type=auto_int)
args = parser.parse_args()

ip = args.ip % 256

inp = open("solidfpgaqa.xml")
data = inp.read()
inp.close()
outp = open("solidfpga.xml", "w")
outp.write(data % ip)
outp.close()

taps = range(16)
slips = [4, 7]

outputfiles = []
boardid = ""
for tap in taps:
    for slip in slips:
        cmd = ["./run64chdigi", "-out"]
        cmd.append("t%d_s%d" % (tap, slip))
        cmd.extend(["-pattern", "0x2030", "-periodic", "250.0", "qa64", "5.0", "data/"])
        print cmd
        outp = subprocess.check_output(cmd)
        outp = outp.split("\n")
        fn = None
        for line in outp:
            if "bytes written" in line:
                fn = line.split(":")[0]
                break
        assert fn is not None
        print "output: %s" % fn
        outputfiles.append(fn)
        boardid = fn.split("_")[-1].replace(".sbf", "")
        time.sleep(1)
"""
outputfiles = os.listdir("data")
for i in range(len(outputfiles)):
    outputfiles[i] = os.path.join("data/", outputfiles[i])
    boardid = outputfiles[i].split("_")[-1].replace(".sbf", "")
print outputfiles
"""

gooddelays = {}
for i in range(64):
    gooddelays[i] = []

FNULL = open(os.devnull, "w")
for fn in outputfiles:
    parts = fn.split("_")
    tap = int(parts[2].replace("t", ""))
    slip = int(parts[3].replace("s", ""))
    cmd = []
    cmd.append("./saffron")
    cmd.append("safopsADCTiming.txt")
    cmd.append("--AppendInputFiles=%s" % fn)
    print cmd
    stat = subprocess.call(cmd, stdout=FNULL)
    assert stat == 0
    inp = ROOT.TFile("S2-histos_cycleMode.root", "READ")
    for chan in range(64):
        h = inp.Get("SCheckTestPattern/h_samples_ch%d" % chan)
        mean = int(h.GetMean())
        rms = h.GetRMS()
        if rms == 0:
            if mean == 0x2030:
                gooddelays[chan].append((tap, slip))
    inp.Close()
FNULL.close()
defaultdelays = [
        (5, 7),     # ADC 0
        (1, 7),     # ADC 1
        (1, 7),     # ADC 2
        (3, 7),     # ADC 3
        (8, 7),     # ADC 4
        (7, 7),     # ADC 5
        (10, 7),     # ADC 6
        (1, 4)      # ADC 7
]
fn = "reports/report_delays_%s_%s.txt" % (boardid, t)
print "Writing report to %s" % fn
outp = open(fn, "w")
outp.write("Time: %s\n" % t)
outp.write("Tester: %s\n" % getpass.getuser())
outp.write("Board: %s\n" % boardid)
outp.write("Delays:\n")
fail = False
nwarn = 0
for chan in range(64):
    delays = gooddelays[chan]
    if len(delays) == 0:
        outp.write("\tchan %d: failure\n" % chan)
        fail = True
        continue
    #assert len(delays) > 0, "Channel %d has no good delays: FAIL" % chan
    adc = int(chan / 8.0)
    default = defaultdelays[adc]
    if default not in delays:
        nwarn += 1
        print "Warning: channel %d default delay (%d, %d) not good" % (chan, default[0], default[1])
        outp.write("\tchan %d: warning\n" % chan)
    else:
        outp.write("\tchan %d: success\n" % chan)
outp.close()

if fail:
    print "Board %s: FAIL" % boardid
else:
    if nwarn > 0:
        print "Board %s: %d warnings" % (boardid, nwarn)
    else:
        print "Board %s: success" % boardid



