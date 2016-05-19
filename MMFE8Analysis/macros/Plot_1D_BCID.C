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

/*
 * Spec for Ben's project:
 * Overlay PDO data from channels 14-17 on one histogram, different colors.
 * Legend should show the different styles and the channel number
 * A text box should give the information not contained in the graph (which VMM)
 * Label axes.
 */

void Plot_1D_BCID(){

  //string filename = "data/BCID_02May16/BCID_test_1.root";
  string filename = "BCID_fullrun.dat.root";
  
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

  double BCID[100];
  double N_BCID[100];

  vector<int> iBCID[100];
  vector<int> iCHw[100];
  vector<int> iPDO[100];

  for(int i = 0; i < 100; i++){
    BCID[i] = 0.;
    N_BCID[i] = 0.;
  }

  for (int i = 0; i < N; i++){
    base->GetEntry(i);

    // if(base->Delay != idelay)
    //   continue;

    if(base->VMM != iVMM)
      continue;

    if(base->CHpulse != iCH)
      continue;

    //if(base->CHword > iCH && base->CHword-10 <= iCH){
      if(base->CHword != iCH || true){
      if(base->BCID >= 0){
	//BCID[base->PulseNum] += base->BCID;
	if(BCID[base->PulseNum] >= 0){
	  if(base->BCID < BCID[base->PulseNum])
	    BCID[base->PulseNum] = base->BCID;
	} else{
	  BCID[base->PulseNum] = base->BCID;
	}
	N_BCID[base->PulseNum] += 1.;
	iBCID[base->PulseNum].push_back(base->BCID);
	iCHw[base->PulseNum].push_back(base->CHword);
	iPDO[base->PulseNum].push_back(base->PDO);
	hist_BCID[base->PulseNum]->Fill(base->BCID);
      }
    }
  }

  for(int i = 0; i < 50; i++){
    cout << N_BCID[i] << " entries for pulse " << i << endl;
    //BCID[i] = int(BCID[i]/N_BCID[i] + 0.5);
    BCID[i] = hist_BCID[i]->GetMaximumBin()-1;
    for(int j = 0; j < iBCID[i].size(); j++)
      cout << iBCID[i][j] << "(" << iCHw[i][j] << ")" << "(" << iPDO[i][j] << ") ";
    cout << endl << BCID[i] << endl;
    cout << endl;
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
    
    if(N_BCID[base->PulseNum] > 0){
      hist->Fill(base->BCID-BCID[base->PulseNum]);
      hist2D->Fill(base->TDO, base->BCID-BCID[base->PulseNum]);
    }
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
  hist->GetXaxis()->SetTitle("BCID - mode(BCID)");
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
  hist2D->GetYaxis()->SetTitle("BCID - mode(BCID)");
  hist2D->GetYaxis()->CenterTitle();
  hist2D->GetZaxis()->SetTitle("N events");
  hist2D->GetZaxis()->SetTitleOffset(1.4);
  hist2D->GetZaxis()->CenterTitle();
  hist2D->GetZaxis()->SetRangeUser(0.1,hist2D->GetMaximum()*1.1);


}
