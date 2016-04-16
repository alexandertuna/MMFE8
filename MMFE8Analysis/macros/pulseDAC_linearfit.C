#include <iostream>
#include <vector>
#include <string>
#include <TCanvas.h>
#include <TH1D.h>
#include <TF1.h>
#include <TGraphErrors.h>
#include <TStyle.h>
#include <TLegend.h>

#include "../include/xADCBase.hh"

using namespace std;

/*
 * Graphing pulse DAC calibration data by moving PDAC points from histograms
 * to TGraphErrors, then fitting.
 */

void pulseDAC_linearfit(){

  string filename = "../../mmfe8_gui/CalibrationRoutine/mmfe8_CalibRoutine.dat.root";
  string yvar = "xADC voltage (V)";
  string xvar = "pulse DAC value (counts)";

  int vmm = 1;
  int degrees_of_freedom=3;
  int max_PDAC = 300;
  int linear_region_start = 80;
  int min_PDAC = 0;
  int min_N_per_bin = 10;
  int fit_color = kAzure;
  int marker_color = kGreen + 1;

  string outputfile = "./xADC_test1";
  /*string title = "VMM #" + to_string(vmm) + " pulse DAC linearity";*/


  ///////////////////////////////////////////////////////

  TChain* tree = new TChain("VMM_data","VMM_data");

  tree->AddFile(filename.c_str());

  xADCBase* base = new xADCBase(tree);

  int N = tree->GetEntries();

  int num_pdacs = max_PDAC - min_PDAC + 1;

  TH1D* hists[num_pdacs];

  int current_PDAC;
  for (int i = 0; i < num_pdacs; i++) {
    current_PDAC = i + min_PDAC;
    hists[i] = new TH1D(("PDAC value " + to_string(current_PDAC)).c_str(),
                        title.c_str(), 4096, -0.00013, 1.00013);
  }

  int max_XADC = 0;

  for (int i = 0; i < N; i++){
    base->GetEntry(i);
    //cout << "VMM # " << base->VMM << endl;
    current_PDAC = base->PDAC;

    if ((vmm == base->VMM) && !(base->CKTPrunning) && (current_PDAC >= min_PDAC) && (current_PDAC <= max_PDAC)) {
      hists[current_PDAC - min_PDAC]->Fill(float(base->XADC) / 4096.0);
      if (base->XADC > max_XADC){
        max_XADC = base->XADC;
      }
    }
  }

  double PDAC_values[num_pdacs];
  double XADC_means[num_pdacs];
  double XADC_stdevs[num_pdacs];
  int num_points = 0;

  for (int i = 0; i < num_pdacs; i++){
    if (hists[i]->GetEntries() >= min_N_per_bin){
      PDAC_values[num_points] = i + min_PDAC;
      XADC_means[num_points] = hists[i]->GetMean();
      XADC_stdevs[num_points] = hists[i]->GetStdDev();
      num_points++;
    }
  }

  TGraphErrors* graph = new TGraphErrors(num_points, PDAC_values, XADC_means, 0, XADC_stdevs);

  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.1);
  graph->SetTitle(title.c_str());
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);

  if (degrees_of_freedom == 3) {
    TF1* fit = new TF1("fit", "pol2", linear_region_start, PDAC_values[num_points - 1]);
  } else if (degrees_of_freedom == 2) {
    TF1* fit = new TF1("fit", "pol1", linear_region_start, PDAC_values[num_points - 1]);
  }
  graph->Fit("fit", "R");
  //fun = graph->GetFunction("fit");
  graph->GetFunction("fit")->SetLineWidth(1);
  graph->GetFunction("fit")->SetLineColor(fit_color);
  graph->SetMarkerColor(marker_color);
  graph->SetMarkerStyle(8);
  graph->SetMarkerSize(0.5);

  double* fit_params = graph->GetFunction("fit")->GetParameters();

  TLegend* legend = new TLegend(0.15, 0.75, 0.75, 0.90, yvar.c_str());
  char formula[256];
  if (degrees_of_freedom == 3) {
    snprintf(formula, sizeof(formula), "(%.4e)x^2 + (%.4e)x + %.4e", fit_params[2], \
            fit_params[1], fit_params[0]);
  } else if (degrees_of_freedom == 2) {
    snprintf(formula, sizeof(formula), "(%.4e)x + %.4e", \
              fit_params[1], fit_params[0]);
  }
  legend->AddEntry("fit", formula);

  can->Draw();
  can->SetGridx();
  can->SetGridy();
  can->cd();

  graph->GetXaxis()->SetTitle(xvar.c_str());
  graph->GetXaxis()->CenterTitle();
  graph->GetXaxis()->SetTitleOffset(1.1);
  graph->GetYaxis()->SetTitle(yvar.c_str());
  graph->GetYaxis()->SetTitleOffset(1.4);
  graph->GetYaxis()->CenterTitle();
  graph->GetXaxis()->SetRangeUser(min_PDAC - 5, max_PDAC + 5);
  graph->GetYaxis()->SetRangeUser(0.,max_XADC/4096.*1.1);
  graph->Draw("ap");

  legend->Draw();

  TFile* test = new TFile((outputfile + ".root").c_str(),"RECREATE");
  test->cd();
  can->Write();
  test->Close();
}
