# VideoSlicer

VideoSlicer is a modern graphical user interface (GUI) utility designed for the rapid, lossless splitting of long video files, either by time duration or by a specific number of segments.

## Core Features
- **Ultra-fast Export:** Utilizes the lossless `ffmpeg -c copy` parameter. Videos are not re-encoded, allowing them to be split in a matter of milliseconds, even at 4K resolution, ensuring absolute zero quality degradation.
- **Dual Slicing Modes:** 
  - Split by constant duration (e.g., automatically slicing a video into exact 30-second segments).
  - Split by a fixed number of segments (e.g., dividing a video into 4 perfectly equal parts).
- **Interactive Timeline:** Features a custom-rendered timeline to preview the sliced segments beforehand. The timeline functions as an interactive control panel; clicking on any specific segment instantly seeks the video player to that exact position.
- **Graphical Progress Indication:** Includes a dedicated progress dialog that monitors background export threads. This prevents the main application thread from freezing or locking up during intensive operations (implemented via `QThread`).

## Technologies Used
The application is written in Python and leverages a modern technological stack:
- **PySide6 / PyQt6 (Qt Framework):** A robust C++ framework wrapped in Python that manages the user interface, including interactive dialogs and the native `QVideoWidget`. It also implements custom rendering on the timeline using the `QPainter` class.
- **FFmpeg:** A low-level multimedia framework used for the raw data stream slicing via the `subprocess` module. It requires `ffmpeg` to be installed and accessible in the system's environment variables (PATH).
- **PyInstaller:** Utilized by the automated build script to compile the application into pre-packaged, standalone executables (`.exe` for Windows or a standalone binary for Linux).

## Running from Source
```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate  # On Linux/macOS
# .\venv\Scripts\activate   # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

## Building Executables (.exe / Linux Standalone)
A configuration script is provided to automate the application compilation process. It must be executed within the activated `venv` environment:

```bash
# Execute the build script
python build.py
```

On **Linux** systems, the script generates a single standalone binary using the `--onefile` argument. The resulting executable is output to `dist/VideoSlicer`.

On **Windows** systems, the script creates a directory-based distribution utilizing the `--onedir` argument. This approach guarantees stability and prevents issues related to native PySide libraries. The final output is located at `dist/VideoSlicer/VideoSlicer.exe`.
