#include <iostream>
#include <TCanvas.h>
#include <TH1D.h>
#include <TStyle.h>

#include "include/MMFE8Base.hh"

using namespace std;

void SimplePlot1D(){

  string filename = "fakefile.dat.root";
  string varname = "VMM";
  
  
  ///////////////////////////////////////////////////////
  
  TChain* tree = new TChain("MMFE8","MMFE8");

  tree->AddFile(filename.c_str());

  MMFE8Base* base = new MMFE8Base(tree);

  int N = tree->GetEntries();

  TH1D* hist = new TH1D("hist","hist", 8, 0.5, 8.5);

  for(int i = 0; i < N; i++){
    base->GetEntry(i);
    cout << "VMM # " << base->VMM << endl;

    hist->Fill(base->VMM);
  
  }

  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.05);
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);

  can->Draw();
  can->SetGridx();
  can->SetGridy();
  
  can->cd();
  hist->Draw();
  
  hist->GetXaxis()->SetTitle(varname.c_str());
  hist->GetXaxis()->CenterTitle();
  hist->GetYaxis()->SetTitle("N events");
  hist->GetYaxis()->SetTitleOffset(1.4);
  hist->GetYaxis()->CenterTitle();
  hist->GetYaxis()->SetRangeUser(0.,hist->GetMaximum()*1.1) ;

  TFile* test = new TFile("test.root","RECREATE");
  test->cd();
  can->Write();
  test->Close();
			     
}
