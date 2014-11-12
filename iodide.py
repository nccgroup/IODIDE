import wx
import wx.aui
import sys
import os
from gdb import gdbproto
from iodideGUI import PyAUIFrame

if __name__ == '__main__':
    
    ID_Connect = wx.NewId()

    class MyApp(wx.App):
        def OnInit(self):

	    gdb = gdbproto()
	    wx.InitAllImageHandlers()
            win = PyAUIFrame(None, gdb, wx.ID_ANY, "IODIDE - The IOS Debugger and Integrated Disassembler Environment v1.0", size=(890, 705))
	    gdb.window(win)	
	    gdb.disableObjects()	   
    	    win.Show()
	    win.Center()	    
	    return True

    app = MyApp(False)
    app.MainLoop()

