
#include <TCanvas.h>
#include <TF1.h>
#include <TSpectrum.h>

#include <algorithm>    // std::sort
#include <iostream>

using std::cout;
using std::endl;

#include "chanhistos.h"

chanHistos::chanHistos(){
    // empty default constructor
}

chanHistos::chanHistos(int i){
    chan = i;
    pedestal = -1;
    RMS = -1;

    char hName[127];
    sprintf(hName,"amp_%i",i);
    h1_amp = new TH1F(hName,hName,1024,0,1024);
    sprintf(hName,"avWf_%i",i);
    h1_AWf = new TH1F(hName,hName,100,0,100);
    sprintf(hName,"PeakWidth_%i",i);
    h1_PW = new TH1F(hName,hName,100,0,100);
    sprintf(hName,"RiseTime_%i",i);
    h1_RT = new TH1F(hName,hName,100,0,100);
    sprintf(hName,"FallTime_%i",i);
    h1_FT = new TH1F(hName,hName,100,0,100);

    sprintf(hName,"AmpVsRiseTime_%i",i);
    h2_AvRT = new TH2F(hName,hName,
                       1000,0,1000,100,0,100);
    sprintf(hName,"AmpVsFallTime_%i",i);
    h2_AvFT = new TH2F(hName,hName,
                       1000,0,1000,100,0,100);

    sprintf(hName,"pedestalValue_%i",i);
    h1_pdVal = new TH1F(hName,hName,16384,0,16384);
    sprintf(hName,"pedestalRMS_%i",i);
    h1_pdRMS = new TH1F(hName,hName,100,0,100);
    sprintf(hName,"nPeaks_%i",i);
    h1_nP = new TH1F(hName,hName,50,0,50);
}

chanHistos::~chanHistos(){
    delete h1_amp;
    delete h1_AWf;
    delete h1_PW;
    delete h1_RT;
    delete h1_FT;

    delete h2_AvRT;
    delete h2_AvFT;

    delete h1_pdVal;
    delete h1_pdRMS;
    delete h1_nP;
}

void chanHistos::writeHistos(TFile *f){
    TF1 *f1 = new TF1("const","1",0,100);
    h1_AWf->Divide(f1,h1_AWf->GetMaximum());
    delete f1;

    f->cd();
    h1_amp->Write();
    h1_AWf->Write();
    h1_PW->Write();
    h1_RT->Write();
    h1_FT->Write();

    h2_AvRT->Write();
    h2_AvFT->Write();

    h1_pdVal->Write();
    h1_pdRMS->Write();
    h1_nP->Write();

    char hName[123];
    sprintf(hName,"gain_%i",chan);
    TH1F *h1_g = new TH1F(hName,hName,1,0,1);
    h1_g->SetBinContent(1,getGain());
    h1_g->Write();
    delete h1_g;
}

void chanHistos::fillHisto(vector<float> *wf){
    int wfLen = wf->size();
    float av = 0;
    for (unsigned int i = 0; i < wfLen; i ++){
        av += wf->at(i);
    }
    av /= wfLen;
    float var = 0;
    for (unsigned int i = 0; i < wfLen; i ++){
        var += (wf->at(i) - av)*
                (wf->at(i) - av);
    }
    var = sqrt(var/wfLen);

    h1_pdVal->Fill(av);
    h1_pdRMS->Fill(var);

    if (pedestal != -1) av = pedestal;
    if (RMS != -1)      var = RMS;

    const int peakPos = 40;
    int nP = 0;
    for(unsigned int i = peakPos+1; i < wfLen-(100-peakPos)-1; i ++){
        if (wf->at(i) > av + 5*var &&
                wf->at(i) > wf->at(i-1) &&
                wf->at(i) > wf->at(i+1)){
            h1_amp->Fill(wf->at(i)-av);
            nP ++;

            // create the average waveform
            for (unsigned int j = 0; j < 100; j ++){
                h1_AWf->Fill(j,wf->at(i+j-peakPos) - av);
            }

            // find the rise time
            int ps = i-1;
            while (ps != 0 && wf->at(ps)-av > 0.05*(wf->at(i)-av)){
                ps --;
            }
            if (ps != 0){
                h1_RT->Fill(i-ps);
                h2_AvRT->Fill(wf->at(i)-av,i-ps);
            }

            // find the fall time
            int pe = i+1;
            while (pe < wf->size() && wf->at(pe)-av > 0.05*(wf->at(i)-av)){
                pe ++;
            }
            if (pe < wf->size()){
                h1_FT->Fill(pe-i);
                h2_AvFT->Fill(wf->at(i)-av,pe-i);
            }

            if (ps != 0 && pe < wf->size()){
                h1_PW->Fill(pe-ps);
            }
        }
    }
    h1_nP->Fill(nP);

    if (nP == 0){
        h1_pdVal->Fill(av);
        h1_pdRMS->Fill(var);
    }
}

float chanHistos::getGain(){
    char cName[12];
    sprintf(cName,"canv_%i",chan);
    TCanvas *c1 = new TCanvas(cName);
    TSpectrum *s = new TSpectrum(16);
    int np = s->Search(h1_amp,2,"",5e-2);
    while (np >= 9 && h1_amp->GetNbinsX() > 250){
        h1_amp->Rebin();
        np = s->Search(h1_amp,2,"",1e-2);
    }
    float *pp = s->GetPositionX();
    float *pv = s->GetPositionY();

    if (np == 0 || h1_amp->GetNbinsX() < 250){
        // there's either no peak or there's not enough stats
        return 0;
    }

    char fName[120];
    vector<TF1*> v_f;
    double rl,rh;
    if (np > 6){
        // only use the 6 largest peaks
        np = 6;
    }
    for (int i = 0; i < np; i ++){
        int pb = h1_amp->GetXaxis()->FindBin(pp[i]);
        int lb = pb-1;
        while(h1_amp->GetBinContent(lb) > 0.5*pv[i]){
            lb --;
        }
        rl = h1_amp->GetXaxis()->GetBinCenter(lb);
        int hb = pb + 1;
        while(h1_amp->GetBinContent(hb) > 0.5*pv[i]){
            hb ++;
        }
        rh = h1_amp->GetXaxis()->GetBinCenter(hb);

        sprintf(fName,"gaus_%i",i);
        v_f.push_back(new TF1(fName,"gaus",rl,rh));
        v_f[i]->SetParameters(pv[i],pp[i],(rh-rl)/2.8);
        h1_amp->Fit(v_f[i],"rq");
    }

    float gain = v_f[0]->GetParameter(1);
    if (np == 1){
        return gain;
    }

    vector<float> nPA(1,0);
    float mu;
    for (int i = 0; i < np; i ++){
        v_f[i]->GetRange(rl,rh);
        mu = v_f[i]->GetParameter(1);
        if (mu < rl || mu > rh){
            // this is a bad fit
            continue;
        }
        bool duplicate = false;
        for (int j = 0; j < i; j ++){
            v_f[j]->GetRange(rl,rh);
            if (mu > rl && mu < rh){
                // this peak falls in the range of
                // a previously found peak,
                duplicate = true;
                break;
            }
        }
        if (!duplicate){
            nPA.push_back(mu);
        }
    }

    sort(nPA.begin(),nPA.end());
    gain = nPA[1] - nPA[0];
    /*
    for (int i = 2; i < nPA.size(); i ++){
        if (nPA[i] - nPA[i-1] < gain){
            gain = nPA[i] - nPA[i-1];
        }
    }
    */

    float res, minRes = getRes(nPA,gain);
    for (float gg = 0.55*gain; gg < 1.25*gain; gg += 0.01){
        res = getRes(nPA,gg);
        if (res < minRes){
            minRes = res;
            gain = gg;
        }
    }

    delete c1;
    return gain;
}

float getRes(vector<float> v, float t){
    float res = 0;
    float n,nr;
    unsigned int ne = v.size();
    for (int i = 0; i < ne; i ++){
        for (int j = 0; j < ne; j ++){
            n = (v[j] - v[i])/t;
            nr = round(n);
            res += (n-nr)*(n-nr);
        }
    }
    return res;
}
