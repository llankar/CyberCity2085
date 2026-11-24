#ifndef SourceDir
  #error SourceDir must point to the complete PyInstaller distribution.
#endif

#ifndef OutputDir
  #define OutputDir "dist"
#endif

#ifndef BuildVersion
  #define BuildVersion "dev"
#endif

[Setup]
AppId={{B56C89A4-8247-4E95-86E0-D6929AA2848B}
AppName=CyberCity 2085
AppVersion={#BuildVersion}
AppPublisher=CyberCity 2085
DefaultDirName={localappdata}\Programs\CyberCity2085
DefaultGroupName=CyberCity 2085
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=CyberCity2085-Setup
; Most of the game is already-compressed PNG/MP3 content. Fast LZMA avoids a
; multi-hour release step without changing the installed standalone payload.
Compression=lzma2/fast
SolidCompression=yes
; The shipped 8K tactical maps make the compressed payload larger than the
; 4.2 GB Windows single-Setup limit. Keep one self-contained installer package
; (Setup plus local data slices) without downloading or requiring runtimes.
DiskSpanning=yes
DiskSliceSize=2100000000
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
SetupLogging=yes
UninstallDisplayIcon={app}\CyberCity2085.exe
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\CyberCity 2085"; Filename: "{app}\CyberCity2085.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\CyberCity 2085"; Filename: "{app}\CyberCity2085.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked

[Run]
Filename: "{app}\CyberCity2085.exe"; Description: "Lancer CyberCity 2085"; Flags: nowait postinstall skipifsilent
