import customtkinter as ctk
import threading
import subprocess
import os
import sys
from tkinter import filedialog

# Set appearance and theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class VibeConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("VibeConverter")
        self.geometry("600x500")

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

        # --- Options & Action Section ---
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        self.formats = ["mp4", "mp3", "gif", "wav", "mkv"]
        self.format_menu = ctk.CTkOptionMenu(self.action_frame, values=self.formats)
        self.format_menu.set("mp4") # Default
        self.format_menu.grid(row=0, column=0, padx=20, pady=20)

        self.convert_button = ctk.CTkButton(self.action_frame, text="Convert", command=self.start_conversion_thread)
        self.convert_button.grid(row=0, column=1, padx=20, pady=20)

        # --- Feedback Section ---
        self.log_textbox = ctk.CTkTextbox(self, state="disabled")
        self.log_textbox.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.progress_bar.set(0)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, filename)

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
                bundled_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")
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
            self.log_message("Error: Please select a file first.")
            return

        target_format = self.format_menu.get()
        
        # Disable button to prevent double clicks
        self.convert_button.configure(state="disabled")
        self.progress_bar.start()
        
        conversion_thread = threading.Thread(target=self.run_conversion, args=(input_file, target_format))
        conversion_thread.daemon = True
        conversion_thread.start()

    def run_conversion(self, input_path, target_format):
        try:
            ffmpeg_cmd = self.get_ffmpeg_path()
            
            # Simple output filename generation
            dirname, filename = os.path.split(input_path)
            name, _ = os.path.splitext(filename)
            output_filename = f"{name}_converted.{target_format}"
            output_path = os.path.join(dirname, output_filename)

            self.log_message(f"Starting conversion: {filename} -> {output_filename}")
            
            # Construct command
            # -y overwrites output
            command = [ffmpeg_cmd, "-i", input_path, "-y", output_path]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            # Read output log
            for line in process.stdout:
                if line:
                    self.log_message(line.strip())
            
            process.wait()

            if process.returncode == 0:
                self.log_message(f"SUCCESS: Saved to {output_path}")
            else:
                self.log_message(f"FAILURE: FFmpeg exited with code {process.returncode}")

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
