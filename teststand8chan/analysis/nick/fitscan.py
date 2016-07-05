import argparse
import array
import json
import os

import ROOT

import fitraw

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--temp", type=float, default=25.0)
parser.add_argument("--date")
parser.add_argument("-d", "--draw", action="store_true")
parser.add_argument("--spafile", action="store_true")
parser.add_argument("--ratefile", action="store_true")
args = parser.parse_args()

fn = "outp/out_breakdown_%gC.json" % args.temp
if args.date is not None:
    fn = fn.replace(".json", "_%s.json" % args.date)
inp = open(fn, "r")
breakdowndata = json.load(inp)
vbrs = breakdowndata["vbr"]
mvbr = sum(vbrs) / float(len(vbrs))
#mvbr += 0.06 * (args.temp - 25.0)
inp.close()


minbias = mvbr + 0.5
maxbias = mvbr + 2.7
print "Using voltage scan in range %g < v_bias < %g V" % (minbias, maxbias)

basedir = "/data/solid/sipmcalibration_bris/good/"
allfiles = os.listdir(basedir)
temp = "%0.2fC" % args.temp
filelist = {}
for fn in allfiles:
    if not fn.startswith("sipmcalib"):
        continue
    if args.date is not None:
        if args.date not in fn:
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
    fn = "outp/out_fitscan_%gC.json" % args.temp
    if args.date is not None:
        fn = fn.replace(".json", "_%s.json" % args.date)
    inp = open(fn, "r")
    spas = json.load(inp)
    inp.close()
    print spas
    keys = spas.keys()
    keys.sort()
    fkeys = []
    for key in keys:
        print key, spas[key]
        spas[float(key)] = spas[key]
        fkeys.append(float(key))
    voltages = fkeys
else:   # no spa file given, calculate from scratch
    for v in voltages:
        l += "%g V: %s\n" % (v, filelist[v])
        inp = ROOT.TFile(filelist[v], "READ")
        keys = inp.GetListOfKeys()
        if keys.GetSize() < 11:
            inp.Close()
            continue
        inp.ls()
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
    voltages = spas.keys()
    voltages.sort()

    outfn = "outp/out_fitscan_%gC.json" % args.temp
    if args.date is not None:
        outfn = outfn.replace(".json", "_%s.json" % args.date)
    outp = open(outfn, "w")
    json.dump(spas, outp, indent=4)
    outp.close()
    # Make graphs

    canv.SetLogy(0)
    outp = ROOT.TFile("outp/outp_fitscan_%gC.root" % args.temp, "RECREATE")
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
        if args.draw:
            raw_input()
        g.Write()
    outp.Close()

ROOT.kBrown = 28
chancolours = [ROOT.kBlack, ROOT.kRed, ROOT.kGreen + 1, ROOT.kBlue, 
               ROOT.kGray, ROOT.kBrown, ROOT.kCyan, ROOT.kMagenta]
ratestyles = [20, 21, 22, 23, 29, 30, 33, 34]

vrates = {}
thresholds = [0.5, 1.5, 2.5, 3.5, 4.5]
nthr = len(thresholds)
if args.ratefile:
    fn = "outp/out_fitrates_%gC.json" % args.temp
    if args.date is not None:
        fn = fn.replace(".json", "_%s.json" % args.date)
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
        hdt = ROOT.TH1D("h_dt", "", 100, 0, 1000)
        canv.SetLogy(0)
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
            graphs = []
            for chan in range(8):
                ped = peds[chan]
                spa = chanspas[chan]
                print "SPA = %g" % spa
                wf = wfs[chan]
                if nsample is None:
                    nsample = len(wf)
                prev = wf[0] - ped
                lasttrig = None
                xall = array.array("d")
                yall = array.array("d")
                xtrig = array.array("d")
                ytrig = array.array("d")
                for i in range(1, len(wf)):
                    val = wf[i] - ped
                    xall.append(i)
                    yall.append(val)
                    for j in range(nthr):
                        thr = thresholds[j] * spa
                        if thr < 0:
                            continue
                        if val >= thr and prev < thr:
                            rates[chan][j] += 1
                            if j == 0:
                                xtrig.append(i)
                                ytrig.append(val)
                            if j == 0 and chan == 0:
                                if lasttrig is not None:
                                    hdt.Fill(i - lasttrig)
                                lasttrig = i
                    prev = val
                if len(xtrig) > 0:
                    gall = ROOT.TGraph(len(xall), xall, yall)
                    gall.SetMarkerStyle(22)
                    gall.SetLineColor(chancolours[chan])
                    gtrig = ROOT.TGraph(len(xtrig), xtrig, ytrig)
                    gtrig.SetMarkerStyle(22)
                    gtrig.SetMarkerColor(chancolours[chan])
                    graphs.append(gall)
                    graphs.append(gtrig)

            if nevt % 10 == 0:
                hdt.Draw()
                canv.Update()
                raw_input("hdt update...")
            if len(graphs) > 0:
                for i in range(len(graphs)):
                    g = graphs[i]
                    if i == 0:
                        g.Draw("AL")
                    elif i % 2 == 0:
                        g.Draw("L")
                    else:
                        g.Draw("P")
                canv.Update()
                raw_input("graphs...")
        hdt.Draw()
        canv.Update()
        raw_input("...")
        canv.SetLogy()
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
    outfn = "outp/out_fitrates_%gC.json" % args.temp
    if args.date is not None:
        outfn = outfn.replace(".json", "_%s.json" % args.date)
    outp = open(outfn, "w")
    json.dump(vrates, outp, indent=4)
    outp.close()


# Plot SPA as function of over voltage
canv.SetLogy(0)
allgraphs = []
allmin = None
allmax = None
minv = None
maxv = None
leg = None
chanleg = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
for chan in range(8):
    graphs = []
    x = array.array("d")
    y = array.array("d")
    minrate = None
    maxrate = None
    for v in voltages:
        spa = spas[v][0][chan]
        if spa < 0:
            print "Skipping v = %g since spa = %g" % (v, spa)
            continue
        else:
            print "chan %d, ov = %g V, SPA = %g" % (chan, v, spa)
        vbr = vbrs[chan]
        ov = v - vbr
        if minv is None or ov < minv:
            minv = ov
        if maxv is None or ov > maxv:
            maxv = ov
        x.append(ov)
        y.append(spa)
    g = ROOT.TGraph(len(x), x, y)
    g.SetName("g_spa_ch%d" % chan)
    g.SetTitle("")
    g.SetMarkerStyle(ratestyles[0])
    g.SetMarkerColor(chancolours[chan])
    g.SetLineColor(chancolours[chan])
    g.GetXaxis().SetTitle("over voltage [V]")
    g.GetYaxis().SetTitle("1 PA [ADC count]")
    g.Draw("AP")
    chanleg.AddEntry(g, "channel %d" % chan, "L")
    graphs.append(g)
    g.Draw("AP")
    canv.Update()
    canv.SaveAs("imgs/g_SPA_chan%d.png" % chan)
    if args.draw:
        raw_input()
    allgraphs.extend(graphs)
    if allmin is None or spa < allmin:
        allmin = spa
    if allmax is None or spa > allmax:
        allmax = spa
fakex = array.array("d", [minv, maxv])
fakey = array.array("d", [allmin, allmax])
gfake = ROOT.TGraph(2, fakex, fakey)
gfake.SetTitle("temperature = %g C" % args.temp)
gfake.GetXaxis().SetTitle("over voltage [V]")
gfake.GetYaxis().SetTitle("1 PA [ADC count]")
gfake.Draw("AP")
for g in allgraphs:
    g.Draw("LP")
chanleg.Draw()
canv.Update()
canv.SaveAs("imgs/g_SPA_%gC_all.eps" % args.temp)
canv.SaveAs("imgs/g_SPA_%gC_all.png" % args.temp)
if args.draw:
    raw_input()

dVBR = []
h_dVBR = ROOT.TH1D("h_dVBR", "", 40, -2, 2)
h_dVBR.SetXTitle("#Delta V_{BR} [V]")
h_dVBR.SetYTitle("channels / 0.1 V")
for g in allgraphs:
    g.Fit("pol1")
    fn = g.GetFunction("pol1")
    g.Draw("ALP")
    canv.Update()
    if args.draw:
        raw_input()
    offset = fn.GetParameter(0)
    gradient = fn.GetParameter(1)
    # Delta vBR is OV when SPA = 0 ADC
    # y = offset + gradient * x
    # when y = 0, x = -offset / gradient
    dV = - offset / gradient
    h_dVBR.Fill(dV)
    dVBR.append(dV)
h_dVBR.Draw()
canv.Update()
canv.SaveAs("imgs/gch_dVBR_%gC.png" % args.temp)
if args.draw:
    raw_input()

# plot rates at different thresholds for single temperature, different voltages
canv.SetLogy(0)
allgraphs = []
allmin = None
allmax = None
minv = None
maxv = None
leg = None
chanleg = ROOT.TLegend(0.7, 0.7, 0.8, 0.95)
for chan in range(8):
    leg = ROOT.TLegend(0.8, 0.7, 0.95, 0.95)
    graphs = []
    x = array.array("d")
    ys = []
    minrate = None
    maxrate = None
    for ithr in range(nthr):
        ys.append(array.array("d"))
    for v in voltages:
        spa = spas[v][0][chan]
        dV = dVBR[chan]
        if spa < 0:
            print "Skipping v = %g since spa = %g" % (v, spa)
            continue
        vbr = vbrs[chan]
        ov = v - vbr
        if minv is None or ov < minv:
            minv = ov
        if maxv is None or ov > maxv:
            maxv = ov
        x.append(ov - dV)
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
        if ithr == 0:
            chanleg.AddEntry(g, "channel %d" % chan, "L")
        graphs.append(g)
        #canv.Update()
        #if args.draw:
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
    if args.draw:
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
chanleg.Draw()
canv.Update()
canv.SaveAs("imgs/g_rates_%gC_all.eps" % args.temp)
canv.SaveAs("imgs/g_rates_%gC_all.png" % args.temp)
if args.draw:
    raw_input()




