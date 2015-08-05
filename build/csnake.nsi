############################################################################################
#      NSIS Installation Script created by NSIS Quick Setup Script Generator v1.09.18
#               Entirely Edited with NullSoft Scriptable Installation System                
#              by Vlasis K. Barkas aka Red Wine red_wine@freemail.gr Sep 2006               
############################################################################################

# compiles with NSIS 3.0b1

!define APP_NAME "CSnake"
!define COMP_NAME "csnake-org"
!define WEB_SITE "https://github.com/csnake-org/CSnake"
!define VERSION_MAJOR 2
!define VERSION_MINOR 6
!define VERSION_BUILD 0
!define VERSION "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_BUILD}.0"
!define COPYRIGHT "${COMP_NAME} © 2015"
!define DESCRIPTION "Application"
!define MAIN_APP_EXE "csnGUI.exe"
!define INSTALL_TYPE "SetShellVarContext current"
!define REG_ROOT "HKCU"
!define REG_APP_PATH "Software\${APP_NAME}"
!define REG_UNINSTALL_PATH "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
!define DISPLAY_ICON_PATH "$INSTDIR\resources\Laticauda_colubrina.ico"
!define INSTALL_SIZE 66400

!define INSTALLER_NAME "${APP_NAME}-${VERSION}-Setup.exe"

######################################################################

VIProductVersion  "${VERSION}"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "CompanyName" "${COMP_NAME}"
VIAddVersionKey "LegalCopyright" "${COPYRIGHT}"
VIAddVersionKey "FileDescription" "${DESCRIPTION}"
VIAddVersionKey "FileVersion" "${VERSION}"

######################################################################

SetCompressor ZLIB
Name "${APP_NAME}"
Caption "${APP_NAME}"
OutFile "${INSTALLER_NAME}"
BrandingText "${APP_NAME}"
XPStyle on
InstallDirRegKey "${REG_ROOT}" "${REG_APP_PATH}" ""
InstallDir "$PROGRAMFILES\${APP_NAME}"
ShowInstDetails show

; messes up with start menu short-cuts otherwise...
RequestExecutionLevel admin

; variables
Var StartMenuFolder

######################################################################

; nsis
!include "MUI2.nsh"
!include "InstallOptions.nsh"

!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

#-------------------------------------
# Welcome
!insertmacro MUI_PAGE_WELCOME

#-------------------------------------
# Installation directory
!insertmacro MUI_PAGE_DIRECTORY

#-------------------------------------
# Start menu short-cuts
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "${APP_NAME}"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${REG_ROOT}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${REG_APP_PATH}" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"

!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

#-------------------------------------
# Installation
!insertmacro MUI_PAGE_INSTFILES

#-------------------------------------
# Finish
!define MUI_FINISHPAGE_RUN "$INSTDIR\${MAIN_APP_EXE}"
!insertmacro MUI_PAGE_FINISH

#-------------------------------------
# Uninstall pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

######################################################################

Section -MainProgram

    !define FILES_DIR "dist"

    ${INSTALL_TYPE}
    SetOverwrite ifnewer

    ; main files
    SetOutPath "$INSTDIR"
    File /r "${FILES_DIR}\*"
        
SectionEnd

######################################################################

Section -Icons_Reg
    SetOutPath "$INSTDIR"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Start menu
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
        ;MessageBox MB_OK "StartMenuFolder: '$StartMenuFolder', SMPROGRAMS: '$SMPROGRAMS'"
        CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
        ;MessageBox MB_OK "StartMenuFolder: '$StartMenuFolder', SMPROGRAMS: '$SMPROGRAMS'"
        CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}" "" "${DISPLAY_ICON_PATH}"
        CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall ${APP_NAME}.lnk" "$INSTDIR\Uninstall.exe"
        !ifdef WEB_SITE
            WriteIniStr "$INSTDIR\${APP_NAME} website.url" "InternetShortcut" "URL" "${WEB_SITE}"
            CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${APP_NAME} Website.lnk" "$INSTDIR\${APP_NAME} website.url"
        !endif
        ; Desktop short-cut
        CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}" "" "${DISPLAY_ICON_PATH}"
    !insertmacro MUI_STARTMENU_WRITE_END

    ; Registry
    WriteRegStr ${REG_ROOT} "${REG_APP_PATH}" "" "$INSTDIR"
    WriteRegStr ${REG_ROOT} "${REG_UNINSTALL_PATH}" "DisplayName" "${APP_NAME}"
    WriteRegStr ${REG_ROOT} "${REG_UNINSTALL_PATH}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr ${REG_ROOT} "${REG_UNINSTALL_PATH}" "DisplayIcon" "${DISPLAY_ICON_PATH}"
    WriteRegStr ${REG_ROOT} "${REG_UNINSTALL_PATH}" "DisplayVersion" "${VERSION}"
    WriteRegStr ${REG_ROOT} "${REG_UNINSTALL_PATH}" "Publisher" "${COMP_NAME}"
    WriteRegDWORD ${REG_ROOT} "${REG_UNINSTALL_PATH}" "EstimatedSize" ${INSTALL_SIZE}
    !ifdef WEB_SITE
        WriteRegStr ${REG_ROOT} "${REG_UNINSTALL_PATH}" "URLInfoAbout" "${WEB_SITE}"
    !endif
SectionEnd

######################################################################

Section Uninstall
    ${INSTALL_TYPE}
    ; Delete all the content of the $INSTDIR
    ; dangerous if INSTDIR is "Program Files"...
    RMDir /r "$INSTDIR"

    ; Clean start menu
    !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
    
    ;MessageBox MB_OK "StartMenuFolder: '$StartMenuFolder', SMPROGRAMS: '$SMPROGRAMS'"
    
    ;StrCmp $StartMenuFolder "" NO_SHORTCUTS
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall ${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\$StartMenuFolder"
    ;NO_SHORTCUTS:

    ; Clean desktop
    Delete "$DESKTOP\${APP_NAME}.lnk"
    
    ; Clean registry
    DeleteRegKey ${REG_ROOT} "${REG_APP_PATH}"
    DeleteRegKey ${REG_ROOT} "${REG_UNINSTALL_PATH}"
SectionEnd

######################################################################

