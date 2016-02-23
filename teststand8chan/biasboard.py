"""
Control global bias and per-channel trims via FDRM uC board.

Library assumes the board is running Nick's code:
    https://developer.mbed.org/teams/SoLid-experiment/code/Solid8chAnalogBoardContol/

The library sends the simply messages over a USB serial connection to set the DAC voltages.
"""

import optparse
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

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-f", "--filename", default="/dev/ttyACM0")
    parser.add_option("-b", "--bias", default=None, type=float)
    parser.add_option("-t", "--trim", default=None, type=float)
    parser.add_option("-c", "--chantrim", default=[], action="append")
    (opts, args) = parser.parse_args()
    bcb = BiasControlBoard(opts.filename)
    if opts.bias is not None:
        bias = opts.bias
        assert bias >= 0.0 and bias <= 70.0
        bcb.bias(bias)
    if opts.trim is not None:
        trim = opts.trim
        assert trim >= 0.0 and trim <= 5.0
        for i in range(8):
            bcb.trim(i, trim)
    else:
        for chantrim in opts.chantrim:
            (chan, trim) = chantrim.split(",")
            chan = int(chan)
            trim = float(trim)
            print "Setting channel %d to %g V" % (chan, trim)
            assert chan >= 0 and chan < 8
            assert trim >= 0.0 and trim <= 5.0
            bcb.trim(chan, trim)
