#include <iostream>
#include <vector>
#include <TCanvas.h>
#include <TH2D.h>
#include <TF1.h>
#include <TStyle.h>
#include <TLegend.h>

#include "../include/xADCBase.hh"

using namespace std;

/*
 * Graphing pulse DAC calibration data using ROOT's VIOLIN option in TH2s.
 */

void pulseDAC_candleplot(){

  string filename = "../xADC_testdata.root";
  string yvar = "xADC voltage (V)";
  string xvar = "pulse DAC value (counts)";
  string outputfile = "./xADC_test1";
  string title = "VMM1 pulse DAC linearity";

  int vmm = 1;
  //int pdacs[] = {20, 40, 60, 80, 100, 120, 140};
  int colors[] = {kViolet+8, kBlue+4, kBlue, kAzure+10, kTeal-5, \
    kTeal+3, kGreen+1, kSpring-8};

  ///////////////////////////////////////////////////////

  TChain* tree = new TChain("MMFE8","MMFE8");

  tree->AddFile(filename.c_str());

  xADCBase* base = new xADCBase(tree);

  int N = tree->GetEntries();

  /*
  int num_vmms = sizeof(vmms) / sizeof(int);
  int num_pdacs = sizeof(pdacs) / sizeof(int);

  vector<TH1D*> hists;
  TLegend* legend = new TLegend(0.65, 0.8, 0.98, 0.98, varname.c_str());

  for (int i = 0; i < num_pdacs; i++) {
    string name = "hist PDAC value " + to_string(pdacs[i]);
    hists.push_back(new TH1D(name.c_str(), "hist", 2048, -0.00013, 1.00013));
  }*/
  TH2D* hist = new TH2D("Violin Plot", title.c_str(), 16, -10.0, 310.0, 4096, -0.00013, 1.00013);

  int min_PDAC = 0;
  int max_PDAC = 0;
  int max_XADC = 0;

  for (int i = 0; i < N; i++){
    base->GetEntry(i);
    //cout << "VMM # " << base->VMM << endl;

    if ((vmm == base->VMM) && !(base->CKTPrunning)) {
      hist->Fill(base->PDAC, float(base->XADC) / 4096.0);
      if (base->PDAC > max_PDAC){
        max_PDAC = base->PDAC;
      } else if (base->PDAC < min_PDAC) {
        min_PDAC = base->PDAC;
      }
      if (base->XADC > max_XADC){
        max_XADC = base->XADC;
      }
    }
  }

  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.1);
  hist->SetTitleOffset(0.02);
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);
  //gStyle->SetOptTitle(0);

  can->Draw();
  can->SetGridx();
  can->SetGridy();

  can->cd();
  hist->GetXaxis()->SetTitle(xvar.c_str());
  hist->GetXaxis()->CenterTitle();
  hist->GetXaxis()->SetTitleOffset(1.1);
  hist->GetYaxis()->SetTitle(yvar.c_str());
  hist->GetYaxis()->SetTitleOffset(1.4);
  hist->GetYaxis()->CenterTitle();
  hist->GetXaxis()->SetRangeUser(min_PDAC - 5, max_PDAC + 5);
  hist->GetYaxis()->SetRangeUser(0.,max_XADC/4096.*1.1);
  hist->Draw("CANDLE");

  TFile* test = new TFile((outputfile + ".root").c_str(),"RECREATE");
  test->cd();
  can->Write();
  test->Close();
}
