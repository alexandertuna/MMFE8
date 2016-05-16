#include <string>
#include <iostream>
#include <vector>
#include <TCanvas.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TStyle.h>
#include <TLegend.h>

#include "include/MMFE8Base.hh"

using namespace std;


void Plot_2D_BCID(){

  //string filename = "data/BCID_02May16/BCID_test_1.root";
  string filename = "alltest.root";
  
  int iVMM = 7;
  int iCH  = 15;

  int idelay = 0;

  ///////////////////////////////////////////////////////

  TChain* tree = new TChain("VMM_data","VMM_data");

  tree->AddFile(filename.c_str());

  MMFE8Base* base = new MMFE8Base(tree);
  //base->PulseNum = 0;

  int N = tree->GetEntries();

  TH1D* hist = new TH1D("hist","hist", 9, -4.5, 4.5);
  TH2D* hist2D = new TH2D("hist2D","hist2D", 100, 0., 100., 9, -4.5, 4.5);

  TH1D* hist_BCID[100];
  char *hname = new char[50];
  for(int i = 0; i < 100; i++){
    sprintf(hname,"hist_%d",i);
    hist_BCID[i] = (TH1D*) new TH1D(hname,
				    hname, 
				    5000, -0.5, 4999.5);
  }

  for (int i = 0; i < N; i++){
    base->GetEntry(i);

    if(base->Delay != idelay)
      continue;

    if(base->VMM != iVMM)
      continue;

    if(base->CHpulse != iCH)
      continue;

    if(base->CHword != iCH)
      continue;
    
    hist->Fill(base->BCID-1001);
    hist2D->Fill(base->TDO, base->BCID-1001);
  }
  

  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.05);
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);

  can->SetLogy();
  can->Draw();
  can->SetGridx();
  can->SetGridy();

  can->cd();
  
  hist->Draw();
  hist->GetXaxis()->SetTitle("BCID - 1001");
  hist->GetXaxis()->CenterTitle();
  hist->GetYaxis()->SetTitle("N events");
  hist->GetYaxis()->SetTitleOffset(1.4);
  hist->GetYaxis()->CenterTitle();
  hist->GetYaxis()->SetRangeUser(0.1,hist->GetMaximum()*1.1);

  TCanvas* can2D = new TCanvas("can2D","can2D",600,500);
  can2D->SetTopMargin(0.05);
  can2D->SetLeftMargin(0.12);
  can2D->SetRightMargin(0.21);
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);

  can2D->SetLogz();
  can2D->Draw();
  can2D->SetGridx();
  can2D->SetGridy();

  can2D->cd();
  
  hist2D->Draw("COLZ");
  hist2D->GetXaxis()->SetTitle("TDO");
  hist2D->GetXaxis()->CenterTitle();
  hist2D->GetYaxis()->SetTitle("BCID - 1001");
  hist2D->GetYaxis()->CenterTitle();
  hist2D->GetZaxis()->SetTitle("N events");
  hist2D->GetZaxis()->SetTitleOffset(1.4);
  hist2D->GetZaxis()->CenterTitle();
  hist2D->GetZaxis()->SetRangeUser(0.1,hist2D->GetMaximum()*1.1);


}
