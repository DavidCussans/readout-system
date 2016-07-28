import argparse
import array
import json
import os

import ROOT

import chanmap

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--temp", type=float)
parser.add_argument("-d", "--draw", action="store_true")
parser.add_argument("--date")
args = parser.parse_args()

basedir = "/data/solid/sipmcalibration_bris/good"
fns = os.listdir(basedir)
filelist = []
for fn in fns:
    if fn.startswith("sipmcalib"):
        if args.date is None or args.date in fn:
            filelist.append(fn)

if args.temp is not None:
    tempfiles = {}
    rmsvals = {}
    for fn in filelist:
        fnsplit = fn.split("_")
        temp = float(fnsplit[2].replace("C", ""))
        if temp != args.temp:
            continue
        voltage = float(fnsplit[1].replace("V", ""))
        tempfiles[voltage] = os.path.join(basedir, fn)
    voltages = tempfiles.keys()
    voltages.sort()
    for voltage in voltages:
        fn = tempfiles[voltage]
        inp = ROOT.TFile(fn, "READ")
        keys = inp.GetListOfKeys()
        if keys.GetSize() < 11:
            inp.Close()
            continue
        rms = []
        for chan in range(8):
            h = inp.Get("h_val_wf_chan%d" % chan)
            rms.append(h.GetRMS())
        inp.Close()
        rmsvals[voltage] = rms
    voltages = rmsvals.keys()
    voltages.sort()
    graphs = []
    yaxes = []
    for chan in range(8):
        yaxes.append(array.array("d"))
    voltages = array.array("d", voltages)
    breakdownvoltages = []
    rmsthresholds = []
    for i in range(8):
        breakdownvoltages.append(None)
    drms = 0.05
    for voltage in voltages:
        for chan in range(8):
            rms = rmsvals[voltage][chan]
            if len(rmsthresholds) < 8:
                rmsthresholds.append(rms + drms)
            yaxes[chan].append(rms)
            if breakdownvoltages[chan] is None and rms > rmsthresholds[chan]:
                breakdownvoltages[chan] = voltage
    canv = ROOT.TCanvas()
    #canv.SetLogy()
    h_vbr = ROOT.TH1D("h_vbr", "", 20, 60.0, 70.0)
    h_vbr.SetXTitle("meausured v_{BR} [V]")
    h_dvbr = ROOT.TH1D("h_dvbr", "", 100, -5, 5)
    h_dvbr.SetXTitle("measured - QA v_{BR} [V]")
    vbr_meas = array.array("d")
    vbr_meas_err = array.array("d")
    vbr_ham = array.array("d")
    vbr_ham_err = array.array("d")
    for chan in range(8):
        g = ROOT.TGraph(len(voltages), voltages, yaxes[chan])
        vbr = breakdownvoltages[chan]
        qavbr = chanmap.sipms[chan].vop - 2.6
        qavbr += 0.06 * (args.temp - 25.0)
        h_vbr.Fill(vbr)
        h_dvbr.Fill(vbr - qavbr)
        vbr_meas.append(vbr)
        vbr_meas_err.append(0.2)
        vbr_ham.append(qavbr)
        vbr_ham_err.append(0.05)
        thr = rmsthresholds[chan]
        g.SetTitle("channel %d, V_{BR} = %g V" % (chan, vbr))
        g.GetXaxis().SetTitle("Bias voltage [V]")
        g.GetYaxis().SetTitle("RMS [ADC count]")
        g.SetMarkerStyle(22)
        g.GetYaxis().SetRangeUser(thr - 0.5, thr + 2.5)
        g.Draw("ALP")
        l = ROOT.TLine(voltages[0], thr, voltages[-1], thr)
        l.SetLineColor(ROOT.kRed)
        l.Draw()
        canv.Update()
        if args.draw:
            raw_input()
            canv.SaveAs("imgs/g_RMS_ch%d_%gC.png" % (chan, args.temp))
    h_vbr.Draw()
    canv.Update()
    if args.draw:
        raw_input()
    h_dvbr.Draw()
    canv.Update()
    if args.draw:
        raw_input()
    g_vbr = ROOT.TGraphErrors(len(vbr_meas), vbr_ham, vbr_meas, vbr_ham_err, vbr_meas_err)
    g_vbr.SetTitle("")
    g_vbr.GetXaxis().SetTitle("QA V_{BR} [V]")
    g_vbr.GetYaxis().SetTitle("measured V_{BR} [V]")
    g_vbr.SetMarkerStyle(22)
    g_vbr.Draw("AP")
    canv.Update()
    if args.draw:
        raw_input()
    outdata = {}
    outdata["temp"] = args.temp
    outdata["vbr"] = list(vbr_meas)
    outfn = "outp/out_breakdown_%gC.json" % args.temp
    if args.date is not None:
        outfn = outfn.replace(".json", "_%s.json" % args.date)
    outp = open(outfn, "w")
    json.dump(outdata, outp, indent=4)
    outp.close()

