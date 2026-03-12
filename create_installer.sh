#!/bin/bash
set -e

echo "1/4: Krok 1 - Vytvářím binární soubor přes PyInstaller..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi
python build.py

echo "2/4: Krok 2 - Připravuji složku instalátoru..."
rm -rf VideoSlicer_Installer
mkdir -p VideoSlicer_Installer

cp dist/VideoSlicer VideoSlicer_Installer/
cp icon.png VideoSlicer_Installer/

echo "3/4: Krok 3 - Vytvářím instalační skript install.sh..."
cat << 'INEOF' > VideoSlicer_Installer/install.sh
#!/bin/bash

echo "Instaluji VideoSlicer pro aktuálního uživatele (~/.local)..."
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons

BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons"
APP_DIR="$HOME/.local/share/applications"

# Kopírování aplikace
cp VideoSlicer "$BIN_DIR/VideoSlicer"
chmod +x "$BIN_DIR/VideoSlicer"

# Kopírování ikony
cp icon.png "$ICON_DIR/videoslicer_icon.png"

# Vytvoření zástupce na plochu/menu (.desktop)
cat << DESKEOF > "$APP_DIR/VideoSlicer.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Video Slicer
Comment=Nástroj pro rychlé stříhání videí
Exec=$BIN_DIR/VideoSlicer
Icon=$ICON_DIR/videoslicer_icon.png
Terminal=false
Categories=AudioVideo;AudioVideoEditing;
DESKEOF

chmod +x "$APP_DIR/VideoSlicer.desktop"
update-desktop-database "$APP_DIR" 2>/dev/null || true

echo ""
echo "=== Hotovo! ==="
echo "VideoSlicer byl úspěšně nainstalován."
echo "Nyní byste jej měli najít v systémovém menu aplikací."
INEOF

chmod +x VideoSlicer_Installer/install.sh

echo "4/4: Krok 4 - Komprimuji do finálního archivu..."
tar -czvf VideoSlicer-Linux-Installer.tar.gz VideoSlicer_Installer/

echo ""
echo "Vše dokončeno!"
echo "Soubor VideoSlicer-Linux-Installer.tar.gz je připraven k distribuci."
