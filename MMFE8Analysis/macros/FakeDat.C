#include <iostream>
#include <fstream>
using namespace std;

int main () {
  ofstream myfile;
  myfile.open ("example.txt");
  myfile << "Writing this to a file.\n";
  myfile.close();
  return 0;
}

void FakeDat(string output){
  int N = 1000;
  
  ofstream ofile;
  ofile.open (output.c_str());

  for(int i = 0; i < N; i++){
    int VMM = int(gRandom->Rndm()*8.)+1;
    int CHword = int(gRandom->Rndm()*64.)+1;
    int CHpulse = CHword;
    int PDO = int(fabs(gRandom->Gaus(777,30.)));
    int TDO = int(fabs(gRandom->Gaus(500,30.)));
    int BCID = int(100000.*gRandom->Rndm());
    int TPDAC = int(gRandom->Gaus(300.,10.));
    int THDAC = int(gRandom->Gaus(400.,10.));
    int Delay = int(gRandom->Rndm()*4.);
    int TACslope = 125;
    int PeakTime = 200;

    ofile << "VMM=" << VMM;
    ofile << " CHword=" << CHword;
    ofile << " CHpulse=" << CHpulse;
    ofile << " PDO=" << PDO;
    ofile << " TDO=" << TDO;
    ofile << " BCID=" << BCID;
    ofile << " TPDAC=" <<  TPDAC;
    ofile << " THDAC=" << THDAC;
    ofile << " Delay=" << Delay;
    ofile << " TACslope=" << TACslope;
    ofile << " PeakTime=" << PeakTime << endl;

  }
  ofile.close();
}
