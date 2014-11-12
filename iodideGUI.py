import sys
import os
import wx
import wx.html
import wx.aui
import string
from wx.lib.wordwrap import wordwrap
import wx.lib.agw.advancedsplash as AS

#------------------------------------------------------------------------------------------


class TestSearchCtrl(wx.SearchCtrl):
    maxSearches = 5
    
    def __init__(self, parent, id=-1, value="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
                 doSearch=None):
        style |= wx.TE_PROCESS_ENTER
        wx.SearchCtrl.__init__(self, parent, id, value, pos, size, style)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEntered)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuItem, id=1, id2=self.maxSearches)
        self.doSearch = doSearch
        self.searches = []

    def OnTextEntered(self, evt):
        text = self.GetValue()
        if self.doSearch(text):
            self.searches.append(text)
            if len(self.searches) > self.maxSearches:
                del self.searches[0]
            self.SetMenu(self.MakeMenu())            
        self.SetValue("")

    def OnMenuItem(self, evt):
        text = self.searches[evt.GetId()-1]
        self.doSearch(text)
        
    def MakeMenu(self):
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)
        for idx, txt in enumerate(self.searches):
            menu.Append(1+idx, txt)
        return menu

#-----------------------------------------------------------------------------

class DisassembleHTML(wx.html.HtmlWindow):


    def OnPopupAddBookmark(self, event):
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnAddBookmarks(1)
	self.win.gdb.dispDialog = 1

    def OnPopupAddComment(self, event):
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnComment(1)
	self.win.gdb.dispDialog = 1

    def OnPopupAddBreakpoint(self, event):
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnSetBreakpoints(1)
	self.win.gdb.dispDialog = 1

    def OnPopupDelBreakpoint(self, event):
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnDelBreakpoints(1)
	self.win.gdb.dispDialog = 1

    def OnPopupDownload(self, event):
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnDownload(1)
	self.win.gdb.dispDialog = 1

    def OnPopupUpload(self, event):
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnUpload(1)
	self.win.gdb.disassusepc = 0
	self.win.gdb.OnDisassemble(1)
	self.win.gdb.dispDialog = 1
	self.win.gdb.disassusepc = 1

    def OnPopupWritemem(self, event):
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnWriteMem(1)
	self.win.gdb.disassusepc = 0
	self.win.gdb.OnDisassemble(1)
	self.win.gdb.dispDialog = 1
	self.win.gdb.disassusepc = 1

    def	OnCellClicked (self, cell, x, y, event):
	self.win = self.GetParent() 
	
	sel = wx.html.HtmlSelection()	



	address = cell.ConvertToText(sel)
	address = string.replace(address, " ", "")

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
		self.win.popupID3 = wx.NewId()
		self.win.popupID4 = wx.NewId()
		self.win.popupID5 = wx.NewId()
		self.win.popupID6 = wx.NewId()
		self.win.popupID7 = wx.NewId()
       		self.win.Bind(wx.EVT_MENU, self.OnPopupAddBookmark, id=self.win.popupID1)
		self.win.Bind(wx.EVT_MENU, self.OnPopupAddComment, id=self.win.popupID2)
		self.win.Bind(wx.EVT_MENU, self.OnPopupAddBreakpoint, id=self.win.popupID3)
		self.win.Bind(wx.EVT_MENU, self.OnPopupDelBreakpoint, id=self.win.popupID4)
		self.win.Bind(wx.EVT_MENU, self.OnPopupDownload, id=self.win.popupID5)
		self.win.Bind(wx.EVT_MENU, self.OnPopupUpload, id=self.win.popupID6)
		self.win.Bind(wx.EVT_MENU, self.OnPopupWritemem, id=self.win.popupID7)
       		menu = wx.Menu()

       		item = wx.MenuItem(menu, self.win.popupID1, "Add bookmark")
	        menu.AppendItem(item)

		menu.Append(self.win.popupID2, "Add comment") 
		menu.Append(self.win.popupID3, "Add breakpoint") 
		menu.Append(self.win.popupID4, "Remove breakpoint")   
		menu.Append(self.win.popupID5, "Download memory from here")  
		menu.Append(self.win.popupID6, "Upload data to here")  	
		menu.Append(self.win.popupID7, "Modify memory")	
       		self.win.PopupMenu(menu)
       		menu.Destroy()


#-----------------------------------------------------------------------------


class RegistersHTML(wx.html.HtmlWindow):

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
	self.win = self.GetParent() 
	sel = wx.html.HtmlSelection()

	address = cell.ConvertToText(sel)
	address = string.replace(address, " ", "" )

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


#-----------------------------------------------------------------------------


class StackHTML(wx.html.HtmlWindow):

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
	self.win = self.GetParent() 
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

#-----------------------------------------------------------------------------


class SigvalHTML(wx.html.HtmlWindow):

    def OnPopupDisassemble(self, event):	

	self.win.gdb.disassusepc = 0	
	self.win.gdb.currentdisass = self.win.gdb.currentclickaddress
	self.win.gdb.dispDialog = 0
	self.win.gdb.OnDisassemble(1)
	self.win.gdb.dispDialog = 1
	self.win.gdb.disassusepc = 1

    def	OnCellClicked (self, cell, x, y, event):
	self.win = self.GetParent() 
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
       		menu = wx.Menu()
       		item = wx.MenuItem(menu, self.win.popupID1, "Disassemble")
	        menu.AppendItem(item)    		
       		self.win.PopupMenu(menu)
       		menu.Destroy()


#-------Create frame----------------------------------------------------------

 
class PyAUIFrame(wx.Frame):
    
    def __init__(self, parent, gdb, id=-1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
                                            wx.SUNKEN_BORDER |
                                            wx.CLIP_CHILDREN):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)


	self.ID_Serial = wx.NewId()
	self.ID_ConfigureConnection = wx.NewId()
	self.ID_Connect = wx.NewId()
	self.ID_Reconnect = wx.NewId()
	self.ID_Open = wx.NewId()
	self.ID_Save = wx.NewId()
	self.ID_Download = wx.NewId()
	self.ID_Upload = wx.NewId()
	self.ID_SaveRunningConfig = wx.NewId()

	self.ID_ReadReg = wx.NewId()
	self.ID_ReadMem = wx.NewId()
	self.ID_ReadHeap = wx.NewId()
	self.ID_MemMap = wx.NewId()
	self.ID_Processes = wx.NewId()
	self.ID_RunningConfig = wx.NewId()
	self.ID_Registry = wx.NewId()	
	self.ID_Disassemble = wx.NewId()
	self.ID_ListBookmarks = wx.NewId()
	self.ID_Search = wx.NewId()

	self.ID_WriteReg = wx.NewId()
	self.ID_WriteMem = wx.NewId()
	self.ID_SetBreakpoints = wx.NewId()
	self.ID_DelBreakpoints = wx.NewId()
	self.ID_Comment = wx.NewId()

	self.ID_StepInto = wx.NewId()
	self.ID_StepOver = wx.NewId()
	self.ID_Jump = wx.NewId()
	self.ID_Continue = wx.NewId()

	self.ID_About = wx.NewId()

	self.ID_toolConnect = wx.NewId()
	self.ID_toolReconnect = wx.NewId()
	self.ID_toolConfigureConnection = wx.NewId()

	self.ID_toolOpen = wx.NewId()
	self.ID_toolSave = wx.NewId()
	self.ID_toolUpload = wx.NewId()
	self.ID_toolDownload = wx.NewId()

	self.ID_toolDisLabel = wx.NewId()
	self.ID_toolDisback = wx.NewId()
	self.ID_toolDisforward = wx.NewId()

	self.ID_toolDebugLabel = wx.NewId()
	self.ID_toolStep = wx.NewId()
	self.ID_toolStepover = wx.NewId()
	self.ID_toolContinue = wx.NewId()

	self.ID_toolBreakLabel = wx.NewId()
	self.ID_toolAddBreak = wx.NewId()
	self.ID_toolDelBreak = wx.NewId()

	self.ID_toolListBookmarks = wx.NewId()

	self.ID_toolComment = wx.NewId()

	self.ID_toolFindNext = wx.NewId()

#-----------------------------------------------------------------------------

        
        # tell FrameManager to manage this frame
       
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)
	self.gdb = gdb
        self._perspectives = []


#-------Splash screen---------------------------------------------------------


	pn = os.path.normpath(os.path.join(".", "images/iodide_splash_screen.png"))
       	bitmap = wx.Bitmap(pn, wx.BITMAP_TYPE_PNG)
       	shadow = wx.WHITE
	frame = AS.AdvancedSplash(self, bitmap=bitmap, timeout=3000)

#-------Set windows icon------------------------------------------------------

	
 	image = wx.Image('images/iodide16x16.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap() 
	icon = wx.EmptyIcon() 
	icon.CopyFromBitmap(image) 
	self.SetIcon(icon) 

   
#-------Create menu-----------------------------------------------------------


        self.mb = wx.MenuBar()

        file_menu = wx.Menu()
	file_menu.Append(self.ID_Open, "&Open session")
	file_menu.Append(self.ID_ConfigureConnection, "&Configure connection")
	file_menu.Append(self.ID_Save, "&Save session")		
	file_menu.Append(self.ID_Connect, "&Connect to device")
	file_menu.Append(self.ID_Reconnect, "&Reconnect to device")		
	file_menu.Append(self.ID_Download, "&Download from memory")
	file_menu.Append(self.ID_Upload, "&Upload to memory")
	file_menu.Append(self.ID_SaveRunningConfig, "&Save running config")
	file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "Exit")

	file_menu.Enable(self.ID_Upload, False)

        view_menu = wx.Menu()
	#view_menu.Append(self.ID_ReadReg, "&Display registers")
	view_menu.Append(self.ID_ReadMem, "&Display memory")
	view_menu.Append(self.ID_Disassemble, "&Disassemble memory")
	view_menu.Append(self.ID_Search, "&Search memory address range")
	view_menu.Append(self.ID_ReadHeap, "&Display heap blocks")
	view_menu.Append(self.ID_MemMap, "&Display memory map")
	view_menu.Append(self.ID_Processes, "&Display processes")
	view_menu.Append(self.ID_RunningConfig, "&Display running config")
	view_menu.Append(self.ID_Registry, "&Display registry information")	
	view_menu.Append(self.ID_ListBookmarks, "&Bookmarks")	
             
        edit_menu = wx.Menu()
	edit_menu.Append(self.ID_WriteReg, "&Modify registers")
	edit_menu.Append(self.ID_WriteMem, "&Modify memory")
	edit_menu.Append(self.ID_SetBreakpoints, "&Set breakpoint")
	edit_menu.Append(self.ID_DelBreakpoints, "&Delete breakpoint")
	edit_menu.Append(self.ID_Comment, "&Insert comment")

	debug_menu = wx.Menu()
	debug_menu.Append(self.ID_StepInto, "&Step into")
	debug_menu.Append(self.ID_StepOver, "&Step over")
	debug_menu.Append(self.ID_Jump, "&Jump to address")
	debug_menu.Append(self.ID_Continue, "&Continue")

	debug_menu.Enable(self.ID_StepOver, False)

        help_menu = wx.Menu()
	help_menu.Append(self.ID_About, "&About")


      
        self.mb.Append(file_menu, "File")
        self.mb.Append(view_menu, "View")
	self.mb.Append(edit_menu, "Edit")
	self.mb.Append(debug_menu, "Debug")
        self.mb.Append(help_menu, "Help")

        
        self.SetMenuBar(self.mb)

        self.statusbar = self.CreateStatusBar(3, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-1,-2, -2])
        self.statusbar.SetStatusText("", 0)
        self.statusbar.SetStatusText("Connection Status: Disconnected from device", 1)
	self.statusbar.SetStatusText("Debugging Status: Not debugging", 2)


#-------Create toolbar--------------------------------------------------------


	self.tb = self.CreateToolBar()
	
	self.tb.AddSimpleTool(self.ID_toolConnect, 
			 wx.Image('images/connect_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Connect to device', 
			 'Connect to device')	

	self.tb.AddSimpleTool(self.ID_toolReconnect, 
			 wx.Image('images/reconnect_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Reconnect to device', 
			 'Reconnect to device')

	self.tb.AddSimpleTool(self.ID_toolConfigureConnection, 
			 wx.Image('images/customize_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Configure connection', 
			 'Configure connection')
	
	self.tb.AddSeparator()

	self.tb.AddSimpleTool(self.ID_toolOpen, 
			 wx.Image('images/folder_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Open session', 
			 'Open session')

	self.tb.AddSimpleTool(self.ID_toolSave, 
			 wx.Image('images/save_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Save session', 
			 'Save session')

	self.tb.AddSimpleTool(self.ID_toolDownload, 
			 wx.Image('images/download_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Download data from memory', 
			 'Download data from memory')

	self.tb.AddSimpleTool(self.ID_toolUpload, 
			 wx.Image('images/upload_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Upload data to memory', 
			 'Upload data to memory')

	self.tb.AddSeparator()

	self.tb.AddControl(wx.StaticText(self.tb, 
		      self.ID_toolDisLabel, 
		      label ='Disassembler:', 
		      name = 'lblDisass',
		      size = (70,-1), 
		      style = 0)) 

	self.tb.AddSimpleTool(self.ID_toolDisback, 
			 wx.Image('images/av_back_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'View previous disassembled memory', 
			 'View previous disassembled memory')

	self.tb.AddSimpleTool(self.ID_toolDisforward, 
			 wx.Image('images/av_play_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'View next disassembled memory', 
			 'View next disassembled memory')

	self.tb.AddSeparator()

	self.tb.AddControl(wx.StaticText(self.tb, 
                      self.ID_toolDebugLabel, 
		      label ='PC:', 
		      name = 'lblDebug',
		      size = (20,-1), 
		      style = 0)) 

	self.tb.AddSimpleTool(self.ID_toolStep, 
			 wx.Image('images/av_play_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Step into', 
			 'Step into')

	self.tb.AddSimpleTool(self.ID_toolStepover, 
			 wx.Image('images/av_fast_forward_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Step over', 
			 'Step over')

	self.tb.AddSimpleTool(self.ID_toolContinue, 
			 wx.Image('images/forward_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
	 		 'Continue execution', 
			 'Continue execution')

	self.tb.AddSeparator()


	self.tb.AddSimpleTool(self.ID_toolAddBreak, 
			 wx.Image('images/document_new_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
			 'Add breakpoint', 
			 'Add breakpoint')

	self.tb.AddSimpleTool(self.ID_toolDelBreak, 
			 wx.Image('images/document_delete_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
	 		 'Delete breakpoint', 
			 'Delete breakpoint')

	self.tb.AddSeparator()
	
	self.tb.AddSimpleTool(self.ID_toolListBookmarks, 
			 wx.Image('images/bookmark_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
	 		 'List bookmarks', 
			 'List bookmarks')

	self.tb.AddSimpleTool(self.ID_toolComment, 
			 wx.Image('images/comment_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
	 		 'Insert comment', 
			 'Insert comment')

	self.tb.AddSeparator()

	search = TestSearchCtrl(self.tb, size=(150,-1), doSearch=self.gdb.DoDisSearch)
        self.tb.AddControl(search)

	self.tb.AddSimpleTool(self.ID_toolFindNext, 
			 wx.Image('images/forward_small.png',
			 wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 
	 		 'Find next', 
			 'Find next')
	
	self.tb.Realize()


#-------Create panes----------------------------------------------------------
	

	self.RegistersHTMLCtrl = RegistersHTML(self, -1, wx.DefaultPosition, wx.Size(650, 195))
	self._mgr.AddPane(self.RegistersHTMLCtrl, wx.aui.AuiPaneInfo().Name("Registers").
								  CenterPane().
								  Caption("Registers").
								  CaptionVisible(True).
								  Fixed())

	self.LastSigvalHTMLCtrl = SigvalHTML(self, -1, wx.DefaultPosition, wx.Size(115, 195))	
	self._mgr.AddPane(self.LastSigvalHTMLCtrl, wx.aui.AuiPaneInfo().Name("LastException").
							       CenterPane().
							       Caption("Last Exception").
							       CaptionVisible(True).
							       Fixed())

	self.BreakpointsHTMLCtrl = wx.html.HtmlWindow(self, -1, wx.DefaultPosition, wx.Size(115, 195))	
	self._mgr.AddPane(self.BreakpointsHTMLCtrl, wx.aui.AuiPaneInfo().Name("Breakpoints").
							       CenterPane().
							       Caption("Breakpoints").
							       CaptionVisible(True).
							       Fixed())

	self.DisassembleHTMLCtrl = DisassembleHTML(self, -1, wx.DefaultPosition, wx.Size(767, 370))
	self._mgr.AddPane(self.DisassembleHTMLCtrl, wx.aui.AuiPaneInfo().Name("Disassembler").
									  CenterPane().
									  Caption("Disassembler").
									  CaptionVisible(True).
									  Fixed()) 

	self.StackHTMLCtrl = StackHTML(self, -1, wx.DefaultPosition, wx.Size(111, 370))	
	self._mgr.AddPane(self.StackHTMLCtrl, wx.aui.AuiPaneInfo().Name("Stack").
									  CenterPane().
									  Caption("Stack").
									  CaptionVisible(True).
							       		  Fixed()) 


#-------Create perspectives---------------------------------------------------


        all_panes = self._mgr.GetAllPanes()
        perspective_default = self._mgr.SavePerspective()

        for ii in xrange(len(all_panes)):
            if not all_panes[ii].IsToolbar():
                all_panes[ii].Hide()

	self._mgr.GetPane("Registers").Show().Top().Layer(0).Row(0).Position(0)
	self._mgr.GetPane("LastException").Show().Top().Layer(0).Row(0).Position(0)
	self._mgr.GetPane("Breakpoints").Show().Top().Layer(0).Row(0).Position(0)	
	self._mgr.GetPane("Disassembler").Show().Bottom().Layer(0).Row(0).Position(0)
	self._mgr.GetPane("Stack").Show().Bottom().Layer(0).Row(0).Position(0)

        self._perspectives.append(perspective_default)
        self._mgr.Update()


#-------Bind events-----------------------------------------------------------


        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose) 
        
	self.Bind(wx.EVT_MENU, self.gdb.OnOpen, id=self.ID_Open)
	self.Bind(wx.EVT_MENU, self.gdb.OnOpen, id=self.ID_toolOpen)
	self.Bind(wx.EVT_MENU, self.gdb.OnSave, id=self.ID_Save)
	self.Bind(wx.EVT_MENU, self.gdb.OnSave, id=self.ID_toolSave)
	self.Bind(wx.EVT_MENU, self.gdb.OnSerial, id=self.ID_Serial)

	self.Bind(wx.EVT_MENU, self.gdb.OnConfigureConnection, id=self.ID_ConfigureConnection)
	self.Bind(wx.EVT_MENU, self.gdb.OnConfigureConnection, id=self.ID_toolConfigureConnection)
	self.Bind(wx.EVT_MENU, self.gdb.OnConnect, id=self.ID_Connect)
	self.Bind(wx.EVT_MENU, self.gdb.OnConnect, id=self.ID_toolConnect)
	self.Bind(wx.EVT_MENU, self.gdb.OnReconnect, id=self.ID_Reconnect)
	self.Bind(wx.EVT_MENU, self.gdb.OnReconnect, id=self.ID_toolReconnect)
	self.Bind(wx.EVT_MENU, self.gdb.OnUpload, id=self.ID_Upload)
	self.Bind(wx.EVT_MENU, self.gdb.OnUpload, id=self.ID_toolUpload)
	self.Bind(wx.EVT_MENU, self.gdb.OnDownload, id=self.ID_Download)
	self.Bind(wx.EVT_MENU, self.gdb.OnDownload, id=self.ID_toolDownload)
	self.Bind(wx.EVT_MENU, self.gdb.OnSaveRunningConfig, id=self.ID_SaveRunningConfig)
	self.Bind(wx.EVT_MENU, self.gdb.OnExit, id=wx.ID_EXIT)

	self.Bind(wx.EVT_MENU, self.gdb.OnReadReg, id=self.ID_ReadReg)
	self.Bind(wx.EVT_MENU, self.gdb.OnReadMem, id=self.ID_ReadMem)
	self.Bind(wx.EVT_MENU, self.gdb.OnReadHeap, id=self.ID_ReadHeap)
	self.Bind(wx.EVT_MENU, self.gdb.OnMemMap, id=self.ID_MemMap)
	self.Bind(wx.EVT_MENU, self.gdb.OnProcesses, id=self.ID_Processes)
	self.Bind(wx.EVT_MENU, self.gdb.OnRunningConfig, id=self.ID_RunningConfig)
	self.Bind(wx.EVT_MENU, self.gdb.OnDisplayRegistry, id=self.ID_Registry)
	self.Bind(wx.EVT_MENU, self.gdb.OnDisassemble, id=self.ID_Disassemble)
	self.Bind(wx.EVT_MENU, self.gdb.OnDisassBackClick, id=self.ID_toolDisback)
	self.Bind(wx.EVT_MENU, self.gdb.OnDisassForwardClick, id=self.ID_toolDisforward)
	self.Bind(wx.EVT_MENU, self.gdb.OnListBookmarks, id=self.ID_ListBookmarks)
	self.Bind(wx.EVT_MENU, self.gdb.OnListBookmarks, id=self.ID_toolListBookmarks)
	self.Bind(wx.EVT_MENU, self.gdb.OnSearch, id=self.ID_Search)

	self.Bind(wx.EVT_MENU, self.gdb.OnWriteReg, id=self.ID_WriteReg)
	self.Bind(wx.EVT_MENU, self.gdb.OnWriteMem, id=self.ID_WriteMem)
	self.Bind(wx.EVT_MENU, self.gdb.OnSetBreakpoints, id=self.ID_SetBreakpoints)
	self.Bind(wx.EVT_MENU, self.gdb.OnSetBreakpoints, id=self.ID_toolAddBreak)
	self.Bind(wx.EVT_MENU, self.gdb.OnDelBreakpoints, id=self.ID_DelBreakpoints)
	self.Bind(wx.EVT_MENU, self.gdb.OnDelBreakpoints, id=self.ID_toolDelBreak)
	self.Bind(wx.EVT_MENU, self.gdb.OnComment, id=self.ID_Comment)
	self.Bind(wx.EVT_MENU, self.gdb.OnComment, id=self.ID_toolComment)

	self.Bind(wx.EVT_MENU, self.gdb.OnStepInto, id=self.ID_StepInto)
	self.Bind(wx.EVT_MENU, self.gdb.OnStepInto, id=self.ID_toolStep)
	self.Bind(wx.EVT_MENU, self.gdb.OnStepOver, id=self.ID_StepOver)
	self.Bind(wx.EVT_MENU, self.gdb.OnStepOver, id=self.ID_toolStepover)

	self.Bind(wx.EVT_MENU, self.gdb.OnContinue, id=self.ID_Continue)
	self.Bind(wx.EVT_MENU, self.gdb.OnContinue, id=self.ID_toolContinue)	
	self.Bind(wx.EVT_MENU, self.gdb.OnJump, id=self.ID_Jump)

	self.Bind(wx.EVT_MENU, self.gdb.OnSearchNextDis, id=self.ID_toolFindNext)

	self.Bind(wx.EVT_MENU, self.OnAbout, id=self.ID_About)

#-------Methods---------------------------------------------------------------


    def OnEraseBackground(self, event):
        event.Skip()

    def OnSize(self, event):
        event.Skip()

    def OnClose(self, event):
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()

    def OnAbout(self, evt):       
        info = wx.AboutDialogInfo()
        info.Name = "IODIDE"
        info.Version = "1.0"
        info.Copyright = "(C) 2014 Andy Davis"
        info.Description = wordwrap(
            "IODIDE is the IOS Debugger and Integrated Disassembler Environment."
            "It connects to a Cisco device running IOS using the Cisco version "
            "of the gdb serial protocol to enable the IOS kernel to be debugged."
            
            "\n\nAlthough, some of the basic features are also available in the "
            "gdb client, IODIDE also offers more advanced functionality, such as "
            "the ability to upload binaries into memory.\n\n "
	    "Developed by Andy Davis (andy.davis@nccgroup.com)",350, wx.ClientDC(self))

        wx.AboutBox(info)

    def CreateHTMLCtrl(self):
        ctrl = wx.html.HtmlWindow(self, -1, wx.DefaultPosition, wx.Size(300, 300))
        if "gtk2" in wx.PlatformInfo:
            ctrl.SetStandardFonts()
     	return ctrl

    def RegisterWinWrite(self,regtext):
	self.RegistersHTMLCtrl.SetPage(regtext)
	
    def MemoryWinWrite(self,memtext):
	self.MemoryHTMLCtrl.SetPage(memtext)

    def DisassWinWrite(self,distext):
	self.DisassembleHTMLCtrl.SetPage(distext)

    def MemoryMapWinWrite(self,memmaptext):
	self.MemoryMapHTMLCtrl.SetPage(memmaptext)





