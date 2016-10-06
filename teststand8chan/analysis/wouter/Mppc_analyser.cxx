//Wouter Van De Pontseele
//UGent
//June 2016

#include "Mppc_analyser.hxx"
#include "ClassHeaders/Consts.h"

#ifndef __Cling__
void StandaloneApplication(int argc, char** argv)
{
    Mppc_analyser();
}

int main(int argc, char** argv)
{
    TApplication app("Root Application",&argc,argv);
    StandaloneApplication(app.Argc(), app.Argv());
    app.Run();
    return 0;
}
#endif


///The main function
void Mppc_analyser()
{
    MEASUREMENT keep;
    srand(time(NULL));
    if (eventnr==0) eventnr =rand() % nrEvents;
    int filesdone=1;

    cout << "-----------------------------------------------" << endl;
    const char *ext=".root";
    TSystemDirectory dir(dirname, dirname);
    TList *files = dir.GetListOfFiles();
    int numberfiles = files->GetSize ()-2;
    if (files)
    {
        TSystemFile *file;
        TString fname;
        TIter next(files);
        while ((file=(TSystemFile*)next()))
        {
            fname = file->GetName();
            if (!file->IsDirectory() && fname.EndsWith(ext))
            {
                string buf(dirname);
                buf.append("/");
                buf.append(fname.Data());
                cout << fname.Data() << endl;
                TFile f(buf.c_str());

                f.GetObject("sensors",treeS);
                f.GetObject("conditions",treeC);
                f.GetObject("waveforms",treeWF);

                sensors MPPC(treeS);
                conditions COND(treeC);
                COND.GetEntry(0);

                MEASUREMENT thisfile;
                thisfile.name = fname;
                thisfile.temp = COND.temp;
                thisfile.reqbias = COND.reqbias;
                //cout << "Conditions of this file:\t Temp: " << COND.temp << "\t reqbias: " << thisfile.reqbias << endl;
                for(int i=0; i<nrChannels; i++)
                {
                    MPPC.GetEntry(i);
                    thisfile.vop.push_back(MPPC.vop);
                    thisfile.gain.push_back(MPPC.gain);
                    thisfile.dcr.push_back(MPPC.dcr);

                    vector<float> temp(nrChannels);
                    thisfile.gainInt=temp;
                    thisfile.gainAmp=temp;
                    thisfile.gainIntErr=temp;
                    thisfile.gainAmpErr=temp;

                    thisfile.peakDistributionVec.push_back(vector<int>(0));

                    thisfile.AmpAll.push_back(vector<float>(0));
                    thisfile.IntAll.push_back(vector<float>(0));

                    thisfile.peaksInt.push_back(vector<int>(3));
                    thisfile.peaksAmp.push_back(vector<int>(3));

                    thisfile.ValleysInt.push_back(vector<float>(0));
                    thisfile.ValleysAmp.push_back(vector<float>(0));

                    thisfile.TopsInt.push_back(vector<float>(0));
                    thisfile.TopsAmp.push_back(vector<float>(0));

                }

                ///Everything happens here!
                waveforms WF(treeWF);
                WF.AnalyseFile(&thisfile,true); //First time
                DefineThresholds(&thisfile,true);

                for(int ch=0; ch<nrChannels; ch++)
                {
                    thisfile.AmpAll[ch].clear();
                    thisfile.IntAll[ch].clear();
                }
                WF.AnalyseFile(&thisfile,false); // Second time, with good thresholds and deadtime
                int ch =0;
                while(thisfile.AmpAll[ch].size()>1000 && ch<nrChannels)
                {
                    ch++;
                }
                if(ch==nrChannels)
                {
                    DefineThresholds(&thisfile,false);
                    CTandDCRcalculator(&thisfile);
                    if(writer) WriteAll(&thisfile);
                }
                else
                {
                    cout<< "Not enough peaks survived second round\t V " << thisfile.reqbias << ", T " << thisfile.temp << ", Ch " << ch << endl;
                }
                if(thisfile.temp==TempToAn && thisfile.reqbias == VoltToAn) keep = thisfile;

                f.Close();
                f.Delete();
                cout << filesdone++ << "/" << numberfiles << endl;
            }
        }
    }
    CTandTimeDistriOneFile(&keep);
    cout << "Percentage of data that passed all tests: " << counter/numberfiles*100/8 << endl;
}

///Loops over the entries of one root file
void waveforms::AnalyseFile(MEASUREMENT* currentfile,bool first)
{
    Long64_t nentries = fChain->GetEntriesFast();
    for (Long64_t jentry=0; jentry<nentries; jentry++)
    {
        Long64_t ientry = LoadTree(jentry);
        fChain->GetEntry(jentry);

        vector<vector<float> > chWF = {*wf_chan0,*wf_chan1,*wf_chan2,*wf_chan3,*wf_chan4,*wf_chan5,*wf_chan6,*wf_chan7};

        for(int ch =0; ch< nrChannels; ch++)
        {
            float sum = std::accumulate(chWF[ch].begin(), chWF[ch].end(), 0.0);
            float mean = sum / chWF[ch].size();
            for (unsigned int i=0; i<chWF[ch].size(); i++)
            {
                chWF[ch][i]-=mean;
            }

            //Containers to stope peak information
            vector<vector<int> > timestamps(nrChannels);

            FindPeaks(&timestamps[ch], chWF[ch],ch,currentfile, first);
            if(!first) AnalyseEntry(&timestamps[ch], ch, currentfile);

            ///ONE EVENT from ONE FILE ANALYSIS (TempToAn,VoltToAn,ChToAn)
            if(ch==ChToAn && currentfile->temp ==TempToAn &&
               currentfile->reqbias == VoltToAn && jentry==eventnr && !first)
            {
                yaxis=chWF[ch];
                vector<float> xaxis = linspace(1,nrSamples,nrSamples);
                g = new TGraph(xaxis.size(), xaxis.data(), chWF[ch].data());
            }
        }
    }
}



///Returns amplitude and index(time) of peaks
void FindPeaks(vector<int>* timestamps, vector<float> wf_chanx,
               int ch, MEASUREMENT* file, bool first)
{
    bool peak= false;
    float grad = 0;
    float centermax=0;
    float maxval =0;
    float valley=0;
    float integ = 0;
    int bin1=0;
    float threshold;

    if(first) threshold=5;                  //FINETUNING
    else threshold = file->ValleysAmp[ch][0]*0.9;  //FINETUNING

    timestamps->push_back(0); //Make sure that these things are not emply, when reading out in analysefile/analyseentry, start loop from 1!

    for (unsigned int p = 1; p < wf_chanx.size(); p++)
    {
        grad = wf_chanx[p+1] - wf_chanx[p];
        if(grad>0 && !peak)
        {
            if(bin1<centermax)
            {
                integ = 0;
                for(unsigned int k =bin1; k<=p; k++)
                {
                    integ+=wf_chanx[k];
                }
                file->IntAll[ch].push_back(integ);
            }
            peak = true;
            valley = wf_chanx[p];
            bin1=p;
        }
        else if(grad<0 && peak)
        {
            maxval=wf_chanx[p];
            if(maxval> (threshold) && (p-centermax)>afterpulsebuffer)
            {
                file->AmpAll[ch].push_back(maxval);
                centermax = p;
                timestamps->push_back(centermax);
            }
            peak=false;
        }
    }
}

///Analyses one entry
void AnalyseEntry(vector<int>* timestamps, int ch, MEASUREMENT* currentfile)
{
    if (timestamps->size()<3) return;
    int t1;
    int t2=(*timestamps)[1];
    for(unsigned int i=1; i < timestamps->size(); i++)
    {
        t1=t2;
        t2=(*timestamps)[i];
        currentfile->peakDistributionVec[ch].push_back(t2-t1);
    }
}

void ColorPeaks(vector<float> v, float threshold)
{
    bool peak= false;
    float grad = 0;
    double centermax=0;
    double maxval =0;
    double valley=0;

    for (unsigned int p = 1; p < v.size(); p++)
    {
        grad = v[p+1] - v[p];
        if(grad>0 && !peak)
        {
            peak = true;
            valley = v[p];
        }
        else if(grad<0 && peak)
        {
            maxval=v[p];
            if(maxval > threshold && (p-centermax)>afterpulsebuffer)
            {
                centermax = p;
                TArrow arr(centermax+1,maxval+0.12,centermax+1,maxval+0.1,0.015,"|>");
                arr.SetLineColor(3);
                arr.SetFillColor(3);
                arr.DrawClone();
            }
            peak=false;
        }
    }
}



void DefineThresholds(MEASUREMENT* file,bool first)
{
    //Parameter
    float grad;
    float gradp;

    ///Option 1: Do things without finetuning
    float avgInt;
    float avgAmp;
    float stdInt;
    float stdAmp;

    ///option2: Do things with finetuning based on first runs without finetuning
    //double ovest= file->reqbias - 61.3 -0.06*file->temp;
    double ovest = 1.0255*file->reqbias+0.055*(25-file->temp)-64.3;

    float gainInt;
    float gainAmp;
    float gainAmpplus;
    float gainIntplus;
    int p;

    float minInt;
    float minAmp;
    float maxInt;
    float maxAmp;

    float gainAmpErr;
    float gainIntErr;

    for(int ch=0; ch<nrChannels; ch++)
    {
        ///Option 1: Do things without finetuning
        //avgAmp = avg_vec(file->AmpAll[ch]);
        //avgInt = avg_vec(file->IntAll[ch]);
        //stdAmp = std_vec(file->AmpAll[ch],avgAmp);
        //stdInt = std_vec(file->IntAll[ch],avgInt);

        //maxInt=30*sqrt(avgInt)*sqrt(sqrt(stdInt));
        //maxAmp=20*sqrt(avgAmp)*sqrt(sqrt(stdAmp));

        ///Option 2: Do things with finetuning based on first runs without finetuning
        maxAmp = ovest*33*7;
        maxInt = ovest*200*7;
        if(ch>3)
        {
            maxAmp=ovest*16*7;
            maxInt=ovest*100*7;
        }

        minInt = 30;
        if(first)
        {
            if(ch>3 && ovest>2) minInt=ovest*50;
            if(ch<4 && ovest>2) minInt=ovest*100;
            minAmp=5;
        }
        else
        {
            minInt=0.9*file->ValleysInt[ch][0];
            minAmp=0.9*file->ValleysAmp[ch][0];
        }


        if (ch==ChToAn && file->reqbias == VoltToAn)
        {
            cout << "Ch" << ch << " Histo bereik: Int " <<  minInt << "-" << maxInt << "/ Amp "  <<  minAmp << "-" << maxAmp << endl;
        }
        TH1F histo_amp("histo_amp","",125,minAmp,maxAmp);   //FINETUNING in number of bins
        TH1F histo_int("histo_int","",125,minInt,maxInt);

        for (unsigned int p = 1; p < file->AmpAll[ch].size(); p++)
        {
            histo_amp.Fill(file->AmpAll[ch][p]);
            histo_int.Fill(file->IntAll[ch][p]);
        }

        gainAmpErr=histo_amp.GetBinWidth(5);  //random bin, does not matter
        gainIntErr=histo_int.GetBinWidth(5);

        //RESET thresholds!
        file->TopsAmp[ch].clear();
        file->TopsInt[ch].clear();
        file->ValleysInt[ch].clear();
        file->ValleysAmp[ch].clear();

        ///INTEGRAL
        p =0;
        grad = -999; //start negative
        gradp = -999;
        while(grad<0 || gradp<0)
        {
            p++;
            grad = histo_int.GetBinContent(p+1) - histo_int.GetBinContent(p);
            gradp = histo_int.GetBinContent(p+3) - histo_int.GetBinContent(p);
        }
        //First maximum
        histo_int.GetXaxis()->SetRangeUser(histo_int.GetBinCenter(p),maxInt );
        p=histo_int.GetMaximumBin();
        file->TopsInt[ch].push_back(histo_int.GetBinCenter(p));
        histo_int.GetXaxis()->UnZoom();
        //First minimum
        histo_int.GetXaxis()->SetRangeUser(minInt,file->TopsInt[ch][0]);
        file->ValleysInt[ch].push_back(histo_int.GetBinCenter(histo_int.GetMinimumBin()));
        histo_int.GetXaxis()->UnZoom();
        grad = -999; //start negative
        gradp = -999;
        while(grad<0 || gradp<0)
        {
            p++;
            grad = histo_int.GetBinContent(p+1) - histo_int.GetBinContent(p);
            gradp = histo_int.GetBinContent(p+3) - histo_int.GetBinContent(p);
        }
        //Second maximum
        histo_int.GetXaxis()->SetRangeUser(histo_int.GetBinCenter(p),maxInt);
        p=histo_int.GetMaximumBin();
        file->TopsInt[ch].push_back(histo_int.GetBinCenter(p));
        histo_int.GetXaxis()->UnZoom();
        //Second minimum
        histo_int.GetXaxis()->SetRangeUser(file->TopsInt[ch][0],
                                           file->TopsInt[ch][1]);
        file->ValleysInt[ch].push_back(histo_int.GetBinCenter(histo_int.GetMinimumBin()));
        histo_int.GetXaxis()->UnZoom();
        grad = -999; //start negative
        gradp = -999;
        while(grad<0 || gradp<0)
        {
            p++;
            grad = histo_int.GetBinContent(p+1) - histo_int.GetBinContent(p);
            gradp = histo_int.GetBinContent(p+3) - histo_int.GetBinContent(p);
        }
        //Third maximum
        histo_int.GetXaxis()->SetRangeUser(histo_int.GetBinCenter(p),maxInt);
        p=histo_int.GetMaximumBin();
        file->TopsInt[ch].push_back(histo_int.GetBinCenter(p));
        histo_int.GetXaxis()->UnZoom();
        //Third minimum
        histo_int.GetXaxis()->SetRangeUser(file->TopsInt[ch][1],
                                           file->TopsInt[ch][2]);
        file->ValleysInt[ch].push_back(histo_int.GetBinCenter(histo_int.GetMinimumBin()));
        histo_int.GetXaxis()->UnZoom();

        if(file->TopsInt[ch].size() > 2 && file->ValleysInt[ch].size() > 2)
        {
            gainInt = ((file->TopsInt[ch][2] - file->TopsInt[ch][0]) +
                      (file->ValleysInt[ch][2]- file->ValleysInt[ch][1]))/3;
            file->gainInt[ch]=gainInt;
            file->gainIntErr[ch]= gainIntErr;
        }
        else
        {
            cout<< "Could not calculate the gainInt\t V " << file->reqbias << ", T " << file->temp << ", Ch " << ch << endl;
            file->gainInt[ch]=0;
        }

        ///AMPLITUDE
        p =0;
        grad = -999; //start negative
        gradp = -999;
        while(grad<0 || gradp<0)
        {
            p++;
            grad = histo_amp.GetBinContent(p+1) - histo_amp.GetBinContent(p);
            gradp = histo_amp.GetBinContent(p+3) - histo_amp.GetBinContent(p);
        }

        //First maximum
        histo_amp.GetXaxis()->SetRangeUser(histo_amp.GetBinCenter(p),maxAmp);
        p=histo_amp.GetMaximumBin();
        file->TopsAmp[ch].push_back(histo_amp.GetBinCenter(p));
        histo_amp.GetXaxis()->UnZoom();
        //First minimum
        histo_amp.GetXaxis()->SetRangeUser(minAmp,file->TopsAmp[ch][0]);
        file->ValleysAmp[ch].push_back(histo_amp.GetBinCenter(histo_amp.GetMinimumBin()));
        //cout << "First valley is for Ch" << ch << ": "<< histo_int.GetBinCenter(histo_int.GetMinimumBin()) << endl;
        histo_amp.GetXaxis()->UnZoom();
        grad = -999; //start negative
        gradp = -999;
        while(grad<0 || gradp<0)
        {
            p++;
            grad = histo_amp.GetBinContent(p+1) - histo_amp.GetBinContent(p);
            gradp = histo_amp.GetBinContent(p+3) - histo_amp.GetBinContent(p);
        }
        //Second maximum
        histo_amp.GetXaxis()->SetRangeUser(histo_amp.GetBinCenter(p),maxAmp);
        p=histo_amp.GetMaximumBin();
        file->TopsAmp[ch].push_back(histo_amp.GetBinCenter(p));
        histo_amp.GetXaxis()->UnZoom();
        //Second minimum
        histo_amp.GetXaxis()->SetRangeUser(file->TopsAmp[ch][0],file->TopsAmp[ch][1]);
        file->ValleysAmp[ch].push_back(histo_amp.GetBinCenter(histo_amp.GetMinimumBin()));
        histo_amp.GetXaxis()->UnZoom();
        grad = -999; //start negative
        gradp = -999;
        while(grad<0 || gradp<0)
        {
            p++;
            grad = histo_amp.GetBinContent(p+1) - histo_amp.GetBinContent(p);
            gradp = histo_amp.GetBinContent(p+3) - histo_amp.GetBinContent(p);
        }
        //Second maximum
        histo_amp.GetXaxis()->SetRangeUser(histo_amp.GetBinCenter(p),maxAmp);
        p=histo_amp.GetMaximumBin();
        file->TopsAmp[ch].push_back(histo_amp.GetBinCenter(p));
        histo_amp.GetXaxis()->UnZoom();
        //Second minimum
        histo_amp.GetXaxis()->SetRangeUser(file->TopsAmp[ch][1],file->TopsAmp[ch][2]);
        file->ValleysAmp[ch].push_back(histo_amp.GetBinCenter(histo_amp.GetMinimumBin()));
        histo_amp.GetXaxis()->UnZoom();

        if(file->TopsAmp[ch].size() > 2 && file->ValleysAmp[ch].size() > 2)
        {
            gainAmp = (file->ValleysAmp[ch][2]- file->ValleysAmp[ch][1]+file->TopsAmp[ch][2]- file->TopsAmp[ch][0])/3;
            file->gainAmp[ch]=gainAmp;
            file->gainAmpErr[ch]= gainAmpErr;
        }
        else
        {
            cout<< "Could not calculate the gainAmp\t V " << file->reqbias << ", T " << file->temp << ", Ch " << ch << endl;
            file->gainAmp[ch]=0;
        }
    }
}


void CTandDCRcalculator(MEASUREMENT* file)
{
    float allpeaksAmp;
    float allpeaksInt;

    float allpeaksAmpCT;
    float allpeaksIntCT;

    float allpeaksAmpCTT;
    float allpeaksIntCTT;

    float CTcorr;
    float fitSlope;
    float fitSlopeerror;

    vector<float> amp_value(0);
    vector<float> amp_error(0);

    vector<float> int_value(0);
    vector<float> int_error(0);

    vector<int> countInt0(0);
    vector<int> countAmp0(0);
    vector<int> countInt1(0);
    vector<int> countAmp1(0);
    vector<int> countInt2(0);
    vector<int> countAmp2(0);

    vector<float> fit(0);
    vector<float> fitErr(0);

    for(int ch=0; ch<nrChannels; ch++)
    {
        for(unsigned int peak=0; peak < file->IntAll[ch].size(); peak++)
        {
            if(file->AmpAll[ch][peak]>file->ValleysAmp[ch][2])
              file->peaksAmp[ch][2]++;
            else if(file->AmpAll[ch][peak]>file->ValleysAmp[ch][1])
              file->peaksAmp[ch][1]++;
            else if(file->AmpAll[ch][peak]>file->ValleysAmp[ch][0])
              file->peaksAmp[ch][0]++;

            if(file->IntAll[ch][peak]>file->ValleysInt[ch][2])
              file->peaksInt[ch][2]++;
            else if(file->IntAll[ch][peak]>file->ValleysInt[ch][1])
              file->peaksInt[ch][1]++;
            else if(file->IntAll[ch][peak]>file->ValleysInt[ch][0])
              file->peaksInt[ch][0]++;
        }

        allpeaksInt=0;  //number of peaks with one avalanche or more
        for (int n : file->peaksInt[ch]) allpeaksInt += n;
        allpeaksIntCT=allpeaksInt-file->peaksInt[ch][0]; //number of peaks with at least two avalanches
        allpeaksIntCTT=allpeaksIntCT-file->peaksInt[ch][1];

        allpeaksAmp=0;  //number of peaks with one avalanche or more
        for (int n : file->peaksAmp[ch]) allpeaksAmp += n;
        allpeaksAmpCT=allpeaksAmp-file->peaksAmp[ch][0]; //number of peaks with at least two avalanches
        allpeaksAmpCTT=allpeaksAmpCT-file->peaksAmp[ch][1];

        ///DARK COUNT RATE
        countAmp0.push_back(allpeaksAmp);
        countInt0.push_back(allpeaksInt);
        countAmp1.push_back(allpeaksAmpCT);
        countInt1.push_back(allpeaksIntCT);
        countAmp2.push_back(allpeaksAmpCTT);
        countInt2.push_back(allpeaksIntCTT);
        //cout << allpeaksAmp << " "<<allpeaksAmpCT<<" "<<allpeaksIntCTT<< endl;
        {
            TH1F h_time_intervals("h_time_intervals","", 1024,1,1024);
            for(unsigned int i=0; i < file->peakDistributionVec[ch].size(); i++)
            {
                h_time_intervals.Fill(file->peakDistributionVec[ch][i]);
            }
            h_time_intervals.Fit("expo","Q0","",afterpulsebuffer,1000);
            CTcorr = (float)  (exp(h_time_intervals.GetFunction("expo")->GetParameter(0)));
            fitSlope= (float)  -1*h_time_intervals.GetFunction("expo")->GetParameter(1);
            fitSlopeerror= (float)  h_time_intervals.GetFunction("expo")->GetParError(1);
            fit.push_back( fitSlope );
            fitErr.push_back(fitSlopeerror);

        }

        ///CROSSTALK
        amp_value.push_back(  (allpeaksAmpCT-CTcorr)/allpeaksAmp    );
        amp_error.push_back(  amp_value.back()*( sqrt( 1/allpeaksAmp + 1/allpeaksAmpCT   )));

        int_value.push_back(  (allpeaksIntCT-CTcorr)/allpeaksInt   );
        int_error.push_back(  int_value.back()*( sqrt( 1/allpeaksInt + 1/allpeaksIntCT   )));
    }
    file->crosstalkAmp=amp_value;
    file->crosstalkInt=int_value;
    file->CT_errorAmp=amp_error;
    file->CT_errorInt=int_error;
    file->DCRcountAmp0=countAmp0;
    file->DCRcountInt0=countInt0;
    file->DCRcountAmp1=countAmp1;
    file->DCRcountInt1=countInt1;
    file->DCRcountAmp2=countAmp2;
    file->DCRcountInt2=countInt2;
    file->DCRfit=fit;
    file->DCRfitErr=fitErr;
}

void WriteAll(MEASUREMENT* file)
{
    string writeline;
    Double_t temp = file->temp;
    Double_t reqbias= file->reqbias;

    float gainInt;
    float gainIntError;
    float gainAmp;
    float gainAmpError;

    float DCRfit;
    float DCRfitError;

    float CTvalInt;
    float CTerrInt;
    float CTvalAmp;
    float CTerrAmp;

    int DCRcountInt0; //poisson, no need for extra errors
    int DCRcountAmp0; //0.5PA

    int DCRcountInt1; //1.5PA
    int DCRcountAmp1;

    int DCRcountInt2; //2.5PA
    int DCRcountAmp2;

    //float ovest= file->reqbias - 61.3 -0.06*file->temp;
    float ovest = ovest = 1.0255*file->reqbias+0.055*(25-file->temp)-64.3;
    float exAmp1 = ovest*34.8;
    float exInt1 = ovest*206;
    float exAmp2 = ovest*16.1;
    float exInt2 = ovest*103;
    bool ok=false;

    for(int ch=0; ch<nrChannels; ch++)
    {


        gainInt = file->gainInt[ch];
        gainAmp = file->gainAmp[ch];

        gainIntError = file->gainIntErr[ch];
        gainAmpError = file->gainAmpErr[ch];

        DCRfit = file->DCRfit[ch];
        DCRfitError = file->DCRfitErr[ch];

        CTvalInt = file->crosstalkInt[ch];
        CTerrInt = file->CT_errorInt[ch];
        CTvalAmp = file->crosstalkAmp[ch];
        CTerrAmp = file->CT_errorAmp[ch];

        DCRcountInt0=file->DCRcountInt0[ch];
        DCRcountAmp0=file->DCRcountAmp0[ch];

        DCRcountInt1=file->DCRcountInt1[ch];
        DCRcountAmp1=file->DCRcountAmp1[ch];

        DCRcountInt2=file->DCRcountInt2[ch];
        DCRcountAmp2=file->DCRcountAmp2[ch];

        ok=false;
        /// Finetuning that checks data for consistency with expected results from earlier runs, throws away data with low of high overvoltages and could be removed if the peakfinder is upgraded to a better one.
        if(DCRfit>0 && CTvalInt>0&& CTerrInt>0&& CTvalAmp>0&& CTerrAmp>0 && CTvalAmp < 0.2*ovest+0.075 && CTvalInt < 0.2*ovest+0.075 )
        {
            if(ch<4)
            {
                if(gainAmp > exAmp1/2-10 && gainAmp < exAmp1*2+10 && gainInt > exInt1/2-30 && gainInt < exInt1*2+30)
                {
                    ok=true;
                }
            }
            if(ch>3)
            {
                if(gainAmp > exAmp2/2-6 && gainAmp < exAmp2*2+6 && gainInt > exInt2-18 && gainInt < exInt2*2+18)
                {
                    ok=true;
                }
            }
        }
        if(ok)
        {
            ofstream myfile;
            myfile.open ("AnalysisResults.txt", ios::out | ios::app );
            writeline = to_string_wp(reqbias,3) + "\t" +to_string_wp(temp,3) + "\t" + to_string(ch) + "\t" + to_string_wp(gainInt,3) + "\t" + to_string_wp(gainAmp,3)+ "\t";
            writeline+= to_string_wp(DCRcountInt0,3)+"\t" + to_string_wp(DCRcountAmp0,3)+"\t" + to_string_wp(DCRfit,3)+ "\t";
            writeline+= to_string_wp(CTvalInt,3)+"\t" + to_string_wp(CTerrInt,3)+"\t" + to_string_wp(CTvalAmp,3)+ "\t" + to_string_wp(CTerrAmp,3)+ "\t";
            writeline+= to_string_wp(DCRfitError,3)+"\t" + to_string_wp(gainIntError,3)+"\t" + to_string_wp(gainAmpError,3)+ "\t";
            writeline+= to_string_wp(DCRcountInt1,3)+"\t" + to_string_wp(DCRcountInt2,3)+ "\t";
            writeline+= to_string_wp(DCRcountAmp1,3)+"\t" + to_string_wp(DCRcountAmp2,3)+ "\n";
            myfile << writeline;
            myfile.close();
            /*
            0:  Voltage
            1:  Temperature
            2:  Channel
            3:  Gain from Integral
            4:  Gain from Amplitude
            5:  DCRcountInt0
            6:  DCRcountAmp0
            7:  DCR from Fit
            8:  CT from Integral
            9:  CT error from Integral
            10: CT from Amplitude
            11: CT error from Amplitude
            12: DCR from fit error
            13: Gain from Integral error
            14: Gain from Amplitude error
            15: DCRcountInt1
            16: DCRcountInt2
            17: DCRcountAmp1
            18: DCRcountAmp2
            */
            counter++;
        }
        else
        {
            cout << "Gain out of range: Ch" << ch << " "<< file->name.Data() << endl;
        }
    }
}

///(TempToAn,VoltToAn,ChToAn)
void CTandTimeDistriOneFile(MEASUREMENT* file)
{
    cout << "-----------------------------------------------" << endl;
    TH1F* h_peaksAmp = new TH1F("h_peaksAmp","", 200,-file->ValleysAmp[ChToAn][0]*.1,16*file->gainAmp[ChToAn]);
    TH1F* h_peaksInt = new TH1F("h_peaksInt","", 200,-file->ValleysInt[ChToAn][0]*.1,16*file->gainInt[ChToAn]);
    for(unsigned int peak=0; peak < file->IntAll[ChToAn].size(); peak++)
    {
        h_peaksAmp->Fill(file->AmpAll[ChToAn][peak]);
        h_peaksInt->Fill(file->IntAll[ChToAn][peak]);
    }
    std::ofstream output_file1("./amps.txt");
    std::ostream_iterator<float> output_iterator1(output_file1, "\n");
    std::copy(file->AmpAll[ChToAn].begin(), file->AmpAll[ChToAn].end(), output_iterator1);

    std::ofstream output_file2("./ints.txt");
    std::ostream_iterator<float> output_iterator2(output_file2, "\n");
    std::copy(file->IntAll[ChToAn].begin(), file->IntAll[ChToAn].end(), output_iterator2);
    //TAxis *axis = h_peaksInt->GetXaxis();
    //int bmin = axis->FindBin(644);
    //int bmax = axis->FindBin(10000);
    //cout << h_peaksInt->Integral(bmin,bmax) << endl;

    //Make plots
    string canvasname = "OVERVIEW \t - \t Temperature: " + to_string_wp(TempToAn,5) + ", reqbias: " + to_string_wp(VoltToAn,3)+ ", Ch: " + to_string(ChToAn) + ", Event " + to_string(eventnr);
    TCanvas * c = new TCanvas("c",canvasname.c_str(),1920*2,1080*2);
    c->Divide(2,2);
    int sampling =1;
    TH1F* h_time_intervals =  new TH1F("h_time_intervals","", 1024/sampling,1,1024);

    for(unsigned int i=0; i < file->peakDistributionVec[ChToAn].size(); i++)
    {
        h_time_intervals->Fill(file->peakDistributionVec[ChToAn][i]);
    }

    c->cd(1);
    h_time_intervals->Draw();
    string timeintervalsname = "Time intervals;time between peaks [samples, 25ns];events / " + to_string(sampling*25) + " ns";
    h_time_intervals->SetTitle(timeintervalsname.c_str());
    h_time_intervals->Fit("expo","","",afterpulsebuffer,1000);
    TF1 *fit = h_time_intervals->GetFunction("expo");
    //double CTcorr = exp(fit->GetParameter(0))/sampling;

    c->cd(3);
    gPad->SetLogy();
    h_peaksAmp->Draw();
    h_peaksAmp->SetTitle("Peak Amplitude;peak amplitude [ADC counts];events");

    c->cd(2);
    string gTitle = "Example waveform (Temperature: " + to_string_wp(TempToAn,5) + ", reqbias: " + to_string_wp(VoltToAn,3) + ", Ch: " + to_string(ChToAn) + ") Event " + to_string(eventnr)+ ";time [25ns samples];ADC counts";
    g->SetTitle(gTitle.c_str());
    g->SetLineColor(kBlue);
    g->Draw();
    g->GetXaxis()->SetRangeUser(0,nrSamples);
    ColorPeaks(yaxis,file->ValleysAmp[ChToAn][0]);
    //cout << file->ValleysAmp[ChToAn][0] << endl;

    c->cd(4);
    gPad->SetLogy();
    h_peaksInt->Draw();
    h_peaksInt->SetTitle("Peak Integral;peak integral;events");

    c->Update();
    string picturename = "Plots/T" + to_string_wp(TempToAn,3) + "reqbias" + to_string_wp(VoltToAn,3) + "Ch" + to_string(ChToAn) + "_Ev" + to_string(eventnr) + ".png";
    c->SaveAs(picturename.c_str());

    //Output in terminal, similar as in the output file
    float gainInt = file->gainInt[ChToAn];
    float gainAmp = file->gainAmp[ChToAn];
    float gainIntError = file->gainIntErr[ChToAn];
    float gainAmpError = file->gainAmpErr[ChToAn];

    float DCRint =file->DCRcountInt0[ChToAn];
    float DCRamp =file->DCRcountAmp0[ChToAn];
    float DCRfit =file->DCRfit[ChToAn];
    float DCRfitError=file->DCRfitErr[ChToAn];

    float CTvalInt=file->crosstalkInt[ChToAn];
    float CTerrInt = file->CT_errorInt[ChToAn];
    float CTvalAmp = file->crosstalkAmp[ChToAn];
    float CTerrAmp = file->CT_errorAmp[ChToAn];

    cout << "-----------------------------------------------" << endl;
    cout << "------------Results for one setting------------" << endl;
    cout << "-----------------------------------------------" << endl;
    string writeline = "V " + to_string_wp(file->reqbias,3) + "\t T " +to_string_wp(file->temp,3) + "\t Ch" + to_string(ChToAn) + "\n";
    writeline+= "gainInt: " + to_string_wp(gainInt,3) +"+/-" + to_string_wp(gainIntError,3)+ "\t gainAmp: " + to_string_wp(gainAmp,3)+"+/-" + to_string_wp(gainAmpError,3)+ "\n";
    writeline+= "DCRint " + to_string_wp(DCRint,3)+"\t DCRamp: " + to_string_wp(DCRamp,3)+"\t DCRfit: " + to_string_wp(DCRfit,3)+"+/-" + to_string_wp(DCRfitError,3)+ "\n";
    writeline+= "CTvalInt: " + to_string_wp(CTvalInt,3)+"+/-" + to_string_wp(CTerrInt,3)+"\t CTvalAmp: " + to_string_wp(CTvalAmp,3)+ "+/-" + to_string_wp(CTerrAmp,3)+ "\n";

    ///For comparison with analytical models

    float integt = 372;
    float ampt = 59;
    int bmin;
    int bmax;

    vector<float> intint;
    vector<float> ampamp;
    vector<float> intinterr;
    vector<float> ampamperr;
    for(int i = 1; i<15; i++)
    {
        TAxis *axisi = h_peaksInt->GetXaxis();
        bmin = axisi->FindBin((i-.5)*integt);
        bmax = axisi->FindBin((i+.5)*integt);
        intint.push_back (h_peaksInt->Integral(bmin,bmax));

        TAxis *axisa = h_peaksAmp->GetXaxis();
        bmin = axisa->FindBin((i-.5)*ampt);
        bmax = axisa->FindBin((i+.5)*ampt);
        ampamp.push_back(h_peaksAmp->Integral(bmin,bmax));
    }
    float sumamp = h_peaksAmp->Integral(1,199);
    float sumint = h_peaksInt->Integral(1,199);

    cout << "yintegral" << ChToAn <<"=[";
    for(int i = 0; i<14; i++)
    {
        intinterr.push_back(sqrt(intint[i])/sumint);
        intint[i]/=sumint;
        cout << intint[i] << ",";
    }
    intinterr.push_back(sqrt(intint[14])/sumint);
    cout <<  intint[14]/sumint << "]"<< endl;
    cout << "interr=[";
    for(int i = 0; i<14; i++)
    {
        cout << intinterr[i] << ",";
    }
    cout <<  intinterr[14]/sumint << "]"<<endl;
    cout << "yamplitude" << ChToAn <<"=[";
    for(int i = 0; i<14; i++)
    {
        ampamperr.push_back(sqrt(ampamp[i])/sumamp);
        ampamp[i]/=sumamp;
        cout << ampamp[i] << ",";
    }
    ampamperr.push_back(sqrt(ampamp[14])/sumamp);
    cout <<  ampamp[14]/sumamp << "]"<<endl;
    cout << "amperr=[";
    for(int i = 0; i<14; i++)
    {
        cout << ampamperr[i] << ",";
    }
    cout <<  ampamperr[14]/sumamp << "]"<<endl;

    cout << writeline << endl;
    cout << "----------------------------------------------" << endl;
//    cout << "amplitude valleys: " << file->ValleysAmp[ChToAn][0] << "\t" << file->ValleysAmp[ChToAn][1] << "\t" << file->ValleysAmp[ChToAn][2] << endl;
//    cout << "amplitude tops: " << file->TopsAmp[ChToAn][0] << "\t" << file->TopsAmp[ChToAn][1] << "\t" << file->TopsAmp[ChToAn][2] << endl;
//
//    cout << "Integral valleys: " << file->ValleysInt[ChToAn][0] << "\t" << file->ValleysInt[ChToAn][1] << "\t" << file->ValleysInt[ChToAn][2] << endl;
//    cout << "Integral tops: " << file->TopsInt[ChToAn][0] << "\t" << file->TopsInt[ChToAn][1] << "\t" << file->TopsInt[ChToAn][2] << endl;
//    for(int ch=0; ch<nrChannels; ch++)
//    {
//        cout  << ch << "\t"<<file->vop[ch]<<  "\t"<<file->gain[ch]<<  "\t"<<file->dcr[ch]<< endl;
//    }

}
