import argparse
import getpass
import subprocess
import time


def auto_int(x):
    return int(x, 0)

parser = argparse.ArgumentParser()
parser.add_argument("ip", type=auto_int)
args = parser.parse_args()

ip = args.ip % 256

t = time.strftime("%d%b%y_%H%M")
user = getpass.getuser()

# First run with default alarm temperature

cmd = ["./overtemp", "0x%02x" % ip]
print cmd
outp = subprocess.check_output(cmd)
outp = outp.split("\n")
boardid = None
temp = None
for line in outp:
    print line
    if "Using board ID" in line:
        boardid = line.rstrip()
        boardid = boardid.split("=")[1]
        boardid = auto_int(boardid)
    if "LM82 local temperature" in line:
        temp = line.rstrip()
        temp = temp.split("=")[-1]
        temp = temp.replace("C", "")
        temp = float(temp)
        
assert boardid is not None
assert temp is not None
print "Board id = %012x" % boardid
print "Current temperature = %0.1f" % temp

# Nex run with alarm temperature 2 C below current temperature
cmd = ["./overtemp", "-alarmtemp", "%0.1f" % (temp - 2), "0x%02x" % ip]
print cmd
code = subprocess.call(cmd)
print "Return code = %d" % code

# Try to ping the board, if ping is success then overtemperature protection failed to shut it down.

cmd = ["ping", "-c", "1", "192.168.235.%d" % ip]
print cmd
code = subprocess.call(cmd)
status = ""
if code == 0:
    status = "failure"
    print "Ping worked, over temperature shutdown failed"
else:
    status = "success"
    print "No ping response, over temperature shutdown worked"

fn = "reports/report_overtemp_%s_%s.txt" % (boardid, t)
print "Writing report to %s" % fn
outp = open(fn, "w")
outp.write("Time: %s\n" % t)
outp.write("Tester: %s\n" % user)
outp.write("Board: %012x\n" % boardid)
outp.write("Over temperature test: %s\n" % status)
outp.close()
print "\nBoard 0x%012x: %s\n" % (boardid, status)
