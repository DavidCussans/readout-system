import array
import optparse
import time

import uhal
import ROOT

import chanmap
import frontend

class ROOTFile:

    def __init__(self, fn, mapping=chanmap.fpgachans):
        self.mapping = mapping
        self.outp = ROOT.TFile(fn, "RECREATE")
        self.outp.cd()
        self.tree = ROOT.TTree("waveforms", "waveforms")
        self.waveforms = []
        self.histos = []
        self.condstree = None
        for i in range(8):
            self.waveforms.append(ROOT.vector("float")())
        for i in range(8):
            name = "wf_chan%d" % i
            wf = self.waveforms[self.mapping[i]]
            self.tree.Branch(name, wf)
            h = ROOT.TH1I("h_val_%s" % name, name, 2**14, 0, 2**14)
            h.SetXTitle("Value [ADC count]")
            h.SetYTitle("samples")
            self.histos.append(h)

    def conditions(self, reqbias, measbias, temp, trims, sipms=chanmap.sipms):
        self.condstree = ROOT.TTree("conditions", "conditions")
        reqbias = array.array("d", [reqbias])
        measbias = array.array("d", [measbias])
        temp = array.array("d", [temp])
        chantrims = ROOT.vector("double")()
        for trim in trims:
            chantrims.push_back(trim)
        self.condstree.Branch("reqbias", reqbias, "reqbias/D")
        self.condstree.Branch("measbias", measbias, "measbias/D")
        self.condstree.Branch("temp", temp, "temp/D")
        self.condstree.Branch("trims", chantrims)
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
            wf = self.waveforms[self.mapping[i]]
            h = self.histos[self.mapping[i]]
            wfpb = wf.push_back
            for val in wfdata:
                wfpb(float(val & 0x3fff))
                h.Fill(val)
        self.tree.Fill()

    def close(self):
        self.outp.cd()
        for h in self.histos:
            h.Write()
        if self.condstree is not None:
            self.condstree.Write()
            self.sensortree.Write()
        self.tree.Write()
        self.outp.Close()

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-b", "--bias", default=65.0, type=float)
    parser.add_option("-p", "--plot", default=False, action="store_true")
    parser.add_option("-n", "--nevt", default=10, type=int)
    parser.add_option("-v", "--fwversion")
    parser.add_option("-t", "--testpattern", type=int)
    (opts, args) = parser.parse_args()
    bias = opts.bias
    if opts.testpattern is not None:
        bias = 0.0
    assert bias >= 0.0 and bias <= 70.0
    fpga = frontend.SoLidFPGA(1, minversion=opts.fwversion)
    print "Initial ADC settings:"
    for adc in fpga.adcs:
        adc.getstatus()
    fpga.reset()
    fpga.readvoltages()
    fpga.bias(bias)
    fpga.trim(0.0)
    fpga.readvoltages()
    trims = []
    for i in range(8):
        trims.append(0.0)
    for adc in fpga.adcs:
        adc.getstatus()
    if opts.testpattern is not None:
        testpattern = opts.testpattern & 0x3fff
        for adc in fpga.adcs:
            adc.testpattern(True, testpattern)
            adc.gettestpattern()
            adc.getstatus()
    outp = ROOTFile("test.root", chanmap.fpgachans) 
    outp.conditions(bias, 0.0, 0.0, trims)
    print "Triggering %d random events." % opts.nevt
    for i in range(opts.nevt):
        if opts.nevt > 1000:
            if i % (opts.nevt / 10) == 0:
                print "%d of %d" % (i, opts.nevt)
        outp.fill(fpga.trigger.trigger())
    outp.close()
