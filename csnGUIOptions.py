#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.6.3 on Tue Mar 11 18:50:25 2008

import wx
import ConfigParser
import pickle

# begin wxGlade: extracode
# end wxGlade
    
wxID_btnSetCMakePath = 23423
wxID_btnSetPythonPath = wxID_btnSetCMakePath + 1

class CSnakeOptionsFrame(wx.Frame):
    """
    Frame where the user can edit application options.
    """
    def __init__(self, *args, **kwds):
        # begin wxGlade: CSnakeOptionsFrame.__init__
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.STAY_ON_TOP|wx.SYSTEM_MENU|wx.RESIZE_BORDER|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.sizer_4_staticbox = wx.StaticBox(self, -1, "Compiler")
        self.cmbCompiler = wx.ComboBox(self, -1, choices=["Visual Studio 7 .NET 2003", "Visual Studio 8 2005", "Visual Studio 8 2005 Win64", "KDevelop3", "Unix Makefiles"], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.btnSetCMakePath = wx.Button(self, wxID_btnSetCMakePath, "Set path to CMake")
        self.txtCMakePath = wx.TextCtrl(self, -1, "")
        self.cmbBuildType = wx.ComboBox(self, -1, choices=["Default (Debug and Release)", "Release", "Debug"], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.btnSetPythonPath = wx.Button(self, -1, "Set path to Python")
        self.txtPythonPath = wx.TextCtrl(self, -1, "")
        self.chkAskToLaunchVisualStudio = wx.CheckBox(self, -1, "Ask to launch VisualStudio")
        self.btnSetVisualStudioPath = wx.Button(self, -1, "Set path to Visual Studio")
        self.txtVisualStudioPath = wx.TextCtrl(self, -1, "")
        self.btnClose = wx.Button(self, -1, "Close")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_COMBOBOX, self.OnSelectCompiler, self.cmbCompiler)
        self.Bind(wx.EVT_BUTTON, self.OnSetCMakePath, id=wxID_btnSetCMakePath)
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectBuildType, self.cmbBuildType)
        self.Bind(wx.EVT_BUTTON, self.OnSetPythonPath, self.btnSetPythonPath)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckAskToLaunchVisualStudio, self.chkAskToLaunchVisualStudio)
        self.Bind(wx.EVT_BUTTON, self.OnSetVisualStudioPath, self.btnSetVisualStudioPath)
        self.Bind(wx.EVT_BUTTON, self.OnClose, self.btnClose)
        # end wxGlade

    def ShowOptions(self, _options = None, _optionsFilename = None):
        """
        If _options is not None, then sets _options as the options edited by this frame.
        Displays the current options.
        """
        if not _optionsFilename is None:
            self.optionsFilename = _optionsFilename
        if not _options is None:
        	self.options = _options
        self.txtCMakePath.SetValue(self.options.cmakePath)
        self.txtPythonPath.SetValue(self.options.pythonPath)
        self.txtVisualStudioPath.SetValue(self.options.visualStudioPath)
        self.chkAskToLaunchVisualStudio.SetValue(self.options.askToLaunchVisualStudio != 0)
        self.cmbCompiler.SetSelection(self.cmbCompiler.FindString(self.options.compiler))
        
        buildTypes = dict()
        buildTypes["None"] = 0
        buildTypes["Release"] = 1
        buildTypes["Debug"] = 2
        self.cmbBuildType.SetSelection(buildTypes[self.options.cmakeBuildType])
        
    def __set_properties(self):
        # begin wxGlade: CSnakeOptionsFrame.__set_properties
        self.SetTitle("CSnakeGUI Options")
        self.SetSize((600, -1))
        self.cmbCompiler.SetSelection(-1)
        self.txtCMakePath.SetMinSize((20,20))
        self.cmbBuildType.SetSelection(-1)
        self.txtPythonPath.SetMinSize((20,20))
        self.txtVisualStudioPath.SetMinSize((20,20))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: CSnakeOptionsFrame.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_5_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
        sizer_4.Add(self.cmbCompiler, 1, wx.EXPAND, 0)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_5.Add(self.btnSetCMakePath, 0, 0, 0)
        sizer_5.Add(self.txtCMakePath, 1, 0, 0)
        sizer_3.Add(sizer_5, 0, wx.EXPAND, 0)
        sizer_3.Add(self.cmbBuildType, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_5_copy.Add(self.btnSetPythonPath, 0, 0, 0)
        sizer_5_copy.Add(self.txtPythonPath, 1, 0, 0)
        sizer_2.Add(sizer_5_copy, 0, wx.EXPAND, 0)
        sizer_2.Add(self.chkAskToLaunchVisualStudio, 0, 0, 0)
        sizer_5_copy_copy.Add(self.btnSetVisualStudioPath, 0, 0, 0)
        sizer_5_copy_copy.Add(self.txtVisualStudioPath, 1, 0, 0)
        sizer_2.Add(sizer_5_copy_copy, 0, wx.EXPAND, 0)
        sizer_2.Add(self.btnClose, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((600, -1))
        # end wxGlade

    def OnSetCMakePath(self, event): # wxGlade: CSnakeOptionsFrame.<event_handler>
        """
        Let the user select where CSnake is located.
        """
        self.Show(False)
        dlg = wx.FileDialog(None, "Select path to CMake")
        if dlg.ShowModal() == wx.ID_OK:
            self.options.cmakePath = dlg.GetPath()
            self.ShowOptions()
        self.Show(True)

    def OnSelectCompiler(self, event): # wxGlade: CSnakeOptionsFrame.<event_handler>
        """
        Let the user select the compiler.
        """
        # use the current selection as the build type to use for visual studio projects
        if hasattr(self, "buildTypeForVisualStudio"):
            self.cmbBuildType.SetSelection(self.buildTypeForVisualStudio)
            
        self.CopyFromGUIToOptions()
        self.ShowOptions()

    def CopyFromGUIToOptions(self):
        """
        Copies the values from the controls in the GUI to the options structure
        """
        self.options.cmakePath = self.txtCMakePath.GetValue()
        self.options.pythonPath = self.txtPythonPath.GetValue()
        self.options.visualStudioPath = self.txtVisualStudioPath.GetValue()
        self.options.askToLaunchVisualStudio = self.chkAskToLaunchVisualStudio.GetValue()
        self.options.compiler = self.cmbCompiler.GetValue()
        
        # correct setting None on Linux to Debug
        if self.options.compiler in ("KDevelop3", "Unix Makefiles") and self.cmbBuildType.GetSelection() == 0:
            self.buildTypeForVisualStudio = self.cmbBuildType.GetSelection() 
            self.cmbBuildType.SetSelection(1)
                     
        if self.cmbBuildType.GetSelection() == 0:
            self.options.cmakeBuildType = "None"
        else:
            self.options.cmakeBuildType = "%s" % self.cmbBuildType.GetValue()
        
    def OnClose(self, event): # wxGlade: CSnakeOptionsFrame.<event_handler>
        self.CopyFromGUIToOptions()
        self.MakeModal(0)
        if not self.optionsFilename is None:
            self.options.Save(self.optionsFilename)
        self.Destroy()

    def OnSelectBuildType(self, event): # wxGlade: CSnakeOptionsFrame.<event_handler>
        # set the current selection as the build type to use for visual studio projects
        self.buildTypeForVisualStudio = self.cmbBuildType.GetSelection() 
        self.CopyFromGUIToOptions()
        self.ShowOptions()

    def OnSetPythonPath(self, event): # wxGlade: CSnakeOptionsFrame.<event_handler>
        self.Show(False)
        dlg = wx.FileDialog(None, "Select path to Python")
        if dlg.ShowModal() == wx.ID_OK:
            self.options.pythonPath = dlg.GetPath()
            self.ShowOptions()
        self.Show(True)

    def OnSetVisualStudioPath(self, event): # wxGlade: CSnakeOptionsFrame.<event_handler>
        self.Show(False)
        dlg = wx.FileDialog(None, "Select path to Python")
        if dlg.ShowModal() == wx.ID_OK:
            self.options.visualStudioPath = dlg.GetPath()
            self.ShowOptions()
        self.Show(True)

    def OnCheckAskToLaunchVisualStudio(self, event): # wxGlade: CSnakeOptionsFrame.<event_handler>
        self.CopyFromGUIToOptions()
        self.ShowOptions()

# end of class CSnakeOptionsFrame

class Options:
    def __init__(self):
        self.cmakePath = "CMake"    
        self.pythonPath = "D:/Python24/python.exe"
        self.compiler = "Visual Studio 7 .NET 2003"
        self.currentGUISettingsFilename = ""
        self.cmakeBuildType = "None"    
        self.askToLaunchVisualStudio = False
        self.visualStudioPath = ""

    def Load(self, filename):
        try:        
            parser = ConfigParser.ConfigParser()
            parser.read([filename])
            section = "CSnake"
            self.cmakePath = parser.get(section, "cmakePath")
            self.pythonPath = parser.get(section, "pythonPath")
            self.compiler = parser.get(section, "compiler")
            self.currentGUISettingsFilename = parser.get(section, "currentGUISettingsFilename")
            self.cmakeBuildType = parser.get(section, "cmakeBuildType")
            if parser.has_option(section, "askToLaunchVisualStudio"):
                self.askToLaunchVisualStudio = parser.get(section, "askToLaunchVisualStudio") == str(True)
            if parser.has_option(section, "visualStudioPath"):
                self.visualStudioPath = parser.get(section, "visualStudioPath")

            return 1
        except:
            try:
                f = open(filename, 'r')
                self = pickle.load(f)
                f.close()            
                return 1
            except:
                return 0
        
    def Save(self, filename):
        parser = ConfigParser.ConfigParser()
        section = "CSnake"
        parser.add_section(section)
        parser.set(section, "cmakePath", self.cmakePath)
        parser.set(section, "pythonPath", self.pythonPath)
        parser.set(section, "compiler", self.compiler)
        parser.set(section, "currentGUISettingsFilename", self.currentGUISettingsFilename)
        parser.set(section, "cmakeBuildType", self.cmakeBuildType)
        parser.set(section, "askToLaunchVisualStudio", self.askToLaunchVisualStudio)
        parser.set(section, "visualStudioPath", self.visualStudioPath)
        f = open(filename, 'w')
        parser.write(f)
        f.close()
        
if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = (None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
