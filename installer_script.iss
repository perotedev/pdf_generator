; Script do Inno Setup para o SGPP
; Este script cria um instalador profissional com suporte a atalhos, registro e atualizações.

[Setup]
; ID único do aplicativo (NÃO mude este ID em versões futuras para que a atualização funcione)
AppId={{A1B2C3D4-E5F6-4G7H-8I9J-K0L1M2N3O4P5}
AppName=SGPP
AppVersion=1.0.1
AppPublisher=PeroteDev
AppPublisherURL=https://perotedev.com
DefaultDirName={autopf}\SGPP
DefaultGroupName=SGPP
AllowNoIcons=yes
; Ícone do instalador
SetupIconFile=assets\sgpp.ico
; Onde o instalador será salvo
OutputDir=installer_output
OutputBaseFilename=SGPP_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Inclui todos os arquivos gerados pelo PyInstaller na pasta dist
Source: "dist\SGPP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SGPP"; Filename: "{app}\SGPP.exe"
Name: "{group}\{cm:UninstallProgram,SGPP}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\SGPP"; Filename: "{app}\SGPP.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SGPP.exe"; Description: "{cm:LaunchProgram,SGPP}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
