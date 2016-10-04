import array
import optparse
import time

import uhal
import ROOT

import chanmap
import frontend
import storedata
import temperature

import numpy as np
import numpy.fft as fft

#import matplotlib.pyplot as plt
#import root2matplot as r2m

class NoiseSpectra:

    def __init__(self, plot=False, mapping=chanmap.fpgachans):
        dt = 25e-9
        wflen = 2048
        self.freqs = np.fft.rfftfreq(wflen, dt) / 1e6 # in MHz
        self.mapping = mapping
        self.plot = plot
        if self.plot:
            self.canv = ROOT.TCanvas()
            self.canv.SetLogy()
        self.histos = []
        self.graphs = []
        self.coeffs = []
        for i in range(8):
            self.coeffs.append(None)
            channumber = self.mapping[i]
            name = "wf_chan%d" % channumber
            h = ROOT.TH1D("h_noise_%s" % name, name, 1000, 0, 100000000)
            h.SetXTitle("frequency [Hz]")
            #h.SetYTitle("samples")
            self.histos.append(h)

    def makegraphs(self):
        self.graphs = []
        for i in range(8):
            g = ROOT.TGraph(len(self.freqs), self.freqs, self.coeffs[i])
            g.SetName("g_noisespectrum_chan%d" % i)
            g.GetXaxis().SetTitle("freq [MHz]")
            self.graphs.append(g)

    def draw(self):
        #Update noise histogram plot for ~real time display
	#for i, h in enumerate(self.histos):
	#    hist = r2m.Hist(h)
	#    plt.subplot(2,4,i+1)
	#plt.draw()
        if self.plot:
            x = self.freqs
            y = self.coeffs[0]
            g = ROOT.TGraph(len(x), x, y)
            g.GetXaxis().SetTitle("freq [MHz]")
            g.Draw("AL")
            self.canv.Update()

    def addwaveforms(self, data):
        #Get noise spectrum from new waveforms, add to existing histos.
        for i in range(len(data)):
            wf = data[i]
            coeffs = np.abs(fft.rfft(wf))
            if self.coeffs[i] is None:
                self.coeffs[i] = coeffs
            else:
                self.coeffs[i] += coeffs
            #fftwf = np.abs(fft.rfft(wf))**2
            #time_step = 25e-09
            #freqs = fft.fftfreq(len(wf), time_step)
            #idx = np.argsort(freqs)
            # Add spectrum to existing histo
            #h = self.histos[i]
            #for f in idx:
                #h.Fill(freqs[f], fftwf[f])
        self.draw()

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
    parser.add_option("-o", "--output", default="data/noisetest.root")
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
        initialtemps = list(tempmonitor.temps)
    bias = opts.bias
    if opts.testpattern is not None:
        bias = 0.0
    assert bias >= 0.0 and bias <= 70.0
    ns = NoiseSpectra(plot=opts.plot)
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
    outp = storedata.ROOTFile(opts.output, chanmap.fpgachans) 
    print "Triggering %d random events." % opts.nevt
    for i in range(opts.nevt):
        if opts.nevt > 1000:
            if i % (opts.nevt / 10) == 0:
                print "%d of %d" % (i, opts.nevt)
        data = fpga.trigger.trigger()
        ns.addwaveforms(data)
	ns.draw()
        outp.fill(data)
    if tempmonitor is not None:
        tempmonitor.update()
        tempfinal = tempmonitor.temps[0]
        finaltemps = list(tempmonitor.temps)
    outp.conditions(bias, 0.0, 0.0, trimlist, chanmap.sipms[opts.Board], tinitial=initialtemps, tfinal = finaltemps)
    ns.makegraphs()
    outp.storehistos(ns.graphs)
    if opts.plot:
        raw_input("Press enter to exit.")
    outp.close()
