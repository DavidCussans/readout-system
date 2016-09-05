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

    def update(self):
        new = True
        while new:
            l = self.ser.readline()
            if len(l) == 0:
                new = False
            else:
                self.parse(l)

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
    t = TemperatureMonitor()
    while True:
        t.update()
        print t
        time.sleep(5.0)
