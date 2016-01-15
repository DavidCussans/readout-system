import optparse

import solidfpga
import uhal

parser = optparse.OptionParser()
parser.add_option("-w", "--wbclk", type=float, default=31.25e6)
parser.add_option("-i", "--i2cclk", type=float, default=40e3)
opts, args = parser.parse_args()

cm = uhal.ConnectionManager("file://solidfpga.xml")
dev = cm.getDevice("SOLID_DIGITAL")
id = dev.getNode("ctrl_reg.id").read()
dev.dispatch()
print "ID = 0x%x" % id


slaveaddr = 0b1101000
print "Configuring I2C to run at %g Hz, with wishbone clock at %g Hz" % (opts.wbclk, opts.i2cclk)
i2c = solidfpga.I2CCore(dev, opts.wbclk, opts.i2cclk, "clk_i2c")
i2c.state()
i2c.clearint()
print "\n\n"
i2c.state()
print "\n\n"

n = i2c.write(slaveaddr, [0x0])
data = i2c.read(slaveaddr, 3)

print n, data
