#include <string>
#include <iostream>
#include <vector>
#include <TCanvas.h>
#include <TH1D.h>
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

void Plot1D(){

  string filename = "scan_CH1-58.root";
  string varname = "PDO";

  ///////////////////////////////////////////////////////

  TChain* tree = new TChain("MMFE8","MMFE8");

  tree->AddFile(filename.c_str());

  MMFE8Base* base = new MMFE8Base(tree);

  int N = tree->GetEntries();


  TH1D* hist = new TH1D("hist","hist", 1000, 0.0, 1000.);

  for (int i = 0; i < N; i++){
    base->GetEntry(i);
    //cout << "VMM # " << base->VMM << endl;

    // for (int j = 0; j < num_channels; j++){
    //   if (channels[j] == base->CHword) {
    //     hists[j]->Fill(base->PDO);
    //   }
    // }

    if(base->VMM != 6|| base->CHpulse != 16)
      continue;

    if(base->CHword == base->CHpulse)
     continue;

    hist->Fill(base->PDO);
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
  hist->GetYaxis()->SetRangeUser(0.,hist->GetMaximum()*1.1);


}
