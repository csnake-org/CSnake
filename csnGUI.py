#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.5 on Sat Sep 15 14:23:13 2007 from D:\Users\Maarten\Projects\Gimias\Prog\GIMIAS.cmake\GBuild\csnGUI.wxg

import wx
import csnGUIOptions
import csnGUIHandler
import csnUtility
import os.path
import sys
import subprocess

class RedirectText:
    """
    Used to redirect messages to stdout to the text control in CSnakeGUIFrame.
    """
    def __init__(self,aWxTextCtrl):
		self.out=aWxTextCtrl

    def write(self,string):
		self.out.WriteText(string)

class CSnakeGUIFrame(wx.Frame):
    """
    The main application frame.
    """
    def __init__(self, *args, **kwds):
        # begin wxGlade: CSnakeGUIFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panelThirdParty = wx.Panel(self, -1)
        self.panelSource = wx.Panel(self, -1)
        self.panelProjectAndInstance = wx.Panel(self, -1)
        
        # Menu Bar
        self.frmCSnakeGUI_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.mnuLoadSettings = wx.MenuItem(wxglade_tmp_menu, wx.NewId(), "Load Settings", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendItem(self.mnuLoadSettings)
        self.mnuSaveSettingsAs = wx.MenuItem(wxglade_tmp_menu, wx.NewId(), "Save Settings As...", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendItem(self.mnuSaveSettingsAs)
        self.mnuExit = wx.MenuItem(wxglade_tmp_menu, wx.NewId(), "Exit", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendItem(self.mnuExit)
        self.frmCSnakeGUI_menubar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        self.mnuEditOptions = wx.MenuItem(wxglade_tmp_menu, wx.NewId(), "Edit Options", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.AppendItem(self.mnuEditOptions)
        self.frmCSnakeGUI_menubar.Append(wxglade_tmp_menu, "Options")
        self.SetMenuBar(self.frmCSnakeGUI_menubar)
        # Menu Bar end
        self.lbCSnakeFile = wx.StaticText(self.panelProjectAndInstance, -1, "CSnake File\n")
        self.txtCSnakeFile = wx.TextCtrl(self.panelProjectAndInstance, -1, "")
        self.btnSelectCSnakeFile = wx.Button(self.panelProjectAndInstance, -1, "...")
        self.labelInstance = wx.StaticText(self.panelProjectAndInstance, -1, "Instance")
        self.cmbInstance = wx.ComboBox(self.panelProjectAndInstance, -1, choices=[], style=wx.CB_DROPDOWN)
        self.btnUpdateListOfTargets = wx.Button(self.panelProjectAndInstance, -1, "Update")
        self.label_1 = wx.StaticText(self.panelSource, -1, "Root Folders\n")
        self.lbRootFolders = wx.ListBox(self.panelSource, -1, choices=[], style=wx.LB_SINGLE)
        self.btnAddRootFolder = wx.Button(self.panelSource, -1, "Add")
        self.btnRemoveRootFolder = wx.Button(self.panelSource, -1, "Remove")
        self.label_1_copy = wx.StaticText(self.panelSource, -1, "Bin Folder\n")
        self.txtBinFolder = wx.TextCtrl(self.panelSource, -1, "")
        self.btnSelectBinFolder = wx.Button(self.panelSource, -1, "...")
        self.label_2 = wx.StaticText(self.panelSource, -1, "Install Folder\n")
        self.txtInstallFolder = wx.TextCtrl(self.panelSource, -1, "")
        self.btnSelectInstallFolder = wx.Button(self.panelSource, -1, "...")
        self.label_1_copy_1 = wx.StaticText(self.panelThirdParty, -1, "ThirdParty Root\n Folder")
        self.txtThirdPartyRootFolder = wx.TextCtrl(self.panelThirdParty, -1, "")
        self.btnSelectThirdPartyRootFolder = wx.Button(self.panelThirdParty, -1, "...")
        self.label_1_copy_copy = wx.StaticText(self.panelThirdParty, -1, "ThirdParty Bin Folder\n")
        self.txtThirdPartyBinFolder = wx.TextCtrl(self.panelThirdParty, -1, "")
        self.btnSelectThirdPartyBinFolder = wx.Button(self.panelThirdParty, -1, "...")
        self.label_2_copy = wx.StaticText(self.panelThirdParty, -1, "KDevelop Project Folder\n\n")
        self.txtKDevelopProjectFolder = wx.TextCtrl(self.panelThirdParty, -1, "")
        self.btnSelectKDevelopProjectFolder = wx.Button(self.panelThirdParty, -1, "...")
        self.textLog = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP)
        self.btnDoAction = wx.Button(self, -1, "Do -->")
        self.cmbAction = wx.ComboBox(self, -1, choices=["Create CMake files and run CMake", "Only create CMake files", "Install files to Bin Folder", "Configure ThirdParty Folder"], style=wx.CB_DROPDOWN)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self.OnLoadSettings, self.mnuLoadSettings)
        self.Bind(wx.EVT_MENU, self.OnSaveSettingsAs, self.mnuSaveSettingsAs)
        self.Bind(wx.EVT_MENU, self.OnExit, self.mnuExit)
        self.Bind(wx.EVT_MENU, self.OnEditOptions, self.mnuEditOptions)
        self.Bind(wx.EVT_BUTTON, self.OnSelectCSnakeFile, self.btnSelectCSnakeFile)
        self.Bind(wx.EVT_BUTTON, self.OnUpdateListOfTargets, self.btnUpdateListOfTargets)
        self.Bind(wx.EVT_BUTTON, self.OnAddRootFolder, self.btnAddRootFolder)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveRootFolder, self.btnRemoveRootFolder)
        self.Bind(wx.EVT_BUTTON, self.OnSelectBinFolder, self.btnSelectBinFolder)
        self.Bind(wx.EVT_BUTTON, self.OnSelectInstallFolder, self.btnSelectInstallFolder)
        self.Bind(wx.EVT_BUTTON, self.OnSelectThirdPartyRootFolder, self.btnSelectThirdPartyRootFolder)
        self.Bind(wx.EVT_BUTTON, self.OnSelectThirdPartyBinFolder, self.btnSelectThirdPartyBinFolder)
        self.Bind(wx.EVT_BUTTON, self.OnSelectKDevelopProjectFolder, self.btnSelectKDevelopProjectFolder)
        self.Bind(wx.EVT_BUTTON, self.OnButtonDo, self.btnDoAction)
        # end wxGlade
        
    def __set_properties(self):
        # begin wxGlade: CSnakeGUIFrame.__set_properties
        self.SetTitle("CSnake GUI")
        self.SetSize((750, 400))
        self.lbCSnakeFile.SetMinSize((100, 15))
        self.txtCSnakeFile.SetMinSize((-1, -1))
        self.txtCSnakeFile.SetToolTipString("The folder containing the target (dll, lib or exe) you wish to build.")
        self.btnSelectCSnakeFile.SetMinSize((30, -1))
        self.labelInstance.SetMinSize((100, 15))
        self.panelProjectAndInstance.SetBackgroundColour(wx.Colour(192, 191, 255))
        self.label_1.SetMinSize((100,50))
        self.lbRootFolders.SetMinSize((4000, 26))
        self.label_1_copy.SetMinSize((100, 15))
        self.txtBinFolder.SetMinSize((-1, -1))
        self.txtBinFolder.SetToolTipString("This is the location where CSnake will generate the \"make files\".")
        self.btnSelectBinFolder.SetMinSize((30, -1))
        self.label_2.SetMinSize((100, 15))
        self.txtInstallFolder.SetMinSize((-1, -1))
        self.txtInstallFolder.SetToolTipString("This is the location where CSnake will generate the \"make files\".")
        self.btnSelectInstallFolder.SetMinSize((30, -1))
        self.panelSource.SetMinSize((-1,-1))
        self.label_1_copy_1.SetMinSize((100, 15))
        self.txtThirdPartyRootFolder.SetMinSize((-1, -1))
        self.txtThirdPartyRootFolder.SetToolTipString("Optional field for the root of the source tree that contains the Project Folder. CSnake will search this source tree for other projects.")
        self.btnSelectThirdPartyRootFolder.SetMinSize((30, -1))
        self.label_1_copy_copy.SetMinSize((100, 15))
        self.txtThirdPartyBinFolder.SetMinSize((-1, -1))
        self.txtThirdPartyBinFolder.SetToolTipString("This is the location where CSnake will generate the \"make files\".")
        self.btnSelectThirdPartyBinFolder.SetMinSize((30, -1))
        self.label_2_copy.SetMinSize((100, 15))
        self.label_2_copy.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.txtKDevelopProjectFolder.SetMinSize((-1, -1))
        self.txtKDevelopProjectFolder.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.txtKDevelopProjectFolder.SetToolTipString("This is the location where CSnake will generate the \"make files\".")
        self.btnSelectKDevelopProjectFolder.SetMinSize((30, -1))
        self.panelThirdParty.SetBackgroundColour(wx.Colour(236, 233, 216))
        self.textLog.SetMinSize((100, 50))
        self.btnDoAction.SetMinSize((100, -1))
        self.cmbAction.SetSelection(0)
        # end wxGlade
        
        self.Initialize()
        
    def RedirectStdOut(self):
        # redirect std out
        redir=RedirectText(self.textLog)
        sys.stdout=redir
        sys.stderr=redir

    def PrintWelcomeMessages(self):
        print "CSnakeGUI loaded.\n"
        print "Checking if CMake is found...\n"

    def CreateMemberVariables(self):
        self.settings = csnGUIHandler.Settings()
        self.handler = csnGUIHandler.Handler()
        self.commandCounter = 0
        
    def CreateOptionsFilenameAndOptionsMemberVariable(self):
        # find out location of application options file
        thisFolder = "%s" % (os.path.dirname(sys.argv[0]))
        thisFolder = thisFolder.replace("\\", "/")
        if thisFolder == "":
            thisFolder = "."
        self.optionsFilename = "%s/options" % thisFolder
        
        # create options
        self.options = csnGUIOptions.Options()
        self.options.currentGUISettingsFilename = "%s/settings" % thisFolder

    def InitializeOptions(self):
        # load options from options file
        self.LoadOptions()
        
        # Write the default options to the options file, and pass them to the handler
        self.WriteOptions()
        self.PassOptionsToHandler()

        iconFile = csnUtility.GetRootOfCSnake() + "/Laticauda_colubrina.ico"
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)
        
    def InitializeSettings(self):        
        # load previously saved settings
        if len(sys.argv) >= 2:
            self.LoadSettings(sys.argv[1])
        else:
            self.LoadSettings()
        # init lbRootFolders
        self.lbRootFolders.SetSelection(self.lbRootFolders.GetCount()-1)
        
    def Initialize(self):
        """
        Initializes the application.
        """
        #self.RedirectStdOut()
        self.PrintWelcomeMessages()
        self.CreateMemberVariables()  
        self.CreateOptionsFilenameAndOptionsMemberVariable()
        self.InitializeOptions()    
        self.InitializeSettings()            

    def StoreSettingsFilename(self, lastUsedSettingsFile):
        """
        Write location of last used config settings to the application options file. 
        """
        self.options.currentGUISettingsFilename = lastUsedSettingsFile
        self.WriteOptions()
        
    def WriteOptions(self):
        """
        Write options to the application options file, and passes them to the handler. 
        """
        self.options.Save(self.optionsFilename)

    def PassOptionsToHandler(self):
        self.handler.SetCompiler(self.options.compiler)
        self.handler.SetPythonPath(self.options.pythonPath)
        return self.handler.SetCMakePath(self.options.cmakePath)
        
    def LoadOptions(self):
        """
        Load options from the application options file. 
        """
        return self.options.Load(self.optionsFilename)
        
    def __do_layout(self):
        # begin wxGlade: CSnakeGUIFrame.__do_layout
        boxSettings = wx.BoxSizer(wx.VERTICAL)
        boxBuildProject = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        boxInstallFolder_copy = wx.BoxSizer(wx.HORIZONTAL)
        boxThirdPartyBinFolder = wx.BoxSizer(wx.HORIZONTAL)
        boxThirdPartyRoot = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        boxInstallFolder = wx.BoxSizer(wx.HORIZONTAL)
        boxBinFolder = wx.BoxSizer(wx.HORIZONTAL)
        boxRootFolder = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        boxRootFolder_copy = wx.BoxSizer(wx.HORIZONTAL)
        boxProjectPath = wx.BoxSizer(wx.HORIZONTAL)
        boxProjectPath.Add(self.lbCSnakeFile, 0, wx.RIGHT|wx.EXPAND, 5)
        boxProjectPath.Add(self.txtCSnakeFile, 2, wx.FIXED_MINSIZE, 0)
        boxProjectPath.Add(self.btnSelectCSnakeFile, 0, 0, 0)
        sizer_3.Add(boxProjectPath, 0, wx.EXPAND, 0)
        boxRootFolder_copy.Add(self.labelInstance, 0, wx.RIGHT|wx.EXPAND, 5)
        boxRootFolder_copy.Add(self.cmbInstance, 1, wx.EXPAND, 0)
        boxRootFolder_copy.Add(self.btnUpdateListOfTargets, 0, 0, 0)
        sizer_3.Add(boxRootFolder_copy, 1, wx.EXPAND, 0)
        self.panelProjectAndInstance.SetSizer(sizer_3)
        boxSettings.Add(self.panelProjectAndInstance, 0, wx.EXPAND, 0)
        boxRootFolder.Add(self.label_1, 0, wx.RIGHT|wx.EXPAND, 5)
        boxRootFolder.Add(self.lbRootFolders, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        sizer_4.Add(self.btnAddRootFolder, 0, 0, 0)
        sizer_4.Add(self.btnRemoveRootFolder, 0, 0, 0)
        boxRootFolder.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_1.Add(boxRootFolder, 0, wx.EXPAND, 0)
        boxBinFolder.Add(self.label_1_copy, 0, wx.RIGHT|wx.EXPAND, 5)
        boxBinFolder.Add(self.txtBinFolder, 2, wx.FIXED_MINSIZE, 0)
        boxBinFolder.Add(self.btnSelectBinFolder, 0, 0, 0)
        sizer_1.Add(boxBinFolder, 1, wx.EXPAND, 0)
        boxInstallFolder.Add(self.label_2, 0, wx.RIGHT|wx.EXPAND, 5)
        boxInstallFolder.Add(self.txtInstallFolder, 2, wx.FIXED_MINSIZE, 0)
        boxInstallFolder.Add(self.btnSelectInstallFolder, 0, 0, 0)
        sizer_1.Add(boxInstallFolder, 1, wx.EXPAND, 0)
        self.panelSource.SetSizer(sizer_1)
        boxSettings.Add(self.panelSource, 0, wx.EXPAND, 0)
        boxThirdPartyRoot.Add(self.label_1_copy_1, 0, wx.RIGHT|wx.EXPAND, 5)
        boxThirdPartyRoot.Add(self.txtThirdPartyRootFolder, 2, wx.FIXED_MINSIZE, 0)
        boxThirdPartyRoot.Add(self.btnSelectThirdPartyRootFolder, 0, 0, 0)
        sizer_2.Add(boxThirdPartyRoot, 1, wx.EXPAND, 0)
        boxThirdPartyBinFolder.Add(self.label_1_copy_copy, 0, wx.RIGHT|wx.EXPAND, 5)
        boxThirdPartyBinFolder.Add(self.txtThirdPartyBinFolder, 2, wx.FIXED_MINSIZE, 0)
        boxThirdPartyBinFolder.Add(self.btnSelectThirdPartyBinFolder, 0, 0, 0)
        sizer_2.Add(boxThirdPartyBinFolder, 1, wx.EXPAND, 0)
        boxInstallFolder_copy.Add(self.label_2_copy, 0, wx.RIGHT|wx.EXPAND, 5)
        boxInstallFolder_copy.Add(self.txtKDevelopProjectFolder, 2, wx.FIXED_MINSIZE, 0)
        boxInstallFolder_copy.Add(self.btnSelectKDevelopProjectFolder, 0, 0, 0)
        sizer_2.Add(boxInstallFolder_copy, 1, wx.EXPAND, 0)
        self.panelThirdParty.SetSizer(sizer_2)
        boxSettings.Add(self.panelThirdParty, 0, wx.EXPAND, 0)
        boxSettings.Add(self.textLog, 1, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)
        boxBuildProject.Add(self.btnDoAction, 0, 0, 0)
        boxBuildProject.Add(self.cmbAction, 2, 0, 0)
        boxSettings.Add(boxBuildProject, 0, wx.EXPAND, 0)
        self.SetSizer(boxSettings)
        self.Layout()
        # end wxGlade

    def OnSelectBinFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Select folder where project binaries must be placed.
        """
        dlg = wx.DirDialog(None, "Select Binary Folder")
        if dlg.ShowModal() == wx.ID_OK:
            self.txtBinFolder.SetValue(dlg.GetPath())

    def OnSelectThirdPartyBinFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Select folder where third party binaries must be placed.
        """
        dlg = wx.DirDialog(None, "Select Third Party Binary Folder")
        if dlg.ShowModal() == wx.ID_OK:
            self.txtThirdPartyBinFolder.SetValue(dlg.GetPath())

    def OnStartNewProject(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Create 'empty' CSnake file for configuring a library or executable (depending on cmbNewProjectType).
        """
        mapping = dict()
        mapping["Dll"] = "dll"
        mapping["Static library"] = "library"
        mapping["Executable"] = "executable"
    	csnGUIHandler.CreateCSnakeProject(self.settings.csnakeFile, self.settings.rootFolders, self.txtNewProjectName.GetValue(), mapping[self.cmbNewProjectType.GetValue()])

    def CopyTextBoxContentsToSettingsVariable(self):
        self.settings.SetBuildFolder( self.txtBinFolder.GetValue().replace("\\", "/") )
        self.settings.installFolder = self.txtInstallFolder.GetValue().replace("\\", "/")
        self.settings.thirdPartyBinFolder = self.txtThirdPartyBinFolder.GetValue().replace("\\", "/")
        self.settings.kdevelopProjectFolder = self.txtKDevelopProjectFolder.GetValue().replace("\\", "/")
        self.settings.csnakeFile = self.txtCSnakeFile.GetValue().replace("\\", "/")
        self.settings.rootFolders = []
        for i in range( self.lbRootFolders.GetCount() ):
            self.settings.rootFolders.append( self.lbRootFolders.GetString(i).replace("\\", "/") )
        self.settings.thirdPartyRootFolder = self.txtThirdPartyRootFolder.GetValue().replace("\\", "/")
        self.settings.instance = self.cmbInstance.GetValue()
        self.settings.cmakeBuildType = self.options.cmakeBuildType
    
    def SaveSettings(self, filename = ""):
        """
        Copy settings from the widget controls to self.settings.
        If filename is not "", save current configuration settings (source folder/bin folder/etc) 
        to filename.
        """
        self.CopyTextBoxContentsToSettingsVariable()
        if not filename == "":
            self.settings.Save(filename)
            # record the settings filename in self.optionsFilename
            self.StoreSettingsFilename(filename)
    
    def OnButtonDo(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Perform action specified in cmbAction.
        """
        print "\n--- Working, patience please... (command counter: %s) ---" % self.commandCounter
        self.SaveSettings(self.options.currentGUISettingsFilename)
        configureProject = self.cmbAction.GetValue() in ("Only create CMake files", "Create CMake files and run CMake")
        alsoRunCMake = self.cmbAction.GetValue() in ("Create CMake files and run CMake")
        configureThirdPartyFolder = self.cmbAction.GetValue() in ("Configure ThirdParty Folder")

        # write application options, and pass them to the handler
        self.WriteOptions()
        if self.PassOptionsToHandler():
        
            # if configuring the target project...            
            if configureProject:
                if self.handler.ConfigureProjectToBinFolder(self.settings, alsoRunCMake):
                    if self.settings.instance.lower() == "gimias":
                        self.ProposeToDeletePluginDlls()
                    if self.options.askToLaunchVisualStudio:
                        self.AskToLaunchVisualStudio( self.handler.GetTargetSolutionPath(self.settings) )
    
            # if installing dlls to the bin folder            
            copyDlls = self.cmbAction.GetValue() in ("Install files to Bin Folder")
            if copyDlls:
                if not self.handler.InstallBinariesToBinFolder(self.settings):
                    print "Error while installing files.\n"
                    
            # if configuring the third party folder            
            if( configureThirdPartyFolder ):
                self.handler.ConfigureThirdPartyFolder(self.settings)
                if self.options.askToLaunchVisualStudio:
                    self.AskToLaunchVisualStudio( self.handler.GetThirdPartySolutionPath(self.settings) )

        print "--- Done (command counter: %s) ---\n" % self.commandCounter
        self.commandCounter += 1
                
    def OnSelectInstallFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Select folder where application binaries are installed when building the INSTALL target.
        """
        dlg = wx.DirDialog(None, "Select Install Folder")
        if dlg.ShowModal() == wx.ID_OK:
            self.txtInstallFolder.SetValue(dlg.GetPath())

    def OnSelectThirdPartyRootFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Select folder where third party sources are found.
        """
        dlg = wx.DirDialog(None, "Select Third Party Root Folder")
        if dlg.ShowModal() == wx.ID_OK:
            self.txtThirdPartyRootFolder.SetValue(dlg.GetPath())

    def OnSelectCSnakeFile(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Select file containing the project that should be configured.
        """
        dlg = wx.FileDialog(None, "Select CSnake file")
        if dlg.ShowModal() == wx.ID_OK:
            self.txtCSnakeFile.SetValue(dlg.GetPath())

    def OnAddRootFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Add folder where CSnake files must be searched to lbRootFolders.
        """
        dlg = wx.DirDialog(None, "Add Root Folder")
        if dlg.ShowModal() == wx.ID_OK:
            self.lbRootFolders.Append(dlg.GetPath())
            self.lbRootFolders.SetSelection(self.lbRootFolders.GetCount()-1)

    def OnRemoveRootFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Remove folder where CSnake files must be searched from lbRootFolders.
        """
        self.lbRootFolders.Delete(self.lbRootFolders.GetSelection())

    def OnLoadSettings(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Let the user load configuration settings.
        """
        dlg = wx.FileDialog(None, "Select CSnake file", wildcard = "*.CSnakeGUI")
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadSettings(dlg.GetPath())

    def OnSaveSettingsAs(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Let the user save configuration settings.
        """
        dlg = wx.FileDialog(None, "Select CSnake file", wildcard = "*.CSnakeGUI", style = wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            (root, ext) = os.path.splitext(dlg.GetPath())
            if ext == ".CSnakeGUI":
                settingsFilename = dlg.GetPath()
            else:
                settingsFilename = "%s.CSnakeGUI" % root
            settingsFilename = dlg.GetPath()
            self.SaveSettings(settingsFilename)

    def CopySettingsVariableToTextBoxContents(self):
        self.txtCSnakeFile.SetValue(self.settings.csnakeFile)
        self.lbRootFolders.Clear()
        for rootFolder in self.settings.rootFolders:
            self.lbRootFolders.Append(rootFolder)
        self.txtThirdPartyRootFolder.SetValue(self.settings.thirdPartyRootFolder)
        self.txtBinFolder.SetValue( self.settings.GetBuildFolder() )
        self.txtInstallFolder.SetValue( self.settings.installFolder )
        self.txtThirdPartyBinFolder.SetValue( self.settings.thirdPartyBinFolder )
        self.txtKDevelopProjectFolder.SetValue( self.settings.kdevelopProjectFolder )
        self.cmbInstance.Clear()
        if self.settings.instance != "":
            self.cmbInstance.Append(self.settings.instance)
            self.cmbInstance.SetSelection(0)
    
    def LoadSettings(self, filename = ""):
        """
        Load configuration settings from filename.
        """
        if filename == "":
            filename = self.options.currentGUISettingsFilename
                
        if os.path.exists( filename ):
            self.settings.Load(filename)
            self.CopySettingsVariableToTextBoxContents()
            
        self.StoreSettingsFilename(filename)
    
    def OnEditOptions(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        """
        Let user edit the application options.
        """
        frmEditOptions = csnGUIOptions.CSnakeOptionsFrame(None, -1, "")
        frmEditOptions.ShowOptions(self.options, self.optionsFilename)
        frmEditOptions.MakeModal()
        frmEditOptions.Show()
        
    def OnUpdateListOfTargets(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        self.SaveSettings()
        targets = self.handler.GetListOfPossibleTargets(self.settings)
        self.cmbInstance.SetItems(targets)
        if len(targets):
            self.cmbInstance.SetSelection(0)

    def ProposeToDeletePluginDlls(self):
        spuriousDlls = self.handler.GetListOfSpuriousPluginDlls(self.settings)
        if len(spuriousDlls) == 0:
            return
            
        dllMessage = ""
        for x in spuriousDlls:
            dllMessage += ("%s\n" % x)
            
        message = "In the Bin folder, CSnake found GIMIAS plugins that have not been configured.\nThe following plugin dlls may crash GIMIAS:\n\n%s\nDelete them?" % dllMessage
        dlg = wx.MessageDialog(self, message, style = wx.YES_NO)
        if dlg.ShowModal() != wx.ID_YES:
            return
            
        for dll in spuriousDlls:
            os.remove(dll)

    def AskToLaunchVisualStudio(self, pathToSolution):
        message = "Launch Visual Studio with solution %s?" % pathToSolution
        dlg = wx.MessageDialog(self, message, style = wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            argList = [self.options.visualStudioPath, pathToSolution]
            retcode = subprocess.Popen(argList)
                
    def OnExit(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        self.Close()

    def Validate(self, action):
        if self.cmbAction.GetValue() == "Only create CMake files":
            pass
        
    def OnSelectKDevelopProjectFolder(self, event): # wxGlade: CSnakeGUIFrame.<event_handler>
        dlg = wx.DirDialog(None, "Select folder for saving the KDevelop project file")
        if dlg.ShowModal() == wx.ID_OK:
            self.txtKDevelopProjectFolder.SetValue(dlg.GetPath())

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
