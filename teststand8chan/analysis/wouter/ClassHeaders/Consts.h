//Wouter Van De Pontseele
//UGent
//June 2016
#ifndef Consts_H_
#define Consts_H_

#include <vector>
#include <TChain.h>


using namespace std;


///Parameters
const float afterpulsebuffer = 10;       //Number of intervals after a peak that is discarded

///Describe output plots
const int ChToAn = 2; //channel
const Double_t TempToAn = 8; //temperature in celsius
const Double_t VoltToAn = 64.50; //bias setting

///Directory of the Data
//const char *dirname="/home/wouter/Documents/MPPC_Data/";
bool writer = true;
const char *dirname="Data_to_Analyse";



/*  Description of the inut data structures, do not change  */

int counter=0; //counts the number of succesful processed files

///Describe input space
const int nrChannels = 8;
const int nrEvents= 1000;
const int nrSamples=2048;
const int timeSample= 25; //nanoseconds

//only for the example waveform plot in the end
int eventnr=0;  //random if 0
vector<float> yaxis;
TGraph *g;

TTree *treeWF;
TTree *treeC;
TTree *treeS;

const char * const h_ADC_array[] = {"h_val_wf_chan0", "h_val_wf_chan1", "h_val_wf_chan2", "h_val_wf_chan3","h_val_wf_chan4", "h_val_wf_chan5", "h_val_wf_chan6","h_val_wf_chan7"};

#endif
