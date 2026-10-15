#define RootDir ExtractFileDir(SourcePath)

[Setup]
AppId={{9A6C4B5D-4B49-4F0F-9A89-1C7E6B2F7E31}
AppName=COMATS
AppVersion=1.0.0
DefaultDirName={autopf}\COMATS
DefaultGroupName=COMATS
OutputBaseFilename=COMATS_Setup
Compression=lzma
SolidCompression=yes
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\main.exe

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; --- Required: PyInstaller runtime ---
Source: "{#RootDir}\dist\main\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#RootDir}\dist\main\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs createallsubdirs ignoreversion

; --- Flatten assets (so code can keep using "Images\...", etc.) ---
Source: "{#RootDir}\dist\main\_internal\Images\*"; DestDir: "{app}\Images"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{#RootDir}\dist\main\_internal\Resources\*"; DestDir: "{app}\Resources"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{#RootDir}\dist\main\_internal\Themes\*"; DestDir: "{app}\Themes"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{#RootDir}\dist\main\_internal\Unity\*"; DestDir: "{app}\Unity"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{#RootDir}\dist\main\_internal\Fonts\*"; DestDir: "{app}\Fonts"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "{#RootDir}\dist\main\_internal\COMATSeasteregg\*"; DestDir: "{app}\COMATSeasteregg"; Flags: recursesubdirs createallsubdirs ignoreversion

; --- Optional: Tests (ONLY if folder exists) ---
Source: "{#RootDir}\dist\main\_internal\Tests\*"; DestDir: "{app}\Tests"; Flags: recursesubdirs createallsubdirs ignoreversion skipifsourcedoesntexist

; --- VC++ runtime (matches your filename) ---
Source: "{#RootDir}\VC_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\COMATS"; Filename: "{app}\main.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\COMATS"; Filename: "{app}\main.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/install /quiet /norestart"; \
  StatusMsg: "Installing Microsoft Visual C++ Runtime..."; Flags: waituntilterminated runhidden
Filename: "{app}\main.exe"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent




