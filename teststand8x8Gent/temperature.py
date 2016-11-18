import argparse
import serial
import time

class TemperatureMonitor:

    def __init__(self, path="/dev/ttyACM0"):
        self.ser = serial.Serial(path, timeout=0.5)
        self.timestamp = None
        self.temps = [None, None, None, None]

    def __repr__(self):
        if self.timestamp is None:
            return "Invalid temperature reading."
        msg = "%s: " % time.strftime("%H%M", self.timestamp)
        for i in range(4):
            msg += "%g, " % self.temps[i]
        msg = msg[:-2] + " C"
        return msg

    def update(self, verbose=False):
        self.ser.write("T")
        l = self.ser.readline()
        if l == "":
            print "Temperature sensor not responding, sending '?'"
            self.ser.write("?\n")
            l = "x"
            while l != "":
                l = self.ser.readline()
            self.ser.write("T")
            l = self.ser.readline()
        if verbose:
            print "Read from UART: ", l.rstrip()
        try:
            self.parse(l)
        except:
            for i in range(4):
                self.temps = None
                self.timestamp = None
            

    def parse(self, line):
        self.timestamp = time.localtime()
        line = line.split()
        sensor = 0
        for part in line:
           if "[C]" in part:
               part = part.replace("[C]", "")
               temp = float(part)
               self.temps[sensor] = temp
               sensor += 1
              

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    t = TemperatureMonitor()
    while True:
        t.update(args.verbose)
        print t
        time.sleep(5.0)
