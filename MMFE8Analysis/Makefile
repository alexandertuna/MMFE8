ROOTCFLAGS    = $(shell root-config --cflags)
ROOTGLIBS     = $(shell root-config --glibs)

CXX            = g++
CXXFLAGS       = -fPIC -Wall -O3 -g
CXXFLAGS       += $(filter-out -stdlib=libc++ -pthread , $(ROOTCFLAGS))
GLIBS          = $(filter-out -stdlib=libc++ -pthread , $(ROOTGLIBS))

INCLUDEDIR       = ./include/
SRCDIR           = ./src/
CXX	         += -I$(INCLUDEDIR) -I.
OUTOBJ	         = ./obj/

CC_FILES := $(wildcard src/*.cc)
HH_FILES := $(wildcard include/*.hh)
OBJ_FILES := $(addprefix $(OUTOBJ),$(notdir $(CC_FILES:.cc=.o)))

all: dat2root calibrate_tpDAC

dat2root:  $(SRCDIR)dat2root.C $(OBJ_FILES) $(HH_FILES)
	$(CXX) $(CXXFLAGS) -o dat2root $(GLIBS) $ $<
	touch dat2root
	# $(CXX) $(CXXFLAGS) -o dat2root $(OUTOBJ)*.o $(GLIBS) $ $<	

calibrate_tpDAC:  $(SRCDIR)calibrate_tpDAC.c $(OBJ_FILES) $(HH_FILES)
	$(CXX) $(CXXFLAGS) -o calib_tpDAC $(GLIBS) $ $<
	touch calib_tpDAC

$(OUTOBJ)%.o: src/%.cc include/%.hh
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OUTOBJ)*.o
	rm -rf *.dSYM
	rm -f dat2root
	rm -f xdat2root
	rm -f calib_tpDAC
