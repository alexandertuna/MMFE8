/*
 * Ben Garber, Harvard University Laboratory for Particle Physics and Cosmology
 * April 2016
 * MicroMegas development: VMM2 calibration and testing
 *
 * PDO_linearity: plotting PDO vs. input charge
 *
 * Assumptions: That the observed lack of change of voltage between CKTP on
 * and off holds, and therefore that the xADC voltage with CKTP off is
 * identical to the test pulse height.
 */

// Includes
#include <vector>
#include <string>
#include <TH1D.h>
#include <TH1I.h>
#include <TCanvas.h>
#include <TStyle.h>
#include <TGraphErrors.h>
#include <TLegend.h>
#include "../include/xADCBase.hh"
#include "../include/MMFE8Base.hh"

using namespace std;

/************ User-editable constants ************/

const string input_filename = \
  "../../mmfe8_gui/CalibrationRoutine/mmfe8_CalibRoutine.dat.root";
const int vmm = 3;
const int channel = 15;
const int min_PDAC = 60;
const int max_PDAC = 300;
const int min_events_per_bin = 10;


/******* Physical constants ******/
/* 12-bit xADC w/ 1V full range, 1.2pF capacitor
 * -> Q = CV = 1.2pF * (1mV/4.096 counts)
 */
const double fC_per_xADC_count = 1.2 / 4.096;

/* Names */
const string vtree_name = "VMM_data";
const string xtree_name = "xADC_data";
const string x_axis_label = "Input charge (fC)";
const string y_axis_label = "PDO output (counts)";
const string plot_title = "PDO calibration";

void PDO_linearity (void) {
  // Open trees
  TChain* xtree = new TChain(xtree_name.c_str());
  TChain* vtree = new TChain(vtree_name.c_str());
  xtree->AddFile(input_filename.c_str());
  vtree->AddFile(input_filename.c_str());
  int Nxadc = xtree->GetEntries();
  int Nvmm = vtree->GetEntries();
  xADCBase* xbase = new xADCBase(xtree);
  MMFE8Base* vbase = new MMFE8Base(vtree);

  // Initialize empty histograms for each possible PDAC value
  const int num_pdacs = max_PDAC - min_PDAC + 1;
  TH1D* xhists[num_pdacs];
  TH1I* vhists[num_pdacs];
  for (int i = 0; i < num_pdacs; i++) {
    int current_PDAC = i + min_PDAC;
    char xtitle[100], vtitle[100];
    snprintf(xtitle, 100, "xADC, PDAC=%d",current_PDAC);
    snprintf(vtitle, 100, "PDO, PDAC=%d",current_PDAC);
    xhists[i] = new TH1D(xtitle, plot_title.c_str(), 4096, -0.1465, 1199.8535);
    vhists[i] = new TH1I(vtitle, plot_title.c_str(), 1024, 0.5, 1023.5);
  }

  // Select data, add it to histograms
  for (int i = 0; i < Nxadc; i++){
    xbase->GetEntry(i);
    int current_PDAC = xbase->PDAC;
    if ((vmm == xbase->VMM) && (current_PDAC >= min_PDAC) && (current_PDAC <= max_PDAC)) {
      double charge = float(xbase->XADC) * fC_per_xADC_count;
      xhists[current_PDAC - min_PDAC]->Fill(charge);
      //printf("PDAC: %d, charge: %.02f, unconverted: %d\n", current_PDAC, charge, xbase->XADC);
    } else {
      printf("Rejected: VMM %d, PDAC %d, unconverted %d\n", xbase->VMM, current_PDAC, xbase->XADC);
    }
  }
  for (int i = 0; i < Nvmm; i++){
    vbase->GetEntry(i);
    int current_PDAC = vbase->TPDAC;
    if ((channel == vbase->CHword) && (vbase->CHpulse == vbase->CHword) && (vmm == vbase->VMM) && (current_PDAC >= min_PDAC) && (current_PDAC <= max_PDAC)) {
      vhists[current_PDAC - min_PDAC]->Fill(vbase->PDO);
      //printf("PDAC: %d, PDO: %d\n", current_PDAC, vbase->PDO);
    } /*else {
      printf("Rejected: VMM %d, CHword %d, CHpulse %d, PDAC %d, PDO %d\n",
             vbase->VMM, vbase->CHword, vbase->CHpulse, current_PDAC, vbase->PDO);
    }*/
  }

  // Pick out large-enough-N points, add them to arrays
  double XADC_means[num_pdacs];
  double XADC_stddevs[num_pdacs];
  double PDO_means[num_pdacs];
  double PDO_stddevs[num_pdacs];
  double PDAC_values[num_pdacs];
  int num_points = 0;

  for (int i = 0; i < num_pdacs; i++){
    if ((vhists[i]->GetEntries() >= min_events_per_bin) && (xhists[i]->GetEntries() >= min_events_per_bin)){
      PDAC_values[num_points] = float(i + min_PDAC);
      XADC_means[num_points] = xhists[i]->GetMean();
      XADC_stddevs[num_points] = xhists[i]->GetStdDev();
      PDO_means[num_points] = vhists[i]->GetMean();
      PDO_stddevs[num_points] = vhists[i]->GetStdDev();
      num_points++;
    }
  }

  //TGraphErrors* graph = new TGraphErrors(num_points, XADC_means, PDO_means, XADC_stddevs, PDO_stddevs);
  //TGraphErrors* graph = new TGraphErrors(num_points, PDAC_values, PDO_means, 0, PDO_stddevs);
  TGraphErrors* graph = new TGraphErrors(num_points, PDAC_values, XADC_means, 0, XADC_stddevs);
  TCanvas* can = new TCanvas("can","can",600,500);
  can->SetTopMargin(0.1);
  graph->SetTitle(plot_title.c_str());
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);

  can->Draw();
  can->SetGridx();
  can->SetGridy();
  can->cd();

  graph->GetXaxis()->SetTitle(x_axis_label.c_str());
  graph->GetXaxis()->CenterTitle();
  graph->GetXaxis()->SetTitleOffset(1.1);
  graph->GetYaxis()->SetTitle(y_axis_label.c_str());
  graph->GetYaxis()->SetTitleOffset(1.4);
  graph->GetYaxis()->CenterTitle();
  graph->GetXaxis()->SetRangeUser(0., 300.);
  graph->GetYaxis()->SetRangeUser(0.,1100.);
  graph->Draw("ap");
}
