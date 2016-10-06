//Wouter Van De Pontseele
//UGent
//June 2016

#ifndef MPPC_H_
#define MPPC_H_


/*#### IMPORTS ####*/
#include "ClassHeaders/waveforms.h"
#include "ClassHeaders/conditions.h"
#include "ClassHeaders/sensors.h"

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <math.h>
#include <numeric>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <time.h>
#include <vector>

#include <TH1F.h>
#include <TStyle.h>
#include <TAxis.h>
#include <TCanvas.h>
#include <TGraph.h>
#include <TArrow.h>
#include <TFile.h>
#include "TSystem.h"
#include "TSystemFile.h"
#include "TSystemDirectory.h"
#include "TApplication.h"
#include "TList.h"
#include "TString.h"
#include "TF1.h"



using namespace std;

/*#### FUNCTIONS ####*/

bool compare_measurement(const MEASUREMENT& a, const MEASUREMENT& b)
{
    bool afirst=true;
    if(a.reqbias > b.reqbias)
    {
        afirst = true;
    }
    else if(a.reqbias < b.reqbias)
    {
        afirst = false;
    }
    {
        afirst = (a.temp < b.temp);
    }
    return afirst;
}


void help(string s)
{
    cout<<"Help: "<< s <<endl;
}

void help(double s)
{
    cout<<"Help: "<< to_string(s) <<endl;
}

vector<float> linspace(float a, float b, int n)
{
    vector<float> array;
    float step = (b-a) / (n-1);

    while(a <= b)
    {
        array.push_back(a);
        a += step;
    }
    return array;
}

template <typename T>
std::string to_string_wp(const T a_value, const int n = 6)
{
    std::ostringstream out;
    out << std::setprecision(n) << a_value;
    return out.str();
}

float avg_vec (std::vector<float> &v)
{
    float avg = std::accumulate(v.begin(), v.end(), (float) 0) / v.size();
    return avg;
}

float std_vec (std::vector<float> &v,double mean)
{
    std::vector<double> diff(v.size());
    std::transform(v.begin(), v.end(), diff.begin(),std::bind2nd(std::minus<double>(), mean));
    double sq_sum = std::inner_product(diff.begin(), diff.end(), diff.begin(), 0.0);
    return (float) std::sqrt(sq_sum / v.size());
}

///Returns amplitude and index(time) of peaks
void FindPeaks(vector<int>* timestamps, vector<float> wf_chanx,int ch,MEASUREMENT*,bool);
void ColorPeaks(vector<float> v,float threshold);

/// Analyse that data!
void DefineThresholds(MEASUREMENT*,bool first);
void CTandDCRcalculator(MEASUREMENT*);
void WriteAll(MEASUREMENT*);

///Analyses one entry: time intervals
void AnalyseEntry(vector<int>* timestamps, int ch,MEASUREMENT*);

///The main function
void Mppc_analyser();

///Analyse one configuration
void CTandTimeDistriOneFile(MEASUREMENT*);

#endif
