#ifndef AppVersion
  #define AppVersion "0.0.0-dev"
#endif

#define RootDir ExtractFileDir(SourcePath)

[Setup]
AppId={{9A6C4B5D-4B49-4F0F-9A89-1C7E6B2F7E31}
AppName=COMATS
AppVersion={#AppVersion}
AppVerName=COMATS {#AppVersion}

DefaultDirName={autopf}\COMATS
DefaultGroupName=COMATS

OutputDir={#RootDir}\installer-output
OutputBaseFilename=COMATS-{#AppVersion}-Setup

Compression=lzma2
SolidCompression=yes
DisableProgramGroupPage=yes

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin

UninstallDisplayIcon={app}\main.exe

CloseApplications=yes
RestartApplications=no

[Tasks]
Name: "desktopicon"; \
    Description: "Create a &desktop icon"; \
    GroupDescription: "Additional icons:"; \
    Flags: unchecked

[Files]
; Complete PyInstaller one-directory build
Source: "{#RootDir}\dist\main\*"; \
    DestDir: "{app}"; \
    Flags: recursesubdirs createallsubdirs ignoreversion

; Microsoft Visual C++ runtime
Source: "{#RootDir}\VC_redist.x64.exe"; \
    DestDir: "{tmp}"; \
    Flags: deleteafterinstall skipifsourcedoesntexist

[Icons]
Name: "{group}\COMATS"; \
    Filename: "{app}\main.exe"; \
    WorkingDir: "{app}"

Name: "{commondesktop}\COMATS"; \
    Filename: "{app}\main.exe"; \
    WorkingDir: "{app}"; \
    Tasks: desktopicon

[Run]
Filename: "{tmp}\VC_redist.x64.exe"; \
    Parameters: "/install /quiet /norestart"; \
    StatusMsg: "Installing Microsoft Visual C++ Runtime..."; \
    Flags: waituntilterminated runhidden skipifdoesntexist

Filename: "{app}\main.exe"; \
    WorkingDir: "{app}"; \
    Flags: nowait postinstall skipifsilent




