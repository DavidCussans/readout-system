import math

import ROOT

def doubleexp(vals, pars):
    x = vals[0]
    a0 = pars[0]
    slope0 = pars[1]
    a1 = pars[2]
    slope1 = pars[3]
    return a0 * math.exp(-x / slope0) + a1 * math.exp(-x / slope1)

def doubleexp2SPA(vals, pars):
    #print list(pars)
    x = vals[0]
    a0 = pars[0]
    slope0 = pars[1]
    a1 = pars[2]
    slope1 = pars[3]
    spa = pars[4]
    amp1pa = pars[5]
    width1pa = pars[6]
    amp2pa = pars[7] * amp1pa
    width2pa = pars[8]
    val = a0 * math.exp(-x / slope0) + a1 * math.exp(-x / slope1)
    val += amp1pa * math.exp(-(x - spa)**2 / width1pa)
    val += amp2pa * math.exp(-(x - 2 * spa)**2 / width2pa)
    return val

def fit(hist):
    maxval = hist.GetMaximum()
    fndoubleexp = ROOT.TF1("doubleexp", doubleexp, 5, 400, 4)
    fndoubleexp.SetParName(0, "amp0")
    fndoubleexp.SetParLimits(0, 0.0, 10 * maxval)
    fndoubleexp.SetParameter(0, maxval)
    fndoubleexp.SetParName(1, "slope0")
    fndoubleexp.SetParLimits(1, 1.0, 10.0)
    fndoubleexp.SetParameter(1, 3.0)
    fndoubleexp.SetParName(2, "amp1")
    fndoubleexp.SetParLimits(2, 0.0, maxval)
    fndoubleexp.SetParameter(2, maxval)
    fndoubleexp.SetParName(3, "slope1")
    fndoubleexp.SetParLimits(3, 10.0, 100.0)
    fndoubleexp.SetParameter(3, 50.0)
    hist.Fit(fndoubleexp, "", "", 0, 500)
    amp0 = fndoubleexp.GetParameter(0)
    slope0 = fndoubleexp.GetParameter(1)
    amp1 = fndoubleexp.GetParameter(2)
    slope1 = fndoubleexp.GetParameter(3)
    fndoubleexpspa = ROOT.TF1("fnSPA", doubleexp2SPA, 5, 400, 9)
    fndoubleexpspa.SetParName(0, "amp0")
    fndoubleexpspa.FixParameter(0, amp0)
    fndoubleexpspa.SetParName(1, "slope0")
    fndoubleexpspa.FixParameter(1, slope0)
    fndoubleexpspa.SetParName(2, "amp1")
    fndoubleexpspa.SetParLimits(2, 0.5 * amp1, amp1)
    fndoubleexpspa.SetParameter(2, 0.8 * amp1)
    fndoubleexpspa.SetParName(3, "slope1")
    fndoubleexpspa.SetParLimits(3, 0.7 * slope1, 1.3 * slope1)
    fndoubleexpspa.SetParameter(3, slope1)
    fndoubleexpspa.SetParName(4, "SPA")
    fndoubleexpspa.SetParLimits(4, 20.0, 150.0)
    fndoubleexpspa.SetParameter(4, 80.0)
    fndoubleexpspa.SetParName(5, "amp1PA")
    fndoubleexpspa.SetParLimits(5, 1e3, maxval)
    fndoubleexpspa.SetParameter(5, 0.1 * maxval)
    fndoubleexpspa.SetParName(6, "width1PA")
    fndoubleexpspa.SetParLimits(6, 10.0, 200.0)
    fndoubleexpspa.SetParameter(6, 50.0)
    fndoubleexpspa.SetParName(7, "relamp2PA")
    fndoubleexpspa.SetParLimits(7, 0.01, 0.5)
    fndoubleexpspa.SetParameter(7, 0.1)
    fndoubleexpspa.SetParName(8, "width2PA")
    fndoubleexpspa.SetParLimits(8, 10.0, 200.0)
    fndoubleexpspa.SetParameter(8, 50.0)
    hist.Fit(fndoubleexpspa, "", "", 0, 500)
    spa = fndoubleexpspa.GetParameter(4)
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

