import serial
import telnetlib
import wx
import wx.aui
import sys
import string
import unicodedata
import subprocess
import os
import re
from ctypes import *
from iodideGUI import TestSearchCtrl
from socket import *

try:
    from agw import hyperlink as hl
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.hyperlink as hl

#------------------------------------------------------------------------------------------

ID_mem_back = wx.NewId()
ID_mem_forward = wx.NewId()
ID_search_mem = wx.NewId()
ID_search_mem_next = wx.NewId()

ID_block_back = wx.NewId()
ID_block_forward = wx.NewId()

ID_add_bookmark = wx.NewId()
ID_del_bookmark = wx.NewId()
ID_goto_bookmark = wx.NewId()

#------------------------------------------------------------------------------------------

SHOW_BAUDRATE   = 1<<0
SHOW_FORMAT     = 1<<1
SHOW_FLOW       = 1<<2
SHOW_TIMEOUT    = 1<<3
SHOW_ALL = SHOW_BAUDRATE|SHOW_FORMAT
wildcard = "All files (*.*)|*.*"




#-------Serial port config dialog----------------------------------------------------------


class SerialConfigDialog(wx.Dialog):
    """Serial Port confiuration dialog, to be used with pyserial 2.0+
       When instantiating a class of this dialog, then the "serial" keyword
       argument is mandatory. It is a reference to a serial.Serial instance.
       the optional "show" keyword argument can be used to show/hide different
       settings. The default is SHOW_ALL which coresponds to 
       SHOW_BAUDRATE|SHOW_FORMAT|SHOW_FLOW|SHOW_TIMEOUT. All constants can be
       found in ths module (not the class)."""
    
    def __init__(self, *args, **kwds):
        #grab the serial keyword and remove it from the dict
        self.serial = kwds['serial']
        del kwds['serial']
        self.show = SHOW_ALL
        if kwds.has_key('show'):
            self.show = kwds['show']
            del kwds['show']
        # begin wxGlade: SerialConfigDialog.__init__
        # end wxGlade
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_2 = wx.StaticText(self, -1, "Port")
        self.combo_box_port = wx.ComboBox(self, -1, choices=["dummy1", "dummy2", "dummy3", "dummy4", "dummy5"], style=wx.CB_DROPDOWN)
        if self.show & SHOW_BAUDRATE:
            self.label_1 = wx.StaticText(self, -1, "Baudrate")
            self.choice_baudrate = wx.Choice(self, -1, choices=["choice 1"])
        if self.show & SHOW_FORMAT:
            self.label_3 = wx.StaticText(self, -1, "Data Bits")
            self.choice_databits = wx.Choice(self, -1, choices=["choice 1"])
            self.label_4 = wx.StaticText(self, -1, "Stop Bits")
            self.choice_stopbits = wx.Choice(self, -1, choices=["choice 1"])
            self.label_5 = wx.StaticText(self, -1, "Parity")
            self.choice_parity = wx.Choice(self, -1, choices=["choice 1"])
        if self.show & SHOW_TIMEOUT:
            self.checkbox_timeout = wx.CheckBox(self, -1, "Use Timeout")
            self.text_ctrl_timeout = wx.TextCtrl(self, -1, "")
            self.label_6 = wx.StaticText(self, -1, "seconds")
        if self.show & SHOW_FLOW:
            self.checkbox_rtscts = wx.CheckBox(self, -1, "RTS/CTS")
            self.checkbox_xonxoff = wx.CheckBox(self, -1, "Xon/Xoff")
        self.button_ok = wx.Button(self, -1, "OK")
        self.button_cancel = wx.Button(self, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()
        #fill in ports and select current setting
        index = 0
        self.combo_box_port.Clear()
        for n in range(4):
            portname = serial.device(n)
            self.combo_box_port.Append(portname)
            if self.serial.portstr == portname:
                index = n
        if self.serial.portstr is not None:
            self.combo_box_port.SetValue(str(self.serial.portstr))
        else:
            self.combo_box_port.SetSelection(index)
        if self.show & SHOW_BAUDRATE:
            #fill in badrates and select current setting
            self.choice_baudrate.Clear()
            for n, baudrate in enumerate(self.serial.BAUDRATES):
                self.choice_baudrate.Append(str(baudrate))
                if self.serial.baudrate == baudrate:
                    index = n
            self.choice_baudrate.SetSelection(index)
        if self.show & SHOW_FORMAT:
            #fill in databits and select current setting
            self.choice_databits.Clear()
            for n, bytesize in enumerate(self.serial.BYTESIZES):
                self.choice_databits.Append(str(bytesize))
                if self.serial.bytesize == bytesize:
                    index = n
            self.choice_databits.SetSelection(index)
            #fill in stopbits and select current setting
            self.choice_stopbits.Clear()
            for n, stopbits in enumerate(self.serial.STOPBITS):
                self.choice_stopbits.Append(str(stopbits))
                if self.serial.stopbits == stopbits:
                    index = n
            self.choice_stopbits.SetSelection(index)
            #fill in parities and select current setting
            self.choice_parity.Clear()
            for n, parity in enumerate(self.serial.PARITIES):
                self.choice_parity.Append(str(serial.PARITY_NAMES[parity]))
                if self.serial.parity == parity:
                    index = n
            self.choice_parity.SetSelection(index)
        if self.show & SHOW_TIMEOUT:
            #set the timeout mode and value
            if self.serial.timeout is None:
                self.checkbox_timeout.SetValue(False)
                self.text_ctrl_timeout.Enable(False)
            else:
                self.checkbox_timeout.SetValue(True)
                self.text_ctrl_timeout.Enable(True)
                self.text_ctrl_timeout.SetValue(str(self.serial.timeout))
        if self.show & SHOW_FLOW:
            #set the rtscts mode
            self.checkbox_rtscts.SetValue(self.serial.rtscts)
            #set the rtscts mode
            self.checkbox_xonxoff.SetValue(self.serial.xonxoff)
        #attach the event handlers
        self.__attach_events()

    def __set_properties(self):
        # begin wxGlade: SerialConfigDialog.__set_properties
        # end wxGlade
        self.SetTitle("Serial Port Config")
        if self.show & SHOW_TIMEOUT:
            self.text_ctrl_timeout.Enable(0)
        self.button_ok.SetDefault()

    def __do_layout(self):
        # begin wxGlade: SerialConfigDialog.__do_layout
        # end wxGlade
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_basics = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Basics"), wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self.label_2, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
        sizer_5.Add(self.combo_box_port, 1, 0, 0)
        sizer_basics.Add(sizer_5, 0, wx.RIGHT|wx.EXPAND, 0)
        if self.show & SHOW_BAUDRATE:
            sizer_baudrate = wx.BoxSizer(wx.HORIZONTAL)
            sizer_baudrate.Add(self.label_1, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_baudrate.Add(self.choice_baudrate, 1, wx.ALIGN_RIGHT, 0)
            sizer_basics.Add(sizer_baudrate, 0, wx.EXPAND, 0)
        sizer_2.Add(sizer_basics, 0, wx.EXPAND, 0)
        if self.show & SHOW_FORMAT:
            sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
            sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
            sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
            sizer_format = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Data Format"), wx.VERTICAL)
            sizer_6.Add(self.label_3, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_6.Add(self.choice_databits, 1, wx.ALIGN_RIGHT, 0)
            sizer_format.Add(sizer_6, 0, wx.EXPAND, 0)
            sizer_7.Add(self.label_4, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_7.Add(self.choice_stopbits, 1, wx.ALIGN_RIGHT, 0)
            sizer_format.Add(sizer_7, 0, wx.EXPAND, 0)
            sizer_8.Add(self.label_5, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_8.Add(self.choice_parity, 1, wx.ALIGN_RIGHT, 0)
            sizer_format.Add(sizer_8, 0, wx.EXPAND, 0)
            sizer_2.Add(sizer_format, 0, wx.EXPAND, 0)
        if self.show & SHOW_TIMEOUT:
            sizer_timeout = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Timeout"), wx.HORIZONTAL)
            sizer_timeout.Add(self.checkbox_timeout, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_timeout.Add(self.text_ctrl_timeout, 0, 0, 0)
            sizer_timeout.Add(self.label_6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_2.Add(sizer_timeout, 0, 0, 0)
        if self.show & SHOW_FLOW:
            sizer_flow = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Flow Control"), wx.HORIZONTAL)
            sizer_flow.Add(self.checkbox_rtscts, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_flow.Add(self.checkbox_xonxoff, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 4)
            sizer_flow.Add((10,10), 1, wx.EXPAND, 0)
            sizer_2.Add(sizer_flow, 0, wx.EXPAND, 0)
        sizer_3.Add(self.button_ok, 0, 0, 0)
        sizer_3.Add(self.button_cancel, 0, 0, 0)
        sizer_2.Add(sizer_3, 0, wx.ALL|wx.ALIGN_RIGHT, 4)
        self.SetAutoLayout(1)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        sizer_2.SetSizeHints(self)
        self.Layout()

    def __attach_events(self):
        wx.EVT_BUTTON(self, self.button_ok.GetId(), self.OnOK)
        wx.EVT_BUTTON(self, self.button_cancel.GetId(), self.OnCancel)
        if self.show & SHOW_TIMEOUT:
            wx.EVT_CHECKBOX(self, self.checkbox_timeout.GetId(), self.OnTimeout)

    def OnOK(self, events):
        success = True
        self.serial.port     = str(self.combo_box_port.GetValue())
        if self.show & SHOW_BAUDRATE:
            self.serial.baudrate = self.serial.BAUDRATES[self.choice_baudrate.GetSelection()]
        if self.show & SHOW_FORMAT:
            self.serial.bytesize = self.serial.BYTESIZES[self.choice_databits.GetSelection()]
            self.serial.stopbits = self.serial.STOPBITS[self.choice_stopbits.GetSelection()]
            self.serial.parity   = self.serial.PARITIES[self.choice_parity.GetSelection()]
        if self.show & SHOW_FLOW:
            self.serial.rtscts   = self.checkbox_rtscts.GetValue()
            self.serial.xonxoff  = self.checkbox_xonxoff.GetValue()
        if self.show & SHOW_TIMEOUT:
            if self.checkbox_timeout.GetValue():
                try:
                    self.serial.timeout = float(self.text_ctrl_timeout.GetValue())
                except ValueError:
                    dlg = wx.MessageDialog(self, 'Timeout must be a numeric value',
                                                'Value Error', wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    success = False
            else:
                self.serial.timeout = None
        if success:
            self.EndModal(wx.ID_OK)
	
    def OnCancel(self, events):
        self.EndModal(wx.ID_CANCEL)

    def OnTimeout(self, events):
        if self.checkbox_timeout.GetValue():
            self.text_ctrl_timeout.Enable(True)
        else:
            self.text_ctrl_timeout.Enable(False)

# end of class SerialConfigDialog


#-----------------------------------------------------------------------------


class MemmapHTML(wx.html.HtmlWindow):

    def OnPopupDisassemble(self, event):	

	self.win.gdb.disassusepc = 0	
	self.win.gdb.currentdisass = self.win.gdb.currentclickaddress
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnDisassemble(1)
	self.win.gdb.dispDialog = 1
	self.win.gdb.disassusepc = 1

    def OnPopupReadmem(self, event):
	self.win.gdb.readmemusepc = 0
	self.win.gdb.currentmem = self.win.gdb.currentclickaddress
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnReadMem(1)
	self.win.gdb.dispDialog = 1
	self.win.gdb.readmemusepc = 1

    def	OnCellClicked (self, cell, x, y, event):
	self.win = self.GetGrandParent() 
	sel = wx.html.HtmlSelection()

	address = cell.ConvertToText(sel)

	if len(address) != 8:
		return 1

	try:
    		dummy = int(address,16)
	except:			
		return 1

	self.win.gdb.currentclickaddress = address

       	if not hasattr(self.win, "self.win.popupID1"):
       		self.win.popupID1 = wx.NewId()
		self.win.popupID2 = wx.NewId()
       		self.win.Bind(wx.EVT_MENU, self.OnPopupDisassemble, id=self.win.popupID1)
		self.win.Bind(wx.EVT_MENU, self.OnPopupReadmem, id=self.win.popupID2)
       		menu = wx.Menu()
       		item = wx.MenuItem(menu, self.win.popupID1, "Disassemble")
	        menu.AppendItem(item) 
		menu.Append(self.win.popupID2, "Read memory")     		
       		self.win.PopupMenu(menu)
       		menu.Destroy()


#-------Main gdb class---------------------------------------------------------------------


class gdbproto:
    """
    Ciscos version of the gdb remote protocol
    """
   
    def __init__(self):

##########################################################

	self.testbreakpoints = []
	self.testbreakpointdata = []
	self.testbreakpointdisass = []

##########################################################
	
	self.currentinstruction = ""
	self.nextinstruction = ""
	self.context = ""
	self.commandline = 0
	self.currentclickaddress = ""
	self.alreadyknowmode = False
	self.dissearch = False
	self.processor = ""
	self.sessionfile = ""
	self.hostname = ""
	self.collect_registry_data = False
	self.connect_after_continue = False
	self.continued = False
	self.reglist_final = []
	self.debugstatus = 0
	self.connectstatus = 0
	self.memreadwin = 0
	self.heapreadwin = 0
	self.memmapwin = 0
	self.processeswin = 0
	self.runningconfigwin = 0
	self.registrywin = 0
	self.bookmarkwin = 0
	self.exploitresultswin = 0
	self.regbuffer = ""
	self.program_counter = ""
	self.IOSVersion = ""
	self.stack_pointer = ""
	self.currentmem = ""
	self.currentdisass = ""
	self.heapstart = ""
	self.datastart = ""
	self.textstart = ""
	self.currentheap = ""
	self.nextblock = ""
	self.prevblock = ""
	self.showrun = ""
	self.searchterm = ""
	self.disasssearchterm = ""
	self.end_address = "ffffffff"
	self.readmemusepc = 1
	self.disassusepc = 1
	self.firstRun = 1
	self.dispDialog = 0
	self.breakpoints=[]
	self.breakpointdata=[]
	self.bookmarkaddress=[]
	self.bookmarktext=[]
	self.pid = []
	self.procname = []	
	self.gdb_connect_debug_process = "Exec            "
	self.gdb_connect_examine_process = "Exec            "
	self.gdb_connect_mode = "Kernel debugging"

	#session related variables:

	self.session_changed = False

	self.connect_mode = "Serial"
	self.telnet_IP = ""
	self.telnet_port = 23
	self.telnet_vty_password = ""
	self.telnet_enable_password = ""
	self.comments =[]
	self.registry =[]
	
	#---------------------------------------
	self.regnames=["r0&nbsp;&nbsp;=&nbsp;","sp&nbsp;&nbsp;=&nbsp;","r2&nbsp;&nbsp;=&nbsp;","r3&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;","r4&nbsp;&nbsp;=&nbsp;","r5&nbsp;&nbsp;=&nbsp;","r6&nbsp;&nbsp;=&nbsp;","r7&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;","r8&nbsp;&nbsp;=&nbsp;","r9&nbsp;&nbsp;=&nbsp;","r10&nbsp;=&nbsp;","r11&nbsp;&nbsp;&nbsp;=&nbsp;","r12&nbsp;=&nbsp;","r13&nbsp;=&nbsp;","r14&nbsp;=&nbsp;","r15&nbsp;&nbsp;&nbsp;=&nbsp;","r16&nbsp;=&nbsp;","r17&nbsp;=&nbsp;","r18&nbsp;=&nbsp;","r19&nbsp;&nbsp;&nbsp;=&nbsp;","r20&nbsp;=&nbsp;","r21&nbsp;=&nbsp;","r22&nbsp;=&nbsp;","r23&nbsp;&nbsp;&nbsp;=&nbsp;","r24&nbsp;=&nbsp;","r25&nbsp;=&nbsp;","r26&nbsp;=&nbsp;","r27&nbsp;&nbsp;&nbsp;=&nbsp;","r28&nbsp;=&nbsp;","r29&nbsp;=&nbsp;","r30&nbsp;=&nbsp;","r31&nbsp;&nbsp;&nbsp;=&nbsp;","pc&nbsp;&nbsp;=&nbsp;","msr&nbsp;=&nbsp;","cr&nbsp;&nbsp;=&nbsp;","lr&nbsp;&nbsp;&nbsp;&nbsp;=&nbsp;","ctr&nbsp;=&nbsp;","xer&nbsp;=&nbsp;","dar&nbsp;=&nbsp;","dsisr&nbsp;=&nbsp;"]

	self.regnames2=["r0","sp","r2","r3","r4","r5","r6","r7","r8","r9","r10","r11","r12","r13","r14","r15","r16","r17","r18","r19","r20","r21","r22","r23","r24","r25","r26","r27","r28","r29","r30","r31","pc","msr","cr","lr","ctr","xer","dar","dsisr"]
	self.regvals= ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"]
	self.lastregvals= ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"]
	self.currentheap = self.heapstart



#-------Get view of GUI--------------------------------------------------------------------


    def window (self, win):
	self.win = win


#-------Initially disable menus and toolbar buttons----------------------------------------


    def disableObjects (self):
	#self.win.mb.Enable(self.win.ID_Reconnect, False)
	self.win.mb.Enable(self.win.ID_Download, False)
	self.win.mb.Enable(self.win.ID_Upload, False)
	self.win.mb.Enable(self.win.ID_SaveRunningConfig, False)	

	#self.win.mb.Enable(self.win.ID_ReadReg, False)
	self.win.mb.Enable(self.win.ID_ReadMem, False)
	self.win.mb.Enable(self.win.ID_ReadHeap, False)
	self.win.mb.Enable(self.win.ID_MemMap, False)
	self.win.mb.Enable(self.win.ID_Processes, False)
	self.win.mb.Enable(self.win.ID_RunningConfig, False)
	self.win.mb.Enable(self.win.ID_Registry, False)
	self.win.mb.Enable(self.win.ID_Disassemble, False)
	self.win.mb.Enable(self.win.ID_ListBookmarks, False)
	self.win.mb.Enable(self.win.ID_Search, False)

	self.win.mb.Enable(self.win.ID_WriteReg, False)
	self.win.mb.Enable(self.win.ID_WriteMem, False)
	self.win.mb.Enable(self.win.ID_SetBreakpoints, False)
	self.win.mb.Enable(self.win.ID_DelBreakpoints, False)
	self.win.mb.Enable(self.win.ID_Comment, False)

	self.win.mb.Enable(self.win.ID_StepInto, False)
	self.win.mb.Enable(self.win.ID_StepOver, False)
	self.win.mb.Enable(self.win.ID_Jump, False)
	self.win.mb.Enable(self.win.ID_Continue, False)


#------------toolbar stuff-----------------------------------------------------------------

	#self.win.tb.EnableTool(self.win.ID_toolReconnect,False)
	self.win.tb.EnableTool(self.win.ID_toolDownload,False)
	self.win.tb.EnableTool(self.win.ID_toolUpload,False)
	
	self.win.tb.EnableTool(self.win.ID_toolDisLabel,False)
	self.win.tb.EnableTool(self.win.ID_toolDisback,False)
	self.win.tb.EnableTool(self.win.ID_toolDisforward,False)

	self.win.tb.EnableTool(self.win.ID_toolDebugLabel,False)
	self.win.tb.EnableTool(self.win.ID_toolStep,False)
	self.win.tb.EnableTool(self.win.ID_toolStepover,False)
	self.win.tb.EnableTool(self.win.ID_toolContinue,False)

	self.win.tb.EnableTool(self.win.ID_toolBreakLabel,False)
	self.win.tb.EnableTool(self.win.ID_toolAddBreak,False)
	self.win.tb.EnableTool(self.win.ID_toolDelBreak,False)
	self.win.tb.EnableTool(self.win.ID_toolListBookmarks,False)

	self.win.tb.EnableTool(self.win.ID_toolComment,False)
	self.win.tb.EnableTool(self.win.ID_toolFindNext,False)


#-------enable menus and toolbar buttons when connected------------------------------------

    def enableObjects (self):
	self.win.mb.Enable(self.win.ID_Reconnect, True)
	self.win.mb.Enable(self.win.ID_Download, True)
	self.win.mb.Enable(self.win.ID_Upload, True)
	self.win.mb.Enable(self.win.ID_SaveRunningConfig, True)	

	#self.win.mb.Enable(self.win.ID_ReadReg, True)
	self.win.mb.Enable(self.win.ID_ReadMem, True)
	self.win.mb.Enable(self.win.ID_ReadHeap, True)
	self.win.mb.Enable(self.win.ID_MemMap, True)
	self.win.mb.Enable(self.win.ID_Processes, True)
	self.win.mb.Enable(self.win.ID_RunningConfig, True)
	self.win.mb.Enable(self.win.ID_Registry, True)
	self.win.mb.Enable(self.win.ID_Disassemble, True)
	self.win.mb.Enable(self.win.ID_ListBookmarks, True)
	self.win.mb.Enable(self.win.ID_Search, True)

	self.win.mb.Enable(self.win.ID_WriteReg, True)
	self.win.mb.Enable(self.win.ID_WriteMem, True)
	self.win.mb.Enable(self.win.ID_SetBreakpoints, True)
	self.win.mb.Enable(self.win.ID_DelBreakpoints, True)
	self.win.mb.Enable(self.win.ID_Comment, True)

	self.win.mb.Enable(self.win.ID_StepInto, True)
	self.win.mb.Enable(self.win.ID_StepOver, True)
	self.win.mb.Enable(self.win.ID_Jump, True)
	self.win.mb.Enable(self.win.ID_Continue, True)



#------------toolbar stuff-----------------------------------------------------------------

	self.win.tb.EnableTool(self.win.ID_toolReconnect,True)
	self.win.tb.EnableTool(self.win.ID_toolDownload,True)
	self.win.tb.EnableTool(self.win.ID_toolUpload,True)
	
	self.win.tb.EnableTool(self.win.ID_toolDisLabel,True)
	self.win.tb.EnableTool(self.win.ID_toolDisback,True)
	self.win.tb.EnableTool(self.win.ID_toolDisforward,True)

	self.win.tb.EnableTool(self.win.ID_toolDebugLabel,True)
	self.win.tb.EnableTool(self.win.ID_toolStep,True)
	self.win.tb.EnableTool(self.win.ID_toolStepover,True)
	self.win.tb.EnableTool(self.win.ID_toolContinue,True)

	self.win.tb.EnableTool(self.win.ID_toolBreakLabel,True)
	self.win.tb.EnableTool(self.win.ID_toolAddBreak,True)
	self.win.tb.EnableTool(self.win.ID_toolDelBreak,True)
	self.win.tb.EnableTool(self.win.ID_toolListBookmarks,True)

	self.win.tb.EnableTool(self.win.ID_toolComment,True)
	self.win.tb.EnableTool(self.win.ID_toolFindNext,True)

#-------Decode run length encoding---------------------------------------------------------


    def decodeRLE(self,data):
	i=2
	multiplier=0
	reply=""

	while i < len(data):

		if data[i] == "*":
			multiplier = int(data[i+1] + data[i+2],16)
			for j in range (0, multiplier):
				reply = reply + data[i-1]
			i = i + 3

		if data[i] == "#":
			break	
        	
		reply = reply + data[i]
		i = i + 1
	return reply


#-------Calculate checksum-----------------------------------------------------------------


    def checksum(self,command):

	csum = 0
	reply = ""
	for x in command:
		csum = csum + ord(x)

	csum = csum % 256

	reply = "$" + command + "#%02x" % csum

	return reply


#-------Send a gdb command and decode the reply--------------------------------------------


    def GdbCommand(self, command):
	"""
	Sends a gdb command to the serial port, decodes any run-length encoding and returns the buffer
	"""
	reply = ""
	char = ""
	

	if self.connect_mode == "Serial":
		self.ser.write(command)	
		while char != "#":
			char = self.ser.read(1)		
			reply = reply + char	
		self.ser.read(2) 			#read checksum bytes

	else:

		self.tn.write(command)
		reply = self.tn.read_until("#",1)	
	
		if reply == "" or reply[0] == "$":
			self.tn.write(command)
			reply = self.tn.read_until("#",1)
	
		self.tn.read_some()

		

	if reply[0] == "-":
		return "E03"

	newrle = self.decodeRLE(reply)
	decoded = newrle.decode()	

	while decoded[0] == "|" or decoded[0] == "+" or decoded[0] == "$":
		decoded = decoded[1:]

	return decoded


#-------Configure the serial port----------------------------------------------------------


    def OnSerial(self, evt):
	dialog_serial_cfg = SerialConfigDialog(None, -1, "", serial=self.ser, show=SHOW_ALL)
        result = dialog_serial_cfg.ShowModal()  


#-------Connect to the device--------------------------------------------------------------


    def OnConnect(self, evt):

	if self.connect_mode == "Serial":

		if self.continued == False:
			try:
				self.ser = serial.Serial(15, timeout=1)  # open first serial port         	
      			except:
              			wx.MessageBox("Serial communication error", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
				return(1)
  
			self.ser.baudrate = 115200
		else:
			self.connect_after_continue = True	

		self.ser.write("\n")  # get the router into a known state
		self.ser.readline()
		self.ser.write("term len 0\n")  
		self.ser.readline()
		self.ser.write("\n")
		reply = self.ser.readline()
		self.hostname = reply[:-3]

		if reply == "":
			wx.MessageBox("Serial communication error", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return(1)
		connection_status = "Connection Status: Connected to \"%s\" via serial" % self.hostname
		self.win.statusbar.SetStatusText(connection_status, 1)
	else:

		if self.continued == False:
			try:
				self.tn = telnetlib.Telnet(self.telnet_IP,self.telnet_port)         	
      			except:
              			wx.MessageBox("Telnet communication error", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
				return(1)
		else:
			self.connect_after_continue = True
		
		if self.telnet_vty_password != "":
			self.tn.read_until("\n")
			self.tn.read_until("Password: ")
    			self.tn.write(self.telnet_vty_password + "\n")
			self.tn.read_some()
			self.tn.write("\n")
			self.tn.read_until("\n")

		if self.telnet_enable_password != "":
			self.tn.write("\n")
			self.tn.read_until("\n",1)
			self.tn.write("\n")  
			self.tn.read_until("\n",1)
			self.tn.write("en\n")
			self.tn.read_until("Password: ")
			self.tn.write(self.telnet_enable_password + "\n")
			self.tn.read_some()

		self.tn.read_until("\n",1)
		self.tn.write("\r\n")  
		self.tn.read_until("#",1)
		self.tn.write("term len 0\n") 
		self.tn.read_until("#",1)
		self.tn.write("\r\n")  
		self.tn.read_until("#",1)
		self.tn.write("\r\n")
		reply = self.tn.read_until("#",1)

				
		connection_status = "Connection Status: Connected to %s" % self.telnet_IP
		self.win.statusbar.SetStatusText(connection_status, 1)			

	connectstatuswin = self.CreateConnectStatusWindow()
	connectstatuswin.SetFocus()

	image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
	icon = wx.EmptyIcon() 
	icon.CopyFromBitmap(image) 
	connectstatuswin.SetIcon(icon) 

	g1 = wx.Gauge(connectstatuswin, -1, 4200, (5, 20), (200, 25))

	gaugestep = 600
	gaugeval = 0	

	self.connectstatus = 1

	gaugeval = gaugeval + gaugestep
	g1.SetValue(gaugeval)

	if not self.pid:
		self.win.statusbar.SetStatusText("Collecting process information...", 0)
		self.RouterShowProcess()
		self.session_changed = True
		wx.SafeYield()

	gaugeval = gaugeval + gaugestep
	g1.SetValue(gaugeval)

	if not self.registry and self.collect_registry_data == True:
		self.win.statusbar.SetStatusText("Collecting registry information...", 0)	
		self.CollectRegistry()
		self.session_changed = True
		wx.SafeYield()

	gaugeval = gaugeval + gaugestep
	g1.SetValue(gaugeval)	

	if not self.reglist_final:
		self.win.statusbar.SetStatusText("Creating memory map...", 0)
		self.RouterShowRegion()
		self.session_changed = True
		wx.SafeYield()
	

	gaugeval = gaugeval + gaugestep
	g1.SetValue(gaugeval)
	
	if not self.processor:
		self.win.statusbar.SetStatusText("Detecting processor...", 0)
		self.DetectProcessor()
		connection_status = connection_status + " (%s)" % self.processor
		self.win.statusbar.SetStatusText(connection_status, 1)

	if not self.IOSVersion:
		self.win.statusbar.SetStatusText("Detecting processor...", 0)
		self.DetectIOSVersion()


	if not self.showrun:
		self.win.statusbar.SetStatusText("Collecting running config...", 0)
		self.RouterShowRun()
		self.session_changed = True

	if not self.continued:   
		self.OkGdb = False
		self.connectgdbwin = self.CreateGdbOptionsWindow()
		self.connectgdbwin.SetFocus()
		self.win.statusbar.SetStatusText("", 0)

		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.connectgdbwin.SetIcon(icon) 

		vs = wx.BoxSizer( wx.VERTICAL )
        	box1_title = wx.StaticBox( self.connectgdbwin, -1, "Select debugging option" )
       	 	box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
		grid1 = wx.FlexGridSizer( 0, 2, 0, 0 )

		self.group1_ctrls = []       

       	 	radio1 = wx.RadioButton( self.connectgdbwin, -1, "Kernel debugging", style = wx.RB_GROUP )
        	radio2 = wx.RadioButton( self.connectgdbwin, -1, "Process debugging (unreliable)" )
        	radio3 = wx.RadioButton( self.connectgdbwin, -1, "Read only process debugging" )

		text1 = wx.StaticText(self.connectgdbwin, -1, "Select process:")
		choice1 = wx.Choice(self.connectgdbwin, -1, choices = self.procname)
		choice2 = wx.Choice(self.connectgdbwin, -1, choices = self.procname)
        	self.group1_ctrls.append((radio1, text1))
        	self.group1_ctrls.append((radio2, choice1))
        	self.group1_ctrls.append((radio3, choice2))
	
        	grid1.Add( radio1, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		grid1.Add( text1, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		grid1.Add( radio2, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		grid1.Add( choice1, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		grid1.Add( radio3, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
		grid1.Add( choice2, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	
		box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
        	vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )

		button = wx.Button(self.connectgdbwin, 1004, "OK")
        	self.connectgdbwin.Bind(wx.EVT_BUTTON, self.OnOkGdb, button)
		vs.Add( button, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )

		self.connectgdbwin.Bind(wx.EVT_CHOICE, self.GdbEvtChoiceDebug, choice1)
		self.connectgdbwin.Bind(wx.EVT_CHOICE, self.GdbEvtChoiceExamine, choice2)
		self.connectgdbwin.SetSizer( vs )
        	vs.Fit( self.connectgdbwin )

		for radio, choice in self.group1_ctrls:
        		self.connectgdbwin.Bind(wx.EVT_RADIOBUTTON, self.OnGdbModeSelect, radio )

		for radio, choice in self.group1_ctrls:
            		radio.SetValue(0)
            		choice.Enable(False)

		radio1.SetValue(1)
		text1.Enable(True)

		while self.OkGdb == False:
			wx.Yield()


	

	if self.connect_mode == "Serial":
		self.ser.write("\n")  # get the router into a known state
		self.ser.readline()
		self.ser.write("\n")  
		self.ser.readline()
	else:
		self.tn.write("\r\n")
		self.tn.read_until("\n",1)
		self.tn.write("\r\n")
		self.tn.read_until("\n",1)


	self.EnterGdbMode()
	val = self.OnReadReg(1)	

	if val == 1:
		connectstatuswin.Close(True)
		return

	gaugeval = gaugeval + gaugestep
	g1.SetValue(gaugeval)
	
	self.dispDialog = 0
	self.OnDisassemble(1)
	
	gaugeval = gaugeval + gaugestep
	g1.SetValue(gaugeval)
	
	try:
		self.OnLastSigval(1)         	
      	except:
              	pass	

	gaugeval = gaugeval + gaugestep
	g1.SetValue(gaugeval)
	
	self.OnReadStack()
	self.OnBreakpoints(1)

	self.OnFindContext(1)
	tmp = "Kernel debugging: Context = %s" % self.context
	self.win.statusbar.SetStatusText(tmp, 2)
	
	connectstatuswin.Close(True)
	self.dispDialog = 1  #after an initial call to display mem etc.
	
	self.win.mb.Enable(self.win.ID_Connect, False)
	self.win.mb.Enable(self.win.ID_Reconnect, False)
	self.win.mb.Enable(self.win.ID_ConfigureConnection, False)

	self.win.tb.EnableTool(self.win.ID_toolConfigureConnection, False)	
	self.win.tb.EnableTool(self.win.ID_toolConnect,False)
	self.win.tb.EnableTool(self.win.ID_toolReconnect,False)


#-------Radio button selection (gdb conf)--------------------------------------------------


    def OnGdbModeSelect( self, event ):
        radio_selected = event.GetEventObject()
         
	self.gdb_connect_mode = radio_selected.GetLabel()

        for radio, choice in self.group1_ctrls:
            	if radio is radio_selected:
                	choice.Enable(True)
            	else:
                	choice.Enable(False)


#-------Radio button selection (con conf)--------------------------------------------------


    def OnConnectModeSelect( self, event ):
        radio_selected = event.GetEventObject()
        self.session_changed = True
 
	self.connect_mode = radio_selected.GetLabel()

        for radio, text in self.conf_ctrls:
            	if radio is radio_selected:
                	text.Enable(True)
            	else:
                	text.Enable(False)

#-------Process telnet options-------------------------------------------------------------


    def ConfConEvtIP(self, event):
         
	self.telnet_IP = event.GetString()
	self.session_changed = True	

    def ConfConEvtPort(self, event):
         
	self.telnet_port = int(event.GetString())
	self.session_changed = True	

    def ConfConEvtVty(self, event):
         
	self.telnet_vty_password = event.GetString()
	self.session_changed = True

    def ConfConEvtEnable(self, event):
         
	self.telnet_enable_password = event.GetString()
	self.session_changed = True


#-------Process choice list----------------------------------------------------------------


    def GdbEvtChoiceDebug(self, event):
         
	self.gdb_connect_debug_process = event.GetString()


#-------Process choice list2---------------------------------------------------------------


    def GdbEvtChoiceExamine(self, event):

        self.gdb_connect_examine_process = event.GetString()


#-------Close gdb window when the OK button is pressed-------------------------------------

    def	OnOkGdb (self,evt):
	
	self.OkGdb = True
	self.connectgdbwin.Close()

#-------Create new window to display connect status----------------------------------------


    def CreateConnectStatusWindow (self):

	win = wx.Frame(self.win, -1, "Collecting initial data",size=(220,95))
	win.Center()
	win.Show(True)
	return win


#-------Create new window to display connection configuration------------------------------


    def CreateConnectConfWindow (self):

	win = wx.Frame(self.win, -1, "Connection configuration",size=(350,200))
	win.Center()
	win.Show(True)
	return win


#-------Create new window to display gdb options-------------------------------------------


    def CreateGdbOptionsWindow (self):

	win = wx.Frame(self.win, -1, "gdb configuration",size=(350,200))
	win.Center()
	win.Show(True)
	return win

#-------Configure serial and telnet--------------------------------------------------------

    def	OnConfigureConnection (self,evt):

	self.OkConConf = False
	self.connectconfwin = self.CreateConnectConfWindow()

	image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
	icon = wx.EmptyIcon() 
	icon.CopyFromBitmap(image) 
	self.connectconfwin.SetIcon(icon) 

	vs = wx.BoxSizer( wx.VERTICAL )
        box1_title = wx.StaticBox( self.connectconfwin, -1, "Select connection type" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
	grid1 = wx.FlexGridSizer( 0, 2, 0, 0 )

	self.conf_ctrls = []       

        radio1 = wx.RadioButton( self.connectconfwin, -1, "Serial", style = wx.RB_GROUP )
	text9 = wx.StaticText(self.connectconfwin, -1, " ")
        radio2 = wx.RadioButton( self.connectconfwin, -1, "Telnet" )
	text1 = wx.StaticText(self.connectconfwin, -1, "IP address:")	
	text2 = wx.TextCtrl( self.connectconfwin, -1, self.telnet_IP)
	text3 = wx.StaticText(self.connectconfwin, -1, "Port:")	
	text4 = wx.TextCtrl( self.connectconfwin, -1, "%d" % self.telnet_port)
	text5 = wx.StaticText(self.connectconfwin, -1, "VTY password:")	
	text6 = wx.TextCtrl( self.connectconfwin, -1, self.telnet_vty_password,style=wx.TE_PASSWORD )
	text7 = wx.StaticText(self.connectconfwin, -1, "Enable password:")	
	text8 = wx.TextCtrl( self.connectconfwin, -1, self.telnet_enable_password,style=wx.TE_PASSWORD )
	
	self.conf_ctrls.append((radio1, text9))
        self.conf_ctrls.append((radio2, text1))
	self.conf_ctrls.append((radio2, text2))
	self.conf_ctrls.append((radio2, text3))
	self.conf_ctrls.append((radio2, text4))
	self.conf_ctrls.append((radio2, text5))
	self.conf_ctrls.append((radio2, text6))
	self.conf_ctrls.append((radio2, text7))
	self.conf_ctrls.append((radio2, text8))

	grid1.Add( radio1, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )	
	grid1.Add( radio2, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text1, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text2, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text3, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text4, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text5, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text6, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text7, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text8, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )
	grid1.Add( text9, 0, wx.ALIGN_LEFT|wx.LEFT|wx.RIGHT|wx.TOP, 5 )	
	
	box1.Add( grid1, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
        vs.Add( box1, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )

	button = wx.Button(self.connectconfwin, 1005, "OK")
        self.connectconfwin.Bind(wx.EVT_BUTTON, self.OnOkConConf, button)
	cb1 = wx.CheckBox(self.connectconfwin, -1, "Collect function registry information?")
	self.connectconfwin.Bind(wx.EVT_CHECKBOX, self.OnCollectRegistry, cb1)
	vs.Add( cb1, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
	vs.Add( button, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )

	self.connectconfwin.Bind(wx.EVT_TEXT, self.ConfConEvtIP, text2)
	self.connectconfwin.Bind(wx.EVT_TEXT, self.ConfConEvtPort, text4)
	self.connectconfwin.Bind(wx.EVT_TEXT, self.ConfConEvtVty, text6)
	self.connectconfwin.Bind(wx.EVT_TEXT, self.ConfConEvtEnable, text8)
	
	self.connectconfwin.SetSizer( vs )
        vs.Fit( self.connectconfwin )
	
        self.connectconfwin.Bind(wx.EVT_RADIOBUTTON, self.OnConnectModeSelect, radio1)
	self.connectconfwin.Bind(wx.EVT_RADIOBUTTON, self.OnConnectModeSelect, radio2)

	for radio, text in self.conf_ctrls:
            	radio.SetValue(0)
            	text.Enable(False)

	if self.connect_mode == "Telnet":
		radio2.SetValue(1)
		text1.Enable(True)
		text2.Enable(True)
		text3.Enable(True)
		text4.Enable(True)
		text5.Enable(True)
		text6.Enable(True)
		text7.Enable(True)
		text8.Enable(True)
	else:
		radio1.SetValue(1)

	while self.OkConConf == False:
		wx.Yield()


#-------Collect function registry info-----------------------------------------------------
	

    def OnCollectRegistry (self,evt):
	self.collect_registry_data = True
	return 0
	

#-------Close connection configuration window when the OK button is pressed----------------

    def	OnOkConConf (self,evt):
	
	self.OkConConf = True
	self.connectconfwin.Close()

#-------Reconnect to the device------------------------------------------------------------


    def OnReconnect(self, evt):
	
	#if self.connect_mode == "Serial":
	#	self.ser = serial.Serial(6, timeout=1)  # open first serial port
	#	self.ser.baudrate = 115200

	#else:
	#	self.tn = telnetlib.Telnet(self.telnet_IP,self.telnet_port) 

	#self.win.statusbar.SetStatusText("Connection Status: Connected to device - Motorola MPC860", 1)	
	#self.connectstatus = 1

	self.debugstatus = 1
	self.win.statusbar.SetStatusText("Debugging Status: Kernel debugging mode", 2)

	self.dispDialog = 0
	self.OnReadReg(1)	
	self.win.statusbar.SetStatusText("Collecting initial data..", 0)
	self.OnDisassemble(1)	
	self.win.statusbar.SetStatusText("Collecting initial data....", 0)
	self.OnLastSigval(1)
	self.win.statusbar.SetStatusText("Collecting initial data......", 0)
	self.OnReadStack()	
	self.win.statusbar.SetStatusText("Collecting initial data........", 0)
	self.OnBreakpoints(1)
	self.enableObjects()
	self.win.statusbar.SetStatusText("", 0)
	self.OnFindContext(1)
	tmp = "Kernel debugging: Context = %s" % self.context
	self.win.statusbar.SetStatusText(tmp, 2)	
	self.dispDialog = 1  #after an initial call to disassemble etc.



#-------Download data from memory----------------------------------------------------------

    def OnDownload(self, evt):

	i = j = 0
	if self.dispDialog == 1:

		dlg = wx.TextEntryDialog(self.win, 'Enter the address to download data from','Download data')

		address = ""
		remainder_string = ""

        	if dlg.ShowModal() == wx.ID_OK:
            		address = dlg.GetValue()
			address = string.lower(address)

		dlg.Destroy()
		if address == "":
			return 1
		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1
	else:
		address = self.currentclickaddress

	dlg = wx.TextEntryDialog(self.win, 'Enter the number of bytes to download (decimal)','Download data')

	num_bytes = ""

        if dlg.ShowModal() == wx.ID_OK:
            	num_bytes = dlg.GetValue()

        dlg.Destroy()
	if num_bytes == "":
		return 1
	try:
    		dummy = int(num_bytes)
	except:
		wx.MessageBox("Invalid number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1
	
        dlg = wx.FileDialog(
            self.win, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=wildcard, style=wx.SAVE
            )

        dlg.SetFilterIndex(2)

	path = ""
        if dlg.ShowModal() == wx.ID_OK:
		path = dlg.GetPath()
		dlg.Destroy()
		if path == "":
			return 1

		downloadwin = self.CreateDownloadWindow()

		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		downloadwin.SetIcon(icon) 

		downloadwin.Center()
		g1 = wx.Gauge(downloadwin, -1, 20000000, (5, 20), (200, 25))

		address_int = int (address,16)		

		bytes_int = int (num_bytes,10)	
		iterations = bytes_int / 200
		remainder = bytes_int % 200 
		remainder_string = "%02x" % remainder
		
		if iterations == 0:
			guagestep = 1
		else:
			gaugestep = 20000000 / iterations
		
		gaugeval = 0

		try:
			fp = file(path, 'wb')	# open file for writing
		except:
			wx.MessageBox("Error opening file", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)

		while j < iterations:
			wx.Yield()
			i = 0
			address = "%08x" % address_int

	  		formatted = self.CreateGetMemoryReq(address,"c8")	# 200 bytes
			data = self.GdbCommand(formatted) #set read memory command

			if data == "E03":
				wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
				downloadwin.Close(True)
				fp.close()
				return 1
			 
			while i < len(data):
				data_int = int(data[i] + data[i+1],16)
				fp.write("%c" % data_int)
				i = i + 2

			address_int = address_int + 200
			
			j = j + 1
	
			g1.SetValue(gaugeval)
			gaugeval = gaugeval + gaugestep
		
		#-----------------write remining bytes------------------------
		wx.Yield()
		address = "%08x" % address_int	

		if remainder != 0:

			formatted = self.CreateGetMemoryReq(address,remainder_string)	
			data = self.GdbCommand(formatted) #set read memory command
			
			if data == "E03":
				wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
				downloadwin.Close(True)
				fp.close()
				return 1

			i = 0
			while i < len(data)-1:
				data_int = int(data[i] + data[i+1],16)
				fp.write("%c" % data_int)
				i = i + 2

		fp.close()  
		downloadwin.Close(True)
		wx.MessageBox("Data download complete", caption="Success", style=wx.OK|wx.ICON_INFORMATION, parent=self.win)



#-------Create new window to display download status------------------------------------


    def CreateDownloadWindow (self):

	win = wx.Frame(self.win, -1, "Downloading data",size=(220,100))
	win.Show(True)
	return win


#-------Create new window to display upload status--------------------------------------


    def CreateUploadWindow (self):

	win = wx.Frame(self.win, -1, "Uploading data",size=(220,100))
	win.Show(True)
	return win

#-------Upload data to memory-----------------------------------------------------------


    def OnUpload(self, evt):	
	
	path = ""
        dlg = wx.FileDialog(
            self.win, message="Choose a file", defaultDir=os.getcwd(), 
            defaultFile="default", wildcard="*.*", style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
		path = dlg.GetPath()
		dlg.Destroy()
		if path == "":
			return 1

		if not os.path.exists(path):
			wx.MessageBox("File does not exist", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

		try:
			fp = file(path, 'rb')	# open file for reading
		except:
			wx.MessageBox("Error opening file", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)

		buffer = fp.read()
		convbuffer = ""
		x = 0
	
		while x < len(buffer):
			convbuffer = convbuffer + "%02x" % ord(buffer[x])	# convert buffer into hex represenations of binary data
			x = x + 1

		i = j = 0

		if self.dispDialog == 1:

			dlg = wx.TextEntryDialog(self.win, 'Enter the address to upload data to','Upload data')

			address = ""
			remainder_string = ""

        		if dlg.ShowModal() == wx.ID_OK:
           	 		address = dlg.GetValue()
				address = string.lower(address)

			dlg.Destroy()
			if address == "":
				return 1
			if self.invalidaddress(address):		
				wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
				return 1

		else:

			address = self.currentclickaddress

		uploadwin = self.CreateUploadWindow()
		uploadwin.Center()
		g1 = wx.Gauge(uploadwin, -1, 20000000, (5, 20), (200, 25))

		address_int = int (address,16)		

		gaugestep = 40000000 / len(convbuffer)		
		gaugeval = 0

		x = 0
		while x < len(convbuffer): 
			wx.Yield()
			command = self.CreateWriteMemoryReq(address,convbuffer[x:x+2],"01")
			result = self.GdbCommand(command) #send write memory command

			command = self.CreateGetMemoryReq(address,"01")
			result = self.GdbCommand(command) #set read memory command
	
			if result != convbuffer[x:x+2]:		
				wx.MessageBox("Write Failed", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)	
				fp.close()
				return 1
			
			x = x + 2
			address_int = address_int + 1
			address = "%08x" % address_int
			g1.SetValue(gaugeval)
			gaugeval = gaugeval + gaugestep

		uploadwin.Close(True)
		if self.dispDialog == 1:
			wx.MessageBox("Data upload complete", caption="Success", style=wx.OK|wx.ICON_INFORMATION, parent=self.win)
		fp.close() 


#-------Save running config----------------------------------------------------------------


    def OnSaveRunningConfig(self, evt):	
	
	path = ""
		
        dlg = wx.FileDialog(self.win, message="Save file as ...", defaultDir=os.getcwd(), 
        		    defaultFile="default", wildcard="*.txt", style=wx.SAVE)

        dlg.SetFilterIndex(2)	

	if dlg.ShowModal() == wx.ID_OK:
		path = dlg.GetPath()
		dlg.Destroy()
	if path == "":
		return 1
	
	try:	
		fp = file(path, 'w')	# open file for writing (appending)
	except:
		wx.MessageBox("Error opening file", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		
	tmp = string.replace(self.showrun, "<br>", "\n" )
	fp.write(tmp)
	
	fp.close()  


#-------Save session-----------------------------------------------------------------------

    def OnSave(self, evt):	
	
	path = ""
	if not self.sessionfile:
		
        	dlg = wx.FileDialog(
           	 self.win, message="Save file as ...", defaultDir=os.getcwd(), 
            	defaultFile="default", wildcard="*.iod", style=wx.SAVE
            	)

        	dlg.SetFilterIndex(2)	

       		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			dlg.Destroy()
		if path == "":
			return 1

	else:
		path = self.sessionfile
	
	try:	
		fp = file(path, 'w')	# open file for writing (appending)
	except:
		wx.MessageBox("Error opening file", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
	
	if self.connect_mode == "Serial":
		fp.write("Mode:Serial:")

	elif self.connect_mode == "Telnet":
		fp.write("Mode:Telnet:")
		fp.write("IP:%s:" % self.telnet_IP)
		fp.write("Port:%d:" % self.telnet_port)
		if self.telnet_vty_password != "":
			fp.write("Vty:%s:" % self.telnet_vty_password)
		if self.telnet_enable_password != "":
			fp.write("Enable:%s:" % self.telnet_enable_password)
		
	if self.comments:
		x = 0
		while x < len(self.comments)-1:
			fp.write("Comment:%s,%s:" %(self.comments[x], self.comments[x+1]))
			x = x + 2
	
	if self.registry:
		x = 0
		while x < len(self.registry)-1:
			fp.write("Reg:%s,%s:" %(self.registry[x], self.registry[x+1]))
			x = x + 2

	if self.reglist_final:
		x = 0
		while x < len(self.reglist_final)-2:
			fp.write("Memmap:%s,%s,%s:" %(self.reglist_final[x], self.reglist_final[x+1], self.reglist_final[x+2]))
			x = x + 3		

	if self.pid:
		x = 0
		while x < len(self.pid):
			fp.write("Process:%s,%s:" %(self.pid[x], self.procname[x]))
			x = x + 1	

	if self.bookmarkaddress:
		x = 0
		while x < len(self.bookmarkaddress):
			fp.write("Bookmark:%s,%s:" %(self.bookmarkaddress[x], self.bookmarktext[x]))
			x = x + 1

	if self.processor:
		fp.write("Processor:%s:" % self.processor)

	if self.IOSVersion:
		fp.write("IOSVersion:%s:" % self.IOSVersion)

	if self.heapstart:
		fp.write("Heapstart:%s:" % self.heapstart)

	if self.datastart:
		fp.write("Datastart:%s:" % self.datastart)

	if self.textstart:
		fp.write("Teststart:%s:" % self.textstart)

	if self.showrun:
		fp.write("Config:%s:" % self.showrun)

	self.session_changed = False
	self.sessionfile = path
	self.win.Title = "IODIDE - " + path
	fp.close()  
		

#-------Load session-----------------------------------------------------------------------


    def OnOpen(self, evt):	
	
	datalist = []
	x = 0
	path = ""
	tmpcomment = []
        dlg = wx.FileDialog(
            self.win, message="Choose a file", defaultDir=os.getcwd(), 
            defaultFile="default", wildcard="*.iod", style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        dlg.SetFilterIndex(2)

        if dlg.ShowModal() == wx.ID_OK:
		path = dlg.GetPath()
		dlg.Destroy()
		if path == "":
			return 1

		if not os.path.exists(path):
			wx.MessageBox("File does not exist", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1



		try:
			fp = file(path, 'r')	# open file for reading
		except:
			wx.MessageBox("Error opening file", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)

		self.win.statusbar.SetStatusText("Reading session file...", 0)

		data = fp.read()
		datalist = data.split(':')

		while x < len(datalist) -1:

			if datalist[x] == "Mode" and datalist[x+1] == "Serial":
				self.connect_mode = "Serial"
				#self.alreadyknowmode = True

			if datalist[x] == "Mode" and datalist[x+1] == "Telnet":
				self.connect_mode = "Telnet"
				#self.alreadyknowmode = True

			if datalist[x] == "IP":
				self.telnet_IP = datalist[x+1]

			if datalist[x] == "Port":
				self.telnet_port = int(datalist[x+1])

			if datalist[x] == "Vty":
				self.telnet_vty_password = datalist[x+1] + "\n"

			if datalist[x] == "Enable":
				self.telnet_enable_password = datalist[x+1] + "\n"

			if datalist[x] == "Comment":
				tmp = datalist[x+1]
				tmpcomment = tmp.split(',')
				self.comments.append(tmpcomment[0])
				self.comments.append(tmpcomment[1])
	
			if datalist[x] == "Reg":
				wx.Yield()
				tmp = datalist[x+1]
				tmpreg = tmp.split(',')
				self.registry.append(tmpreg[0])
				self.registry.append(tmpreg[1])

			if datalist[x] == "Memmap":
				tmp = datalist[x+1]
				tmpmap = tmp.split(',')
				self.reglist_final.append(tmpmap[0])
				self.reglist_final.append(tmpmap[1])
				self.reglist_final.append(tmpmap[2])

			if datalist[x] == "Process":
				tmp = datalist[x+1]
				tmpproc = tmp.split(',')
				self.pid.append(int(tmpproc[0]))
				self.procname.append(tmpproc[1])

			if datalist[x] == "Bookmark":
				tmp = datalist[x+1]
				tmpbook = tmp.split(',')
				self.bookmarkaddress.append(tmpbook[0])
				self.bookmarktext.append(tmpbook[1])

			if datalist[x] == "Processor":
				self.processor = datalist[x+1]

			if datalist[x] == "IOSVersion":
				self.IOSVersion = datalist[x+1]
			
			if datalist[x] == "Heapstart":
				self.heapstart = datalist[x+1]

			if datalist[x] == "Datastart":
				self.datastart = datalist[x+1]

			if datalist[x] == "Teststart":
				self.textstart = datalist[x+1]

			if datalist[x] == "Config":
				self.showrun = datalist[x+1]

			x = x + 2

		self.sessionfile = path
		self.win.Title = "IODIDE - " + path
		self.win.statusbar.SetStatusText("", 0)
		fp.close() 

#-------Gather memory map information------------------------------------------------------


    def	RouterShowRegion(self):

	if self.connect_mode == "Serial":
		self.ser.write("show region\n")	# get region info
		self.ser.readline()
		region = self.ser.read(900)

	else:

		self.tn.write("show region")	# get region info
		self.tn.write("\r\n")	
		self.tn.read_until("\n",1)
		region = self.tn.read_until("#",1)

	t,n = re.subn(';.*\n', '', region)
	self.reglist = t.split()

	x = 8

	while x < len(self.reglist)-5:
	
		if self.reglist[x+5] != "main":
			

			self.reglist_final.append(self.reglist[x])	# get start address
			if x < len(self.reglist) - 1:		
				x = x + 1
			else:
				break
			self.reglist_final.append(self.reglist[x])	# get end address
			if x < len(self.reglist) - 1:		
				x = x + 4
			else:
				break


			tmp = self.reglist[x]
			tmp = string.replace(tmp, ":", "." )
			self.reglist_final.append(tmp)	# get region name

			if self.reglist[x] == "main:heap":
				self.heapstart = self.reglist[x-5]
				self.heapstart = self.heapstart[2:]
				self.heapstart = string.lower(self.heapstart)

			if self.reglist[x] == "main:data":
				self.datastart = self.reglist[x-5]
				self.datastart = self.datastart[2:]
				self.datastart = string.lower(self.datastart)

			if self.reglist[x] == "main:text":
				self.textstart = self.reglist[x-5]
				self.textstart = self.textstart[2:]
				self.textstart = string.lower(self.textstart)

			if x < len(self.reglist) - 1:		
				x = x + 1
			else:
				break	

		else:
	
			x = x + 6
	
	#####cater for the extra text at the end of the show region command sometimes
	
	x = 0	
	regionlist = []
	while x < len(self.reglist_final)-1:
		temp = self.reglist_final[x]
		temp = temp[:2]
		if temp != "0x":
			self.reglist_final = regionlist
			return 0
		regionlist.append(self.reglist_final[x])
		regionlist.append(self.reglist_final[x+1])
		regionlist.append(self.reglist_final[x+2])
		x = x + 3

	self.reglist_final = regionlist
	return 0


#-------Gather process information---------------------------------------------------------


    def	RouterShowProcess(self):

	if self.connect_mode == "Serial":
		self.ser.write("show processes\n")	# get process info
		self.ser.readline()
		self.ser.readline() # ignore headings
		self.ser.readline() # ignore headings

	else:
		self.tn.write("show processes")	# get process info
		self.tn.write("\r\n")	# get process info
		self.tn.read_until("\n",1)
		self.tn.read_until("\n",1)
		self.tn.read_until("\n",1)
		
	reply ="   "
	complete_reply = ""


	if self.connect_mode == "Serial":
		reply = self.ser.readline()
	else:
		reply = self.tn.read_until("\n")

	while reply[len(reply)-1] != "#":
		if reply[0:4] == " PID":
			if self.connect_mode == "Serial":
				reply = self.ser.readline()
			else:
				reply = self.tn.read_until("\n")

		self.pid.append(int(reply[0:4]))
		self.procname.append(reply[64:len(reply)-2])  
		if self.connect_mode == "Serial":		
			reply = self.ser.readline()
		else:
			reply = self.tn.read_until("\n",1)
			if reply == "":
				reply = self.tn.read_some()
	return 0


#-------Gather running config information--------------------------------------------------


    def	RouterShowRun(self):

	if self.connect_mode == "Serial":
		self.ser.write("show run\n")	# get running config
		self.ser.readline()
		self.ser.readline()
		self.ser.readline()
		self.ser.readline()
		self.ser.readline()
	else:
		self.tn.write("show run")	# get running config
		self.tn.write("\r\n")		
		self.tn.read_until("\n",1)
		self.tn.read_until("\n",1)
		self.tn.read_until("\n",1)	
		self.tn.read_until("\n",1)
		self.tn.read_until("\n",1)

	reply = "  "
		
	while reply != "end\r\n":
		if self.connect_mode == "Serial":
			reply = self.ser.readline()
		else:
			reply = self.tn.read_until("\n")
		self.showrun = self.showrun + reply 
	
	#self.showrun = self.showrun[29:] 
	self.showrun = string.replace(self.showrun, ":", "" )                           
	self.showrun = string.replace(self.showrun, "\r\n", "<br>" )

	# mop up the trailing text

	if self.connect_mode == "Serial":
		reply = self.ser.readline()
	else:
		reply = self.tn.read_until("\n")

	
	if self.connect_mode == "Serial":
		self.ser.write("\n") 
		self.ser.readline()

	else:
		self.tn.write("\r\n")  
		self.tn.read_until("#",1)

	return 0


#-------Detect processor-------------------------------------------------------------------


    def	DetectProcessor(self):
	
	x = 0
	y = 1
	processor = ""

	if self.connect_mode == "Serial":
		self.ser.write("sh ver | inc \\) processor\n")	
		self.ser.readline()
		reply = self.ser.readline()
	
	else:
		
		self.tn.write("\n")
		self.tn.read_until("#",1)
		self.tn.write("sh ver | inc \\) processor\n")
		reply = self.tn.read_until("#",1)

	i = reply.find(' (')
	processor = ""
	x = i+2
	while reply[x] != ")":
		processor += reply[x]
		x += 1

	self.processor = processor


#-------Detect IOS version-------------------------------------------------------------------


    def	DetectIOSVersion(self):
	
	if self.connect_mode == "Serial":
		self.ser.write("sh ver | inc IOS\n")	
		self.ser.readline()
		reply = self.ser.readline()
	
	else:
		
		self.tn.write("\n")
		self.tn.read_until("#",1)
		self.tn.write("sh ver | inc IOS\n")
		reply = self.tn.read_until("#",1)

	i = reply.find('Version')
	i = i + 8

	self.IOSVersion = "%s" % reply[i:i+4]


#-------Collect registry information-------------------------------------------------------	

    def	CollectRegistry(self):
	
	x = 0
	y = 1
	processor = ""

	if self.connect_mode == "Serial":
		self.ser.write("sh registry brief | inc Stub\n")	
		self.ser.readline()
	else:		
		self.tn.write("sh registry brief | inc Stub")
		self.tn.write("\r\n")	
		self.tn.read_until("\n")

	reply ="   "
	address = ""
	function = ""
	tmp = []

	if self.connect_mode == "Serial":
		reply = self.ser.readline()
	else:
		reply = self.tn.read_until("\n")

	while reply[len(reply)-1] != "#":

		tmp = reply.split(':')
		function = tmp[0]		
		tmp = tmp[1].split('0x')
		address = tmp[1]

		if address[8] == '\r':
			address = address[0:8]
			address = string.lower(address)	
			self.registry.append(function)	# add the function name	
			self.registry.append(address)	# add the function address			

		if self.connect_mode == "Serial":		
			reply = self.ser.readline()
		else:
			reply = self.tn.read_until("\n",1)
			if reply == "":
				reply = self.tn.read_some()
	return 0


#-------Put router into gdb mode-----------------------------------------------------------


    def	EnterGdbMode(self):

	if self.gdb_connect_mode == "Kernel debugging":
		connect_string = "gdb kernel\r\n"
		self.enableObjects()
		self.win.statusbar.SetStatusText("Debugging Status: Kernel debugging", 2)
	elif self.gdb_connect_mode == "Process debugging (unreliable)":
		connect_string = "gdb debug "
		self.enableObjects()
		x = 0
		
		while x < len(self.procname)-1:
			if self.procname[x] == self.gdb_connect_debug_process:
				connect_string = connect_string + "%d" % self.pid[x]
				connect_string = connect_string + "\r\n"
				status = "Debugging Status: Debugging %s" % self.gdb_connect_debug_process
				self.win.statusbar.SetStatusText(status, 2)
				break
			x = x + 1
	else:
		connect_string = "gdb examine "
		self.enableObjects()

		# read only mode - cant do any of the following stuff so disable menus and buttons

		self.win.mb.Enable(self.win.ID_Continue, False)
		self.win.mb.Enable(self.win.ID_StepInto, False)
		self.win.mb.Enable(self.win.ID_StepOver, False)
		self.win.mb.Enable(self.win.ID_Jump, False)
		self.win.mb.Enable(self.win.ID_Upload, False)
		self.win.mb.Enable(self.win.ID_WriteReg, False)
		self.win.mb.Enable(self.win.ID_WriteMem, False)
		self.win.tb.EnableTool(self.win.ID_toolUpload,False)
		self.win.tb.EnableTool(self.win.ID_toolStep,False)
		self.win.tb.EnableTool(self.win.ID_toolStepover,False)
		self.win.tb.EnableTool(self.win.ID_toolContinue,False)
		self.win.mb.Enable(self.win.ID_SetBreakpoints, False)
		self.win.mb.Enable(self.win.ID_DelBreakpoints, False)
		self.win.tb.EnableTool(self.win.ID_toolBreakLabel,False)
		self.win.tb.EnableTool(self.win.ID_toolAddBreak,False)
		self.win.tb.EnableTool(self.win.ID_toolDelBreak,False)

		x = 0
		while x < len(self.procname)-1:
			if self.procname[x] == self.gdb_connect_examine_process:
				connect_string = connect_string + "%d" % self.pid[x]
				connect_string = connect_string + "\r\n"
				status = "Debugging Status: Debugging (read only) %s" % self.gdb_connect_examine_process
				self.win.statusbar.SetStatusText(status, 2)
				break
			x = x + 1

	if self.connect_mode == "Serial":
		self.ser.write(connect_string)	# put router into gdb mode
		self.ser.readline()
		self.ser.read(4)

	else:
		self.tn.write(connect_string)	# put router into gdb mode
		self.tn.read_until("||||",1)
		#self.tn.read_some()

	self.debugstatus = 1
	
	return 0


#-------Exit application-------------------------------------------------------------------

  
    def OnExit(self, evt):

	self.connect_after_continue = True
	
	if self.connectstatus == 1:
		if self.connect_mode == "Serial":
			self.ser.write("$c#63\n")	# exit gdb mode
			self.ser.readline()
			self.ser.close()	#close serial port
		else:
			self.tn.write("$c#63\n")	# exit gdb mode
			self.tn.read_until("\n",1)
			self.tn.close()	

	if self.session_changed == True:
		
		dlg = wx.MessageDialog(self.win,'Do you want to save the changes?','IODIDE', style=wx.YES | wx.NO | wx.CANCEL | wx.ICON_INFORMATION)        
		val = dlg.ShowModal()

            	if val == wx.ID_YES:
			dlg.Destroy()
                	self.OnSave(1)			

            	if val == wx.ID_NO:
			dlg.Destroy()
                
		if val == wx.ID_CANCEL:
			dlg.Destroy()
			return 0
        
        self.win.Close(True)


#-------Read stack and display in window---------------------------------------------------


    def OnReadStack(self):

	formatted = self.CreateGetMemoryReq(self.stack_pointer,"f0")
	result = self.GdbCommand(formatted) #set read memory command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	self.DisplayStack(result)


#-------Display stack----------------------------------------------------------------------


    def DisplayStack(self, result):

	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"

	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + result[0:8]
	displaybuffer = displaybuffer + "<br>"
	displaybuffer = displaybuffer + "</font>"	

	i = 0
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue	
    	while i < len(result):
		if result[i:i+8] == "fd0110df":
			break
		displaybuffer = displaybuffer + result[i:i+8]
		displaybuffer = displaybuffer + "<br>"
		i = i + 8
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "</font></body></html>"
	self.win.StackHTMLCtrl.SetPage(displaybuffer)
	return 0 


#-------Read registers and display in window-----------------------------------------------


    def OnReadReg(self, evt):

	"""
	Read the registers and display them in the registers window
	"""
	result = self.GdbCommand("$g#67\n") #set read registers command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	self.regbuffer = result
	self.DisplayRegistersPPC(result)


#-------Display registers for PowerPC------------------------------------------------------


    def DisplayRegistersPPC(self, regbuffer):
	"""
	Displays the returned registers in the registers window
	"""
	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"

    	i = 8
	j = 0
		
    	while i < 328:
		tmp = regbuffer[i:i+8]
		self.regvals[j] = tmp
		i = i + 8
		j = j + 1
	
	self.program_counter = self.regvals[32].encode('ascii')	# the unicode problem
	self.stack_pointer = self.regvals[1].encode('ascii')	# the unicode problem
	
	self.currentmem = self.program_counter
	self.currentdisass = self.program_counter

	i=0

	while i < 40:
			
		#Display first column
	
		displaybuffer = displaybuffer + self.regnames[i]
		
		if self.regvals[i] == self.lastregvals[i]:
			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
		else:
			if self.firstRun == 1:
				displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
			else:
				displaybuffer = displaybuffer + "<font color=\"#ff0000\">"
	
		displaybuffer = displaybuffer + self.regvals[i]
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "</font>"

		#Display second column

		displaybuffer = displaybuffer + self.regnames[i+1]
		
		if self.regvals[i+1] == self.lastregvals[i+1]:
			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
		else:
			if self.firstRun == 1:
				displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
			else:
				displaybuffer = displaybuffer + "<font color=\"#ff0000\">"
	
		displaybuffer = displaybuffer + self.regvals[i+1]
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "</font>"

		#Display third column
		
		displaybuffer = displaybuffer + self.regnames[i+2]
		
		if self.regvals[i+2] == self.lastregvals[i+2]:
			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
		else:
			if self.firstRun == 1:
				displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
			else:
				displaybuffer = displaybuffer + "<font color=\"#ff0000\">"
	
		displaybuffer = displaybuffer + self.regvals[i+2]
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "</font>"

		#Display forth column

		displaybuffer = displaybuffer + self.regnames[i+3]
		
		if self.regvals[i+3] == self.lastregvals[i+3]:
			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
		else:
			if self.firstRun == 1:
				displaybuffer = displaybuffer + "<font color=\"#0000ff\">"
			else:
				displaybuffer = displaybuffer + "<font color=\"#ff0000\">"
	
		displaybuffer = displaybuffer + self.regvals[i+3]
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "</font>"

		displaybuffer = displaybuffer + "<br>"
		i = i + 4


	self.lastregvals[0:40] = self.regvals[0:40]
	self.firstRun = 0

	displaybuffer = displaybuffer[:-4] # remove last <br>
	
	displaybuffer = displaybuffer + "</font></body></html>"

	self.win.RegistersHTMLCtrl.SetPage(displaybuffer)

	return 0 


#-------Create new window to display memory---------------------------------------------


    def CreateMemoryWindow (self):

	win = wx.Frame(self.win, -1, "Memory",size=(700,340))
	win.Show(True)
	return win


#-------Read memory and display in window-----------------------------------------------


    def OnReadMem(self, evt):
	"""
	Read the memory and display them in the memory window
	"""
	address = ""
	if self.readmemusepc == 1:
		address = self.program_counter	
	else:
		address = self.currentmem

	if self.dispDialog == 1:

		dlg = wx.TextEntryDialog(self.win, 'Enter the address to read memory from','Read Memory')
		dlg.SetValue(self.datastart)
		address = ""
        	if dlg.ShowModal() == wx.ID_OK:
            		address = dlg.GetValue()
			address = string.lower(address)
        	dlg.Destroy()

		if address == "":
			return 1

		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1
		
	formatted = self.CreateGetMemoryReq(address,"f0")

	result = self.GdbCommand(formatted) #set read memory command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	if not self.memreadwin:
            	self.memreadwin = self.CreateMemoryWindow ()

		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.memreadwin.SetIcon(icon) 

		self.MemoryHTMLCtrl = wx.html.HtmlWindow(self.memreadwin, -1, wx.DefaultPosition, wx.Size(700, 195))

#--------Toolbar stuff---------------------------------------------------------------------

		memtoolbar = self.memreadwin.CreateToolBar()
		
		memtoolbar.AddSimpleTool(ID_mem_back, wx.Image('images/av_back_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Display previous memory', 'Display previous memory')
        	self.win.Bind(wx.EVT_TOOL, self.OnMemBackClick, id=ID_mem_back)

		memtoolbar.AddSimpleTool(ID_mem_forward, wx.Image('images/av_play_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Display next memory', 'Display next memory')
		self.win.Bind(wx.EVT_TOOL, self.OnMemForwardClick, id=ID_mem_forward)

		memtoolbar.AddSeparator()

		search = TestSearchCtrl(memtoolbar, size=(150,-1), doSearch=self.DoMemSearch)
        	memtoolbar.AddControl(search)

		memtoolbar.AddSimpleTool(ID_search_mem_next, wx.Image('images/forward_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Find next', 'Find next')

		self.win.Bind(wx.EVT_TOOL, self.OnSearchNext, id=ID_search_mem_next)
		

		memtoolbar.Realize()
        	self.win.Centre()
        	self.win.Show(True)
		
	self.DisplayMemory (address,result) 
	self.memreadwin.SetFocus()
	self.currentmem = address


#-------Perform a search from the show memory toolbar--------------------------------------

    def DoMemSearch (self, text):
	
	if text == "":
		return False
	self.searchterm = text
	self.dispDialog = 0
	self.OnSearch(1)
	self.dispDialog = 1
	return True


#-------Perform a search from the show memory toolbar--------------------------------------


    def DoDisSearch (self, text):

	if text == "":
		return False
	self.dissearch = True
	self.disasssearchterm = text
	self.dispDialog = 0
	self.OnSearch(1)
	self.dispDialog = 1
	self.dissearch = False
	return True



#-------Format a gdb read memory request---------------------------------------------------


    def CreateGetMemoryReq(self, address, len):
	"""
	Creates a gdb request for memory and returns the formatted request
	"""
	address = "m" + address + "," + len
	formatted = self.checksum(address)
	formatted = formatted + "\n"
	return formatted


#-------Display bytes of memory------------------------------------------------------------


    def DisplayMemory(self, address, memory):

	# get ASCII data

	addr = int(address[0:8],16)
	i = 0
	data = ""
	datavals=[]
	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"


	while i < len(memory):
		tmp = memory[i:i+2]

		if int(tmp[0] + tmp[1],16) == 60 or int(tmp[0] + tmp[1],16) == 62:
			data = "."
	
		elif int(tmp[0] + tmp[1],16) == 38:
			data = "."

		elif int(tmp[0] + tmp[1],16) > 31 and int(tmp[0] + tmp[1],16) < 127:
			data = "%c" % int(tmp[0] + tmp[1],16)
		else:
			data = "."	

		datavals.append (data)
		i = i + 2

	#datavals contains the ASCII

	x = y = z = i = 0	
	
	found = 0
	while i < len(self.reglist_final):
		if addr >= int(self.reglist_final[i],16) and addr <= int(self.reglist_final[i+1],16):
			displaybuffer = displaybuffer + self.reglist_final[i+2]
			found = 1
			break
		i = i + 3

	if found == 0:
		displaybuffer = displaybuffer + "unknown"			

	displaybuffer = displaybuffer + ":"
	i = 0
	displaybuffer = displaybuffer + "%08x " % addr	#print address 
	

	for x in range (0, len (memory)):	#loop thorough all bytes (two digits per byte)

		
		if (x % 8) == 0 and x > 0:
			displaybuffer = displaybuffer + "&nbsp;"
		
		
		if (x % 32) == 0 and x > 0:		#have 16 bytes been printed?
			addr = addr + 16		#yes
			
			displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
			displaybuffer = displaybuffer + "&nbsp;&nbsp;"
			for y in range (z, z+16):
				displaybuffer = displaybuffer + datavals[y]
			displaybuffer = displaybuffer + "</font>"

			displaybuffer = displaybuffer + "<br>"

			found = 0
			while i < len(self.reglist_final):
				if addr >= int(self.reglist_final[i],16) and addr <= int(self.reglist_final[i+1],16):
					displaybuffer = displaybuffer + self.reglist_final[i+2]
					found = 1
					break
				i = i + 3	

			if found == 0:
				displaybuffer = displaybuffer + "unknown"

			displaybuffer = displaybuffer + ":"
			i = 0
			displaybuffer = displaybuffer + "%08x " % addr			
			z = z + 16
		
		displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		displaybuffer = displaybuffer + memory[x]
		displaybuffer = displaybuffer + "</font>"	
	
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
	for y in range (z, z+16):
		displaybuffer = displaybuffer + datavals[y]
	displaybuffer = displaybuffer + "</font>"

	displaybuffer = displaybuffer + "</font></body></html>"
	self.MemoryHTMLCtrl.SetPage(displaybuffer)


#-------Move back a page in memory---------------------------------------------------------


    def OnMemBackClick(self, evt):
	
	self.readmemusepc = 0
	tempmem = "0x" + self.currentmem
	tempmem2 = int (tempmem,16)
	tempmem2 = tempmem2 - 0xf0
	tempmem = "%08x" % tempmem2
	self.currentmem = tempmem
	self.dispDialog = 0
	self.OnReadMem(1)
	self.dispDialog = 1
	self.readmemusepc = 1


#-------Move forward a page in memory------------------------------------------------------


    def OnMemForwardClick(self, evt):
	
	self.readmemusepc = 0
	tempmem = "0x" + self.currentmem
	tempmem2 = int (tempmem,16)
	tempmem2 = tempmem2 + 0xf0
	tempmem = "%08x" % tempmem2
	self.currentmem = tempmem
	self.dispDialog = 0
	self.OnReadMem(1)
	self.dispDialog = 1
	self.readmemusepc = 1


#-------Create new window to display heap--------------------------------------------------


    def CreateHeapWindow (self):

	win = wx.Frame(self.win, -1, "Decode Heap Blocks",size=(650,610))
	win.Show(True)
	return win


#-------Create new window to display memory map--------------------------------------------


    def CreateMemmapWindow (self):

	win = wx.Frame(self.win, -1, "Memory map",size=(420,400))
	win.Show(True)
	return win


#-------Create new window to display running config----------------------------------------


    def CreateRunningConfigWindow (self):

	win = wx.Frame(self.win, -1, "Running config",size=(600,600))
	win.Show(True)
	return win


#-------Create new window to display processes---------------------------------------------


    def CreateProcessesWindow (self):

	win = wx.Frame(self.win, -1, "Processes",size=(320,400))
	win.Show(True)
	return win


#-------Create new window to display registry information----------------------------------


    def CreateRegistryWindow (self):

	win = wx.Frame(self.win, -1, "Registry information",size=(700,400))
	win.Show(True)
	return win


#-------Display registry information-------------------------------------------------------


    def OnDisplayRegistry (self, evt):
	y = 0

	if not self.registry:
		wx.MessageBox("No registry information available", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return(1)

	if not self.registrywin:
            	self.registrywin = self.CreateRegistryWindow ()
		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.registrywin.SetIcon(icon)
		self.RegistryHTMLCtrl = wx.html.HtmlWindow(self.registrywin, -1, wx.DefaultPosition, wx.Size(692, 400))

	self.registrywin.SetFocus()

	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"
	while y < len (self.registry):
		tmp = self.registry[y]
		tmplist = tmp.split('/')
		displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		displaybuffer = displaybuffer + self.registry[y+1]  	#address
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;Registry:&nbsp;"
		tmp = string.replace(tmplist[0], " ", "" )
		displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
		displaybuffer = displaybuffer + tmplist[0]		#registry
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;Service:&nbsp;"
		tmp = string.replace(tmplist[1], " ", "" )
		displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
		displaybuffer = displaybuffer + tmp			#service
		displaybuffer = displaybuffer + "()"
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "<br>"
		y = y + 2

	displaybuffer = displaybuffer + "</font></body></html>"
	self.RegistryHTMLCtrl.SetPage(displaybuffer)


#-------Display running config-------------------------------------------------------------


    def OnRunningConfig(self, evt):

	if not self.runningconfigwin:
            	self.runningconfigwin = self.CreateRunningConfigWindow ()
		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.runningconfigwin.SetIcon(icon)
		self.RunningConfigHTMLCtrl = wx.html.HtmlWindow(self.runningconfigwin, -1, wx.DefaultPosition, wx.Size(592, 600))

	self.runningconfigwin.SetFocus()

	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"

	displaybuffer = displaybuffer + self.showrun
	displaybuffer = displaybuffer + "</font></body></html>"
	self.RunningConfigHTMLCtrl.SetPage(displaybuffer)


#-------Display processes------------------------------------------------------------------


    def OnProcesses(self, evt):

	i = 0
	if not self.processeswin:
            	self.processeswin = self.CreateProcessesWindow ()
		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.processeswin.SetIcon(icon)
		self.ProcessesHTMLCtrl = wx.html.HtmlWindow(self.processeswin, -1, wx.DefaultPosition, wx.Size(312, 400))

	self.processeswin.SetFocus()

	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"
	displaybuffer = displaybuffer + "PID:&nbsp;Process:<br>"

	while i < len(self.pid) - 1:
		displaybuffer = displaybuffer + "<font color=\"#000000\">"
		displaybuffer = displaybuffer + "%d" % self.pid[i]
		if self.pid[i]<10:
			displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;&nbsp;"
		elif self.pid[i]<100:
			displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
		else:
			displaybuffer = displaybuffer + "&nbsp;&nbsp;"
		displaybuffer = displaybuffer + self.procname[i]
		displaybuffer = displaybuffer + "<br>"
		displaybuffer = displaybuffer + "</font>"
		i = i + 1

	displaybuffer = displaybuffer + "</font></body></html>"
	self.ProcessesHTMLCtrl.SetPage(displaybuffer)


#-------Display memory map-----------------------------------------------------------------


    def OnMemMap(self, evt):

	i = 0
	if not self.memmapwin:
            	self.memmapwin = self.CreateMemmapWindow ()
		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.memmapwin.SetIcon(icon)
		self.MemmapHTMLCtrl = MemmapHTML(self.memmapwin, -1, wx.DefaultPosition, wx.Size(420, 400))

	self.memmapwin.SetFocus()

	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"
	displaybuffer = displaybuffer + "General<br>"
	displaybuffer = displaybuffer + "-------<br>"	
	displaybuffer = displaybuffer + "Start:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;End:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Name:<br>"


	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "00000000"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;-&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "03ffffff"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + "physical address space"
	displaybuffer = displaybuffer + "</font><br>"

	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "40000000"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;-&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "4fffffff"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + "PCI memory space"
	displaybuffer = displaybuffer + "</font><br>"

	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "67000000"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;-&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "67ffffff"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + "NVRAM, WIC, internal regs"
	displaybuffer = displaybuffer + "</font><br>"

	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "68000000"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;-&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "6800ffff"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + "PCI config / IO"
	displaybuffer = displaybuffer + "</font><br>"

	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "68010000"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;-&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "6801ffff"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + "PowerQUICC regs"
	displaybuffer = displaybuffer + "</font><br>"

	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "fff03000"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;-&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000000\">"
	displaybuffer = displaybuffer + "fff7ffff"
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	displaybuffer = displaybuffer + "ROMMON"
	displaybuffer = displaybuffer + "</font><br><br>"

	displaybuffer = displaybuffer + "Specific<br>"	
	displaybuffer = displaybuffer + "--------<br>"
	displaybuffer = displaybuffer + "Start:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;End:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Name:<br>"


	while i < len(self.reglist_final) - 1:
		displaybuffer = displaybuffer + "<font color=\"#000000\">"
		displaybuffer = displaybuffer + self.reglist_final[i].lower()[2:]
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "&nbsp;-&nbsp;"	
		displaybuffer = displaybuffer + "<font color=\"#000000\">"		
		displaybuffer = displaybuffer + self.reglist_final[i+1].lower()[2:]
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
		displaybuffer = displaybuffer + self.reglist_final[i+2]
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "<br>"
		i = i + 3

	displaybuffer = displaybuffer + "</font></body></html>"
	self.MemmapHTMLCtrl.SetPage(displaybuffer)	


#-------Read heap memory and display in window---------------------------------------------


    def OnReadHeap(self, evt):
	"""
	Read the memory and display them in the memory window
	"""
	address = ""
	
	
	if self.dispDialog == 1:

		dlg = wx.TextEntryDialog(self.win, 'Enter the address of a heap block','Display heap blocks')
		dlg.SetValue(self.heapstart)
		address = ""
        	if dlg.ShowModal() == wx.ID_OK:
            		address = dlg.GetValue()
			address = string.lower(address)
		
		if address == "":
			return 1
		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

        	dlg.Destroy()		
	else:
		address = self.currentheap
		if address == "":
			return 1
		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1
		
	if self.IOSVersion == "12.4" or self.IOSVersion == "12.5":
		formatted = self.CreateGetMemoryReq(address,"30")
	else:
		formatted = self.CreateGetMemoryReq(address,"28")

	result = self.GdbCommand(formatted) #set read memory command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	if not self.heapreadwin:
            	self.heapreadwin = self.CreateHeapWindow ()

		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.heapreadwin.SetIcon(icon)

		self.HeapHTMLCtrl = MemmapHTML(self.heapreadwin, -1, wx.DefaultPosition, wx.Size(650, 600))

#--------Toolbar stuff---------------------------------------------------------------------

		heaptoolbar = self.heapreadwin.CreateToolBar()
		
		heaptoolbar.AddSimpleTool(ID_block_back, wx.Image('images/av_back_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Display previous block', 'Display previous block')
        	self.win.Bind(wx.EVT_TOOL, self.OnBlockBackClick, id=ID_block_back)

		heaptoolbar.AddSimpleTool(ID_block_forward, wx.Image('images/av_play_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Display next block', 'Display next block')
		self.win.Bind(wx.EVT_TOOL, self.OnBlockForwardClick, id=ID_block_forward)		

		heaptoolbar.Realize()
        	
	self.heapreadwin.SetFocus()	
	self.DisplayHeap (address,result) 
	self.currentheap = address


#-------Display bytes of heap memory------------------------------------------------------------


    def DisplayHeap(self, address, memory):
	
	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"
	displaybuffer = displaybuffer + "Collecting data - please be patient..."
	displaybuffer = displaybuffer + "</font></body></html>"
	self.HeapHTMLCtrl.SetPage(displaybuffer)
	# get ASCII data

	addr = int(address[0] + address[1] + address[2] + address[3] + address[4] + address[5] + address[6] + address[7],16)
	blockvals=[]
	x = 0
	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"

	while x < len(memory):
		
		tmp = memory[x:x+8]
		blockvals.append(tmp)
		x = x + 8
	
	displaybuffer = displaybuffer + "<font color=\"#657383\">"	#grey
	displaybuffer = displaybuffer + "=========================================================================<br>"
	displaybuffer = displaybuffer + "</font>"

	displaybuffer = displaybuffer + "Block addr:&nbsp;&nbsp;&nbsp;"  
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + "%08x<br>" % addr	#print address	
	displaybuffer = displaybuffer + "</font>"

	displaybuffer = displaybuffer + "<font color=\"#657383\">"	#grey
	displaybuffer = displaybuffer + "=========================================================================<br>"
	displaybuffer = displaybuffer + "</font>"

	displaybuffer = displaybuffer + "Magic:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[0]
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>PID:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[1]
	displaybuffer = displaybuffer + "</font>"

	if self.IOSVersion != "12.4" and self.IOSVersion != "12.5":
		displaybuffer = displaybuffer + "<br>Alloc check:&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		displaybuffer = displaybuffer + blockvals[2]
		displaybuffer = displaybuffer + "</font>"

	displaybuffer = displaybuffer + "<br>Alloc name:&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
	formatted = self.CreateGetMemoryReq(blockvals[3],"28")	
	result = self.GdbCommand(formatted.encode('ascii')) #set read memory command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1


	displaybuffer = displaybuffer + "\""
	x = 0
	while int(result[x] + result[x+1],16) != 0:	
		displaybuffer = displaybuffer + "%c" % int(result[x] + result[x+1],16)
		x = x + 2
	displaybuffer = displaybuffer + "\""
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>Alloc PC:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[4]
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>Next block:&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[5]
	self.nextblock = blockvals[5]
	self.nextblock = self.nextblock.encode('ascii')

	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>Prev block:&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[6]
	self.prevblock = blockvals[6]
	self.prevblock = self.prevblock.encode('ascii')

	tempmem = "0x" + self.prevblock		# for some reason prevblock is 0x14 larger
	tempmem2 = int (tempmem,16)
	tempmem2 = tempmem2 - 0x14
	self.prevblock = "%08x" % tempmem2

	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>Block size:&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[7]
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>Ref number:&nbsp;&nbsp;&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[8]
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>Last Dealloc:&nbsp;"
	displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
	displaybuffer = displaybuffer + blockvals[9]
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "<br>"

	if self.IOSVersion == "12.4" or self.IOSVersion == "12.5":
		displaybuffer = displaybuffer + "Unknown:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		displaybuffer = displaybuffer + blockvals[10]
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "<br>"
		displaybuffer = displaybuffer + "Unknown:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
		displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		displaybuffer = displaybuffer + blockvals[11]
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "<br>"



	displaybuffer = displaybuffer + "<font color=\"#657383\">"	#grey
	displaybuffer = displaybuffer + "=========================================================================<br>"
	displaybuffer = displaybuffer + "</font>"

	displaybuffer = displaybuffer + "Block data: (max 240 bytes - for more data use \"View -> Display memory\")<br>"

	displaybuffer = displaybuffer + "<font color=\"#657383\">"	#grey
	displaybuffer = displaybuffer + "=========================================================================<br>"
	displaybuffer = displaybuffer + "</font>"

	tempmem = "0x" + address	# add 40 bytes to move onto data portion of block
	tempmem2 = int (tempmem,16)
	if self.IOSVersion == "12.4" or self.IOSVersion == "12.5":
		tempmem2 = tempmem2 + 48
	else:
		tempmem2 = tempmem2 + 40

	address = "%08x" % tempmem2

	redzone = 0

	displaybuffercache = displaybuffer
	displaybuffer = displaybuffer + "</font></body></html>"
	self.HeapHTMLCtrl.SetPage(displaybuffer)
	displaybuffer = displaybuffercache

	while redzone == 0:

		wx.Yield()
		formatted = self.CreateGetMemoryReq(address,"f0")

		redzone = 1 ##### here to display just one page of memory #####

		memory = self.GdbCommand(formatted) #set read memory command

		if memory == "E03":
			wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

		wx.Yield()
		addr = int(address[0] + address[1] + address[2] + address[3] + address[4] + address[5] + address[6] + address[7],16)
		i = 0
		data = ""
		datavals=[]
	
		while i < len(memory):
			tmp = memory[i:i+2]

			if int(tmp[0] + tmp[1],16) == 60 or int(tmp[0] + tmp[1],16) == 62:
				data = "."

			elif int(tmp[0] + tmp[1],16) == 38:
				data = "."

			elif int(tmp[0] + tmp[1],16) > 31 and int(tmp[0] + tmp[1],16) < 127:
				data = "%c" % int(tmp[0] + tmp[1],16)
			else:
				data = "."	

			datavals.append (data)
			i = i + 2

		#datavals contains the ASCII

		x = y = z = i = 0	
	
		while i < len(self.reglist_final):
			if addr >= int(self.reglist_final[i],16) and addr <= int(self.reglist_final[i+1],16):
				displaybuffer = displaybuffer + self.reglist_final[i+2]
				break
			i = i + 3			

		displaybuffer = displaybuffer + ":"
		i = 0
		displaybuffer = displaybuffer + "%08x " % addr	#print address 
	
		a = 0
		for x in range (0, len (memory)):	#loop thorough all bytes (two digits per byte)
			
			wx.Yield()
			if memory[x:x+8] == "fd0110df":
				redzone = 1
				break		

			if (x % 8) == 0 and x > 0:

				displaybuffer = displaybuffer + "&nbsp;"
				
			if (x % 32) == 0 and x > 0:		#have 16 bytes been printed?

				addr = addr + 16		#yes
				a = 0
			
				displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
				displaybuffer = displaybuffer + "&nbsp;&nbsp;"
				for y in range (z, z+16):
					displaybuffer = displaybuffer + datavals[y]
				displaybuffer = displaybuffer + "</font>"

				displaybuffer = displaybuffer + "<br>"

				while i < len(self.reglist_final):
					if addr >= int(self.reglist_final[i],16) and addr <= int(self.reglist_final[i+1],16):
						displaybuffer = displaybuffer + self.reglist_final[i+2]
						break
					i = i + 3	

				displaybuffer = displaybuffer + ":"
				i = 0
				displaybuffer = displaybuffer + "%08x " % addr			
				z = z + 16
		
			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
			displaybuffer = displaybuffer + memory[x]
			displaybuffer = displaybuffer + "</font>"	
			a = a + 1	

		if a != 32:			# cater for the situation where less than 16 chars are displayed 
			c = a

			if c > 23:
				c = 33 -c	
			elif c > 15:
				c = 34 - c
			elif c > 7:
				c = 35 - c
			for b in range (0, c):
				displaybuffer = displaybuffer + "&nbsp;"

		displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;"

		
		if a != 32:			# cater for the situation where less than 16 chars are displayed 
			a = a / 2
			for y in range (z, z+a):				
				displaybuffer = displaybuffer + datavals[y]

		else:
			for y in range (z, z+16):				
				displaybuffer = displaybuffer + datavals[y]

		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "<br>"

		a = a + 1
		tempmem = "0x" + address	
		tempmem2 = int (tempmem,16)
		tempmem2 = tempmem2 + 0xf0
		address = "%08x" % tempmem2

		displaybuffercache = displaybuffer
		displaybuffer = displaybuffer + "</font></body></html>"
		self.HeapHTMLCtrl.SetPage(displaybuffer)
		displaybuffer = displaybuffercache
		
	#displaybuffer = displaybuffer + "</font></body></html>"
	#self.HeapHTMLCtrl.SetPage(displaybuffer)


#-------Move back a block------------------------------------------------------------------


    def OnBlockBackClick(self, evt):
	
	if self.currentheap == self.heapstart:
		return 1
	self.currentheap = self.prevblock	
	self.dispDialog = 0
	self.OnReadHeap(1)
	self.dispDialog = 1

#-------Move forward a block---------------------------------------------------------------


    def OnBlockForwardClick(self, evt):

	self.currentheap = self.nextblock	
	self.dispDialog = 0
	self.OnReadHeap(1)
	self.dispDialog = 1


#-------Display Disassembled memory---------------------------------------------------------


    def OnDisassemble(self, evt):
	"""
	Read the memory and display in the disassemble window
	"""
	if self.disassusepc == 1:
		address = self.program_counter	
	else:
		address = self.currentdisass


	if self.dispDialog == 1:

		dlg = wx.TextEntryDialog(self.win, 'Enter the address to disassemble from','Disassemble')
		dlg.SetValue(self.textstart)
		address = ""
        	if dlg.ShowModal() == wx.ID_OK:
            		address = dlg.GetValue()
			address = string.lower(address)
        	dlg.Destroy()
		if address == "":
		  	return 1
		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

	formatted = self.CreateGetMemoryReq(address,"f0")

	result = self.GdbCommand(formatted) #set read memory command

	if result == "E03":
		displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"
		displaybuffer = displaybuffer + "Address %s can not be read" % address
		displaybuffer = displaybuffer + "</font></body></html>"
		self.win.DisassembleHTMLCtrl.SetPage(displaybuffer)
		return 1
			
	self.currentinstruction = result[0:8]
	self.nextinstruction = result[8:16]

	self.DisassembleMemoryPPC (address,result) 
	self.currentdisass = address

#------------------------------------------------------------------------------------------

    def OnRightClick(self,event):
	address = event.GetLabelText()
	print address



#-------Disassemble memory-----------------------------------------------------------------


    def DisassembleMemoryPPC(self, address, memory):

	addr = int(address[0:8],16)
	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"
	
	dis = cdll.disass #access disass.dll
	result = create_string_buffer('\000' * 32)
	
	i = j = l = x = y = 0
	res = ""

	while i < len(memory)-8:
		k = 0
		
		tmp = memory[i:i+8]
		word =int(tmp ,16)
		dis.disass_ppc(result,addr,word)	
		
		while result[k] != "\x00":
			res = res + result[k]
			k = k + 1				
		
		res = string.replace(res, "\n", "" )		
		res = string.replace(res, "\t", "&nbsp;" )	

		tmp_address = "%08x" % addr
		indexval = 0xffff

		try:
			indexval = self.breakpoints.index(tmp_address)
		except:
			pass


		
		if address == self.program_counter and l == 0:
			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		else:
			displaybuffer = displaybuffer + "<font color=\"#000000\">"	#black

		x = 0

		found = 0

		while x < len(self.reglist_final)-2:
			if addr >= int(self.reglist_final[x],16) and addr <= int(self.reglist_final[x+1],16):
				if indexval != 0xffff:
					displaybuffer = displaybuffer + "<font color=\"#ff0000\">"
					displaybuffer = displaybuffer + self.reglist_final[x+2]
					displaybuffer = displaybuffer + "</font>"
					found = 1
					break
				else:
					displaybuffer = displaybuffer + self.reglist_final[x+2]
					found = 1
					break
			x = x + 3

		if found == 0:
			if indexval != 0xffff:
				displaybuffer = displaybuffer + "<font color=\"#ff0000\">"
				displaybuffer = displaybuffer + "unknown"
				displaybuffer = displaybuffer + "</font>"
			else:
				displaybuffer = displaybuffer + "unknown"


		displaybuffer = displaybuffer + ":&nbsp;"
		displaybuffer = displaybuffer + "</font>"


		if indexval != 0xffff:
			displaybuffer = displaybuffer + "<font color=\"#ff0000\">"	#red
			displaybuffer = displaybuffer + "%08x" % addr
			displaybuffer = displaybuffer + "</font>"

		elif address == self.program_counter and l == 0:
			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
			l = 1
			displaybuffer = displaybuffer + "%08x" % addr
			displaybuffer = displaybuffer + "</font>"
			
		else:
			displaybuffer = displaybuffer + "%08x" % addr

		displaybuffer = displaybuffer + "&nbsp;"

		while j < 7:

			if indexval != 0xffff:
				tmp = self.breakpointdata[indexval]			

			displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
			
			displaybuffer = displaybuffer + "&nbsp;"

			displaybuffer = displaybuffer + tmp[j]
			displaybuffer = displaybuffer + tmp[j+1]

			displaybuffer = displaybuffer + "</font>"			
			j = j + 2

		j = 0

		displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
		displaybuffer = displaybuffer + "&nbsp;&nbsp;&nbsp;&nbsp;"

		if indexval == 0xffff:
			displaybuffer = displaybuffer + res
		else:
			
			k = 0
			res = ""
			tmp = self.breakpointdata[indexval]
			word =int(tmp ,16)
			dis.disass_ppc(result,addr,word)	
		
			while result[k] != "\x00":
				res = res + result[k]
				k = k + 1				
		
			res = string.replace(res, "\n", "" )		
			res = string.replace(res, "\t", "&nbsp;" )
			displaybuffer = displaybuffer + res


		displaybuffer = displaybuffer + "</font>"	

		currentaddr = "%08x" % addr
		
		while y < len (self.comments) - 1:
			if currentaddr == self.comments[y]:
				displaybuffer = displaybuffer + "<font color=\"#008000\">"	#dark green

				t=0
				while t < 28 - len(res):
					displaybuffer = displaybuffer + "&nbsp;"
					t = t + 1

				displaybuffer = displaybuffer + "#"


				displaybuffer = displaybuffer + self.comments[y+1]				
				displaybuffer = displaybuffer + "</font>"
			y = y + 2
			
		displaybuffer = displaybuffer + "<br>"	
		y = 0
		
		res = ""
		addr = addr + 4

		# Is it a branch command?
		
		if tmp[j:j+2] == "48" or tmp[j:j+2] == "4b":
			displaybuffer = displaybuffer + "<font color=\"#657383\">"	#grey
			displaybuffer = displaybuffer + "#&nbsp;-------------------------------------------------------<br><br>"
			displaybuffer = displaybuffer + "</font>"
		
		# Is it a blr command?

		if tmp[j:j+8] == "4e800020":

			displaybuffer = displaybuffer + "<font color=\"#657383\">"	#grey
			displaybuffer = displaybuffer + "#&nbsp;Function end<br><br>"
			displaybuffer = displaybuffer + "#&nbsp;================ Start of function ====================<br>"
			y = 0
			while y < len (self.registry):
				curaddr = "%08x" % addr
				if curaddr == self.registry[y+1]:
					tmp = self.registry[y]
					tmplist = tmp.split('/')
					displaybuffer = displaybuffer + "#&nbsp;Registry:&nbsp;"
					tmp = string.replace(tmplist[0], " ", "" )
					displaybuffer = displaybuffer + tmp
					displaybuffer = displaybuffer + "<br>"
					displaybuffer = displaybuffer + "#&nbsp;Service:&nbsp;&nbsp;"
					tmp = string.replace(tmplist[1], " ", "" )
					displaybuffer = displaybuffer + tmp
					displaybuffer = displaybuffer + "()"
					displaybuffer = displaybuffer + "<br>"
					displaybuffer = displaybuffer + "#&nbsp;-------------------------------------------------------<br><br>"
				y = y + 2
			displaybuffer = displaybuffer + "</font>"
			y = 0		
		i = i + 8

	displaybuffer = displaybuffer[:-11] # remove last <br>
	displaybuffer = displaybuffer + "</font>"
	displaybuffer = displaybuffer + "</font></body></html>"

	self.win.DisassembleHTMLCtrl.SetPage(displaybuffer)
	#self.win.DisassembleHTMLCtrl.LoadString(displaybuffer)

#-------Move back a page in memory---------------------------------------------------------


    def OnDisassBackClick(self, evt):
	
	self.disassusepc = 0
	tempmem = "0x" + self.currentdisass
	tempmem2 = int (tempmem,16)
	tempmem2 = tempmem2 - 0xec
	tempmem = "%08x" % tempmem2
	self.currentdisass = tempmem
	self.dispDialog = 0
	self.OnDisassemble(1)
	self.dispDialog = 1
	self.disassusepc = 1


#-------Move forward a page in memory------------------------------------------------------


    def OnDisassForwardClick(self, evt):
	
	self.disassusepc = 0
	tempmem = "0x" + self.currentdisass
	tempmem2 = int (tempmem,16)
	tempmem2 = tempmem2 + 0xec
	tempmem = "%08x" % tempmem2
	self.currentdisass = tempmem
	self.dispDialog = 0
	self.OnDisassemble(1)
	self.dispDialog = 1
	self.disassusepc = 1


#-------Search for next data in memory-----------------------------------------------------


    def OnSearchNext(self, evt):
	self.dispDialog = 0
	self.OnSearch(1)
	self.dispDialog = 1


#-------Search for next data in disassembler-----------------------------------------------


    def OnSearchNextDis(self, evt):
	if self.debugstatus == 0 or self.connectstatus == 0:
		return
	
	self.dissearch = True
	self.dispDialog = 0
	self.OnSearch(1)
	self.dispDialog = 1
	self.dissearch == False


#-------Search for data in memory----------------------------------------------------------


    def OnSearch(self, evt):
	if self.debugstatus == 0 or self.connectstatus == 0:
		return

	if self.dispDialog == 1:
		if self.memreadwin:
        		dlg = wx.TextEntryDialog(self.memreadwin, 'Enter the start address to search from','Search Memory - start address')
		else:
			dlg = wx.TextEntryDialog(self.win, 'Enter the start address to search from','Search Memory - start address')
	
		dlg.SetValue(self.datastart)

		start_address = ""

        	if dlg.ShowModal() == wx.ID_OK:
            		start_address = dlg.GetValue()
			start_address = string.lower(start_address)

        	dlg.Destroy()
		if start_address == "":
			return 1

		if self.memreadwin:
			if self.invalidaddress(start_address):		
				wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.memreadwin)
				return 1
		else:
			if self.invalidaddress(start_address):	
				wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self)
				return 1

		if self.memreadwin:
        		dlg = wx.TextEntryDialog(self.memreadwin, 'Enter the end address to search to','Search Memory - end address')
		else:
			dlg = wx.TextEntryDialog(self.win, 'Enter the end address to search to','Search Memory - end address')

		dlg.SetValue("ffffffff")

		end_address = ""

        	if dlg.ShowModal() == wx.ID_OK:
            		end_address = dlg.GetValue()
			end_address = string.lower(end_address)

        	dlg.Destroy()

		if end_address == "":
			return 1

		if self.memreadwin:
			if self.invalidaddress(end_address):		
				wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.memreadwin)
				return 1
		else:
			if self.invalidaddress(end_address):	
				wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self)
				return 1

		if self.memreadwin:
			dlg = wx.TextEntryDialog(self.memreadwin, 'Enter the search term','Search Memory - end address')
		else:
			dlg = wx.TextEntryDialog(self.win, 'Enter the search term','Search Memory - end address')

		
		search_term = ""

        	if dlg.ShowModal() == wx.ID_OK:
          	  	search_term = dlg.GetValue()

        	dlg.Destroy()
		if search_term == "":
			return 1

	else:

		if self.dissearch == True:

			tmpstart = int(self.currentdisass,16)
			tmpstart += 4
			start_address = "%08x" % tmpstart
			end_address = self.end_address
			search_term = self.disasssearchterm
			if search_term == "":
				return 1
		else:
			tmpstart = int(self.currentmem,16)
			tmpstart += 4
			start_address = "%08x" % tmpstart
			end_address = self.end_address
			search_term = self.searchterm	
			if search_term == "":
				return 1

	searchwin = self.CreateSearchWindow()

	image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
	icon = wx.EmptyIcon() 
	icon.CopyFromBitmap(image) 
	searchwin.SetIcon(icon) 

	searchwin.Center()
	g1 = wx.Gauge(searchwin, -1, 20000000, (5, 20), (200, 25))

	button = wx.Button(searchwin, 1003, "Cancel")
        button.SetPosition((70, 60))
        searchwin.Bind(wx.EVT_BUTTON, self.OnCancelSearch, button)	


	if search_term[0] == "\"" and search_term[len(search_term)-1] == "\"":
		search_term = search_term[1:-1]		#remove quotes
		newterm = ""
		for x in range (0, len(search_term)):
			newterm = newterm + "%02x" % ord(search_term[x])
			x = x + 1

		search_term = newterm		# search_term is now ASCII values of text search term

	start_addr = int(start_address,16)
	end_addr = int(end_address,16)
	search_length = end_addr - start_addr
	lentxt = "%02x" % search_length

	self.cancelsearch = False

	iterations = search_length / 200
	remainder = search_length % 200 

	gaugestep = 20000000 / iterations
	gaugeval = 0
	
	remainder_string = "%02x" % remainder

	current_address = start_address
	current_addr = int(current_address,16)
	z = i = 0
	y = 200 - len(search_term)


	while i < iterations:
		wx.Yield()
		if self.cancelsearch == True:
			searchwin.Close(True)
			return 0
		formatted = self.CreateGetMemoryReq(current_address,"c8")
		result = self.GdbCommand(formatted) #set read memory command	

		if result == "E03":
			wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			searchwin.Close(True)
			return 1
	
		x = z = 0
		while z < y:
			foundaddr = current_addr + z								
			if result[x:x+len(search_term)] == search_term:	

				if self.dissearch == True:
					self.dissearch = False
					self.disassusepc = 0
					self.currentdisass = "%08x" % foundaddr
					self.disasssearchterm = search_term
					self.end_address = end_address
					searchwin.Close(True)
					self.dispDialog = 0
					self.OnDisassemble(1)
					self.dispDialog = 1
					self.disassusepc = 1				
					return 0

				else:							
					self.readmemusepc = 0
					self.currentmem = "%08x" % foundaddr
					self.searchterm = search_term
					self.end_address = end_address
					searchwin.Close(True)
					self.dispDialog = 0
					self.OnReadMem(1)
					self.dispDialog = 1
					self.readmemusepc = 1				
					return 0
			x = x + 2
			z = z + 1

		current_addr = current_addr + y
		current_address = "%08x" % current_addr
		i = i + 1
		g1.SetValue(gaugeval)
		gaugeval = gaugeval + gaugestep

	#search the remainder of the memory

	formatted = self.CreateGetMemoryReq(current_address,remainder_string)
	result = self.GdbCommand(formatted) #set read memory command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		searchwin.Close(True)
		return 1

	x = z = 0
	while x < y:
		foundaddr = current_addr + z								
		if result[x:x+len(search_term)] == search_term:								
			self.readmemusepc = 0
			self.currentmem = "%08x" % foundaddr
			searchwin.Close(True)
			self.dispDialog = 0
			self.OnReadMem(1)
			self.dispDialog = 1
			self.readmemusepc = 1				
			return 0
		x = x + 2
		z = z + 1
	
	searchwin.Close(True)		
	wx.MessageBox("Search failed", caption="Failed", style=wx.OK|wx.ICON_ERROR, parent=self.win)
	return 1


    def OnCancelSearch (self,evt):
	self.cancelsearch = True


#-------Create new window to display search status------------------------------------


    def CreateSearchWindow (self):

	win = wx.Frame(self.win, -1, "Searching...",size=(220,120))
	win.Show(True)
	return win


#-------Write Registers--------------------------------------------------------------------


    def OnWriteReg(self, evt):
        
	"""
	Modify a register value 
	"""
	x = i = j = 0
	regbuf = ""
	tmpregvals=[]



	dlg = wx.TextEntryDialog(self.win, 'Enter the register name to modify','Write Register')
	reg = ""

        if dlg.ShowModal() == wx.ID_OK:
            	reg = dlg.GetValue()
		reg = string.lower(reg)

       	dlg.Destroy()
	if reg == "":
		wx.MessageBox("Invalid register", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1	

	found = 0
	while x < len(self.regnames2):
		if self.regnames2[x] == reg:
			found = 1
			break
		x = x + 1

	if found == 0:
		wx.MessageBox("Invalid register", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	dlg = wx.TextEntryDialog(self.win, 'Enter the data to write to the register','Write Register')

	data = ""

        if dlg.ShowModal() == wx.ID_OK:
            	data = dlg.GetValue()
		data = string.lower(data)
	
	dlg.Destroy()
	if data == "":		
		wx.MessageBox("Invalid data", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1
	try:
    		dummy = int(data,16)
	except:	
		wx.MessageBox("Invalid data", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	
	while i < len(self.regbuffer):
		tmp = self.regbuffer[i:i+8]
		tmpregvals.append(tmp)
		i = i + 8
	
	tmpregvals[x+1] = data	# write new register value to temp store

	while j < len (tmpregvals):
		regbuf = regbuf + tmpregvals[j]
		j = j + 1
	
	command = self.CreateWriteRegistersReq(regbuf)

	result = self.GdbCommand(command.encode('ascii')) #send write registers command
	result = self.GdbCommand("$g#67\n") #set read registers command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	x = x + 1 # ignore first entry 0x00000050
	x = x * 8

	if result [x:x+8] != data:			
		wx.MessageBox("Write Failed", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	self.OnReadReg(1)


#-------Format a write registers request---------------------------------------------------


    def CreateWriteRegistersReq(self, data):
	"""
	Creates a gdb request to write registers and returns the formatted request
	"""
	request = "G" + data
	formatted = self.checksum(request)
	formatted = formatted + "\n"
	return formatted


#-------Write Memory-----------------------------------------------------------------------


    def OnWriteMem(self, evt):
	"""
	Write data to a memory location 
	"""

	if self.dispDialog == 1:

		dlg = wx.TextEntryDialog(self.win, 'Enter the address to write data to','Write Address')
		address = ""

        	if dlg.ShowModal() == wx.ID_OK:
            		address = dlg.GetValue()
			address = string.lower(address)

       	 	dlg.Destroy()
		if address == "":
			return 1
		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

	else:

		address = self.currentclickaddress

	dlg = wx.TextEntryDialog(self.win, 'Enter data to write (four bytes only)','Write Data')
	data = ""

        if dlg.ShowModal() == wx.ID_OK:
            	data = dlg.GetValue()
		data = string.lower(data)

        dlg.Destroy()
	if data == "":		
		wx.MessageBox("Invalid data", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1
	try:
    		dummy = int(data,16)
	except:	
		wx.MessageBox("Invalid data", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	command = self.CreateWriteMemoryReq(address,data,"4")
	result = self.GdbCommand(command) #send write memory command

	command = self.CreateGetMemoryReq(address,"04")
	result = self.GdbCommand(command) #set read memory command
	
	if result == data:
		if self.dispDialog == 1:
			wx.MessageBox("Data Written", caption="Success", style=wx.OK|wx.ICON_INFORMATION, parent=self.win)
	else:	
		wx.MessageBox("Write Failed", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)	


#-------Format write memory request--------------------------------------------------------


    def CreateWriteMemoryReq(self, address, data, datalen):
	"""
	Creates a gdb request to write to memory and returns the formatted request Maddr,length:XX... 
	"""
	address = "M" + address + "," + datalen + ":" + data
	formatted = self.checksum(address)
	formatted = formatted + "\n"
	return formatted


#-------Add bookmarks----------------------------------------------------------------------


    def OnAddBookmarks(self, evt):

	x = 0

	if self.dispDialog == 1:

		dlg = wx.TextEntryDialog(self.bookmarkwin, 'Enter the address to set a bookmark at','Bookmark Address')

		address = ""

        	if dlg.ShowModal() == wx.ID_OK:
            		address = dlg.GetValue()
			address = string.lower(address)

        	dlg.Destroy()
		if address == "":
			return 1
		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)
			return 1
	else:

		address = self.currentclickaddress

	

	if self.bookmarkwin:
		print "here"
		dlg = wx.TextEntryDialog(self.bookmarkwin, 'Enter the bookmark text','Bookmark Text')
	else:		
		dlg = wx.TextEntryDialog(self.win, 'Enter the bookmark text','Bookmark Text')

	booktext = ""

        if dlg.ShowModal() == wx.ID_OK:
            booktext = dlg.GetValue()

        dlg.Destroy()

	temp_booktext = string.replace(booktext, " ", "" )
	if self.invalidstring(temp_booktext):
		if self.bookmarkwin:		
			wx.MessageBox("Invalid input - alphanumeric only", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)
		else:			
			wx.MessageBox("Invalid input - alphanumeric only", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	if len(self.bookmarkaddress) == 0:
		self.bookmarkaddress.append(address)
		self.bookmarktext.append(booktext) 

	else:

		while x < len(self.bookmarkaddress):
			if self.bookmarkaddress[x] == address:
				self.bookmarktext[x] = booktext
				break
			else:
				self.bookmarkaddress.append(address)
				self.bookmarktext.append(booktext)
				break	

			x = x + 1

	if self.dispDialog == 1:
		self.OnListBookmarks(1)


#-------Del bookmarks----------------------------------------------------------------------


    def OnDelBookmarks(self, evt):
	
	x = 0
	dlg = wx.TextEntryDialog(self.bookmarkwin, 'Enter the bookmark number','Bookmark number')
	dlg.SetValue("")
	number = ""

        if dlg.ShowModal() == wx.ID_OK:
            number = dlg.GetValue()

        dlg.Destroy()
	if number == "":		
		wx.MessageBox("Invalid bookmark number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)
		return 1
	try:
    		dummy = int(number)
	except:	
		wx.MessageBox("Invalid bookmark number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)
		return 1

	intnum = int(number)

	try:
		self.bookmarkaddress.remove(self.bookmarkaddress[intnum])
		self.bookmarktext.remove(self.bookmarktext[intnum])
	except:
		wx.MessageBox("Invalid bookmark number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)

	self.OnListBookmarks(1)


#-------Create new window to display bookmarks------------------------------------------


    def CreateBookmarkWindow (self):

	win = wx.Frame(self.win, -1, "Bookmarks",size=(620,340))
	win.Show(True)
	return win


#-------Read memory and display in window-----------------------------------------------


    def OnListBookmarks(self, evt):

	

	if not self.bookmarkwin:
            	self.bookmarkwin = self.CreateBookmarkWindow ()

		image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
		icon = wx.EmptyIcon() 
		icon.CopyFromBitmap(image) 
		self.bookmarkwin.SetIcon(icon) 

		self.BookmarkHTMLCtrl = wx.html.HtmlWindow(self.bookmarkwin, -1, wx.DefaultPosition, wx.Size(880, 195))

#--------Toolbar stuff---------------------------------------------------------------------

		memtoolbar = self.bookmarkwin.CreateToolBar()
		
		memtoolbar.AddSimpleTool(ID_add_bookmark, wx.Image('images/document_new_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Add bookmark', 'Add bookmark')
        	self.win.Bind(wx.EVT_TOOL, self.OnAddBookmarks, id=ID_add_bookmark)

		memtoolbar.AddSimpleTool(ID_del_bookmark, wx.Image('images/document_delete_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Delete bookmark', 'Delete bookmark')
		self.win.Bind(wx.EVT_TOOL, self.OnDelBookmarks, id=ID_del_bookmark)

		memtoolbar.AddSimpleTool(ID_goto_bookmark, wx.Image('images/bookmark_small.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Go to bookmark', 'Go to bookmark')
		self.win.Bind(wx.EVT_TOOL, self.OnGotoBookmark, id=ID_goto_bookmark)

		memtoolbar.Realize()
  
	self.bookmarkwin.SetFocus()

	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"

	x = 0
	while x < len(self.bookmarkaddress):
		displaybuffer = displaybuffer + "%d" % x 
		displaybuffer = displaybuffer + "&nbsp;&nbsp;" + self.bookmarkaddress[x] + "&nbsp;&nbsp;" 
		displaybuffer = displaybuffer + "<font color=\"#000080\">"	#dark blue
		displaybuffer = displaybuffer + "\"" + self.bookmarktext[x] + "\"" + "<br>"
		displaybuffer = displaybuffer + "</font>"
		x = x +1

	displaybuffer = displaybuffer + "</font></body></html>"
	self.BookmarkHTMLCtrl.SetPage(displaybuffer)
		

#-------Goto Bookmark----------------------------------------------------------------------


    def OnGotoBookmark(self, evt):


	x = 0
	dlg = wx.TextEntryDialog(self.bookmarkwin, 'Enter the bookmark number','Bookmark number')
	dlg.SetValue("")
	number = ""

        if dlg.ShowModal() == wx.ID_OK:
            number = dlg.GetValue()

        dlg.Destroy()
	if number == "":		
		wx.MessageBox("Invalid bookmark number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)
		return 1
	try:
    		dummy = int(number)
	except:	
		wx.MessageBox("Invalid bookmark number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)
		return 1

	try:
		self.currentdisass = self.bookmarkaddress[int(number)]
	except:
		wx.MessageBox("Invalid bookmark number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.bookmarkwin)
		return 1

	self.bookmarkwin.Close(True)
	
	self.disassusepc = 0
	self.dispDialog = 0
	self.OnDisassemble(1)
	self.dispDialog = 1
	self.disassusepc = 1


#-------Edit breakpoints-------------------------------------------------------------------


    def OnSetBreakpoints(self, evt):
	"""
	Set breakpoints 
	"""
	x = 0

	if self.dispDialog == 1:
		dlg = wx.TextEntryDialog(self.win, 'Enter the address to set a breakpoint at','Breakpoint Address')

		address = ""

       	 	if dlg.ShowModal() == wx.ID_OK:
            		address = dlg.GetValue()
			address = string.lower(address)

        	dlg.Destroy()
		if address == "":
			return 1
		if self.invalidaddress(address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

	else:

		address = self.currentclickaddress

	command = self.CreateGetMemoryReq(address,"04")
	result = self.GdbCommand(command) #set read memory command

	temp_address = address
	temp_result = result		

	command = self.CreateWriteMemoryReq(address,"7d821008","4")	#write breakpoint
	result = self.GdbCommand(command) #send write memory command

	command = self.CreateGetMemoryReq(address,"04")
	result = self.GdbCommand(command) #set read memory command
	
	if result != "7d821008":		
		wx.MessageBox("Breakpoint Set Failed", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1	

	self.breakpoints.append(temp_address)
	self.breakpointdata.append(temp_result)

	self.OnBreakpoints(1)
	self.dispDialog = 0
	self.disassusepc = 0
	self.OnDisassemble(1)
	self.disassusepc = 1
	self.dispDialog = 1


#-------Delete breakpoints-----------------------------------------------------------------


    def OnDelBreakpoints(self, evt):
	"""
	Delete breakpoints 
	"""

	if self.dispDialog == 1:
		dlg = wx.TextEntryDialog(self.win, 'Enter the breakpoint number to delete','Delete Breakpoint')
		dlg.SetValue("0")
		number = ""

        	if dlg.ShowModal() == wx.ID_OK:
           	 	number = dlg.GetValue()

        	dlg.Destroy()
		if number == "":		
			wx.MessageBox("Invalid breakpoint number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1
		try:
    			dummy = int(number)
		except:	
			wx.MessageBox("Invalid breakpoint number", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1
	
		breaknum = eval(number) 
	
	else:
		address = self.currentclickaddress
		breaknum = self.breakpoints.index(address)


	command = self.CreateWriteMemoryReq(self.breakpoints[breaknum],self.breakpointdata[breaknum],"4")   #write orig data back
	result = self.GdbCommand(command.encode('ascii')) #send write memory command

	command = self.CreateGetMemoryReq(self.breakpoints[breaknum],"04")
	result = self.GdbCommand(command) #set read memory command
	
	if result != self.breakpointdata[breaknum]:		
		wx.MessageBox("Breakpoint Remove Failed", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)	

	self.breakpoints.remove(self.breakpoints[breaknum])
	self.breakpointdata.remove(self.breakpointdata[breaknum])
	self.OnBreakpoints(1)
	self.dispDialog = 0
	self.disassusepc = 0
	self.OnDisassemble(1)
	self.disassusepc = 1
	self.dispDialog = 1


#-------View breakpoints-------------------------------------------------------------------

    def OnBreakpoints(self, evt):
	"""
	View breakpoints 
	"""
	x = 0
	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"black\">"
	while x < len(self.breakpoints):
		
		displaybuffer = displaybuffer + "%d:&nbsp;" % x
		displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		displaybuffer = displaybuffer + self.breakpoints[x]
		displaybuffer = displaybuffer + "</font>"
		displaybuffer = displaybuffer + "<br>"
		x = x + 1 

	displaybuffer = displaybuffer + "</font></body></html>"

	self.win.BreakpointsHTMLCtrl.SetPage(displaybuffer)
	return 0 


#-------Insert comment---------------------------------------------------------------------


    def OnComment(self, evt):

	if self.dispDialog == 1:

        	dlg = wx.TextEntryDialog(self.win, 'Enter the address at which the comment will be inserted','Comment address')

		dlg.SetValue("")

		comment_address = ""

        	if dlg.ShowModal() == wx.ID_OK:
            		comment_address = dlg.GetValue()
			comment_address = string.lower(comment_address)

        	dlg.Destroy()
		if comment_address == "":
			return 1
		if self.invalidaddress(comment_address):		
			wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

	else:

		comment_address = self.currentclickaddress

	dlg = wx.TextEntryDialog(self.win, 'Enter the comment','Comment')

	dlg.SetValue("")

	comment = ""

        if dlg.ShowModal() == wx.ID_OK:
            	comment = dlg.GetValue()

        dlg.Destroy()

	if comment != "":
		temp_comment = string.replace(comment, " ", "" )

		if self.invalidstring(temp_comment):		
			wx.MessageBox("Invalid input - alphanumeric only", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1


	x = 0
	
	if self.comments:
		while x < len(self.comments):
			if self.comments[x] == comment_address: 
				self.comments.pop(x)
				self.comments.pop(x)
				if comment != "":	
					self.comments.append(comment_address)
					self.comments.append(comment)
					self.session_changed = True
				break
			else:
				if comment != "":
					self.comments.append(comment_address)
					self.comments.append(comment)
					self.session_changed = True
				break

			x = x + 2

	else:
		if comment != "":
		 	self.comments.append(comment_address)
			self.comments.append(comment)
			self.session_changed = True

	self.dispDialog = 0
	self.disassusepc = 0
	self.OnDisassemble(1)
	self.disassusepc = 1
	self.dispDialog = 1


#-------Display last exception-------------------------------------------------------------


    def OnLastSigval(self, evt):
	"""
	Read the last signal value and display in a window
	"""
	sigum = 0 
	i = 3	
	signames=["SIGHUP","SIGINT","SIGQUIT","SIGILL","SIGTRAP","SIGIOT","SIGEMT","SIGFPE","SIGKILL","SIGBUS","SIGSEGV","SIGSYS","SIGPIPE","SIGALRM","SIGTERM","SIGUSR1","SIGUSR2","SIGCLD","SIGPWR","SIGWDOG","SIGEXIT"]

	displaybuffer = "<html><body><font size=\"9\" face=\"Fixedsys\" color=\"#000080\">"	#dark blue

	result = self.GdbCommand("$?#3f\n") #set last sigval command

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1
	
	result = result.encode('ascii')

	signum = int(result[1] + result[2],16)
	displaybuffer = displaybuffer + signames[signum-1]	

	displaybuffer = displaybuffer + "<font color=\"black\">"
	displaybuffer = displaybuffer + "<br><br>Trace:<br>"
	displaybuffer = displaybuffer + "</font>"

	if result[0] != "S":
		displaybuffer = displaybuffer + "<font color=\"#0000ff\">"	#light blue
		while i < len (result):
		
			if result[i] == ";":
				displaybuffer = displaybuffer + "<br>"
				i = i + 1
		
			displaybuffer = displaybuffer + result[i:i+8]

			i = i + 8
	
		displaybuffer = displaybuffer + "</font>"

	displaybuffer = displaybuffer + "</font></body></html>"
	self.win.LastSigvalHTMLCtrl.SetPage(displaybuffer)	
	return 0


#-------Single step------------------------------------------------------------------------


    def OnStepInto(self, evt):
	
	if self.connect_mode == "Serial":
		self.ser.write("$s#73\n")
		self.ser.read(5)
	else:
		self.tn.write("$s#73\n")
		self.tn.read_some()
	self.OnReadReg(1)
	self.OnReadStack()
	self.dispDialog = 0
	self.OnDisassemble(1)
	self.dispDialog = 1


#-------Step over--------------------------------------------------------------------------


    def OnStepOver(self, evt):

	current = int(self.currentinstruction,16)	

	if current & 0x48000001 == 0x48000001 or current & 0x40000001 == 0x40000001 or self.currentinstruction == "4e800421":		# bl or bctrl commands

		addr = int(self.program_counter,16)
		addr += 4
		address = "%08x" % addr

		command = self.CreateWriteMemoryReq(address,"7d821008","4")	#write breakpoint
		result = self.GdbCommand(command.encode('ascii')) #send write memory command



		command = self.CreateGetMemoryReq(address,"04")
		result = self.GdbCommand(command.encode('ascii')) #set read memory command
	
		if result != "7d821008":		
			wx.MessageBox("Step over failed", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

		if self.connect_mode == "Serial":
			self.ser.write("$c#63\n")
			self.ser.read(5)
		else:
			self.tn.write("$c#63\n")
			self.tn.read_some()

		command = self.CreateWriteMemoryReq(address,self.nextinstruction,"4")	#write breakpoint
		result = self.GdbCommand(command.encode('ascii')) #send write memory command

		command = self.CreateGetMemoryReq(address,"04")
		result = self.GdbCommand(command.encode('ascii')) #set read memory command

		if result != self.nextinstruction:		
			wx.MessageBox("Step over failed", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1

	else:
		if self.connect_mode == "Serial":
			self.ser.write("$s#73\n")
			self.ser.read(5)
		else:
			self.tn.write("$s#73\n")
			self.tn.read_some()

	self.OnReadReg(1)
	self.OnReadStack()
	self.dispDialog = 0
	self.OnDisassemble(1)
	self.dispDialog = 1


#-------Continue---------------------------------------------------------------------------


    def OnContinue(self, evt):
	
	if self.connect_mode == "Serial":
		self.ser.write("$c#63\n")
		self.ser.read(5)
	else:
		self.tn.write("$c#63\n")
		self.tn.read_some()

	self.debugstatus = 0
	self.win.statusbar.SetStatusText("Debugging Status: Not debugging", 2)

	displaybuffer = "<html><body></body></html>"	
	self.win.RegistersHTMLCtrl.SetPage(displaybuffer)	# clear all the panes
	self.win.DisassembleHTMLCtrl.SetPage(displaybuffer)
	self.win.LastSigvalHTMLCtrl.SetPage(displaybuffer)
	self.win.BreakpointsHTMLCtrl.SetPage(displaybuffer)
	self.win.StackHTMLCtrl.SetPage(displaybuffer)

	self.disableObjects()

	self.win.mb.Enable(self.win.ID_Connect, True)
	self.win.tb.EnableTool(self.win.ID_toolConnect,True)
	self.win.mb.Enable(self.win.ID_ConfigureConnection, True)
	self.win.tb.EnableTool(self.win.ID_toolConfigureConnection, True)

	self.dispDialog = 0
	self.disassusepc = 1
	self.continued = True
	reply = ""

	i = -1
	if self.connect_mode == "Serial":
		while i == -1:
			wx.Yield()
			try:
				reply = self.ser.read(20)
			except:
				pass
			i = reply.find ( '|' )			
			if self.connect_after_continue == True:	
				self.connect_after_continue = False			
				return 0			

		self.OnReconnect(1)

	else:
		while i == -1:
			wx.Yield()
			try:
			 	reply = self.tn.read_eager()
			except:
				pass
			i = reply.find ( '|' )			
			if self.connect_after_continue == True:	
				self.connect_after_continue = False			
				return 0			

		self.OnReconnect(1)


#-------Jump to address--------------------------------------------------------------------


    def OnJump(self, evt):

	dlg = wx.TextEntryDialog(self.win, 'Enter address to jump to','Jump to address')

	addr = ""

	if dlg.ShowModal() == wx.ID_OK:
            	addr = dlg.GetValue()
		address = string.lower(address)

        dlg.Destroy()
	if address == "":
		return 1
	if self.invalidaddress(address):		
		wx.MessageBox("Invalid address", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1
	
	request = self.CreateJumpReq(addr)

	self.GdbCommand(request)	# issue the gdb "jump to address" command
	self.debugstatus = 0
	self.win.statusbar.SetStatusText("Debugging Status: Not debugging", 2)

	displaybuffer = "<html><body></body></html>"	
	self.win.RegistersHTMLCtrl.SetPage(displaybuffer)	# clear all the panes
	self.win.DisassembleHTMLCtrl.SetPage(displaybuffer)
	self.win.LastSigvalHTMLCtrl.SetPage(displaybuffer)
	self.win.BreakpointsHTMLCtrl.SetPage(displaybuffer)

	self.ser.close()		#close serial port
	self.win.statusbar.SetStatusText("Connection Status: Disconnected", 1)

	self.disableObjects()

	self.win.mb.Enable(self.win.ID_Connect, True)
	self.win.mb.Enable(self.win.ID_Reconnect, True)
	self.win.mb.Enable(self.win.ID_ConfigureConnection, True)

	self.win.tb.EnableTool(self.win.ID_toolConfigureConnection, True)
	self.win.tb.EnableTool(self.win.ID_toolReconnect,True)
	self.win.tb.EnableTool(self.win.ID_toolConnect,True)
	
	self.connectstatus = 0


#-------Format a jump request---------------------------------------------------


    def CreateJumpReq(self, data):
	"""
	Creates a gdb request to write registers and returns the formatted request
	"""
	request = "c" + data
	formatted = self.checksum(request)
	formatted = formatted + "\n"
	return formatted


#-------Handle unsigned ints----------------------------------------------------


    def int32(self, x):
  	if x>0xFFFFFFFF:
    		raise OverflowError
  	if x>0x7FFFFFFF:
    		x=int(0x100000000-x)
    		if x<2147483648:
      			return -x
    		else:
      			return -2147483648
  	return x


#-------Sanitise address input--------------------------------------------------


    def	invalidaddress(self, address):

	try:
    		dummy = int(address,16)
	except:			
		return 1

	if len(address) > 8:
		return 1

	return 0


#-------Sanitise string input---------------------------------------------------


    def invalidstring(self, data):

	if data.isalnum():
		return 0
	else:
		return 1


#-------------------------------------------------------------------------------

    def OnFindContext(self, evt):

	if self.debugstatus == 0:
		return

	end_address = self.stack_pointer
	current_address = "%08x" % (int(end_address,16) - 196)
	search_term = "ab1234cd"

	found = False

	while found == False:
		wx.Yield()

		formatted = self.CreateGetMemoryReq(current_address,"c8")
		result = self.GdbCommand(formatted) 	

		if result == "E03":
			wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
			return 1
	
		x = 0
		while x < 392:
			if result [x:x+8] == search_term:
				found_address = "%08x" % (int(current_address,16) + (x/2))
				found = True
			x += 8
	
		current_address = "%08x" % (int(current_address,16) - 196)


	formatted = self.CreateGetMemoryReq(found_address,"08")
	result = self.GdbCommand(formatted) 

	if result == "E03":
		wx.MessageBox("Address can not be read", caption="Error", style=wx.OK|wx.ICON_ERROR, parent=self.win)
		return 1

	context = int(result[8:16],16) 
	
	if context == 4294967294:
		context = -1
		self.context = "unknown"
		return
	
	else:
		try:
			indexval = self.pid.index(context)
			self.context = "%s" % 	self.procname[indexval]
		except:
			context = int(result[8:12],16) 				# Cater for >= v12.4 with modified heap headers
			indexval = self.pid.index(context)
			self.context = "%s" % 	self.procname[indexval]


	self.context = string.replace(self.context, "  ", "")
	


