import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests
import yt_dlp
import os
import io
import webbrowser

class YouTubeDownloader:
    def __init__(self, master):
        self.master = master
        self.master.title("TubDown by Erkut Yildirim")  # Pencere başlığını değiştirdik
        self.master.geometry("600x600")  # Pencere boyutunu büyüttük

        # Üst menü oluştur
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

        # Downloads butonu ekle
        self.downloads_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Downloads", menu=self.downloads_menu)
        self.downloads_menu.add_command(label="Open", command=self.open_downloads)

        # Video URL Girişi
        self.url_label = tk.Label(master, text="YouTube Video veya Playlist URL:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(master, width=70)  # Giriş alanını genişlettik
        self.url_entry.pack(pady=5)

        # Bilgi Butonu
        self.info_button = tk.Button(master, text="Get Video Info", command=self.get_video_info, bg="lightblue")
        self.info_button.pack(pady=10)

        # Başlık
        self.title_label = tk.Label(master, text="", font=("Arial", 16))  # Font boyutunu büyüttük
        self.title_label.pack(pady=5)

        # Kapak Fotoğrafı
        self.thumbnail_label = tk.Label(master)
        self.thumbnail_label.pack(pady=5)

        # İndirme Türü Seçimi
        self.download_type_label = tk.Label(master, text="Select Download Type:")
        self.download_type_label.pack(pady=5)
        self.download_type_combo = ttk.Combobox(master, values=["Video (MP4)", "Audio (MP3)"], state="readonly")
        self.download_type_combo.pack(pady=5)
        self.download_type_combo.current(0)  # Varsayılan olarak video seçili

        # Çözünürlük Seçimi
        self.resolution_label = tk.Label(master, text="Select Resolution:")
        self.resolution_label.pack(pady=5)
        self.resolution_combo = ttk.Combobox(master, values=["480p", "720p", "1080p"], state="readonly")
        self.resolution_combo.pack(pady=5)
        self.resolution_combo.current(0)  # Varsayılan olarak 480p seçili

        # İndirme Butonu
        self.download_button = tk.Button(master, text="Download", command=self.download_media, bg="lightgreen")
        self.download_button.pack(pady=10)

        # Yükleniyor Etiketi
        self.loading_label = tk.Label(master, text="", font=("Arial", 12))
        self.loading_label.pack(pady=5)

        # Sistem indirme yolunu ayarla
        self.download_folder = os.path.join(os.path.expanduser("~"), "Downloads", "EvriTink", "tubdown")
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)  # İndirme dizinini oluştur

    def open_downloads(self):
        webbrowser.open(self.download_folder)  # İndirme klasörünü aç

    def get_video_info(self):
        video_url = self.url_entry.get()
        self.loading_label.config(text="Yükleniyor...")  # Yükleniyor mesajı
        self.master.update_idletasks()  # Arayüzü güncelle

        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(video_url, download=False)
                self.title_label.config(text=info['title'])

                # Kapak Fotoğrafı
                if 'thumbnail' in info:
                    thumbnail_url = info['thumbnail']
                    self.load_thumbnail(thumbnail_url)  # Resmi yükle
                else:
                    self.thumbnail_label.config(text="No Thumbnail Available")

                # Playlist kontrolü ve çözünürlük ayarı
                if 'playlist' in video_url:
                    self.resolution_label.config(text="Select Maximum Resolution:")
                    self.resolution_combo['values'] = ["480p", "720p", "1080p", "1440p", "2160p"]
                    self.resolution_combo.current(2)  # Varsayılan olarak 1080p seçili
                else:
                    self.resolution_label.config(text="Select Resolution:")
                    self.resolution_combo['values'] = ["480p", "720p", "1080p"]
                    self.resolution_combo.current(0)  # Varsayılan olarak 480p seçili

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.loading_label.config(text="")  # Yükleniyor mesajını kaldır

    def load_thumbnail(self, url):
        try:
            response = requests.get(url)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))  # io.BytesIO ile görüntü verisini kullan
            img.thumbnail((200, 200))  # Resmi küçült
            self.thumbnail = ImageTk.PhotoImage(img)
            self.thumbnail_label.config(image=self.thumbnail)
            self.thumbnail_label.image = self.thumbnail
        except Exception as e:
            messagebox.showerror("Error", f"Could not load thumbnail: {str(e)}")

    def download_media(self):
        video_url = self.url_entry.get()
        max_resolution = self.resolution_combo.get().replace("p", "")
        download_type = self.download_type_combo.get()
        self.loading_label.config(text="İndiriliyor...")  # İndirilirken yükleniyor mesajı
        self.master.update_idletasks()  # Arayüzü güncelle

        try:
            if download_type == "Video (MP4)":
                ydl_opts = {
                    'format': f'bestvideo[height<={max_resolution}]+bestaudio/best',
                    'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',  # Videoyu MP4 formatında indir
                    'noupdate': True,  # Dosya varsa üzerine yaz
                }
            elif download_type == "Audio (MP3)":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',  # Ses MP3 formatında olacak
                        'preferredquality': '192',  # En yüksek kalitede olacak
                    }],
                    'noupdate': True,  # Dosya varsa üzerine yaz
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if "playlist" in video_url:  # Playlist kontrolü
                    ydl.download([video_url])  # Playlisti indir
                else:
                    ydl.download([video_url])  # Tek videoyu indir

            self.loading_label.config(text="Tamamlandı!")  # Başarı mesajı

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.loading_label.config(text="")  # Yükleniyor mesajını kaldır

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
