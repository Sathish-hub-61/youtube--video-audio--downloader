import tkinter as tk
from tkinter import filedialog
import threading
import os
import yt_dlp
import customtkinter as ctk
import shutil
import glob

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader (Video & Audio)")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Top bar
        top_frame = ctk.CTkFrame(self.root, height=50, corner_radius=10)
        top_frame.pack(fill="x", padx=10, pady=10)
        title_label = ctk.CTkLabel(top_frame, text="YouTube Downloader (Video & Audio)", font=("Segoe UI", 20, "bold"))
        title_label.pack(pady=10)

        # Main container
        main_container = ctk.CTkFrame(self.root, corner_radius=10)
        main_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Sidebar
        sidebar = ctk.CTkFrame(main_container, width=200, corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=(0, 10), pady=10)
        sidebar.pack_propagate(False)

        self.folder_btn = ctk.CTkButton(sidebar, text="Choose Download Folder", command=self.select_folder, height=50, font=("Segoe UI", 14), corner_radius=10)
        self.folder_btn.pack(pady=10, padx=10, fill="x")

        self.download_btn = ctk.CTkButton(sidebar, text="Start Download", command=self.start_download_thread, height=50, font=("Segoe UI", 14), corner_radius=10)
        self.download_btn.pack(pady=10, padx=10, fill="x")

        self.cancel_btn = ctk.CTkButton(sidebar, text="Cancel Download", command=self.cancel_download, state="disabled", height=50, font=("Segoe UI", 14), corner_radius=10)
        self.cancel_btn.pack(pady=10, padx=10, fill="x")

        # Main area
        main_area = ctk.CTkFrame(main_container, corner_radius=10)
        main_area.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)

        # URL input
        url_frame = ctk.CTkFrame(main_area, corner_radius=10)
        url_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(url_frame, text="Enter YouTube URL or Playlist:", font=("Segoe UI", 14)).pack(anchor="w", padx=10, pady=5)
        self.url_entry = ctk.CTkEntry(url_frame, width=400, font=("Segoe UI", 12), corner_radius=10)
        self.url_entry.pack(padx=10, pady=5, fill="x")

        # Mode selection
        mode_frame = ctk.CTkFrame(main_area, corner_radius=10)
        mode_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(mode_frame, text="Download Mode:", font=("Segoe UI", 14)).pack(anchor="w", padx=10, pady=5)
        self.mode_var = tk.StringVar(value="video")
        self.video_radio = ctk.CTkRadioButton(mode_frame, text="Download Video", variable=self.mode_var, value="video", command=self.toggle_mode, font=("Segoe UI", 12))
        self.video_radio.pack(side="left", padx=20, pady=5)
        self.audio_radio = ctk.CTkRadioButton(mode_frame, text="Download Audio (MP3)", variable=self.mode_var, value="audio", command=self.toggle_mode, font=("Segoe UI", 12))
        self.audio_radio.pack(side="left", padx=20, pady=5)

        # Quality options
        self.quality_frame = ctk.CTkFrame(main_area, corner_radius=10)
        self.quality_frame.pack(fill="x", pady=10, padx=10)
        self.res_label = ctk.CTkLabel(self.quality_frame, text="Video Resolution:", font=("Segoe UI", 14))
        self.res_options = ["144p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "best"]
        self.res_var = tk.StringVar(value="best")
        self.res_menu = ctk.CTkComboBox(self.quality_frame, variable=self.res_var, values=self.res_options, font=("Segoe UI", 12), corner_radius=10)
        self.bitrate_label = ctk.CTkLabel(self.quality_frame, text="Audio Bitrate (kbps):", font=("Segoe UI", 14))
        self.bitrate_options = ["64", "128", "192", "320"]
        self.bitrate_var = tk.StringVar(value="192")
        self.bitrate_menu = ctk.CTkComboBox(self.quality_frame, variable=self.bitrate_var, values=self.bitrate_options, font=("Segoe UI", 12), corner_radius=10)

        # Folder path
        self.folder_path = tk.StringVar(value=os.getcwd())
        self.folder_label = ctk.CTkLabel(main_area, textvariable=self.folder_path, font=("Segoe UI", 12))
        self.folder_label.pack(pady=5, padx=10, anchor="w")

        # Progress bar
        self.progress = ctk.CTkProgressBar(main_area, width=400, corner_radius=10)
        self.progress.pack(pady=10, padx=10, fill="x")
        self.progress.set(0)

        # Status
        self.status = ctk.CTkLabel(main_area, text="", font=("Segoe UI", 12))
        self.status.pack(pady=5, padx=10, anchor="w")

        self.download_thread = None
        self.cancel_flag = False

        self.toggle_mode()

    def toggle_mode(self):
        self.res_label.pack_forget()
        self.res_menu.pack_forget()
        self.bitrate_label.pack_forget()
        self.bitrate_menu.pack_forget()
        if self.mode_var.get() == "video":
            self.res_label.pack(side="left", padx=10, pady=5)
            self.res_menu.pack(side="left", padx=10, pady=5)
        else:
            self.bitrate_label.pack(side="left", padx=10, pady=5)
            self.bitrate_menu.pack(side="left", padx=10, pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def start_download_thread(self):
        self.cancel_flag = False
        self.progress.set(0)
        self.status.configure(text="Starting download...")
        self.download_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.download_thread = threading.Thread(target=self.download)
        self.download_thread.start()

    def cancel_download(self):
        self.cancel_flag = True
        self.status.configure(text="Cancelling download...")

    def progress_hook(self, d):
        if self.cancel_flag:
            raise yt_dlp.utils.DownloadCancelled()
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').strip('%')
            try:
                percent = float(percent_str)
                self.progress.set(percent / 100)
            except ValueError:
                pass
            self.status.configure(text=f"Downloading: {d['_percent_str']} ETA: {d.get('_eta_str','')}")
        elif d['status'] == 'finished':
            self.progress.set(1.0)
            self.status.configure(text="Download complete. Processing...")

    def download(self):
        url = self.url_entry.get().strip()
        output_path = self.folder_path.get()
        is_audio = self.mode_var.get() == "audio"
        resolution = self.res_var.get()
        bitrate = self.bitrate_var.get()

        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'noplaylist': False,
            'merge_output_format': 'mp4'
        }

        # Detect ffmpeg path
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = os.path.dirname(ffmpeg_path)
        else:
            common_ffmpeg_dirs = glob.glob(os.path.expandvars(
                r'%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_*\ffmpeg-*\bin'))
            if common_ffmpeg_dirs:
                ydl_opts['ffmpeg_location'] = common_ffmpeg_dirs[0]

        if is_audio:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate
            }]
        else:
            if resolution == "best":
                ydl_opts['format'] = "bestvideo+bestaudio/best"
            else:
                height = resolution.replace("p", "")
                # Force best available up to requested resolution
                ydl_opts['format'] = f"bestvideo[height<={height}]+bestaudio/best"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if not self.cancel_flag:
                self.status.configure(text="Download finished successfully.")
        except Exception as e:
            if "ffmpeg" in str(e).lower():
                self.status.configure(
                    text="Error: ffmpeg is required for video merging. Please install ffmpeg from https://ffmpeg.org/download.html")
            else:
                self.status.configure(text=f"Error: {e}")
        finally:
            self.download_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")

if __name__ == "__main__":
    root = ctk.CTk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
