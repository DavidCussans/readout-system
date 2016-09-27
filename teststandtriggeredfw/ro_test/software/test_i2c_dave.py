#!/usr/bin/python

import uhal
from time import sleep
import sys

#uhal.setLogLevelTo(uhal.LogLevel.INFO)
board = uhal.getDevice("glib", "ipbusudp-2.0://192.168.235.0:50001", "file://ipbus_example.xml")
#board.getClient().setTimeoutPeriod(10000)

v = board.getNode("ctrl_reg.id").read()
board.dispatch()
print hex(v)

print "Soft reset"
board.getNode("ctrl_reg.rst").write(0x1)
board.dispatch()

print "Write enable bit and prescale"
board.getNode("i2c.ps_lo").write(0x3f)
board.getNode("i2c.ps_hi").write(0x00)
board.getNode("i2c.ctrl").write(0x80)
board.getNode("i2c.cmd_stat").write(0x00)
board.dispatch()

print "Write address"
board.getNode("i2c.data").write(0xd1)
board.getNode("i2c.cmd_stat").write(0x90)
v = board.getNode("i2c.cmd_stat").read()
board.dispatch()

print "Read data"
board.getNode("i2c.cmd_stat").write(0x20)
board.dispatch()

v = board.getNode("i2c.data").read()
board.dispatch()
print hex(v)

board.getNode("i2c.cmd_stat").write(0x40)
board.dispatch()
