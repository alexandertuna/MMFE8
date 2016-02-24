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

void SimplePlot1D(){

  string filename = "fakeData.dat.root";
  string varname = "PDO";

  int channels[] = {14,15,16,17};
  int colors[] = {kViolet+8, kBlue+4, kBlue, kAzure+10, kTeal-5};

  ///////////////////////////////////////////////////////

  TChain* tree = new TChain("MMFE8","MMFE8");

  tree->AddFile(filename.c_str());

  MMFE8Base* base = new MMFE8Base(tree);

  int N = tree->GetEntries();

  int num_channels = sizeof(channels) / sizeof(int);

  vector<TH1D*> hists;
  TLegend* legend = new TLegend(0.65, 0.8, 0.98, 0.98, varname.c_str());

  for (int i = 0; i < num_channels; i++) {
    string name = "hist chan " + to_string(channels[i]);
    hists.push_back(new TH1D(name.c_str(), "hist", 1024, -0.5, 1023.5));
  }

  TH1D* hist = new TH1D("hist","hist", 100, 0.0, 1000.);

  for (int i = 0; i < N; i++){
    base->GetEntry(i);
    //cout << "VMM # " << base->VMM << endl;

    for (int j = 0; j < num_channels; j++){
      if (channels[j] == base->CHword) {
        hists[j]->Fill(base->PDO);
      }
    }

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
  
  hists[0]->GetXaxis()->SetTitle(varname.c_str());
  hists[0]->GetXaxis()->CenterTitle();
  hists[0]->GetYaxis()->SetTitle("N events");
  hists[0]->GetYaxis()->SetTitleOffset(1.4);
  hists[0]->GetYaxis()->CenterTitle();
  hists[0]->GetYaxis()->SetRangeUser(0.,hists[0]->GetMaximum()*1.1);

  for (int i = 0; i < num_channels; i++){
    hists[i]->SetLineColorAlpha(colors[i], 0.8);
    if (i != 0){
      hists[i]->Draw("same");
    }
    else {
      hists[i]->Draw();
    }
    legend->AddEntry(hists[i], ("Channel " + to_string(channels[i])).c_str());
  }
  legend->Draw();

  TFile* test = new TFile("test.root","RECREATE");
  test->cd();
  can->Write();
  test->Close();
}
