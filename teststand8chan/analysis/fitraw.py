import argparse
import math

import ROOT

def guessspa(h, amp, mean, width):
    hnew = h.Clone("hnew")
    for i in range(1, hnew.GetNbinsX()):
        val = h.GetBinContent(i)
        center = h.GetBinCenter(i)
        if center > mean + width:
            val -= amp * math.exp(- (center - mean)**2 / 2.0 / width**2)
            hnew.SetBinContent(i, val)
        else:
            hnew.SetBinContent(i, 0)
    #c = ROOT.TCanvas()
    #c.SetLogy()
    #hnew.Draw()
    #c.Update()
    #raw_input()
    spa = hnew.GetBinCenter(hnew.GetMaximumBin())
    spa -= mean
    return spa

def findrange(h):
    minval = None
    maxval = None
    nbins = h.GetNbinsX()
    for i in range(1, nbins):
        val = h.GetBinContent(i)
        if val > 0:
            maxval = h.GetBinCenter(min(i + 10, nbins))
            if minval is None:
                minval = h.GetBinCenter(max(0, i - 10))
    return minval, maxval


def gausExp(vals, pars):
    x = vals[0]
    gausamp = pars[0]
    gausmean = pars[1]
    gaussigma = pars[2]
    expamp = pars[3]
    expslope = pars[4]
    x -= gausmean
    val = gausamp * math.exp(-x**2 / gaussigma**2)
    if x > 0:
        val += expamp * math.exp(-x / expslope)
    return val


def fitGausExp(h, gausfn, rangemin, rangemax):
    amp = gausfn.GetParameter(0)
    mean = gausfn.GetParameter(1)
    sigma = gausfn.GetParameter(2)
    fn = ROOT.TF1("gausExp", gausExp, 0, 2**14, 5)
    fn.SetParName(0, "gaus amp")
    fn.FixParameter(0, amp)
    fn.SetParName(1, "gaus mean")
    fn.FixParameter(1, mean)
    fn.SetParName(2, "gaus sigma")
    fn.FixParameter(2, sigma)
    fn.SetParName(3, "exp amp")
    fn.SetParName(4, "exp slope")
    fn.SetParLimits(4, 10, 100)
    fn.SetParameter(4, 50)
    h.Fit(fn, "", "", rangemin, rangemax)
    return h

def gausExp1PA(vals, pars):
    x = vals[0]
    gausamp = pars[0]
    gausmean = pars[1]
    gaussigma = pars[2]
    expamp = pars[3]
    expslope = pars[4]
    spa = pars[5]
    amp1pa = pars[6]
    width1pa = pars[7]
    x -= gausmean
    val = gausamp * math.exp(-x**2 / 2.0 / gaussigma**2)
    if x > 0:
        val += expamp * math.exp(-x / expslope)
        val += amp1pa * math.exp(-(x - spa)**2 / width1pa**2)
    return val

def fitGausExp1PA(h, gausexpfn, rangemin, rangemax):
    gausamp = gausexpfn.GetParameter(0)
    gausmean = gausexpfn.GetParameter(1)
    gaussigma = gausexpfn.GetParameter(2)
    #expamp = gausexpfn.GetParameter(3)
    #expslope = gausexpfn.GetParameter(4)
    fn = ROOT.TF1("gausExp1PA", gausExp1PA, 0, 2**14, 8)
    fn.SetParName(0, "gaus amp")
    fn.FixParameter(0, gausamp)
    fn.SetParName(1, "gaus mean")
    fn.FixParameter(1, gausmean)
    fn.SetParName(2, "gaus sigma")
    fn.FixParameter(2, gaussigma)
    fn.SetParName(3, "exp amp")
    #fn.SetParLimits(3, 0.75 * expamp, 0.9*expamp)
    #fn.SetParameter(3, 0.8 * expamp)
    fn.SetParName(4, "exp slope")
    fn.SetParLimits(4, 10, 100)
    fn.SetParameter(4, 50)
    fn.SetParName(5, "SPA")
    fn.SetParLimits(5, 20, 150)
    fn.SetParameter(5, 50)
    fn.SetParName(6, "amp 1 PA")
    fn.SetParLimits(6, 0.001 * gausamp, 0.25 * gausamp)
    fn.SetParameter(6, 0.1 * gausamp)
    fn.SetParName(7, "width 1 PA")
    fn.SetParLimits(7, 10, 100)
    fn.SetParameter(7, 50)
    h.Fit(fn, "", "", rangemin, rangemax)
    return h

def gausExp2PA(vals, pars):
    x = vals[0]
    gausamp = pars[0]
    gausmean = pars[1]
    gaussigma = pars[2]
    expamp = pars[3]
    expslope = pars[4]
    spa = pars[5]
    amp1pa = pars[6]
    width1pa = pars[7]
    amp2pa = pars[8] * amp1pa
    width2pa = pars[9]
    x -= gausmean
    val = gausamp * math.exp(-x**2 / 2.0 / gaussigma**2)
    if x > 0:
        val += expamp * math.exp(-x / expslope)
        val += amp1pa * math.exp(-(x - spa)**2 / width1pa**2)
        val += amp2pa * math.exp(-(x - 2 * spa)**2 / width2pa**2)
    return val

def fitGausExp2PA(h, gausexpfn, spaguess, rangemin, rangemax):
    gausamp = gausexpfn.GetParameter(0)
    gausmean = gausexpfn.GetParameter(1)
    gaussigma = gausexpfn.GetParameter(2)
    #expamp = gausexpfn.GetParameter(3)
    #expslope = gausexpfn.GetParameter(4)
    fn = ROOT.TF1("gausExp2PA", gausExp2PA, 0, 2**14, 10)
    fn.SetParName(0, "gaus amp")
    fn.FixParameter(0, gausamp)
    fn.SetParName(1, "gaus mean")
    fn.FixParameter(1, gausmean)
    fn.SetParName(2, "gaus sigma")
    fn.FixParameter(2, gaussigma)
    fn.SetParName(3, "exp amp")
    #fn.SetParLimits(3, 0.75 * expamp, 0.9*expamp)
    #fn.SetParameter(3, 0.8 * expamp)
    fn.SetParName(4, "exp slope")
    fn.SetParLimits(4, 10, 100)
    fn.SetParameter(4, 50)
    fn.SetParName(5, "SPA")
    fn.SetParLimits(5, 0.7 * spaguess, 1.3 * spaguess)
    fn.SetParameter(5, spaguess)
    fn.SetParName(6, "amp 1 PA")
    fn.SetParLimits(6, 0.001 * gausamp, 0.25 * gausamp)
    fn.SetParameter(6, 0.1 * gausamp)
    fn.SetParName(7, "width 1 PA")
    fn.SetParLimits(7, 5, 20)
    fn.SetParameter(7, 10)
    fn.SetParName(8, "rel amp 2 PA")
    fn.SetParLimits(8, 0.01, 0.2)
    fn.SetParameter(8, 0.1)
    fn.SetParName(9, "width 2 PA")
    fn.SetParLimits(9, 5, 20)
    fn.SetParameter(9, 15)
    h.Fit(fn, "", "", rangemin, rangemax)
    return h

def gausExp3PA(vals, pars):
    x = vals[0]
    gausamp = pars[0]
    gausmean = pars[1]
    gaussigma = pars[2]
    expamp = pars[3]
    expslope = pars[4]
    spa = pars[5]
    amp1pa = pars[6]
    width1pa = pars[7]
    amp2pa = pars[8] * amp1pa
    width2pa = pars[9]
    amp3pa = pars[10] * amp1pa
    width3pa = pars[11]
    x -= gausmean
    val = gausamp * math.exp(-x**2 / 2.0 / gaussigma**2)
    if x > 0:
        val += expamp * math.exp(-x / expslope)
        val += amp1pa * math.exp(-(x - spa)**2 / width1pa**2)
        val += amp2pa * math.exp(-(x - 2 * spa)**2 / width2pa**2)
        val += amp3pa * math.exp(-(x - 3 * spa)**2 / width3pa**2)
    return val

def fitGausExp3PA(h, gausexp1pafn, rangemin, rangemax):
    gausamp = gausexp1pafn.GetParameter(0)
    gausmean = gausexp1pafn.GetParameter(1)
    gaussigma = gausexp1pafn.GetParameter(2)
    expamp = gausexp1pafn.GetParameter(3)
    expslope = gausexp1pafn.GetParameter(4)
    spa = gausexp1pafn.GetParameter(5)
    amp1pa = gausexp1pafn.GetParameter(6)
    width1pa = gausexp1pafn.GetParameter(7)
    fn = ROOT.TF1("gausExp3PA", gausExp3PA, 0, 2**14, 12)
    fn.SetParName(0, "gaus amp")
    fn.FixParameter(0, gausamp)
    fn.SetParName(1, "gaus mean")
    fn.FixParameter(1, gausmean)
    fn.SetParName(2, "gaus sigma")
    fn.FixParameter(2, gaussigma)
    fn.SetParName(3, "exp amp")
    fn.SetParLimits(3, 0.7 * expamp, 0.95 * expamp)
    fn.SetParameter(3, 0.9 * expamp)
    fn.SetParName(4, "exp slope")
    fn.FixParameter(4, expslope)
    fn.SetParName(5, "SPA")
    fn.SetParLimits(5, 0.8 * spa, 1.2 * spa)
    fn.SetParameter(5, spa)
    fn.SetParName(6, "amp 1 PA")
    fn.SetParLimits(6, 0.8 * amp1pa, 1.2 * amp1pa)
    fn.SetParameter(6, amp1pa)
    fn.SetParName(7, "width 1 PA")
    fn.SetParLimits(7, 0.8 * width1pa, 1.2 * width1pa)
    fn.SetParameter(7, width1pa)
    fn.SetParName(8, "rel amp 2 PA")
    fn.SetParLimits(8, 0.1, 0.75)
    fn.SetParameter(8, 0.1)
    fn.SetParName(9, "width 2 PA")
    fn.SetParLimits(9, 50, 150)
    fn.SetParameter(9, 75.0)
    fn.SetParName(10, "rel amp 3 PA")
    fn.SetParLimits(10, 0.01, 0.2)
    fn.SetParameter(10, 0.05)
    fn.SetParName(11, "width 3 PA")
    fn.SetParLimits(11, 50, 150)
    fn.SetParameter(11, 75.0)
    h.Fit(fn, "", "", rangemin, rangemax)
    return h

def fit(h):
    minrange, maxrange = findrange(h)
    h.GetXaxis().SetRangeUser(minrange, maxrange)
    ped = h.GetBinCenter(h.GetMaximumBin())
    h.Fit("gaus", "", "", ped - 10, ped + 10)
    gfn = h.GetFunction("gaus")
    amp = gfn.GetParameter(0)
    ped = gfn.GetParameter(1)
    width = gfn.GetParameter(2)
    spa = guessspa(h, amp, ped, width)
    fitGausExp2PA(h, gfn, spa, minrange, maxrange)
    fn = h.GetFunction("gausExp2PA")
    spa_fit= fn.GetParameter(5)
    spa_fit_err = fn.GetParError(5)
    return h, spa_fit, spa_fit_err

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fn", default="/data/solid/sipmcalibration_bris/good/sipmcalib_63.80V_20.00C_23Feb2016_2127.root")
    args = parser.parse_args()

    inp = ROOT.TFile(args.fn, "READ")

    canv = ROOT.TCanvas()
    canv.SetLogy()
    h = inp.Get("h_val_wf_chan2")
    minrange, maxrange = findrange(h)
    h.GetXaxis().SetRangeUser(minrange, maxrange)
    ped = h.GetBinCenter(h.GetMaximumBin())
    print "max val at %g" % ped
    h.Fit("gaus", "", "", ped - 10, ped + 10)
    h.Draw()
    canv.Update()
    raw_input()
    gfn = h.GetFunction("gaus")
    amp = gfn.GetParameter(0)
    ped = gfn.GetParameter(1)
    width = gfn.GetParameter(2)
    spa = guessspa(h, amp, ped, width)
    print "ped = %g, spa = %g" % (ped, spa)

    #fitGausExp(h, gfn, minrange, maxrange)
    #h.Draw()
    #canv.Update()
    #raw_input()
    #gefn = h.GetFunction("gausExp")
    fitGausExp2PA(h, gfn, spa, minrange, maxrange)
    h.Draw()
    canv.Update()
    raw_input()

    """
    ge1pafn = h.GetFunction("gausExp1PA")
    fitGausExp3PA(h, ge1pafn, minrange, maxrange)
    h.Draw()
    canv.Update()
    raw_input()
    """

    inp.Close()
