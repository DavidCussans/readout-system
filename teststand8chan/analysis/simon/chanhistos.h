#ifndef CHANHISTOS_H
#define CHANHISTOS_H

#include <TFile.h>
#include <TH1F.h>
#include <TH2F.h>

#include <vector>
using std::vector;

class chanHistos
{
private:
    TH1F *h1_amp;
    TH1F *h1_AWf;
    TH1F *h1_PW;
    TH1F *h1_RT;
    TH1F *h1_FT;

    TH2F *h2_AvRT;
    TH2F *h2_AvFT;

    TH1F *h1_pdVal;
    TH1F *h1_pdRMS;
    TH1F *h1_nP;

    int chan;
    float pedestal,RMS;
    float bias;

public:
    chanHistos();
    chanHistos(int i, float bias = -1);

    ~chanHistos();
    void writeHistos(TFile *f);

    TH1F* getAmpHisto(){return h1_amp;}
    void fillHisto(vector<float> *wf);
    TH1F* getGain(float &gain);
    void getPedestalInfo(float &val, float &RMS){
        val = h1_pdVal->GetMean();
        RMS = h1_pdRMS->GetMean();
    }
    void setPedestalInfo(float _val, float _RMS){
        pedestal = _val; RMS = _RMS;
    }
};

float getRes(vector<float> v, float t);
float getBias(const char *fName);

#endif // CHANHISTOS_H
