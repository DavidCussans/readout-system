import argparse
import array
import json
import os

import ROOT

import fitraw

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--temp", type=float, default=25.0)
parser.add_argument("-d", "--draw", action="store_true")
parser.add_argument("--spafile", action="store_true")
parser.add_argument("--ratefile", action="store_true")
parser.add_argument("-r", "--rates", action="store_true")
args = parser.parse_args()

inp = open("out_breakdown_%gC.json" % args.temp, "r")
breakdowndata = json.load(inp)
vbrs = breakdowndata["vbr"]
mvbr = sum(vbrs) / float(len(vbrs))
#mvbr += 0.06 * (args.temp - 25.0)
inp.close()


minbias = mvbr + 1.5
maxbias = mvbr + 2.7
print "Using voltage scan in range %g < v_bias < %g V" % (minbias, maxbias)

basedir = "/data/solid/sipmcalibration_bris/good/"
allfiles = os.listdir(basedir)
temp = "%0.2fC" % args.temp
filelist = {}
for fn in allfiles:
    if not fn.startswith("sipmcalib"):
        continue
    fnparts = fn.split("_")
    if fnparts[2] != temp:
        continue
    vbias = float(fnparts[1].replace("V", ""))
    if vbias < minbias or vbias > maxbias:
        continue
    print fn
    filelist[vbias] = os.path.join(basedir, fn)
voltages = filelist.keys()
voltages.sort()
l = ""
spas = {}
canv = ROOT.TCanvas()
canv.SetLogy()
if args.spafile: 
    fn = "out_fitscan_%gC.json" % args.temp
    inp = open(fn, "r")
    spas = json.load(inp)
    inp.close()
    print spas
    keys = spas.keys()
    keys.sort()
    for key in keys:
        print key, spas[key]
        spas[float(key)] = spas[key]
else:   # no spa file given, calculate from scratch
    for v in voltages:
        l += "%g V: %s\n" % (v, filelist[v])
        inp = ROOT.TFile(filelist[v], "READ")
        spavals = []
        spaerrs = []
        for chan in range(8):
            h = inp.Get("h_val_wf_chan%d" % chan)
            h, spa, spaerr = fitraw.fit(h)
            h.Draw()
            canv.Update()
            msg = "chan %d, v = %g V, spa = %g +- %g" % (chan, v, spa, spaerr)
            if args.draw:
                raw_input(msg)
            else:
                print msg
            spavals.append(spa)
            spaerrs.append(spaerr)
        spas[v] = [spavals, spaerrs]
        inp.Close()

    outp = open("out_fitscan_%gC.json" % args.temp, "w")
    json.dump(spas, outp)
    outp.close()
    # Make graphs

    canv.SetLogy(0)
    outp = ROOT.TFile("outp_fitscan_%gC.root" % args.temp, "RECREATE")
    for chan in range(8):
        x = array.array("d")
        xerr = array.array("d")
        y = array.array("d")
        yerr = array.array("d")
        vbr = vbrs[chan]
        for v in voltages:
            ov = v - vbr
            overr = 0.05
            spa = spas[v][0][chan]
            spaerr = spas[v][1][chan]
            x.append(ov)
            xerr.append(overr)
            y.append(spa)
            yerr.append(spaerr)
        g = ROOT.TGraphErrors(len(x), x, y, xerr, yerr)
        g.SetName("g_spa_chan%d" % chan)
        g.SetTitle("Channel %d" % chan)
        g.GetXaxis().SetTitle("over voltage [V]")
        g.GetYaxis().SetTitle("1 PA [ADC count]")
        #g.Fit("pol1")
        g.Draw("AL")
        canv.Update()
        raw_input()
        g.Write()
    outp.Close()

vrates = {}
thresholds = [0.5, 1.5, 2.5, 3.5, 4.5]
nthr = len(thresholds)
if args.ratefile:
    fn = "out_fitrates_%gC.json" % args.temp
    inp = open(fn, "r")
    vrates = json.load(inp)
    vkeys = vrates.keys()
    for v in vkeys:
        vrates[float(v)] = vrates[v]
    inp.close()
else:
    vrates = {}
    for v in voltages:
        chanspas = spas[v][0]
        nevt = 0
        chan0rates = []
        chan1rates = []
        chan2rates = []
        chan3rates = []
        chan4rates = []
        chan5rates = []
        chan6rates = []
        chan7rates = []
        rates = [chan0rates, chan1rates, chan2rates, chan3rates,
                 chan4rates, chan5rates, chan6rates, chan7rates]
        for thr in thresholds:
            for chan in range(8):
                rates[chan].append(0)
        fn = filelist[v]
        inp = ROOT.TFile(fn, "READ")
        peds = []
        for chan in range(8):
            h = inp.Get("h_val_wf_chan%d" % chan)
            peds.append(h.GetBinCenter(h.GetMaximumBin()))
        tree = inp.Get("waveforms")
        nsample = None
        for event in tree:
            nevt += 1
            wf0 = event.wf_chan0
            wf1 = event.wf_chan1
            wf2 = event.wf_chan2
            wf3 = event.wf_chan3
            wf4 = event.wf_chan4
            wf5 = event.wf_chan5
            wf6 = event.wf_chan6
            wf7 = event.wf_chan7
            wfs = [wf0, wf1, wf2, wf3, wf4, wf5, wf6, wf7]
            for chan in range(8):
                ped = peds[chan]
                spa = chanspas[chan]
                wf = wfs[chan]
                if nsample is None:
                    nsample = len(wf)
                prev = wf[0] - ped
                for i in range(1, len(wf)):
                    val = wf[i] - ped
                    for j in range(nthr):
                        thr = thresholds[j] * spa
                        if val >= thr and prev < thr:
                            rates[chan][j] += 1
                    prev = val
        # Scale number of signals into rate
        print "over voltage = %g V" % (v - mvbr)
        for chan in range(8):
            msg = "Chan %d: " % chan
            for i in range(nthr):
                rates[chan][i] /= nevt * nsample / 40e6
                msg += "%g Hz > %g PA, " % (rates[chan][i], thresholds[i])
            print msg
        vrates[v] = rates
        inp.Close()
    outp = open("out_fitrates_%gC.json" % args.temp, "w")
    json.dump(vrates, outp)
    outp.close()

chancolours = [ROOT.kBlack, ROOT.kRed, ROOT.kGreen + 1, ROOT.kBlue, 
               ROOT.kGray, ROOT.kAzure, ROOT.kCyan, ROOT.kMagenta]
ratestyles = [20, 21, 22, 23, 29, 30, 33, 34]
# plot rates and cross talk

# plot rates at different thresholds for single temperature, different voltages
canv.SetLogy(0)
allgraphs = []
allmin = None
allmax = None
minv = None
maxv = None
leg = None
for chan in range(8):
    leg = ROOT.TLegend(0.8, 0.8, 0.95, 0.95)
    graphs = []
    x = array.array("d")
    ys = []
    minrate = None
    maxrate = None
    for ithr in range(nthr):
        ys.append(array.array("d"))
    for v in voltages:
        spa = spas[v][0][chan]
        if spa < 0:
            print "Skipping v = %g since spa = %g" % (v, spa)
            continue
        vbr = vbrs[chan]
        ov = v - vbr
        if minv is None or ov < minv:
            minv = ov
        if maxv is None or ov > maxv:
            maxv = ov
        x.append(ov)
        rates = vrates[v][chan]
        for ithr in range(nthr):
            thr = thresholds[ithr]
            rate = rates[ithr] * 1e-3
            if minrate is None or rate < minrate:
                minrate = rate
            if maxrate is None or rate > maxrate:
                maxrate = rate
            ys[ithr].append(rate)
    for ithr in range(nthr):
        g = ROOT.TGraph(len(x), x, ys[ithr])
        g.SetName("g_ch%d_th%d" % (chan, ithr))
        g.SetTitle("")
        g.SetMarkerStyle(ratestyles[ithr])
        g.SetMarkerColor(chancolours[chan])
        g.SetLineColor(chancolours[chan])
        g.GetXaxis().SetTitle("over voltage [V]")
        g.GetYaxis().SetTitle("rate [kHz]")
        #g.Draw("AP")
        leg.AddEntry(g, "amp > %g PA" % thresholds[ithr], "P")
        graphs.append(g)
        #canv.Update()
        #raw_input()
    gfake = ROOT.TGraph(2, array.array("d", [x[0], x[-1]]), array.array("d", [minrate, maxrate]))
    gfake.SetMarkerColor(0)
    gfake.SetTitle("")
    gfake.GetXaxis().SetTitle("over voltage [V]")
    gfake.GetYaxis().SetTitle("rate [kHz]")
    gfake.Draw("AP")
    for g in graphs:
        g.Draw("P")
    leg.Draw()
    canv.Update()
    raw_input()
    allgraphs.extend(graphs)
    if allmin is None or minrate < allmin:
        allmin = minrate
    if allmax is None or maxrate > allmax:
        allmax = maxrate
fakex = array.array("d", [minv, maxv])
fakey = array.array("d", [allmin, allmax])
gfake = ROOT.TGraph(2, fakex, fakey)
gfake.SetTitle("temperature = %g C" % args.temp)
gfake.GetXaxis().SetTitle("over voltage [V]")
gfake.GetYaxis().SetTitle("rate [kHz]")
gfake.Draw("AP")
for g in allgraphs:
    g.Draw("LP")
leg.Draw()
canv.Update()
canv.SaveAs("g_rates_%gC_all.eps" % args.temp)
canv.SaveAs("g_rates_%gC_all.png" % args.temp)
raw_input()
