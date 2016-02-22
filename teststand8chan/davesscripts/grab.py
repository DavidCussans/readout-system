#!/usr/bin/python

import uhal
from time import sleep
import sys

uhal.setLogLevelTo(uhal.LogLevel.INFO)
board = uhal.getDevice("glib", "ipbusudp-2.0://192.168.235.0:50001", "file://top.xml")
#board.getClient().setTimeoutPeriod(10000)

print "*Soft reset"
board.getNode("ctrl_reg.ctrl.soft_rst").write(0x1)
board.dispatch()

print "*clk40 reset"
board.getNode("timing.csr.ctrl.rst").write(0x1)
board.dispatch()
board.getNode("timing.csr.ctrl.rst").write(0x0)
board.dispatch()

v = board.getNode("ctrl_reg.id").read()
v2 = board.getNode("ctrl_reg.stat").read()
board.dispatch()
print "ID, stat:", hex(v), hex(v2)

SLIP_CNT = 7
TAP_CNT = 16
DATA_PATT = 0x7f

print "*Setting up channels"
for i in range(8):
    board.getNode("ctrl_reg.ctrl.chan").write(i)
    board.getNode("chan.csr.ctrl.en_sync").write(1)
board.dispatch()

for j in range(SLIP_CNT):
    board.getNode("timing.csr.ctrl.chan_slip").write(1)
    board.dispatch()
board.getNode("timing.csr.ctrl.chan_slip").write(0)
board.dispatch()
for j in range(TAP_CNT):
    board.getNode("timing.csr.ctrl.chan_inc").write(1)
    board.dispatch()
board.getNode("timing.csr.ctrl.chan_inc").write(0)
board.dispatch()

print "*Sampling"
board.getNode("timing.csr.ctrl.chan_cap").write(1)
board.getNode("timing.csr.ctrl.chan_cap").write(0)
board.dispatch()

for i in range(8):
    board.getNode("ctrl_reg.ctrl.chan").write(i)
    v = board.getNode("chan.fifo").readBlock(0x800)
    board.dispatch()
    print ','.join(str(int(p) & 0x3fff) for p in v)
