import customtkinter as ctk
import threading
import subprocess
import os
import sys
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class VibeConverterApp(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        # Window setup — resizable with a minimum size
        self.title("Daverter")
        self.geometry("600x540")
        self.minsize(600, 540)

        try:
            self.iconbitmap(resource_path("app.ico"))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        # Variables
        self.input_path_var = ctk.StringVar()
        self.input_path_var.trace_add("write", self._on_batch_or_path_change)
        self.batch_var = ctk.BooleanVar(value=False)
        self.batch_var.trace_add("write", self._on_batch_or_path_change)
        self.current_process = None
        self.cancelled = False

        # Layout — row 3 is the log textbox (expands)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- Input Section ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.file_path_entry = ctk.CTkEntry(
            self.input_frame,
            textvariable=self.input_path_var,
            placeholder_text="Select a file, or drag & drop here..."
        )
        self.file_path_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(
            self.input_frame, text="Browse", command=self.browse_file, width=80
        )
        self.browse_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.batch_mode_switch = ctk.CTkSwitch(
            self.input_frame, text="Batch Mode", variable=self.batch_var
        )
        self.batch_mode_switch.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        self.file_count_label = ctk.CTkLabel(self.input_frame, text="")
        self.file_count_label.grid(row=1, column=1, padx=(5, 10), pady=(0, 10), sticky="e")

        # --- Output Selection Row ---
        self.output_path_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Default (Source Folder)"
        )
        self.output_path_entry.grid(row=2, column=0, padx=(10, 5), pady=(0, 10), sticky="ew")

        self.output_browse_button = ctk.CTkButton(
            self.input_frame, text="Browse Output...", command=self.browse_output, width=80
        )
        self.output_browse_button.grid(row=2, column=1, padx=(5, 10), pady=(0, 10))

        # --- Options & Action Section ---
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)
        self.action_frame.grid_columnconfigure(2, weight=1)

        self.formats = ["mp4", "mp3", "gif", "wav", "mkv", "flac", "aac", "webm", "mov"]
        self.format_menu = ctk.CTkOptionMenu(self.action_frame, values=self.formats)
        self.format_menu.set("mp4")
        self.format_menu.grid(row=0, column=0, padx=20, pady=20)

        self.preset_menu = ctk.CTkOptionMenu(
            self.action_frame,
            values=list(self.PRESETS.keys())
        )
        self.preset_menu.set("Default")
        self.preset_menu.grid(row=0, column=1, padx=20, pady=20)

        self.convert_button = ctk.CTkButton(
            self.action_frame, text="Convert", command=self.start_conversion_thread,
            fg_color="#009933", hover_color="#006622",
            border_width=2, border_color="white"
        )
        self.convert_button.grid(row=0, column=2, padx=20, pady=20)

        self.cancel_button = ctk.CTkButton(
            self.action_frame, text="Cancel", command=self.cancel_conversion,
            fg_color="#cc3333", hover_color="#991a1a",
            border_width=2, border_color="white"
        )
        # Hidden until a conversion starts

        # --- Log Header ---
        self.log_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_header_frame.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.log_header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.log_header_frame, text="Log", anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        self.clear_log_button = ctk.CTkButton(
            self.log_header_frame, text="Clear", width=60, command=self.clear_log,
            fg_color="transparent", border_width=1
        )
        self.clear_log_button.grid(row=0, column=1, sticky="e")

        # --- Log Textbox ---
        self.log_textbox = ctk.CTkTextbox(self, state="disabled")
        self.log_textbox.grid(row=3, column=0, padx=20, pady=(4, 0), sticky="nsew")

        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        self.progress_bar.set(0)

        # Register whole window as drag-and-drop target
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.handle_drop)

    # ------------------------------------------------------------------
    # Drag & drop
    # ------------------------------------------------------------------

    def handle_drop(self, event):
        """Accept a dragged file or folder onto the window."""
        # tkinterdnd2 wraps paths containing spaces in curly braces
        path = event.data.strip().strip("{}")
        self.input_path_var.set(path)
        if os.path.isdir(path):
            self.batch_var.set(True)
        else:
            self.batch_var.set(False)

    # ------------------------------------------------------------------
    # File count preview
    # ------------------------------------------------------------------

    # File type sets used for format auto-detection and batch scanning
    VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm'}
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg'}

    # Output formats classed by type
    VIDEO_OUTPUT_FORMATS = {'mp4', 'mkv', 'mov', 'webm', 'gif'}
    AUDIO_OUTPUT_FORMATS = {'mp3', 'aac', 'flac', 'wav'}
    LOSSLESS_OUTPUT_FORMATS = {'flac', 'wav'}

    # Preset FFmpeg flags keyed by preset name, then 'video' / 'audio'
    PRESETS = {
        "Default": {},
        "High Quality": {
            "video": ["-crf", "18", "-preset", "slow"],
            "audio": ["-b:a", "320k"],
        },
        "Small File": {
            "video": ["-crf", "28", "-preset", "fast"],
            "audio": ["-b:a", "128k"],
        },
        "Web Optimized": {
            "video": ["-crf", "23", "-preset", "medium", "-movflags", "+faststart"],
            "audio": ["-b:a", "192k"],
        },
    }

    def get_preset_flags(self, target_format, preset_name):
        """Return the FFmpeg flags for the chosen preset and output format."""
        if preset_name == "Default" or target_format not in (
            self.VIDEO_OUTPUT_FORMATS | self.AUDIO_OUTPUT_FORMATS
        ):
            return []
        preset = self.PRESETS[preset_name]
        if target_format in self.AUDIO_OUTPUT_FORMATS:
            # Lossless formats don't benefit from bitrate flags
            if target_format in self.LOSSLESS_OUTPUT_FORMATS:
                return []
            return preset.get("audio", [])
        # Video path
        if target_format == "gif":
            return []  # GIF has no meaningful CRF/preset
        if target_format == "webm":
            # VP9 uses constrained quality mode instead of libx264 presets
            webm_crf = {"High Quality": "20", "Small File": "33", "Web Optimized": "30"}
            return ["-crf", webm_crf.get(preset_name, "30"), "-b:v", "0"]
        return preset.get("video", [])

    def _on_batch_or_path_change(self, *args):
        """Update file count label and auto-select output format when path or batch toggle changes."""
        path = self.input_path_var.get().strip()
        is_batch = self.batch_var.get()

        # --- File count preview (batch mode only) ---
        if not is_batch:
            self.file_count_label.configure(text="")
        else:
            if not path or not os.path.isdir(path):
                self.file_count_label.configure(text="")
            else:
                all_extensions = self.VIDEO_EXTENSIONS | self.AUDIO_EXTENSIONS
                count = sum(
                    1 for _, _, files in os.walk(path)
                    for f in files
                    if os.path.splitext(f)[1].lower() in all_extensions
                )
                if count == 0:
                    self.file_count_label.configure(text="No compatible files", text_color="orange")
                else:
                    self.file_count_label.configure(
                        text=f"{count} file{'s' if count != 1 else ''} found",
                        text_color="#00cc44"
                    )

        # --- Auto-select output format (single file mode only) ---
        if not is_batch and path and os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in self.VIDEO_EXTENSIONS:
                self.format_menu.set("mp4")
            elif ext in self.AUDIO_EXTENSIONS:
                self.format_menu.set("mp3")

    # ------------------------------------------------------------------
    # Browse / output
    # ------------------------------------------------------------------

    def browse_file(self):
        if self.batch_var.get():
            target = filedialog.askdirectory(parent=self)
        else:
            target = filedialog.askopenfilename(parent=self)
        if target:
            self.input_path_var.set(target)

    def browse_output(self):
        target = filedialog.askdirectory(parent=self)
        if target:
            self.output_path_entry.delete(0, "end")
            self.output_path_entry.insert(0, target)

    # ------------------------------------------------------------------
    # FFmpeg path resolution
    # ------------------------------------------------------------------

    def get_ffmpeg_path(self):
        """
        Cross-platform helper to find ffmpeg.
        Linux: Relies on system PATH.
        Windows: Checks local bin/ or sys._MEIPASS (PyInstaller).
        """
        if sys.platform.startswith("linux"):
            return "ffmpeg"
        elif sys.platform.startswith("win"):
            # Check for bundled executable (PyInstaller)
            if hasattr(sys, "_MEIPASS"):
                bundled_path = os.path.join(sys._MEIPASS, "bin", "ffmpeg.exe")
                if os.path.exists(bundled_path):
                    return bundled_path
            # Check local bin folder
            local_bin = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")
            if os.path.exists(local_bin):
                return local_bin
            # Fallback to system PATH
            return "ffmpeg.exe"
        else:
            return "ffmpeg"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log_message(self, message):
        """Thread-safe way to append text to the log window."""
        def _log():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        self.after(0, _log)

    def clear_log(self):
        """Clear the log textbox."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    def cancel_conversion(self):
        self.cancelled = True
        if self.current_process:
            self.current_process.terminate()
        self.log_message("Cancelling...")

    def start_conversion_thread(self):
        input_file = self.input_path_var.get().strip()
        if not input_file:
            self.log_message("Error: Please select a file or folder first.")
            return

        target_format = self.format_menu.get()
        is_batch = self.batch_var.get()
        self.cancelled = False

        # Swap Convert for Cancel
        self.convert_button.grid_remove()
        self.cancel_button.grid(row=0, column=2, padx=20, pady=20)

        # Use determinate progress for batch, indeterminate for single
        if is_batch:
            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(0)
        else:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()

        conversion_thread = threading.Thread(
            target=self.run_conversion, args=(input_file, target_format, is_batch)
        )
        conversion_thread.daemon = True
        conversion_thread.start()

    def run_conversion(self, input_path, target_format, is_batch):
        try:
            ffmpeg_cmd = self.get_ffmpeg_path()
            self.log_message(f"Info: Using FFmpeg path: {ffmpeg_cmd}")

            if os.path.isabs(ffmpeg_cmd) and not os.path.exists(ffmpeg_cmd):
                self.log_message(f"ERROR: FFmpeg not found at {ffmpeg_cmd}")
                return

            files_to_convert = []
            custom_output_dir = self.output_path_entry.get().strip()
            preset_name = self.preset_menu.get()
            preset_flags = self.get_preset_flags(target_format, preset_name)

            all_extensions = self.VIDEO_EXTENSIONS | self.AUDIO_EXTENSIONS

            if is_batch:
                if not os.path.isdir(input_path):
                    self.log_message(f"ERROR: {input_path} is not a valid directory.")
                    return

                # Recurse into subdirectories with os.walk
                for root, _, files in os.walk(input_path):
                    for f in files:
                        if os.path.splitext(f)[1].lower() in all_extensions:
                            files_to_convert.append(os.path.join(root, f))

                if not files_to_convert:
                    self.log_message("ERROR: No compatible files found in folder.")
                    return

                output_dir = custom_output_dir if custom_output_dir else os.path.join(input_path, "converted")
                os.makedirs(output_dir, exist_ok=True)
                self.log_message(f"Batch mode started. Found {len(files_to_convert)} files.")
            else:
                files_to_convert = [input_path]
                if custom_output_dir:
                    output_dir = custom_output_dir
                    os.makedirs(output_dir, exist_ok=True)
                else:
                    output_dir = os.path.dirname(input_path)

            total_files = len(files_to_convert)

            for i, current_file in enumerate(files_to_convert, 1):
                if self.cancelled:
                    self.log_message("Conversion cancelled by user.")
                    break

                filename = os.path.basename(current_file)
                name, _ = os.path.splitext(filename)
                output_filename = f"{name}_converted.{target_format}"

                # Mirror subdirectory structure for recursive batch output
                if is_batch:
                    rel_dir = os.path.relpath(os.path.dirname(current_file), input_path)
                    file_output_dir = os.path.normpath(os.path.join(output_dir, rel_dir))
                    os.makedirs(file_output_dir, exist_ok=True)
                else:
                    file_output_dir = output_dir

                output_path = os.path.join(file_output_dir, output_filename)

                if is_batch:
                    self.log_message(f"\nProcessing file {i} of {total_files}: {filename}...")
                else:
                    self.log_message(f"Starting conversion: {filename} -> {output_filename}")

                command = [ffmpeg_cmd, "-i", current_file] + preset_flags + ["-y", output_path]

                creation_flags = 0
                if sys.platform.startswith("win"):
                    creation_flags = subprocess.CREATE_NO_WINDOW

                self.current_process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=creation_flags
                )

                output_lines = []
                for line in self.current_process.stdout:
                    if line:
                        if not is_batch:
                            self.log_message(line.strip())
                        else:
                            output_lines.append(line.strip())

                self.current_process.wait()

                if self.cancelled:
                    self.log_message("Conversion cancelled by user.")
                    break

                if self.current_process.returncode == 0:
                    self.log_message(f"SUCCESS: Saved to {output_path}")
                else:
                    self.log_message(
                        f"FAILURE: FFmpeg exited with code {self.current_process.returncode} for {filename}"
                    )
                    if is_batch:
                        for line in output_lines[-10:]:
                            self.log_message(f"  {line}")

                if is_batch:
                    self.after(0, lambda val=i / total_files: self.progress_bar.set(val))

            self.current_process = None

            if not self.cancelled:
                if sys.platform.startswith("win"):
                    try:
                        os.startfile(output_dir)
                        self.log_message(f"Opened output folder: {output_dir}")
                    except Exception as e:
                        self.log_message(f"Could not open folder: {e}")
                self.log_message("\n--- Task Completed ---")

        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")

        finally:
            def _reset_ui():
                self.progress_bar.stop()
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.set(0)
                self.cancel_button.grid_remove()
                self.convert_button.grid(row=0, column=2, padx=20, pady=20)
                self.convert_button.configure(state="normal")
            self.after(0, _reset_ui)


if __name__ == "__main__":
    app = VibeConverterApp()
    app.mainloop()
