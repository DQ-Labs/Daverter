# Daverter v0.7

A modern, dark-mode GUI for FFmpeg built with Python and CustomTkinter. Daverter allows you to easily convert media files using a sleek interface, supporting both single-file and batch folder processing.

## Downloads & Pre-Built Binaries

You don't need Python or any development tools to run Daverter! Pre-compiled standalone applications are available:

- [Download for Windows / Linux](../../releases/latest) (Check the repository Releases tab)

---

## Features

- **Modern Dark-Mode GUI**: Built with CustomTkinter for a native-looking, professional interface.
- **Single File Conversion**: Quickly convert individual video or audio files.
- **Batch Folder Mode**: Process entire directories at once — subfolders are scanned recursively and the folder structure is mirrored in the output.
- **Custom Output Folder**: Choose where your converted files are saved, or default to a subfolder.
- **Silent/Background Processing**: Conversions run in the background without annoying popup console windows.
- **Drag & Drop**: Drop files or folders directly onto the window to load them instantly.
- **Cancel Conversion**: Stop any in-progress conversion with a single click.
- **Batch Progress Bar**: A real progress bar tracks how many files have been processed in batch mode.
- **File Count Preview**: Batch mode shows how many compatible files are found in the selected folder before converting.

## Supported Formats

### Input Formats (Read)
In batch mode, Daverter picks up files with the following extensions (in single-file mode, any file FFmpeg can read will work):
- **Video**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`, `.webm`
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
- **FFmpeg**: Either installed on your system `PATH`, or `ffmpeg.exe` placed in the project's `bin/` folder (FFmpeg 8.x recommended).

### Installation

1.  **Clone the repository** (or extract the source).
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
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
    pyinstaller --noconfirm --onefile --windowed --name "Daverter" --icon="app.ico" --add-data "app.ico;." --add-data "bin/ffmpeg.exe;bin" --collect-all tkinterdnd2 --clean main.py
    ```

3.  **Locate the Executable**:
    The finished `Daverter.exe` will be generated in the `dist/` folder.

## Version History

- **v0.7** (unreleased): Updated bundled FFmpeg to 8.1.1; FFmpeg is now resolved from the system `PATH` when no bundled copy exists; fixed launch-directory dependence and unicode handling in conversion logs.
- **v0.6.5**: Conversion presets (Default / High Quality / Small File / Web Optimized); recursive batch mode mirrors subfolder structure.
- **v0.6**: Expanded output formats (FLAC, AAC, WEBM, MOV); auto-selects mp4/mp3 based on input type.
- **v0.5**: Drag & drop support, resizable window, file count preview, clear log button.
- **v0.4.4**: Added cancel button and determinate batch progress bar.
- **v0.3**: Bug fixes — resolved FFmpeg PATH detection on Linux, improved batch error reporting, added requirements.txt.
- **v0.2**: Added automated cross-platform CI/CD builds (Windows and Linux binaries) via GitHub Actions.
- **v0.1**: Initial release. Basic FFmpeg integration with CustomTkinter GUI.

---
*Powered by FFmpeg and CustomTkinter.*
