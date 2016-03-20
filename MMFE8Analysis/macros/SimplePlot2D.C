#include <iostream>
#include <TCanvas.h>
#include <TChain.h>
#include <TH2D.h>
#include <TGraph.h>
#include <TStyle.h>
#include <TLatex.h>

#include "include/MMFE8Base.hh"

using namespace std;

void SimplePlot2D(){

  //string filename = "data/scan_CH1-64_unmasked.root";
  //string filename = "data/scan_CH1-50_masked.root";
  string filename = "test.root";
  string varXname = "VMM #";
  string varYname = "CH #";
  
  // delay count stuff
  int CH = 21;
  double delays[5];
  double count_tot[5];
  double count_right[5];
  for(int i = 0; i < 5; i++){
    delays[i] = double(i)*5.;
    count_tot[i] = 0.;
    count_right[i] = 0.;
  }
  
      

  ///////////////////////////////////////////////////////
  
  TChain* tree = new TChain("MMFE8","MMFE8");

  tree->AddFile(filename.c_str());

  MMFE8Base* base = new MMFE8Base(tree);

  int N = tree->GetEntries();

  TH2D* hist = new TH2D("hist","hist", 8, 0.5, 8.5, 64, 0.5,64.5);
  TH2D* histN = (TH2D*) hist->Clone("norm");
  TH2D* histchch = new TH2D("histchch","histchch", 64, 0.5, 64.5, 64, 0.5,64.5);
  TH2D* histDelay = new TH2D("histN","histN", 31, 9.5, 40.5, 5,-0.5, 4.5);	
  TH2D* histDelayD = new TH2D("histD","histD", 31, 9.5, 40.5, 5,-0.5, 4.5);

  for(int i = 0; i < N; i++){
    base->GetEntry(i);
    
    if(base->CHpulse == CH){
      //count_tot[base->Delay] += 1.;
      count_tot[(base->TPDAC-80)/20] += 1.;
      if(base->CHpulse == base->CHword)
	//count_right[base->Delay] += base->TDO;
      	count_right[(base->TPDAC-80)/20] += base->PDO;
    }

    //histDelayD->Fill(base->CHpulse,base->Delay);
    histDelayD->Fill(base->CHpulse,(base->TPDAC-80)/20);
    if(base->CHpulse == base->CHword)
      //histDelay->Fill(base->CHpulse,base->Delay,base->TDO);
      histDelay->Fill(base->CHpulse,(base->TPDAC-80)/20,base->PDO);

    if((base->CHpulse != base->CHword || true) &&
       base->VMM == 6)
      histchch->Fill(base->CHpulse,base->CHword);

    if(base->CHpulse != base->CHword)
      continue;

    hist->Fill(base->VMM,base->CHpulse,base->PDO);
    histN->Fill(base->VMM,base->CHpulse);
  
  }

  for(int x = 0; x < 8; x++){
    for(int y = 0; y < 64; y++){
      double v = hist->GetBinContent(x+1,y+1);
      double N = histN->GetBinContent(x+1,y+1);
      hist->SetBinContent(x+1,y+1,v/max(int(N),1));
    }
  }
  
  TLatex l;
  //l.NDC();

  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.05);
  can->SetLeftMargin(0.12);
  can->SetRightMargin(0.15);
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

  TCanvas* canN = new TCanvas("canN","canN",600,500);
  canN->SetTopMargin(0.05);
  canN->SetLeftMargin(0.12);
  canN->SetRightMargin(0.15);

  canN->Draw();
  canN->SetGridx();
  canN->SetGridy();
  
  canN->cd();

  histN->Draw("COLZ");
  
  histN->GetXaxis()->SetTitle(varXname.c_str());
  histN->GetXaxis()->CenterTitle();
  histN->GetYaxis()->SetTitle(varYname.c_str());
  histN->GetYaxis()->CenterTitle();
  histN->GetYaxis()->SetTitleOffset(1.4);
  histN->GetYaxis()->CenterTitle();
			     
  TCanvas* canchch = new TCanvas("canchch","canchch",600,500);
  canchch->SetTopMargin(0.05);
  canchch->SetLeftMargin(0.12);
  canchch->SetRightMargin(0.15);

  canchch->Draw();
  canchch->SetGridx();
  canchch->SetGridy();
  
  canchch->cd();
  histchch->Draw("COLZ");
  
  histchch->GetXaxis()->SetTitle("CH pulsed");
  histchch->GetXaxis()->CenterTitle();
  histchch->GetYaxis()->SetTitle("CH data");
  histchch->GetYaxis()->CenterTitle();
  histchch->GetYaxis()->SetTitleOffset(1.4);
  histchch->GetYaxis()->CenterTitle();
  histchch->GetZaxis()->SetTitle("Number of data events");
  histchch->GetZaxis()->SetTitleOffset(1.4);
  histchch->GetZaxis()->CenterTitle();
 
  l.DrawLatex(.54,65.2,"VMM 2");

  TCanvas* can_delay = new TCanvas("can_delay","can_delay",600,500);
  can_delay->Draw();
  can_delay->cd();

  for(int i = 0; i < 5; i++)
    count_tot[i] = count_right[i]/count_tot[i];
  TGraph* gr = new TGraph(5,delays,count_tot);
  gr->SetMarkerSize(4);
  gr->SetMarkerStyle(5);
  gr->Draw("AP");

  histDelay->Divide(histDelayD);

  TCanvas* canDelay = new TCanvas("canDelay","canDelay",600,500);
  canDelay->SetTopMargin(0.05);
  canDelay->SetLeftMargin(0.12);
  canDelay->SetRightMargin(0.15);

  canDelay->Draw();
  canDelay->SetGridx();
  canDelay->SetGridy();
  
  canDelay->cd();
  histDelay->Draw("COLZ");
  
  histDelay->GetXaxis()->SetTitle("CH pulsed");
  histDelay->GetXaxis()->CenterTitle();
  histDelay->GetYaxis()->SetTitle("Delay Count");
  histDelay->GetYaxis()->CenterTitle();
  histDelay->GetYaxis()->SetTitleOffset(1.4);
  histDelay->GetYaxis()->CenterTitle();
  histDelay->GetZaxis()->SetTitle("Fraction zeroes");
  histDelay->GetZaxis()->SetTitleOffset(1.4);
  histDelay->GetZaxis()->CenterTitle();
}
