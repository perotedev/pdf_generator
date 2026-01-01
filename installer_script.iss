; Script do Inno Setup para o PDF Generator
; Este script cria um instalador profissional com suporte a atalhos, registro e atualizações.

[Setup]
; ID único do aplicativo (NÃO mude este ID em versões futuras para que a atualização funcione)
AppId={{A1B2C3D4-E5F6-4G7H-8I9J-K0L1M2N3O4P5}
AppName=PDF Generator
AppVersion=1.0.1
AppPublisher=PeroteDev
AppPublisherURL=https://perotedev.com
DefaultDirName={autopf}\PDF Generator
DefaultGroupName=PDF Generator
AllowNoIcons=yes
; Ícone do instalador
SetupIconFile=assets\pdf_generator.ico
; Onde o instalador será salvo
OutputDir=installer_output
OutputBaseFilename=PDF_Generator_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Inclui todos os arquivos gerados pelo PyInstaller na pasta dist
Source: "dist\PDF Generator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PDF Generator"; Filename: "{app}\PDF Generator.exe"
Name: "{group}\{cm:UninstallProgram,PDF Generator}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\PDF Generator"; Filename: "{app}\PDF Generator.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PDF Generator.exe"; Description: "{cm:LaunchProgram,PDF Generator}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
