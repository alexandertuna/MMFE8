#include <TH1I.h>
#include <TF1.h>
#include <TCanvas.h>
#include <cmath>
#include <string>

using namespace std;

/***************  RUN SETTINGS  ***************/
string



/**************  CODE BELOW  ***************/

// Totally jacked from https://meetingcpp.com/index.php/br/items/cpp-and-pi.html
constexpr double const_pi() { return std::atan(1)*4; }

// Function prototype
double double_histogram_function(double* xs, double* ps);

// Main function.
// Invariants: parameters: {N0, mu0, sig0, N1, mu1, sig1}
void double_histogram_fit(){
  // Open file

  // Populate histogram with appropriate settings

  // Create the double histogram function with the appropriate defaults
  // and limits

  // Fit the Function

  // Plot results
}

// General normal distribution with integral N
double normal_distribution(double N, double mu, double sg, double x){
  double G = exp(-((x - mu)**2) / (2 * (sg**2))) / (sqrt(2 * const_pi()) * sg);
  return N * G;
}

// Custom function for test pulse DAC fit, two Gaussians.
// Invariants: parameters: {N0, mu0, sig0, N1, mu1, sig1}
double double_histogram_function(double* xs, double* par){
  float x = xs[0];
  double G0 = normal_distribution(par[0], par[1], par[2], x);
  double G1 = normal_distribution(par[3], par[4], par[5], x);
  return G0 + G1;
}
