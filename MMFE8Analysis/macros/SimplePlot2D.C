#include <iostream>
#include <TCanvas.h>
#include <TChain.h>
#include <TH2D.h>
#include <TStyle.h>

#include "include/MMFE8Base.hh"

using namespace std;

void SimplePlot2D(){

  string filename = "test.root";
  string varXname = "PDO";
  string varYname = "VMM #";
  
  
  ///////////////////////////////////////////////////////
  
  TChain* tree = new TChain("MMFE8","MMFE8");

  tree->AddFile(filename.c_str());

  MMFE8Base* base = new MMFE8Base(tree);

  int N = tree->GetEntries();

  TH2D* hist = new TH2D("hist","hist", 1000, 0.0, 1000.,8,0.5,8.5);

  for(int i = 0; i < N; i++){
    base->GetEntry(i);

    if(base->CHpulse != base->CHword)
      continue;

    if(base->CHpulse != 7)
      continue;

    if(base->VMM == 2)
      continue;

    hist->Fill(base->PDO,base->VMM);
  
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
  hist->Draw("COLZ");
  
  hist->GetXaxis()->SetTitle(varXname.c_str());
  hist->GetXaxis()->CenterTitle();
  hist->GetYaxis()->SetTitle(varYname.c_str());
  hist->GetYaxis()->CenterTitle();
  hist->GetYaxis()->SetTitleOffset(1.4);
  hist->GetYaxis()->CenterTitle();
  //hist->GetYaxis()->SetRangeUser(0.,hist->GetMaximum()*1.1) ;
			     
}
