; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Legend of the Five Rings: Character Manager"
!define PRODUCT_VERSION "3.9.2"
!define PRODUCT_PUBLISHER "openningia"
!define PRODUCT_WEB_SITE "http://code.google.com/p/l5rcm/"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\l5rcm.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; FONT INSTALLER
!include FontReg.nsh
!include FontName.nsh
!include WinMessages.nsh

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "l5rcm.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\l5rcm.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "l5rcm-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\OpenNingia\L5RCM"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File /r "..\dist\*.*"
  CreateDirectory "$SMPROGRAMS\OpenNingia\L5RCM"
  CreateShortCut "$SMPROGRAMS\OpenNingia\L5RCM\L5RCM.lnk" "$INSTDIR\l5rcm.exe"
  CreateShortCut "$DESKTOP\l5rcm.lnk" "$INSTDIR\l5rcm.exe"

  # Register File Extension
  WriteRegStr HKCR ".l5r" "" "L5Rcm.Character"
  WriteRegStr HKCR ".l5rcmpack" "" "L5Rcm.Pack"

  # Register File Type and assign an Icon
  WriteRegStr HKCR "L5Rcm.Character" "" "L5R: CM - Character File"
  WriteRegStr HKCR "L5Rcm.Character\DefaultIcon" "" "$INSTDIR\l5rcm.exe,0"

  WriteRegStr HKCR "L5Rcm.Pack" "" "L5R: CM - Data Pack File"
  WriteRegStr HKCR "L5Rcm.Pack\DefaultIcon" "" "$INSTDIR\l5rcm.exe,1"

  # Register the Verbs
    WriteRegStr HKCR "L5Rcm.Character\shell\open\command" "" '"$INSTDIR\l5rcm.exe" --open "%1"'
	WriteRegStr HKCR "L5Rcm.Pack\shell\open\command" "" '"$INSTDIR\l5rcm.exe" --import "%1"'
SectionEnd

Section "Fonts"
  StrCpy $FONT_DIR $FONTS
  #StrCpy $FONT_DIR "$WINDIR\Fonts"

  !insertmacro InstallTTFFont "fonts\OLDSH___.TTF"
  !insertmacro InstallTTFFont "fonts\OLDSIH__.TTF"
  !insertmacro InstallTTFFont "fonts\OLDSSCH_.TTF"

  SendMessage ${HWND_BROADCAST} ${WM_FONTCHANGE} 0 0 /TIMEOUT=5000
SectionEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
  CreateShortCut "$SMPROGRAMS\OpenNingia\L5RCM\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\l5rcm.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\l5rcm.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\*.*"
  Delete "$SMPROGRAMS\OpenNingia\L5RCM\Uninstall.lnk"
  Delete "$DESKTOP\L5RCM.lnk"
  Delete "$SMPROGRAMS\OpenNingia\L5RCM\L5RCM.lnk"
  RMDir "$SMPROGRAMS\OpenNingia\L5RCM"
  RMDir "$SMPROGRAMS\OpenNingia"
  RMDir /r "$INSTDIR"
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  # Remove File Type and icon
  DeleteRegKey HKCR "L5Rcm.Character"
  DeleteRegKey HKCR ".l5r"

  DeleteRegKey HKCR "L5Rcm.Pack"
  DeleteRegKey HKCR ".l5rcmpack"

  SetAutoClose true
SectionEnd
