import array
import optparse
import time

import uhal
import ROOT

import biasboard
import chanmap

class TriggerBlock:

    def __init__(self, target, nsamples=0x800):
        self.target = target
        self.nsamples = nsamples
        self.capture = target.getNode("timing.csr.ctrl.chan_cap")
        self.chanselect = target.getNode("ctrl_reg.ctrl.chan")
        self.fifo = target.getNode("chan.fifo")
        self.reset()

    def reset(self, slip=7, tap=16):
        print "Resetting board."
        # Soft reset
        soft_rst = self.target.getNode("ctrl_reg.ctrl.soft_rst")
        soft_rst.write(1)
        soft_rst.write(0)
        self.target.dispatch()
        time.sleep(1.0)
        # Reset clock
        timing_rst = self.target.getNode("timing.csr.ctrl.rst")
        timing_rst.write(0x1)
        self.target.dispatch()
        timing_rst.write(0x0)
        self.target.dispatch()
        # check ID
        boardid = self.target.getNode("ctrl_reg.id").read()
        stat = self.target.getNode("ctrl_reg.stat").read()
        self.target.dispatch()
        print "ID = 0x%x, stat = 0x%x" % (boardid, stat)
        # Set up channels
        for i in range(8):
            self.target.getNode("ctrl_reg.ctrl.chan").write(i)
            self.target.getNode("chan.csr.ctrl.en_sync").write(1)
        self.target.dispatch()
        # Timing offset
        print "Setting timing offset with channel slip = %d and %d taps." % (slip, tap)
        chan_slip = self.target.getNode("timing.csr.ctrl.chan_slip")
        for i in range(slip):
            chan_slip.write(1)
            self.target.dispatch()
        chan_slip.write(0)
        self.target.dispatch()
        chan_inc = self.target.getNode("timing.csr.ctrl.chan_inc")
        for i in range(tap):
            chan_inc.write(1)
            self.target.dispatch()
        chan_inc.write(0)
        self.target.dispatch()
        print "Reset complete."

    def trigger(self):
        data = []
        self.capture.write(1)
        self.capture.write(0)
        self.target.dispatch()
        for i in range(8):
            self.chanselect.write(i)
            wf = self.fifo.readBlock(self.nsamples)
            self.target.dispatch()
            data.append(wf)
        return data


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
    (opts, args) = parser.parse_args()
    bias = opts.bias
    assert bias >= 0.0 and bias <= 70.0
    biascontrol = biasboard.BiasControlBoard()
    biascontrol.bias(bias)
    trims = []
    for i in range(8):
        biascontrol.trim(i, 0.0)
        trims.append(0.0)
    target = uhal.getDevice("trenz", "ipbusudp-2.0://192.168.235.0:50001", "file://addr_table/top.xml")
    triggerblock = TriggerBlock(target)
    outp = ROOTFile("test.root", chanmap.fpgachans) 
    outp.conditions(bias, 0.0, 0.0, trims)
    print "Triggering %d random events." % opts.nevt
    for i in range(opts.nevt):
        if opts.nevt > 1000:
            if i % (opts.nevt / 10) == 0:
                print "%d of %d" % (i, opts.nevt)
        outp.fill(triggerblock.trigger())
    outp.close()
