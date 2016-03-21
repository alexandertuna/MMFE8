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

#include "include/MMFE8Base.hh"

using namespace std;

TColor *icolor[9][2];
int color_list[4][10];
int style_list[4][10];
void setstyle(int istyle);

void Plot_1D_mult(string filename){
  
  //string filename = "data/scan_CH1-50_masked.root";
 
  string varXname = "TDO [ns]";
  string varYname = "#frac{1}{N}#frac{dN}{d(TDO)}";

  int VMM = 4;
  int CH = 30;
  
  int Nx = 150;
  double Xmin = 0.;
  double Xmax = 150;

  vector<int> Value;
  vector<string> Label;

  // Value.push_back(0);
  // Label.push_back("Test Pulse DAC = 80");
  // Value.push_back(1);
  // Label.push_back("Test Pulse DAC = 100");
  // Value.push_back(2);
  // Label.push_back("Test Pulse DAC = 120");
  // Value.push_back(3);
  // Label.push_back("Test Pulse DAC = 140");
  // Value.push_back(4);
  // Label.push_back("Test Pulse DAC = 160");

  Value.push_back(0);
  Label.push_back("Delay Count = 0");
  Value.push_back(1);
  Label.push_back("Delay Count = 1");
  Value.push_back(2);
  Label.push_back("Delay Count = 2");
  Value.push_back(3);
  Label.push_back("Delay Count = 3");
  Value.push_back(4);
  Label.push_back("Delay Count = 4");

  ///////////////////////////////////////////////////////
  setstyle(0);
  
  TChain* tree = new TChain("MMFE8","MMFE8");

  tree->AddFile(filename.c_str());

  MMFE8Base* base = new MMFE8Base(tree);

  int N = tree->GetEntries();

  int Nval = Value.size();

  vector<TH1D*> hist;
  
  for(int i = 0; i < Nval; i++){
    hist.push_back(new TH1D(("hist_"+string(to_string(i))).c_str(),
			    ("hist_"+string(to_string(i))).c_str(),
			    Nx, Xmin, Xmax));
  }

  for(int i = 0; i < N; i++){
    base->GetEntry(i);

    if(base->VMM != VMM)
      continue;
    
    if(base->CHpulse != CH)
      continue;
    
    //int ival = (base->TPDAC-80)/20;
    int ival = base->Delay;
    
    for(int v = 0; v < Nval; v++){
      if(ival == Value[v]){
	hist[v]->Fill(base->TDO);
      }
    }
  }

  double max = -1.;
  int imax = -1;
  for(int i = 0; i < Nval; i++){
    if(hist[i]->Integral() > 0.)
      hist[i]->Scale(1./hist[i]->Integral());
    if(hist[i]->GetMaximum() > max){
      max = hist[i]->GetMaximum();
      imax = i;
    }
  }
  
  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetLeftMargin(0.15);
  can->SetRightMargin(0.04);
  can->SetBottomMargin(0.15);
  can->SetTopMargin(0.085);
  
  can->Draw();
  can->SetGridx();
  can->SetGridy();
  
  can->cd();

  hist[imax]->Draw();
  hist[imax]->GetXaxis()->CenterTitle();
  hist[imax]->GetXaxis()->SetTitleFont(132);
  hist[imax]->GetXaxis()->SetTitleSize(0.06);
  hist[imax]->GetXaxis()->SetTitleOffset(1.06);
  hist[imax]->GetXaxis()->SetLabelFont(132);
  hist[imax]->GetXaxis()->SetLabelSize(0.05);
  hist[imax]->GetXaxis()->SetTitle(varXname.c_str());
  hist[imax]->GetYaxis()->CenterTitle();
  hist[imax]->GetYaxis()->SetTitleFont(132);
  hist[imax]->GetYaxis()->SetTitleSize(0.06);
  hist[imax]->GetYaxis()->SetTitleOffset(1.);
  hist[imax]->GetYaxis()->SetLabelFont(132);
  hist[imax]->GetYaxis()->SetLabelSize(0.05);
  hist[imax]->GetYaxis()->SetTitle(varYname.c_str());
  
  for(int i = 0; i < Nval; i++){
    hist[i]->SetLineColor(1393+2*i);
    hist[i]->SetLineWidth(3);
    hist[i]->SetMarkerColor(1393+2*i);
    hist[i]->SetMarkerSize(0);
    hist[i]->SetFillColor(kWhite);
    hist[i]->Draw("SAME");
  }

  TLegend* leg = new TLegend(0.688,0.22,0.93,0.42);
  leg->SetTextFont(132);
  leg->SetTextSize(0.045);
  leg->SetFillColor(kWhite);
  leg->SetLineColor(kWhite);
  leg->SetShadowColor(kWhite);
  for(int i = 0; i < Nval; i++)
    leg->AddEntry(hist[i],Label[i].c_str());
  leg->SetLineColor(kWhite);
  leg->SetFillColor(kWhite);
  leg->SetShadowColor(kWhite);
  leg->Draw("SAME");
  
  TLatex l;
  l.SetTextFont(132);
  l.SetNDC();
  l.SetTextSize(0.05);
  l.SetTextFont(132);
  l.DrawLatex(0.27,0.94,"MMFE8 Analysis");
  l.SetTextSize(0.04);
  l.SetTextFont(42);
  l.DrawLatex(0.02,0.943,"#bf{#it{ATLAS}} Internal");

  string label = "VMM # = "+to_string(VMM)+
    ", CH # = "+to_string(CH);
  l.SetTextSize(0.05);
  l.SetTextFont(132);
  l.DrawLatex(0.64,0.94, label.c_str());

 
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
