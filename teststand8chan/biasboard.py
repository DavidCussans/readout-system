"""
Control global bias and per-channel trims via FDRM uC board.

Library assumes the board is running Nick's code:
    https://developer.mbed.org/teams/SoLid-experiment/code/Solid8chAnalogBoardContol/

The library sends the simply messages over a USB serial connection to set the DAC voltages.
"""

import serial


class BiasControlBoard:
	"""FDRM uC board running Nick's code."""

	def __init__(self, fn="/dev/ttyACM0", timeout=1.0):
		self.ser = serial.Serial(fn, timeout=timeout)


	def readsome(self, verbose=True):
		msg = ""
		read = True
		while read:
			l = self.ser.readline()
			if len(l) == 0:
				read = False
			else:
				msg += l + "\n"
				if verbose:
					print l
		return msg
		

	def trim(self, chan, voltage):
		"""Set the trim voltage (0 - 5 V) on a specific channel."""
		self.ser.write("vtrim=%d,%f\n" % (chan, voltage))
		rep = self.readsome()
		
	def bias(self, voltage):
		"""Set the global HV bias (0 - 70 V)."""
		self.ser.write("vbias=%f\n" % voltage)
		rep = self.readsome()
