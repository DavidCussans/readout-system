"""
Channel mapping for Bristol 8 channel test stand and Gent 8x8 test plane.
"""


class SiPM:

    def __init__(self, serial, vop, gain, dcr):
        self.serial = serial
        self.vop = vop
        self.gain = gain * 1e6
        self.dcr = dcr * 1e6


# List contains ribbon cable number for each FPGA register
fpgachans = [1, 0, 3, 2, 5, 4, 6, 7]

# List contains SiPM for each ribbon cable number
sipmsBristol = [
    SiPM(3405, 66.85, 1.25, 1.1),
    SiPM(3404, 66.85, 1.25, 1.0),
    SiPM(3403, 66.90, 1.25, 1.0),
    SiPM(3399, 66.91, 1.24, 0.98),
    SiPM(3397, 66.89, 1.25, 0.92),
    SiPM(3396, 66.88, 1.24, 0.95),
    SiPM(3395, 66.90, 1.25, 0.92),
    SiPM(1125, 66.92, 1.26, 0.81)
]
sipmsGent0 = [
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.01)
]
sipmsGent1 = [
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0),
    SiPM(0000, 00.00, 0.00, 0.0)
]

sipms = {
        "SoLidFPGA" : sipmsBristol,
        "Gent0": sipmsGent1,
        "Gent1": sipmsGent1
}

