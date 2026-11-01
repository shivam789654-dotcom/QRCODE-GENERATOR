import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
from generator import QRGenerator
from reader import QRReader
from utils import APP_DIR, OUTPUT_DIR, HISTORY_FILE, open_path, open_url

BG = "#101827"
PANEL = "#182438"
PANEL2 = "#202f46"
TEXT = "#edf3fc"
MUTED = "#9aabc2"
ACCENT = "#61d5c4"
ACCENT2 = "#8b9cff"
DANGER = "#ff7b85"

class QRCodeStudio:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("QR Code Studio")
        self.root.geometry("1100x760")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)
        self.generator = QRGenerator()
        self.reader = QRReader()
        self.current_image = None
        self.preview_photo = None
        self.fg_color = "#111827"
        self.bg_color = "#ffffff"
        self.history = self._load_history()
        self._style()
        self._build_ui()
        self._refresh_history()

    def run(self):
        self.root.mainloop()

    def _style(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=PANEL2, foreground=TEXT,
                    padding=(18, 10), font=("Segoe UI", 10, "bold"))
        s.map("TNotebook.Tab", background=[("selected", ACCENT)],
              foreground=[("selected", BG)])
        s.configure("TCombobox", fieldbackground=PANEL2, background=PANEL2,
                    foreground=TEXT, arrowcolor=TEXT)
        s.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground=TEXT, rowheight=28, borderwidth=0)
        s.configure("Treeview.Heading", background=PANEL2, foreground=TEXT,
                    font=("Segoe UI", 9, "bold"))
        s.map("Treeview", background=[("selected", ACCENT)],
              foreground=[("selected", BG)])

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(22, 14))
        tk.Label(header, text="QR CODE STUDIO", bg=BG, fg=TEXT,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Generate • Customize • Read • Manage",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.generator_tab = tk.Frame(self.tabs, bg=BG)
        self.reader_tab = tk.Frame(self.tabs, bg=BG)
        self.history_tab = tk.Frame(self.tabs, bg=BG)
        self.tabs.add(self.generator_tab, text="  GENERATOR  ")
        self.tabs.add(self.reader_tab, text="  READER  ")
        self.tabs.add(self.history_tab, text="  HISTORY  ")
        self._build_generator()
        self._build_reader()
        self._build_history()

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(12, 5))

    def _entry(self, parent, **kwargs):
        return tk.Entry(parent, bg=PANEL2, fg=TEXT, insertbackground=TEXT,
                        relief="flat", font=("Segoe UI", 10), **kwargs)

    def _button(self, parent, text, command, primary=False):
        color = ACCENT if primary else PANEL2
        fg = BG if primary else TEXT
        return tk.Button(parent, text=text, command=command, bg=color, fg=fg,
                         activebackground=ACCENT2, activeforeground=BG,
                         relief="flat", bd=0, padx=13, pady=9,
                         cursor="hand2", font=("Segoe UI", 9, "bold"))

    def _build_generator(self):
        wrap = tk.Frame(self.generator_tab, bg=BG)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)
        left = tk.Frame(wrap, bg=PANEL, padx=20, pady=16)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        right = tk.Frame(wrap, bg=PANEL, padx=20, pady=16, width=350)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(left, text="Create a QR code", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        self._label(left, "CONTENT")
        self.content = tk.Text(left, height=6, bg=PANEL2, fg=TEXT,
                               insertbackground=TEXT, relief="flat",
                               font=("Segoe UI", 10), wrap="word")
        self.content.pack(fill="x")
        self._label(left, "ERROR CORRECTION")
        self.error_var = tk.StringVar(value="M")
        ttk.Combobox(left, textvariable=self.error_var, state="readonly",
                     values=["L", "M", "Q", "H"], width=12).pack(anchor="w")
        self._label(left, "MODULE SIZE")
        self.box_var = tk.IntVar(value=10)
        tk.Scale(left, from_=4, to=20, orient="horizontal", variable=self.box_var,
                 bg=PANEL, fg=TEXT, troughcolor=PANEL2, highlightthickness=0,
                 activebackground=ACCENT, length=250).pack(anchor="w")
        self._label(left, "BORDER (QUIET ZONE)")
        self.border_var = tk.IntVar(value=4)
        tk.Scale(left, from_=2, to=10, orient="horizontal", variable=self.border_var,
                 bg=PANEL, fg=TEXT, troughcolor=PANEL2, highlightthickness=0,
                 activebackground=ACCENT, length=250).pack(anchor="w")
        colors = tk.Frame(left, bg=PANEL)
        colors.pack(fill="x", pady=(14, 0))
        self._button(colors, "Foreground color", lambda: self._choose_color("fg")).pack(side="left")
        self._button(colors, "Background color", lambda: self._choose_color("bg")).pack(side="left", padx=8)
        self._button(left, "GENERATE QR", self._generate, True).pack(anchor="w", pady=20)

        tk.Label(right, text="Live preview", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.preview = tk.Label(right, text="Your QR code will appear here",
                                bg="#ffffff", fg="#64748b", width=34, height=15)
        self.preview.pack(fill="both", expand=True, pady=15)
        self.status = tk.Label(right, text="Ready", bg=PANEL, fg=MUTED,
                               font=("Segoe UI", 9))
        self.status.pack(anchor="w")
        actions = tk.Frame(right, bg=PANEL)
        actions.pack(fill="x", pady=(12, 0))
        self._button(actions, "Save PNG", lambda: self._save("PNG")).pack(side="left")
        self._button(actions, "Save JPG", lambda: self._save("JPEG")).pack(side="left", padx=6)

    def _build_reader(self):
        frame = tk.Frame(self.reader_tab, bg=PANEL, padx=24, pady=22)
        frame.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(frame, text="Read a QR code image", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(frame, text="Choose a PNG, JPG, BMP or other supported image.",
                 bg=PANEL, fg=MUTED).pack(anchor="w", pady=(5, 15))
        self._button(frame, "CHOOSE IMAGE", self._read_image, True).pack(anchor="w")
        self.reader_image = tk.Label(frame, text="No image selected", bg=PANEL2,
                                     fg=MUTED, width=40, height=10)
        self.reader_image.pack(anchor="w", pady=16)
        tk.Label(frame, text="DECODED CONTENT", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.decoded = tk.Text(frame, height=5, bg=PANEL2, fg=TEXT,
                               insertbackground=TEXT, relief="flat",
                               font=("Segoe UI", 10), wrap="word")
        self.decoded.pack(fill="x", pady=(6, 10))
        row = tk.Frame(frame, bg=PANEL)
        row.pack(anchor="w")
        self._button(row, "COPY RESULT", self._copy_result).pack(side="left")
        self._button(row, "OPEN URL", self._open_decoded_url).pack(side="left", padx=8)

    def _build_history(self):
        frame = tk.Frame(self.history_tab, bg=PANEL, padx=18, pady=18)
        frame.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(frame, text="Recent generated QR codes", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
        cols = ("created", "content", "file")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        self.tree.heading("created", text="CREATED")
        self.tree.heading("content", text="CONTENT")
        self.tree.heading("file", text="FILE")
        self.tree.column("created", width=150, stretch=False)
        self.tree.column("content", width=400)
        self.tree.column("file", width=250)
        self.tree.pack(fill="both", expand=True)
        self._button(frame, "OPEN SELECTED FILE", self._open_history_file).pack(anchor="w", pady=12)

    def _choose_color(self, which):
        initial = self.fg_color if which == "fg" else self.bg_color
        result = colorchooser.askcolor(initialcolor=initial, parent=self.root)[1]
        if result:
            if which == "fg":
                self.fg_color = result
            else:
                self.bg_color = result

    def _generate(self):
        data = self.content.get("1.0", "end").strip()
        if not data:
            messagebox.showwarning("Missing content", "Enter text or a URL first.")
            return
        try:
            self.current_image = self.generator.create(
                data, error=self.error_var.get(), box_size=self.box_var.get(),
                border=self.border_var.get(), fill=self.fg_color, back=self.bg_color
            )
            self._show_preview(self.current_image, self.preview, (280, 280))
            self.status.config(text="QR code generated successfully", fg=ACCENT)
            self.history.insert(0, {"created": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "content": data[:120], "file": ""})
            self._save_history()
            self._refresh_history()
        except Exception as exc:
            messagebox.showerror("Generation failed", str(exc))

    def _show_preview(self, image, widget, size):
        preview = image.copy()
        preview.thumbnail(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(preview)
        widget.configure(image=photo, text="")
        widget.image = photo
        if widget == self.preview:
            self.preview_photo = photo

    def _save(self, fmt):
        if self.current_image is None:
            messagebox.showinfo("Nothing to save", "Generate a QR code first.")
            return
        ext = ".png" if fmt == "PNG" else ".jpg"
        path = filedialog.asksaveasfilename(defaultextension=ext,
                    filetypes=[("PNG image", "*.png")] if fmt == "PNG" else [("JPEG image", "*.jpg")])
        if not path:
            return
        try:
            image = self.current_image
            if fmt == "JPEG" and image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            image.save(path, format=fmt, quality=95)
            if self.history:
                self.history[0]["file"] = path
                self._save_history()
                self._refresh_history()
            self.status.config(text=f"Saved: {os.path.basename(path)}", fg=ACCENT)
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))

    def _read_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All files", "*.*")])
        if not path:
            return
        try:
            result = self.reader.decode(path)
            img = Image.open(path).convert("RGB")
            self._show_preview(img, self.reader_image, (250, 170))
            self.decoded.delete("1.0", "end")
            self.decoded.insert("1.0", result)
        except ValueError as exc:
            messagebox.showwarning("No QR code found", str(exc))
        except Exception as exc:
            messagebox.showerror("Read failed", str(exc))

    def _copy_result(self):
        value = self.decoded.get("1.0", "end").strip()
        if value:
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            self.root.update()
            messagebox.showinfo("Copied", "Decoded content copied to clipboard.")

    def _open_decoded_url(self):
        value = self.decoded.get("1.0", "end").strip()
        if value.startswith(("https://", "http://")):
            open_url(value)
        else:
            messagebox.showinfo("Not a URL", "The decoded content does not start with http:// or https://.")

    def _load_history(self):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return []

    def _save_history(self):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history[:50], f, indent=2, ensure_ascii=False)

    def _refresh_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, item in enumerate(self.history[:50]):
            self.tree.insert("", "end", iid=str(index),
                             values=(item.get("created", ""), item.get("content", ""),
                                     item.get("file", "")))

    def _open_history_file(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.history[int(selected[0])]
        path = item.get("file")
        if path and os.path.exists(path):
            open_path(path)
        else:
            messagebox.showinfo("File unavailable", "Save this QR code to create a file first.")
