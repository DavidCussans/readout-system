import math

import ROOT

def doubleexp(vals, pars):
    x = vals[0]
    a0 = pars[0]
    slope0 = pars[1]
    a1 = pars[2]
    slope1 = pars[3]
    return a0 * math.exp(-x / slope0) + a1 * math.exp(-x / slope1)

def exp2SPA(vals, pars):
    #print list(pars)
    x = vals[0]
    a0 = pars[0]
    slope0 = pars[1]
    spa = pars[2]
    amp1pa = pars[3]
    width1pa = pars[4]
    amp2pa = pars[5] * amp1pa
    width2pa = pars[6]
    val = a0 * math.exp(-x / slope0)
    val += amp1pa * math.exp(-(x - spa)**2 / width1pa)
    val += amp2pa * math.exp(-(x - 2 * spa)**2 / width2pa)
    return val

def fit(hist, spamin=20.0, spamax=150.0):
    highval = 0
    for i in range(1, hist.GetNbinsX()):
        val = hist.GetBinContent(i)
        if val > 10:
            highval = hist.GetBinCenter(i)
    maxval = hist.GetMaximum()
    guessSPA = hist.GetBinCenter(hist.GetMaximumBin())
    #hist.Fit("expo", "", "", min(100, 0.5 * highval), max(200, highval))
    #hist.Draw()
    #raw_input()
    #expo = hist.GetFunction("expo")
    #amp = expo.GetParameter(0)
    #slope = -1 / expo.GetParameter(1)
    #fndoubleexp = ROOT.TF1("doubleexp", doubleexp, 5, 400, 4)
    #fndoubleexp.SetParName(0, "amp0")
    #fndoubleexp.SetParLimits(0, 0.0, 10 * maxval)
    #fndoubleexp.SetParameter(0, maxval)
    #fndoubleexp.SetParName(1, "slope0")
    #fndoubleexp.SetParLimits(1, 1.0, 10.0)
    #fndoubleexp.SetParameter(1, 3.0)
    #fndoubleexp.SetParName(2, "amp1")
    #fndoubleexp.SetParLimits(2, 0.0, maxval)
    #fndoubleexp.SetParameter(2, maxval)
    #fndoubleexp.SetParName(3, "slope1")
    #fndoubleexp.SetParLimits(3, 10.0, 100.0)
    #fndoubleexp.SetParameter(3, 50.0)
    #hist.Fit(fndoubleexp, "", "", 0, 500)
    #amp0 = fndoubleexp.GetParameter(0)
    #slope0 = fndoubleexp.GetParameter(1)
    #amp1 = fndoubleexp.GetParameter(2)
    #slope1 = fndoubleexp.GetParameter(3)
    fnexpspa = ROOT.TF1("fnSPA", exp2SPA, 5, 400, 7)
    fnexpspa.SetParName(0, "amp0")
    fnexpspa.SetParLimits(0, 0.5 * maxval, 10.0 * maxval)
    fnexpspa.SetParameter(0, 3 * maxval)
    fnexpspa.SetParName(1, "slope0")
    fnexpspa.SetParLimits(1, 10.0, 50.0)
    fnexpspa.SetParameter(1, 20.0)
    fnexpspa.SetParName(2, "SPA")
    fnexpspa.SetParLimits(2, spamin, spamax)
    fnexpspa.SetParameter(2, guessSPA)
    fnexpspa.SetParName(3, "amp1PA")
    fnexpspa.SetParLimits(3, 1e3, maxval)
    fnexpspa.SetParameter(3, 0.1 * maxval)
    fnexpspa.SetParName(4, "width1PA")
    fnexpspa.SetParLimits(4, 10.0, 200.0)
    fnexpspa.SetParameter(4, 50.0)
    fnexpspa.SetParName(5, "relamp2PA")
    fnexpspa.SetParLimits(5, 0.01, 0.5)
    fnexpspa.SetParameter(5, 0.1)
    fnexpspa.SetParName(6, "width2PA")
    fnexpspa.SetParLimits(6, 30.0, 200.0)
    fnexpspa.SetParameter(6, 50.0)
    hist.Fit(fnexpspa, "", "", 0.7 * guessSPA, highval)
    spa = fnexpspa.GetParameter(2)
    return hist, spa

if __name__ == "__main__":
    canv = ROOT.TCanvas()
    canv.SetLogy()
    inp = ROOT.TFile("data/calib_sipmcalib_64.20V_25.00C_23Feb2016_2042.root", "READ")
    h = inp.Get("h_amp_ch2")
    h, SPA = fit(h)
    print "SPA = %g" % SPA
    h.Draw()
    canv.Update()
    raw_input()

    inp.Close()

