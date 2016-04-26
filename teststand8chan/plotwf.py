import argparse
import array

import ROOT


def plotwf(wf, canv, nsaved=0, ped=True):
    x = array.array("d", range(wf.size()))
    y = array.array("d")
    values = {}
    for val in wf:
        val = float(int(val) & 0x3fff)
        y.append(val)
        if val in values:
            values[val] += 1
        else:
            values[val] = 1
    maxval = 0 
    if ped:
        maxcount = None
        for val in values:
            n = values[val]
            if maxcount is None or n > maxcount:
                maxcount = n
                maxval = val
        for i in range(len(y)):
            y[i] -= maxval
    pedline = ROOT.TLine(0, maxval, wf.size(), maxval)
    pedline.SetLineColor(ROOT.kBlue)
    print ped, maxval, y[:3], y[-3:], min(y), max(y)
    g = ROOT.TGraph(len(x), x, y)
    g.SetTitle("")
    g.GetXaxis().SetTitle("sample")
    g.GetYaxis().SetTitle("voltage [ADC count]")
    g.Draw("AL")
    #pedline.Draw()
    #ped2line.Draw()
    canv.Update()
    s = raw_input()
    if s == "s":
        canv.SaveAs("g_wf%d.png" % nsaved)
        canv.SaveAs("g_wf%d.eps" % nsaved)
        nsaved += 1
    return s
    

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("channel", type=int)
parser.add_argument("--noped", action="store_true")
args = parser.parse_args()

canv = ROOT.TCanvas()
inp = ROOT.TFile(args.filename)
h = inp.Get("h_val_wf_chan%d" % args.channel)
h.Draw()
ped = h.GetBinCenter(h.GetMaximumBin())
canv.Update()
x = raw_input("ped = %g" % ped)
if x != "":
    ped = float(x)

if args.noped:
    print "Not using a pedestal"
    ped = 0.0

nsaved = 0
tree = inp.Get("waveforms")
for event in tree:
    wfs = [event.wf_chan0, event.wf_chan1, event.wf_chan2, event.wf_chan3,
           event.wf_chan4, event.wf_chan5, event.wf_chan6, event.wf_chan7]
    wf = wfs[args.channel]
    s = plotwf(wf, canv, ped, nsaved)
    if s != "":
        if s == "s":
            nsaved += 1
        else:
            break
inp.Close()

