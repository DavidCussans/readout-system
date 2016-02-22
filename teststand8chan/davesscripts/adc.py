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
DATA_PATT = 8 * [0x7f] + 2 * [0x3f80] + 2 * [0x2aaa]

for i in range(12):
    print hex(i), ":",
    board.getNode("ctrl_reg.ctrl.chan").write(i)    
    board.getNode("chan.csr.ctrl.en_sync").write(1)
    board.getNode("chan.csr.ctrl.patt").write(DATA_PATT[i])
    board.dispatch()
    for j in range(SLIP_CNT):
        board.getNode("timing.csr.ctrl.chan_slip").write(1)
        board.dispatch()
    board.getNode("timing.csr.ctrl.chan_slip").write(0)
    board.dispatch()
    va = 0xfffff
    for j in range(32):
        board.getNode("chan.csr.ctrl.en_comp").write(1)
        board.dispatch()
        sleep(0.1)
        v = board.getNode("chan.csr.stat.err_cnt").read()
        board.dispatch()
        if v != va:
            print hex(j), hex(v), "|", 
        va = v
        board.getNode("chan.csr.ctrl.en_comp").write(0)
        board.getNode("timing.csr.ctrl.chan_inc").write(1)
        board.getNode("timing.csr.ctrl.chan_inc").write(0)
        board.dispatch()
    print
