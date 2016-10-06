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

def dump():
	b0 = board.getNode("trig.csr.evt_ctr").read() # Event counter
	b1 = board.getNode("trig.csr.stat").read() # Trigger block status
	b2 = board.getNode("roc.csr.stat").read() # ROC status
	b3 = board.getNode("roc.buf.count").read() # ROC buffer count
	b4 = board.getNode("roc.csr.tot_data").read() # ROC total data issued
	b5 = board.getNode("chan.csr.stat").read() # Channel status
	b6 = board.getNode("roc.csr.wctr").read() # Debug - not important
	board.dispatch()
	
	print "Evt_ctr: %08x Trig_stat: %08x Roc_stat: %08x Buf_cnt: %08x Roc_tot: %08x Chan_stat: %08x Wctr: %08x" % (int(b0), int(b1), int(b2), int(b3), int(b4), int(b5), int(b6))

uhal.setLogLevelTo(uhal.LogLevel.ERROR)
board = uhal.getDevice("board", "ipbusudp-2.0://192.168.235.1:50001", "file://addr_tab/top.xml")
#board.getClient().setTimeoutPeriod(10000)

v = board.getNode("csr.id").read()
board.dispatch()
print hex(v)

board.getNode("timing.csr.ctrl.rst").write(1) # Hold clk40 domain in reset
board.dispatch()

board.getNode("csr.ctrl.soft_rst").write(1) # Reset ipbus registers
board.dispatch()

sleep(1)

board.getNode("csr.ctrl.chan").write(0x0) # Talk to channel 0
board.getNode("chan.csr.ctrl.mode").write(0x0) # Set to normal DAQ mode
board.getNode("chan.csr.ctrl.src").write(0x3) # Set source to random number generator
board.getNode("chan.csr.ctrl.zs_thresh").write(0x2fff) # Set ZS threshold
board.getNode("chan.csr.ctrl.en_buf").write(0x1) # Enable this channel
board.getNode("csr.ctrl.chan").write(0x1) # Talk to channel 1
board.getNode("chan.csr.ctrl.mode").write(0x0)
board.getNode("chan.csr.ctrl.src").write(0x3)
board.getNode("chan.csr.ctrl.zs_thresh").write(0x1fff)
board.getNode("chan.csr.ctrl.en_buf").write(0x1)
board.getNode("trig.loc.rnd_mode").write(0x3) # Set random trigger generator to Poisson mode
board.getNode("trig.loc.rnd_div").write(0xa) # Set random trigger rate to 40MHz / 2^11 = 20kHz
board.getNode("trig.loc.trig_en").write(0x1) # Enable trigger type 0 (random trigger)
board.getNode("trig.seq.conf.addr").write(0x0) # Set sequencer table to entry 0 (trigger type 0) 
board.getNode("trig.seq.conf.data").write(0x00010000) # Set offet = 0, block count = 1 for trigger type 0
board.getNode("timing.csr.ctrl.force_sync").write(1) # And... go.
board.dispatch()

sleep(1)

r = list()
evts = 0
max_evts = 100
nbuf = 0

outp = open("test.bin", "bw")

while evts < max_events:

	while nbuf == 0:
		nbuf = board.getNode("roc.buf.count").read() # Get the buffer data count
		board.dispatch()
#	dump()

	b = board.getNode("roc.buf.data").readBlock(int(nbuf)) # Read the buffer contents
	board.dispatch()
        outp.write(bytearray(b))
        evts += 1
outp.close()
