/*
 * Script to analyze the Bristol 8 channel setup,
 * takes an input file and a number of arguments,
 * writes a number of histograms to a root file (see
 * https://bitbucket.org/solidexperiment/readout-system/issues/48#comment-28983697
 * for information on the contents of the root file)
 *
 * compile using:
 * g++ -O3 main.cpp waveforms.cpp chanHistos.cpp -o awf `root-config --cflags --glibs` -lSpectrum
 *
 * A 'pedestals.root' file with the pedestals andthe RMS values
 * of the waveforms can created using the -m option on a
 * below breakdown file.
 *
 * The pedestals.root file can (should) be used via
 *  -p pedestals.root
 *
 */

#include <TChain.h>
#include <TF1.h>
#include <TFile.h>
#include <TH1F.h>

#include <iostream>
#include <vector>

#include "chanhistos.h"
#include "waveforms.h"

using namespace std;

int main(int argc, char *argv[]){
    TChain * chain = new TChain("waveforms");
    int filecount = 0;
    char outpFName[511];
    sprintf(outpFName,"%s","outp.root");
    bool setPD = false;
    bool makePD = false;
    char PDfile[511];
    float bias = 0;
    sprintf(PDfile,"%s","pedestals.root");
    for (int i = 1; i < argc; i ++){
        if (argv[i][0] == '-'){
            if (argv[i][1] == 'o'){
                // set the output
                sprintf(outpFName,"%s",argv[i+1]);
                i ++;
                continue;
            }
            if (argv[i][1] == 'p'){
                // set the pedestal info
                setPD = true;
                sprintf(PDfile,"%s",argv[i+1]);
                i ++;
                continue;
            }
            if (argv[i][1] == 'm'){
                // make pedestal info
                makePD = true;
                continue;
            }
            cerr<<"unidentified option "<<argv[i];
            cerr<<", read the code for allowed options."<< endl;
            return -1;
        } else {
            cout << argv[i] << flush;
            chain->Add(argv[i]);
            bias = getBias(argv[i]);
            cout<<" added ("<<bias<<" V bias)"<<endl;
            filecount ++;
        }
    }
    if (filecount == 0){
        cerr << "Give at least one file to read" << endl;
        return -1;
    }


    vector<chanHistos*> v_ch;
    for (int i = 0; i < 8; i ++){
        v_ch.push_back(new chanHistos(i,bias));
    }


    if (setPD){
        TFile *pdf = new TFile(PDfile,"read");
        TH1F *h_pd = (TH1F*) pdf->Get("pdHisto");
        for (int i = 0; i < 8; i ++){
            v_ch.at(i)->setPedestalInfo(
                        h_pd->GetBinContent(i+1),
                        h_pd->GetBinError(i+1));
        }
        delete h_pd;
        delete pdf;
    }

    waveforms *tree = new waveforms(chain);
    int nentries = tree->fChain->GetEntries();
    for (int ientry = 0; ientry < nentries; ientry ++){
        tree->GetEntry(ientry);

        v_ch.at(0)->fillHisto(tree->wf_chan0);
        v_ch.at(1)->fillHisto(tree->wf_chan1);
        v_ch.at(2)->fillHisto(tree->wf_chan2);
        v_ch.at(3)->fillHisto(tree->wf_chan3);
        v_ch.at(4)->fillHisto(tree->wf_chan4);
        v_ch.at(5)->fillHisto(tree->wf_chan5);
        v_ch.at(6)->fillHisto(tree->wf_chan6);
        v_ch.at(7)->fillHisto(tree->wf_chan7);
    }

    TH1F* hpdo = new TH1F("pdHisto","pdHisto",8,0,8);
    TFile *fOut = new TFile(outpFName,"recreate");
    float pdV,pdR;
    for (int i = 0; i < 8; i ++){
        v_ch.at(i)->writeHistos(fOut);
        v_ch.at(i)->getPedestalInfo(pdV,pdR);
        hpdo->SetBinContent(i+1,pdV);
        hpdo->SetBinError(i+1,pdR);
        delete v_ch.at(i);
    }
    delete fOut;

    if (makePD){
        TFile *pdo = new TFile("pedestals.root","recreate");
        hpdo->Write();
        delete pdo;
    }
    delete hpdo;

    return 1;
}

