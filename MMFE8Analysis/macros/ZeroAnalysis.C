#include <iostream>
#include <string>

#include <TFile.h>
#include <TTree.h>
#include <TBranch.h>
#include <TGraph.h>
#include <TMultiGraph.h>
#include <TAxis.h>
#include <TCanvas.h>
#include <TMath.h>
#include <TLegend.h>
#include <TLatex.h>
#include <TColor.h>
#include <TColorWheel.h>
#include <TH1D.h>
#include <TH2D.h>
#include <TStyle.h>

#include "include/VMM_data.hh"

using namespace std;

TColor *icolor[9][2];
int color_list[4][10];
int style_list[4][10];
void setstyle(int istyle);

TCanvas* Plot_Me(string scan, TH2D* histo, string X, string Y, string title = "", string label = "");
TCanvas* Plot_Me(string scan, vector<TH1D*>& histo, string X, vector<string>& label, string title = "");


void ZeroAnalysis(string filename){

  ///////////////////////////////////////////////////////
  setstyle(0);
  
  TChain* tree = new TChain("VMM_data","VMM_data");

  tree->AddFile(filename.c_str());

  VMM_data* base = new VMM_data(tree);

  int Ne = tree->GetEntries();

  TH2D* hist_N0 = new TH2D("h_N0","h_N0",
			   8,  -0.5, 7.5,
			   64, 0.5, 64.5);

  vector<TH2D*> hist_occ;
  hist_occ.push_back((TH2D*) new TH2D("h_occ0","h_occ0",
				      8,  -0.5, 7.5,
				      64, 0.5, 64.5));
  hist_occ.push_back((TH2D*) new TH2D("h_occ1","h_occ1",
				      8,  -0.5, 7.5,
				      64, 0.5, 64.5));

  vector<TH1D*> hist_FIFO;
  hist_FIFO.push_back((TH1D*) new TH1D("h_FIFO0","h_FIFO0",
				       511, -0.5, 510.5));
  hist_FIFO.push_back((TH1D*) new TH1D("h_FIFO1","h_FIFO1",
				       511, -0.5, 510.5));
  vector<TH1D*> hist_BCIDtrig;
  hist_BCIDtrig.push_back((TH1D*) new TH1D("h_BCIDtrig","h_BCIDtrig",
					   4200, -0.5, 4199.5));
  hist_BCIDtrig.push_back((TH1D*) new TH1D("h_BCIDtrig","h_BCIDtrig",
					   4200, -0.5, 4199.5));

  vector<TH1D*> hist_PDO;
  hist_PDO.push_back((TH1D*) new TH1D("h_PDO0","h_PDO0",
				      1000, -0.5, 510.5));
  hist_PDO.push_back((TH1D*) new TH1D("h_PDO1","h_PDO1",
				      1000, -0.5, 510.5));

  vector<TH1D*> hist_TDO;
  hist_TDO.push_back((TH1D*) new TH1D("h_TDO0","h_TDO0",
				      511, -0.5, 510.5));
  hist_TDO.push_back((TH1D*) new TH1D("h_TDO1","h_TDO1",
				      511, -0.5, 510.5));

  vector<TH1D*> hist_BCID;
  hist_BCID.push_back((TH1D*) new TH1D("h_BCID0","h_BCID0",
				       4200, -0.5, 4199.5));
  hist_BCID.push_back((TH1D*) new TH1D("h_BCID1","h_BCID1",
				       4200, -0.5, 4199.5));

  vector<TH1D*> hist_VMM;
  hist_VMM.push_back((TH1D*) new TH1D("h_VMM0","h_VMM0",
				      8, -0.5, 7.5));
  hist_VMM.push_back((TH1D*) new TH1D("h_VMM1","h_VMM1",
				      8, -0.5, 7.5));

  vector<TH1D*> hist_CH;
  hist_CH.push_back((TH1D*) new TH1D("h_CH0","h_CH0",
				     64, 0.5, 64.5));
  hist_CH.push_back((TH1D*) new TH1D("h_CH1","h_CH1",
				     64, 0.5, 64.5));

  // vector<TH2D*> hist_TDOvBCID;
  // hist_TDOvBCID.push_back((TH2D*) new TH2D("h_occ0","h_occ0",
  // 					   8,  -0.5, 7.5,
  // 					   64, 0.5, 64.5));
  // hist_TDOvBCID.push_back((TH2D*) new TH2D("h_occ1","h_occ1",
  // 					   8,  -0.5, 7.5,
  // 					   64, 0.5, 64.5));
  
  int N0   = 0;
  int NTOT = 0;

  int Ntrig_cur = -1;
  bool has_zero = false;
  int index = 0;
  int FIFO_cur     = -1;
  int BCIDtrig_cur = -1;
  vector<int> PDO;
  vector<int> TDO;
  vector<int> CH;
  vector<int> VMM;
  vector<int> BCID;
  for(int e = 0; e < Ne; e++){
    base->GetEntry(e);

    if(base->Ntrig != Ntrig_cur){
      // new event, tally last one
      int Nhit = PDO.size();
      if(Nhit > 0){
	NTOT++;
	index = 0;
	if(has_zero){
	  N0++;
	  index = 1;
	}
	hist_FIFO[index]->Fill(FIFO_cur);
	hist_BCIDtrig[index]->Fill(BCIDtrig_cur);
	for(int h = 0; h < Nhit; h++){
	  hist_occ[index]->Fill(VMM[h],CH[h]);
	  hist_PDO[index]->Fill(PDO[h]);
	  hist_TDO[index]->Fill(TDO[h]);
	  hist_BCID[index]->Fill(BCID[h]);
	  hist_VMM[index]->Fill(VMM[h]);
	  hist_CH[index]->Fill(CH[h]);
	}
      }
      // prepare new event
      // if(base->FIFO > 20)
      // 	continue;
      Ntrig_cur = base->Ntrig;
      has_zero = false;
      FIFO_cur = base->FIFO;
      BCIDtrig_cur = base->BCIDtrig;
      PDO.clear();
      TDO.clear();
      CH.clear();
      VMM.clear();
      BCID.clear();
    }

    if(base->PDO <= 0){
      hist_N0->Fill(base->VMM,base->CHword);
      has_zero = true;
    }
   
    PDO.push_back(base->PDO);
    TDO.push_back(base->TDO);
    CH.push_back(base->CHword);
    VMM.push_back(base->VMM);
    BCID.push_back(base->BCID);
  }

  cout << NTOT << " events without PDO = 0" << endl;
  cout << N0 << " events with PDO = 0" << endl;
  cout << "Total zero event fraction is " << 100.*double(N0)/double(NTOT) << " %" << endl;
  
  vector<string> label;
  label.push_back("No Zeroes");
  label.push_back("#geq 1 Zero");
  TCanvas* c0 = Plot_Me("c0", hist_occ[0], "VMM #", "Channel #", "Occupancy in non-zero events");
  TCanvas* c1 = Plot_Me("c1", hist_occ[1], "VMM #", "Channel #", "Occupancy in zero events");
  TCanvas* c2 = Plot_Me("c2", hist_CH, "Channel #", label);
  TCanvas* c3 = Plot_Me("c3", hist_PDO, "PDO", label);
  TCanvas* c4 = Plot_Me("c4", hist_TDO, "TDO", label);
  TCanvas* c5 = Plot_Me("c5", hist_BCID, "BCID", label);
  TCanvas* c6 = Plot_Me("c6", hist_BCIDtrig, "BCID of external trigger", label);
  TCanvas* c7 = Plot_Me("c7", hist_FIFO, "FIFO count", label);
  TCanvas* c8 = Plot_Me("c8", hist_N0, "VMM #", "Channel #", "Occupancy of PDO = 0");



  // TCanvas* can = new TCanvas("can","can",600,500);
  // can->SetLeftMargin(0.15);
  // can->SetRightMargin(0.22);
  // can->SetBottomMargin(0.15);
  // can->SetTopMargin(0.08);

  // can->Draw();
  // can->SetGridx();
  // can->SetGridy();
  
  // can->cd();

  // hist = histN;

  // hist->Draw("COLZ");

  // hist->GetXaxis()->CenterTitle();
  // hist->GetXaxis()->SetTitleFont(132);
  // hist->GetXaxis()->SetTitleSize(0.06);
  // hist->GetXaxis()->SetTitleOffset(1.06);
  // hist->GetXaxis()->SetLabelFont(132);
  // hist->GetXaxis()->SetLabelSize(0.05);
  // hist->GetXaxis()->SetTitle(varXname.c_str());
  // hist->GetYaxis()->CenterTitle();
  // hist->GetYaxis()->SetTitleFont(132);
  // hist->GetYaxis()->SetTitleSize(0.06);
  // hist->GetYaxis()->SetTitleOffset(1.12);
  // hist->GetYaxis()->SetLabelFont(132);
  // hist->GetYaxis()->SetLabelSize(0.05);
  // hist->GetYaxis()->SetTitle(varYname.c_str());
  // hist->GetZaxis()->CenterTitle();
  // hist->GetZaxis()->SetTitleFont(132);
  // hist->GetZaxis()->SetTitleSize(0.06);
  // hist->GetZaxis()->SetTitleOffset(1.3);
  // hist->GetZaxis()->SetLabelFont(132);
  // hist->GetZaxis()->SetLabelSize(0.05);
  // hist->GetZaxis()->SetTitle(varZname.c_str());
  // hist->GetZaxis()->SetRangeUser(0.9*hist->GetMinimum(),1.1*hist->GetMaximum());

  // TLatex l;
  // l.SetTextFont(132);
  // l.SetNDC();
  // l.SetTextSize(0.05);
  // l.SetTextFont(132);
  // l.DrawLatex(0.5,0.943,"MMFE8 Analysis");
  // l.SetTextSize(0.04);
  // l.SetTextFont(42);
  // l.DrawLatex(0.15,0.943,"#bf{#it{ATLAS}} Internal");

  // l.SetTextSize(0.06);
  // l.SetTextFont(132);
  // l.DrawLatex(0.80,0.04, "VMM #6");

 
}

void setstyle(int istyle) {
	
  // For the canvas:
  gStyle->SetCanvasBorderMode(0);
  gStyle->SetCanvasColor(kWhite);
  gStyle->SetCanvasDefH(300); //Height of canvas
  gStyle->SetCanvasDefW(600); //Width of canvas
  gStyle->SetCanvasDefX(0);   //POsition on screen
  gStyle->SetCanvasDefY(0);
	
  // For the Pad:
  gStyle->SetPadBorderMode(0);
  // gStyle->SetPadBorderSize(Width_t size = 1);
  gStyle->SetPadColor(kWhite);
  gStyle->SetPadGridX(false);
  gStyle->SetPadGridY(false);
  gStyle->SetGridColor(0);
  gStyle->SetGridStyle(3);
  gStyle->SetGridWidth(1);
	
  // For the frame:
  gStyle->SetFrameBorderMode(0);
  gStyle->SetFrameBorderSize(1);
  gStyle->SetFrameFillColor(0);
  gStyle->SetFrameFillStyle(0);
  gStyle->SetFrameLineColor(1);
  gStyle->SetFrameLineStyle(1);
  gStyle->SetFrameLineWidth(1);
	
  // set the paper & margin sizes
  gStyle->SetPaperSize(20,26);
  gStyle->SetPadTopMargin(0.065);
  gStyle->SetPadRightMargin(0.065);
  gStyle->SetPadBottomMargin(0.15);
  gStyle->SetPadLeftMargin(0.17);
	
  // use large Times-Roman fonts
  gStyle->SetTitleFont(132,"xyz");  // set the all 3 axes title font
  gStyle->SetTitleFont(132," ");    // set the pad title font
  gStyle->SetTitleSize(0.06,"xyz"); // set the 3 axes title size
  gStyle->SetTitleSize(0.06," ");   // set the pad title size
  gStyle->SetLabelFont(132,"xyz");
  gStyle->SetLabelSize(0.05,"xyz");
  gStyle->SetLabelColor(1,"xyz");
  gStyle->SetTextFont(132);
  gStyle->SetTextSize(0.08);
  gStyle->SetStatFont(132);
	
  // use bold lines and markers
  gStyle->SetMarkerStyle(8);
  gStyle->SetHistLineWidth(1.85);
  gStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes
	
  //..Get rid of X error bars
  gStyle->SetErrorX(0.001);
	
  // do not display any of the standard histogram decorations
  gStyle->SetOptTitle(0);
  gStyle->SetOptStat(0);
  gStyle->SetOptFit(11111111);
	
  // put tick marks on top and RHS of plots
  gStyle->SetPadTickX(1);
  gStyle->SetPadTickY(1);
	
  // set a decent palette
  gStyle->SetPalette(1);

  const Int_t NRGBs = 5;
  const Int_t NCont = 28;
  
  Double_t stops[NRGBs] = { 0.00, 0.5, 0.70, 0.82, 1.00 };
  Double_t red[NRGBs]   = { 0.00, 0.00, 0.74, 1.00, 1. };
  Double_t green[NRGBs] = { 0.00, 0.61, 0.82, 0.70, 1.00 };
  Double_t blue[NRGBs]  = { 0.31, 0.73, 0.08, 0.00, 1.00 };
  
  TColor::CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
  gStyle->SetNumberContours(NCont);
  
  gStyle->cd();
	
  TColorWheel *w = new TColorWheel();
	
  icolor[0][1] = new TColor(1390, 0.90, 0.60, 0.60, ""); //red
  icolor[0][0] = new TColor(1391, 0.70, 0.25, 0.25, "");
  icolor[1][1] = new TColor(1392, 0.87, 0.87, 0.91, ""); //blue
  icolor[1][0] = new TColor(1393, 0.59, 0.58, 0.91, "");
  icolor[2][1] = new TColor(1394, 0.65, 0.55, 0.85, ""); //violet (gamma)
  icolor[2][0] = new TColor(1395, 0.49, 0.26, 0.64, "");
  icolor[3][1] = new TColor(1396, 0.95, 0.95, 0.60, ""); // yellow (alpha)
  icolor[3][0] = new TColor(1397, 0.95, 0.95, 0.00, "");
  icolor[4][1] = new TColor(1398, 0.75, 0.92, 0.68, ""); //green (2beta+gamma)
  icolor[4][0] = new TColor(1399, 0.36, 0.57, 0.30, "");
  icolor[5][1] = new TColor(1400, 0.97, 0.50, 0.09, ""); // orange
  icolor[5][0] = new TColor(1401, 0.76, 0.34, 0.09, "");
  icolor[6][1] = new TColor(1402, 0.97, 0.52, 0.75, ""); // pink
  icolor[6][0] = new TColor(1403, 0.76, 0.32, 0.51, "");
  icolor[7][1] = new TColor(1404, 0.49, 0.60, 0.82, ""); // dark blue (kpnn)
  icolor[7][0] = new TColor(1405, 0.43, 0.48, 0.52, "");
  icolor[8][1] = new TColor(1406, 0.70, 0.70, 0.70, "");  // black
  icolor[8][0] = new TColor(1407, 0.40, 0.40, 0.40, "");
	
	
  if(istyle == 0){
		
    //SM MC
    color_list[3][0] = kCyan+3;
		
    //DATA
    color_list[0][0] = 1;
    color_list[0][1] = 2;
    color_list[0][2] = 4;
    style_list[0][0] = 20;
    style_list[0][1] = 23;
		
    //BKG MC
    color_list[1][0] = 0;
    color_list[1][3] = kGreen-9; //Light green
    color_list[1][5] = kOrange-2; //dark blue
    color_list[1][4] = kGreen+3; //yellow
    color_list[1][1] = kBlue-10; //light blue
    color_list[1][2] = kBlue+4; //dark green
    style_list[1][0] = 1001;
    style_list[1][1] = 1001;
    style_list[1][2] = 3002;
    style_list[1][3] = 1001;
    style_list[1][4] = 1001;
    style_list[1][5] = 1001;
		
    //SIG MC
    color_list[2][0] = 1;
    color_list[2][1] = 1;
    color_list[2][2] = 1;
    style_list[2][0] = 2;
    style_list[2][1] = 5;
  }
  if(istyle == 1){
		
    //SM MC
    color_list[3][0] = kSpring+4;
		
    //DATA
    color_list[0][0] = 1;
    color_list[0][1] = 2;
    color_list[0][2] = 4;
    style_list[0][0] = 20;
    style_list[0][1] = 23;
		
    //BKG MC
    color_list[1][0] = 0;
    color_list[1][1] = kGreen-9; //Light green
    color_list[1][2] = kGreen+3; //dark blue
    color_list[1][3] = kYellow-7; //yellow
    color_list[1][4] = kBlue-10; //light blue
    color_list[1][5] = kBlue+4; //dark blue
    style_list[1][0] = 1001;
    style_list[1][1] = 1001;
    style_list[1][2] = 3002;
    style_list[1][3] = 1001;
    style_list[1][4] = 1001;
    style_list[1][5] = 1001;
		
    //SIG MC
    color_list[2][0] = 1;
    color_list[2][1] = 1;
    color_list[2][2] = 1;
    style_list[2][0] = 2;
    style_list[2][1] = 5;
  }
  if(istyle == 2){
		
    //SM MC
    color_list[3][0] = kMagenta+2;
		
    //DATA
    color_list[0][0] = 1;
    color_list[0][1] = 2;
    color_list[0][2] = 4;
    style_list[0][0] = 20;
    style_list[0][1] = 23;
		
    //BKG MC
    color_list[1][0] = 0;
    color_list[1][3] = kRed-9; //Light green
    color_list[1][5] = kRed+3; //dark blue
    color_list[1][4] = kYellow-7; //yellow
    color_list[1][1] = kMagenta-10; //light blue
    color_list[1][2] = kMagenta+4; //dark green
    style_list[1][0] = 1001;
    style_list[1][1] = 1001;
    style_list[1][2] = 3002;
    style_list[1][3] = 1001;
    style_list[1][4] = 1001;
    style_list[1][5] = 1001;
		
    //SIG MC
    color_list[2][0] = 1;
    color_list[2][1] = 1;
    color_list[2][2] = 1;
    style_list[2][0] = 2;
    style_list[2][1] = 5;
  }
	
}

TCanvas* Plot_Me(string scan, TH2D* histo, string X, string Y, string title, string label){
  TCanvas *c1 = new TCanvas(scan.c_str(),scan.c_str(),600,500);
  c1->SetLeftMargin(0.15);
  c1->SetRightMargin(0.22);
  c1->SetBottomMargin(0.15);
  c1->SetTopMargin(0.08);
  c1->Draw();
  c1->SetGridx();
  c1->SetGridy();
  c1->SetLogz();
  
  histo->Draw("COLZ");
  histo->GetXaxis()->SetTitle(X.c_str());
  histo->GetXaxis()->SetTitleOffset(1.08);
  histo->GetXaxis()->CenterTitle();
  histo->GetYaxis()->SetTitle(Y.c_str());
  histo->GetYaxis()->SetTitleOffset(1.11);
  histo->GetYaxis()->CenterTitle();
  histo->GetZaxis()->SetTitle("N_{event}");
  histo->GetZaxis()->SetTitleOffset(1.5);
  histo->GetZaxis()->CenterTitle();
  histo->GetZaxis()->SetRangeUser(0.9*histo->GetMinimum(),1.1*histo->GetMaximum());
  histo->Draw("COLZ");
  
  TLatex l;
  l.SetTextFont(132);	
  l.SetNDC();	
  l.SetTextSize(0.045);
  l.SetTextFont(132);
  l.DrawLatex(0.4,0.955,title.c_str());
  l.SetTextSize(0.04);
  l.SetTextFont(42);
  l.DrawLatex(0.15,0.955,"#bf{#it{ATLAS}} Internal");
  l.SetTextSize(0.045);
  l.SetTextFont(132);
  l.DrawLatex(0.75,0.06,label.c_str());
	
  return c1;
}
TCanvas* Plot_Me(string scan, vector<TH1D*>& histo, string X, vector<string>& label, string title){
  TCanvas *c1 = new TCanvas(scan.c_str(),scan.c_str(),700,500);
  c1->SetRightMargin(0.05);
  c1->Draw();
  c1->SetGridx();
  c1->SetGridy();

  int Nh = histo.size();
  int imax = 0;
  int imin = 0;
  double max = 0;
  double min = -1;
  for(int i = 0; i < Nh; i++){
    if(histo[i]->GetMaximum() > max){
      imax = i;
      max = histo[i]->GetMaximum();
    }
    if(histo[i]->GetMinimum(0.) < min || min < 0){
      imin = i;
      min = histo[i]->GetMinimum(0.);
    }
  }

  histo[imax]->Draw();
  histo[imax]->GetXaxis()->SetTitle(X.c_str());
  histo[imax]->GetXaxis()->SetTitleOffset(1.08);
  histo[imax]->GetXaxis()->CenterTitle();
  histo[imax]->GetYaxis()->SetTitle("N_{event}");
  histo[imax]->GetYaxis()->SetTitleOffset(1.13);
  histo[imax]->GetYaxis()->CenterTitle();
  histo[imax]->GetYaxis()->SetRangeUser(0.9*min,1.1*max);

  for(int i = 0; i < Nh; i++){
    histo[i]->SetLineColor(1393+2*i);
    histo[i]->SetLineWidth(3);
    histo[i]->SetMarkerColor(1393+2*i);
    histo[i]->SetMarkerSize(0);
    histo[i]->SetFillColor(kWhite);
    histo[i]->Draw("SAME");
  }

  TLegend* leg = new TLegend(0.688,0.22,0.93,0.42);
  leg->SetTextFont(132);
  leg->SetTextSize(0.045);
  leg->SetFillColor(kWhite);
  leg->SetLineColor(kWhite);
  leg->SetShadowColor(kWhite);
  for(int i = 0; i < Nh; i++)
    leg->AddEntry(histo[i],label[i].c_str());
  leg->SetLineColor(kWhite);
  leg->SetFillColor(kWhite);
  leg->SetShadowColor(kWhite);
  leg->Draw("SAME");

  TLatex l;
  l.SetTextFont(132);	
  l.SetNDC();	
  l.SetTextSize(0.045);
  l.SetTextFont(132);
  l.DrawLatex(0.5,0.955,title.c_str());
  l.SetTextSize(0.04);
  l.SetTextFont(42);
  l.DrawLatex(0.17,0.955,"#bf{#it{ATLAS}} Internal");

  return c1;
}
