import tkinter as tk
from tkinter import Menu
import webbrowser  # Tarayıcıda link açmak için
import youtube_downloader
import pdf_to_png
import os

class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("SumTink Main Menu")
        self.master.geometry("500x350")

        # Hoş geldiniz mesajı
        self.welcome_label = tk.Label(master, text="Welcome to SumTink - Something I need!\n"
                                                   "Choose an application from the menu on top left\n\n"
                                                   "Do not close this page to use app",
                                      font=("Arial", 14), justify="center")
        self.welcome_label.pack(pady=35)


        self.welcome_label = tk.Label(master, text="by Erkut Yildirim",
                                      font=("Arial", 12), justify="center")
        self.welcome_label.pack()

        # LinkedIn linki etiketi
        self.link_label = tk.Label(master, text="Visit my LinkedIn Profile", font=("Arial", 12), fg="blue", cursor="hand2")
        self.link_label.pack(pady=10)
        self.link_label.bind("<Button-1>", self.open_linkedin)  # Tıklama olayını bağla

        # Menü oluştur
        self.menu = Menu(master)
        self.master.config(menu=self.menu)

        self.file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Applications", menu=self.file_menu)
        self.file_menu.add_command(label="YouTube Downloader", command=self.open_youtube_downloader)
        self.file_menu.add_command(label="PDF to PNG Converter", command=self.open_pdf_to_png)
        self.file_menu.add_command(label="Video Cutter", command=self.open_video_cutter)  # Yeni satır eklendi

        # Downloads menüsü ekle
        self.download_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Downloads", menu=self.download_menu)
        self.download_menu.add_command(label="Open Downloads Folder", command=self.open_downloads_folder)

    def open_linkedin(self, event):
        webbrowser.open_new("https://www.linkedin.com/in/erkutyildirim/")  # LinkedIn profiline git

    def open_youtube_downloader(self):
        new_window = tk.Toplevel(self.master)
        youtube_downloader.YouTubeDownloader(new_window)  # YouTube Downloader arayüzünü başlat

    def open_pdf_to_png(self):
        new_window = tk.Toplevel(self.master)
        pdf_to_png.PdfToPngConverter(new_window)  # PDF-PNG dönüştürücü arayüzünü başlat

    def open_video_cutter(self):
        import video_cutter  # Video cutter modülünü içe aktar
        new_window = tk.Toplevel(self.master)
        video_cutter.VideoCutterApp(new_window)  # Video cutter arayüzünü başlat

    def open_downloads_folder(self):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "EvriTink")  # Kullanıcının indirme klasörünü bul
        os.startfile(downloads_path)  # İndirme klasörünü aç

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
