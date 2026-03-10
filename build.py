import PyInstaller.__main__
import sys

# Definice společných parametrů pro PyInstaller pro obě platformy
common_args = [
    'main.py',
    '--name=VideoSlicer',
    '--windowed',                  # Vypne konzolové okno aplikace za chodem (Důležité pro GUI Qt)
    '--noconfirm',                 # Při sestavování rovnou potvrdí přepsání minulé verze
    '--clean',
    '--hidden-import=PySide6.QtCore',
    '--hidden-import=PySide6.QtGui',
    '--hidden-import=PySide6.QtWidgets',
    '--hidden-import=PySide6.QtMultimedia',
    '--hidden-import=PySide6.QtMultimediaWidgets'
]

if sys.platform.startswith('linux'):
    print("Spouštím build pro Linux...")
    linux_args = common_args + [
        '--onefile',                 # Vytvoří jenom jeden spustitelný .AppImage/Soubor bez tisíce knihoven vedle
        '--icon=assets/icon.png'     # Volitelně - ikona pokud byste časem nějakou chtěli přidat (není nutné)
    ]
    PyInstaller.__main__.run(linux_args)
    
elif sys.platform.startswith('win'):
    print("Spouštím build pro Windows...")
    windows_args = common_args + [
        '--onedir',                  # Na windowsu je 'onedir' stabilnější při práci s velkými moduly jako je QtMultimeda a ffmpeg.
        '--icon=assets/icon.ico' 
    ]
    PyInstaller.__main__.run(windows_args)
    
else:
    print(f"Nepodporovaný systém pro automatický build: {sys.platform}")
