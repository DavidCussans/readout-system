import array
import optparse
import time

import uhal
import ROOT

import chanmap
import frontend
import temperature

class ROOTFile:

    def __init__(self, fn, mapping=chanmap.fpgachans):
        self.mapping = mapping
        self.outp = ROOT.TFile(fn, "RECREATE")
        self.outp.cd()
        self.tree = ROOT.TTree("waveforms", "waveforms")
        self.waveforms = []
        self.histos = []
        self.condstree = None
        self.temptree = None
        for i in range(8):
            self.waveforms.append(ROOT.vector("float")())
        for i in range(8):
            name = "wf_chan%d" % i
            wf = self.waveforms[self.mapping[i]]
            self.tree.Branch(name, wf)
            channumber = self.mapping[i]
            name = "wf_chan%d" % channumber
            h = ROOT.TH1I("h_val_%s" % name, name, 2**14, 0, 2**14)
            h.SetXTitle("Value [ADC count]")
            h.SetYTitle("samples")
            self.histos.append(h)

    def conditions(self, reqbias, measbias, temp, trims, sipms=chanmap.sipms, tinitial=[], tfinal=[]):
        self.condstree = ROOT.TTree("conditions", "conditions")
        reqbias = array.array("d", [reqbias])
        measbias = array.array("d", [measbias])
        tempinitial = ROOT.vector("double")()
        tempfinal = ROOT.vector("double")()
        for t in tinitial:
            tempinitial.push_back(t)
        for t in tfinal:
            tempfinal.push_back(t)
        chantrims = ROOT.vector("double")()
        for trim in trims:
            chantrims.push_back(trim)
        self.condstree.Branch("HVbias", reqbias, "ias/D")
        self.condstree.Branch("initialtemp", tempinitial)
        self.condstree.Branch("finaltemp", tempfinal)
        self.condstree.Branch("LVtrims", chantrims)
        self.condstree.Fill()

        self.sensortree = ROOT.TTree("sensors", "Sensors")
        serial = array.array("i", [0])
        vop = array.array("d", [0.0])
        gain = array.array("d", [0.0])
        dcr = array.array("d", [0.0])
        self.sensortree.Branch("serial", serial, "serial/I")
        self.sensortree.Branch("vop", vop, "vop/D")
        self.sensortree.Branch("gain", gain, "gain/D")
        self.sensortree.Branch("dcr", dcr, "dcr/D")
        for sipm in sipms:
            serial[0] = sipm.serial
            vop[0] = sipm.vop
            gain[0] = sipm.gain
            dcr[0] = sipm.dcr
            self.sensortree.Fill()

    def fill(self, data):
        for wf in self.waveforms:
            wf.clear()
        for i in range(8):
            wfdata = data[i]
            wf = self.waveforms[i]
            h = self.histos[i]
            wfpb = wf.push_back
            for val in wfdata:
                wfpb(float(val & 0x3fff))
                h.Fill(val)
        self.tree.Fill()

    def close(self):
        self.outp.cd()
        for i in self.mapping:
            self.histos[i].Write()
        if self.condstree is not None:
            self.condstree.Write()
            self.sensortree.Write()
        if self.temptree is not None:
            self.temptree.Write()
        self.tree.Write()
        self.outp.Close()

    def storetemps(self, tempinitial, tempfinal):
        self.outp.cd()
        self.temptree = ROOT.TTree("temperature", "temperature")
        self.tinitial = array.array("d", [tempinitial])
        self.tfinal = array.array("d", [tempfinal])
        self.temptree.Branch("initial", self.tinitial, "initial/D")
        self.temptree.Branch("final", self.tfinal, "final/D")
        self.temptree.Fill()

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-b", "--bias", default=65.0, type=float)
    parser.add_option("-c", "--chantrim", default=[], action="append")
    parser.add_option("--trim", default=0.0, type=float)
    parser.add_option("-p", "--plot", default=False, action="store_true")
    parser.add_option("-n", "--nevt", default=10, type=int)
    parser.add_option("-v", "--fwversion", type=int)
    parser.add_option("-t", "--testpattern", type=int)
    parser.add_option("-B", "--Board", default="SoLidFPGA")
    parser.add_option("-o", "--output", default="data/test.root")
    parser.add_option("--temp", default=False, action="store_true")
    (opts, args) = parser.parse_args()
    tempinitial = None
    tempfinal = None
    tempmonitor = None
    initialtemps = []
    finaltemps = []
    if opts.temp:
        tempmonitor = temperature.TemperatureMonitor()
        tempmonitor.update()
        while tempmonitor.timestamp is None:
            tempmonitor.update()
        tempinitial = tempmonitor.temps[0]
        initialtemps = list(tempmonitor.temps[:2])
    bias = opts.bias
    if opts.testpattern is not None:
        bias = 0.0
    assert bias >= 0.0 and bias <= 70.0
    fpga = frontend.SoLidFPGA(opts.Board, 1, minversion=opts.fwversion)
    print "Initial ADC settings:"
    for adc in fpga.adcs:
        adc.getstatus()
    fpga.reset()
    fpga.readvoltages()
    fpga.bias(bias)
    trim = opts.trim
    assert trim >= 0.0 and trim <= 5.0
    #fpga.trim(trim)
    #fpga.readvoltages()
    trims = {}
    trimlist = []
    for i in range(8):
        trims[i] = trim
        trimlist.append(trim)
    for chantrim in opts.chantrim:
        chan, trim = chantrim.split(",")
        chan = int(chan)
        trim = float(trim)
        assert chan >= 0 and chan < 8
        assert trim >= 0.0 and trim <= 5.0
        trims[chan] = trim
        trimlist[chan] = trim
    fpga.trims(trims)
    fpga.readvoltages()

    for adc in fpga.adcs:
        adc.getstatus()
    if opts.testpattern is not None:
        testpattern = int(opts.testpattern) & 0x3fff
        for adc in fpga.adcs:
            adc.testpattern(True, testpattern)
            adc.gettestpattern()
            adc.getstatus()
    outp = ROOTFile(opts.output, chanmap.fpgachans) 
    print "Triggering %d random events." % opts.nevt
    for i in range(opts.nevt):
        if opts.nevt > 1000:
            if i % (opts.nevt / 10) == 0:
                print "%d of %d" % (i, opts.nevt)
        outp.fill(fpga.trigger.trigger())
    if tempmonitor is not None:
        tempmonitor.update()
        tempfinal = tempmonitor.temps[0]
        finaltemps = list(tempmonitor.temps[:2])
    outp.conditions(bias, 0.0, 0.0, trimlist, chanmap.sipms[opts.Board], tinitial=initialtemps, tfinal = finaltemps)
    outp.close()
