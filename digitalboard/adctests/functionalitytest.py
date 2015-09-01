"""
functionalitytest.py checks the SPI interface to the LTM9007.
"""

import adc


dev = adc.ADC(True) # Enforce write check
# Perform each configuration fuction
dev.reset()
dev.testpattern(True, 0x2b0b) 
dev.testpattern(False)
dev.setoutputmode(3.0, False, True, 1, 14)
dev.setformat(True, False)
dev.setsleep(True)
dev.setsleep(False)
dev.nap([1, 4, 7, 8])
dev.reset()
