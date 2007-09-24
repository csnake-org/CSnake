#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.5 on Sat Sep 15 14:23:13 2007 from D:\Users\Maarten\Projects\Gimias\Prog\GIMIAS.cmake\GBuild\csnGUI.wxg

import wx
import csnGUIHandler

class CSnakeGUIFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CSnakeGUIFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.lblProjectFolder = wx.StaticText(self, -1, "Project Folder\n")
        self.txtProjectFolder = wx.TextCtrl(self, -1, "")
        self.btnSelectProjectFolder = wx.Button(self, -1, "...")
        self.label_1 = wx.StaticText(self, -1, "Project Root\n")
        self.txtProjectRoot = wx.TextCtrl(self, -1, "")
        self.btnSelectProjectRoot = wx.Button(self, -1, "...")
        self.label_1_copy = wx.StaticText(self, -1, "Bin Folder\n")
        self.txtBinFolder = wx.TextCtrl(self, -1, "")
        self.btnSelectBinFolder = wx.Button(self, -1, "...")
        self.text_ctrl_1 = wx.TextCtrl(self, -1, "Tip: it is convenient to have the Project Root and Bin Folder as subfolders of a common parent folder. For example, \n\nProject Root = <somepath>/TextEditorProject/source, \nBin Folder = <somepath>/TextEditorProject/bin. \nProject Folder = <somepath>/TextEditorProject/source/TextEditorGUI.", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP)
        self.btnCreateProject = wx.Button(self, -1, "Start new project")
        self.lblProjectName = wx.StaticText(self, -1, "Name")
        self.txtNewProjectName = wx.TextCtrl(self, -1, "")
        self.lblNewProjectType = wx.StaticText(self, -1, "Type")
        self.cmbNewProjectType = wx.ComboBox(self, -1, choices=["Executable", "Static library", "Dll"], style=wx.CB_DROPDOWN)
        self.btnBuildProject = wx.Button(self, -1, "Configure Project to Bin Folder")
        self.cmbBuildProjectType = wx.ComboBox(self, -1, choices=["Build CMake files and run CMake", "Only build CMake files"], style=wx.CB_DROPDOWN)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.OnTypingProjectFolder, self.txtProjectFolder)
        self.Bind(wx.EVT_BUTTON, self.OnSelectProjectFolder, self.btnSelectProjectFolder)
        self.Bind(wx.EVT_TEXT, self.OnTypingProjectRoot, self.txtProjectRoot)
        self.Bind(wx.EVT_BUTTON, self.OnSelectProjectRoot, self.btnSelectProjectRoot)
        self.Bind(wx.EVT_BUTTON, self.OnSelectBinFolder, self.btnSelectBinFolder)
        self.Bind(wx.EVT_BUTTON, self.OnStartNewProject, self.btnCreateProject)
        self.Bind(wx.EVT_BUTTON, self.OnConfigureProjectToBinFolder, self.btnBuildProject)
        # end wxGlade
        self.handler = csnGUIHandler.Handler

    def __set_properties(self):
        # begin wxGlade: CSnakeGUIFrame.__set_properties
        self.SetTitle("CSnake GUI")
        self.SetSize((500, 459))
        self.txtProjectFolder.SetMinSize((-1, -1))
        self.txtProjectFolder.SetToolTipString("The folder containing the target (dll, lib or exe) you wish to build.")
        self.btnSelectProjectFolder.SetMinSize((30, -1))
        self.txtProjectRoot.SetMinSize((-1, -1))
        self.txtProjectRoot.SetToolTipString("Optional field for the root of the source tree that contains the Project Folder. CSnake will search this source tree for other projects.")
        self.btnSelectProjectRoot.SetMinSize((30, -1))
        self.txtBinFolder.SetMinSize((-1, -1))
        self.txtBinFolder.SetToolTipString("This is the location where CSnake will generate the \"make files\".")
        self.btnSelectBinFolder.SetMinSize((30, -1))
        self.text_ctrl_1.SetMinSize((-1, 800))
        self.btnCreateProject.SetToolTipString("Start a new project in the Project Folder based on a template")
        self.txtNewProjectName.SetMinSize((-1, -1))
        self.cmbNewProjectType.SetMinSize((100, 21))
        self.cmbNewProjectType.SetSelection(0)
        self.cmbBuildProjectType.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: CSnakeGUIFrame.__do_layout
        boxSettings = wx.BoxSizer(wx.VERTICAL)
        boxBuildProject = wx.BoxSizer(wx.HORIZONTAL)
        boxCreateProject = wx.BoxSizer(wx.HORIZONTAL)
        sizeNewProjectType = wx.BoxSizer(wx.HORIZONTAL)
        sizeNewProjectName = wx.BoxSizer(wx.HORIZONTAL)
        boxBinFolder = wx.BoxSizer(wx.HORIZONTAL)
        boxProjectRoot = wx.BoxSizer(wx.HORIZONTAL)
        boxProjectFolder = wx.BoxSizer(wx.HORIZONTAL)
        boxProjectFolder.Add(self.lblProjectFolder, 0, wx.RIGHT, 5)
        boxProjectFolder.Add(self.txtProjectFolder, 2, wx.FIXED_MINSIZE, 0)
        boxProjectFolder.Add(self.btnSelectProjectFolder, 0, 0, 0)
        boxSettings.Add(boxProjectFolder, 1, wx.EXPAND, 0)
        boxProjectRoot.Add(self.label_1, 0, wx.RIGHT, 5)
        boxProjectRoot.Add(self.txtProjectRoot, 2, wx.FIXED_MINSIZE, 0)
        boxProjectRoot.Add(self.btnSelectProjectRoot, 0, 0, 0)
        boxSettings.Add(boxProjectRoot, 1, wx.EXPAND, 0)
        boxBinFolder.Add(self.label_1_copy, 0, wx.RIGHT, 5)
        boxBinFolder.Add(self.txtBinFolder, 2, wx.FIXED_MINSIZE, 0)
        boxBinFolder.Add(self.btnSelectBinFolder, 0, 0, 0)
        boxSettings.Add(boxBinFolder, 1, wx.EXPAND, 0)
        boxSettings.Add(self.text_ctrl_1, 2, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        boxCreateProject.Add(self.btnCreateProject, 0, 0, 0)
        sizeNewProjectName.Add(self.lblProjectName, 0, 0, 5)
        sizeNewProjectName.Add(self.txtNewProjectName, 2, 0, 5)
        boxCreateProject.Add(sizeNewProjectName, 2, wx.EXPAND, 5)
        sizeNewProjectType.Add(self.lblNewProjectType, 0, 0, 5)
        sizeNewProjectType.Add(self.cmbNewProjectType, 0, 0, 5)
        boxCreateProject.Add(sizeNewProjectType, 0, wx.EXPAND|wx.ALIGN_RIGHT, 5)
        boxSettings.Add(boxCreateProject, 1, wx.EXPAND, 0)
        boxBuildProject.Add(self.btnBuildProject, 0, 0, 0)
        boxBuildProject.Add(self.cmbBuildProjectType, 2, 0, 0)
        boxSettings.Add(boxBuildProject, 1, wx.EXPAND, 0)
        self.SetSizer(boxSettings)
        self.Layout()
        # end wxGlade

    def OnSelectProjectFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        dlg = wx.DirDialog(None, "Select Project Folder")
        if dlg.ShowModal() == wx.ID_OK:
            pass
        event.Skip()

    def OnSelectProjectRoot(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        dlg = wx.DirDialog(None, "Select Project Root Folder")
        if dlg.ShowModal() == wx.ID_OK:
            pass
        event.Skip()

    def OnSelectBinFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        dlg = wx.DirDialog(None, "Select Binary Folder")
        if dlg.ShowModal() == wx.ID_OK:
            pass
        event.Skip()

    def OnStartNewProject(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
    	csnGUIHandler.CreateCSnakeProject(self.txtProjectFolder.GetValue(), self.txtProjectRoot.GetValue(), self.txtNewProjectName.GetValue(), self.cmbNewProjectType.GetValue().lower())

    def OnConfigureProjectToBinFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        print "Event handler `OnConfigureProjectToBinFolder' not implemented"
        event.Skip()

    def OnTypingProjectFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        print "Event handler `OnTypingProjectFolder' not implemented"
        event.Skip()

    def OnTypingProjectRoot(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        print "Event handler `OnTypingProjectRoot' not implemented"
        event.Skip()

# end of class CSnakeGUIFrame


class CSnakeGUIApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        frmCSnakeGUI = CSnakeGUIFrame(None, -1, "")
        self.SetTopWindow(frmCSnakeGUI)
        frmCSnakeGUI.Show()
        return 1

# end of class CSnakeGUIApp

if __name__ == "__main__":
    app = CSnakeGUIApp(0)
    app.MainLoop()
