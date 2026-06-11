# Daverter v0.2

A modern, dark-mode GUI for FFmpeg built with Python and CustomTkinter. Daverter allows you to easily convert media files using a sleek interface, supporting both single-file and batch folder processing.

## Downloads & Pre-Built Binaries

You don't need Python or any development tools to run Daverter! Pre-compiled standalone applications are available:

- [Download for Windows / Linux](../../releases/latest) (Check the repository Releases tab)

---

## Features

- **Modern Dark-Mode GUI**: Built with CustomTkinter for a native-looking, professional interface.
- **Single File Conversion**: Quickly convert individual video or audio files.
- **Batch Folder Mode**: Process all media files in a folder at once (top level only, not recursive).
- **Custom Output Folder**: Choose where your converted files are saved, or default to a subfolder.
- **Silent/Background Processing**: Conversions run in the background without annoying popup console windows.

## Supported Formats

### Input Formats (Read)
In batch mode, Daverter picks up files with the following extensions (in single-file mode, any file FFmpeg can read will work):
- **Video**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`
- **Audio**: `.mp3`, `.wav`, `.aac`, `.flac`, `.m4a`, `.ogg`

### Output Formats (Write)
You can convert files to the following formats using the dropdown menu:
- `mp4`
- `mp3`
- `gif`
- `wav`
- `mkv`

## Developer Setup (Running from Source)

### Prerequisites
- **Python 3.x** installed.
- **FFmpeg**: Either installed on your system `PATH`, or `ffmpeg.exe` placed in the project's `bin/` folder (FFmpeg 8.x recommended).

### Installation

1.  **Clone the repository** (or extract the source).
2.  **Install Dependencies**:
    ```bash
    pip install customtkinter
    ```
    (Note: `pyinstaller` is required if you plan to build the executable)

3.  **FFmpeg Setup**:

    If FFmpeg is already installed on your system `PATH`, Daverter will find it automatically and you can skip this step. To use a local copy instead (required for building the standalone executable):
    -   Create a folder named `bin` in the project root directory.
    -   Download `ffmpeg.exe` (e.g. the latest release build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or [ffmpeg.org](https://ffmpeg.org/download.html)).
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

- **v0.2.1** (unreleased): Updated bundled FFmpeg to 8.1.1. FFmpeg is now found on the system `PATH` when no bundled copy exists; fixed launch-directory dependence and unicode handling in conversion logs.
- **v0.2**: Added automated cross-platform CI/CD builds (Windows and Linux binaries) via GitHub Actions.
- **v0.1**: Initial release. Basic FFmpeg integration with CustomTkinter GUI.

---
*Powered by FFmpeg and CustomTkinter.*
