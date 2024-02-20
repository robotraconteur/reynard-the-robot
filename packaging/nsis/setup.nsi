!define VERSIONMAJOR 0
!define VERSIONMINOR 1
!define VERSIONBUILD 0

!define APPNAME "Reynard the Robot"
!define COMPANYNAME "Robot Raconteur"
!define DESCRIPTION "Reynard the Robot Raconteur educational robot"

; Include Modern UI
!include "MUI2.nsh"

; Include LogicLib for logical operations
!include LogicLib.nsh

; Include x64.nsh for 64-bit support
!include x64.nsh

; General
Name "${APPNAME}"
Outfile "reynand-the-robot-${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}-setup-win64.exe"
InstallDir "$PROGRAMFILES64\${COMPANYNAME}\${APPNAME}"


; Strings

!define MUI_WELCOMEPAGE_TITLE "Welcome to Reynard the Robot"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of Reynard the Robot."

!define MUI_DIRECTORYPAGE_TEXT_TOP "Select Installation Folder"

!define MUI_FINISHPAGE_TITLE "Installation Complete"

!define MUI_FINISHPAGE_TEXT  "Reynard the Robot has been successfully installed on your computer."

!define MUI_UNTEXT_UNINSTALLER_SUBTITLE "MUI_UNCONFIRMPAGE_TEXT_TOP "

!define MUI_LICENSEPAGE_TEXT_TOP "License Agreement"
!define MUI_LICENSEPAGE_TEXT_BOTTOM "Please read the following license agreements carefully."

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Default section
Section

    ; Check if the system is 64-bit
    ${If} ${RunningX64}
        ; If it is, continue with the installation
    ${Else}
        ; If it's not, show a message box and abort the installation
        MessageBox MB_OK|MB_ICONSTOP "This program requires a 64-bit system."
        Abort
    ${EndIf}

    ; Set registry view to 64-bit
    SetRegView 64

    ; Set output path to the installation directory.
    SetOutPath $INSTDIR

    ; Include dist files
    File /r "..\..\dist\reynard-the-robot\*"    

    ; Create a shortcut named "Reynard the Robot" on the desktop
    CreateDirectory "$SMPROGRAMS\${COMPANYNAME}"
    CreateShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\reynard-the-robot.exe"

    ; Store installation folder
    WriteRegStr HKCU "Software\${COMPANYNAME}\${APPNAME}" "" $INSTDIR

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstaller.exe"

    ; Write uninstaller registry key
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\Uninstaller.exe"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\reynard-the-robot.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" "${VERSIONMAJOR}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" "${VERSIONMINOR}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionBuild" "${VERSIONBUILD}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"

SectionEnd

; Uninstaller section
Section "Uninstall"

    ; Set registry view to 64-bit
    SetRegView 64

    ; Set output path to the installation directory.
    SetOutPath $INSTDIR

    ; Remove registry keys
    DeleteRegKey HKCU "Software\${COMPANYNAME}\${APPNAME}"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"

    ; Remove files and uninstaller
    Delete "$INSTDIR\reynard-the-robot.exe"
    RMDir /r "$INSTDIR\_internal"
    Delete "$INSTDIR\Uninstaller.exe"

    ; Remove directories used
    RMDir "$INSTDIR"

SectionEnd