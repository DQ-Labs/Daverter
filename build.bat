venv\Scripts\pyinstaller --noconfirm --onefile --windowed --name "Daverter" --icon="app.ico" --add-data "app.ico;." --add-data "bin/ffmpeg.exe;bin" --collect-all tkinterdnd2 --clean main.py
