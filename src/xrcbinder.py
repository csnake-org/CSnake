import wx
from wx import xrc

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
        
    def HasBuddyValue(self):
        return hasattr(self.GetBuddyClass(), self.buddyField)
        
    def SetBuddyValue(self, value):
        if self.HasBuddyValue():
            setattr(self.GetBuddyClass(), self.buddyField, value)
        
    def GetBuddyValue(self):
        return getattr(self.GetBuddyClass(), self.buddyField)
        
    def OnKillFocus(self, event):
        """ User moved from one field to the other, copy latest values to the context """
        self.UpdateBuddy()
        self.UpdateControl()
        event.Skip()
        
class ControlWithField(BoundControl):
    def GetControlValue(self):
        controlValue = self.control.GetValue()
        if FilenameLabel() in self.labels:
            controlValue = controlValue.replace("\\", "/")
        return controlValue

class TextControl(ControlWithField):
    def __init__(self, binder, control, labels = None, buddyClass = None, buddyField = None):
        ControlWithField.__init__(self, binder, control, labels, buddyClass, buddyField)
        control.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus, control)
    
    def UpdateBuddy(self):
        self.SetBuddyValue(self.GetControlValue())

    def UpdateControl(self):
        if self.HasBuddyValue():
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

    def AddListBox(self, control, buddyClass = None, buddyField = None, isFilename = False):
        self.controls.append(ListBoxControl(self, control, self.__GetLabels(isFilename), buddyClass, buddyField))

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

    def AddListBox(self, controlName, container = None, buddyClass = None, buddyField = None, isFilename = False):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddListBox(self, control, buddyClass, buddyField, isFilename)

    def AddCheckBox(self, controlName, container = None, buddyClass = None, buddyField = None):
        if container is None:
            container = self.defaultContainer
        setattr(self.target, controlName, xrc.XRCCTRL(container, controlName))
        control = getattr(self.target, controlName)
        ControlBinder.AddCheckBox(self, control, buddyClass, buddyField)
