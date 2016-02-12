#!/usr/bin/env python26

"""
MMFE8 VERSION 1.0.0 

ALL REGISTER ADDRESSES ARE BASED ON ADDRESS FOR THE Univ Arizona 
mini1 - GLIB, uHAL - IPbus project

===> THE ADDRESS MAP IS NOT CURRENTLY VALID <===
 
The UDP commands sent to the board are of the form:

command address data newline
W 0x40000063 0xC0FFEE 0xBADC0DE 0xDEADBEEF \n

Where command is W=write, R=read
If multiple data values are sent, the address indexs automatically for each.

This version is for the mmfe8 and is based on version 3.1.7 of the version 
for the mini1.  It prints the configuration stream of 51 32-bit words to the 
terminal based on the configuration setup on the screen of tab 1.  It writes 
these words to the appropriate vmm2 registers.  It cycles the data in the 
registers to vmm2 as a 1616 bit stream.  

This version is able to read the DAQ from the 41-bit FIFO.  The -bit data is 
displayed as:
vmm number, channel address, amplitude, time, and BCid.  
It is also written to a file.  

Currently, waiting for the global, and DAQ resets to be set up in firmware.

The data displayed in the terminal will eventually be displayed in a gtk.
TextViewon one of the tabs.  Histograms will also be displayed, probably 
using pyroot.

-- added the ability to edit user_ipb_vmm_cfg_reg63 (0x44A1_00FF) on tab 3
-- also added the ability to read and write to the FIFO38 ctrl/status reg on tab 3

by Charlie Armijo and James Wymer.
Physics Department
University of Arizona 

"""

import pygtk
pygtk.require('2.0')
import gtk
from array import *
#### On PCROD0 use from Numpy import *
import numpy as np
#from Numeric import *
from struct import *
import gobject 
#from PyChipsUser import *
from subprocess import call
from time import sleep
import sys 
import os
import string
import random
import binstr
###import uhal
import socket
import time
import math



#########################
#########################
##### channel class #####
#########################
#########################
class channel:

    def __init__(self, chan_num):
        self.chan_num = chan_num
        self.chan_obj_list = []

    def add_object(self, object):
        self.chan_obj_list.append(object)

#####################
#####################
##### vmm class #####
#####################
#####################
class Vmm:


    ############################################################
    ##################### GLOBAL VARIABLES #####################
    ############################################################

    #hostAddr = "192.168.0.1"
    #hostPort = 50000
    msg = np.zeros((67), dtype=np.uint32)
    read_msg = np.zeros((67), dtype=np.uint32)
    chan = np.zeros((24), dtype=int)
    globalreg = np.zeros((96), dtype=int)
    #reg = [[chan] for i in range(65)]
    reg = np.zeros((64, 24), dtype=int)
    chnlReg = np.zeros((51), dtype=int)
    dummyReg = np.zeros((32), dtype=int)
    buf = gtk.TextBuffer(table=None)
    byteint = np.zeros((51), dtype=np.uint32)
    myDebug = False
    R = "52"  # ASCII Bytecode for read
    W = "57"  # ASCII Bytecode for pythonwrite
    vmm2cfg = 0 # vmm_cfg_num
    vmm2mon = 0 # vmm_mon_num
    vmm_cfg_sel_reg = np.zeros((32), dtype=int)
    #configAddr = 0x400000C0
    #UDP_IP = "127.0.0.1"
    #UDP_PORT_out = 50001
    #UDP_PORT_data = 50000
    UDP_PORT = 50001
    testreg1 = 0
    testreg2 = 0
    testreg3 = 0
    stopReadOut = False
    #glibAddrTable = AddressTable("./glibAddrTable.dat")
    #hw = list()
    #boardNum = 0
    
    # ipAddr will be obtained from an xml file in the future
    ipAddr = ["127.0.0.1","192.168.0.130","192.168.0.167","192.168.0.101","192.168.0.102",                             "192.168.0.103","192.168.0.104","192.168.0.105","192.168.0.106","192.168.0.107","192.168.0.108","192.168.0.109","192.168.0.110",]
    # each is the starting address for the 51 config regs for each vmm 
    mmfeID = 0
    vmmBaseConfigAddr = [0x44A10020,0x44A10038,0x44A10050,0x44A10068,
                         0x44A10080,0x44A10098,0x44A100B0,0x44A100C8,0x44A100E0]
    chan_list = []
    #boards = list()
    #uHAL_ID = ["glib.10","glib.11","glib.12","glib.13","glib.14"]

    ############################################################
    ################### END GLOBAL VARIABLES ###################
    ############################################################

    ############################################################
    ##################### MAJOR FUNCTIONS #####################
    ############################################################

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

    def udp_client(self, MESSAGE):
        sock = socket.socket(socket.AF_INET, # Internet
             socket.SOCK_DGRAM) # UDP 
        sock.settimeout(5)
        try:
            #send data
            print >>sys.stderr, 'sending "%s"' % MESSAGE
            sent = sock.sendto(MESSAGE,(self.UDP_IP, self.UDP_PORT))

            #receive response
            #sock.setblocking(0)
            #receive response
            print >>sys.stderr, 'waiting for response'
            data, server = sock.recvfrom(4096)
            print >>sys.stderr, 'received:\n' + data
        except:
            print "ERROR:  ", sys.exc_info()[0]

        print "closing socket\n--=====================--\n"
        sock.close()
        return data

    def set_IDs(self, widget):
        self.load_IDs()
        return

    def load_IDs(self):
        #Message = "W 0x44A10100 0x{0:X}".format(self.vmm2cfg) 
        #Message = Message + " 0x{0:X}".format(self.vmm2mon)
        #Message = Message + " 0x{0:X}".format(self.mmfeID)
        #Message = Message + " \0 \n"
        #self.udp_client(Message)
        #print Message
        byteint = 0
        cfg_vmm = '{0:04b}'.format(self.vmm2cfg)
        #print cfg_vmm
        cfg_vmm_list = list(cfg_vmm)
        #print cfg_vmm_list
        cfg_vmm_list = map(int, cfg_vmm)
        #print cfg_vmm_list
        ### add new value to register ###
        for i in range(4): #,-1,-1):
            self.vmm_cfg_sel_reg[28+i] = cfg_vmm_list[i]
	sel_vmm = '{0:04b}'.format(self.vmm2mon)
        sel_vmm_list = list(sel_vmm)
        sel_vmm_list = map(int, sel_vmm)
        #print sel_vmm_list
        ### add new value to register ###
        for i in range(4): #,-1,-1):
            self.vmm_cfg_sel_reg[24+i] = sel_vmm_list[i]
        mmfe_ID = '{0:04b}'.format(self.mmfeID)
        mmfe_ID_list = list(mmfe_ID)
        mmfe_ID_list = map(int, mmfe_ID)
        #print mmfe_ID_list
        ### add new value to register ###
        for i in range(4): #,-1,-1):
            self.vmm_cfg_sel_reg[20+i] = mmfe_ID_list[i]
        #print self.vmm_cfg_sel_reg
        for bit in range(32):
            byteint += int(self.vmm_cfg_sel_reg[bit])*pow(2, 31-bit)
            byteword = int(byteint) 
        print "vmm_cfg_sel = " + str(hex(byteword))
        #print byteword 
        message = "w 0x44A100FC"
        message = message + ' 0x{0:X}'.format(byteword)  
        message = message + '\0' + '\n'
        self.udp_client(message)   
        return
	

    def write_vmmConfigRegisters(self,widget):
        """ create full config list """
        # command strings < 100 chars
        # due to bram limitations on artix7
        self.entry_SDP_.grab_focus()
        self.entry_SDT.grab_focus()
        self.button_write.grab_focus()
        active = self.combo_vmm2_id.get_active()
        #configAddr = self.vmmBaseConfigAddr[0]
        reglist = list(self.reg.flatten())
        globalreglist = list(self.globalreg.flatten())
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
            #myVal2 = hex(myval)
            #print  '0x{0:X}  '.format(myVal) + string 
            MESSAGE = MESSAGE + ' 0x{0:X}'.format(myVal)
            #MESSAGE = MESSAGE + '{0:08X}'.format(myVal).decode('hex')
            if (c+1)%6 == 0:
                w = w + 1
                MSGsend = StartMsg + MESSAGE + '\0' + '\n'
                MESSAGE = ""
                m = m + 24
                StartMsg = "W" +' 0x{0:08X}'.format(self.vmmBaseConfigAddr[w])
                self.udp_client(MSGsend)
                if self.myDebug:
                    print "Sent Message to " + self.UDP_IP 
                    print MSGsend #+ "  {0}".format(m)    
        MSGsend = StartMsg + MESSAGE + '\0' + '\n'
        self.udp_client(MSGsend)
        if self.myDebug:
            print "Sent Message to " + self.UDP_IP 
            print MSGsend
        print "\nWrote to Config Registers\n" 
        self.load_IDs()
        #sleep(5)
        #self.daq_readOut()
               

    def read_reg(self,widget):
        # not currently used -- was intended to read the config stream out
        return        

    def empty_callback(self, widget, data=None):
        """ This Function does nothing, but it is very quick and effective 
        """
        return

    def ext_trigger(self, widget):
        """ Causes the config stream to be clocked into the vmm from the FPGA 
        """
        #set the control reg to 0 and then to run config
        MSGsend0 = "W 0x44A10104 1\0\n" 
        MSGsend1 = "W 0x44A10104 0\0\n"
        #MSGsend2 = "W 0x44A10010 0\0\n"
        self.udp_client(MSGsend0)
        sleep(2)
        self.udp_client(MSGsend1)
        #sleep(2)
        #self.udp_client(MSGsend2)
        #print("Vmm2 Configured")     
             
    def print_config(self, widget):
        ##create and print full config list
        self.entry_SDP_.grab_focus() # gets data for 
        self.entry_SDT.grab_focus()
        self.button_print_config.grab_focus()
        reglist = list(self.reg.flatten())
        globalreglist = list(self.globalreg.flatten())
        fullreg = reglist[::-1] + globalreglist[::-1]
        #self.buf = [] 
        print "\n\nCONFIG STRING"
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
    """    
    def handleData(self, data):
        size = len(data)
        i = 0
        m = 0
        n = 8
        k = 0
        while n <= size:
            i = i + 1
            try:
                fifo41 = data[m:n].encode('hex')
                print fifo41
                if fifo41 < 4:
                    k = k + 1
                    continue 
                currentData = fifo41
                fifo41 = fifo41 >> 2  # get rid of first 2 bits (threshold)
                addr = (fifo41 & 63) + 1 # get channel number as on GUI
                fifo41 = fifo41 >> 6 # get rid of address
                amp = fifo41 &  1023 # get amplitude
                if (amp & 15) == 0:  # are the lower 4 bit zeros?  if so, tag.
                    odd = " ****"
                else:
                    odd = ""
                fifo41 = fifo41 >> 10
                timing = fifo41 & 255
                fifo41 = fifo41 >> 8
                BCid = int(fifo41 & 4095) # next change from gray code to int
                BCid2 = binstr.int_to_b(BCid,16) 
                myBCid = binstr.b_gray_to_bin(BCid2)
                myIntBCid = binstr.b_to_int(myBCid)
                fifo41 = fifo41 >> 12 
                vmm = fifo41 & 7
                fifo41 >> 3
                if fifo41 > 0:
                    print("Error: output data > 41 bits.")
                else:
                    print str(i) + ": FIFO41=" + str(hex(mydata)) + ", vmm=" + (vmm+1) + ", addr=" + str(addr) + \
                               ", amp="+str(amp) + ", time="+str(timing) + ", BCid= " + str(myIntBCid) + odd
                    if odd=="": # only untagged data
                        with open('mmfe8Test.dat', 'a') as myfile:
                            myfile.write(str(int(vmm+1))+'\t'+str(int(addr))+'\t'+ str(int(amp))+'\t'+ str(int(timing))+'\t'+ str(myIntBCid) +'\n')
                m = m + 8
                n = n + 8 
 
            except:
                print "There was an error at data i = ", str(i)
                break
        if k > 0:
            print "d0 and/or d1 high, but no data {0} times." 
    """

    def daq_readOut(self):
        for i in range(10):
            #msgFifoCnt = "r 0x44A10014 1\n" # read word count of data fifo
            msgFifoData = "k 0x44A10010 10\n" # read 10 words from fifo
            fifoData = self.udp_client(msgFifoData)
            #cntData  = self.udp_client(msgFifoCnt)
            #cntList = cntData.split()
            #count = int(cntList[2],0)
            #print count
            n = 2
            while n < 12:
                dataList = fifoData.split()
                fifo32 = int(dataList[n],16)
                if fifo32 > 0:
                    fifo32 = fifo32 >> 2  # get rid of first 2 bits (threshold)
                    addr = (fifo32 & 63) + 1 # get channel number as on GUI
                    fifo32 = fifo32 >> 6 # get rid of address
                    amp = fifo32 &  1023 # get amplitude
                    #if (amp & 15) == 0:  # are the lower 4 bit zeros?  if so, tag.
                    #    odd = " ****"
                    #else:
                    #    odd = ""
                    fifo32 = fifo32 >> 10
                    timing = fifo32 & 255
                    fifo32 = fifo32 >> 8  # we will later check for vmm number
                    if (n+1) < 12:
                        fifohigh = int(dataList[n+1],16)
                        BCIDgray = int(fifohigh & 4095) # next change from gray code to int
                        BCid2 = binstr.int_to_b(BCIDgray,16)
                        myBCid = binstr.b_gray_to_bin(BCid2)
                        myIntBCid = binstr.b_to_int(myBCid)
                        fifohigh = fifohigh >> 12  # later we will get the turn number 	 
                    print dataList[n+1] + " "+ dataList[n] + ", addr=" + str(addr) + \
                                   ", amp="+str(amp) + ", time="+str(timing) + ", BCid= " + str(myIntBCid)
                    with open('mmfe8Test.dat', 'a') as myfile:
                                myfile.write(str(int(addr))+'\t'+ str(int(amp))+'\t'+ str(int(timing))+'\t'+ str(myIntBCid) +'\n')
                    n=n+2
                else:
                    print "out of order or no data =" #+ str(hex(dataList[n]))
                    n= n+1 
                sleep(0.002)
            #sleep(2)
            #cntData  = self.udp_client(msgFifoCnt)
            #cntList = cntData.split()
            #count = int(cntList[2],0)    
          

    """
    def daq_ReadOutserver(self):
        # This creates a new thread to read each data packet
        loopback = False
        active = self.combo_vmm2_id.get_active()
        sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
        if active == 0:
            UDP_IP = self.ipAddr[0] # loopback
            UDP_PORT = self.UDP_PORT_data
            loopback = True
        else:
            UDP_IP = hostAddr
            UDP_PORT = hostPort
        #    sock.bind((UDP_IP, UDP_PORT))
        print("DAQ Read Out Server Started")
        while True:
            if self.stopReadOut:
                print("Exiting DAQ Read Out Server.")
                break
            n = 1
            if loopback:
                data = ""
                for n in range(60):
                    sleep(0.001)
                    Vmm = random.randint(0, 7) << 6
                    BC = random.randint(0, 4196)
                    BCtop = BC >> 6
                    BClow = (BC & 0x3F) << 26
                    Tim = random.randint(0, 255) << 18
                    Amp = random.randint(0, 1023) << 8
                    Addr = random.randint(0, 63) << 2
                    data2 = Vmm + BCtop
                    data1 = BClow + Tim + Amp + Addr + 2
                    data = data + "0x" + str(hex(data1)) + " 0x" + str(hex(data2)) + " "
            else:         
                #    data, addr = sock.recvfrom(2048) # buffer size is 2048 bytes
                continue
            try:
                thread.start_new_thread(handleData, data)
                n = n + 1
            except:
                print "Error:  Unable to start thread {0}.".format(n)        
    """

    def reset_fifo(self):
        print "\nResetting the DAQ FIFO"
        MSGsend0 = "W 0x44A10082 1 0\n" #reset FIFO
        MSGsend1 = "W 0x44A100FF 1 8\n"
        MSGsend2 = "W 0x44A10082 1 0\n"
        self.udp_client(MSGsend0)
        self.udp_client(MSGsend1)
        self.udp_client(MSGsend2)
        print("Data FIFO Reset\n")

    def acq_reset(self):
        print "\nrunning acquistion reset"
        MSGsend0 = "W 0x44A100FF 0\n"
        MSGsend1 = "W 0x44A100FF 8\n"
        MSGsend2 = "W 0x44A100FF 0\n"
        self.udp_client(MSGsend0)
        self.udp_client(MSGsend1)
        self.udp_client(MSGsend2)
        print("Acquistion Reset Completed.")
 
    def start(self, widget):
        #print "\nStarting VMM2 enable high, cktp and cktk set to run"
        #self.label_start.set_markup('<span color="#008000" ><b>START\nrunning...</b></span>')
        #self.label_start_no_cktp.set_markup('<span color="#000000" >Start No CKTP</span>')      
        #self.label_stop_reset_acq.set_markup('<span color="#C00000" ><b>STOP</b></span>')
        #self.stopReadOut = False
        self.daq_readOut()
        #self.reset_fifo()
        #self.acq_reset()
        #MSGsend = "W 0x44A100FF 1 0x70\0\n"
        #self.udp_client(MSGsend)               
        
    def start_no_cktp(self, widget):
        print "\nStarting VMM2"
        self.label_start.set_markup('<span color="#000000" >Start</span>')
        self.label_start_no_cktp.set_markup('<span color="#008000" ><b>START NO CKTP\nrunning...</b></span>')      
        self.label_stop_reset_acq.set_markup('<span color="#C00000" ><b>STOP</b></span>')
        self.stopReadOut = False
        self.daq_ReadOutserver()
        self.acq_reset()
        MSGsend = "W 0x44A100FF 1 0x50\0\n"
        self.udp_client(MSGsend)               
        
    def clear_data_file(self, widget):
        print "\nClearing mmfe8Test.dat"
        with open('mmfe8Test.dat', 'w') as myfile:
             myfile.write("")
   
    def reset_global(self, widget):
        print "\nRunning Global Reset"
        #self.reset_fifo()
        MSGsend0 = "W 0x44A10100 0 \0\n"  
        MSGsend1 = "W 0x44A10100 1 \0\n"
        #sleep(1)
        MSGsend2 = "W 0x44A10100 0 \0\n" 
        self.udp_client(MSGsend0) 
        self.udp_client(MSGsend1)
	sleep(1)
        self.udp_client(MSGsend2)       
        print "Global Rest Completed\n" 

    def send_pulses(self, widget):
        print "\nSending CKTP"
        #self.reset_fifo()
        MSGsend0 = "W 0x44A1014C 0 \0\n"  
        MSGsend1 = "W 0x44A1014C 1 \0\n"
        MSGsend2 = "W 0x44A1014C 0 \0\n" 
        self.udp_client(MSGsend0) 
        self.udp_client(MSGsend1)
	sleep(1)
        self.udp_client(MSGsend2)       
        print "Send CKTP Completed\n"   


    #######################################################
    ##################                  ###################
    ##################      CHANNEL     ###################
    ##################     FUNCTIONS    ###################
    ##################                  ###################
    #######################################################

            
    ##### input charge polarity #####
    def SP_callback(self, widget, data=None):
        SP = self.reg[data-1][0]
        if widget.get_active():
            ### toggle button is down ###
            if SP == 0:
                self.reg[data-1][0] = 1
                widget.set_label("p")
        else:
            ### toggle button is up ###
            if SP > 0:
                self.reg[data-1][0] = 0
                widget.set_label("n")

    ##### large sensor capacitance mode #####
    def SC_callback(self, widget, data=None):
        SC = self.reg[data-1][1]
        if widget.get_active():
        ### button is checked ###
            if SC == 0:
                self.reg[data-1][1] = 1
        else:
        ### button is not checked ###
            if SC > 0:
                self.reg[data-1][1] = 0

    ##### leakage current disable #####
    def SL_callback(self, widget, data=None):
        SL = self.reg[data-1][2]
        if widget.get_active():
        ### button is checked ###
            if SL == 0:
                self.reg[data-1][2] = 1
        else:
        ### button is not checked ###
            if SL > 0:
                self.reg[data-1][2] = 0

    ##### test capacitor enable #####
    def ST_callback(self, widget, data=None):
        ST = self.reg[data-1][3]
        if widget.get_active():
        ### button is checked ###
            if ST == 0:
                self.msg[data-1] = self.msg[data-1] + np.uint32(0x0008)
                self.reg[data-1][3] = 1
        else:
        ### button is not checked ###
            if ST > 0:
                self.msg[data-1] = self.msg[data-1] - np.uint32(0x0008)
                self.reg[data-1][3] = 0

    ##### mask enable #####
    def SM_callback(self, widget, data=None):
        SM = self.reg[data-1][4]
        if widget.get_active():
        ### button is checked ###
            if SM == 0:
                self.msg[data-1] = self.msg[data-1] + np.uint32(0x0010)
                self.reg[data-1][4] = 1
        else:
        ### button is not checked ###
            if SM > 0:
                self.msg[data-1] = self.msg[data-1] - np.uint32(0x0010)
                self.reg[data-1][4] = 0

    ##### threshold DAC #####
    def get_SD_value(self, widget, data=None):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SD_value = active
            self.msg[data-1] = np.uint32(0xFE1F) & self.msg[data-1]

            ### convert value to list of binary digits ###
            SD_value = '{0:04b}'.format(SD_value)
            SD_list = list(SD_value)
            SD_list = map(int, SD_value)

            ### add new value to register ###
            self.msg[data-1] = np.uint32(SD_value) ^ self.msg[data-1]
            for i in range(3,-1,-1):        
                self.reg[data-1][i+5] = SD_list[i]

    ##### channel monitor mode #####
    def SMX_callback(self, widget, data=None):
        SMX = self.reg[data-1][9]
        if widget.get_active():
        ### button is checked ###
            if SMX == 0:
                self.reg[data-1][9] = 1
        else:
        ### button is not checked ###
            if SMX > 0:
                self.reg[data-1][9] = 0

    ##### 10-bit ADC #####
    def get_SZ10b_value(self, widget, data=None):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SZ10b = active

            ### convert value to list of binary digits ###
            SZ10b = '{0:05b}'.format(SZ10b)
            SZ10b_list = list(SZ10b)
            SZ10b_list = map(int, SZ10b)

            ### add new value to register ###
            for i in range(4,-1,-1):
                self.reg[data-1][i+10] = SZ10b_list[i]

    ##### 8-bit ADC #####
    def get_SZ8b_value(self, widget, data=None):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SZ8b = active

            ### convert value to list of binary digits ###
            SZ8b = '{0:04b}'.format(SZ8b)
            SZ8b_list = list(SZ8b)
            SZ8b_list = map(int, SZ8b)

            ### add new value to register ###
            for i in range(3,-1,-1):
                self.reg[data-1][i+15] = SZ8b_list[i]

    ##### 6-bit ADC #####
    def get_SZ6b_value(self, widget, data=None):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SZ6b = active

            ### convert value to list of binary digits ###
            SZ6b = '{0:03b}'.format(SZ6b)
            SZ6b_list = list(SZ6b)
            SZ6b_list = map(int, SZ6b)

            ### add new value to register ###
            for i in range(2,-1,-1):
                self.reg[data-1][i+19] = SZ6b_list[i]

    ###############################################################
    #####################                  ########################
    #####################      GLOBAL      ########################
    #####################     COMMANDS     ########################
    #####################                  ########################
    ###############################################################

    ##### delay counts #####
    def glob_DC_value(self, widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            DC = active
#            MSGsend1 = "W 0x44A10148 " + str(DC)+" \0\n"
            MSGsend1 = "W 0x44A10148 {0:02x} \0\n".format(DC)
            self.udp_client(MSGsend1)
    
    def SP_qs_callback(self, widget):
        if widget.get_active():
                widget.set_label("p")
        else:
                widget.set_label("n")

    def quick_set(self, widget):
        
        if self.check_button_SP_qs.get_active():
            if self.toggle_button_SP.get_active():        
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[2].set_active(True)
                        self.chan_list[ch_num].chan_obj_list[2].set_label("p") 
            else:
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[2].set_active(False)
                        self.chan_list[ch_num].chan_obj_list[2].set_label("n") 
        
        if self.check_button_SC_qs.get_active():
            if self.check_button_SC.get_active():        
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[3].set_active(True) 
            else:
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[3].set_active(False)

        if self.check_button_SL_qs.get_active():
            if self.check_button_SL.get_active():        
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[4].set_active(True) 
            else:
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[4].set_active(False)

        if self.check_button_ST_qs.get_active():
            if self.check_button_ST.get_active():        
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[5].set_active(True) 
            else:
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[5].set_active(False)

        if self.check_button_SM_qs.get_active():
            if self.check_button_SM.get_active():        
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[6].set_active(True) 
            else:
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[6].set_active(False)

        if self.check_button_SD_qs.get_active():
            active = self.combo_SD_qs.get_active()        
            for ch_num in range(0, 65):
                if ch_num < 65:
                    self.chan_list[ch_num].chan_obj_list[7].set_active(active) 

        if self.check_button_SMX_qs.get_active():
            if self.check_button_SMX.get_active():        
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[8].set_active(True) 
            else:
                for ch_num in range(0, 65):
                    if ch_num < 65:
                        self.chan_list[ch_num].chan_obj_list[8].set_active(False)
       
    ##########################################################################################################
    
    def set_board_ip(self, widget, textBox):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            board = active
            self.UDP_IP = self.ipAddr[board]
            textBox.set_text(str(board))
            self.mmfeID = int(board)
            print "UDP_IP= " + self.UDP_IP + "    MMFE8 ID= " + str(self.mmfeID)


    def set_vmm_cfg_num(self, widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            self.vmm2cfg =  int(active)
            print "Config vmm # = " + str(self.vmm2cfg)

    def set_vmm_mon_num(self, widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            self.vmm2mon = int(active)
            print "Monitor vmm # = " + str(self.vmm2mon)

    ##########################################################################################################

    ##### input charge polarity #####
    def glob_SPG_callback(self, widget, data=None):
        SPG = self.globalreg[16]
        if widget.get_active():
        ### button is checked ###
            if SPG == 0:
                self.globalreg[16] = 1
        else:
        ### button is not checked ###
            if SPG > 0:
                self.globalreg[16] = 0

    ##### disable at peak #####
    def glob_SDPeak_callback(self, widget, data=None):
        SDP = self.globalreg[17]
        if widget.get_active():
        ### button is checked ###
            if SDP == 0:
                self.globalreg[17] = 1
        else:
        ### button is not checked ###
            if SDP > 0:
                self.globalreg[17] = 0

    ##### route analog monitor to pdo output #####
    def glob_SBMX_callback(self, widget, data=None):
        SBMX = self.globalreg[18]
        if widget.get_active():
        ### button is checked ###
            if SBMX == 0:
                self.globalreg[18] = 1
        else:
        ### button is not checked ###
            if SBMX > 0:
                self.globalreg[18] = 0

    ##### analog output buffers enable tdo #####
    def glob_SBFT_callback(self, widget, data=None):
        SBFT = self.globalreg[19]
        if widget.get_active():
        ### button is checked ###
            if SBFT == 0:
                self.globalreg[19] = 1
        else:
        ### button is not checked ###
            if SBFT > 0:
                self.globalreg[19] = 0

    ##### analog output buffers enable pdo #####
    def glob_SBFP_callback(self, widget, data=None):
        SBFP = self.globalreg[20]
        if widget.get_active():
        ### button is checked ###
            if SBFP == 0:
                self.globalreg[20] = 1
        else:
        ### button is not checked ###
            if SBFP > 0:
                self.globalreg[20] = 0

    ##### analog output buffers enable mo #####
    def glob_SBFM_callback(self, widget, data=None):
        SBFM = self.globalreg[21]
        if widget.get_active():
        ### button is checked ###
            if SBFM == 0:
                self.globalreg[21] = 1
        else:
        ### button is not checked ###
            if SBFM > 0:
                self.globalreg[21] = 0

    ##### leakage current disable #####
    def glob_SLG_callback(self, widget, data=None):
        SLG = self.globalreg[22]
        if widget.get_active():
        ### button is checked ###
            if SLG == 0:
                self.globalreg[22] = 1
        else:
        ### button is not checked ###
            if SLG > 0:
                self.globalreg[22] = 0

    ##### monitor multiplexing #####
    def glob_SM_value(self, widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SM = active

            ### convert value to list of binary digits ###
            SM = '{0:06b}'.format(SM)
            SM_list = list(SM)
            SM_list = map(int, SM)

            ### add new value to register ###
            for i in range(5,-1,-1):
                self.globalreg[i+23] = SM_list[i]

    ##### monitor multiplexing enable #####
    def glob_SCMX_callback(self, widget, data=None):
        SCMX = self.globalreg[29]
        if widget.get_active():
        ### button is checked ###
            if SCMX == 0:
                self.globalreg[29] = 1
        else:
        ### button is not checked ###
            if SCMX > 0:
                self.globalreg[29] = 0

    ##### ART enable #####
    def glob_SFA_callback(self, widget, data=None):
        SFA = self.globalreg[30]
        if widget.get_active():
        ### button is checked ###
            if SFA == 0:
                self.globalreg[30] = 1
        else:
        ### button is not checked ###
            if SFA > 0:
                self.globalreg[30] = 0

    ##### ART mode #####
    def glob_SFAM_value(self, widget, data=None):
        SFAM = self.globalreg[31]
        if widget.get_active():
        ### 2nd option is selected ###
            if SFAM == 0:
               self.globalreg[31] = 1
        else:
        ### 1st option is selected ###
            if SFAM > 0:
                self.globalreg[31] = 0


##### peaking time #####
    def glob_ST_value(self, widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            ST = active

            ### convert value to list of binary digits ###
            ST = '{0:02b}'.format(ST)
            ST_list = list(ST)
            ST_list = map(int, ST)

            ### add new value to register ###
            for i in range(1,-1,-1):
                self.globalreg[i+32] = ST_list[i]

    ##### UNKNOWN #####
    def glob_SFM_callback(self, widget, data=None):
        SFM = self.globalreg[34]
        if widget.get_active():
        ### button is checked ###
            if SFM == 0:
                self.globalreg[34] = 1
        else:
        ### button is not checked ###
            if SFM > 0:
                self.globalreg[34] = 0

    ##### gain #####
    def glob_SG_value(self, widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SG = active

            ### convert value to list of binary digits ###
            SG = '{0:03b}'.format(SG)
            SG_list = list(SG)
            SG_list = map(int, SG)

            ### add new value to register ###
            for i in range(2,-1,-1):
                self.globalreg[i+35] = SG_list[i]

    ##### neighbor triggering enable #####
    def glob_SNG_callback(self, widget, data=None):
        SNG = self.globalreg[38]
        if widget.get_active():
        ### button is checked ###
            if SNG == 0:
                self.globalreg[38] = 1
        else:
        ### button is not checked ###
            if SNG > 0:
                self.globalreg[38] = 0

    ##### timing outputs control ##### 
    def glob_STOT_value(self, widget, data=None):
        STOT = self.globalreg[39]
        if widget.get_active():
        ### button is checked ###
            if STOT == 0:
                self.globalreg[39] = 1
        else:
        ### button is not checked ###
            if STOT > 0:
                self.globalreg[39] = 0

    ##### timing outputs enable #####
    def glob_STTT_callback(self, widget, data=None):
        STTT = self.globalreg[40]
        if widget.get_active():
        ### button is checked ###
            if STTT == 0:
                self.globalreg[40] = 1
        else:
        ### button is not checked ###
            if STTT > 0:
                self.globalreg[40] = 0

    ##### sub-hysteresis discrimination enable #####
    def glob_SSH_callback(self, widget, data=None):
        SSH = self.globalreg[41]
        if widget.get_active():
        ### button is checked ###
            if SSH == 0:
                self.globalreg[41] = 1
        else:
        ### button is not checked ###
            if SSH > 0:
                self.globalreg[41] = 0

    ##### TAC slope adjustment #####
    def glob_STC_value(self,widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            STC = active

            ### convert value to list of binary digits ###
            STC = '{0:02b}'.format(STC)
            STC_list = list(STC)
            STC_list = map(int, STC)

            ### add new value to register ###
            for i in range(1,-1,-1):
                self.globalreg[i+42] = STC_list[i]

    ##### course threshold DAC #####
    def glob_SDT_entry(self, widget, entry):
        try:
            entry = widget.get_text()
            value = int(entry)
        except ValueError:
            print "SDT value must be a decimal number"
            print
            return None                
        if (value < 0) or (1023 < value):
            print "SDT value out of range"
            print
            return None
        else:
            SDT = value

            ### convert value to list of binary digits ###
            SDT = '{0:010b}'.format(SDT)
            SDT_list = list(SDT)
            SDT_list = map(int, SDT)

            ### add new value to register ###
            for i in range(9,-1,-1):
                self.globalreg[i+44] = SDT_list[i] ## 28

    ##### test pulse DAC #####
    def glob_SDP_entry(self,widget,entry):
        try:
            entry = widget.get_text()
            value = int(entry)
        except ValueError:
            print "SDP value must be a decimal number"
            print
            return None                
        if (value < 0) or (1023 < value):
            print "SDP value out of range"
            print
            return None
        else:
            SDP = value

            ### convert value to list of binary digits ###
            SDP = '{0:010b}'.format(SDP)
            SDP_list = list(SDP)
            SDP_list = map(int, SDP)

            ### add new value to register ###
            for i in range(9,-1,-1):
                self.globalreg[i+54] = SDP_list[i] ## 38

    ##### 10-bit ADC conversion time #####
    def glob_SC10b_value(self,widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SC10b = active

            ### convert value to list of binary digits ###
            SC10b = '{0:02b}'.format(SC10b)
            SC10b_list = list(SC10b)
            SC10b_list = map(int, SC10b)

            ### add new value to register ###
            # reverse bit order
            for i in range(2):
                self.globalreg[65-i] = SC10b_list[i]

    ##### 8-bit ADC conversion time #####
    def glob_SC8b_value(self,widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SC8b = active

            ### convert value to list of binary digits ###
            SC8b = '{0:02b}'.format(SC8b)
            SC8b_list = list(SC8b)
            SC8b_list = map(int, SC8b)

            ### add new value to register ###
            # reverse bit order
            for i in range(2):
                self.globalreg[67-i] = SC8b_list[i]

    ##### 6-bit ADC conversion time #####
    def glob_SC6b_value(self,widget):
        active = widget.get_active()
        if active < 0:
            return None
        else:
            SC6b = active

            ### convert value to list of binary digits ###
            SC6b = '{0:03b}'.format(SC6b)
            SC6b_list = list(SC6b)
            SC6b_list = map(int, SC6b)

            ### add new value to register ###
            # reverse bit order
            for i in range(3):
                self.globalreg[70-i] = SC6b_list[i]

    ##### 8-bit ADC conversion mode #####
    def glob_S8b_callback(self,widget, data=None):
        S8b = self.globalreg[71]
        if widget.get_active():
        ### button is checked ###
            if S8b == 0:
               self.globalreg[71] = 1
        else:
        ### button is not checked ###
            if S8b > 0:
                self.globalreg[71] = 0

    ##### 6-bit ADC conversion enable #####
    def glob_S6b_callback(self, widget, data=None):
        S6b = self.globalreg[72]
        if widget.get_active():
        ### button is checked ###
            if S6b == 0:
                self.globalreg[72] = 1
        else:
        ### button is not checked ###
            if S6b > 0:
                self.globalreg[72] = 0

    ##### ADCs enable #####
    def glob_SPDC_callback(self, widget, data=None):
        SPDC = self.globalreg[73]
        if widget.get_active():
        ### button is checked ###
            if SPDC == 0:
                self.globalreg[73] = 1
        else:
        ### button is not checked ###
            if SPDC > 0:
                self.globalreg[73] = 0

    ##### dual clock edge serialized data enable #####
    def glob_SDCKS_callback(self, widget, data=None):
        SDCKS = self.globalreg[74]
        if widget.get_active():
        ### button is checked ###
            if SDCKS == 0:
                self.globalreg[74] = 1
        else:
        ### button is not checked ###
            if SDCKS > 0:
                self.globalreg[74] = 0

    ##### dual clock edge serialized ART enable #####
    def glob_SDCKA_callback(self, widget, data=None):
        SDCKA = self.globalreg[75]
        if widget.get_active():
        ### button is checked ###
            if SDCKA == 0:
                self.globalreg[75] = 1
        else:
        ### button is not checked ###
            if SDCKA > 0:
                self.globalreg[75] = 0

    ##### dual clock edge serialized 6-bit enable #####
    def glob_SDCK6b_callback(self, widget, data=None):
        SDCK6b = self.globalreg[76]
        if widget.get_active():
        ### button is checked ###
            if SDCK6b == 0:
                self.globalreg[76] = 1
        else:
        ### button is not checked ###
            if SDCK6b > 0:
                self.globalreg[76] = 0

    ##### tristates analog outputs with token, used in analog mode #####
    def glob_SDRV_callback(self, widget, data=None):
        SDRV = self.globalreg[77]
        if widget.get_active():
        ### button is checked ###
            if SDRV == 0:
                self.globalreg[77] = 1
        else:
        ### button is not checked ###
            if SDRV > 0:
                self.globalreg[77] = 0

    ##### timing outputs control 2 #####
    def glob_STPP_callback(self, widget, data=None):
        STPP = self.globalreg[78]
        if widget.get_active():
        ### button is checked ###
            if STPP == 0:
                self.globalreg[78] = 1
        else:
        ### button is not checked ###
            if STPP > 0:
                self.globalreg[78] = 0

    def myTest(self, widget, data=None):
        print "Hello"

#########################################
########### page 3 commands #############
#########################################

    def tobits(self, s):
        result = []
        for c in s:
            bits = bin(ord(c))[2:]
            bits = '00000000'[len(bits):] + bits
            #result.extend([int(b) for b in bits])
        return bits

    def page3_write_button_statusReg1_callback(self, widget, textBox):
        try:            
            entry = int(textBox.get_text(),base=16)
            if entry > 0xffffffff:
                myMsg = "a ValueError exception occurred\nReg 1 Value > 0xFFFFFFFF."
                self.on_erro(widget, myMsg)
            else:    
                
                # IPbus Transaction
                self.hw.getNode("B").getNode("A0").write(entry)
                self.hw.dispatch()
                
                print "Wrote",hex(entry),"to STATUS REG 1"
            
        except IOError as e:
            myMsg = "I/O Error:  {1}".format(e.errno, e.strerror)
            self.on_erro(widget, myMsg)
        except ValueError:
            myMsg = "a ValueError exception occurred\nStatus Reg 1 not hexadecimal."
            self.on_erro(widget, myMsg)
        except:
            print  "Unexpected Error:  ", sys.exc_info()[0]
            self.on_erro(widget, "Unexpected Error:\nDetails printed to shell.")
        
    def page3_write_button_ctrlReg1_callback(self, widget, textBox):
        VALUE = textBox.get_text()
        myValue = string.split(VALUE,'x')
        if (len(myValue) == 1):
            MESSAGE = "W 0x44A10010 1 0x" + myValue[0] + "\n"
        elif (len(myValue) == 2):
            MESSAGE = "W 0x44A10010 1 0x" + myValue[1] + "\n"
        else:
            print "ERROR:  Improper value"
            textBox.set_text("Error!")
            return 0
        #print myValue
        print "Sending: " + MESSAGE
        data = self.udp_client(MESSAGE)
        myData = string.split(data,'\n')
        textBox.set_text(myData[0])
       
        """
        try:
            entry = int(textBox.get_text(),base=16)
            if entry > 0xffffffff:
                myMsg = "a ValueError exception occurred\nCtrl Reg 2 Value > 0xFFFFFFFF."
                self.on_erro(widget, myMsg)
            else:                    
                # IPbus Transaction
                self.hw.getNode("B").getNode("A3").write(entry)
                self.hw.dispatch()                
                print "Wrote",hex(entry),"to 32-bit Scratch Pad Reg\n"
        except IOError as e:
            myMsg = "I/O Error:  {1}".format(e.errno, e.strerror)
            self.on_erro(widget, myMsg)
        except ValueError:
            myMsg = "a ValueError exception occurred\nCtrl Reg 1 Value not hexadecimal."
            self.on_erro(widget, myMsg)
        except:
            print "Unexpected Error:  ", sys.exc_info()[0]
            self.on_erro(widget, "Unexpected Error:\nDetails printed to shell.")
        """
        
    def page3_write_button_ctrlReg2_callback(self, widget, textBox):
        try:
            entry = int(textBox.get_text(),base=16)
            if entry > 0xffffffff:
                myMsg = "a ValueError exception occurred\nCtrl Reg 2 Value > 0xFFFFFFFF."
                self.on_erro(widget, myMsg)
            else:                   
                self.hw.getNode("DAQ").getNode("A0").write(entry)
                self.hw.dispatch()                
                print "Wrote",hex(entry),"to FIF038 CTRL REG 82"
        except IOError as e:
            myMsg = "I/O Error:  {1}".format(e.errno, e.strerror)
            self.on_erro(widget, myMsg)
        except ValueError:
            myMsg = "a ValueError exception occurred\nFIFO38 Ctrl Reg 2 Value not hexadecimal."
            self.on_erro(widget, myMsg)
        except:
            print "Unexpected Error:  ", sys.exc_info()[0]
            self.on_erro(widget, "Unexpected Error:\nDetails printed to shell.")
        
    def page3_write_button_ctrlReg63_callback(self, widget, textBox):
        try:
            entry = int(textBox.get_text(),base=16)
            if entry > 0xffffffff:
                myMsg = "a ValueError exception occurred\nCtrl Reg 63 Value > 0xFFFFFFFF."
                self.on_erro(widget, myMsg)
            else:    
                
                self.hw.getNode("CFG").getNode("A63").write(entry)
                self.hw.dispatch()
                
                print "Wrote",hex(entry),"to CTRL REG 63"
        except IOError as e:
            myMsg = "I/O Error:  {1}".format(e.errno, e.strerror)
            self.on_erro(widget, myMsg)
        except ValueError:
            myMsg = "a ValueError exception occurred\nCtrl Reg 63 Value not hexadecimal."
            self.on_erro(widget, myMsg)
        except:
            print "Unexpected Error Writing to Ctrl Reg 63:\n", sys.exc_info()[0]
            self.on_erro(widget, "Unexpected Error:\nDetails printed to shell.")

    #==========================  READ BUTTONS  ===========================   
    def page3_read_button_statusReg1_callback(self, widget, textBox):
        """
        try:
            # IPbus Transaction
            
            #entry = self.hw.getNode("B").getNode("A0").read()
            #self.hw.dispatch()
            
            #print "Status Reg 1 value =",             
            # Enter into box.
            #textBox.set_text(hex(entry))
            #print "Status Reg 1 contains", hex(entry)
        """
        MESSAGE = "r 0x44A10100 1\n"
        data = self.udp_client(MESSAGE)
        myData = string.split(data,' ')
        textBox.set_text(myData[2])
        print "Should be 0x67_6F_6C_64 = gold in ascii"
        """"    
        except IOError as e:
            myMsg = "I/O Error Reading Status Reg 1:\n{1}".format(e.errno, e.strerror)
            self.on_erro(widget, myMsg)
        except:
            print "Unexpected Errohw.getNoder Reading Status Reg 1:\n", sys.exc_info()[0]
            self.on_erro(widget, "Unexpected Error:\nDetails printed to shell.")
         """       

    def page3_read_button_ctrlReg1_callback(self, widget, textBox):
        MESSAGE = "r 0x40000101 1\n"
        data = self.udp_client(MESSAGE)
        myData = string.split(data,' ')
        textBox.set_text(myData[2])        

    def page3_read_button_ctrlReg2_callback(self, widget, textBox):
        try:          
            MSG = "r 0x44A10187 1\n"
            data = self.udp_client(MSG)
            myData = string.split(data,' ')

            #print "FIFO41 Ctrl Reg 187 contains", hex(myData)
            
        except IOError as e:
            myMsg = "I/O Error Reading FIFO41 Ctrl Reg 182:\n{1}".format(e.errno, e.strerror)
            self.on_erro(widget, myMsg)
        except:
            print "Unexpected Error Reading FIFO41 Ctrl Reg 2:\n", sys.exc_info()[0]
            self.on_erro(widget, "Unexpected Error:\nDetails printed to shell.")
        

    def page3_read_button_crtlReg63_callback(self, widget, textBox):
        try:
            MSG = "r 0x44A10187 1\n"
            data = self.udp_client(MSG)
            myData = string.split(data,' ')

            #print "Ctrl Reg 63 contains", hex(entry)
          
        except IOError as e:
            myMsg = "I/O Error Reading Ctrl Reg 63:\n{1}".format(e.errno, e.strerror)
            self.on_erro(widget, myMsg)
        except:
            print "Unexpected Error Reading Ctrl Reg 63:\n", sys.exc_info()[0]
            self.on_erro(widget, "Unexpected Error:\nDetails printed to shell.")

    

    ####################################################################
    ##########################            ##############################
    ##########################  __INIT__  ##############################
    ##########################            ##############################
    ####################################################################

    def __init__(self):
        print "loading GUI..."
        print 
        self.tv = gtk.TextView()
        self.tv.set_editable(False)
        self.tv.set_wrap_mode(gtk.WRAP_WORD)
        self.buffer = self.tv.get_buffer()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(1500,950) ###set_size_request(1440,900)
        self.window.set_resizable(True)
        self.window.set_title("MMFE8 Setup GUI (v4.0.1)")
        self.window.set_border_width(0)
        self.notebook = gtk.Notebook()
        self.notebook.set_size_request(-1,0)
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.tab_label_1 = gtk.Label("VMM2 A Config")
        self.tab_label_2 = gtk.Label("VMM2 Output")
        self.tab_label_3 = gtk.Label("Register Test")
        # self.findHw()

        
        """print "Configuration Message Array ="
        print self.globalreg
        print self.reg
        print "read back message array ="
        #print self.read_msg"""


        ####################################################
        ####################         #######################
        #################### BUTTONS #######################
        ####################         #######################
        ####################################################

        self.button_exit = gtk.Button("EXIT")
        self.button_exit.set_size_request(-1,-1)
        self.button_exit.connect("clicked",self.destroy)

        self.button_start = gtk.Button("Start")
        self.button_start.child.set_justify(gtk.JUSTIFY_CENTER)
        self.label_start = self.button_start.get_children()[0]
        self.button_start.set_size_request(-1,-1)
        self.button_start.connect("clicked",self.start)
        #self.button_start.set_sensitive(False)

        self.button_clear_data_file = gtk.Button("Clear Data File")
        self.button_clear_data_file.child.set_justify(gtk.JUSTIFY_CENTER)
        #self.button_clear_data_file.set_sensitive(False)
        
        self.label_stop_reset_acq = self.button_clear_data_file.get_children()[0]
        self.button_clear_data_file.set_size_request(-1,-1)
        self.button_clear_data_file.connect("clicked",self.clear_data_file)    

#        self.button_resetVMM = gtk.Button("Global Reset")
#        self.button_resetVMM.set_size_request(-1,-1)
#        self.button_resetVMM.connect("clicked",self.reset_global)
#        #self.button_resetVMM.set_sensitive(False)

       	self.button_resetVMM = gtk.Button("Global Reset and Configure VMM")
        self.button_resetVMM.set_size_request(-1,-1)
        self.button_resetVMM.connect("clicked",self.reset_global)
        #self.button_resetVMM.set_sensitive(False)

       	self.button_pulse = gtk.Button("Send CKTP")
        self.button_pulse.set_size_request(-1,-1)
        self.button_pulse.connect("clicked",self.send_pulses)

        self.label_But_Space1 = gtk.Label(" ")
        self.label_But_Space2 = gtk.Label(" ")        
        self.label_But_Space3 = gtk.Label(" ")
        self.label_But_Space4 = gtk.Label(" ")
        self.label_But_Space5 = gtk.Label(" ") 
        self.label_But_Space8 = gtk.Label(" ")
        self.label_But_Space9 = gtk.Label(" ")
        self.label_But_Space10 = gtk.Label(" ")      

        self.button_write = gtk.Button("Write to Config\nRegisters")
        self.button_write.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_write.set_size_request(-1,-1)        
        self.button_write.connect("clicked",self.write_vmmConfigRegisters)
        self.button_read_reg = gtk.Button("READ Config\nRegisters")
        self.button_read_reg.set_sensitive(False)
        self.button_read_reg.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_read_reg.set_size_request(-1,-1)
        self.button_read_reg.connect("clicked",self.read_reg)
        self.button_ext_trigger = gtk.Button("External Trigger")
        self.button_ext_trigger.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_ext_trigger.connect("clicked",self.ext_trigger)
        self.button_ext_trigger.set_size_request(-1,-1)
        #self.button_ext_trigger.set_sensitive(False)
        self.button_start_no_cktp = gtk.Button("Start No CKTP")
        self.button_start_no_cktp.set_sensitive(False)
        self.button_start_no_cktp.child.set_justify(gtk.JUSTIFY_CENTER)
        self.label_start_no_cktp = self.button_start_no_cktp.get_children()[0]
        #self.label_start_no_cktp.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('green'))
        self.button_start_no_cktp.set_size_request(-1,-1)
        self.button_start_no_cktp.connect("clicked",self.start_no_cktp)
        self.button_reset_fifo = gtk.Button("Rest DAQ FIFO")
        self.button_reset_fifo.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_reset_fifo.set_size_request(-1,-1)
        self.button_reset_fifo.set_sensitive(False)
        self.button_reset_fifo.connect("clicked",self.reset_fifo)
        self.button_print_config = gtk.Button("Print Config")
        self.button_print_config.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_print_config.set_size_request(-1,-1)
        self.button_print_config.connect("clicked",self.print_config)

        # Choose Board

        self.label_mmfe8_id = gtk.Label("mmfe8")
        self.label_mmfe8_id.set_markup('<span color="blue"><b>mmfe\nID</b></span>')
        self.label_mmfe8_id.set_justify(gtk.JUSTIFY_CENTER)
        self.entry_mmfeID = gtk.Entry(max=3)
        self.entry_mmfeID.set_text(str(self.mmfeID))
        self.entry_mmfeID.set_editable(False)
        
        self.label_IP = gtk.Label("IP ADDRESS")
        self.label_IP.set_markup('<span color="blue"><b>MMFE8\nIP ADDRESS</b></span>')
        self.label_IP.set_justify(gtk.JUSTIFY_CENTER)
        self.combo_IP = gtk.combo_box_new_text()
        self.combo_IP.append_text(self.ipAddr[0])      
        self.combo_IP.append_text(self.ipAddr[1])
        self.combo_IP.append_text(self.ipAddr[2])
        self.combo_IP.append_text(self.ipAddr[3])
        self.combo_IP.append_text(self.ipAddr[4])
        self.combo_IP.append_text(self.ipAddr[5])
        self.combo_IP.append_text(self.ipAddr[6])
        self.combo_IP.append_text(self.ipAddr[7])
        self.combo_IP.append_text(self.ipAddr[8])
        self.combo_IP.append_text(self.ipAddr[9])
        self.combo_IP.append_text(self.ipAddr[10])
        self.combo_IP.append_text(self.ipAddr[11])
        self.combo_IP.append_text(self.ipAddr[12])
        self.combo_IP.set_active(0)
        self.combo_IP.connect("changed",self.set_board_ip, self.entry_mmfeID) 


        self.label_vmm2_id = gtk.Label("vmm2")
        self.label_vmm2_id.set_markup('<span color="blue"><b>vmm\nto cfg</b></span>')
        self.label_vmm2_id.set_justify(gtk.JUSTIFY_CENTER)
        self.combo_vmm2_id = gtk.combo_box_new_text()
        self.combo_vmm2_id.append_text("0")
        self.combo_vmm2_id.append_text("1")
        self.combo_vmm2_id.append_text("2")
        self.combo_vmm2_id.append_text("3")
        self.combo_vmm2_id.append_text("4")
        self.combo_vmm2_id.append_text("5")
        self.combo_vmm2_id.append_text("6")
        self.combo_vmm2_id.append_text("7")

        #self.combo_vmm2_id.append_text("ALL")
        self.combo_vmm2_id.set_active(0)
        self.combo_vmm2_id.connect("changed",self.set_vmm_cfg_num)

        self.button_setIDs = gtk.Button("Set IDs")
        self.button_setIDs.child.set_justify(gtk.JUSTIFY_CENTER)
        self.button_setIDs.set_size_request(-1,-1)        
        self.button_setIDs.connect("clicked",self.set_IDs)
        
        self.label_mmfe8_id = gtk.Label("mmfe8")
        self.label_mmfe8_id.set_markup('<span color="blue"><b>mmfe8\nID</b></span>')
        self.label_mmfe8_id.set_justify(gtk.JUSTIFY_CENTER)
        self.label_Space20 = gtk.Label("   ")
        self.box_mmfeID = gtk.HBox()
        self.box_mmfeID.pack_start(self.label_mmfe8_id,expand=True)
        self.box_mmfeID.pack_start(self.entry_mmfeID,expand=False)

        self.label_mon_vmm_id = gtk.Label("vmm2")
        self.label_mon_vmm_id.set_markup('<span color="blue"><b>vmm\nto mon</b></span>')
        self.label_mon_vmm_id.set_justify(gtk.JUSTIFY_CENTER)
        self.combo_mon_vmm_id = gtk.combo_box_new_text()
        self.combo_mon_vmm_id.append_text("0")
        self.combo_mon_vmm_id.append_text("1")
        self.combo_mon_vmm_id.append_text("2")
        self.combo_mon_vmm_id.append_text("3")
        self.combo_mon_vmm_id.append_text("4")
        self.combo_mon_vmm_id.append_text("5")
        self.combo_mon_vmm_id.append_text("6")
        self.combo_mon_vmm_id.append_text("7")

        self.combo_mon_vmm_id.set_active(0)
        self.combo_mon_vmm_id.connect("changed",self.set_vmm_mon_num)

        self.label_Space21 = gtk.Label("    ")
        self.box_labelID = gtk.HBox()
        self.box_labelID.pack_start(self.label_Space20,expand=True) #
        self.box_labelID.pack_start(self.label_mon_vmm_id,expand=False)
        self.box_labelID.pack_start(self.label_Space21,expand=False)
        self.box_labelID.pack_start(self.label_vmm2_id,expand=False)

        self.label_Space22 = gtk.Label("  ")
        self.box_vmmID = gtk.HBox()
        self.box_vmmID.pack_start(self.button_setIDs,expand=True) #
        self.box_vmmID.pack_start(self.combo_mon_vmm_id,expand=False)
        self.box_vmmID.pack_start(self.label_Space22,expand=False)
        self.box_vmmID.pack_start(self.combo_vmm2_id,expand=False)

        """
        self.button_reset = gtk.Button("Reset")
        self.button_reset.set_sensitive(False)
        #self.button_reset.set_size_request(50,30)
        self.button_reset.connect("clicked",self.reset_params)
        """

        self.button_quick_set = gtk.Button("QUICK SET")
        self.button_quick_set.connect("clicked",self.quick_set)
        self.button_quick_set.set_sensitive(True)

        ###############################################
        ###################          ##################
        ################### channels ##################
        ###################          ##################
        ###############################################

        ###########################################################
        ##################### CHANNEL LABELS ######################
        ###########################################################

        self.label_Chan_num_a = gtk.Label("    \n   ")
        self.label_Chan_SP_a = gtk.Label("     S \n     P ")
        self.label_Chan_SP_a.set_markup('<span color="blue"><b>  S \n  P </b></span>')
        self.label_Chan_SC_a = gtk.Label("S\nC")
        self.label_Chan_SC_a.set_markup('<span color="blue"><b> S \n C </b></span>')
        self.label_Chan_ST_a = gtk.Label("S\nL")
        self.label_Chan_ST_a.set_markup('<span color="blue"><b> S \n L</b></span>')
        self.label_Chan_SL_a = gtk.Label("S\nT")
        self.label_Chan_SL_a.set_markup('<span color="blue"><b>  S \n  T </b></span>')
        self.label_Chan_SM_a = gtk.Label("S\nM")
        self.label_Chan_SM_a.set_markup('<span color="blue"><b> S    \n M     </b></span>')
        self.label_Chan_SD_a = gtk.Label("SD")
        self.label_Chan_SD_a.set_markup('<span color="blue"><b>  SD     </b></span>')
        self.label_Chan_SMX_a = gtk.Label("S\nM\nX")
        self.label_Chan_SMX_a.set_markup('<span color="blue"><b> S  \n M  \n X  </b></span>')
        self.label_Chan_SZ10b_a = gtk.Label("SZ10b")
        self.label_Chan_SZ10b_a.set_markup('<span color="blue"><b>  SZ10b   </b></span>')
        self.label_Chan_SZ8b_a = gtk.Label("SZ8b")
        self.label_Chan_SZ8b_a.set_markup('<span color="blue"><b>  SZ8b    </b></span>')
        self.label_Chan_SZ6b_a = gtk.Label("SZ6b")        
        self.label_Chan_SZ6b_a.set_markup('<span color="blue"><b>  SZ6b    </b></span>')

        self.box_chan_labels_a = gtk.HBox()
        self.box_chan_labels_a.pack_start(self.label_Chan_num_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SP_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SC_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_ST_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SL_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SM_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SD_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SMX_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SZ10b_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SZ8b_a)
        self.box_chan_labels_a.pack_start(self.label_Chan_SZ6b_a)

        self.label_Chan_num_b = gtk.Label("    \n   ")
        self.label_Chan_SP_b = gtk.Label("     S \n     P ")
        self.label_Chan_SP_b.set_markup('<span color="blue"><b>  S \n  P </b></span>')
        self.label_Chan_SC_b = gtk.Label(" S \n C ")
        self.label_Chan_SC_b.set_markup('<span color="blue"><b> S \n C </b></span>')
        self.label_Chan_ST_b = gtk.Label(" S \n L ")
        self.label_Chan_ST_b.set_markup('<span color="blue"><b> S \n L </b></span>')
        self.label_Chan_SL_b = gtk.Label(" S \n T ")
        self.label_Chan_SL_b.set_markup('<span color="blue"><b>  S \n  T </b></span>')
        self.label_Chan_SM_b = gtk.Label("S    \nM    ")
        self.label_Chan_SM_b.set_markup('<span color="blue"><b> S    \n M     </b></span>')
        self.label_Chan_SD_b = gtk.Label("  SD     ")
        self.label_Chan_SD_b.set_markup('<span color="blue"><b>  SD     </b></span>')
        self.label_Chan_SMX_b = gtk.Label(" S  \n M  \n X  ")
        self.label_Chan_SMX_b.set_markup('<span color="blue"><b> S  \n M  \n X  </b></span>')
        self.label_Chan_SZ10b_b = gtk.Label("  SZ10b   ")
        self.label_Chan_SZ10b_b.set_markup('<span color="blue"><b>  SZ10b   </b></span>')
        self.label_Chan_SZ8b_b = gtk.Label("  SZ8b    ")
        self.label_Chan_SZ8b_b.set_markup('<span color="blue"><b>  SZ8b    </b></span>')
        self.label_Chan_SZ6b_b = gtk.Label("  SZ6b    ")        
        self.label_Chan_SZ6b_b.set_markup('<span color="blue"><b>  SZ6b    </b></span>')

        self.box_chan_labels_b = gtk.HBox()
        self.box_chan_labels_b.pack_start(self.label_Chan_num_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SP_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SC_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_ST_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SL_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SM_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SD_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SMX_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SZ10b_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SZ8b_b)
        self.box_chan_labels_b.pack_start(self.label_Chan_SZ6b_b)

        ##########################################################
        ##################### CHANNEL BOXES ######################
        ##########################################################



        for ch_num in range(0, 66):
            #print ch_num,
            self.chan_list.append( channel(ch_num) )

            self.gbox = gtk.HBox(homogeneous=False,spacing=0)
            if ch_num < 10:
                self.glabel = gtk.Label( "  " + str(ch_num) )
            else:
                self.glabel = gtk.Label( str(ch_num) )
            #self.glabel.set_property( liststore
            self.button_SP = gtk.ToggleButton( label="n" )
            self.button_SC = gtk.CheckButton()
            self.button_SL = gtk.CheckButton()
            self.button_ST = gtk.CheckButton()
            self.button_SM = gtk.CheckButton()
            self.combo_SD = gtk.combo_box_new_text()
            self.button_SMX = gtk.CheckButton()
            self.combo_SZ10b = gtk.combo_box_new_text()
            self.combo_SZ8b = gtk.combo_box_new_text()
            self.combo_SZ6b = gtk.combo_box_new_text()

            for i in range(16):
                self.combo_SD.append_text(str(i) + " mv")
            self.combo_SD.set_active(0)
            #self.combo_SD.set_active(0)
            for i in range(32):
                self.combo_SZ10b.append_text(str(i) + " ns")        
            self.combo_SZ10b.set_active(0)
            for i in range(16):
                self.combo_SZ8b.append_text(str(i) + " ns")        
            self.combo_SZ8b.set_active(0)
            for i in range(8):
                self.combo_SZ6b.append_text(str(i) + " ns")        
            self.combo_SZ6b.set_active(0)

            
            self.button_SP.connect("toggled",self.SP_callback,ch_num)
            self.button_SC.connect("toggled",self.SC_callback,ch_num)
            self.button_SL.connect("toggled",self.SL_callback,ch_num)
            self.button_ST.connect("toggled",self.ST_callback,ch_num)
            self.button_SM.connect("toggled",self.SM_callback,ch_num)
            if ch_num < 65:
                self.button_SM.set_active(True)
            self.combo_SD.connect("changed",self.get_SD_value,ch_num)
            self.button_SMX.connect("toggled",self.SMX_callback,ch_num)
            self.combo_SZ10b.connect("changed",self.get_SZ10b_value,ch_num)
            self.combo_SZ8b.connect("changed",self.get_SZ8b_value,ch_num)
            self.combo_SZ6b.connect("changed",self.get_SZ6b_value,ch_num)

            self.gbox.pack_start(self.glabel,expand=False)
            self.gbox.pack_start(self.button_SP,expand=False)
            self.gbox.pack_start(self.button_SC,expand=False)
            self.gbox.pack_start(self.button_SL,expand=False)
            self.gbox.pack_start(self.button_ST,expand=False)
            self.gbox.pack_start(self.button_SM,expand=False)
            self.gbox.pack_start(self.combo_SD,expand=False)
            self.gbox.pack_start(self.button_SMX,expand=False)
            self.gbox.pack_start(self.combo_SZ10b,expand=False)
            self.gbox.pack_start(self.combo_SZ8b,expand=False)
            self.gbox.pack_start(self.combo_SZ6b,expand=False)

            self.chan_list[ch_num].add_object(self.gbox)
            self.chan_list[ch_num].add_object(self.glabel)
            self.chan_list[ch_num].add_object(self.button_SP)
            self.chan_list[ch_num].add_object(self.button_SC)
            self.chan_list[ch_num].add_object(self.button_SL)
            self.chan_list[ch_num].add_object(self.button_ST)
            self.chan_list[ch_num].add_object(self.button_SM)
            self.chan_list[ch_num].add_object(self.combo_SD)
            self.chan_list[ch_num].add_object(self.button_SMX)
            self.chan_list[ch_num].add_object(self.combo_SZ10b)
            self.chan_list[ch_num].add_object(self.combo_SZ8b)
            self.chan_list[ch_num].add_object(self.combo_SZ6b)

 

        #####################################################
        ##################                ###################   
        ##################   QUICK SET    ###################
        ##################                ###################
        #####################################################


        self.check_button_SP_qs = gtk.CheckButton()
        self.check_button_SC_qs = gtk.CheckButton()
        self.check_button_SL_qs = gtk.CheckButton()
        self.check_button_ST_qs = gtk.CheckButton()
        self.check_button_SM_qs = gtk.CheckButton()
        self.check_button_SD_qs = gtk.CheckButton()
        self.check_button_SMX_qs = gtk.CheckButton()

        self.toggle_button_SP = gtk.ToggleButton(label="n")
        self.toggle_button_SP.connect("toggled",self.SP_qs_callback)
        self.check_button_SC = gtk.CheckButton()
        self.check_button_SL = gtk.CheckButton()
        self.check_button_ST = gtk.CheckButton()
        self.check_button_SM = gtk.CheckButton()
        self.combo_SD_qs = gtk.combo_box_new_text()
        self.check_button_SMX = gtk.CheckButton()

        #self.label_Chan_num_qs = gtk.Label(" \n ")
        self.label_Chan_SP_qs = gtk.Label("SP")
        self.label_Chan_SC_qs = gtk.Label("SC")
        self.label_Chan_SL_qs = gtk.Label("SL")
        self.label_Chan_ST_qs = gtk.Label("ST")
        self.label_Chan_SM_qs = gtk.Label("SM")
        self.label_Chan_SD_qs = gtk.Label("SD")
        self.label_Chan_SMX_qs = gtk.Label("SMX")

        for i in range(16):
            self.combo_SD_qs.append_text(str(i) + " mv")
        self.combo_SD_qs.set_active(0)

        self.check_button_SP_qs.set_sensitive(True)
        self.check_button_SC_qs.set_sensitive(True)
        self.check_button_SL_qs.set_sensitive(True)
        self.check_button_ST_qs.set_sensitive(True)
        self.check_button_SM_qs.set_sensitive(True)
        self.check_button_SD_qs.set_sensitive(True)
        self.check_button_SMX_qs.set_sensitive(True)
        self.toggle_button_SP.set_sensitive(True)
        self.check_button_SC.set_sensitive(True)
        self.check_button_SL.set_sensitive(True)
        self.check_button_ST.set_sensitive(True)
        self.check_button_SM.set_sensitive(True)
        self.combo_SD_qs.set_sensitive(True)
        self.check_button_SMX.set_sensitive(True)


        self.qs_table = gtk.Table(rows=3, columns=7, homogeneous=False)
        self.qs_table.attach(self.label_Chan_SP_qs, left_attach=0, right_attach=1, top_attach=0, bottom_attach=1, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SP_qs, left_attach=0, right_attach=1, top_attach=1, bottom_attach=2, xpadding=5, ypadding=0)
        self.qs_table.attach(self.toggle_button_SP, left_attach=0, right_attach=1, top_attach=2, bottom_attach=3, xpadding=5, ypadding=0)
        self.qs_table.attach(self.label_Chan_SC_qs, left_attach=1, right_attach=2, top_attach=0, bottom_attach=1, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SC_qs, left_attach=1, right_attach=2, top_attach=1, bottom_attach=2, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SC, left_attach=1, right_attach=2, top_attach=2, bottom_attach=3, xpadding=5, ypadding=0)
        self.qs_table.attach(self.label_Chan_SL_qs, left_attach=2, right_attach=3, top_attach=0, bottom_attach=1, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SL_qs, left_attach=2, right_attach=3, top_attach=1, bottom_attach=2, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SL, left_attach=2, right_attach=3, top_attach=2, bottom_attach=3, xpadding=5, ypadding=0)
        self.qs_table.attach(self.label_Chan_ST_qs, left_attach=3, right_attach=4, top_attach=0, bottom_attach=1, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_ST_qs, left_attach=3, right_attach=4, top_attach=1, bottom_attach=2, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_ST, left_attach=3, right_attach=4, top_attach=2, bottom_attach=3, xpadding=5, ypadding=0)
        self.qs_table.attach(self.label_Chan_SM_qs, left_attach=4, right_attach=5, top_attach=0, bottom_attach=1, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SM_qs, left_attach=4, right_attach=5, top_attach=1, bottom_attach=2, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SM, left_attach=4, right_attach=5, top_attach=2, bottom_attach=3, xpadding=5, ypadding=0)
        self.qs_table.attach(self.label_Chan_SD_qs, left_attach=5, right_attach=6, top_attach=0, bottom_attach=1, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SD_qs, left_attach=5, right_attach=6, top_attach=1, bottom_attach=2, xpadding=5, ypadding=0)
        self.qs_table.attach(self.combo_SD_qs, left_attach=5, right_attach=6, top_attach=2, bottom_attach=3, xpadding=5, ypadding=0)
        self.qs_table.attach(self.label_Chan_SMX_qs, left_attach=6, right_attach=7, top_attach=0, bottom_attach=1, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SMX_qs, left_attach=6, right_attach=7, top_attach=1, bottom_attach=2, xpadding=5, ypadding=0)
        self.qs_table.attach(self.check_button_SMX, left_attach=6, right_attach=7, top_attach=2, bottom_attach=3, xpadding=5, ypadding=0)

        ####################################################
        #####################            ###################
        ##################### vmm Global ###################
        ##################### variables  ###################
        #####################            ###################
        ####################################################

        self.label_Global = gtk.Label("GLOBAL CONFIGURATION")
        self.label_Global.set_markup('<span color="blue" size="18000">      <b><u>GLOBAL CONFIGURATION</u></b></span>')
        self.label_Global.set_justify(gtk.JUSTIFY_CENTER)
        self.box_Global = gtk.HBox()
        self.box_Global.pack_start(self.label_Global, expand=False)

        self.check_button_SPG = gtk.CheckButton() 
        self.label_SPG = gtk.Label("Input Charge Polarity")
        self.label_SPG.set_markup('<span color="blue"><b>Input Charge Polarity   </b></span>')
        self.label_SPGa = gtk.Label(" spg")   
        self.check_button_SPG.connect("toggled", self.glob_SPG_callback)
        self.box_SPG = gtk.HBox()
        self.box_SPG.pack_start(self.label_SPG, expand=False) 
        self.box_SPG.pack_start(self.check_button_SPG, expand=False)
        self.box_SPG.pack_start(self.label_SPGa, expand=False)
            
        self.label_SBMX = gtk.Label("Route Analog Monitor to PDO Output")
        self.label_SBMX.set_markup('<span color="blue"><b>Route Analog Monitor to PDO Output   </b></span>')
        self.check_button_SBMX = gtk.CheckButton("")
        self.check_button_SBMX.connect("toggled", self.glob_SBMX_callback)
        self.check_button_SBMX.set_active(0)
        self.label_SBMXa = gtk.Label(" sbmx")
        self.box_SBMX = gtk.HBox()
        self.box_SBMX.pack_start(self.label_SBMX, expand=False)
        self.box_SBMX.pack_start(self.check_button_SBMX, expand=False)
        self.box_SBMX.pack_start(self.label_SBMXa, expand=False)

        self.label_SDP = gtk.Label("Disable-at-Peak")
        self.label_SDP.set_markup('<span color="blue"><b>Disable-at-Peak   </b></span>')
        self.check_button_SDP = gtk.CheckButton()
        self.check_button_SDP.connect("toggled", self.glob_SDPeak_callback)
        self.label_SDPa = gtk.Label(" sdp")
        self.box_SDP = gtk.HBox()
        self.box_SDP.pack_start(self.label_SDP, expand=False)
        self.box_SDP.pack_start(self.check_button_SDP, expand=False)
        self.box_SDP.pack_start(self.label_SDPa, expand=False)

        self.label_SBXX = gtk.Label("Analog Output Buffers:")
        self.label_SBXX.set_markup('<span color="blue"><b>Analog Output Buffers   </b></span>')
        self.check_button_SBFT = gtk.CheckButton("TDO")
        self.check_button_SBFT.connect("toggled", self.glob_SBFT_callback)
        self.check_button_SBFT.set_active(1)
        self.check_button_SBFP = gtk.CheckButton("PDO")
        self.check_button_SBFP.connect("toggled", self.glob_SBFP_callback)
        self.check_button_SBFP.set_active(1)
        self.check_button_SBFM = gtk.CheckButton("MO")
        self.check_button_SBFM.connect("toggled", self.glob_SBFM_callback)
        self.check_button_SBFM.set_active(1)
        self.box_SBXX = gtk.HBox()
        self.box_SBXX.pack_start(self.label_SBXX, expand=False)
        self.box_SBXX.pack_start(self.check_button_SBFT, expand=False)
        self.box_SBXX.pack_start(self.check_button_SBFP, expand=False)
        self.box_SBXX.pack_start(self.check_button_SBFM, expand=False)
        
        self.check_button_SLG = gtk.CheckButton() 
        self.label_SLG = gtk.Label("Leakage Current Disable")
        self.label_SLG.set_markup('<span color="blue"><b>Leakage Current Disable   </b></span>')   
        self.check_button_SLG.connect("toggled", self.glob_SLG_callback)
        self.label_SLGa = gtk.Label(" slg")
        self.box_SLG = gtk.HBox()
        self.box_SLG.pack_start(self.label_SLG, expand=False) 
        self.box_SLG.pack_start(self.check_button_SLG, expand=False)
        self.box_SLG.pack_start(self.label_SLGa, expand=False)

        self.label_SM = gtk.Label("   Monitor")
        self.label_SM.set_markup('<span color="blue"><b>   Monitor   </b></span>')
        self.combo_SM = gtk.combo_box_new_text()
        self.combo_SM.connect("changed", self.glob_SM_value)
        self.combo_SM.append_text("CHN 1")
        self.combo_SM.append_text("CHN 2 | pulser DAC")
        self.combo_SM.append_text("CHN 3 | threshold DAC")
        self.combo_SM.append_text("CHN 4 | band-gap ref")
        self.combo_SM.append_text("CHN 5 | temp")
        for i in range(5, 64):
            self.combo_SM.append_text("CHN " + str(i+1))
        self.combo_SM.set_active(8)
        self.label_SCMX = gtk.Label(" scmx")
        self.label_SCMX.set_markup('<span color="blue"><b>SCMX   </b></span>')
        self.check_button_SCMX = gtk.CheckButton()   
        self.check_button_SCMX.connect("toggled", self.glob_SCMX_callback)
        self.check_button_SCMX.set_active(1)
        self.box_SCMX = gtk.HBox()
        self.box_SCMX.pack_start(self.label_SCMX, expand=False)
        self.box_SCMX.pack_start(self.check_button_SCMX, expand=False)
        self.box_SCMX.pack_start(self.label_SM, expand=False) 
        self.box_SCMX.pack_start(self.combo_SM, expand=False)

        self.label_SFA = gtk.Label("ART Enable")
        self.label_SFA.set_markup('<span color="blue"><b>ART Enable   </b></span>')    
        self.check_button_SFA = gtk.CheckButton()
        self.check_button_SFA.connect("toggled",self.glob_SFA_callback)
        self.check_button_SFA.set_active(True)
        self.label_SFAa = gtk.Label(" sfa")
        self.label_mode_SFAM = gtk.Label("  Mode    ")
        self.label_mode_SFAM.set_markup('<span color="blue"><b>  Mode    </b></span>')
        self.combo_SFAM = gtk.combo_box_new_text()
        self.combo_SFAM.connect("changed",self.glob_SFAM_value)
        self.combo_SFAM.append_text("timing-at-threshold")      
        self.combo_SFAM.append_text("timing-at-peak")
        self.combo_SFAM.set_active(0)
        self.label_SFAM = gtk.Label(" sfam")
        self.box_SFAM = gtk.HBox()
        self.box_SFAM.pack_start(self.label_SFA, expand=False)
        self.box_SFAM.pack_start(self.check_button_SFA, expand=False)
        self.box_SFAM.pack_start(self.label_SFAa, expand=False)
        self.box_SFAM.pack_start(self.label_mode_SFAM, expand=False)
        self.box_SFAM.pack_start(self.combo_SFAM, expand=False)
        self.box_SFAM.pack_start(self.label_SFAM, expand=False)

        self.label_Var_DC = gtk.Label("Delay Counts")
        self.label_Var_DC.set_markup('<span color="blue"><b> Delay Counts   </b></span>')
        self.combo_DC = gtk.combo_box_new_text()
        self.combo_DC.connect("changed",self.glob_DC_value)
        self.combo_DC.append_text("0")
        self.combo_DC.append_text("1")
        self.combo_DC.append_text("2")
        self.combo_DC.append_text("3")
        self.combo_DC.append_text("4")
        self.combo_DC.set_active(0)
        self.label_DC = gtk.Label(" st")
        self.box_DC = gtk.HBox()
        self.box_DC.pack_start(self.label_Var_DC, expand=False)
        self.box_DC.pack_start(self.combo_DC, expand=False)
        self.box_DC.pack_start(self.label_DC, expand=False)


        self.label_Var_ST = gtk.Label("Peaking Time")
        self.label_Var_ST.set_markup('<span color="blue"><b>Peaking Time   </b></span>')
        self.combo_ST = gtk.combo_box_new_text()
        self.combo_ST.connect("changed",self.glob_ST_value)
        self.combo_ST.append_text("200 ns")
        self.combo_ST.append_text("100 ns")
        self.combo_ST.append_text("50 ns")
        self.combo_ST.append_text("25 ns")
        self.combo_ST.set_active(0)
        self.label_ST = gtk.Label(" st")
        self.box_ST = gtk.HBox()
        self.box_ST.pack_start(self.label_Var_ST, expand=False)
        self.box_ST.pack_start(self.combo_ST, expand=False)
        self.box_ST.pack_start(self.label_ST, expand=False)

        self.check_button_SFM = gtk.CheckButton()
        self.label_SFM = gtk.Label("SFM")
        self.label_SFM.set_markup('<span color="blue"><b>SFM   </b></span>')   
        self.check_button_SFM.connect("toggled", self.glob_SFM_callback)
        self.check_button_SFM.set_active(1)
        self.label_SFMb = gtk.Label("  Doubles the Leakage Current")
        self.label_SFMb.set_markup('<span color="blue"><b>  (Doubles the Leakage Current)</b></span>')        
        self.box_SFM = gtk.HBox()
        self.box_SFM.pack_start(self.label_SFM, expand=False) 
        self.box_SFM.pack_start(self.check_button_SFM, expand=False)
        self.box_SFM.pack_start(self.label_SFMb, expand=False)

        self.label_Var_SG = gtk.Label("Gain")
        self.label_Var_SG.set_markup('<span color="blue"><b>Gain   </b></span>')
        self.combo_SG = gtk.combo_box_new_text()
        self.combo_SG.connect("changed",self.glob_SG_value)
        self.combo_SG.append_text("0.5 (000)")     
        self.combo_SG.append_text("1 (001)")
        self.combo_SG.append_text("3 (010)")
        self.combo_SG.append_text("4.5 (011)")
        self.combo_SG.append_text("6 (100)")
        self.combo_SG.append_text("9 (101)")
        self.combo_SG.append_text("12 (110)")
        self.combo_SG.append_text("16 (111)")
        self.combo_SG.set_active(5)
        self.label_SG = gtk.Label(" (mV/fC)    sg")
        self.box_SG = gtk.HBox()
        self.box_SG.pack_start(self.label_Var_SG, expand=False)
        self.box_SG.pack_start(self.combo_SG, expand=False)
        self.box_SG.pack_start(self.label_SG, expand=False)

        self.check_button_SNG = gtk.CheckButton() 
        self.label_SNG = gtk.Label("Neighbor Triggering")
        self.label_SNG.set_markup('<span color="blue"><b>Neighbor Triggering   </b></span>')    
        self.check_button_SNG.connect("toggled",self.glob_SNG_callback)
        self.label_SNGa = gtk.Label(" sng")
        self.box_SNG = gtk.HBox()
        self.box_SNG.pack_start(self.label_SNG, expand=False) 
        self.box_SNG.pack_start(self.check_button_SNG,expand=False)
        self.box_SNG.pack_start(self.label_SNGa, expand=False) 

        self.label_STTT = gtk.Label("Timing Outputs")
        self.label_STTT.set_markup('<span color="blue"><b>Timing Outputs </b></span>')
        self.check_button_STTT = gtk.CheckButton()
        self.check_button_STTT.connect("toggled",self.glob_STTT_callback)
        self.label_STTTa = gtk.Label(" sttt")
        self.label_mode_STOT = gtk.Label("  Mode    ")
        self.label_mode_STOT.set_markup('<span color="blue"><b>  Mode  </b></span>')
        self.combo_STOT = gtk.combo_box_new_text()
        self.combo_STOT.connect("changed",self.glob_STOT_value)      
        self.combo_STOT.append_text("threshold-to-peak")
        self.combo_STOT.append_text("time-over-threshold")
        self.combo_STOT.append_text("pulse-at-peak (10ns)")
        self.combo_STOT.append_text("peak-to-threshold")
        self.combo_STOT.set_active(0)        
        self.label_STOT = gtk.Label(" stot")
        self.box_STXX = gtk.HBox()
        self.box_STXX.pack_start(self.label_STTT, expand=False)                
        self.box_STXX.pack_start(self.check_button_STTT, expand=False)
        self.box_STXX.pack_start(self.label_STTTa, expand=False)
        self.box_STXX.pack_start(self.label_mode_STOT, expand=False)
        self.box_STXX.pack_start(self.combo_STOT, expand=False)
        self.box_STXX.pack_start(self.label_STOT, expand=False)

        self.label_SSH = gtk.Label("Sub-Hysteresis\nDiscrimination")    
        self.label_SSH.set_markup('<span color="blue"><b>Sub-Hysteresis   \nDiscrimination</b></span>')
        self.check_button_SSH = gtk.CheckButton()
        self.check_button_SSH.connect("toggled", self.glob_SSH_callback)
        self.label_SSHa = gtk.Label(" ssh")
        self.box_SSH = gtk.HBox()
        self.box_SSH.pack_start(self.label_SSH, expand=False)        
        self.box_SSH.pack_start(self.check_button_SSH, expand=False)
        self.box_SSH.pack_start(self.label_SSHa, expand=False)

        self.label_STPP = gtk.Label("Timing Outputs Control 2")    
        self.label_STPP.set_markup('<span color="blue"><b>Timing Outputs Control 2   </b></span>')
        self.check_button_STPP = gtk.CheckButton()
        self.check_button_STPP.connect("toggled", self.glob_STPP_callback)
        self.label_STPPa = gtk.Label(" stpp")
        self.box_STPP = gtk.HBox()
        self.box_STPP.pack_start(self.label_STPP, expand=False)        
        self.box_STPP.pack_start(self.check_button_STPP, expand=False)
        self.box_STPP.pack_start(self.label_STPPa, expand=False)

        self.label_Var_STC = gtk.Label("TAC Slope")
        self.label_Var_STC.set_markup('<span color="blue"><b>TAC Slope   </b></span>')              
        self.combo_STC = gtk.combo_box_new_text()
        self.combo_STC.connect("changed", self.glob_STC_value)
        self.combo_STC.append_text("125 ns (00)")        
        self.combo_STC.append_text("250 ns (01)")
        self.combo_STC.append_text("500 ns (10)")
        self.combo_STC.append_text("1000 ns (11)")
        self.combo_STC.set_active(2)
        self.label_STC = gtk.Label(" stc")
        self.box_STC = gtk.HBox()
        self.box_STC.pack_start(self.label_Var_STC, expand=False)
        self.box_STC.pack_start(self.combo_STC, expand=False)
        self.box_STC.pack_start(self.label_STC, expand=False)

        self.label_Var_SDT = gtk.Label("Threshold DAC")
        self.label_Var_SDT.set_markup('<span color="blue"><b>Threshold DAC   </b></span>')
        self.entry_SDT = gtk.Entry(max=4)
        self.entry_SDT.set_text("300")
        self.entry_SDT.connect("focus-out-event", self.glob_SDT_entry)
        self.entry_SDT.connect("activate", self.glob_SDT_entry, self.entry_SDT)
        #self.label_Var_SDTb = gtk.Label("Press Enter to SET")
        #self.label_Var_SDTb.set_markup('<span color="red"><b>  <u>PRESS &lt;ENTER&gt;</u> to SET</b></span>')        
        # self.combo_SDT = gtk.combo_box_new_text()
        # for i in range(1024):
            # self.combo_SDT.append_text(str(i))
        # self.combo_SDT.set_active(0)
        self.label_SDT = gtk.Label()
        self.box_SDT = gtk.HBox()
        self.box_SDT.pack_start(self.label_Var_SDT, expand=False)
        self.box_SDT.pack_start(self.entry_SDT, expand=False)
        #self.box_SDT.pack_start(self.combo_SDT)
        self.box_SDT.pack_start(self.label_SDT, expand=False)
        #self.box_SDT.pack_start(self.label_Var_SDTb, expand=False)

        self.label_Var_SDP_ = gtk.Label("Test Pulse DAC")
        self.label_Var_SDP_.set_markup('<span color="blue"><b>Test Pulse DAC   </b></span>')
        self.entry_SDP_ = gtk.Entry(max=4)
        self.entry_SDP_.set_text("300")
        self.entry_SDP_.connect("focus-out-event", self.glob_SDP_entry ) #,self.entry_SDP_
        self.entry_SDP_.connect("activate", self.glob_SDP_entry, self.entry_SDP_)

        #self.label_Var_SDP_b = gtk.Label("Press Enter to SET")
        #self.label_Var_SDP_b.set_markup('<span color="red"><b>  <u>PRESS &lt;ENTER&gt;</u> to SET</b></span>') 
        self.label_SDP_ = gtk.Label()
        self.box_SDP_ = gtk.HBox()
        self.box_SDP_.pack_start(self.label_Var_SDP_,expand=False)
        self.box_SDP_.pack_start(self.entry_SDP_,expand=False)
        self.box_SDP_.pack_start(self.label_SDP_,expand=False)
        #self.box_SDP_.pack_start(self.label_Var_SDP_b,expand=False)

        self.label_variable1 = gtk.Label("  \n   ")
        self.label_variable2 = gtk.Label("  \n   ")
        self.label_variable3 = gtk.Label("  \n   ")
        self.label_variable4 = gtk.Label("  \n   ") 
        self.label_variable5 = gtk.Label("   ")
        self.label_variable6 = gtk.Label("Values for Threshold and Test Pulse :") 
        self.label_variable6.set_markup('<span color="purple"><b>Values for Threshold and Test Pulse :</b></span>') 
        self.label_variable7 = gtk.Label("  \n  ")
        self.label_variable9 = gtk.Label("  \n  ") 
        self.label_variable10 = gtk.Label("  0 <= x <= 1023")
        self.label_variable11 = gtk.Label(" ")
        self.label_variable12 = gtk.Label("to Set the Values for SDT and SDP_")
        self.label_variable12.set_markup('<span color="purple">to <b>Set</b> the Values for <b>SDT</b> and <b>SDP_</b></span>')
        self.box_SDP_SDT = gtk.HBox()
        self.box_SDP_SDT.pack_start(self.label_variable6,expand=False)
        self.box_SDP_SDT.pack_start(self.label_variable10,expand=False)

        self.label_Var_SC10b = gtk.Label("10-bit Conversion Time")
        self.label_Var_SC10b.set_markup('<span color="blue"><b>10-bit Conversion Time   </b></span>')
        self.combo_SC10b = gtk.combo_box_new_text()
        self.combo_SC10b.connect("changed", self.glob_SC10b_value)
        self.combo_SC10b.append_text("0 ns (00)")
        self.combo_SC10b.append_text("1 ns (10)")
        self.combo_SC10b.append_text("2 ns (01)")
        self.combo_SC10b.append_text("3 ns (11)")
        self.combo_SC10b.set_active(0)
        self.label_SC10b = gtk.Label(" sc10b")
        self.box_SC10b = gtk.HBox()
        self.box_SC10b.pack_start(self.label_Var_SC10b, expand=False)
        self.box_SC10b.pack_start(self.combo_SC10b, expand=False)
        self.box_SC10b.pack_start(self.label_SC10b, expand=False)

        self.label_Var_SC8b = gtk.Label("8-bit Conversion Time")
        self.label_Var_SC8b.set_markup('<span color="blue"><b>8-bit Conversion Time   </b></span>')
        self.combo_SC8b = gtk.combo_box_new_text()
        self.combo_SC8b.connect("changed", self.glob_SC8b_value)
        self.combo_SC8b.append_text("0 ns (00)")
        self.combo_SC8b.append_text("1 ns (10)")
        self.combo_SC8b.append_text("2 ns (01)")
        self.combo_SC8b.append_text("3 ns (11)")
        self.combo_SC8b.set_active(0)
        self.label_SC8b = gtk.Label(" sc8b")
        self.box_SC8b = gtk.HBox()
        self.box_SC8b.pack_start(self.label_Var_SC8b, expand=False)
        self.box_SC8b.pack_start(self.combo_SC8b, expand=False)
        self.box_SC8b.pack_start(self.label_SC8b, expand=False)

        self.label_Var_SC6b = gtk.Label("6-bit Conversion Time")
        self.label_Var_SC6b.set_markup('<span color="blue"><b>6-bit Conversion Time   </b></span>')
        self.combo_SC6b = gtk.combo_box_new_text()
        self.combo_SC6b.connect("changed", self.glob_SC6b_value)
        self.combo_SC6b.append_text("0 ns (000)")
        self.combo_SC6b.append_text("1 ns (100)")
        self.combo_SC6b.append_text("2 ns (010)")
        self.combo_SC6b.append_text("3 ns (110)")
        self.combo_SC6b.append_text("4 ns (001)")
        self.combo_SC6b.append_text("5 ns (101)")
        self.combo_SC6b.append_text("6 ns (011)")
        self.combo_SC6b.append_text("7 ns (111)")
        self.combo_SC6b.set_active(0)
        self.label_Var_SC6ba = gtk.Label(" sc6b")
        self.box_SC6b = gtk.HBox()
        self.box_SC6b.pack_start(self.label_Var_SC6b, expand=False)
        self.box_SC6b.pack_start(self.combo_SC6b, expand=False)
        self.box_SC6b.pack_start(self.label_Var_SC6ba, expand=False)

        self.label_S6b = gtk.Label("6-bit ADC Enable")
        self.label_S6b.set_markup('<span color="blue"><b>6-bit ADC Enable   </b></span>')
        self.check_button_S6b = gtk.CheckButton()   
        self.check_button_S6b.connect("toggled", self.glob_S6b_callback)
        self.check_button_S6b.set_active(False)
        self.label_S6ba = gtk.Label("Disables 8 & 10 bit ADC")
        self.label_S6ba.set_markup('<span color="blue"><b>  (Disables 8 &amp; 10 bit ADC)</b></span>')
        self.label_S6bb = gtk.Label(" s6b")
        self.box_S6b = gtk.HBox()
        self.box_S6b.pack_start(self.label_S6b, expand=False)
        self.box_S6b.pack_start(self.check_button_S6b, expand=False)
        self.box_S6b.pack_start(self.label_S6ba, expand=False)
        self.box_S6b.pack_start(self.label_S6bb, expand=False)

        self.label_Var_S8b = gtk.Label("8-bit ADC Mode")
        self.label_Var_S8b.set_markup('<span color="blue"><b>8-bit ADC Mode   </b></span>')
        self.combo_S8b = gtk.CheckButton()
        self.combo_S8b.connect("toggled", self.glob_S8b_callback)
        self.combo_S8b.set_active(1)
        self.label_Var_S8ba = gtk.Label(" s8b")
        self.box_S8b = gtk.HBox()
        self.box_S8b.pack_start(self.label_Var_S8b, expand=False)
        self.box_S8b.pack_start(self.combo_S8b, expand=False)
        self.box_S8b.pack_start(self.label_Var_S8ba, expand=False)

        self.label_Var_SPDC = gtk.Label("ADCs Enable")
        self.label_Var_SPDC.set_markup('<span color="blue"><b>ADCs Enable   </b></span>')
        self.button_SPDC = gtk.CheckButton()
        self.button_SPDC.connect("toggled", self.glob_SPDC_callback)
        self.button_SPDC.set_active(1)
        self.label_Var_SPDCa = gtk.Label(" spdc")
        self.box_SPDC = gtk.HBox()
        self.box_SPDC.pack_start(self.label_Var_SPDC, expand=False)
        self.box_SPDC.pack_start(self.button_SPDC, expand=False)
        self.box_SPDC.pack_start(self.label_Var_SPDCa, expand=False)

        self.label_SDCKS = gtk.Label("Dual Clock Edge\nSerialized Data Enable\n")    
        self.label_SDCKS.set_markup('<span color="blue"><b>Dual Clock Edge\nSerialized Data Enable\n   </b></span>')
        self.check_button_SDCKS = gtk.CheckButton()
        self.check_button_SDCKS.connect("toggled", self.glob_SDCKS_callback)
        self.label_SDCKSa = gtk.Label(" sdcks")
        self.box_SDCKS = gtk.HBox()
        self.box_SDCKS.pack_start(self.label_SDCKS, expand=False)        
        self.box_SDCKS.pack_start(self.check_button_SDCKS, expand=False)
        self.box_SDCKS.pack_start(self.label_SDCKSa, expand=False)

        self.label_SDCKA = gtk.Label("Dual Clock Edge\nSerialized ART Enable\n")    
        self.label_SDCKA.set_markup('<span color="blue"><b>Dual Clock Edge\nSerialized ART Enable\n   </b></span>')
        self.check_button_SDCKA = gtk.CheckButton()
        self.check_button_SDCKA.connect("toggled", self.glob_SDCKA_callback)
        self.label_SDCKAa = gtk.Label(" sdcka")
        self.box_SDCKA = gtk.HBox()
        self.box_SDCKA.pack_start(self.label_SDCKA, expand=False)        
        self.box_SDCKA.pack_start(self.check_button_SDCKA, expand=False)
        self.box_SDCKA.pack_start(self.label_SDCKAa, expand=False)

        self.label_SDCK6b = gtk.Label("Dual Clock Edge\nSerialized 6-bit Enable\n")    
        self.label_SDCK6b.set_markup('<span color="blue"><b>Dual Clock Edge\nSerialized 6-bit Enable\n    </b></span>')
        self.check_button_SDCK6b = gtk.CheckButton()
        self.check_button_SDCK6b.connect("toggled", self.glob_SDCK6b_callback)
        self.label_SDCK6ba = gtk.Label(" sdck6b")
        self.box_SDCK6b = gtk.HBox()
        self.box_SDCK6b.pack_start(self.label_SDCK6b, expand=False)        
        self.box_SDCK6b.pack_start(self.check_button_SDCK6b, expand=False)
        self.box_SDCK6b.pack_start(self.label_SDCK6ba, expand=False)

        self.label_SDRV = gtk.Label("Tristates Analog Outputs")    
        self.label_SDRV.set_markup('<span color="blue"><b>Tristates Analog Outputs   </b></span>')
        self.check_button_SDRV = gtk.CheckButton()
        self.check_button_SDRV.connect("toggled", self.glob_SDRV_callback)
        self.check_button_SDRV.set_active(0)
        self.label_SDRVa = gtk.Label(" sdrv")
        self.box_SDRV = gtk.HBox()
        self.box_SDRV.pack_start(self.label_SDRV, expand=False)        
        self.box_SDRV.pack_start(self.check_button_SDRV, expand=False)
        self.box_SDRV.pack_start(self.label_SDRVa, expand=False)

        self.box_var_labels = gtk.VBox()
        self.box_var_labels.set_border_width(10)
        self.box_var_labels.pack_start(self.label_variable1)
        self.box_var_labels.pack_start(self.label_variable2)
        self.box_var_labels.pack_start(self.label_variable3)
        self.frame_qs = gtk.Frame()
        self.frame_qs.set_shadow_type(gtk.SHADOW_OUT)
        self.frame_qs.set_label("QUICK SET")
        self.frame_qs.set_label_align(0.5,0.0)
        self.box_quick_set = gtk.VBox(homogeneous=False,spacing=0)
        self.box_quick_set.set_border_width(20)
        self.qs_label = gtk.Label("QUICK SET")
        self.box_quick_set.pack_start(self.qs_table)
        self.box_quick_set.pack_end(self.button_quick_set)                
        self.frame_qs.add(self.box_quick_set)

        self.label_But_Space6 = gtk.Label(" ")
        self.label_But_Space7 = gtk.Label(" ")

        self.box_variables = gtk.VBox()
        self.box_variables.set_border_width(5)
        self.box_variables.pack_start(self.box_Global, expand=False)
        self.box_variables.pack_start(self.label_But_Space6, expand=False)
        self.box_variables.pack_start(self.label_But_Space7, expand=False)
        self.box_variables.pack_start(self.box_SPG, expand=False)
        self.box_variables.pack_start(self.box_SDP, expand=False)
        self.box_variables.pack_start(self.box_SBMX, expand=False)
        self.box_variables.pack_start(self.box_SBXX, expand=False)
        self.box_variables.pack_start(self.box_SLG, expand=False)
        self.box_variables.pack_start(self.box_SCMX, expand=False)
        self.box_variables.pack_start(self.box_SFAM, expand=False)
        self.box_variables.pack_start(self.box_ST, expand=False)
        self.box_variables.pack_start(self.box_DC, expand=False)
        self.box_variables.pack_start(self.box_SFM, expand=False)

        self.box_variables.pack_start(self.box_SG, expand=False)
        self.box_variables.pack_start(self.box_SNG, expand=False)
        self.box_variables.pack_start(self.box_STXX, expand=False)

        self.box_variables.pack_start(self.box_SSH, expand=False)
        self.box_variables.pack_start(self.box_STC, expand=False)

        self.box_variables.pack_start(self.box_SC10b, expand=False)
        self.box_variables.pack_start(self.box_S8b, expand=False)
        self.box_variables.pack_start(self.box_SC8b, expand=False)
        self.box_variables.pack_start(self.box_S6b, expand=False)
        self.box_variables.pack_start(self.box_SC6b, expand=False)
        self.box_variables.pack_start(self.box_SPDC, expand=False)
        
        self.box_variables.pack_start(self.box_SDCKS, expand=False)
        self.box_variables.pack_start(self.box_SDCKA, expand=False)
        self.box_variables.pack_start(self.box_SDCK6b, expand=False)
        self.box_variables.pack_start(self.box_SDRV, expand=False)
        self.box_variables.pack_start(self.box_STPP, expand=False)

        self.box_variables.pack_start(self.label_variable5,expand=False)
        self.box_variables.pack_start(self.label_variable11,expand=False)
        self.box_variables.pack_start(self.box_SDT,expand=False)
        self.box_variables.pack_start(self.box_SDP_,expand=False)
        self.box_variables.pack_start(self.box_SDP_SDT,expand=False)
        self.box_variables.pack_start(self.label_variable12,expand=False)
        self.box_variables.pack_start(self.label_variable9)
        self.box_variables.pack_end(self.frame_qs,expand=False) 


        ###########################################################
        ###########################################################
        ########################   FRAME 1   ######################
        ###########################################################
        ###########################################################


        self.box_buttons = gtk.VBox()
        self.box_buttons.set_border_width(5)
        self.box_buttons.set_size_request(-1,-1)
        self.box_buttons.pack_start(self.label_But_Space9,expand=True)
        self.box_buttons.pack_start(self.label_IP,expand=False)
        self.box_buttons.pack_start(self.combo_IP,expand=False)
        self.box_buttons.pack_start(self.box_mmfeID,expand=False)
        self.box_buttons.pack_start(self.box_labelID,expand=False)
        self.box_buttons.pack_start(self.box_vmmID,expand=False)
        self.box_buttons.pack_start(self.label_But_Space8,expand=True)  
        self.box_buttons.pack_start(self.button_print_config,expand=False)
        self.box_buttons.pack_start(self.button_write,expand=False)
        self.box_buttons.pack_start(self.label_But_Space3,expand=True)
        self.box_buttons.pack_start(self.button_resetVMM,expand=False)
        self.box_buttons.pack_start(self.button_pulse,expand=False)
        self.box_buttons.pack_start(self.button_ext_trigger,expand=False)
        self.box_buttons.pack_start(self.button_start,expand=False)
        self.box_buttons.pack_start(self.button_start_no_cktp,expand=False)
        # self.box_buttons.pack_start(self.button_read_reg,expand=False)
        self.box_buttons.pack_start(self.label_But_Space4,expand=True)
        # self.box_buttons.pack_start(self.button_read_config_VMM_reg,expand=False)
        self.box_buttons.pack_start(self.button_reset_fifo,expand=False)
        self.box_buttons.pack_start(self.button_clear_data_file,expand=False)
        self.box_buttons.pack_start(self.label_But_Space5,expand=True)
        self.box_buttons.pack_start(self.button_exit,expand=False)                       
        self.box_buttons.pack_start(self.label_But_Space2,expand=True)
        self.box_buttons.pack_start(self.label_But_Space1,expand=True)



                                
        #################################################
        ###################                 #############
        ################### CHANNELS FRAMES #############   
        ###################                 #############   
        #################################################
        
        self.frame_2_a = gtk.Frame()
        self.frame_2_a.set_border_width(4)
        self.frame_2_a.set_shadow_type(gtk.SHADOW_IN)   
        self.box_channels_1a = gtk.VBox(homogeneous=False,spacing=0)
        self.box_channels_a = gtk.VBox(homogeneous=True,spacing=0)
        for ch_num in range(1, 33):
            self.box_channels_a.pack_start(self.chan_list[ch_num].chan_obj_list[0])

        self.box_channels_1a.pack_start(self.box_chan_labels_a,expand=False)        
        self.box_channels_1a.pack_start(self.box_channels_a,expand=False)
        self.frame_2_a.add(self.box_channels_1a)

        self.frame_2_b = gtk.Frame()
        self.frame_2_b.set_border_width(4)
        self.frame_2_b.set_shadow_type(gtk.SHADOW_IN)

        self.box_channels_1b = gtk.VBox(homogeneous=False,spacing=0)

        self.box_channels_b = gtk.VBox(homogeneous=True,spacing=0)

        for ch_num in range(33, 65):
            self.box_channels_b.pack_start(self.chan_list[ch_num].chan_obj_list[0])

        self.box_channels_1b.pack_start(self.box_chan_labels_b,expand=False)        
        self.box_channels_1b.pack_start(self.box_channels_b,expand=False)
        self.frame_2_b.add(self.box_channels_1b)



        #################################################
        ###############                     #############
        ############### END CHANNELS FRAMES #############       
        ###############                     #############
        #################################################


        self.box_all_channels = gtk.HBox()
        self.box_all_channels.pack_start(self.frame_2_a)
        self.box_all_channels.pack_start(self.frame_2_b)

        self.page1_box = gtk.HBox(homogeneous=0,spacing=0)
        self.page1_box.pack_start(self.box_buttons, expand=False)        
	self.page1_box.pack_start(self.box_all_channels, expand=False)
        self.page1_box.pack_end(self.box_variables, expand=True)

        ##====================== Page 2 =======================## 
        
        self.page2_box = gtk.VBox(homogeneous=False)
        #self.page2_box.pack_start(self.page2_table, expand=True)
                
        
        ##====================== Page 3 =======================##
        self.page3_box = gtk.VBox(homogeneous=False)
        self.page3_table = gtk.Table(rows=4, columns=4, homogeneous=False)
        self.page3_table.set_row_spacings(10)
        self.page3_table.set_col_spacings(10)

        self.page3_topfiller_label_1 = gtk.Label("")
        self.page3_topfiller_label_1a = gtk.Label("")
        self.page3_topfiller_label_2 = gtk.Label(" Registers\n(press buttons to activate)")
        self.page3_topfiller_label_2.set_markup('<span color="blue" size="24000" ><b> Registers</b></span>\n<span><b>(press buttons to activate)</b></span>')
        self.page3_bottomfiller_label_3 = gtk.Label("")
        self.page3_bottomfiller_label_4 = gtk.Label("")
        self.page3_top = gtk.VBox(homogeneous=True,spacing=0)
        self.page3_top.pack_start(self.page3_topfiller_label_1,expand=True)
        self.page3_top.pack_start(self.page3_topfiller_label_1a,expand=True)
        self.page3_top.pack_start(self.page3_topfiller_label_2,expand=True)
        self.page3_bottom = gtk.VBox(homogeneous=True,spacing=0)
        self.page3_bottom.pack_start(self.page3_bottomfiller_label_3,expand=True)
        self.page3_bottom.pack_start(self.page3_bottomfiller_label_4,expand=True)
        self.page3_leftfiller_label = gtk.Label("41-Bit FIFO CTRL/STATUS\n    (0x44A1_0182)\n------------------------------ \
                \nWRITE\nBit 3 = FIFO41 reset\nBit 5 = FIFO38 read enable\n\nREAD\nBit 0 = almost empty\nBit 1 = empty \
                \nBit 2 = almost full\nBit 3 = full")
        self.page3_leftfiller_label.set_markup('<span color="blue"><b>38-Bit FIFO CTRL/STATUS</b></span>\n<span>    (0x44A1_0082)\n<b>------------------------------</b> \
                \nWRITE\nBit 3 = FIFO41 reset\nBit 5 = FIFO38 read enable\n\nREAD\nBit 0 = almost empty\nBit 1 = empty \
                \nBit 2 = almost full\nBit 3 = full</span>')
        self.page3_rightfiller_label = gtk.Label("CFG CTRL/STATUS REG A63\n    (0x44A1_00FF)\n------------------------------ \
               \nBIT 0 = VMM CFG load Enable\nBIT 1 = cfg_run \
                \nBIT 2 = gbl_rst\nBIT 3 = ac1_rst\nBIT 4 = ENA [0,1]\nBIT 5 = CKTP (1=run)  \
                \nBIT 6 = token clock (1=enable)\nBIT 8:7 = token clock delay\nBIT 11:9 = CFG clock delay\nBIT 31:12 = 0")
        self.page3_rightfiller_label.set_markup('<span color="blue"><b>CFG CTRL/STATUS REG A63</b></span>\n<span>    (0x44A1_01FF)\n<b>------------------------------</b> \
               \nBIT 0 = VMM CFG load Enable\nBIT 1 = cfg_run \
                \nBIT 2 = gbl_rst\nBIT 3 = acq_rst\nBIT 4 = ENA [0,1]\nBIT 5 = CKTP (1=run)  \
                \nBIT 6 = token clock (1=enable)\nBIT 8:7 = token clock delay\nBIT 11:9 = CFG clock delay\nBIT 31:12 = 0</span>')
        self.page3_label_title_a = gtk.Label("32-bit Hexadecimal")
        self.page3_label_title_b = gtk.Label("32-bit Hexadecimal")        
    
        ### page3 text boxes ###
        self.page3_write_entry_statusReg1 = gtk.Entry(max=13)
        self.page3_write_entry_statusReg1.set_text("Read Only Reg")
        self.page3_write_entry_statusReg1.set_editable(False)        
        self.page3_write_entry_ctrlReg1 = gtk.Entry(max=10)
        self.page3_write_entry_ctrlReg1.set_text("0")
        
        self.page3_write_entry_ctrlReg2 = gtk.Entry(max=10)
        self.page3_write_entry_ctrlReg2.set_text("0")
        
        self.page3_write_entry_ctrlReg63 = gtk.Entry(max=10)
        self.page3_write_entry_ctrlReg63.set_text("0")

        ### the following have been set to read only
        self.page3_read_entry_statusReg1 = gtk.Entry()
        self.page3_read_entry_statusReg1.set_text("")
        self.page3_read_entry_statusReg1.set_editable(False)
        
        self.page3_read_entry_ctrlReg1 = gtk.Entry()
        self.page3_read_entry_ctrlReg1.set_text("")
        self.page3_read_entry_ctrlReg1.set_editable(False)
        
        self.page3_read_entry_ctrlReg2 = gtk.Entry(max=10)
        self.page3_read_entry_ctrlReg2.set_text("")
        self.page3_read_entry_ctrlReg2.set_editable(False)
        
        self.page3_read_entry_ctrlReg63 = gtk.Entry(max=10)
        self.page3_read_entry_ctrlReg63.set_text("")
        self.page3_read_entry_ctrlReg63.set_editable(False)
        

        ### page 3 buttons ###
        
        self.page3_write_button_statusReg1 = gtk.Button("WRITE\nStatus Reg 1")
        self.page3_write_button_statusReg1.set_sensitive(False)
        self.page3_write_button_ctrlReg1 = gtk.Button("WRITE 32-bit\ntest word")
        self.page3_write_button_ctrlReg2 = gtk.Button("WRITE FIFO38\nCtrl Reg 82")
        self.page3_write_button_ctrlReg63 = gtk.Button("WRITE CFG\nREG 63")

        self.page3_write_button_statusReg1.child.set_justify(gtk.JUSTIFY_CENTER)
        self.page3_write_button_ctrlReg1.child.set_justify(gtk.JUSTIFY_CENTER)
        self.page3_write_button_ctrlReg2.child.set_justify(gtk.JUSTIFY_CENTER)
        self.page3_write_button_ctrlReg63.child.set_justify(gtk.JUSTIFY_CENTER)

        self.page3_write_button_statusReg1.set_size_request(100,45)
        self.page3_write_button_ctrlReg1.set_size_request(100,45)
        self.page3_write_button_ctrlReg2.set_size_request(100,45)
        self.page3_write_button_ctrlReg63.set_size_request(100,45)

        self.page3_write_button_statusReg1.connect("clicked", self.page3_write_button_statusReg1_callback,self.page3_write_entry_statusReg1)
        self.page3_write_button_ctrlReg1.connect("clicked", self.page3_write_button_ctrlReg1_callback, self.page3_write_entry_ctrlReg1)
        self.page3_write_button_ctrlReg2.connect("clicked", self.page3_write_button_ctrlReg2_callback, self.page3_write_entry_ctrlReg2)
        self.page3_write_button_ctrlReg63.connect("clicked", self.page3_write_button_ctrlReg63_callback, self.page3_write_entry_ctrlReg63)

        self.page3_read_button_statusReg1 = gtk.Button("READ\nStatus Reg 1")
        self.page3_read_button_ctrlReg1 = gtk.Button("READ 32-bit\ntest word")
        self.page3_read_button_ctrlReg2 = gtk.Button("READ FIFO38\nCtrl Reg 82")
        self.page3_read_button_ctrlReg63 = gtk.Button("READ CFG\nREG 63")

        self.page3_read_button_statusReg1.child.set_justify(gtk.JUSTIFY_CENTER)
        self.page3_read_button_ctrlReg1.child.set_justify(gtk.JUSTIFY_CENTER)
        self.page3_read_button_ctrlReg2.child.set_justify(gtk.JUSTIFY_CENTER)
        self.page3_read_button_ctrlReg63.child.set_justify(gtk.JUSTIFY_CENTER)

        self.page3_read_button_statusReg1.set_size_request(100,45)
        self.page3_read_button_ctrlReg1.set_size_request(100,45)
        self.page3_read_button_ctrlReg2.set_size_request(100,45)
        self.page3_read_button_ctrlReg63.set_size_request(100,45)
 
        self.page3_read_button_statusReg1.connect("clicked", self.page3_read_button_statusReg1_callback, self.page3_read_entry_statusReg1) 
        self.page3_read_button_ctrlReg1.connect("clicked", self.page3_read_button_ctrlReg1_callback, self.page3_read_entry_ctrlReg1)
        self.page3_read_button_ctrlReg2.connect("clicked", self.page3_read_button_ctrlReg2_callback, self.page3_read_entry_ctrlReg2)
        self.page3_read_button_ctrlReg63.connect("clicked", self.page3_read_button_crtlReg63_callback, self.page3_read_entry_ctrlReg63)

        ### pack page 3boxes ###
        self.page3_table.attach(self.page3_label_title_a, left_attach=4, right_attach=5, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.page3_table.attach(self.page3_label_title_b, left_attach=6, right_attach=7, top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)
        self.page3_table.attach(self.page3_leftfiller_label, left_attach=0, right_attach=3, top_attach=0, bottom_attach=4, xpadding=40, ypadding=20)
        self.page3_table.attach(self.page3_rightfiller_label, left_attach=7, right_attach=10, top_attach=0, bottom_attach=4, xpadding=40, ypadding=20)        
        self.page3_table.attach(self.page3_write_button_statusReg1, left_attach=3, right_attach=4, top_attach=1, bottom_attach=2, xpadding=10, ypadding=20)
        self.page3_table.attach(self.page3_write_button_ctrlReg1, left_attach=3, right_attach=4, top_attach=2, bottom_attach=3, xpadding=10, ypadding=20)
        self.page3_table.attach(self.page3_write_button_ctrlReg2, left_attach=3, right_attach=4, top_attach=3, bottom_attach=4, xpadding=10, ypadding=20)
        self.page3_table.attach(self.page3_write_button_ctrlReg63, left_attach=3, right_attach=4, top_attach=4, bottom_attach=5, xpadding=10, ypadding=20)
        self.page3_table.attach(self.page3_write_entry_statusReg1, left_attach=4, right_attach=5, top_attach=1, bottom_attach=2, xpadding=60, ypadding=20)
        self.page3_table.attach(self.page3_write_entry_ctrlReg1, left_attach=4, right_attach=5, top_attach=2, bottom_attach=3, xpadding=60, ypadding=20)
        self.page3_table.attach(self.page3_write_entry_ctrlReg2, left_attach=4, right_attach=5, top_attach=3, bottom_attach=4, xpadding=60, ypadding=20)
        self.page3_table.attach(self.page3_write_entry_ctrlReg63, left_attach=4, right_attach=5, top_attach=4, bottom_attach=5, xpadding=60, ypadding=20)
        self.page3_table.attach(self.page3_read_button_statusReg1, left_attach=5, right_attach=6, top_attach=1, bottom_attach=2, xpadding=20, ypadding=20)
        self.page3_table.attach(self.page3_read_button_ctrlReg1, left_attach=5, right_attach=6, top_attach=2, bottom_attach=3, xpadding=20, ypadding=20)
        self.page3_table.attach(self.page3_read_button_ctrlReg2, left_attach=5, right_attach=6, top_attach=3, bottom_attach=4, xpadding=20, ypadding=20)
        self.page3_table.attach(self.page3_read_button_ctrlReg63, left_attach=5, right_attach=6, top_attach=4, bottom_attach=5, xpadding=20, ypadding=20)
        self.page3_table.attach(self.page3_read_entry_statusReg1, left_attach=6, right_attach=7, top_attach=1, bottom_attach=2, xpadding=60, ypadding=20)
        self.page3_table.attach(self.page3_read_entry_ctrlReg1, left_attach=6, right_attach=7, top_attach=2, bottom_attach=3, xpadding=60, ypadding=20)
        self.page3_table.attach(self.page3_read_entry_ctrlReg2, left_attach=6, right_attach=7, top_attach=3, bottom_attach=4, xpadding=60, ypadding=20)
        self.page3_table.attach(self.page3_read_entry_ctrlReg63, left_attach=6, right_attach=7, top_attach=4, bottom_attach=5, xpadding=60, ypadding=20)
        self.page3_box.pack_start(self.page3_top)
        self.page3_box.pack_start(self.page3_table, fill=False)
        self.page3_box.pack_start(self.page3_bottom)
        

        self.page1_scrolledWindow = gtk.ScrolledWindow()
        self.page1_viewport = gtk.Viewport()
        self.page1_viewport.add(self.page1_box)
        self.page1_scrolledWindow.add(self.page1_viewport)
        self.notebook.append_page(self.page1_scrolledWindow, self.tab_label_1)
        #self.notebook.append_page(self.page2_box, self.tab_label_2)
        self.notebook.append_page(self.page3_box, self.tab_label_3)

        self.box_GUI = gtk.HBox(homogeneous=0,spacing=0)
        #self.box_GUI.pack_start(self.myBigButtonsBox, expand=False)
        self.box_GUI.pack_end(self.notebook, expand=True)               
        self.window.add(self.box_GUI)
        self.window.show_all()
        self.window.connect("destroy",self.destroy)



############################__INIT__################################
############################__INIT__################################

    def main(self):
        gtk.main()

############################################################
############################################################
##################                 #########################
############################################################
############################################################

if __name__ == "__main__":
    vmm = Vmm()
    vmm.main()

 
