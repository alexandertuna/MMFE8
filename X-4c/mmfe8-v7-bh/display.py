from ROOT import gROOT, gPad, TCanvas, TF1, TH1I
import time
 
gROOT.Reset()

c1 = TCanvas( 'evtDisp', 'All Channels', 1400, 1000 )
 
#
# Create a one dimensional function and draw it
#

c1.Divide(2,2)

h_chan = TH1I( 'h_chan', 'channel occupancy', 64, 0, 65 )

h_amp_all = TH1I( 'h_amp_all', 'amplitude for all channels', 1050, 0, 1050 )

h_time_all = TH1I( 'h_time_all', 'time for all channels', 100, 0, 260 )

h_bcid_all = TH1I( 'h_bcid_all', 'bcid for all channels', 4095, 1, 4100 )

h_amp = []
h_time = []
h_bcid = []

for chan in range(0,65):
    name = 'h_amp_{0}'.format(chan)
    title = 'channel {0} amplitude'.format(chan)
    h_temp = TH1I( str(name), str(title), 1050, 0, 1050 )
    h_amp.append(h_temp)
    
    name = 'h_time_{0}'.format(chan)
    title = 'channel {0} time'.format(chan)
    h_temp = TH1I( str(name), str(title), 100, 0, 260 )
    h_time.append(h_temp)

    name = 'h_bcid_{0}'.format(chan)
    title = 'channel {0} bcid'.format(chan)
    h_temp = TH1I( str(name), str(title), 4095, 1, 4100 )
    h_bcid.append(h_temp)

c1.cd(1)
h_chan.Draw()

c1.cd(2)
h_bcid_all.Draw()

c1.cd(3)
h_amp_all.Draw()

c1.cd(4)
h_time_all.Draw()

h_chan.SetXTitle('channel number')
h_bcid_all.SetXTitle('bcid')
h_amp_all.SetXTitle('amplitude')
h_time_all.SetXTitle('time')

c1.Update()

startFromLine = 1

hasNewData = True

while 1 > 0:

    infile = open('mmfe8Test.dat','r')
    #infile = open('data.txt','r')
    linesCounter = 0
    
    for line in infile:
        #print 'linesCounter = {0}'.format(linesCounter)
        if linesCounter > startFromLine:
            hasNewData = True
            #print line
            entry = line.split()
            if len(entry) == 4:
            #if len(entry) == 3:
                
                evtChan = int(entry[0])
                evtAmp = float(entry[1])
                evtTime = float(entry[2])
                evtBCID = float(entry[3])
                #print 'chan = {0} amp = {1} time = {2}'.format(evtChan,evtAmp,evtTime)
                
                h_chan.Fill(evtChan)
                h_amp_all.Fill(evtAmp)
                h_time_all.Fill(evtTime)
                h_bcid_all.Fill(evtBCID)
                
                h_amp[evtChan].Fill(evtAmp)
                h_time[evtChan].Fill(evtTime)
                h_bcid[evtChan].Fill(evtBCID)

        linesCounter += 1

    startFromLine = linesCounter - 1

    if hasNewData:

        c1.cd(1)
        h_chan.Draw()

        c1.cd(2)
        h_bcid_all.Draw()

        c1.cd(3)
        h_amp_all.Draw()

        c1.cd(4)
        h_time_all.Draw()

        c1.Update()

        hasNewData = False

    time.sleep( 0.0167 )
