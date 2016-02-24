import argparse
import array
import math
import os

import ROOT

import fitspa

parser = argparse.ArgumentParser()
parser.add_argument("chan", type=int)
parser.add_argument("-t", "--temp", type=float, default=25.0)
args = parser.parse_args()
assert args.temp in [15.0, 20.0, 25.0]

def twospa(vals, pars):
    x = vals[0]
    ampexp = pars[0]
    slopeexp = pars[1]
    spa = pars[2]
    amp1pa = pars[3]
    width1pa = pars[4]
    relamp2pa = pars[5]
    width2pa = pars[6]
    val = ampexp * math.exp(-x / slopeexp)
    val += amp1pa * math.exp(-(x - spa)**2 / width1pa)
    val += amp1pa * relamp2pa * math.exp(-(x - 2*spa)**2 / width2pa)
    return val

class ChanCalibrations:

    def __init__(self, chan):
        self.chan = chan
        self.calibrations = []
        self.colours = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kMagenta, ROOT.kCyan, ROOT.kGray]

    def add(self, calib):
        assert calib.chan == self.chan
        self.calibrations.append(calib)

    def drawpeaks(self, canv):
        maxhist = None
        maxheight = 0
        minv = None
        for calib in self.calibrations:
            height = calib.h_amp.GetMaximum()
            if height > maxheight:
                maxheight = height
                maxhist = calib.h_amp
            v = calib.voltage
            if minv is None or v < minv:
                minv = v
        leg = ROOT.TLegend(0.8, 0.6, 0.95, 0.95)
        for i in range(len(self.calibrations)):
            self.calibrations[i].h_amp.SetLineColor(self.colours[i % len(self.colours)])
            v = self.calibrations[i].voltage - minv
            leg.AddEntry(self.calibrations[i].h_amp, "v_{0} + %g V" % v, "L")
        maxhist.GetXaxis().SetRangeUser(0, 200.0)
        maxhist.Draw()
        for calib in self.calibrations:
            calib.h_amp.Draw("SAME")
        leg.Draw()
        canv.Update()
        canv.SaveAs("h_amp_ch%d.png" % self.chan)
        canv.SaveAs("h_amp_ch%d.eps" % self.chan)
        raw_input("...")

class Calibration:

    def __init__(self, voltage, temp, chan, inp):
        self.voltage = voltage
        self.temp = temp
        self.chan = chan
        self.inp = inp
        self.h_amp = None
        self.SPA = None
        self.dSPA = None
        self.DCR = None
        self.CT = None

    def getamps(self):
        name = "h_amp_ch%d" % self.chan
        self.h_amp = self.inp.Get(name)
        name = self.h_amp.GetName
        self.h_amp.SetName("%s_%0.2fV_%0.2fC" % (name, self.voltage, self.temp))

    def fitSPA(self, canv=ROOT.TCanvas()):
        self.h_amp = self.inp.Get("h_amp_ch%d" % self.chan)
        rms = self.h_amp.GetRMS()
        if rms < 5:
            print "RMS = %g, skipping this file" % rms
            return
        #fitfn = ROOT.TF1("fn", twospa, 10, 200, 7)
        #maxval = self.h_amp.GetMaximum()
        #fitfn.SetParLimits(0, 0.01 * maxval, 10 * maxval)
        #fitfn.SetParName(0, "amp exp")
        #fitfn.SetParLimits(1, 40, 500)
        #fitfn.SetParName(1, "slope exp")
        #fitfn.SetParLimits(2, 40, 120) # SPA
        #fitfn.SetParName(2, "SPA")
        #fitfn.SetParLimits(3, 10, self.h_amp.GetMaximum()) # amp1pa
        #fitfn.SetParName(3, "amp 1PA")
        #fitfn.SetParLimits(4, 10, 40) # width1pa
        #fitfn.SetParName(4, "width 1PA")
        #fitfn.SetParLimits(5, 0.05, 0.3) # relamp2pa
        #fitfn.SetParName(5, "amp 2PA / 1 PA")
        #fitfn.SetParLimits(6, 10, 40) # width2pa
        #fitfn.SetParName(6, "width 2 PA")
        #fitfn.SetParameter(0, maxval) # amp exp
        #fitfn.SetParameter(1, 50) # slope exp
        #fitfn.SetParameter(2, 5.0) # SPA
        #fitfn.SetParameter(3, 200) # amp1pa
        #fitfn.SetParameter(4, 20) # width 1 PA
        #fitfn.SetParameter(5, 0.10) # amp2pa
        #fitfn.SetParameter(6, 20) # width 2 PA
        self.h_amp, self.SPA = fitspa.fit(self.h_amp)
        #self.h_amp.Fit(fitfn, "", "", 20, 400)
        #self.SPA = fitfn.GetParameter(2)
        fitfn = self.h_amp.GetFunction("fnSPA")
        self.dSPA = fitfn.GetParError(4)
        self.h_amp.Draw()
        canv.Update()
        #k = raw_input("Use this? [Y/n]\n")
        #if k != "":
        #    self.SPA = None

    def checkdark(self):
        if self.SPA is None:
            return
        fn = self.inp.GetName()
        fn = os.path.split(fn)[1].replace("calib_", "", 1)
        fn = os.path.join("/data/solid/sipmcalibration_bris/", fn)
        inp = ROOT.TFile(fn, "READ")
        tree = inp.Get("waveforms")
        sampletime = 25e-9
        totaltime = 0.0
        n0p5PA = 0
        n1p5PA = 0
        for event in tree:
            wf = [event.wf_chan0, event.wf_chan1, event.wf_chan2, event.wf_chan3,
                  event.wf_chan4, event.wf_chan5, event.wf_chan6, event.wf_chan7][self.chan]
            values = {}
            for val in wf:
                if val in values:
                    values[val] += 1
                else:
                    values[val] = 1
            maxval = None
            maxcount = None
            for val in values:
                n = values[val]
                if maxcount is None or n > maxcount:
                    maxcount = n
                    maxval = val
            ped = maxval
            totaltime += wf.size() * sampletime
            prev = (float(int(wf[0]) & 0x3fff) - ped) / self.SPA
            for val in wf[1:]:
                val = float(int(val) & 0x3fff) - ped
                val /= self.SPA
                if val > 0.5 and prev <= 0.5:
                    n0p5PA += 1
                if val > 1.5 and prev <= 1.5:
                    n1p5PA += 1
                prev = val
        inp.Close()
        self.DCR = n0p5PA / totaltime
        self.CT = (n1p5PA / totaltime) / self.DCR
        print "Channel %d, v = %g V, DCR = %g MHz, CT = %g" % (self.chan, self.voltage, self.DCR * 1e-6, self.CT)


chan = args.chan
temp = args.temp
vmin = 62.0
vmax = 68.0

ROOT.gStyle.SetOptStat(0)
canv = ROOT.TCanvas()
files = os.listdir("data")
#print files
vfiles = {}
for fn in files:
    if "%02.f" % temp in fn:
        voltage = float(fn.split("_")[2].replace("V", ""))
        if voltage >= vmin and voltage < vmax:
            vfiles[voltage] = ROOT.TFile(os.path.join("data", fn), "READ")
vcalibs = {}
calib = ChanCalibrations(chan)
voltages = vfiles.keys()
voltages.sort()
for v in voltages:
    cal = Calibration(v, temp, chan, vfiles[v])
    cal.getamps()
    #cal.fitSPA(canv)
    #cal.checkdark()
    vcalibs[v] = cal
    calib.add(cal)
canv.SetLogy()
calib.drawpeaks(canv)
for v in vcalibs:
    vcalibs[v].fitSPA(canv)
    vcalibs[v].checkdark()
canv.SetLogy(0)
voltages = vcalibs.keys()
voltages.sort()
x = array.array("d")
xerr = array.array("d")
ySPA = array.array("d")
ySPAerr = array.array("d")
yDCR = array.array("d")
yCT = array.array("d")
v0 = voltages[0]
for v in voltages:
    spa = vcalibs[v].SPA
    if spa is None:
        continue
    spaerr = vcalibs[v].dSPA
    dcr = vcalibs[v].DCR / 1e6
    ct = vcalibs[v].CT * 100.0
    if spa is not None:
        print "v = %g V, SPA = %g, DCR = %g MHz, CT = %g %%" % (v, spa, dcr, ct)
        x.append(v)
        xerr.append(0)
        ySPA.append(spa)
        ySPAerr.append(spaerr)
        yDCR.append(dcr)
        yCT.append(ct)
gSPA = ROOT.TGraphErrors(len(x), x, ySPA, xerr, ySPAerr)
gSPA.SetTitle("channel %d, T = %g C" % (chan, temp))
gSPA.GetXaxis().SetTitle("bias voltage [V]")
gSPA.GetYaxis().SetTitle("SPA [ADC count]")
gSPA.Draw("AL")
gSPA.Fit("pol1")
canv.Update()
canv.SaveAs("g_SPA_ch%d_%gC.png" % (chan, temp))
canv.SaveAs("g_SPA_ch%d_%gC.eps" % (chan, temp))
raw_input()

gDCR = ROOT.TGraph(len(x), x, yDCR)
gDCR.SetTitle("channel %d, T = %g C" % (chan, temp))
gDCR.GetXaxis().SetTitle("bias voltage [V]")
gDCR.GetYaxis().SetTitle("DCR [MHz]")
gDCR.Draw("AL")
canv.Update()
canv.SaveAs("g_DCR_ch%d_%gC.png" % (chan, temp))
canv.SaveAs("g_DCR_ch%d_%gC.eps" % (chan, temp))
raw_input()

gCT = ROOT.TGraph(len(x), x, yCT)
gCT.SetTitle("channel %d, T = %g C" % (chan, temp))
gCT.GetXaxis().SetTitle("bias voltage [V]")
gCT.GetYaxis().SetTitle("Cross talk [%]")
gCT.Draw("AL")
canv.Update()
canv.SaveAs("g_CT_ch%d_%gC.png" % (chan, temp))
canv.SaveAs("g_CT_ch%d_%gC.eps" % (chan, temp))
raw_input()

outp = ROOT.TFile("data/fit_ch%d_%02.fC.root", "RECREATE")

calibtree = ROOT.TTree("calibration", "calibration")
calibV = array.array("d", [-1])
calibT = array.array("d", [-1])
calibSPA = array.array("d", [-1])
calibDCR = array.array("d", [-1])
calibCT = array.array("d", [-1])
calibtree.Branch("voltage", calibV, "voltage/D")
calibtree.Branch("temp", calibT, "temp/D")
calibtree.Branch("SPA", calibSPA, "SPA/D")
calibtree.Branch("DCR", calibDCR, "DCR/D")
calibtree.Branch("CT", calibCT, "CT/D")
outp.cd()
for v in voltages:
    cal = vcalibs[v]
    if cal.SPA is None:
        continue
    cal.h_amp.Write()
    calibV[0] = v
    calibT[0] = args.temp
    calibSPA[0] = cal.SPA
    calibDCR[0] = cal.DCR
    calibCT[0] = cal.CT
    calibtree.Fill()
gCT.Write()
gDCR.Write()
gSPA.Write()
calibtree.Write()
outp.Close()



