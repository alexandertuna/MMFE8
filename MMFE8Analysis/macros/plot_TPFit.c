// Includes
#include <vector>
#include <string>
#include <TCanvas.h>
#include <TStyle.h>
#include <TGraphErrors.h>
#include "../include/TPFitBase.hh"

using namespace std;


/************ User-editable constants ************/
const string input_filename = \
  "../../mmfe8_gui/CalibrationRoutine/mmfe8_CalibRoutine.root";
const int vmm = 3;

/*********************       CODE      *******************/
const string plot_name = "Input charge vs. test pulse DAC";
const string tree_name = "TPFit";
const int max_N = 20;

void plot_TPFit(){
  // Open tree
  TChain* tree = new TChain(tree_name.c_str(), tree_name.c_str());
  tree->AddFile(input_filename.c_str());
  int N = 0;
  double meanQ[max_N], tpDAC[max_N], sigQ[max_N];
  int tree_items = tree->GetEntries();
  TPFitBase* base = new TPFitBase(tree);

  for (int i = 0; i < tree_items; i++){
    base->GetEntry(i);
    if (base->VMM == vmm){
      tpDAC[N] = base->TPDAC;
      meanQ[N] = base->MeanQ;
      sigQ[N] = base->SigmaQ;
      cout << "Point " << N << ": tpDAC " << tpDAC[N];
      cout << ", Mean " << meanQ[N] << ", Sigma " << sigQ[N] << endl;
      N++;
    }
  }
  TGraphErrors* plot = new TGraphErrors(N, tpDAC, meanQ, 0, sigQ);
  TCanvas* can = new TCanvas("can","can",1200,1000);
  can->SetTopMargin(0.1);
  plot->SetTitle(plot_name.c_str());
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);

  can->Draw();
  can->SetGridx();
  can->SetGridy();
  can->cd();

  plot->GetXaxis()->SetTitle("Test pulse DAC");
  plot->GetXaxis()->CenterTitle();
  plot->GetXaxis()->SetTitleOffset(1.1);
  plot->GetYaxis()->SetTitle("Input charge (fC)");
  plot->GetYaxis()->SetTitleOffset(1.4);
  plot->GetYaxis()->CenterTitle();
  plot->GetXaxis()->SetRangeUser(0., 220.);
  plot->GetYaxis()->SetRangeUser(0.,120.);
  plot->SetMarkerStyle(4);
  plot->SetMarkerColor(kAzure + 10);
  plot->SetMarkerSize(3);
  plot->Draw("ap");
}
