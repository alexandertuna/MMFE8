#include <TH1I.h>
#include <TF1.h>
#include <TCanvas.h>
#include <cmath>
#include <string>
#include "../include/xADCBase.hh"

using namespace std;

/***************  RUN SETTINGS  ***************/
const string input_file = "../../mmfe8_gui/CalibrationRoutine/mmfe8_CalibRoutine.root";
const unsigned int tpDAC = 140;
const unsigned int vmm = 3;


/**************  CODE BELOW  ***************/

// Global settings:
const string tree_name = "xADC_data";
const string x_label = "xADC readout (counts, 12-bit 1V full-range)";
const string y_label = "Number of events (count)";
const string func_name = "double_gauss";

// Totally jacked from https://meetingcpp.com/index.php/br/items/cpp-and-pi.html
constexpr double const_pi() { return std::atan(1)*4; }

// Function prototype
double double_gaus_function(double* xs, double* par);

// Main function.
// Invariants: parameters: {N0, mu0, sig0, N1, mu1, sig1}
void double_histogram_fit(){
  // Open file
  TChain* tree = new TChain(tree_name.c_str(), tree_name.c_str());
  tree->AddFile(filename.c_str());
  xADCBase* base = new xADCBase(tree);

  // Populate histogram with appropriate settings
  const float min_count = -0.5; const float max_count = 4095.5;
  const unsigned int N = tree->GetEntries();
  TH1I* hist = new TH1I("xADC data", "xADC data", 4096, min_count, max_count);

  for (unsigned int i = 0; i < N; i++){
    base->GetEntry(i);
    if ((vmm == base->VMM) && (tpDAC == base->PDAC) && (base->CKTPrunning)) {
      hist->Fill(base->XADC);
    }
  }

  // Create the double Gaussian function with the appropriate defaults
  // and limits. Parameters: {N0, mu0, sig0, N1, mu1, sig1}
  const float mu_tot = hist->GetMean();
  const float sig_tot = hist->GetStdDev();
  TF1* fun = new TF1(func_name.c_str(), double_gaus_function, min_count,
                              max_count, 6);

  // Defaults:
  fun->SetParameter(0, N / 2); // N0 = N1 = Ntot/2
  fun->SetParameter(3, N / 2);
  fun->SetParameter(1, mu_tot - sig_tot); // mu0
  fun->SetParameter(4, mu_tot + sig_tot);
  // fun->SetParameter(2, sig_tot / 2); // sig0
  // fun->SetParameter(5, sig_tot / 2);

  // Limits:
  fun->SetParLimits(0, 0, 2 * N); // 0 < N0, N1 < 2Ntot
  fun->SetParLimits(3, 0, 2 * N);
  fun->SetParLimits(1, 0, mu_tot); // 0 < mu0 < mu_tot
  fun->SetParLimits(4, mu_tot, max_count);
  fun->SetParLimits(2, 0, max_count); // 0 < sig0, sig1 < large number
  fun->SetParLimits(5, 0, max_count);

  // Plot and fit
  TCanvas* can = new TCanvas("can", "can", 800, 600);
  can->SetTopMargin(0.05);
  can->SetLeftMargin(0.12);
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  can->Draw();
  can->SetGridx();
  can->SetGridy();
  can->cd();
  hist->Draw();
  hist->Fit(func_name.c_str(), "IL");
  fun->Draw("same");
}

// General normal distribution with integral N
double normal_distribution(double N, double mu, double sg, double x){
  double G = exp(-((x - mu)**2) / (2 * (sg**2))) / (sqrt(2 * const_pi()) * sg);
  return N * G;
}

// Custom function for test pulse DAC fit, two Gaussians.
// Invariants: parameters: {N0, mu0, sig0, N1, mu1, sig1}
double double_gaus_function(double* xs, double* par){
  float x = xs[0];
  double G0 = normal_distribution(par[0], par[1], par[2], x);
  double G1 = normal_distribution(par[3], par[4], par[5], x);
  return G0 + G1;
}
