//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Jun 28 15:47:59 2016 by ROOT version 5.34/32
// from TTree waveforms/waveforms
// found on file: ../rawFiles/sipmcalib_62.30V_16.00C_16Mar2016_1721.root
//////////////////////////////////////////////////////////

#ifndef waveforms_h
#define waveforms_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include <vector>

using std::vector;

// Fixed size dimensions of array or collections stored in the TTree if any.

class waveforms {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

   // Declaration of leaf types
   vector<float>   *wf_chan0;
   vector<float>   *wf_chan1;
   vector<float>   *wf_chan2;
   vector<float>   *wf_chan3;
   vector<float>   *wf_chan4;
   vector<float>   *wf_chan5;
   vector<float>   *wf_chan6;
   vector<float>   *wf_chan7;

   // List of branches
   TBranch        *b_wf_chan0;   //!
   TBranch        *b_wf_chan1;   //!
   TBranch        *b_wf_chan2;   //!
   TBranch        *b_wf_chan3;   //!
   TBranch        *b_wf_chan4;   //!
   TBranch        *b_wf_chan5;   //!
   TBranch        *b_wf_chan6;   //!
   TBranch        *b_wf_chan7;   //!

   waveforms(TTree *tree=0);
   virtual ~waveforms();
   virtual Int_t    Cut(Long64_t entry);
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   virtual void     Loop();
   virtual Bool_t   Notify();
   virtual void     Show(Long64_t entry = -1);
};

#endif

#ifdef waveforms_cxx
waveforms::waveforms(TTree *tree) : fChain(0) 
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("../rawFiles/sipmcalib_62.30V_16.00C_16Mar2016_1721.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("../rawFiles/sipmcalib_62.30V_16.00C_16Mar2016_1721.root");
      }
      f->GetObject("waveforms",tree);

   }
   Init(tree);
}

waveforms::~waveforms()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t waveforms::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t waveforms::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
      Notify();
   }
   return centry;
}

void waveforms::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   wf_chan0 = 0;
   wf_chan1 = 0;
   wf_chan2 = 0;
   wf_chan3 = 0;
   wf_chan4 = 0;
   wf_chan5 = 0;
   wf_chan6 = 0;
   wf_chan7 = 0;
   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("wf_chan0", &wf_chan0, &b_wf_chan0);
   fChain->SetBranchAddress("wf_chan1", &wf_chan1, &b_wf_chan1);
   fChain->SetBranchAddress("wf_chan2", &wf_chan2, &b_wf_chan2);
   fChain->SetBranchAddress("wf_chan3", &wf_chan3, &b_wf_chan3);
   fChain->SetBranchAddress("wf_chan4", &wf_chan4, &b_wf_chan4);
   fChain->SetBranchAddress("wf_chan5", &wf_chan5, &b_wf_chan5);
   fChain->SetBranchAddress("wf_chan6", &wf_chan6, &b_wf_chan6);
   fChain->SetBranchAddress("wf_chan7", &wf_chan7, &b_wf_chan7);
   Notify();
}

Bool_t waveforms::Notify()
{
   // The Notify() function is called when a new file is opened. This
   // can be either for a new TTree in a TChain or when when a new TTree
   // is started when using PROOF. It is normally not necessary to make changes
   // to the generated code, but the routine can be extended by the
   // user if needed. The return value is currently not used.

   return kTRUE;
}

void waveforms::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
Int_t waveforms::Cut(Long64_t entry)
{
// This function may be called from Loop.
// returns  1 if entry is accepted.
// returns -1 otherwise.
   return 1;
}
#endif // #ifdef waveforms_cxx
