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

    def __init__(self, plot=None, mapping=chanmap.fpgachans):
        dt = 25e-9
        wflen = 2048
        self.freqs = np.fft.rfftfreq(wflen, dt) / 1e6 # in MHz
        self.mapping = mapping
        self.plot = plot
        self.canv = None
        if self.plot is not None:
            print "Setting up plotting."
            ROOT.gROOT.SetBatch(ROOT.kFALSE)
            print "BAtch mode: ", ROOT.gROOT.IsBatch()
            self.canv = ROOT.TCanvas()
            #self.canv.SetLogy()
        self.histos = []
        self.h2dft = None
        self.graphs = []
        self.coeffs = []
        self.nwf = 0
        for i in range(8):
            self.coeffs.append(None)
            channumber = self.mapping[i]
            name = "wf_chan%d" % channumber
            h = ROOT.TH1D("h_noise_%s" % name, name, 1000, 0, 100000000)
            h.SetXTitle("frequency [MHz]")
            #h.SetYTitle("samples")
            self.histos.append(h)

    def draw2d(self):
        df = self.freqs[1] - self.freqs[2]
        self.h2dft = ROOT.TH2D("h2dft", "", 8, 0, 8, len(self.freqs), self.freqs[0], self.freqs[-1] + df)
        self.h2dft.SetXTitle("Channel")
        self.h2dft.SetYTitle("freq [MHz]")
        self.h2dft.SetZTitle("power")
        for i in range(8):
            for j in range(1, len(self.freqs)):
                f = self.freqs[j]
                p = np.abs(self.coeffs[i][j]) / self.nwf
                self.h2dft.Fill(i, f, p)
        if self.plot is not None:
            #self.canv.SetLogy(0)
            #self.canv.SetLogz()
            self.h2dft.Draw("COLZ")
            self.canv.Update()

    def makegraphs(self):
        self.graphs = []
        for i in range(8):
            g = ROOT.TGraph(len(self.freqs), self.freqs, np.abs(self.coeffs[i]))
            g.SetName("g_noisespectrum_chan%d" % i)
            g.SetTitle("channel %d" % i)
            g.GetXaxis().SetTitle("freq [MHz]")
            self.graphs.append(g)

    def draw(self):
        #Update noise histogram plot for ~real time display
	#for i, h in enumerate(self.histos):
	#    hist = r2m.Hist(h)
	#    plt.subplot(2,4,i+1)
	#plt.draw()
        if self.plot is not None:
            x = self.freqs
            y = self.coeffs[self.plot] / self.nwf
            g = ROOT.TGraph(len(x[1:]), x[1:], y[1:])
            g.SetTitle("Channel %d" % self.plot)
            g.GetXaxis().SetTitle("freq [MHz]")
            g.GetYaxis().SetTitle("power")
            g.Draw("AL")
            self.canv.Update()

    def addwaveforms(self, data):
        self.nwf += 1
        #Get noise spectrum from new waveforms, add to existing histos.
        for i in range(len(data)):
            wf = np.array(data[i]) & 0x3fff
            #coeffs = np.abs(fft.rfft(wf))
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
    parser.add_option("-p", "--plot", type=int)
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
    if opts.plot is not None:
        assert opts.plot >= 0 and opts.plot < 8
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
    if opts.plot is not None:
        raw_input("...")
    ns.draw2d()
    if opts.plot is not None:
        raw_input("Press enter to exit.")
    outp.storehistos([ns.h2dft])
    outp.close()
