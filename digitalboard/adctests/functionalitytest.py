"""
functionalitytest.py checks the SPI interface to the LTM9007.
"""

import solidfpa

fpga = SoLidFPGA(1)
fpga.adcs[0].checkwrite=True
fpga.config()

dut = fpga.adcs[0]
# Perform each configuration fuction
dut.reset()
dut.testpattern(True, 0x2b0b) 
dut.testpattern(False)
dut.setoutputmode(3.0, False, True, 1, 14)
dut.setformat(True, False)
dut.setsleep(True)
dut.setsleep(False)
dut.nap([1, 4, 7, 8])
dut.reset()
