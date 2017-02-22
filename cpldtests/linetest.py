import sys

import uhal

print sys.argv

if len(sys.argv) > 3 or len(sys.argv) < 2:
    print "python lintests.py <cpld line> [led setting]"
    sys.exit(1)

line = int(sys.argv[1]) % 32
cm = uhal.ConnectionManager("file://solidfpga.xml")
target = cm.getDevice("Fry")
target.getNode("csr.ctrl.io_sel").write(line)
target.dispatch()
val = target.getNode("csr.ctrl.io_sel").read()
target.dispatch()
print "CPLD address lines, tried to set %d, value now %d" % (line, val)

if len(sys.argv) == 3:
    led = int(sys.argv[2]) % 8
    target.getNode("csr.ctrl.leds").write(led)
    target.dispatch()
    val = target.getNode("csr.ctrl.leds").read()
    target.dispatch()
    print "Tried to set LEDs to %d, value now %d" % (led, val)

