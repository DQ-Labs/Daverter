# Daverter v0.6

A modern, dark-mode GUI for FFmpeg built with Python and CustomTkinter. Daverter allows you to easily convert media files using a sleek interface, supporting both single-file and batch folder processing.

## Downloads & Pre-Built Binaries

You don't need Python or any development tools to run Daverter! Pre-compiled standalone applications are available:

- [Download for Windows / Linux](../../releases/latest) (Check the repository Releases tab)

---

## Features

- **Modern Dark-Mode GUI**: Built with CustomTkinter for a native-looking, professional interface.
- **Single File Conversion**: Quickly convert individual video or audio files.
- **Batch Folder Mode**: Process entire directories of files at once (recursive).
- **Custom Output Folder**: Choose where your converted files are saved, or default to a subfolder.
- **Silent/Background Processing**: Conversions run in the background without annoying popup console windows.
- **Drag & Drop**: Drop files or folders directly onto the window to load them instantly.
- **Cancel Conversion**: Stop any in-progress conversion with a single click.
- **Batch Progress Bar**: A real progress bar tracks how many files have been processed in batch mode.
- **File Count Preview**: Batch mode shows how many compatible files are found in the selected folder before converting.

## Supported Formats

### Input Formats (Read)
Daverter validates and processes files with the following extensions:
- **Video**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`
- **Audio**: `.mp3`, `.wav`, `.aac`, `.flac`, `.m4a`, `.ogg`

### Output Formats (Write)
You can convert files to the following formats using the dropdown menu:
- `mp4` *(default for video input)*
- `mp3` *(default for audio input)*
- `gif`
- `wav`
- `mkv`
- `flac`
- `aac`
- `webm`
- `mov`

## Developer Setup (Running from Source)

### Prerequisites
- **Python 3.x** installed.
- **FFmpeg**: You must have `ffmpeg.exe` available.

### Installation

1.  **Clone the repository** (or extract the source).
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: `pyinstaller` is required if you plan to build the executable)

3.  **FFmpeg Setup (Crucial)**:
    -   Create a folder named `bin` in the project root directory.
    -   Download `ffmpeg.exe` (from [ffmpeg.org](https://ffmpeg.org/download.html) or similar).
    -   Place `ffmpeg.exe` inside the `bin/` folder.
    -   Structure should look like:
        ```
        Daverter/
        ├── bin/
        │   └── ffmpeg.exe
        ├── main.py
        └── ...
        ```

4.  **Run the App**:
    ```bash
    python main.py
    ```

## Building for Windows

To create a standalone `.exe` file that includes the FFmpeg binary:

1.  Ensure you have `pyinstaller` installed:
    ```bash
    pip install pyinstaller
    ```
2.  Run the included build script:
    ```cmd
    build.bat
    ```
    Or manually run:
    ```cmd
    pyinstaller --noconfirm --onefile --windowed --name "Daverter" --add-data "bin/ffmpeg.exe;bin" --clean main.py
    ```

3.  **Locate the Executable**:
    The finished `Daverter.exe` will be generated in the `dist/` folder.

## Version History

- **v0.6**: Expanded output formats (FLAC, AAC, WEBM, MOV); auto-selects mp4/mp3 based on input type.
- **v0.5**: Drag & drop support, resizable window, file count preview, clear log button.
- **v0.4.4**: Added cancel button and determinate batch progress bar.
- **v0.3**: Bug fixes — resolved FFmpeg PATH detection on Linux, improved batch error reporting, added requirements.txt.
- **v0.2**: Added automated cross-platform CI/CD builds (Windows and Linux binaries) via GitHub Actions.
- **v0.1**: Initial release. Basic FFmpeg integration with CustomTkinter GUI.

---
*Powered by FFmpeg and CustomTkinter.*
