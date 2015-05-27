"""
Draw estimated signal rates for different readout schemes
"""
import array

import ROOT


def estimaterates(darkcountrate, crosstalk, coincidence=None, dt=50e-9):
    thresholds = array.array("d")
    rates = array.array("d")
    for i in range(5):
        thresholds.append(i + 0.5)
        rate = None
        if coincidence is None:
            rate = darkcountrate * crosstalk**i
        else:
            rate = darkcountrate * crosstalk**i
            coinc = rate * dt * coincidence
            if coinc < 1.0:
                rate *= coinc
        rates.append(rate * 0.001)
    g = ROOT.TGraph(len(thresholds), thresholds, rates)
    g.GetXaxis().SetTitle("Zero suppression threshold [PA]")
    g.GetYaxis().SetTitle("Dark count signal rate [kHz]")
    return g

maxrate = 375 # kHz
saferate = 200 # kHz

gmaxrate = ROOT.TGraph(2, array.array("d", [0, 5]), array.array("d", [maxrate, maxrate]))
gmaxrate.SetLineColor(ROOT.kRed)
gsaferate = ROOT.TGraph(2, array.array("d", [0, 5]), array.array("d", [saferate, saferate]))
gsaferate.SetLineColor(ROOT.kGreen)

def plot(fn, name, graphs, labels):
    canv = ROOT.TCanvas()
    canv.SetLogy()
    leg = ROOT.TLegend(0.8, 0.8, 1.0, 1.0, "")
    graphs[0].GetYaxis().SetRangeUser(1, 1000)
    graphs[0].SetTitle(name)
    for i in range(len(graphs)):
        g = graphs[i]
        l = labels[i]
        leg.AddEntry(g, l, "P")
        if i == 0:
            g.Draw("LAP")
        else:
            g.Draw("LP")
    gsaferate.Draw("L")
    gmaxrate.Draw("L")
    leg.Draw()
    canv.Update()
    canv.SaveAs("imgs/%s.eps" % fn)
    canv.SaveAs("imgs/%s.png" % fn)
    raw_input()

dcr_s12572 = 2e6
g_s12572_30_single = estimaterates(dcr_s12572, 0.3)
g_s12572_30_single.SetMarkerStyle(22)
g_s12572_30_24 = estimaterates(dcr_s12572, 0.3, 24)
g_s12572_30_24.SetMarkerStyle(23)
g_s12572_30_16 = estimaterates(dcr_s12572, 0.3, 16)
g_s12572_30_16.SetMarkerStyle(24)
g_s12572_30_1 = estimaterates(dcr_s12572, 0.3, 1)
g_s12572_30_1.SetMarkerStyle(25)
graphs_s12572_30pct = [g_s12572_30_single, g_s12572_30_24, g_s12572_30_16, g_s12572_30_1]
labels_s12572_30pct = ["no coincidence", "24 way coincidence", "16 way coincidence", "1 way coincidence"]

g_s12572_10_single = estimaterates(dcr_s12572, 0.1)
g_s12572_10_single.SetMarkerStyle(22)
g_s12572_10_24 = estimaterates(dcr_s12572, 0.1, 24)
g_s12572_10_24.SetMarkerStyle(23)
g_s12572_10_16 = estimaterates(dcr_s12572, 0.1, 16)
g_s12572_10_16.SetMarkerStyle(24)
g_s12572_10_1 = estimaterates(dcr_s12572, 0.1, 1)
g_s12572_10_1.SetMarkerStyle(25)
graphs_s12572_10pct = [g_s12572_10_single, g_s12572_10_24, g_s12572_10_16, g_s12572_10_1]
labels_s12572_10pct = ["no coincidence", "24 way coincidence", "16 way coincidence", "1 way coincidence"]

dcr_s12572_5C = 4e5
g_s12572_10_5C_single = estimaterates(dcr_s12572_5C, 0.1)
g_s12572_10_5C_single.SetMarkerStyle(22)
g_s12572_10_5C_24 = estimaterates(dcr_s12572_5C, 0.1, 24)
g_s12572_10_5C_24.SetMarkerStyle(23)
g_s12572_10_5C_16 = estimaterates(dcr_s12572_5C, 0.1, 16)
g_s12572_10_5C_16.SetMarkerStyle(24)
g_s12572_10_5C_1 = estimaterates(dcr_s12572_5C, 0.1, 1)
g_s12572_10_5C_1.SetMarkerStyle(25)
graphs_s12572_10pct_5C = [g_s12572_10_5C_single, g_s12572_10_5C_24, g_s12572_10_5C_16, g_s12572_10_5C_1]
labels_s12572_10pct_5C = ["no coincidence", "24 way coincidence", "16 way coincidence", "1 way coincidence"]

plot("g_s12572_30pct", "S12572, 30% cross talk, T = 25 C", graphs_s12572_30pct, labels_s12572_30pct)
plot("g_s12572_10pct", "S12572, 10% cross talk, T = 25 C", graphs_s12572_10pct, labels_s12572_10pct)
plot("g_s12572_10pct_5C", "S12572, 10% cross talk, T = 5 C", graphs_s12572_10pct_5C, labels_s12572_10pct_5C)

dcr_sensl = 860e3
g_sensl_10_single = estimaterates(dcr_sensl, 0.1)
g_sensl_10_single.SetMarkerStyle(22)
g_sensl_10_24 = estimaterates(dcr_sensl, 0.1, 24)
g_sensl_10_24.SetMarkerStyle(23)
g_sensl_10_16 = estimaterates(dcr_sensl, 0.1, 16)
g_sensl_10_16.SetMarkerStyle(24)
g_sensl_10_1 = estimaterates(dcr_sensl, 0.1, 1)
g_sensl_10_1.SetMarkerStyle(25)
graphs_sensl_10pct = [g_sensl_10_single, g_sensl_10_24, g_sensl_10_16, g_sensl_10_1]
labels_sensl_10pct = ["no coincidence", "24 way coincidence", "16 way coincidence", "1 way coincidence"]

plot("g_sensl_10pct", "sensl C series, 10% cross talk, T = 21 C", graphs_sensl_10pct, labels_sensl_10pct)
