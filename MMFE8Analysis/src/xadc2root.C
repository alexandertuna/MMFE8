// C++ includes
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <dirent.h>

// ROOT includes
#include <TROOT.h>
#include <TFile.h>
#include <TTree.h>
#include <TChain.h>

using namespace std;

/// Main function that runs the analysis algorithm on the
/// specified input files
int main(int argc, char* argv[]) {
  char inputFileName[400];
  char outputFileName[400];

  if ( argc < 2 ){
    cout << "Error at Input: please specify an input .dat file";
    cout << " and an output filename" << endl;
    cout << "Example:   ./dat2root input_file.dat" << endl;
    cout << "Example:   ./dat2root input_file.dat -o output_file.root" << endl;
    return 1;
  }
  bool user_output = false;
  for (int i=0;i<argc;i++){
    sscanf(argv[1],"%s", inputFileName);
    if (strncmp(argv[i],"-o",2)==0){
      sscanf(argv[i+1],"%s", outputFileName);
      user_output = true;
    }

    // if (strncmp(argv[i],"-Njob",5)==0)
    //   sscanf(argv[i],"-Njob=%d",  &NJOB);
    // if (strncmp(argv[i],"-ijob",5)==0)
    //   sscanf(argv[i],"-ijob=%d",  &iJOB);
  }
  if(!user_output)
    sprintf(outputFileName,"%s.root",inputFileName);

  cout << "Input File:  " << inputFileName << endl;
  cout << "Output File: " << outputFileName << endl;

  vector<string> sVAR;
  sVAR.push_back("VMM");
  sVAR.push_back("CHword");
  sVAR.push_back("CHpulse");
  sVAR.push_back("PDO");
  sVAR.push_back("TDO");
  sVAR.push_back("BCID");
  sVAR.push_back("TPDAC");
  sVAR.push_back("THDAC");
  sVAR.push_back("Delay");
  sVAR.push_back("TACslope");
  sVAR.push_back("PeakTime");

  int Nvar = sVAR.size();
  vector<int> vVAR;
  for(int i = 0; i < Nvar; i++)
    vVAR.push_back(0);

  string line;
  ifstream ifile(inputFileName);

  TFile* ofile = new TFile(outputFileName,"RECREATE");
  ofile->cd();
  TTree* tree = new TTree("MMFE8","MMFE8");

  for(int i = 0; i < Nvar; i++){
    tree->Branch(sVAR[i].c_str(), &vVAR[i]);
  }

  if(ifile.is_open()){
    while(getline(ifile,line)){
      char sline[1000];
      sprintf(sline,"%s",line.c_str());
      char* p = strtok(sline, " ");
      while(p){
      	for(int v = 0; v < Nvar; v++){
      	  if(strncmp(sVAR[v].c_str(),p,sVAR[v].length())==0){
      	    sscanf(p,(sVAR[v]+"=%d").c_str(), &vVAR[v]);
      	    break;
      	  }
      	}
      	p = strtok(NULL, " ");
      }
      tree->Fill();
    }
  }

  ofile->cd();
  tree->Write();
  ofile->Close();

  return 0;
}
