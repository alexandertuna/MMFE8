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

void square_wave_fit(){

  string filename = "../../mmfe8_gui/CalibrationRoutine/mmfe8_CalibRoutine.root";
  string varname = "xADC voltage (V)";
  bool output_enable = false;
  string outputfile = "./xADC_test1";

  bool Gaussian_fit = true;
  int vmm = 3;
  int pdac = 80;
  int colors[] = {kViolet+8, kBlue+4, kBlue, kAzure+10, kTeal-5, \
    kTeal+3, kGreen+1, kSpring-8};

  ///////////////////////////////////////////////////////

  const double min_V = -0.00013;
  const double max_V = 1.00013;

  TChain* tree = new TChain("xADC_data","xADC_data");

  tree->AddFile(filename.c_str());

  xADCBase* base = new xADCBase(tree);

  int N = tree->GetEntries();

  //int num_vmms = sizeof(vmms) / sizeof(int);
  //int num_pdacs = sizeof(pdacs) / sizeof(int);

  //vector<TH1D*> hists;
  TH1D* hist = new TH1D("full histogram","hist", 2048, min_V, max_V);
  // TLegend* legend = new TLegend(0.65, 0.8, 0.98, 0.98, varname.c_str());

  for (int i = 0; i < N; i++){
    base->GetEntry(i);

    if ((vmm == base->VMM) && (pdac == base->PDAC) && (base->CKTPrunning)) {
      hist->Fill(float(base->XADC) / 4096.0);
      // printf("%f",float(base->XADC / 4096.0));
    }
  }

  // TH1D* low_hist = hist->Clone("low peak");
  // TH1D* high_hist = low_hist->Clone("high peak");
  double hist_mean = hist->GetMean();
  //low_hist->GetXaxis()->SetRange(min_V, hist_mean);
  //high_hist->GetXaxis()->SetRange(hist_mean, max_V);


  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.05);
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);

  can->Draw();
  can->SetGridx();
  can->SetGridy();

  can->cd();

  double plot_max = hist->GetMaximum();

  hist->Draw();
  hist->GetXaxis()->SetTitle(varname.c_str());
  hist->GetXaxis()->CenterTitle();
  hist->GetYaxis()->SetTitle("N events");
  hist->GetYaxis()->SetTitleOffset(1.4);
  hist->GetYaxis()->CenterTitle();
  hist->GetYaxis()->SetRangeUser(0.,plot_max*1.1);
  hist->GetXaxis()->SetRangeUser(0.0, //mean[1]+(6*stdev[1]));
                                0.5);
  //hist->Draw();

  if Gaussian_fit {
    TF1* low_fit = new TF1("low fit", "gaus", min_V, hist_mean);
    low_fit->SetLineColor(kBlue);
    TF1* high_fit = new TF1("high fit", "gaus", hist_mean, max_V);
    high_fit->SetLineColor(kTeal+3);
    hist->Fit("low fit", "R");
    hist->Fit("high fit", "R");
    // TF1* low_fit = low_hist->GetFunction("gaus");
    // TF1* high_fit = high_hist->GetFunction("gaus");
    // low_fit->SetLineStyle(5);
    // current_fit->SetLineWidth(1);
    // current_fit->SetLineColor(kGray+2);//colors[i]);
  }
  if Gaussian_fit {
    low_fit->Draw("same");
    high_fit->Draw("same");
  }
  // for (int i = 0; i < num_pdacs; i++){
  //   hists[i]->SetLineColorAlpha(colors[i], 0.8);
  //   hists[i]->SetLineWidth(1);
  //   if (i != 0){
  //     hists[i]->Draw("same");
  //   }
  //   legend->AddEntry(hists[i], ("PDAC value " + to_string(pdacs[i])).c_str());
  // }
  // legend->Draw();

  if output_enable {
    TFile* test = new TFile((outputfile + ".root").c_str(),"RECREATE");
    test->cd();
    can->Write();
    test->Close();
  }
}
