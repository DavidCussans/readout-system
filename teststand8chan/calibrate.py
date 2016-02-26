import argparse
import os.path

import ROOT

def findpeaks(h, wf, ped):
    prevprev = None
    prev = None
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
    for val in wf:
        if prevprev is not None and prev is not None:
            if prev > prevprev and prev < val:
                h.Fill(prev - ped)
        prevprev = prev
        prev = val

parser = argparse.ArgumentParser()
parser.add_argument("fn", nargs="*")
args = parser.parse_args()

ROOT.gROOT.SetBatch()

for fn in args.fn:
    outpfn = os.path.split(fn)[1]
    outpfn = os.path.join("data", "calib_" + outpfn)
    print "Processing %s -> %s" % (fn, outpfn)
    if os.path.exists(outpfn):
        print "Skipping %s, already exists." % outpfn
        continue
    peaks = []
    nchan = 8
    for i in range(nchan):
        h = ROOT.TH1D("h_amp_ch%d" % i, "channel %d" % i, 560, -10, 550)
        h.SetXTitle("peak amplitude [ADC count]")
        h.SetYTitle("peaks")
        peaks.append(h)

    peds = []
    inp = ROOT.TFile(fn, "READ")
    #inp.ls()
    badfile = False
    for i in range(nchan):
        name = "h_val_wf_chan%d" % i
        #print name
        h = inp.Get(name)
        if not h.__class__ == ROOT.TH1I:
            print "Bad histo: ", h, h.__class__
            badfile = True
            break
        peds.append(h.GetBinCenter(h.GetMaximumBin()))
    if badfile:
        print "Skipping event with bad file: %s" % fn
        inp.Close()
        continue

    #print "peaks histos: ", peaks
    tree = inp.Get("waveforms")
    for event in tree:
        wfs = [event.wf_chan0, event.wf_chan1, event.wf_chan2, event.wf_chan3,
               event.wf_chan4, event.wf_chan5, event.wf_chan6, event.wf_chan7]
        for i in range(nchan):
            findpeaks(peaks[i], wfs[i], peds[i])
    inp.Close()

    outp = ROOT.TFile(outpfn, "RECREATE")
    outp.cd()
    canv = ROOT.TCanvas()
    canv.SetLogy()
    for h in peaks:
        h.Write()
        #h.Draw()
        #canv.Draw()
        #canv.Update()
        #canv.SaveAs("imgs/g_%s_%s" % (h.GetName(), fn.replace("data/", "").replace(".root", ".png")))
    outp.Close()
