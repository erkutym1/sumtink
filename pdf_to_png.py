import tkinter as tk
from tkinter import filedialog, messagebox
import pymupdf  # PyMuPDF
import os
import webbrowser

class PdfToPngConverter:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF to PNG Converter")
        self.master.geometry("600x400")

        # Üst menü oluştur
        self.menu = tk.Menu(master)
        master.config(menu=self.menu)

        # Converted Files butonu ekle
        self.converted_files_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Converted Files", menu=self.converted_files_menu)
        self.converted_files_menu.add_command(label="Open ", command=self.open_converted_files)

        self.label = tk.Label(master, text="PDF dosyalarını seçin:")
        self.label.pack(pady=10)

        self.select_button = tk.Button(master, text="PDF Seç", command=self.select_pdf)
        self.select_button.pack(pady=5)

        self.pdf_file_label = tk.Label(master, text="", wraplength=500)
        self.pdf_file_label.pack(pady=10)

        self.convert_button = tk.Button(master, text="PNG'ye Dönüştür", command=self.convert_to_png, state="disabled")
        self.convert_button.pack(pady=10)

        self.selected_files = []

    def open_converted_files(self):
        # EvriTink yolunu aç
        evritink_folder = os.path.join(os.path.expanduser("~"), "Downloads", "EvriTink", "pdftopng")
        webbrowser.open(evritink_folder)

    def select_pdf(self):
        self.selected_files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if self.selected_files:
            files_list = "\n".join(os.path.basename(file) for file in self.selected_files)
            self.pdf_file_label.config(text=f"Seçilen PDF'ler:\n{files_list}")
            self.convert_button.config(state="normal")

    def convert_to_png(self):
        try:
            # Ana kaydetme klasörü
            main_save_folder = os.path.join(os.path.expanduser("~"), "Downloads", "EvriTink", "pdftopng")
            os.makedirs(main_save_folder, exist_ok=True)  # Ana klasörü oluştur

            for pdf_file in self.selected_files:
                pdf_document = pymupdf.open(pdf_file)

                # Her PDF için ayrı bir klasör oluştur
                pdf_folder = os.path.join(main_save_folder, os.path.basename(pdf_file).replace('.pdf', ''))
                os.makedirs(pdf_folder, exist_ok=True)

                for page_number in range(len(pdf_document)):
                    page = pdf_document.load_page(page_number)

                    # Görüntü kalitesini artırmak için dpi ayarı
                    pix = page.get_pixmap(dpi=300)  # dpi'yi 300 olarak ayarladık

                    # Sayfa numarasını dört basamaklı formatta ayarla
                    formatted_page_number = f"{page_number + 1:04}"  # Dört basamaklı sayfa numarası
                    output_file = os.path.join(pdf_folder, f"page_{formatted_page_number}.png")
                    pix.save(output_file)
                pdf_document.close()

            messagebox.showinfo("Başarılı", "Dönüştürme tamamlandı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Dönüştürme hatası: {e}")


# Uygulamanızı başlatacak kod burada olabilir
if __name__ == "__main__":
    root = tk.Tk()
    converter = PdfToPngConverter(root)
    root.mainloop()
