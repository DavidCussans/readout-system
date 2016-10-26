//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Tue Apr  5 14:37:35 2016 by ROOT version 6.05/02
// from TTree conditions/conditions
// found on file: sipmcalib_63.00V_10.00C_16Mar2016_1451.root
//////////////////////////////////////////////////////////

#ifndef conditions_h
#define conditions_h

#include <TROOT.h>
#include <TChain.h>
#include <TFile.h>

// Header file for the classes stored in the TTree if any.
#include <vector>

using namespace std;

class conditions {
public :
   TTree          *fChain;   //!pointer to the analyzed TTree or TChain
   Int_t           fCurrent; //!current Tree number in a TChain

// Fixed size dimensions of array or collections stored in the TTree if any.

   // Declaration of leaf types
   Double_t        reqbias;
   Double_t        measbias;
   Double_t        temp;
   vector<double>  *trims;

   // List of branches
   TBranch        *b_reqbias;   //!
   TBranch        *b_measbias;   //!
   TBranch        *b_temp;   //!
   TBranch        *b_trims;   //!

   conditions(TTree *tree=0);
   virtual ~conditions();
   virtual Int_t    GetEntry(Long64_t entry);
   virtual Long64_t LoadTree(Long64_t entry);
   virtual void     Init(TTree *tree);
   //virtual void     Loop();
   virtual void     Show(Long64_t entry = -1);
};

conditions::conditions(TTree *tree) : fChain(0)
{
// if parameter tree is not specified (or zero), connect the file
// used to generate this class and read the Tree.
   if (tree == 0) {
      TFile *f = (TFile*)gROOT->GetListOfFiles()->FindObject("sipmcalib_63.00V_10.00C_16Mar2016_1451.root");
      if (!f || !f->IsOpen()) {
         f = new TFile("sipmcalib_63.00V_10.00C_16Mar2016_1451.root");
      }
      f->GetObject("conditions",tree);

   }
   Init(tree);
}

conditions::~conditions()
{
   if (!fChain) return;
   delete fChain->GetCurrentFile();
}

Int_t conditions::GetEntry(Long64_t entry)
{
// Read contents of entry.
   if (!fChain) return 0;
   return fChain->GetEntry(entry);
}
Long64_t conditions::LoadTree(Long64_t entry)
{
// Set the environment to read one entry
   if (!fChain) return -5;
   Long64_t centry = fChain->LoadTree(entry);
   if (centry < 0) return centry;
   if (fChain->GetTreeNumber() != fCurrent) {
      fCurrent = fChain->GetTreeNumber();
   }
   return centry;
}

void conditions::Init(TTree *tree)
{
   // The Init() function is called when the selector needs to initialize
   // a new tree or chain. Typically here the branch addresses and branch
   // pointers of the tree will be set.
   // It is normally not necessary to make changes to the generated
   // code, but the routine can be extended by the user if needed.
   // Init() will be called many times when running on PROOF
   // (once per file to be processed).

   // Set object pointer
   trims = 0;
   // Set branch addresses and branch pointers
   if (!tree) return;
   fChain = tree;
   fCurrent = -1;
   fChain->SetMakeClass(1);

   fChain->SetBranchAddress("reqbias", &reqbias, &b_reqbias);
   fChain->SetBranchAddress("measbias", &measbias, &b_measbias);
   fChain->SetBranchAddress("temp", &temp, &b_temp);
   fChain->SetBranchAddress("trims", &trims, &b_trims);
}

void conditions::Show(Long64_t entry)
{
// Print contents of entry.
// If entry is not specified, print current entry
   if (!fChain) return;
   fChain->Show(entry);
}
#endif // #ifdef conditions_cxx
