import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import cv2
import pytesseract
from PIL import Image
import numpy as np
import time

# Caminho do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

DB_PATH = "plates.db"

# ---------- Banco de dados ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT UNIQUE NOT NULL,
            owner TEXT,
            vehicle TEXT,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

def normalize_plate(s):
    if s is None:
        return ""
    return ''.join(filter(str.isalnum, str(s).upper()))

def add_plate(plate, owner="", vehicle="", note=""):
    plate = normalize_plate(plate)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO plates (plate, owner, vehicle, note) VALUES (?, ?, ?, ?)",
                  (plate, owner, vehicle, note))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def update_plate(id_, plate, owner, vehicle, note):
    plate = normalize_plate(plate)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            UPDATE plates
            SET plate=?, owner=?, vehicle=?, note=?
            WHERE id=?
        """, (plate, owner, vehicle, note, id_))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()

def delete_plate(id_):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM plates WHERE id=?", (id_,))
    conn.commit()
    conn.close()

def get_all_plates():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, plate, owner, vehicle, note FROM plates ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def find_plate_db(plate):
    plate = normalize_plate(plate)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM plates WHERE plate=?", (plate,))
    row = c.fetchone()
    conn.close()
    return row


# ---------- Tkinter App ----------
class PlatesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Placas - IFPE")
        self.root.geometry("860x480")
        self.camera_running = False
        self.selected_id = None

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        # Lista de placas
        self.tree = ttk.Treeview(frame, columns=("id","plate", "owner", "vehicle", "note"), show="headings", height=18)
        self.tree.heading("id", text="ID")
        self.tree.heading("plate", text="Placa")
        self.tree.heading("owner", text="Proprietário")
        self.tree.heading("vehicle", text="Veículo")
        self.tree.heading("note", text="Observação")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("plate", width=120, anchor="center")
        self.tree.column("owner", width=180, anchor="center")
        self.tree.column("vehicle", width=160, anchor="center")
        self.tree.column("note", width=200, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="left", fill="y")

        # Painel lateral
        right = ttk.Frame(frame, padding=(10,0,0,0))
        right.pack(side="right", fill="y")

        ttk.Label(right, text="Placa:").pack(anchor="w")
        self.entry_plate = ttk.Entry(right)
        self.entry_plate.pack(fill="x")

        ttk.Label(right, text="Proprietário:").pack(anchor="w", pady=(8,0))
        self.entry_owner = ttk.Entry(right)
        self.entry_owner.pack(fill="x")

        ttk.Label(right, text="Veículo:").pack(anchor="w", pady=(8,0))
        self.entry_vehicle = ttk.Entry(right)
        self.entry_vehicle.pack(fill="x")

        ttk.Label(right, text="Observação:").pack(anchor="w", pady=(8,0))
        self.entry_note = ttk.Entry(right)
        self.entry_note.pack(fill="x")

        ttk.Button(right, text="Adicionar", command=self.on_add).pack(fill="x", pady=(12,4))
        ttk.Button(right, text="Editar selecionado", command=self.on_edit).pack(fill="x", pady=4)
        ttk.Button(right, text="Excluir selecionado", command=self.on_delete).pack(fill="x", pady=4)
        ttk.Button(right, text="Atualizar lista", command=self.refresh_list).pack(fill="x", pady=4)

        ttk.Button(right, text="Ligar câmera (OCR)", command=self.start_camera_thread).pack(fill="x", pady=(20,4))

        self.status_label = ttk.Label(right, text="Status: aguardando...", foreground="blue")
        self.status_label.pack(pady=10)

    # ---------- CRUD ----------
    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in get_all_plates():
            self.tree.insert("", "end", values=item)

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        self.selected_id = values[0]

        self.entry_plate.delete(0, tk.END)
        self.entry_plate.insert(0, values[1])

        self.entry_owner.delete(0, tk.END)
        self.entry_owner.insert(0, values[2])

        self.entry_vehicle.delete(0, tk.END)
        self.entry_vehicle.insert(0, values[3])

        self.entry_note.delete(0, tk.END)
        self.entry_note.insert(0, values[4])

    def on_add(self):
        plate = self.entry_plate.get().strip()
        if not plate:
            messagebox.showwarning("Aviso", "Digite a placa.")
            return

        ok, err = add_plate(
            plate,
            self.entry_owner.get().strip(),
            self.entry_vehicle.get().strip(),
            self.entry_note.get().strip()
        )

        if ok:
            messagebox.showinfo("Sucesso", "Placa cadastrada.")
            self.refresh_list()
        else:
            messagebox.showerror("Erro", err)

    def on_edit(self):
        if not self.selected_id:
            messagebox.showwarning("Aviso", "Selecione uma placa para editar.")
            return

        ok, err = update_plate(
            self.selected_id,
            self.entry_plate.get().strip(),
            self.entry_owner.get().strip(),
            self.entry_vehicle.get().strip(),
            self.entry_note.get().strip()
        )

        if ok:
            messagebox.showinfo("Sucesso", "Placa atualizada.")
            self.refresh_list()
        else:
            messagebox.showerror("Erro", err)

    def on_delete(self):
        if not self.selected_id:
            messagebox.showwarning("Aviso", "Selecione uma placa para excluir.")
            return

        if messagebox.askyesno("Confirmar", "Deseja realmente excluir esta placa?"):
            delete_plate(self.selected_id)
            self.refresh_list()
            self.selected_id = None

            self.entry_plate.delete(0, tk.END)
            self.entry_owner.delete(0, tk.END)
            self.entry_vehicle.delete(0, tk.END)
            self.entry_note.delete(0, tk.END)

    # ---------- CÂMERA + OCR ----------
    def start_camera_thread(self):
        if self.camera_running:
            messagebox.showinfo("Aviso", "A câmera já está ligada.")
            return
        self.camera_running = True
        threading.Thread(target=self.camera_loop, daemon=True).start()

    def camera_loop(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.update_status("Erro ao acessar câmera!", "red")
            self.camera_running = False
            return

        self.update_status("Câmera ligada. Mostre a placa...", "blue")

        ultimo = 0
        intervalo = 0.6

        while self.camera_running:
            ret, frame = cap.read()
            if not ret:
                self.update_status("Erro ao capturar.", "red")
                break

            h, w, _ = frame.shape
            roi_w = int(w * 0.40)
            roi_h = int(h * 0.20)

            x1 = (w - roi_w) // 2
            y1 = (h - roi_h) // 2
            x2 = x1 + roi_w
            y2 = y1 + roi_h

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow("Video monitoramento - Precione 'Q' para FECHAR", frame)

            if time.time() - ultimo >= intervalo:
                ultimo = time.time()
                roi = frame[y1:y2, x1:x2]

                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 11, 17, 17)
                gray = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)[1]

                pil_img = Image.fromarray(gray)

                texto = pytesseract.image_to_string(
                    pil_img,
                    config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                ).strip()

                texto = normalize_plate(texto)

                if texto:
                    row = find_plate_db(texto)
                    if row:
                        self.update_status(f"LIBERADO ({texto})", "green")
                    else:
                        self.update_status(f"NÃO RECONHECIDO ({texto})", "red")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.camera_running = False
        self.update_status("Câmera desligada.", "blue")

    def update_status(self, txt, color):
        self.status_label.config(text=f"Status: {txt}", foreground=color)


# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = PlatesApp(root)
    root.mainloop()
