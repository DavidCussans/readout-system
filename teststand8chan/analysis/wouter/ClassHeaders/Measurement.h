//Wouter Van De Pontseele
//UGent
//June 2016

///Defines a struct that has the information of a root file, could be converted to a class in future

#ifndef MEASUREMENT_H_
#define MEASUREMENT_H_

#include <vector>
#include "TString.h"

using namespace std;

struct MEASUREMENT     // One struct for each root file
{
    TString name;

    ///CONDITIONS
    Double_t temp;
    Double_t reqbias;
    Int_t serial;

    ///MPPC specifications
    vector<Double_t> vop;
    vector<Double_t> gain;
    vector<Double_t> dcr;

    ///GAIN per CH
    vector<float> gainInt;
    vector<float> gainAmp;

    vector<float> gainIntErr;
    vector<float> gainAmpErr;

    ///CROSSTALK per CH
    vector<float> crosstalkInt;
    vector<float> crosstalkAmp;

    vector<float> CT_errorInt;
    vector<float> CT_errorAmp;

    ///DCR INFO per CH
    vector<int> DCRcountInt0; //poisson, no need for extra errors
    vector<int> DCRcountAmp0; //0.5PA

    vector<int> DCRcountInt1; //1.5PA
    vector<int> DCRcountAmp1;

    vector<int> DCRcountInt2; //2.5PA
    vector<int> DCRcountAmp2;


    vector<float> DCRfit;
    vector<float> DCRfitErr;


    //helpers//
    vector<vector<int> > peakDistributionVec;
    //peaks[Channel][number of pe, k]=number of signals with k peaks
    vector<vector<int> > peaksInt;
    vector<vector<int> > peaksAmp;

    ///Unsorted arrays that contain info about all the peaks
    vector<vector<float> > IntAll;
    vector<vector<float> > AmpAll;

    ///Arrays that contain information about the structure behind the peaks
    vector<vector<float> > ValleysInt;
    vector<vector<float> > ValleysAmp;

    vector<vector<float> > TopsInt;
    vector<vector<float> > TopsAmp;
};

#endif
