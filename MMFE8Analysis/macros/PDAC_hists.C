#include <iostream>
#include <vector>
#include <string>
#include <TCanvas.h>
#include <TH1D.h>
#include <TF1.h>
#include <TStyle.h>
#include <TLegend.h>

#include "../include/xADCBase.hh"

using namespace std;

/*
 * Plots multiple histograms corresponding to multiple specified PDAC values
 * on the same plot.  All are fitted with Gaussians.
 */

void PDAC_hists(){

  string filename = "../../mmfe8_gui/CalibrationRoutine/mmfe8_CalibRoutine.dat.root";
  string varname = "xADC voltage (V)";
  bool output_enable = false;
  string outputfile = "./xADC_test1";

  bool Gaussian_fit = true;
  int vmm = 1;
  int pdacs[] = {40, 140};
  int colors[] = {kViolet+8, kBlue+4, kBlue, kAzure+10, kTeal-5, \
    kTeal+3, kGreen+1, kSpring-8};

  ///////////////////////////////////////////////////////

  TChain* tree = new TChain("xADC_data","xADC_data");

  tree->AddFile(filename.c_str());

  xADCBase* base = new xADCBase(tree);

  int N = tree->GetEntries();

  //int num_vmms = sizeof(vmms) / sizeof(int);
  int num_pdacs = sizeof(pdacs) / sizeof(int);

  vector<TH1D*> hists;
  TLegend* legend = new TLegend(0.65, 0.8, 0.98, 0.98, varname.c_str());

  for (int i = 0; i < num_pdacs; i++) {
    string name = "hist PDAC value " + to_string(pdacs[i]);
    hists.push_back(new TH1D(name.c_str(), "hist", 2048, -0.00013, 1.00013));
  }

  for (int i = 0; i < N; i++){
    base->GetEntry(i);
    //cout << "VMM # " << base->VMM << endl;

    for (int j = 0; j < num_pdacs; j++){
      if ((vmm == base->VMM) && (pdacs[j] == base->PDAC)) {
        hists[j]->Fill(float(base->XADC) / 4096.0);
        break; // Is supposed to only break out of inner loop.
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

  double mean[num_pdacs];
  double stdev[num_pdacs];
  double plot_max = 0;
  double current_value;
  TF1* current_fit;

  for (int i = 0; i < num_pdacs; i++){
     mean[i] = hists[i]->GetMean();
     stdev[i] = hists[i]->GetStdDev();
     if Gaussian_fit {
       hists[i]->Fit("gaus");
       current_fit = hists[i]->GetFunction("gaus");
       current_fit->SetLineStyle(5);
       current_fit->SetLineWidth(1);
       current_fit->SetLineColor(kGray+2);//colors[i]);
     }
     current_value = hists[i]->GetMaximum();
     if (current_value > plot_max){
       plot_max = current_value;
     }
  }

  hists[0]->Draw();
  hists[0]->GetXaxis()->SetTitle(varname.c_str());
  hists[0]->GetXaxis()->CenterTitle();
  hists[0]->GetYaxis()->SetTitle("N events");
  hists[0]->GetYaxis()->SetTitleOffset(1.4);
  hists[0]->GetYaxis()->CenterTitle();
  hists[0]->GetYaxis()->SetRangeUser(0.,plot_max*1.1);
  hists[0]->GetXaxis()->SetRangeUser(mean[0]-(6*stdev[0]), //mean[1]+(6*stdev[1]));
                                mean[num_pdacs - 1]+(6*stdev[num_pdacs - 1]));

  for (int i = 0; i < num_pdacs; i++){
    hists[i]->SetLineColorAlpha(colors[i], 0.8);
    hists[i]->SetLineWidth(1);
    if (i != 0){
      hists[i]->Draw("same");
    }
    legend->AddEntry(hists[i], ("PDAC value " + to_string(pdacs[i])).c_str());
  }
  legend->Draw();

  if output_enable {
    TFile* test = new TFile((outputfile + ".root").c_str(),"RECREATE");
    test->cd();
    can->Write();
    test->Close();
  }
}
