#!/usr/bin/python

import uhal
from time import sleep
import sys
import collections

def zsdot(i):
	return ' ' if i == 0 else '!'

def zsfmt(i):
	return "%s%s%04x %s%s%04x" % (zsdot(i & 0x8000), zsdot(i & 0x4000), i & 0x3fff,
		zsdot(i & 0x80000000), zsdot(i & 0x40000000), (i & 0x3fff0000) >> 16)

uhal.setLogLevelTo(uhal.LogLevel.ERROR)
board = uhal.getDevice("board", "ipbusudp-2.0://192.168.235.1:50001", "file://addr_tab/top.xml")
#board.getClient().setTimeoutPeriod(10000)

v = board.getNode("csr.id").read()
board.dispatch()
print hex(v)

board.getNode("timing.csr.ctrl.rst").write(1)
board.dispatch()

board.getNode("csr.ctrl.soft_rst").write(1)
board.dispatch()
board.getNode("csr.ctrl.soft_rst").write(0)
board.dispatch()

sleep(1)

board.getNode("csr.ctrl.chan").write(0x0)
board.getNode("chan.csr.ctrl.mode").write(0x0)
board.getNode("chan.csr.ctrl.src").write(0x3)
board.getNode("chan.csr.ctrl.zs_thresh").write(0x2fff)
board.getNode("chan.csr.ctrl.en_buf").write(0x1)
board.getNode("csr.ctrl.chan").write(0x1)
board.getNode("chan.csr.ctrl.mode").write(0x0)
board.getNode("chan.csr.ctrl.src").write(0x3)
board.getNode("chan.csr.ctrl.zs_thresh").write(0x1fff)
board.getNode("chan.csr.ctrl.en_buf").write(0x1)
board.getNode("trig.loc.rnd_mode").write(0x0)
board.getNode("trig.loc.rnd_div").write(0x2)
board.getNode("trig.loc.trig_en").write(0x1)
board.getNode("trig.seq.conf.addr").write(0x0)
board.getNode("trig.seq.conf.data").write(0x00020000)
board.getNode("trig.csr.ctrl.dtmon_en").write(0)
board.getNode("timing.csr.ctrl.force_sync").write(1)
board.dispatch()

sleep(1)

board.getNode("trig.csr.ctrl.dtmon_en").write(1)
board.dispatch()


while True:
	
	board.getNode("trig.loc.trig_force").write(1)
	board.getNode("trig.loc.trig_force").write(0)
	board.dispatch()
	
	sleep(1)
	
	b0 = board.getNode("trig.csr.evt_ctr").read()
	b1 = board.getNode("trig.csr.stat").read()
	b2 = board.getNode("roc.csr.stat").read()
	b3 = board.getNode("roc.buf.count").read()
	b4 = board.getNode("roc.csr.tot_data").read()
	b5 = board.getNode("chan.csr.stat").read()
	board.getNode("trig.dtmon.addr").write(0)
	bb = board.getNode("trig.dtmon.data").readBlock(16)
	board.dispatch()
	
	print "Evt_ctr: %08x Trig_stat: %08x Roc_stat: %08x Buf_cnt: %08x Roc_tot: %08x Chan_stat: %08x" % (int(b0), int(b1), int(b2), int(b3), int(b4), int(b5))
	print "DT: ", [hex(bb[i]) for i in range(16)]
