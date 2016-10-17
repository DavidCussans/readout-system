import argparse
import array

import ROOT


def plotwf(wfs, canv, nsaved=0):
    maxamp = None
    minamp = None
    print wfs
    first = True
    graphs = []
    for chan in wfs:
        wf = wfs[chan]
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
        maxy = max(y)
        miny = min(y)
        if maxamp is None or maxy > maxamp:
            maxamp = maxy
        if minamp is None or miny < minamp:
            minamp = miny
        maxval = 0 
        g = ROOT.TGraph(len(x), x, y)
        g.SetTitle("")
        g.GetXaxis().SetTitle("sample")
        g.GetYaxis().SetTitle("voltage [ADC count]")
        g.SetLineColor(colours[chan])
        graphs.append(g)
    xfake = array.array("f", [0, 2048])
    yfake = array.array("f", [minamp - 5, maxamp + 5])
    gfake = ROOT.TGraph(2, xfake, yfake)
    gfake.SetMarkerColor(0)
    gfake.Draw("AP")
    for g in graphs:
        g.Draw("L")
    #pedline.Draw()
    #ped2line.Draw()
    canv.Update()
    s = raw_input()
    if s == "s":
        canv.SaveAs("g_wf%d.png" % nsaved)
        canv.SaveAs("g_wf%d.eps" % nsaved)
        nsaved += 1
    return s
    

colours = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen + 3,
           ROOT.kOrange+10, ROOT.kViolet, ROOT.kGray, ROOT.kCyan + 2]

parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("-c", "--channel", type=int, action="append")
#parser.add_argument("--noped", action="store_true")
args = parser.parse_args()

canv = ROOT.TCanvas()
inp = ROOT.TFile(args.filename)
#h = inp.Get("h_val_wf_chan%d" % args.channel)
#h.Draw()
#ped = h.GetBinCenter(h.GetMaximumBin())
#canv.Update()
#x = raw_input("ped = %g" % ped)
#if x != "":
#    ped = float(x)
#
#if args.noped:
#    print "Not using a pedestal"
#    ped = 0.0

nsaved = 0
tree = inp.Get("waveforms")
for event in tree:
    wfs = {
        0: event.wf_chan0,
        1: event.wf_chan1,
        2: event.wf_chan2,
        3: event.wf_chan3,
        4: event.wf_chan4,
        5: event.wf_chan5,
        6: event.wf_chan6,
        7: event.wf_chan7
    }
    todraw = {}
    for chan in args.channel:
        todraw[chan] = wfs[chan]
    s = plotwf(todraw, canv, nsaved)
    if s != "":
        if s == "s":
            nsaved += 1
        else:
            break
inp.Close()

