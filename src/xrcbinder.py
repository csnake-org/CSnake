import wx
from wx import xrc
import csnUtility

class FilenameLabel:
    def __eq__(self, other):
        return isinstance(other, FilenameLabel)
    def __ne__(self, other):
        return not isinstance(other, FilenameLabel)
    
class BoundControl:
    def __init__(self, binder, control, labels = None, buddyClass = None, buddyField = None):
        if labels is None:
            labels = []
        self.control = control
        self.buddyClass = buddyClass
        self.buddyField = buddyField
        self.labels = labels
        self.binder = binder
        
    def GetBuddyClass(self):
        return self.binder.GetBuddyClass(self)
        
    def HasBuddyField(self):
        """ Check that the field exists using the HasField method of the buddy class. """
        return self.GetBuddyClass().HasField(self.buddyField)
        
    def SetBuddyValue(self, value):
        """ Set the buddy value using the SetField method of the buddy class. """
        self.GetBuddyClass().SetField(self.buddyField, value)
        
    def GetBuddyValue(self):
        """ Get the buddy value using the GetField method of the buddy class. """
        return self.GetBuddyClass().GetField(self.buddyField)
        
    def OnKillFocus(self, event):
        """ User moved from one field to the other, copy latest values to the context """
        self.UpdateBuddy()
        self.UpdateControl()
        event.Skip()
        
class ControlWithField(BoundControl):
    def GetControlValue(self):
        controlValue = self.control.GetValue()
        if controlValue != "" and FilenameLabel() in self.labels:
            controlValue = csnUtility.NormalizePath( controlValue )
        return controlValue

class TextControl(ControlWithField):
    def __init__(self, binder, control, labels = None, buddyClass = None, buddyField = None):
        ControlWithField.__init__(self, binder, control, labels, buddyClass, buddyField)
        control.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus, control)
    
    def UpdateBuddy(self):
        self.SetBuddyValue(self.GetControlValue())

    def UpdateControl(self):
        self.control.SetValue(self.GetBuddyValue())
    
class ComboBoxControl(ControlWithField):
    def __init__(self, binder, control, valueListFunctor, labels = None, buddyClass = None, buddyField = None):
        ControlWithField.__init__(self, binder, control, labels, buddyClass, buddyField)
        self.valueListFunctor = valueListFunctor
        control.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus, control)
        control.Bind(wx.EVT_COMBOBOX, self.OnSelectItem, control)
    
    def UpdateBuddy(self):
        controlValue = self.GetControlValue()
        if self.control.GetValue() != controlValue:
            self.control.SetValue(controlValue)
        self.SetBuddyValue(controlValue)

    def UpdateControl(self):
        self.control.Clear()
        self.control.SetItems(self.valueListFunctor())
        self.control.SetValue(self.GetBuddyValue())
        wx.CallAfter(self.control.SetValue, self.GetBuddyValue())
        
    def OnSelectItem(self, event):
        """ User moved from one field to the other, copy latest values to the context """
        self.UpdateBuddy()
        event.Skip()

class DropDownListControl(BoundControl):
    def __init__(self, binder, control, valueListFunctor, labels = None, buddyClass = None, buddyField = None):
        BoundControl.__init__(self, binder, control, labels, buddyClass, buddyField)
        self.valueListFunctor = valueListFunctor
        control.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus, control)
        control.Bind(wx.EVT_COMBOBOX, self.OnSelectItem, control)
    
    def GetControlValue(self):
        return self.control.GetValue()
    
    def UpdateBuddy(self):
        self.SetBuddyValue(self.GetControlValue())

    def UpdateControl(self):
        self.control.Clear()
        items = self.valueListFunctor()
        value = self.GetBuddyValue()
        self.control.SetItems(items)
        if value in items:
            self.control.SetValue(value)
        elif len(items) > 0:
            self.control.SetValue(items[0])
            self.UpdateBuddy()
        else:
            raise ValueError("Non existing value for drop down list.")
        wx.CallAfter(self.control.SetValue, self.GetBuddyValue())
        
    def OnSelectItem(self, event):
        """ User moved from one field to the other, copy latest values to the context """
        self.UpdateBuddy()
        event.Skip()

class ListBoxControl(BoundControl):
    def __init__(self, binder, control, labels = None, buddyClass = None, buddyField = None):
        BoundControl.__init__(self, binder, control, labels, buddyClass, buddyField)
        
    def UpdateBuddy(self):
        result = list()
        for i in range( self.control.GetCount() ):
            controlValue = self.control.GetString(i)
            if FilenameLabel() in self.labels:
                controlValue = controlValue.replace("\\", "/")
            result.append( controlValue )
        self.SetBuddyValue(result)

    def UpdateControl(self):
        self.control.Clear()
        for x in self.GetBuddyValue():
            self.control.Append(x)

class GridControl(BoundControl):
    def __init__(self, binder, control, labels = None, buddyClass = None, buddyField = None):
        BoundControl.__init__(self, binder, control, labels, buddyClass, buddyField)
        control.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnCellChange, control)
        self.cellChange = False
        
    def UpdateBuddy(self):
        replaceSlashes = False
        result = []
        for i in range( self.control.GetNumberRows() ):
            row = []
            for j in range( self.control.GetNumberCols() ):
                value = self.control.GetCellValue(i, j)
                if replaceSlashes:
                    value = value.replace("\\", "/")
                row.append( value )
            result.append(row)
        self.SetBuddyValue(result)

    def UpdateControl(self):
        self.cellChange = True
        if self.control.GetNumberRows() > 0:
            self.control.DeleteRows(0, self.control.GetNumberRows(), True)
        buddyValue = self.GetBuddyValue()
        self.control.AppendRows(len(buddyValue), True)
        for row in range( self.control.GetNumberRows() ):
            for col in range( self.control.GetNumberCols() ):
                self.control.SetCellValue(row, col, buddyValue[row][col])
        self.control.AutoSizeColumn(0)
        self.control.AutoSizeColumn(1)
        
        self.control.ForceRefresh()
        self.cellChange = False
    
    def OnCellChange(self, event):
        self.UpdateBuddy()
        if not self.cellChange:
            self.UpdateControl()
        event.Skip()
        
class CheckBoxControl(BoundControl):
    def __init__(self, binder, control, labels = None, buddyClass = None, buddyField = None):
        BoundControl.__init__(self, binder, control, labels, buddyClass, buddyField)
        
    def UpdateBuddy(self):
        self.SetBuddyValue(self.control.GetValue())

    def UpdateControl(self):
        self.control.SetValue(self.GetBuddyValue())
         
class ControlBinder:
    def __init__(self):
        self.controls = list()
        self.buddyClasses = dict()

    def SetBuddyClass(self, buddyClassName, buddyClass):
        self.buddyClasses[buddyClassName] = buddyClass
    
    def __GetLabels(self, isFilename = False):
        labels = []
        if isFilename:
            labels.append(FilenameLabel())
        return labels
    
    def AddTextControl(self, control, buddyClass = None, buddyField = None, isFilename = False):
        self.controls.append(TextControl(self, control, self.__GetLabels(isFilename), buddyClass, buddyField))

    def AddComboBox(self, control, valueListFunctor, buddyClass = None, buddyField = None, isFilename = False):
        self.controls.append(ComboBoxControl(self, control, valueListFunctor, self.__GetLabels(isFilename), buddyClass, buddyField))
        
    def AddDropDownList(self, control, valueListFunctor, buddyClass = None, buddyField = None, isFilename = False):
        self.controls.append(DropDownListControl(self, control, valueListFunctor, self.__GetLabels(isFilename), buddyClass, buddyField))

    def AddListBox(self, control, buddyClass = None, buddyField = None, isFilename = False):
        self.controls.append(ListBoxControl(self, control, self.__GetLabels(isFilename), buddyClass, buddyField))
        
    def AddGrid(self, control, buddyClass = None, buddyField = None, isFilename = False):
        self.controls.append(GridControl(self, control, self.__GetLabels(isFilename), buddyClass, buddyField))

    def AddCheckBox(self, control, buddyClass = None, buddyField = None):
        self.controls.append(CheckBoxControl(self, control, self.__GetLabels(), buddyClass, buddyField))

    def GetBuddyClass(self, boundControl):
        return self.buddyClasses[boundControl.buddyClass]
    
    def UpdateBuddies(self):
        for boundControl in self.controls:
            boundControl.UpdateBuddy()

    def UpdateControls(self):
        for boundControl in self.controls:
            boundControl.UpdateControl()
         
class Binder(ControlBinder):
    def __init__(self, target, defaultContainer = None):
        ControlBinder.__init__(self)
        self.target = target
        self.defaultContainer = defaultContainer

    def AddTextControl(self, controlName, container = None, buddyClass = None, buddyField = None, isFilename = False):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddTextControl(self, control, buddyClass, buddyField, isFilename)

    def AddComboBox(self, controlName, valueListFunctor, container = None, buddyClass = None, buddyField = None, isFilename = False):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddComboBox(self, control, valueListFunctor, buddyClass, buddyField, isFilename)
        
    def AddDropDownList(self, controlName, valueListFunctor, container = None, buddyClass = None, buddyField = None, isFilename = False):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddDropDownList(self, control, valueListFunctor, buddyClass, buddyField, isFilename)

    def AddListBox(self, controlName, container = None, buddyClass = None, buddyField = None, isFilename = False):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddListBox(self, control, buddyClass, buddyField, isFilename)
        
    def AddGrid(self, controlName, container = None, buddyClass = None, buddyField = None, isFilename = False):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddGrid(self, control, buddyClass, buddyField, isFilename)

    def AddCheckBox(self, controlName, container = None, buddyClass = None, buddyField = None):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddCheckBox(self, control, buddyClass, buddyField)
