import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time
import os
import ffmpeg

class VideoCutterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Cutter with Cursor")
        self.master.geometry("800x800")

        self.video_path = ""
        self.cap = None
        self.total_frames = 0
        self.fps = 30  # Sabit fps

        self.playing = False
        self.current_frame_idx = 0

        # Video gösterme için label (siyah arkaplanlı)
        self.video_label = tk.Label(master, bg="black")
        self.video_label.pack(pady=10)

        # Video seçme butonu
        self.select_btn = tk.Button(master, text="Video Seç", command=self.select_video)
        self.select_btn.pack(pady=5)

        # Başlangıç ve Bitiş frame sliderları
        self.start_slider = tk.Scale(master, from_=0, to=0, orient=tk.HORIZONTAL, label="Başlangıç Frame'i")
        self.start_slider.pack(fill="x", padx=20)

        self.end_slider = tk.Scale(master, from_=0, to=0, orient=tk.HORIZONTAL, label="Bitiş Frame'i", command=self.on_end_slider_move)
        self.end_slider.pack(fill="x", padx=20)
        self.end_slider.bind("<ButtonRelease-1>", self.on_end_slider_release)  # Mouse bırakma olayını yakala

        # Play / Pause butonları
        controls = tk.Frame(master)
        controls.pack(pady=5)
        self.play_btn = tk.Button(controls, text="Play", command=self.play_video)
        self.play_btn.pack(side="left", padx=5)

        self.pause_btn = tk.Button(controls, text="Pause", command=self.pause_video)
        self.pause_btn.pack(side="left", padx=5)

        # Kesme butonu
        self.cut_btn = tk.Button(master, text="Videoyu Kes", command=self.cut_video, state="disabled")
        self.cut_btn.pack(pady=10)

    def select_video(self):
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")])
        if filename:
            self.video_path = filename
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(self.video_path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # fps sabit 30
            self.fps = 30
            # Sliderları güncelle
            self.start_slider.config(to=self.total_frames - 1)
            self.end_slider.config(to=self.total_frames - 1)
            self.end_slider.set(self.total_frames - 1)
            self.current_frame_idx = 0
            self.cut_btn.config(state="normal")
            self.show_frame(0)

    def show_frame(self, frame_idx):
        if not self.cap or frame_idx >= self.total_frames or frame_idx < 0:
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = self.cap.read()
        if not ret:
            return
        # BGR'den RGB'ye çevir
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Görüntüyü 640x360'a küçült
        frame = cv2.resize(frame, (640, 360))
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk  # Referansı tut
        self.video_label.config(image=imgtk)
        self.current_frame_idx = frame_idx

    def play_video(self):
        if not self.cap:
            return
        if self.playing:
            # Zaten oynuyor, tekrar başlatma
            return
        # Play başlatılırken current_frame_idx = başlangıç slider'ı
        self.current_frame_idx = self.start_slider.get()
        self.playing = True

        def run():
            while self.playing and self.current_frame_idx < self.total_frames:
                self.show_frame(self.current_frame_idx)
                self.start_slider.set(self.current_frame_idx)
                # Bitiş sliderını aşma
                if self.current_frame_idx > self.end_slider.get():
                    # Bitiş frame'ine ulaştı, durdur
                    self.playing = False
                    break
                self.current_frame_idx += 1
                time.sleep(1 / self.fps)

        threading.Thread(target=run, daemon=True).start()

    def pause_video(self):
        self.playing = False

    # Slider sürüklendikçe anlık bitiş frame gösterimi
    def on_end_slider_move(self, val):
        if not self.playing:
            frame_idx = int(val)
            # Başlangıç frame'den küçük olmasın
            if frame_idx <= self.start_slider.get():
                frame_idx = self.start_slider.get() + 1
                self.end_slider.set(frame_idx)
            self.show_frame(frame_idx)
            self.current_frame_idx = frame_idx

    # Slider bırakıldığında video başa dönsün
    def on_end_slider_release(self, event):
        if not self.playing:
            self.show_frame(0)
            self.current_frame_idx = 0
            self.start_slider.set(0)
            # Bitiş sliderını da geçerli değer olarak ayarla
            self.end_slider.set(max(self.end_slider.get(), 0))

    def cut_video(self):
        if not self.video_path:
            messagebox.showerror("Hata", "Önce video seçin!")
            return
        start_frame = self.start_slider.get()
        end_frame = self.end_slider.get()
        if start_frame >= end_frame:
            messagebox.showerror("Hata", "Bitiş frame'i başlangıç frame'inden büyük olmalı!")
            return
        start_sec = start_frame / self.fps
        end_sec = end_frame / self.fps

        save_folder = os.path.join(os.path.expanduser("~"), "Downloads", "EvriTink", "videocutter")
        os.makedirs(save_folder, exist_ok=True)
        base_name = os.path.basename(self.video_path)
        output_path = os.path.join(save_folder, f"cut_{base_name}")

        try:
            (
                ffmpeg
                .input(self.video_path, ss=start_sec, to=end_sec)
                .output(output_path, codec='copy')
                .run(overwrite_output=True)
            )
            messagebox.showinfo("Başarılı", f"Video kesildi:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Kesme başarısız oldu:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCutterApp(root)
    root.mainloop()
