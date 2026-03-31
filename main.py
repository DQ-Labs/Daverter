import customtkinter as ctk
import threading
import subprocess
import os
import sys
from tkinter import filedialog

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

class VibeConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("Daverter")
        self.geometry("600x500")
        
        try:
            self.iconbitmap(resource_path("app.ico"))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
            pass # Icon optional

        # Variables
        self.batch_var = ctk.BooleanVar(value=False)

        # Layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Log area expands

        # --- Input Section ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.file_path_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Select a file...")
        self.file_path_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.browse_button = ctk.CTkButton(self.input_frame, text="Browse", command=self.browse_file, width=80)
        self.browse_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.batch_mode_switch = ctk.CTkSwitch(self.input_frame, text="Batch Mode", variable=self.batch_var)
        self.batch_mode_switch.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

        # --- Output Selection Row ---
        self.output_path_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Default (Source Folder)")
        self.output_path_entry.grid(row=2, column=0, padx=(10, 5), pady=(0, 10), sticky="ew")

        self.output_browse_button = ctk.CTkButton(self.input_frame, text="Browse Output...", command=self.browse_output, width=80)
        self.output_browse_button.grid(row=2, column=1, padx=(5, 10), pady=(0, 10))

        # --- Options & Action Section ---
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        self.formats = ["mp4", "mp3", "gif", "wav", "mkv"]
        self.format_menu = ctk.CTkOptionMenu(self.action_frame, values=self.formats)
        self.format_menu.set("mp4") # Default
        self.format_menu.grid(row=0, column=0, padx=20, pady=20)

        self.convert_button = ctk.CTkButton(self.action_frame, text="Convert", command=self.start_conversion_thread,
                                            fg_color="#009933", hover_color="#006622",
                                            border_width=2, border_color="white")
        self.convert_button.grid(row=0, column=1, padx=20, pady=20)

        # --- Feedback Section ---
        self.log_textbox = ctk.CTkTextbox(self, state="disabled")
        self.log_textbox.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.progress_bar.set(0)

    def browse_file(self):
        if self.batch_var.get():
            target = filedialog.askdirectory(parent=self)
        else:
            target = filedialog.askopenfilename(parent=self)
            
        if target:
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, target)

    def browse_output(self):
        target = filedialog.askdirectory(parent=self)
        if target:
            self.output_path_entry.delete(0, "end")
            self.output_path_entry.insert(0, target)

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
                
            # Fallback to system path or default assumption
            return "ffmpeg.exe"
        else:
            return "ffmpeg"

    def log_message(self, message):
        """Thread-safe way to append text to the log window."""
        def _log():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        self.after(0, _log)

    def start_conversion_thread(self):
        input_file = self.file_path_entry.get()
        if not input_file:
            self.log_message("Error: Please select a file or folder first.")
            return

        target_format = self.format_menu.get()
        is_batch = self.batch_var.get()
        
        # Disable button to prevent double clicks
        self.convert_button.configure(state="disabled")
        self.progress_bar.start()
        
        conversion_thread = threading.Thread(target=self.run_conversion, args=(input_file, target_format, is_batch))
        conversion_thread.daemon = True
        conversion_thread.start()

    def run_conversion(self, input_path, target_format, is_batch):
        try:
            ffmpeg_cmd = self.get_ffmpeg_path()
            self.log_message(f"Debug: Using FFmpeg path: {ffmpeg_cmd}")

            if not os.path.exists(ffmpeg_cmd):
                 self.log_message(f"ERROR: FFmpeg not found at {ffmpeg_cmd}")
                 return

            files_to_convert = []

            custom_output_dir = self.output_path_entry.get().strip()
            if custom_output_dir == "Default (Source Folder)":
                custom_output_dir = ""

            if is_batch:
                if not os.path.isdir(input_path):
                    self.log_message(f"ERROR: {input_path} is not a valid directory.")
                    return
                
                # Video and Audio extensions
                extensions = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.mp3', '.wav', '.aac', '.flac', '.m4a', '.ogg')
                for f in os.listdir(input_path):
                    if f.lower().endswith(extensions):
                        files_to_convert.append(os.path.join(input_path, f))
                
                if not files_to_convert:
                    self.log_message("ERROR: No compatible files found in folder.")
                    return
                
                if custom_output_dir:
                    output_dir = custom_output_dir
                else:
                    output_dir = os.path.join(input_path, "converted")
                
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
                filename = os.path.basename(current_file)
                name, _ = os.path.splitext(filename)
                output_filename = f"{name}_converted.{target_format}"
                output_path = os.path.join(output_dir, output_filename)

                if is_batch:
                    self.log_message(f"\nProcessing file {i} of {total_files}: {filename}...")
                else:
                    self.log_message(f"Starting conversion: {filename} -> {output_filename}")

                # Construct command
                command = [ffmpeg_cmd, "-i", current_file, "-y", output_path]
                
                creation_flags = 0
                if sys.platform.startswith("win"):
                    creation_flags = subprocess.CREATE_NO_WINDOW

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=creation_flags
                )

                # Read output log
                for line in process.stdout:
                    if line and not is_batch: # Only flood log in single mode
                        self.log_message(line.strip())
                
                process.wait()

                if process.returncode == 0:
                    self.log_message(f"SUCCESS: Saved to {output_path}")
                else:
                    self.log_message(f"FAILURE: FFmpeg exited with code {process.returncode} for {filename}")

            # Auto-open output folder
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
            # Re-enable UI
            self.after(0, lambda: self.progress_bar.stop())
            self.after(0, lambda: self.progress_bar.set(0))
            self.after(0, lambda: self.convert_button.configure(state="normal"))

if __name__ == "__main__":
    app = VibeConverterApp()
    app.mainloop()
