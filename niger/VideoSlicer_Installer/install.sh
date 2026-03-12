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
