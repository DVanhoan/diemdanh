from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from typing import Callable, Any

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

class AttendanceView(tk.Frame):
    FALLBACK_BG = "#355C8C"
    BANNER_BG = "#FFFFFF"
    BORDER_COLOR = "#B8B8B8"
    PANEL_BG = "#FFFFFF"
    TITLE_RED = "#D32F2F"

    ACTION_BLUE = "#3498DB"
    BTN_OPEN_BG = "#8A9BAE"
    BTN_CLOSE_BG = "#0A1128"
    AVATAR_SIZE = 160

    def __init__(
        self,
        master: tk.Tk,
        on_start_camera: Callable[..., object],
        on_stop_camera: Callable[..., object],
        on_submit_check: Callable[..., object],
        on_lesson_change: Callable[[str], object],
        on_back: Callable[..., None],
        assets_dir: Path,
    ):
        super().__init__(master, bg=self.FALLBACK_BG)
        self.assets_dir = assets_dir

        self.on_start_camera = on_start_camera
        self.on_stop_camera = on_stop_camera
        self.on_submit_check = on_submit_check
        self.on_lesson_change = on_lesson_change
        self.on_back = on_back

        self._bg_path = self._resolve_background_path()
        self._bg_original = None
        self._bg_photo = None
        self._bg_image_id = None
        self._resize_job = None
        self._last_size = None

        self.class_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Vào")
        self.lesson_combo: ttk.Combobox | None = None

        self.avatar_box: tk.Label | None = None
        self.avatar_photo_var: Any | None = None
        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.time_var = tk.StringVar()

        self.subject_var = tk.StringVar()
        self.lesson_info_var = tk.StringVar()
        self.session_time_var = tk.StringVar()

        self._configure_styles()

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self.FALLBACK_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._build_top_widgets()
        self._build_content()
        self._start_clock()


    def _resolve_background_path(self):
        candidates = [
            self.assets_dir / "bg.jpg",
            self.assets_dir / "bg.png",
            self.assets_dir / "attendance_bg.png",
        ]
        for p in candidates:
            if p.exists():
                return p
        return None

    def _configure_styles(self):
        style = ttk.Style()
        style.configure("Attend.TCombobox", font=("times new roman", 10))


    def _build_top_widgets(self):
        font_clock = ("times new roman", 11, "bold")
        font_banner = ("times new roman", 14, "bold")

        # Clock
        clock_box = tk.Frame(self.canvas, bg=self.BANNER_BG,
                             highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        clock_box.pack_propagate(False)
        clock_box.configure(width=120, height=44)

        self.time_label = tk.Label(clock_box, text="00:00:00 AM",
                                   bg=self.BANNER_BG, fg="#1F1F1F", font=font_clock)
        self.time_label.pack(fill="x")

        self.date_label = tk.Label(clock_box, text="01-01-2000",
                                   bg=self.BANNER_BG, fg="#1F1F1F", font=font_clock)
        self.date_label.pack(fill="x")

        self._clock_win = self.canvas.create_window(0, 0, window=clock_box, anchor="nw")

        # Title
        banner = tk.Frame(self.canvas, bg=self.BANNER_BG,
                          highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        banner.pack_propagate(False)
        banner.configure(width=520, height=34)

        tk.Label(
            banner,
            text="Hệ thống điểm danh khuôn mặt",
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=font_banner,
        ).pack(expand=True)

        self._banner_win = self.canvas.create_window(0, 0, window=banner, anchor="n")

        # Back button
        back_box = tk.Frame(self.canvas, bg=self.BANNER_BG,
                            highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        back_box.pack_propagate(False)
        back_box.configure(width=110, height=34)

        tk.Button(
            back_box,
            text="Quay lại",
            command=self.on_back,
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            bd=0,
            cursor="hand2",
            font=("times new roman", 11, "bold"),
        ).pack(fill="both", expand=True)

        self._back_win = self.canvas.create_window(0, 0, window=back_box, anchor="ne")


    def _build_content(self):
        outer = tk.Frame(self.canvas, bg=self.PANEL_BG,
                         highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        self._content_win = self.canvas.create_window(0, 0, window=outer, anchor="nw")

        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=6)
        outer.grid_columnconfigure(1, weight=4)

        # LEFT
        left = tk.Frame(outer, bg=self.PANEL_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self._build_left(left)

        # RIGHT
        right = tk.Frame(outer, bg=self.PANEL_BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        self._build_right(right)


    def _build_left(self, parent):
        # Dùng LabelFrame để tạo viền giống thiết kế
        left_group = tk.LabelFrame(parent, text="Màn hình nhận diện", bg=self.PANEL_BG, font=("times new roman", 11, "bold"))
        left_group.pack(fill="both", expand=True)

        # Row 1: Comboboxes
        top = tk.Frame(left_group, bg=self.PANEL_BG)
        top.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(top, text="Chọn Môn/ID buổi học:", bg=self.PANEL_BG, font=("times new roman", 9, "bold")).pack(side="left")
        self.lesson_combo = ttk.Combobox(
            top,
            textvariable=self.class_var,
            style="Attend.TCombobox",
            width=18,
            state="readonly",
        )
        self.lesson_combo.pack(side="left", padx=(5, 20))
        self.lesson_combo.bind("<<ComboboxSelected>>", self._on_lesson_selected)

        tk.Label(top, text="Chọn loại Điểm Danh:", bg=self.PANEL_BG, font=("times new roman", 9, "bold")).pack(side="left")
        ttk.Combobox(top, textvariable=self.type_var, values=["Vào", "Ra"], style="Attend.TCombobox", width=8).pack(side="left", padx=5)

        # Camera Container
        self.camera_container = tk.Frame(left_group, bg="#EAEAEA", highlightthickness=1, relief="solid", bd=1)
        self.camera_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.camera_container.pack_propagate(False)

        self.camera_display = tk.Label(self.camera_container, text="[Camera streaming]", bg="#EAEAEA")
        self.camera_display.pack(fill="both", expand=True)

        # Line + Status Label
        ttk.Separator(left_group, orient="horizontal").pack(fill="x", padx=10, pady=(5, 0))
        tk.Label(
            left_group, text="Bạn không có môn học nào cần điểm danh hôm nay",
            fg="red", bg=self.PANEL_BG, font=("times new roman", 9, "bold")
        ).pack(anchor="w", padx=10, pady=(2, 5))

        # Row 3: Buttons
        btns = tk.Frame(left_group, bg=self.PANEL_BG)
        btns.pack(fill="x", padx=10, pady=(5, 15))

        tk.Button(
            btns, text="Mở Camera", command=self.on_start_camera,
            bg=self.BTN_OPEN_BG, fg="white", font=("times new roman", 11, "bold"), relief="flat"
        ).pack(side="left", expand=True, fill="x", padx=(0, 10), ipady=6)

        tk.Button(
            btns, text="Đóng Camera", command=self.on_stop_camera,
            bg=self.BTN_CLOSE_BG, fg="white", font=("times new roman", 11, "bold"), relief="flat"
        ).pack(side="left", expand=True, fill="x", padx=(10, 0), ipady=6)


    def _build_right(self, parent):
        top_group = tk.LabelFrame(parent, text="Điểm danh thành công", bg=self.PANEL_BG, font=("times new roman", 11, "bold"))
        top_group.pack(fill="both", expand=True, pady=(0, 10))

        avatar_wrap = tk.Frame(top_group, bg=self.PANEL_BG, width=self.AVATAR_SIZE, height=self.AVATAR_SIZE)
        avatar_wrap.pack(pady=15)
        avatar_wrap.pack_propagate(False)

        self.avatar_box = tk.Label(
            avatar_wrap,
            text="?",
            bg="#000000",
            fg="white",
            font=("times new roman", 44, "bold"),
            relief="solid",
            bd=1,
        )
        self.avatar_box.pack(fill="both", expand=True)

        def row(container, txt, var):
            frame = tk.Frame(container, bg=self.PANEL_BG)
            frame.pack(fill="x", padx=15, pady=6)
            tk.Label(frame, text=txt, bg=self.PANEL_BG, font=("times new roman", 10, "bold")).pack(side="left")
            tk.Label(frame, textvariable=var, bg=self.PANEL_BG, fg="#333", font=("times new roman", 10)).pack(side="left", padx=10)

        row(top_group, "ID Học sinh:", self.student_id_var)
        row(top_group, "Tên Học sinh:", self.student_name_var)
        row(top_group, "Thời gian:", self.time_var)

        bottom_group = tk.LabelFrame(parent, text="Thông tin buổi học", bg=self.PANEL_BG, font=("times new roman", 11, "bold"))
        bottom_group.pack(fill="x", pady=(0, 10))

        row(bottom_group, "Lớp:", self.subject_var)
        row(bottom_group, "Tên môn học/ID buổi học:", self.lesson_info_var)
        row(bottom_group, "Thời gian:", self.session_time_var)

        tk.Button(
            parent,
            text="Xác nhận Điểm danh",
            command=self._submit,
            bg=self.ACTION_BLUE,
            fg="white",
            font=("times new roman", 11, "bold"),
            relief="flat",
            pady=8
        ).pack(fill="x")



    def _submit(self):
        ok, msg = self.on_submit_check(
            self.class_var.get(),
            self.type_var.get(),
        )
        if ok:
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showerror("Lỗi", msg)


    def _on_canvas_configure(self, event):
        self._last_size = (event.width, event.height)
        if self._resize_job:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(30, self._redraw)

    def _redraw(self):
        if not self._last_size:
            return
        w, h = self._last_size
        self._draw_background(w, h)
        self._layout_widgets(w, h)

    def _start_clock(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%I:%M:%S %p"))
        self.date_label.config(text=now.strftime("%d-%m-%Y"))
        self.after(1000, self._start_clock)

    def _draw_background(self, w, h):
        if not self._bg_path:
            return

        if Image:
            if not self._bg_original:
                self._bg_original = Image.open(self._bg_path).convert("RGB")
            resized = self._bg_original.resize((w, h))
            self._bg_photo = ImageTk.PhotoImage(resized)
        else:
            self._bg_photo = tk.PhotoImage(file=str(self._bg_path))

        if not self._bg_image_id:
            self._bg_image_id = self.canvas.create_image(0, 0, image=self._bg_photo, anchor="nw")
        else:
            self.canvas.itemconfigure(self._bg_image_id, image=self._bg_photo)
        self.canvas.tag_lower(self._bg_image_id)

    def _layout_widgets(self, w, h):
        margin = 15
        top_h = 75

        self.canvas.coords(self._clock_win, margin, margin)
        self.canvas.coords(self._banner_win, w // 2, margin)
        self.canvas.coords(self._back_win, w - margin, margin)

        content_x = margin
        content_y = top_h
        content_w = w - margin * 2
        content_h = h - top_h - margin

        self.canvas.coords(self._content_win, content_x, content_y)
        self.canvas.itemconfigure(self._content_win, width=content_w, height=content_h)

    def set_lesson_options(self, options: list[str]) -> None:
        if self.lesson_combo is None:
            return
        self.lesson_combo["values"] = options
        if options:
            self.class_var.set(options[0])
            self.lesson_info_var.set(options[0])
        else:
            self.class_var.set("")
            self.lesson_info_var.set("")

    def _on_lesson_selected(self, _: object = None) -> None:
        self.on_lesson_change(self.class_var.get())

    def set_avatar_image(self, image_path: Path | None) -> None:
        if self.avatar_box is None:
            return
        if image_path is None or not image_path.exists() or Image is None or ImageTk is None:
            self.clear_avatar()
            return

        try:
            avatar = Image.open(image_path).convert("RGB").resize((self.AVATAR_SIZE, self.AVATAR_SIZE))
            self.avatar_photo_var = ImageTk.PhotoImage(avatar)
            self.avatar_box.configure(text="", image=self.avatar_photo_var)
        except Exception:
            self.clear_avatar()

    def clear_avatar(self) -> None:
        if self.avatar_box is None:
            return
        self.avatar_photo_var = None
        self.avatar_box.configure(image="", text="?")
