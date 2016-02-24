#!/usr/bin/env python26

#    by Charlie Armijo, Ken Johns, Bill Hart, Sarah Jones, James Wymer, Kade Gigliotti
#    Experimental Elementary Particle Physics Laboratory
#    Physics Department
#    University of Arizona    
#    armijo at physics.arizona.edu
#    johns at physics.arizona.edu
#
#    This is version 7 of the MMFE8 GUI

#    calibration routine by Christopher Rogan
#    Physics Department
#    Harvard University    
#    crogan at cern.ch



import pygtk
pygtk.require('2.0')
import gtk
from array import *
#### On PCROD0 use from Numpy import *
import numpy as np
#from Numeric import *
from struct import *
import gobject 
from subprocess import call
from time import sleep
import sys 
import os
import string
import random
import binstr
import socket
import time
import math
from mmfe8_vmm import vmm
from mmfe8_chan import channel
from mmfe8_userRegs import userRegs
from mmfe8_udp import udp_stuff
from mmfe8_guiUtil import loop_pair


############################################################################
############################################################################
###############################               ##############################
###############################  MMFE8 CLASS  ##############################
###############################               ##############################
############################################################################
############################################################################

class MMFE8:
    """
    # ipAddr will be obtained from an xml file in the future
    ipAddr = ["127.0.0.1","192.168.0.130","192.168.0.101","192.168.0.102","192.168.0.103","192.168.0.104","192.168.0.105","192.168.0.106",
              "192.168.0.107","192.168.0.108","192.168.0.109","192.168.0.110","192.168.0.111","192.168.0.112","192.168.0.167"]
    # each is the starting address for the 51 config regs for each vmm 
    mmfeID = 0
    vmmBaseConfigAddr = [0x44A10020,0x44A10038,0x44A10050,0x44A10068,
                         0x44A10080,0x44A10098,0x44A100B0,0x44A100C8,0x44A100E0]
    vmm_cfg_sel_reg = np.zeros((32), dtype=int)
    VMM = []
    UDP_PORT = 50001
    UDP_IP = ""
    chnlReg = np.zeros((51), dtype=int)
    vmmGlobalReset = np.zeros((32), dtype=int)
    start_intTrig_pulseCnt = np.zeros((32), dtype=int)
    byteint = np.zeros((51), dtype=np.uint32)
    byteword = np.zeros((32), dtype=int)
    """


    def destroy(self,widget,data=None):
        # exit gently
        self.stopReadOut = True
        sleep(1) # allow the threads to complete
        print "Goodbye from the MMFE8 GUI!"
        gtk.main_quit()
        
    def on_erro(self, widget, msg):
        md = gtk.MessageDialog(None,
             gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
             gtk.BUTTONS_OK, msg)
        md.set_title("ERROR")
        md.run()
        md.destroy()
   
	
    ######################################################
    #    Configuration Functions
    ######################################################

    def write_vmmConfigRegisters(self,widget):
        """ create full config list """
        current_vmm = int(self.notebook.get_current_page())
        # command strings must be <= 100 chars
        # due to bram limitations on artix7
        self.VMM[current_vmm].entry_SDP_.grab_focus()
        self.VMM[current_vmm].entry_SDT.grab_focus()
        self.button_write.grab_focus()
        #active = self.combo_vmm2_id.get_active()
        #configAddr = self.vmmBaseConfigAddr[0]
        reg = self.VMM[current_vmm].get_channel_val()
        reglist = list(self.VMM[current_vmm].reg.flatten())
        globalreglist = list(self.VMM[current_vmm].globalreg.flatten())
        fullreg = reglist[::-1] + globalreglist[::-1] 
        chars = []
        MESSAGE = ""
        n=0
        m=0
        w=0
        reglist = reglist[::-1]
        for b in range(51):
            self.byteint[b] = 0
            bytelist = fullreg[b*32:(b+1)*32]
            n = n+1
            dummyReg = bytelist[::-1]
            #string = "A" + str(b)
            for bit in range(32):
                self.byteint[b] += int(dummyReg[bit])*pow(2, 31-bit)             
        StartMsg =  "W" +' 0x{0:08X}'.format(self.vmmBaseConfigAddr[0]) #.decode('hex')      
        for c in range(0,51):
            string = "A" + str(c+1)
            myVal = int(self.byteint[c])
            MESSAGE = MESSAGE + ' 0x{0:X}'.format(myVal)
            if (c+1)%6 == 0:
                w = w + 1
                MSGsend = StartMsg + MESSAGE + '\0' + '\n'
                MESSAGE = ""
                m = m + 24
                StartMsg = "W" +' 0x{0:08X}'.format(self.vmmBaseConfigAddr[w])
                self.udp.udp_client(MSGsend,self.UDP_IP,self.UDP_PORT)
                #if self.myDebug:
                #    print "Sent Message to " + self.UDP_IP 
                #    print MSGsend #+ "  {0}".format(m)    
        MSGsend = StartMsg + MESSAGE + '\0' + '\n'
        self.udp.udp_client(MSGsend,self.UDP_IP,self.UDP_PORT)
        #if self.myDebug:
        #    print "Sent Message to " + self.UDP_IP 
        #    print MSGsend
        print "\nWrote to Config Registers\n" 
        self.load_IDs()
        #sleep(5)
        #self.daq_readOut()
        return

    def glob_DC_value(self, widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            DC = active
            MSGsend1 = "W 0x44A10148 {0:02x} \0\n".format(DC)
            self.udp.udp_client(MSGsend1,self.UDP_IP,self.UDP_PORT)
            sleep(1)
               

    def read_reg(self,widget):
        # not currently used -- was intended to read the config stream out
        return        
             
    def print_config(self, widget):
        current_vmm = int(self.notebook.get_current_page())
        ##create and print full config list
        self.VMM[current_vmm].entry_SDP_.grab_focus() # gets data for 
        self.VMM[current_vmm].entry_SDT.grab_focus()
        self.button_print_config.grab_focus()
        reg = self.VMM[current_vmm].get_channel_val()
        reglist = list(self.VMM[current_vmm].reg.flatten())
        globalreglist = list(self.VMM[current_vmm].globalreg.flatten())
        fullreg = reglist[::-1] + globalreglist[::-1]
        #self.buf = [] 
        print "\n\nCONFIG STRING for VMM" + str(current_vmm + 1)
        n=0
        reglist = reglist[::-1]
        #try:
        for b in range(51):
            bytelist = fullreg[b*32:(b+1)*32]
            byteint = 0
            n = n+1
            dummyReg = bytelist[::-1]
            for bit in range(32):
                byteint += int(dummyReg[bit])*pow(2, 31-bit)
            byte = bin(byteint)
            byteword = int(byteint)
            self.chnlReg[b] = byteword
            #print hex(self.chnlReg[b])
            print "0x{0:08x}  reg {1:2d}".format(byteword,n)  
            #except:  IOError as e:
            #    myMsg = "I/O Error"# Reading Ctrl Reg 3:\n{1}".format(e.errno, e.strerror)
            #    #    self.on_erro(widget, myMsg)
        return

    ######################################################
    #    Readout Functions
    ######################################################

    def daq_readOut(self):
        fifoCnt = 0
        r=10
        #while ( ( fifoCnt == 0) and ( self.terminate == 0)):
        while ( ( fifoCnt == 0) and ( r != 0)):
            #if( self.terminate == 1):
            #    return
            r = r -1
            msgFifoCnt = "r 0x44A10014 1 \0 \n" # read word count of data fifo
            FifoCntData = self.udp.udp_client(msgFifoCnt,self.UDP_IP,self.UDP_PORT)
            print FifoCntData
            FifoCntStr = string.split(FifoCntData,' ') # split the string to a list
            print FifoCntStr
            fifoCnt = int(FifoCntStr[2],16) # We now have the number of words in the FIFO
            sleep(1)
        print "FIFOCNT ", fifoCnt
        if fifoCnt % 2 == 0:
            fcnt = fifoCnt
        else:
            print "/nlost one count"
            fcnt = (fifoCnt - 1)
        cycles = fcnt / 10  # reading 10 32-bit data words
        remainder = fcnt % 10
        for i in range(1+cycles)[::-1]:  # reverses the order of the count
            #if( self.terminate == 1):
            #    return
            if i == 0:                             # 0 has less than ten words
                m = 2 + remainder
                reads = remainder  # less that 10
            else:
                m = 12 # total words in packet payload
                reads = 10
            msgFifoData = "k 0x44A10010 " + str(reads) + "\n" # read 10 words from fifo
            fifoData = self.udp.udp_client(msgFifoData,self.UDP_IP,self.UDP_PORT)
            n = 2
            while n < m:
                #if( self.terminate == 1):
                #    return
                dataList = fifoData.split()
                fifo32 = int(dataList[n],16)
                if fifo32 > 0:
                    fifo32 = fifo32 >> 2     # get rid of first 2 bits (threshold)
                    addr = (fifo32 & 63) + 1 # get channel number as on GUI
                    fifo32 = fifo32 >> 6     # get rid of address
                    amp = fifo32 &  1023 # get amplitude
                    #if (amp & 15) == 0:  # are the lower 4 bit zeros?  if so, tag.
                    #    odd = " ****"
                    #else:
                    #    odd = ""
                    fifo32 = fifo32 >> 10
                    timing = fifo32 & 255
                    fifo32 = fifo32 >> 8  # we will later check for vmm number
                    vmm = fifo32 &  7 # get vmm number
                    if (n+1) < 12:
                        fifohigh = int(dataList[n+1],16)
                        print fifohigh
                        BCIDgray = int(fifohigh & 4095) # next change from gray code to int
                        BCid2 = binstr.int_to_b(BCIDgray,16)
                        myBCid = binstr.b_gray_to_bin(BCid2)
                        myIntBCid = binstr.b_to_int(myBCid)
                        fifohigh = fifohigh >> 12  # later we will get the turn number 	 
                    #print dataList[n+1] + " "+ dataList[n] + ", addr=" + str(addr) + \
                    #               ", amp="+str(amp) + ", time="+str(timing) + ", BCid= " + str(myIntBCid)
                    print dataList[n] + " "+ dataList[n+1] + ", addr=" + str(addr) + \
                                   ", amp="+str(amp) + ", time="+str(timing) + ", BCid= " + str(myIntBCid) + ", VMM= " + str(vmm)
                    #with open('mmfe8Test.dat', 'a') as myfile:
                    #            myfile.write(str(int(addr))+'\t'+ str(int(amp))+'\t'+ str(int(timing))+'\t'+ str(myIntBCid) +'\n')
                    with open('mmfe8Test.dat', 'a') as myfile:
                                myfile.write(str(int(addr))+'\t'+ str(int(amp))+'\t'+ str(int(timing))+'\t'+ str(myIntBCid) +'\t'+ str(vmm) +'\n')
                    n=n+2
                else:
                    print "out of order or no data ="# + str(hex(dataList[n]))
                    #n= n+1       
                    n=n+2 #paolo
					
					
    def read_xadc(self, widget):
        #msg = "w 0x44A10058 1 \0 \n"
        self.udp.udp_client(msg,self.UDP_IP,self.UDP_PORT)
        msg = "x \0 \n"  # command to command_handler to send xadc
        # 1. request pdo from microblaze
        myXADC = self.udp.udp_client(msg,self.UDP_IP,self.UDP_PORT) 
        # 2. create an empty list
        pd = [] 
        n = 1
        while n<9:
            
            xadcList = myXADC.split()
            thing1 = int(xadcList[n],16)
            thing2 = (thing1 * 1.0)/4096.0
            pd.append(thing2)
            n = n+1
            print 'XADC = {0:.4f} {1:.4f} {2:.4f} {3:.4f} {4:.4f} {5:.4f} {6:.4f} {7:.4f}'.format(pd[0],pd[1],pd[2],pd[3],pd[4],pd[5],pd[6],pd[7]) 
            s = '{0:.4f}\t{1:.4f}\t{2:.4f}\t{3:.4f}\t{4:.4f}\t{5:.4f}\t{6:.4f}\t{7:.4f}\n'.format(pd[0],pd[1],pd[2],pd[3],pd[4],pd[5],pd[6],pd[7])
            with open('mmfe8-xadc.dat', 'a') as myfile:
                myfile.write(s)  
        return
		
    def internal_trigger(self, widget):
        if widget.get_active():
            widget.set_label("ON")
            self.readout_runlength[24] = 1
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        else:
            widget.set_label("OFF")
            self.readout_runlength[24] = 0
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100F4" 
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        return

    def external_trigger(self, widget):
        if widget.get_active():
            widget.set_label("ON")
            self.readout_runlength[26] = 1
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        else:
            widget.set_label("OFF")
            self.readout_runlength[26] = 0
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100F4"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        return

    def leaky_readout(self, widget):
        if widget.get_active():
            widget.set_label("ON")
            self.readout_runlength[25] = 1
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        else:
            widget.set_label("OFF")
            self.readout_runlength[25] = 0
            #self.udp.udp_client(MSG,self.UDP_IP,self.UDP_PORT)
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100F4"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        return


    def set_pulses(self,widget,entry):
        try:
            entry = widget.get_text()
            value = int(entry)
        except ValueError:
            print "Pulses value must be a decimal integer"
            print
            return None                
        if (value < 0) or (999 < value): #0x3E7
            print "SDP value out of range"
            print "0 <= Pulses <= 999" 
            return None
        else:
            pulses = value
            ### convert value to list of binary digits ###
            pulses = '{0:010b}'.format(pulses)
            pulses_list = list(pulses)
            pulses_list = map(int, pulses)
            ### add new value to register ###
            for i in range(9,-1,-1):
                self.readout_runlength[9-i] = pulses_list[i] 
            tempInt = 0
            for bit in range(32):
                tempInt += int(self.readout_runlength[bit])*pow(2, bit)
            print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
            message = "w 0x44A100F4"
            message = message + ' 0x{0:X}'.format(tempInt)  
            message = message + '\0' + '\n'
            self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)  
            sleep(1)
            return

    def set_acq_reset_count(self,widget,entry):
        try:
            entry = widget.get_text()
            #entry = int( widget.get_text(),base=16)
            value = int(entry,base=16)
        except ValueError:
            print "acq_count value must be a hex number"
            print
            return None                
        if (value < 0) or (0xffffffff < value): #0x3E7
            print "Acq count value out of range"
            print "0 <= acq_count <= 0xffffffff" 
            return None
        else:
            acq_count = value
            MESSAGE = "W 0x44A10120 " + str(value) + '\0' + '\n'             
            print "Wrote",hex(value),"to counts_to_acq_reset"
            print "counts_to_acq_reset = " + ' 0x{0:X}'.format(value) #str(hex(tempInt))
            data = self.udp.udp_client(MESSAGE,self.UDP_IP,self.UDP_PORT)
            sleep(1)
            myData = string.split(data,'\n')
            return

    def set_acq_reset_hold(self,widget,entry):
        try:
            entry = widget.get_text()
            #entry = int( widget.get_text(),base=16)
            value = int(entry,base=16)
        except ValueError:
            print "acq_hold value must be a hex number"
            print
            return None                
        if (value < 0) or (0xffffffff < value): #0x3E7
            print "Acq hold value out of range"
            print "0 <= acq_hold <= 0xffffffff" 
            return None
        else:
            acq_count = value
            MESSAGE = "W 0x44A10124 " + str(value) + '\0' + '\n'             
            print "Wrote",hex(value),"to counts_to_acq_hold"
            print "counts_to_acq_hold = " + ' 0x{0:X}'.format(value) #str(hex(tempInt))
            data = self.udp.udp_client(MESSAGE,self.UDP_IP,self.UDP_PORT)
            sleep(1)
            myData = string.split(data,'\n')
            return


    ######################################################
    #    Control Functions
    ######################################################
			
    def start(self, widget):
        tempInt = 0
        self.control[2] = 1
        #byteint = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
            #byteword = int(byteint) 
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        self.daq_readOut()                   
        sleep(1)
        tempInt = 0
        self.control[2] = 0
        #byteint = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
            #byteword = int(byteint) 
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        #self.daq_readOut()                   
        return
		
    def reset_global(self, widget):
        tempInt = 0
        self.control[0] = 1
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n'
        print "VMM Global Reset  " + message  
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT) 
        sleep(1)
        tempInt = 0
        self.control[0] = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n'
        print "VMM Global Reset  " + message  
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT) 
        sleep(1)
        return
   
    def system_init(self, widget):
        tempInt = 0
        self.control[1] = 1
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n' 
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        sleep(1)
        tempInt = 0
        self.control[1] = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n' 
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        sleep(1)
        return

    def system_load(self, widget):
        tempInt = 0
        self.control[3] = 1
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n' 
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        sleep(1)
        tempInt = 0
        self.control[3] = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
        message = "w 0x44A100FC" 
        message = message + ' 0x{0:X}'.format(tempInt) + '\0' + '\n' 
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        sleep(1)
        return


    ######################################################
    #    Setup Functions
    ######################################################

    def set_IDs(self, widget):
        self.load_IDs()
        return

    def load_IDs(self):
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.vmm_cfg_sel[bit])*pow(2, bit)
        print "vmm_cfg_sel = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100EC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        sleep(1)
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        print "readout_runlength = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100F4" 
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        sleep(1)
        return  
       
    def set_board_ip(self, widget, textBox):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            board = active
            self.userRegs.set_udp_ip(self.ipAddr[board])
            self.UDP_IP = self.ipAddr[board]
            print "mmfe8 ip addr = " + self.UDP_IP
            textBox.set_text(str(board))
            self.mmfeID = int(board)
            mmfe_ID = '{0:04b}'.format(self.mmfeID)
            mmfe_ID_list = list(mmfe_ID)
            mmfe_ID_list = map(int, mmfe_ID)
            #print mmfe_ID_list
            ### add new value to register ###
            for i in range(4): #,-1,-1):
                #self.vmm_cfg_sel[28+i] = mmfe_ID_list[i]
                self.vmm_cfg_sel[11-i] = mmfe_ID_list[i]
            print "MMFE8 ID= " + str(self.mmfeID)
            
    ##==============================================##

    def set_display(self, widget): #, textBox
        active = widget.get_active()
        if active < 0:
            return None
        else:
            my_display = active
            ### convert value to list of binary digits ###
            display = '{0:05b}'.format(int(my_display))
            display_list = list(display)
            #print display_list
            display_list = map(int, display)

            ### add new value to register ###
            for i in range(5):
                self.vmm_cfg_sel[16-i] = display_list[i]
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.vmm_cfg_sel[bit])*pow(2, bit)
        print "vmm_cfg_sel = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100EC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        return

    def set_display_no_enet(self, widget): #, textBox
        active = widget.get_active()
        if active < 0:
            return None
        else:
            my_display = active
            ### convert value to list of binary digits ###
            display = '{0:05b}'.format(int(my_display))
            display_list = list(display)
            #print display_list
            display_list = map(int, display)

            ### add new value to register ###
            for i in range(5):
                self.vmm_cfg_sel[16-i] = display_list[i]
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.vmm_cfg_sel[bit])*pow(2, bit)
        #print "vmm_cfg_sel = " + ' 0x{0:X}'.format(tempInt) #str(hex(tempInt))
        message = "w 0x44A100EC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        #self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        return
       
    ######################################################
    #    vmm Readout select Functions
    ######################################################
    
    def readoutVmm1_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[16] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[16] = 0
        self.load_IDs()

    def readoutVmm2_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[17] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[17] = 0
        self.load_IDs()

    def readoutVmm3_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[18] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[18] = 0
        self.load_IDs()

    def readoutVmm4_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[19] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[19] = 0
        self.load_IDs()

    def readoutVmm5_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[20] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[20] = 0
        self.load_IDs()

    def readoutVmm6_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[21] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[21] = 0
        self.load_IDs()

    def readoutVmm7_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[22] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[22] = 0
        self.load_IDs()

    def readoutVmm8_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.readout_runlength[23] = 1
        else:
        ### button is not checked ###
            self.readout_runlength[23] = 0
        self.load_IDs()
		
    ######################################################
    #    Reset / config vmm select Functions
    ######################################################

    def Vmm1Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[0] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[0] = 0
        self.load_IDs()
        return

    def Vmm2Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[1] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[1] = 0
        self.load_IDs()
        return

    def Vmm3Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[2] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[2] = 0
        self.load_IDs()
        return
    
    def Vmm4Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[3] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[3] = 0
        self.load_IDs()
        return
    
    def Vmm5Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[4] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[4] = 0
        self.load_IDs()
        return
    
    def Vmm6Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[5] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[5] = 0
        self.load_IDs()
        return
    
    def Vmm7Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[6] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[6] = 0
        self.load_IDs()
        return

    def Vmm8Reset_callback(self, widget):
        if widget.get_active():
        ### button is checked ###
            self.vmm_cfg_sel[7] = 1
        else:
        ### button is not checked ###
            self.vmm_cfg_sel[7] = 0
        self.load_IDs()
        return

    ######################################################
    #    CR - Calibration Routine Functions
    ######################################################

    def set_outputdat_LoopCR(self,widget,entry):
        fname = entry.get_text()
        if len(fname) <= 0:
            print "No Output .dat File Given"
            print
            return None 
        self.CRLoop_Output_dat = fname
        print "**CR-Loop** Setting output .dat filename to: %s" % fname
        print

    def set_outputroot_LoopCR(self,widget,entry):
        fname = entry.get_text()
        if len(fname) <= 0:
            print "No Output .root File Given"
            print
            return None 
        self.CRLoop_Output_root = fname
        print "**CR-Loop** Setting output .root filename to: %s" % fname
        print

    def set_pulses_LoopCR(self,widget,entry):
        try:
            entry = entry.get_text()
            val = int(entry)
        except ValueError:
            print "Number of pulses must be decimal integer"
            print
            return None
        if (val < 1) or (998 < val):
            print "Number of pulses must be between 1 and 998"
            print
            return None 
        self.CRLoop_Npulse = val
        print "**CR-Loop** Setting Number of Pulses: %s" % str(val)
        print

        
    def fix_tpDAC(self,widget,entry):
        try:
            entry = entry.get_text()
            value = int(entry)
        except ValueError:
            print "Test Pulse DAC must be decimal integer"
            print
            return None                
        if (value < 0) or (1023 < value):
            print "Test Pulse DAC out of range"
            print
            return None 

        self.CRLoop_tpDAC = [value]
        print "**CR-Loop** Setting Test Pulse DAC: %s" % str(value)
        print

    def loop_tpDAC(self,widget,entry):
        try:
            entry = entry.get_text()
            entry = entry.split(',')
            val = []
            for x in entry:
                x.strip()
                val += [int(x)]
        except ValueError:
            print "Test Pulse DAC must be decimal integer"
            print
            return None
        for x in val:               
            if (x < 0) or (1023 < x):
                print "Test Pulse DAC out of range"
                print
                return None 

        self.CRLoop_tpDAC = val
        tpDACstr = str(val[0])
        for x in val[1:]:
            tpDACstr += ", "+str(x)
        print "**CR-Loop** Setting Test Pulse DAC: %s" % tpDACstr
        print

    def fix_thDAC(self,widget,entry):
        try:
            entry = entry.get_text()
            value = int(entry)
        except ValueError:
            print "Threshold DAC must be decimal integer"
            print
            return None                
        if (value < 0) or (1023 < value):
            print "Threshold DAC out of range"
            print
            return None 

        self.CRLoop_thDAC = [value]
        print "**CR-Loop** Setting Threshold DAC %s" % str(value)
        print

    def loop_thDAC(self,widget,entry):
        try:
            entry = entry.get_text()
            entry = entry.split(',')
            val = []
            for x in entry:
                x.strip()
                val += [int(x)]
        except ValueError:
            print "Threshold DAC must be decimal integer"
            print
            return None
        for x in val:               
            if (x < 0) or (1023 < x):
                print "Threshold DAC out of range"
                print
                return None 

        self.CRLoop_thDAC = val
        thDACstr = str(val[0])
        for x in val[1:]:
            thDACstr += ", "+str(x)
        print "**CR-Loop** Setting Threshold DAC: %s" % thDACstr
        print

    def fix_chan(self,widget,entry):
        try:
            entry = entry.get_text()
            value = int(entry)
        except ValueError:
            print "Channel must be decimal integer"
            print
            return None                
        if (value < 1) or (64 < value):
            print "Channel out of range"
            print
            return None 

        self.CRLoop_chan = [value]
        print "**CR-Loop** Setting Channel: %s" % str(value)
        print

    def loop_chan(self,widget,entry):
        try:
            entry = entry.get_text()
            entry = entry.split(',')
            val = []
            for x in entry:
                x.strip()
                val += [int(x)]
        except ValueError:
            print "Channel must be decimal integer"
            print
            return None
        for x in val:               
            if (x < 1) or (64 < x):
                print "Channel out of range"
                print
                return None 
        self.CRLoop_chan = val
        CHstr = str(val[0])
        for x in val[1:]:
           CHstr += ", "+str(x)
        print "**CR-Loop** Setting Channels: %s" % CHstr
        print

    def loop_all_chan(self,widget):
        self.CRLoop_chan = range(1,65)
        CHstr = str(self.CRLoop_chan[0])
        for x in self.CRLoop_chan[1:]:
           CHstr += ", "+str(x)
        print "**CR-Loop** Setting Channels: %s" % CHstr
        print

    def fix_VMM(self,widget,entry):
        try:
            entry = entry.get_text()
            value = int(entry)
        except ValueError:
            print "VMM must be decimal integer"
            print
            return None                
        if (value < 1) or (8 < value):
            print "VMM out of range"
            print
            return None 

        self.CRLoop_VMM = [value]
        print "**CR-Loop** Setting VMMs: %s" % str(value)
        print

    def loop_VMM(self,widget,entry):
        try:
            entry = entry.get_text()
            entry = entry.split(',')
            val = []
            for x in entry:
                x.strip()
                val += [int(x)]
        except ValueError:
            print "VMM must be decimal integer"
            print
            return None
        for x in val:               
            if (x < 1) or (8 < x):
                print "VMM out of range"
                print
                return None 
        self.CRLoop_VMM = val
        VMMstr = str(val[0])
        for x in val[1:]:
           VMMstr += ", "+str(x)
        print "**CR-Loop** Setting VMMs: %s" % VMMstr
        print

    def loop_all_VMM(self,widget):
        val = range(1,9)
        self.CRLoop_VMM = val
        VMMstr = str(val[0])
        for x in val[1:]:
           VMMstr += ", "+str(x)
        print "**CR-Loop** Setting VMMs: %s" % VMMstr
        print 

    def fix_TACslope(self, widget):
        active = widget.get_active()
        if active < 0:
            return None

        self.CRLoop_TACslope = [active]
        print "**CR-Loop** Setting TAC Slope: %s" % str(active)
        print

    def loop_TACslope(self, widget):
        self.CRLoop_TACslope = range(0,4)
        print "**CR-Loop** Setting loop over TAC Slopes"
        print

    def fix_peakingtime(self, widget):
        active = widget.get_active()
        if active < 0:
            return None

        self.CRLoop_peakingtime = [active]
        print "**CR-Loop** Setting Peaking Time: %s" % str(active)
        print

    def loop_peakingtime(self, widget):
        self.CRLoop_peakingtime = range(0,4)
        print "**CR-Loop** Setting loop over Peaking Times"
        print

    def fix_delay(self, widget):
        active = widget.get_active()
        if active < 0:
            return None

        self.CRLoop_delay = [active]
        print "**CR-Loop** Setting Delay Time: %s" % str(active)
        print

    def loop_delay(self, widget):
        self.CRLoop_delay = range(0,5)
        print "**CR-Loop** Setting loop over Delay Times"
        print

    def activate_channel(self, iVMM, ich):
        if iVMM < 1 or iVMM > 8:
            return None
        if ich < 1 or ich > 64:
            return None
        self.VMM[iVMM-1].chan_list[ich-1].button_SM.set_active(False)
        self.VMM[iVMM-1].chan_list[ich-1].button_ST.set_active(True)
        print "**CR-Loop** Activating Channel %d in VMM %d" % (ich,iVMM)
        print
        
    def deactivate_channel(self, iVMM, ich):
        if iVMM < 1 or iVMM > 8:
            return None
        if ich < 1 or ich > 64:
            return None
        self.VMM[iVMM-1].chan_list[ich-1].button_SM.set_active(True)
        self.VMM[iVMM-1].chan_list[ich-1].button_ST.set_active(False)
        
    def run_CRLoop(self, widget):
        if widget.get_active() is False:
            return
        self.button_RunCR.set_sensitive(False)

        print "**CR-Loop** >>> RUNNING CALIBRATION ROUTINE <<<"
        print 
        
        # delete existing .dat file for new writing
        cmd = "rm -f %s" % self.CRLoop_Output_dat
        os.system(cmd)

        Loop_chan  = self.CRLoop_chan
        Loop_VMM   = self.CRLoop_VMM
        Loop_tpDAC = self.CRLoop_tpDAC
        Loop_thDAC = self.CRLoop_thDAC
        Loop_delay = self.CRLoop_delay
        Loop_TACslope = self.CRLoop_TACslope
        Loop_peakingtime = self.CRLoop_peakingtime

        # VMMs to be enabled
        self.Cur_VMM = Loop_VMM
        
        # initialize system for looping
        self.init_CRLoop()

        # loop over different parameter settings
        for tpDAC in Loop_tpDAC:
            for thDAC in Loop_thDAC:
                for delay in Loop_delay:
                    for TAC in Loop_TACslope:
                        for peak in Loop_peakingtime:
                            for chan in Loop_chan:
                                # set current values of parameters
                                self.Cur_chan = chan
                                self.Cur_tpDAC = tpDAC
                                self.Cur_thDAC = thDAC
                                self.Cur_delay = delay
                                self.Cur_TACslope = TAC
                                self.Cur_peaktime = peak

                                # turn of all channels for all VMMs
                                for ivmm in range(1,9):
                                    for ich in range(1,65):
                                        self.deactivate_channel(ivmm,ich)
                                
                                # VMM loop
                                for ivmm in Loop_VMM:
                                    # set channel
                                    self.activate_channel(ivmm,chan)

                                    # set TP DAC
                                    self.VMM[ivmm-1].entry_SDP_.set_text(str(tpDAC))
                                    self.VMM[ivmm-1].entry_SDP_.activate()

                                    # set Thresh DAC
                                    self.VMM[ivmm-1].entry_SDT.set_text(str(thDAC))
                                    self.VMM[ivmm-1].entry_SDT.activate()

                                    # set TAC slope
                                    self.VMM[ivmm-1].combo_STC.set_active(TAC)

                                    # set peak time
                                    self.VMM[ivmm-1].combo_ST.set_active(peak)
                                    
                                # set delay counts
                                self.combo_DC.set_active(delay)

                                # run configure and run DAQ for this configuration
                                self.run_CRLoop_point()

        # create .root file from .dat file (requires dat2root in path)
        cmd = "dat2root %s -o %s" % (self.CRLoop_Output_dat,self.CRLoop_Output_root)
        os.system(cmd) 

        print "**CR-Loop** >>> FINISHED CALIBRATION ROUTINE <<<"
        print 
                                
        self.button_RunCR.set_sensitive(True)
        self.button_RunCR.set_active(False)

    def init_CRLoop(self):
        print "**CR-Loop** Initializing system for calibration routine..."

        self.readout_runlength[24] = 0

        print "**CR-Loop**    ...turning on selected VMM readout"
        # turn off readout for all VMMs 
        for i in range(1,9):
            self.readout_runlength[15+i] = 0
        # Turn on readout for selected VMMs
        for i in self.Cur_VMM:
            self.readout_runlength[15+i] = 1

        print "**CR-Loop**    ...turning on selected VMM load"
        # turn off load/reset for all VMMs 
        for i in range(1,9):
            self.vmm_cfg_sel[i-1] = 0
        # turn on load/reset for selected VMMs
        for i in self.Cur_VMM:
            self.vmm_cfg_sel[i-1] = 1
            
        self.load_IDs()

        # load number of pulses
        self.entry_pulses.set_text(str(self.CRLoop_Npulse))
        self.entry_pulses.activate()

        # load acquisition reset and hold counts
        self.entry_acq_reset_count.activate()
        self.entry_acq_reset_hold.activate()
        
        VMMstr = str(self.Cur_VMM[0])
        for x in self.Cur_VMM[1:]:
           VMMstr += ", "+str(x)
        print "**CR-Loop** ...Enabled VMMs for readout/reset/load: %s" % VMMstr
        print 
    
    def run_CRLoop_point(self):
        print "**CR-Loop** Initializing calibration point:"
        print "**CR-Loop**    Channel = %d" % self.Cur_chan
        print "**CR-Loop**    Test Pulse DAC = %d" % self.Cur_tpDAC
        print "**CR-Loop**    Threshold DAC = %d" % self.Cur_thDAC
        print "**CR-Loop**    Delay Counts = %d st" % self.Cur_delay
        print "**CR-Loop**    TAC Slope = %d" % self.Cur_TACslope
        print "**CR-Loop**    Peak Time = %d" % self.Cur_peaktime
        
        # write VMM configuration
        print "**CR-Loop** ...Writing VMM config"
        self.write_VMM_CRLoop()

        # global reset
        print "**CR-Loop** ...Gobal Reset"
        self.button_resetVMM.clicked()
        
        # system reset
        print "**CR-Loop** ...System Reset"
        self.button_SystemInit.clicked()
        
        # VMM load
        print "**CR-Loop** ...Loading VMMs"
        self.button_SystemLoad.clicked()

        # internal trigger
        self.readout_runlength[24] = 1
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        message = "w 0x44A100F4" 
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        sleep(1)

        # Start DAQ
        print "**CR-Loop** ...Starting data-taking"
        self.start_daq_CRLoop()
             
        self.readout_runlength[24] = 0
        tempInt = 0
        for bit in range(32):
            tempInt += int(self.readout_runlength[bit])*pow(2, bit)
        message = "w 0x44A100F4" 
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)   
        sleep(1)

        print "**CR-Loop** Calibration Point Completed"
        print 

    def write_VMM_CRLoop(self):
        # get first enabled VMM as "current"
        # current_vmm = int(self.notebook.get_current_page())
        current_vmm = self.Cur_VMM[0]-1

        # command strings must be <= 100 chars
        # due to bram limitations on artix7
        self.VMM[current_vmm].entry_SDP_.grab_focus()
        self.VMM[current_vmm].entry_SDT.grab_focus()
        self.button_write.grab_focus()
        #active = self.combo_vmm2_id.get_active()
        #configAddr = self.vmmBaseConfigAddr[0]
        reg = self.VMM[current_vmm].get_channel_val()
        reglist = list(self.VMM[current_vmm].reg.flatten())
        globalreglist = list(self.VMM[current_vmm].globalreg.flatten())
        fullreg = reglist[::-1] + globalreglist[::-1] 
        chars = []
        MESSAGE = ""
        n=0
        m=0
        w=0
        reglist = reglist[::-1]
        for b in range(51):
            self.byteint[b] = 0
            bytelist = fullreg[b*32:(b+1)*32]
            n = n+1
            dummyReg = bytelist[::-1]
            #string = "A" + str(b)
            for bit in range(32):
                self.byteint[b] += int(dummyReg[bit])*pow(2, 31-bit)             
        StartMsg =  "W" +' 0x{0:08X}'.format(self.vmmBaseConfigAddr[0]) #.decode('hex')      
        for c in range(0,51):
            string = "A" + str(c+1)
            myVal = int(self.byteint[c])
            MESSAGE = MESSAGE + ' 0x{0:X}'.format(myVal)
            if (c+1)%6 == 0:
                w = w + 1
                MSGsend = StartMsg + MESSAGE + '\0' + '\n'
                MESSAGE = ""
                m = m + 24
                StartMsg = "W" +' 0x{0:08X}'.format(self.vmmBaseConfigAddr[w])
                self.udp.udp_client(MSGsend,self.UDP_IP,self.UDP_PORT)
                sleep(1)                                                                                                                                
        MSGsend = StartMsg + MESSAGE + '\0' + '\n'
        self.udp.udp_client(MSGsend,self.UDP_IP,self.UDP_PORT)
        sleep(1)
        print "\nWrote to Config Registers\n"
        
        self.load_IDs()
        
        return

    def start_daq_CRLoop(self):
        # start the DAQ readout
        tempInt = 0
        self.control[2] = 1
        #byteint = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
            #byteword = int(byteint) 
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        sleep(1)

        print "**CR-Loop** ...Starting DAQ"
        self.daq_readOut_CRLoop()
        print "**CR-Loop** ...DAQ finished"             
        sleep(1)

        tempInt = 0
        self.control[2] = 0
        #byteint = 0
        for bit in range(32):
            tempInt += int(self.control[bit])*pow(2, bit)
            #byteword = int(byteint) 
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(tempInt)  
        message = message + '\0' + '\n'
        print message
        self.udp.udp_client(message,self.UDP_IP,self.UDP_PORT)
        sleep(1)
        
    def daq_readOut_CRLoop(self):
        while True:
            fifoCnt = 0
            r=10
            #while ( ( fifoCnt == 0) and ( self.terminate == 0)):
            while ( ( fifoCnt == 0) and ( r != 0)):
                #if( self.terminate == 1):
                #    return
                r = r -1
                msgFifoCnt = "r 0x44A10014 1 \0 \n" # read word count of data fifo
                FifoCntData = self.udp.udp_client(msgFifoCnt,self.UDP_IP,self.UDP_PORT)
                sleep(1)
                print FifoCntData
                FifoCntStr = string.split(FifoCntData,' ') # split the string to a list
                print FifoCntStr
                fifoCnt = int(FifoCntStr[2],16) # We now have the number of words in the FIFO
            print "FIFOCNT ", fifoCnt
            if fifoCnt % 2 == 0:
                fcnt = fifoCnt
            else:
                print "/n lst one count"
                fcnt = (fifoCnt - 1)
            cycles = fcnt / 10  # reading 10 32-bit data words
            remainder = fcnt % 10
            if fcnt <= 0:
                break
            for i in range(1+cycles)[::-1]:  # reverses the order of the count
                #if( self.terminate == 1):
                #    return
                if i == 0:                             # 0 has less than ten words
                    m = 2 + remainder
                    reads = remainder  # less that 10
                else:
                    m = 12 # total words in packet payload
                    reads = 10
                msgFifoData = "k 0x44A10010 " + str(reads) + "\n" # read 10 words from fifo
                fifoData = self.udp.udp_client(msgFifoData,self.UDP_IP,self.UDP_PORT)
                n = 2
                while n < m:
                    #if( self.terminate == 1):
                    #    return
                    dataList = fifoData.split()
                    fifo32 = int(dataList[n],16)
                    if fifo32 > 0:
                        fifo32 = fifo32 >> 2     # get rid of first 2 bits (threshold)
                        
                        CHword = (fifo32 & 63) + 1 # get channel number as on GUI

                        fifo32 = fifo32 >> 6     # get rid of address
                        PDO    = fifo32 &  1023 # get amplitude

                        fifo32 = fifo32 >> 10
                        TDO = fifo32 & 255
                        
                        fifo32 = fifo32 >> 8  # we will later check for vmm number
                        VMMword = (fifo32 & 7) + 1 # get vmm number

                        BCID = 0
                        if (n+1) < 12:
                            fifohigh = int(dataList[n+1],16)
                            print fifohigh
                            BCIDgray = int(fifohigh & 4095) # next change from gray code to int
                            BCid2 = binstr.int_to_b(BCIDgray,16)
                            myBCid = binstr.b_gray_to_bin(BCid2)
                            BCID = binstr.b_to_int(myBCid)
                            fifohigh = fifohigh >> 12  # later we will get the turn number 	 

                        output_string  = "VMM=%s" % str(VMMword)
                        output_string += " CHword=%s" % str(CHword)
                        output_string += " CHpulse=%s" % str(self.Cur_chan)
                        output_string += " PDO=%s" % str(PDO)
                        output_string += " TDO=%s" % str(TDO)
                        output_string += " BCID=%s" % str(BCID)
                        output_string += " TPDAC=%s" % str(self.Cur_tpDAC)
                        output_string += " THDAC=%s" % str(self.Cur_thDAC)
                        output_string += " Delay=%s" % str(self.Cur_delay)
                        output_string += " TACslope=%s" % str(self.Cur_TACslope)
                        output_string += " PeakTime=%s" % str(self.Cur_peaktime)
                        
                        print dataList[n] + " "+ dataList[n+1] + ", " + output_string
                    
                        with open('mmfe8_CalibRoutine.dat', 'a') as myfile:
                                myfile.write(output_string+'\n')
                        n=n+2
                    else:
                        print "out of order or no data ="# + str(hex(dataList[n]))
                        #n= n+1       
                        n=n+2 #paolo
        
    #######################################################################
    #
    #
    #                              __init__    <<==========================
    #
    #
    #######################################################################

    def __init__(self):
        print "loading MMFE8 Calibration Routine GUI..."
        print 
        self.tv = gtk.TextView()
        self.tv.set_editable(False)
        self.tv.set_wrap_mode(gtk.WRAP_WORD)
        self.buffer = self.tv.get_buffer()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(1000,700) ###set_size_request(1440,900)
        self.window.set_resizable(True)

        self.window.set_title("MMFE8 vmm2 Calibration Routine GUI (v1.0.0)")
        self.window.set_border_width(0)
        
        self.notebook = gtk.Notebook()
        self.notebook.set_size_request(-1,0)
        self.notebook.set_tab_pos(gtk.POS_TOP)

        # different tabs are defined here
        self.tab_label_1 = gtk.Label("VMM 1")
        self.tab_label_2 = gtk.Label("VMM 2")
        self.tab_label_3 = gtk.Label("VMM 3")
        self.tab_label_4 = gtk.Label("VMM 4")
        self.tab_label_5 = gtk.Label("VMM 5")
        self.tab_label_6 = gtk.Label("VMM 6")
        self.tab_label_7 = gtk.Label("VMM 7")
        self.tab_label_8 = gtk.Label("VMM 8")
        self.tab_label_9 = gtk.Label("User Defined")
        #self.tab_label_10 = gtk.Label("VMM Output")
        #print "loading Registers..."
        self.VMM = []
        for i in range(8):
            self.VMM.append(vmm())
        self.udp = udp_stuff()
        # ipAddr will be obtained from an xml file in the future
        self.ipAddr = ["127.0.0.1","192.168.0.130","192.168.0.101","192.168.0.102","192.168.0.103","192.168.0.104","192.168.0.105","192.168.0.106",
              "192.168.0.107","192.168.0.108","192.168.0.109","192.168.0.110","192.168.0.111","192.168.0.112","192.168.0.167"]
        # each is the starting address for the 51 config regs for each vmm 
        self.mmfeID = 0
        self.vmmBaseConfigAddr = [0x44A10020,0x44A10038,0x44A10050,0x44A10068,
                         0x44A10080,0x44A10098,0x44A100B0,0x44A100C8,0x44A100E0]

        #self.vmmGlobalReset = np.zeros((32), dtype=int)                #0x44A100EC  #vmm_global_reset          #reset & vmm_gbl_rst_i & vmm_cfg_en_vec( 7 downto 0)
        #self.vmm_cfg_sel_reg = np.zeros((32), dtype=int)               #0x44A100EC  #vmm_cfg_sel               #vmm_2display_i(16 downto 12) & mmfeID(11 downto 8) & vmm_readout_i(7 downto 0)
        self.vmm_cfg_sel = np.zeros((32), dtype=int)                	#0x44A100EC  #vmm_cfg_sel               #vmm_2display_i(16 downto 12) & mmfeID(11 downto 8) & vmm_readout_i(7 downto 0)
        self.cktp_period_dutycycle = np.zeros((32), dtype=int)          #0x44A100F0  #cktp_period_dutycycle     #clk_tp_period_cnt(15 downto 0) & clk_tp_dutycycle_cnt(15 downto 0)
        #self.start_mmfe8 = np.zeros((32), dtype=int)
        self.readout_runlength = np.zeros((32), dtype=int)         		#0x44A100F4  #ReadOut_RunLength         #ext_trigger_in_sel(26)&axi_data_to_use(25)&int_trig(24)&vmm_readout_i(23 downto 16)&pulses(15 downto 0)
        self.acq_count_runlength = np.zeros((32), dtype=int)         	#0x44A10120  #counts_to_acq_reset       #counts_to_acq_reset( 31 downto 0)
        self.acq_hold_runlength = np.zeros((32), dtype=int)         	#0x44A10120  #counts_to_acq_hold        #counts_to_hold_acq_reset( 31 downto 0)
        self.xadc = np.zeros((32), dtype=int)                           #0x44A100F8  #xadc                      #read
        self.admux = np.zeros((32), dtype=int)                          #0x44A100F8  #admux                     #write
        self.control = np.zeros((32), dtype=int)                 		#0x44A100FC  #was vmm_global_reset      #reset & vmm_gbl_rst_i & vmm_cfg_en_vec( 7 downto 0)
        #self.system_init = np.zeros((32), dtype=int)                   #0x44A10100  #axi_reg_60( 0)            #original reset
        #self.userRegs = userRegs()                                     #0x44A10104,08,0C,00,14                 #user_reg_1 #user_reg_2 #user_reg_3 #user_reg_4         
        self.userRegs = userRegs()                                      #0x44A10104,08,0C,00,14                 #user_reg_1 #user_reg_2 #user_reg_3 #user_reg_4 #user_reg_5
        self.ds2411_low = np.zeros((32), dtype=int)                     #0x44A10118  #DS411_low                 #Low
        self.ds2411_high = np.zeros((32), dtype=int)                    #0x44A1011C  #DS411_high                #High
        self.counts_to_acq_reset = np.zeros((32), dtype=int)            #0x44A10120  #counts_to_acq_reset       #0 to FFFF_FFFF #0=Not Used
        self.counts_to_acq_hold = np.zeros((32), dtype=int)            #0x44A10120  #counts_to_hold_acq_reset       #0 to FFFF_FFFF #0=Not Used
        self.terminate = 0                    
        self.UDP_PORT = 50001
        self.UDP_IP = ""
        self.chnlReg = np.zeros((51), dtype=int)
        self.byteint = np.zeros((51), dtype=np.uint32)
        self.byteword = np.zeros((32), dtype=int)

        ####################################################
        ##                    GUI   
        ##                   GLOBAL  
        ##                   BUTTONS 
        ####################################################
        #print "loading buttons..."

        self.button_exit = gtk.Button("EXIT")
        self.button_exit.set_size_request(-1,-1)
        self.button_exit.connect("clicked",self.destroy)

        self.button_start = gtk.Button("Start")
        self.button_start.child.set_justify(gtk.JUSTIFY_CENTER)
        self.label_start = self.button_start.get_children()[0]
        self.button_start.set_size_request(-1,-1)
        self.button_start.connect("clicked",self.start)
        #self.button_start.set_sensitive(False)


        self.label_pulses = gtk.Label("pulses")
        self.label_pulses.set_markup('<span color="blue"><b>Pulses:</b></span>')
        self.label_pulses.set_justify(gtk.JUSTIFY_LEFT)
        self.entry_pulses = gtk.Entry(max=3)
        self.entry_pulses.set_text("0")
        self.entry_pulses.set_editable(True)
        self.entry_pulses.connect("focus-out-event", self.set_pulses)
        self.entry_pulses.connect("activate", self.set_pulses, self.entry_pulses)

        #self.combo_pulses.connect("changed",self.set_pulses)
        #self.combo_pulses.set_active(0)
        self.box_pulses = gtk.HBox()
        self.box_pulses.pack_start(self.label_pulses, expand=True)
        self.box_pulses.pack_start(self.entry_pulses, expand=False)

        self.label_pulses2 = gtk.Label("999 == Continuous")
        self.label_pulses2.set_markup('<span color="purple"><b>999 == Continuous</b></span>')
        self.label_pulses2.set_justify(gtk.JUSTIFY_CENTER)

        self.label_Var_DC = gtk.Label("Delay Counts")
        self.label_Var_DC.set_markup('<span color="blue"><b> Delay Counts   </b></span>')
        self.combo_DC = gtk.combo_box_new_text()
        self.combo_DC.connect("changed",self.glob_DC_value)
        self.combo_DC.append_text("0")
        self.combo_DC.append_text("1")
        self.combo_DC.append_text("2")
        self.combo_DC.append_text("3")
        self.combo_DC.append_text("4")
        #self.combo_DC.set_active(0)
        self.label_DC = gtk.Label(" st")
        self.box_DC = gtk.HBox()
        self.box_DC.pack_start(self.label_Var_DC, expand=False)
        self.box_DC.pack_start(self.combo_DC, expand=False)
        self.box_DC.pack_start(self.label_DC, expand=False)

        self.label_acq_reset_count = gtk.Label("acq_rst_count")
        self.label_acq_reset_count.set_markup('<span color="Navy"><b>      acq_reset_count:    </b></span>')
        self.label_acq_reset_count.set_justify(gtk.JUSTIFY_LEFT)
        self.entry_acq_reset_count = gtk.Entry(max=8)
        self.entry_acq_reset_count.set_width_chars(8)
        self.entry_acq_reset_count.set_text("0")
        self.entry_acq_reset_count.set_editable(True)
        self.entry_acq_reset_count.connect("focus-out-event", self.set_acq_reset_count)
        self.entry_acq_reset_count.connect("activate", self.set_acq_reset_count, self.entry_acq_reset_count)
        self.label_acq_reset_count2 = gtk.Label("0 == None")
        self.label_acq_reset_count2.set_markup('<span color="DarkGreen"><b> (0 == No Reset)</b></span>')
        self.label_acq_reset_count2.set_justify(gtk.JUSTIFY_CENTER)
        self.counts_to_acq_reset = np.zeros((32), dtype=int)                    #0x44A1010C  #DS411_high                #High
        # set default
        self.entry_acq_reset_count.set_text("50")
        # self.entry_acq_reset_count.activate()

        self.box_acq_reset_count = gtk.HBox()
        self.box_acq_reset_count.pack_start(self.label_acq_reset_count, expand=False)
        self.box_acq_reset_count.pack_start(self.entry_acq_reset_count, expand=False)
        self.box_acq_reset_count.pack_start(self.label_acq_reset_count2, expand=False)
        
        self.label_acq_reset_hold = gtk.Label("acq_rst_hold")
        self.label_acq_reset_hold.set_markup('<span color="Navy"><b>      acq_reset_hold:      </b></span>')
        self.label_acq_reset_hold.set_justify(gtk.JUSTIFY_LEFT)
        self.entry_acq_reset_hold = gtk.Entry(max=8)
        self.entry_acq_reset_hold.set_width_chars(8)
        self.entry_acq_reset_hold.set_text("0")
        self.entry_acq_reset_hold.set_editable(True)
        self.entry_acq_reset_hold.connect("focus-out-event", self.set_acq_reset_hold)
        self.entry_acq_reset_hold.connect("activate", self.set_acq_reset_hold, self.entry_acq_reset_hold)
        self.label_acq_reset_hold2 = gtk.Label("0 == None")
        self.label_acq_reset_hold2.set_markup('<span color="DarkGreen"><b> (0 == No Hold)</b></span>')
        self.label_acq_reset_hold2.set_justify(gtk.JUSTIFY_CENTER)
        self.counts_to_acq_hold = np.zeros((32), dtype=int)                    #0x44A1010C  #DS411_high                #High
        # set default
        self.entry_acq_reset_hold.set_text("40")
        # self.entry_acq_reset_hold.activate()
        
        self.box_acq_reset_hold = gtk.HBox()
        self.box_acq_reset_hold.pack_start(self.label_acq_reset_hold, expand=False)
        self.box_acq_reset_hold.pack_start(self.entry_acq_reset_hold, expand=False)
        self.box_acq_reset_hold.pack_start(self.label_acq_reset_hold2, expand=False)


        self.button_resetVMM = gtk.Button("VMM Global Reset")
        self.button_resetVMM.set_size_request(-1,-1)
        self.button_resetVMM.connect("clicked",self.reset_global)
        #self.button_resetVMM.set_sensitive(False)

        self.button_SystemInit = gtk.Button("System Reset")
        self.button_SystemInit.set_size_request(-1,-1)
        self.button_SystemInit.connect("clicked",self.system_init) ###<<<======

        self.button_SystemLoad = gtk.Button("VMM Load")
        self.button_SystemLoad.set_size_request(-1,-1)
        self.button_SystemLoad.connect("clicked",self.system_load)

        self.label_vmmGlobal_Reset = gtk.Label("vmm2")
        self.label_vmmGlobal_Reset.set_markup('<span color="blue"><b>VMMs to Reset / Load</b></span>')
        self.label_vmmGlobal_Reset.set_justify(gtk.JUSTIFY_CENTER)

        self.check_button_vmm1_reset = gtk.CheckButton()
        self.check_button_vmm1_reset.connect("toggled", self.Vmm1Reset_callback)
        self.check_button_vmm2_reset = gtk.CheckButton()
        self.check_button_vmm2_reset.connect("toggled", self.Vmm2Reset_callback)
        self.check_button_vmm3_reset = gtk.CheckButton()
        self.check_button_vmm3_reset.connect("toggled", self.Vmm3Reset_callback)
        self.check_button_vmm4_reset = gtk.CheckButton()
        self.check_button_vmm4_reset.connect("toggled", self.Vmm4Reset_callback)
        self.check_button_vmm5_reset = gtk.CheckButton()
        self.check_button_vmm5_reset.connect("toggled", self.Vmm5Reset_callback)
        self.check_button_vmm6_reset = gtk.CheckButton()
        self.check_button_vmm6_reset.connect("toggled", self.Vmm6Reset_callback)
        self.check_button_vmm7_reset = gtk.CheckButton()
        self.check_button_vmm7_reset.connect("toggled", self.Vmm7Reset_callback)
        self.check_button_vmm8_reset = gtk.CheckButton()        
        self.check_button_vmm8_reset.connect("toggled", self.Vmm8Reset_callback)
        self.label_vmmReset_1 = gtk.Label("1")
        self.label_vmmReset_2 = gtk.Label("2")
        self.label_vmmReset_3 = gtk.Label("3")
        self.label_vmmReset_4 = gtk.Label("4")
        self.label_vmmReset_5 = gtk.Label("5")
        self.label_vmmReset_6 = gtk.Label("6")
        self.label_vmmReset_7 = gtk.Label("7")
        self.label_vmmReset_8 = gtk.Label("8")

        self.vmmReset_table1 = gtk.Table(rows=2, columns=8, homogeneous=True)
        self.vmmReset_table1.attach(self.label_vmmReset_1, left_attach=0, right_attach=1, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm1_reset, left_attach=0, right_attach=1, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_2, left_attach=1, right_attach=2, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm2_reset, left_attach=1, right_attach=2, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_3, left_attach=2, right_attach=3, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm3_reset, left_attach=2, right_attach=3, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_4, left_attach=3, right_attach=4, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm4_reset, left_attach=3, right_attach=4, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_5, left_attach=4, right_attach=5, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm5_reset, left_attach=4, right_attach=5, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_6, left_attach=5, right_attach=6, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm6_reset, left_attach=5, right_attach=6, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_7, left_attach=6, right_attach=7, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm7_reset, left_attach=6, right_attach=7, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.label_vmmReset_8, left_attach=7, right_attach=8, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReset_table1.attach(self.check_button_vmm8_reset, left_attach=7, right_attach=8, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)


        self.label_But_Space1 = gtk.Label(" ")
        self.label_But_Space2 = gtk.Label(" ")        
        self.label_But_Space3 = gtk.Label(" ")
        self.label_But_Space4 = gtk.Label(" ")
        self.label_But_Space5 = gtk.Label(" ") 
        self.label_But_Space8 = gtk.Label(" ")
        self.label_But_Space9 = gtk.Label(" ")
        self.label_But_Space10 = gtk.Label(" ")      


        self.label_vmmReadoutMask = gtk.Label("vmm2")
        self.label_vmmReadoutMask.set_markup('<span color="blue"><b>VMM Readout Enable</b></span>')
        self.label_vmmReadoutMask.set_justify(gtk.JUSTIFY_CENTER)

        self.check_button_vmm1_readout = gtk.CheckButton()
        self.check_button_vmm1_readout.connect("toggled", self.readoutVmm1_callback)
        self.check_button_vmm2_readout = gtk.CheckButton()
        self.check_button_vmm2_readout.connect("toggled", self.readoutVmm2_callback)
        self.check_button_vmm3_readout = gtk.CheckButton()
        self.check_button_vmm3_readout.connect("toggled", self.readoutVmm3_callback)
        self.check_button_vmm4_readout = gtk.CheckButton()
        self.check_button_vmm4_readout.connect("toggled", self.readoutVmm4_callback)
        self.check_button_vmm5_readout = gtk.CheckButton()
        self.check_button_vmm5_readout.connect("toggled", self.readoutVmm5_callback)
        self.check_button_vmm6_readout = gtk.CheckButton()
        self.check_button_vmm6_readout.connect("toggled", self.readoutVmm6_callback)
        self.check_button_vmm7_readout = gtk.CheckButton()
        self.check_button_vmm7_readout.connect("toggled", self.readoutVmm7_callback)
        self.check_button_vmm8_readout = gtk.CheckButton()
        self.check_button_vmm8_readout.connect("toggled", self.readoutVmm8_callback)        
        self.label_vmmReadout_1 = gtk.Label("1")
        self.label_vmmReadout_2 = gtk.Label("2")
        self.label_vmmReadout_3 = gtk.Label("3")
        self.label_vmmReadout_4 = gtk.Label("4")
        self.label_vmmReadout_5 = gtk.Label("5")
        self.label_vmmReadout_6 = gtk.Label("6")
        self.label_vmmReadout_7 = gtk.Label("7")
        self.label_vmmReadout_8 = gtk.Label("8")

        self.vmmReadout_table1 = gtk.Table(rows=2, columns=8, homogeneous=True)
        self.vmmReadout_table1.attach(self.label_vmmReadout_1, left_attach=0, right_attach=1, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm1_readout, left_attach=0, right_attach=1, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_2, left_attach=1, right_attach=2, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm2_readout, left_attach=1, right_attach=2, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_3, left_attach=2, right_attach=3, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm3_readout, left_attach=2, right_attach=3, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_4, left_attach=3, right_attach=4, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm4_readout, left_attach=3, right_attach=4, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_5, left_attach=4, right_attach=5, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm5_readout, left_attach=4, right_attach=5, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_6, left_attach=5, right_attach=6, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm6_readout, left_attach=5, right_attach=6, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_7, left_attach=6, right_attach=7, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm7_readout, left_attach=6, right_attach=7, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.label_vmmReadout_8, left_attach=7, right_attach=8, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.vmmReadout_table1.attach(self.check_button_vmm8_readout, left_attach=7, right_attach=8, top_attach=1, bottom_attach=2, xpadding=0, ypadding=0)



        self.button_write = gtk.Button("Write to Config Buffer")
        self.button_write.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_write.set_size_request(-1,-1)        
        self.button_write.connect("clicked",self.write_vmmConfigRegisters)
        
        self.button_read_reg = gtk.Button("READ Config\nRegisters")
        self.button_read_reg.set_sensitive(False)
        self.button_read_reg.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_read_reg.set_size_request(-1,-1)
        self.button_read_reg.connect("clicked",self.read_reg)
        
        self.label_internal_trigger =  gtk.Label("Internal Trigger:    ")
        self.label_internal_trigger.set_markup('<span color="blue"><b>Internal Trigger:    </b></span>')
        self.button_internal_trigger = gtk.ToggleButton("OFF")
        self.button_internal_trigger.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_internal_trigger.connect("clicked",self.internal_trigger)
        self.button_internal_trigger.set_size_request(-1,-1)
        
        self.label_external_trigger =  gtk.Label("External Trigger:    ")
        self.label_external_trigger.set_markup('<span color="blue"><b>External Trigger:    </b></span>')
        self.button_external_trigger = gtk.ToggleButton("OFF")
        self.button_external_trigger.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_external_trigger.connect("clicked",self.external_trigger)
        self.button_external_trigger.set_size_request(-1,-1)
        
        self.label_leaky_readout =  gtk.Label("Leaky Readout Data:    ")
        self.label_leaky_readout.set_markup('<span color="blue"><b>Leaky Readout:    </b></span>')
        self.button_leaky_readout = gtk.ToggleButton("OFF")
        self.button_leaky_readout.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_leaky_readout.connect("clicked",self.leaky_readout)
        self.button_leaky_readout.set_size_request(-1,-1)
        
        self.button_read_XADC = gtk.Button("Read XADC")
        self.button_read_XADC.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_read_XADC.connect("clicked",self.read_xadc)
        self.button_read_XADC.set_size_request(-1,-1)
        
        self.button_print_config = gtk.Button("Print Config Load")
        self.button_print_config.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_print_config.set_size_request(-1,-1)
        self.button_print_config.connect("clicked",self.print_config)

        # Choose Board
        #print "Choosing Board..."

        self.label_mmfe8_id = gtk.Label("mmfe8")
        self.label_mmfe8_id.set_markup('<span color="Navy"><b>mmfe\nID</b></span>')
        self.label_mmfe8_id.set_justify(gtk.JUSTIFY_CENTER)
        self.entry_mmfeID = gtk.Entry(max=3)
        self.entry_mmfeID.set_width_chars(6)
        self.entry_mmfeID.set_text(str(self.mmfeID))
        self.entry_mmfeID.set_editable(False)
        
        self.label_IP = gtk.Label("IP ADDRESS")
        self.label_IP.set_markup('<span color="Navy"><b>MMFE8\nIP ADDRESS</b></span>')
        self.label_IP.set_justify(gtk.JUSTIFY_CENTER)
        self.combo_IP = gtk.combo_box_new_text()
        for i in range (len(self.ipAddr)):
            self.combo_IP.append_text(self.ipAddr[i]) 

        self.combo_IP.set_active(0)
        self.combo_IP.connect("changed",self.set_board_ip, self.entry_mmfeID)
        self.combo_IP.set_size_request(200,-1)
        self.combo_IP.set_active(3)

        self.combo_display = gtk.combo_box_new_text()
        for i in range(32):
            self.combo_display.append_text(str(hex(i)))
        self.combo_display.connect("changed",self.set_display_no_enet)
        self.combo_display.set_active(0)


        #self.combo_vmm2_id = gtk.combo_box_new_text()
        #for i in range(256):
        #    self.combo_vmm2_id.append_text(str(hex(i)))

        #self.combo_vmm2_id.append_text("ALL")
        #self.combo_vmm2_id.set_active(0)
        #self.combo_vmm2_id.connect("changed",self.set_vmm_cfg_num)

        self.button_setIDs = gtk.Button("Set IDs")
        self.button_setIDs.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_setIDs.set_size_request(-1,-1)        
        self.button_setIDs.connect("clicked",self.set_IDs)
        
        self.label_mmfe8_id = gtk.Label("mmfe8")
        self.label_mmfe8_id.set_markup('<span color="Navy"><b>                     MMFE8 ID   </b></span>')
        self.label_mmfe8_id.set_justify(gtk.JUSTIFY_CENTER)
        self.label_Space20 = gtk.Label("   ")
        self.box_mmfeID = gtk.HBox()
        self.box_mmfeID.pack_start(self.label_mmfe8_id,expand=False)
        self.box_mmfeID.pack_start(self.entry_mmfeID,expand=False)

        self.label_display_id = gtk.Label("vmm2")
        self.label_display_id.set_markup('<span color="blue"><b>Scope  </b></span>')
        self.label_display_id.set_justify(gtk.JUSTIFY_CENTER)

        self.label_Space21 = gtk.Label("    ")
        self.box_labelID = gtk.HBox()
        self.box_labelID.pack_start(self.label_Space20,expand=True) #
        #self.box_labelID.pack_start(self.label_Space21,expand=False)
        #self.box_labelID.pack_start(self.label_vmm2_id,expand=False)
        #self.box_labelID.pack_start(self.qs_table,expand=False)

        self.label_Space22 = gtk.Label("  ") 

        self.box_ResetID = gtk.VBox()
        self.box_ResetID.pack_start(self.label_vmmGlobal_Reset,expand=False)
        self.box_ResetID.pack_start(self.vmmReset_table1,expand=False)
        self.box_ResetID.pack_start(self.button_resetVMM,expand=False)
        #self.box_ResetID.pack_start(self.label_Space22,expand=False)   

        self.box_ReadoutMask = gtk.VBox()
        self.box_ReadoutMask.pack_start(self.label_vmmReadoutMask,expand=False)
        self.box_ReadoutMask.pack_start(self.vmmReadout_table1,expand=False)
        #self.box_ResetID.pack_start(self.button_resetVMM,expand=False)
        #self.box_ResetID.pack_start(self.label_Space22,expand=False)   

        self.box_vmmID = gtk.HBox()
        self.box_vmmID.pack_start(self.button_setIDs,expand=False) #
        self.box_vmmID.pack_start(self.label_Space21,expand=True)
        self.box_vmmID.pack_start(self.label_display_id,expand=False)
        self.box_vmmID.pack_start(self.combo_display,expand=False)

        self.box_internal_trigger = gtk.HBox()
        self.box_internal_trigger.pack_start(self.label_internal_trigger,expand=False) #
        self.box_internal_trigger.pack_start(self.button_internal_trigger,expand=True)

        self.box_external_trigger = gtk.HBox()
        self.box_external_trigger.pack_start(self.label_external_trigger,expand=False) #
        self.box_external_trigger.pack_start(self.button_external_trigger,expand=True)

        self.box_leaky_readout = gtk.HBox()
        self.box_leaky_readout.pack_start(self.label_leaky_readout,expand=False) #
        self.box_leaky_readout.pack_start(self.button_leaky_readout,expand=True)

        ################################################################################################
        ################################################################################################
        ################################################################################################
        # CR - Calibration loop buttons
        ################################################################################################
        ################################################################################################
        ################################################################################################
        self.frame_Loop = gtk.Frame()
        self.frame_Loop.set_shadow_type(gtk.SHADOW_OUT)
        
        map = self.frame_Loop.get_colormap() 
        bkg_color = map.alloc_color("firebrick4")
        txt_color = map.alloc_color("white")
        wait_color = map.alloc_color("honeydew")
        run_color  = map.alloc_color("darkgreen")

        style_frame = self.frame_Loop.get_style().copy()
        style_frame.bg[gtk.STATE_NORMAL]   = bkg_color
        style_frame.base[gtk.STATE_NORMAL] = bkg_color
        style_frame.fg[gtk.STATE_NORMAL]   = txt_color
        style_frame.text[gtk.STATE_NORMAL] = txt_color
        style_run = style_frame.copy()
        style_run.bg[gtk.STATE_NORMAL]   = wait_color
        style_run.base[gtk.STATE_NORMAL] = wait_color
        style_run.fg[gtk.STATE_NORMAL]   = run_color
        style_run.text[gtk.STATE_NORMAL] = run_color
        style_run.bg[gtk.STATE_ACTIVE]   = run_color
        style_run.base[gtk.STATE_ACTIVE] = run_color
        style_run.fg[gtk.STATE_ACTIVE]   = txt_color
        style_run.text[gtk.STATE_ACTIVE] = txt_color
        style_run.bg[gtk.STATE_INSENSITIVE]   = run_color
        style_run.base[gtk.STATE_INSENSITIVE] = run_color
        style_run.fg[gtk.STATE_INSENSITIVE]   = txt_color
        style_run.text[gtk.STATE_INSENSITIVE] = txt_color
        
        self.frame_Loop.set_style(style_frame)
        
        self.buttons_Loop = gtk.VBox()
        self.buttons_Loop.set_spacing(5)
        self.buttons_Loop.set_border_width(5)
        self.buttons_Loop.set_size_request(-1,-1)
        self.box_buttons_Loop = gtk.EventBox()
        self.box_buttons_Loop.add(self.buttons_Loop)
        self.box_buttons_Loop.set_style(style_frame)
        self.frame_Loop.add(self.box_buttons_Loop)

        self.label_Loop = gtk.Label("CR")
        self.label_Loop.set_markup('<span color="white" size="x-large"><b>Calibration Routine Settings</b></span>')
        self.label_Loop.set_justify(gtk.JUSTIFY_CENTER)
        self.label_Loop.set_style(style_frame)
        self.buttons_Loop.pack_start(self.label_Loop,expand=True)
        
        self.button_RunCR = gtk.ToggleButton(">>>>>><<<<<<        Run Routine      >>>>>><<<<<<")
        self.button_RunCR.connect("clicked", self.run_CRLoop)
        self.button_RunCR.set_style(style_run)
        self.button_RunCR.get_child().set_style(style_run)
        self.box_RunCR = gtk.EventBox()
        self.box_RunCR.set_style(style_frame)
        self.box_RunCR.add(self.button_RunCR)
        self.buttons_Loop.pack_start(self.box_RunCR,expand=True)

        # set output .dat filename
        self.label_outputdat = gtk.Label("outputdat")
        self.label_outputdat.set_markup('<span color="white"><b>    Output .dat filename     </b></span>')
        self.label_outputdat.set_justify(gtk.JUSTIFY_LEFT)
        self.button_outputdat = gtk.Entry()
        self.button_outputdat.set_width_chars(21)
        self.button_outputdat.set_text("mmfe8_CalibRoutine.dat")
        self.button_outputdat.set_editable(True)
        #self.button_outputdat.connect("focus-out-event", self.set_outputdat_LoopCR)
        self.button_outputdat.connect("activate", self.set_outputdat_LoopCR, self.button_outputdat)
        self.button_outputdat.activate()
        self.box_button_outputdat = gtk.EventBox()
        self.box_button_outputdat.add(self.button_outputdat)
        self.box_outputdat = gtk.HBox()
        self.box_outputdat.pack_start(self.label_outputdat, expand=False)
        self.box_outputdat.pack_start(self.box_button_outputdat, expand=False)
        self.label_outputdat.set_style(style_frame)
        self.box_button_outputdat.set_style(style_frame)
        self.box_outputdat.set_style(style_frame)
        self.buttons_Loop.pack_start(self.box_outputdat,expand=True)
        
        # set output .root filename
        self.label_outputroot = gtk.Label("outputroot")
        self.label_outputroot.set_markup('<span color="white"><b>    Output .root filename   </b></span>')
        self.label_outputroot.set_justify(gtk.JUSTIFY_LEFT)
        self.button_outputroot = gtk.Entry()
        self.button_outputroot.set_width_chars(21)
        self.button_outputroot.set_text("mmfe8_CalibRoutine.root")
        self.button_outputroot.set_editable(True)
        #self.button_outputroot.connect("focus-out-event", self.set_outputroot_LoopCR)
        self.button_outputroot.connect("activate", self.set_outputroot_LoopCR, self.button_outputroot)
        self.button_outputroot.activate()
        self.box_button_outputroot = gtk.EventBox()
        self.box_button_outputroot.add(self.button_outputroot)
        self.box_outputroot = gtk.HBox()
        self.box_outputroot.pack_start(self.label_outputroot, expand=False)
        self.box_outputroot.pack_start(self.box_button_outputroot, expand=False)
        self.label_outputroot.set_style(style_frame)
        self.box_button_outputroot.set_style(style_frame)
        self.box_outputroot.set_style(style_frame)
        self.buttons_Loop.pack_start(self.box_outputroot,expand=True)

        # set desired number of pulses
        self.label_set_pulses = gtk.Label("Number of Pulses / Point")
        self.label_set_pulses.set_markup('<span color="white"><b>    Number of Pulses / Point (1-998)     </b></span>')
        self.label_set_pulses.set_justify(gtk.JUSTIFY_LEFT)
        self.button_set_pulses = gtk.Entry(max=3)
        self.button_set_pulses.set_width_chars(5)
        self.button_set_pulses.set_text("100")
        self.button_set_pulses.set_editable(True)
        #self.button_set_pulses.connect("focus-out-event", self.set_pulses_LoopCR)
        self.button_set_pulses.connect("activate", self.set_pulses_LoopCR, self.button_set_pulses)
        self.button_set_pulses.activate()
        self.box_button_set_pulses = gtk.EventBox()
        self.box_button_set_pulses.add(self.button_set_pulses)
        self.box_set_pulses = gtk.HBox()
        self.box_set_pulses.pack_start(self.label_set_pulses, expand=False)
        self.box_set_pulses.pack_start(self.box_button_set_pulses, expand=False)
        self.label_set_pulses.set_style(style_frame)
        self.box_button_set_pulses.set_style(style_frame)
        self.box_set_pulses.set_style(style_frame)
        self.buttons_Loop.pack_start(self.box_set_pulses,expand=True)
        
        # fix channel
        self.button_fix_chan = gtk.Entry(max=2)
        self.button_fix_chan.set_editable(True)
        self.button_fix_chan.set_width_chars(6)
        self.button_fix_chan.set_text("15")
        self.button_fix_chan.connect("activate", self.fix_chan, self.button_fix_chan)
        self.button_fix_chan.activate()

        # loop channels
        self.button_loop_chan = gtk.Entry()
        self.button_loop_chan.set_editable(True)
        self.button_loop_chan.set_width_chars(8)
        self.button_loop_chan.set_text("15,16,17,18")
        self.button_loop_chan.connect("activate", self.loop_chan, self.button_loop_chan)

        # loop all channels
        self.button_loop_allchan = gtk.CheckButton("All Channels")
        self.button_loop_allchan.connect("toggled", self.loop_all_chan)
        loop_buttons = [self.button_loop_chan,self.button_loop_allchan]
        
        self.frame_chan = loop_pair("Channels",self.button_fix_chan,loop_buttons)
        self.buttons_Loop.pack_start(self.frame_chan.frame,expand=True)

        # fix VMM
        self.button_fix_VMM = gtk.Entry(max=1)
        self.button_fix_VMM.set_editable(True)
        self.button_fix_VMM.set_width_chars(6)
        self.button_fix_VMM.set_text("15")
        self.button_fix_VMM.connect("activate", self.fix_VMM, self.button_fix_VMM)
        self.button_fix_VMM.activate()
        
        # loop VMM
        self.button_loop_VMM = gtk.Entry()
        self.button_loop_VMM.set_editable(True)
        self.button_loop_VMM.set_width_chars(8)
        self.button_loop_VMM.set_text("1,2,3")
        self.button_loop_VMM.connect("activate", self.loop_VMM, self.button_loop_VMM)

        # loop all VMM
        self.button_loop_all_VMM = gtk.CheckButton("All VMMs")
        self.button_loop_all_VMM.connect("toggled", self.loop_all_VMM)
        loop_buttons = [self.button_loop_VMM,self.button_loop_all_VMM]
        
        self.frame_VMM = loop_pair("VMM's",self.button_fix_VMM,loop_buttons)
        self.buttons_Loop.pack_start(self.frame_VMM.frame,expand=True)

        # fix Delay Time
        self.button_fix_delay = gtk.combo_box_new_text()
        self.button_fix_delay.append_text("0 st")        
        self.button_fix_delay.append_text("1 st")
        self.button_fix_delay.append_text("2 st")
        self.button_fix_delay.append_text("3 st")
        self.button_fix_delay.append_text("4 st")
        self.button_fix_delay.connect("changed", self.fix_delay)
        self.button_fix_delay.set_active(0)

        # loop all Delay Times
        self.button_loop_delay = gtk.CheckButton("All Delay Times")
        self.button_loop_delay.connect("toggled", self.loop_delay)

        self.frame_delay = loop_pair("Delay Time",self.button_fix_delay,self.button_loop_delay)
        self.buttons_Loop.pack_start(self.frame_delay.frame,expand=True)
        
        # fix test pulse DAC
        self.button_fix_tpDAC = gtk.Entry(max=3)
        self.button_fix_tpDAC.set_editable(True)
        self.button_fix_tpDAC.set_width_chars(6)
        self.button_fix_tpDAC.set_text("300")
        self.button_fix_tpDAC.connect("activate", self.fix_tpDAC, self.button_fix_tpDAC)
        self.button_fix_tpDAC.activate()

        # loop test pulse DAC
        self.button_loop_tpDAC = gtk.Entry()
        self.button_loop_tpDAC.set_editable(True)
        self.button_loop_tpDAC.set_width_chars(8)
        self.button_loop_tpDAC.set_text("200,300")
        self.button_loop_tpDAC.connect("activate", self.loop_tpDAC, self.button_loop_tpDAC)
        
        self.frame_tpDAC = loop_pair("Test Pulse DAC",self.button_fix_tpDAC,self.button_loop_tpDAC)
        self.buttons_Loop.pack_start(self.frame_tpDAC.frame,expand=True)

        # fix threshold DAC
        self.button_fix_thDAC = gtk.Entry(max=3)
        self.button_fix_thDAC.set_editable(True)
        self.button_fix_thDAC.set_width_chars(6)
        self.button_fix_thDAC.set_text("200")
        self.button_fix_thDAC.connect("activate", self.fix_thDAC, self.button_fix_thDAC)
        self.button_fix_thDAC.activate()
        
        # loop threshold DAC
        self.button_loop_thDAC = gtk.Entry()
        self.button_loop_thDAC.set_editable(True)
        self.button_loop_thDAC.set_width_chars(8)
        self.button_loop_thDAC.set_text("100,200")
        self.button_loop_thDAC.connect("activate", self.loop_thDAC, self.button_loop_thDAC)
        
        self.frame_thDAC = loop_pair("Threshold DAC",self.button_fix_thDAC,self.button_loop_thDAC)
        self.buttons_Loop.pack_start(self.frame_thDAC.frame,expand=True)

        # fix TAC Slope
        self.button_fix_TACslope = gtk.combo_box_new_text()
        self.button_fix_TACslope.append_text("125 ns (00)")        
        self.button_fix_TACslope.append_text("250 ns (01)")
        self.button_fix_TACslope.append_text("500 ns (10)")
        self.button_fix_TACslope.append_text("1000 ns (11)")
        self.button_fix_TACslope.connect("changed", self.fix_TACslope)
        self.button_fix_TACslope.set_active(0)

        # loop all TAC slopes
        self.button_loop_TACslope = gtk.CheckButton("All TAC Slopes")
        self.button_loop_TACslope.connect("toggled", self.loop_TACslope)

        self.frame_TACslope = loop_pair("TAC Slope",self.button_fix_TACslope,self.button_loop_TACslope)
        self.buttons_Loop.pack_start(self.frame_TACslope.frame,expand=True)

        # fix Peaking Time
        self.button_fix_peakingtime = gtk.combo_box_new_text()
        self.button_fix_peakingtime.append_text("200 ns (00)")        
        self.button_fix_peakingtime.append_text("100 ns (01)")
        self.button_fix_peakingtime.append_text("50 ns (10)")
        self.button_fix_peakingtime.append_text("25 ns (11)")
        self.button_fix_peakingtime.connect("changed", self.fix_peakingtime)
        self.button_fix_peakingtime.set_active(0)

        # loop all Peaking Times
        self.button_loop_peakingtime = gtk.CheckButton("All Peaking Times")
        self.button_loop_peakingtime.connect("toggled", self.loop_peakingtime)

        self.frame_peakingtime = loop_pair("Peaking Time",self.button_fix_peakingtime,self.button_loop_peakingtime)
        self.buttons_Loop.pack_start(self.frame_peakingtime.frame,expand=True)
        

        
        

        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #
        #                          FRAME 1   
        #
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        #print "loading Frame 1..."


        self.frame_Reset = gtk.Frame()
        self.frame_Reset.set_shadow_type(gtk.SHADOW_OUT)
        self.frame_Reset.add(self.box_ResetID)

        self.frame_ReadoutMask = gtk.Frame()
        self.frame_ReadoutMask.set_shadow_type(gtk.SHADOW_OUT)
        self.frame_ReadoutMask.add(self.box_ReadoutMask)

        self.box_buttons = gtk.VBox()
        self.box_buttons.set_spacing(5)
        self.box_buttons.set_border_width(5)
        self.box_buttons.set_size_request(-1,-1)

        label_space_1 = gtk.Label(" ")
        label_space_2 = gtk.Label(" ")
        label_space_3= gtk.Label(" ")
        
        self.box_buttons.pack_start(label_space_1,expand=True)
        self.box_buttons.pack_start(self.label_IP,expand=False)
        self.box_buttons.pack_start(self.combo_IP,expand=False)
        self.box_buttons.pack_start(label_space_2,expand=True)
        self.box_buttons.pack_start(self.box_mmfeID,expand=False)
        self.box_buttons.pack_start(label_space_3,expand=True)

        #self.box_buttons.pack_start(self.box_labelID,expand=False)
        #self.box_buttons.pack_start(self.frame_configID,expand=False)
        #self.box_buttons.pack_start(self.frame_ReadoutMask,expand=False)
        #self.box_buttons.pack_start(self.box_vmmID,expand=False)

         # calibration routine
        self.box_buttons.pack_start(self.frame_Loop,expand=False)
        
        self.box_buttons.pack_start(self.label_But_Space8,expand=True)  
        #self.box_buttons.pack_start(self.button_print_config,expand=False)
        #self.box_buttons.pack_start(self.button_write,expand=False)

        #self.box_buttons.pack_start(self.label_But_Space3,expand=True)
        #self.box_buttons.pack_start(self.frame_Reset,expand=False)  
        #self.box_buttons.pack_start(self.button_resetVMM,expand=False)
        #self.button_resetVMM.set_sensitive(False)
        #self.box_buttons.pack_start(self.button_SystemInit,expand=False)
        #self.box_buttons.pack_start(self.button_SystemLoad,expand=False)
        
        #self.box_buttons.pack_start(self.label_Space22,expand=True)
        #self.box_buttons.pack_start(self.box_internal_trigger,expand=False)
        #self.box_buttons.pack_start(self.box_external_trigger,expand=False)
        #self.box_buttons.pack_start(self.box_leaky_readout,expand=False)
        #self.box_buttons.pack_start(self.box_pulses,expand=False)        
        #self.box_buttons.pack_start(self.box_DC,expand=False)        
        #self.box_buttons.pack_start(self.label_pulses2,expand=False)
        self.box_buttons.pack_start(self.box_acq_reset_count,expand=False)        
        #self.box_buttons.pack_start(self.label_acq_reset_count2,expand=False)
        self.box_buttons.pack_start(self.box_acq_reset_hold,expand=False)        
        #self.box_buttons.pack_start(self.label_acq_reset_hold2,expand=False)
        
        #self.box_buttons.pack_start(self.button_start,expand=False)
        #self.box_buttons.pack_start(self.button_start_no_cktp,expand=False)
        # self.box_buttons.pack_start(self.button_read_reg,expand=False)
        
        #self.box_buttons.pack_start(self.label_But_Space4,expand=True)
        # self.box_buttons.pack_start(self.button_read_config_VMM_reg,expand=False)
        #self.box_buttons.pack_start(self.button_read_XADC,expand=False)
        #self.box_buttons.pack_start(self.label_But_Space5,expand=True)
        #self.box_buttons.pack_start(self.button_exit,expand=False)                       
        #self.box_buttons.pack_start(self.label_But_Space2,expand=True)
        #self.box_buttons.pack_start(self.label_But_Space1,expand=True)

        self.page1_box = gtk.HBox(homogeneous=0,spacing=0)      
        self.page1_box.pack_start(self.VMM[0].box_all_channels, expand=False)
        self.page1_box.pack_end(self.VMM[0].box_variables, expand=True)       
        self.page2_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page2_box.pack_start(self.VMM[1].box_all_channels, expand=False)
        self.page2_box.pack_end(self.VMM[1].box_variables, expand=True)                     
        self.page3_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page3_box.pack_start(self.VMM[2].box_all_channels, expand=False)
        self.page3_box.pack_end(self.VMM[2].box_variables, expand=True)  
        self.page4_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page4_box.pack_start(self.VMM[3].box_all_channels, expand=False)
        self.page4_box.pack_end(self.VMM[3].box_variables, expand=True)  
        self.page5_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page5_box.pack_start(self.VMM[4].box_all_channels, expand=False)
        self.page5_box.pack_end(self.VMM[4].box_variables, expand=True)   
        self.page6_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page6_box.pack_start(self.VMM[5].box_all_channels, expand=False)
        self.page6_box.pack_end(self.VMM[5].box_variables, expand=True)  
        self.page7_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page7_box.pack_start(self.VMM[6].box_all_channels, expand=False)
        self.page7_box.pack_end(self.VMM[6].box_variables, expand=True)  
        self.page8_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page8_box.pack_start(self.VMM[7].box_all_channels, expand=False)
        self.page8_box.pack_end(self.VMM[7].box_variables, expand=True)  
        #self.page9_box = gtk.HBox(homogeneous=0,spacing=0)

    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #
    #                      START the GUI
    #
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        #print "Starting the GUI..."

        self.page1_scrolledWindow = gtk.ScrolledWindow()
        self.page1_viewport = gtk.Viewport()
        self.page1_viewport.add(self.page1_box)
        self.page1_scrolledWindow.add(self.page1_viewport)
        self.page2_scrolledWindow = gtk.ScrolledWindow()
        self.page2_viewport = gtk.Viewport()
        self.page2_viewport.add(self.page2_box)
        self.page2_scrolledWindow.add(self.page2_viewport)
        self.page3_scrolledWindow = gtk.ScrolledWindow()
        self.page3_viewport = gtk.Viewport()
        self.page3_viewport.add(self.page3_box)
        self.page3_scrolledWindow.add(self.page3_viewport)
        self.page4_scrolledWindow = gtk.ScrolledWindow()
        self.page4_viewport = gtk.Viewport()
        self.page4_viewport.add(self.page4_box)
        self.page4_scrolledWindow.add(self.page4_viewport)
        self.page5_scrolledWindow = gtk.ScrolledWindow()
        self.page5_viewport = gtk.Viewport()
        self.page5_viewport.add(self.page5_box)
        self.page5_scrolledWindow.add(self.page5_viewport)
        self.page6_scrolledWindow = gtk.ScrolledWindow()
        self.page6_viewport = gtk.Viewport()
        self.page6_viewport.add(self.page6_box)
        self.page6_scrolledWindow.add(self.page6_viewport)
        self.page7_scrolledWindow = gtk.ScrolledWindow()
        self.page7_viewport = gtk.Viewport()
        self.page7_viewport.add(self.page7_box)
        self.page7_scrolledWindow.add(self.page7_viewport)
        self.page8_scrolledWindow = gtk.ScrolledWindow()
        self.page8_viewport = gtk.Viewport()
        self.page8_viewport.add(self.page8_box)
        self.page8_scrolledWindow.add(self.page8_viewport)
        
        self.notebook.append_page(self.page1_scrolledWindow, self.tab_label_1)
        self.notebook.append_page(self.page2_scrolledWindow, self.tab_label_2)
        self.notebook.append_page(self.page3_scrolledWindow, self.tab_label_3)
        self.notebook.append_page(self.page4_scrolledWindow, self.tab_label_4)
        self.notebook.append_page(self.page5_scrolledWindow, self.tab_label_5)
        self.notebook.append_page(self.page6_scrolledWindow, self.tab_label_6)
        self.notebook.append_page(self.page7_scrolledWindow, self.tab_label_7)
        self.notebook.append_page(self.page8_scrolledWindow, self.tab_label_8)
        self.notebook.append_page(self.userRegs.userRegs_box, self.tab_label_9)

        self.page0_scrolledWindow = gtk.ScrolledWindow()
        self.page0_scrolledWindow.set_size_request(550,-1)
        self.page0_viewport = gtk.Viewport()
        self.page0_viewport.add(self.box_buttons)
        self.page0_scrolledWindow.add(self.page0_viewport)
        
        #self.notebook.append_page(self.page9_box, self.tab_label_9)
        self.box_GUI = gtk.HBox(homogeneous=0,spacing=0)
        #self.box_GUI.pack_start(self.myBigButtonsBox, expand=False)
        #self.box_GUI.pack_start(self.box_buttons, expand=False)
        self.box_GUI.pack_start(self.page0_scrolledWindow, expand=False)
        self.box_GUI.pack_end(self.notebook, expand=True)               
        #self.window.add(self.box_buttons)
        self.window.add(self.box_GUI)
        self.window.show_all()
        self.window.connect("destroy",self.destroy)
        
        #print "Put it out there..."

############################__INIT__################################
############################__INIT__################################

    def main(self):
        gtk.main()

############################################################
############################################################
##################      MAIN       #########################
############################################################
############################################################

if __name__ == "__main__":
    mmfe8 = MMFE8()
    mmfe8.main()
