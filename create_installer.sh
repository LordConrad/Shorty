#!/bin/bash
set -e

echo "1/4: Krok 1 - Vytvářím binární soubor přes PyInstaller..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi
python build.py

echo "2/4: Krok 2 - Připravuji složku instalátoru..."
rm -rf Shorty_Installer
mkdir -p Shorty_Installer

cp dist/Shorty Shorty_Installer/
cp icon.png Shorty_Installer/

echo "3/4: Krok 3 - Vytvářím instalační skript install.sh..."
cat << 'INEOF' > Shorty_Installer/install.sh
#!/bin/bash

echo "Instaluji Shorty pro aktuálního uživatele (~/.local)..."
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons

BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons"
APP_DIR="$HOME/.local/share/applications"

# Kopírování aplikace
cp Shorty "$BIN_DIR/Shorty"
chmod +x "$BIN_DIR/Shorty"

# Kopírování ikony
cp icon.png "$ICON_DIR/shorty_icon.png"

# Vytvoření zástupce na plochu/menu (.desktop)
cat << DESKEOF > "$APP_DIR/Shorty.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Shorty
Comment=Nástroj pro rychlé stříhání videí
Exec=$BIN_DIR/Shorty
Icon=$ICON_DIR/shorty_icon.png
Terminal=false
Categories=AudioVideo;AudioVideoEditing;
DESKEOF

chmod +x "$APP_DIR/Shorty.desktop"
update-desktop-database "$APP_DIR" 2>/dev/null || true

echo ""
echo "=== Hotovo! ==="
echo "Shorty byl úspěšně nainstalován."
echo "Nyní byste jej měli najít v systémovém menu aplikací."
INEOF

chmod +x Shorty_Installer/install.sh

echo "4/4: Krok 4 - Komprimuji do finálního archivu..."
tar -czvf Shorty-Linux-Installer.tar.gz Shorty_Installer/

echo ""
echo "Vše dokončeno!"
echo "Soubor Shorty-Linux-Installer.tar.gz je připraven k distribuci."
