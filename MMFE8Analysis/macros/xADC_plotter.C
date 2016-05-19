#include <iostream>
#include <vector>
#include <TCanvas.h>
#include <TH1D.h>
#include <TF1.h>
#include <TStyle.h>
#include <TLegend.h>

#include "../include/xADCBase.hh"

using namespace std;

/*
 * Spec for Ben's project:
 * Overlay PDO data from vmms 14-17 on one histogram, different colors.
 * Legend should show the different styles and the channel number
 * A text box should give the information not contained in the graph (which VMM)
 * Label axes.
 */

void xADC_plotter(){

  string filename = "../../mmfe8_gui/CalibrationRoutine/mmfe8_CalibRoutine.dat.root";
  string varname = "xADC voltage (V)";
  string outputfile = "./xADC_test1";

  int vmms[] = {1};
  int pdac = 40;
  int colors[] = {kViolet+8, kBlue+4, kBlue, kAzure+10, kTeal-5};

  ///////////////////////////////////////////////////////

  TChain* tree = new TChain("xADC_data","MMFE8");

  tree->AddFile(filename.c_str());

  xADCBase* base = new xADCBase(tree);

  int N = tree->GetEntries();

  int num_vmms = sizeof(vmms) / sizeof(int);

  vector<TH1D*> hists;
  TLegend* legend = new TLegend(0.65, 0.8, 0.98, 0.98, varname.c_str());

  for (int i = 0; i < num_vmms; i++) {
    string name = "hist chan " + to_string(vmms[i]);
    hists.push_back(new TH1D(name.c_str(), "hist", 4096, -0.01, 1.025));
  }

  for (int i = 0; i < N; i++){
    base->GetEntry(i);
    //cout << "VMM # " << base->VMM << endl;

    for (int j = 0; j < num_vmms; j++){
      if ((vmms[j] == base->VMM) && (pdac == base->PDAC)) {
        hists[j]->Fill(float(base->XADC)/(4096.0));
      }
    }
  }

  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.05);
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);

  //TF1* function = new TF1("normal", )

  can->Draw();
  can->SetGridx();
  can->SetGridy();

  can->cd();

  double mean = hists[0]->GetMean();
  double stdev = hists[0]->GetStdDev();

  hists[0]->GetXaxis()->SetTitle(varname.c_str());
  hists[0]->GetXaxis()->CenterTitle();
  hists[0]->GetYaxis()->SetTitle("N events");
  hists[0]->GetYaxis()->SetTitleOffset(1.4);
  hists[0]->GetYaxis()->CenterTitle();
  hists[0]->GetYaxis()->SetRangeUser(0.,hists[0]->GetMaximum()*1.1);
  hists[0]->GetXaxis()->SetRangeUser(mean-(6*stdev),mean+(6*stdev));

  for (int i = 0; i < num_vmms; i++){
    hists[i]->SetLineColorAlpha(colors[i], 0.8);
    if (i != 0){
      hists[i]->Fit("gaus");
      hists[i]->Draw("same");
    }
    else {
      hists[i]->Fit("gaus");
      hists[i]->Draw();
    }
    legend->AddEntry(hists[i], ("Channel " + to_string(vmms[i])).c_str());
  }
  legend->Draw();

  TFile* test = new TFile((outputfile + ".root").c_str(),"RECREATE");
  test->cd();
  can->Write();
  test->Close();
}
