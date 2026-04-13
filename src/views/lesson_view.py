from __future__ import annotations

from datetime import datetime
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from typing import Callable

try:
    from PIL import Image, ImageTk  # type: ignore
except Exception:  # noqa: BLE001
    Image = None
    ImageTk = None

from src.models.lesson_model import LessonModel

class lessonView(tk.Frame):     
    FALLBACK_BG = "#355C8C"
    BANNER_BG = "#FFFFFF"
    BORDER_COLOR = "#B8B8B8"
    PANEL_BG = "#FFFFFF"
    TITLE_RED = "#C62828"

    ACTION_BLUE = "#3498DB"
    ACTION_BLUE_ACTIVE = "#2E86C1"
    ACTION_YELLOW = "#F2C94C"
    ACTION_YELLOW_ACTIVE = "#E0B93C"

    def __init__( 
        self,
        master: tk.Tk,
        on_save: Callable[..., object],
        on_update: Callable[..., object],
        on_delete: Callable[..., object],
        on_refresh: Callable[..., object],
        on_search: Callable[..., object],
        on_back: Callable[[], None],
        assets_dir: Path,
    ) -> None: 
        super().__init__(master, bg=self.FALLBACK_BG)
        self.assets_dir = assets_dir
        self.on_save = on_save
        self.on_update = on_update
        self.on_delete = on_delete
        self.on_refresh = on_refresh
        self.on_search = on_search
        self.on_back = on_back

        self.lesson_id_var      = tk.StringVar()
        self.start_time_var     = tk.StringVar()
        self.end_time_var       = tk.StringVar()
        self.date_var           = tk.StringVar(value="26/04/2024")
        self.teacher_id_var     = tk.StringVar()
        self.teacher_name_var   = tk.StringVar()
        self.subject_id_var     = tk.StringVar()
        self.subject_name_var   = tk.StringVar()

        self._bg_path = self._resolve_background_path()
        self._bg_original = None
        self._bg_photo = None
        self._bg_image_id: int | None = None
        self._resize_job: str | None = None
        self._last_size: tuple[int, int] | None = None
            
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self.FALLBACK_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self._build_top_widgets()
        self._build_content()
        self._start_clock()

    
    def _resolve_background_path(self) -> Path | None:
        candidates = [
            self.assets_dir / "bg.jpg",
            self.assets_dir / "bg.png",
            self.assets_dir / "teacher_bg.png",
            self.assets_dir / "teacher_bg.jpg",
        ]
        for path in candidates:
            if path.exists():
                return path
        return None 

    def _build_top_widgets(self) -> None:
        font_banner = ("times new roman", 14, "bold")
        font_clock = ("times new roman", 11, "bold")

        clock = tk.Frame(
            self.canvas,
            bg=self.BANNER_BG,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        clock.pack_propagate(False)
        clock.configure(width=120, height=44)

        self.time_label = tk.Label(clock, text="00:00:00 AM", bg=self.BANNER_BG, fg="#1F1F1F", font=font_clock)
        self.time_label.pack(fill="x")
        self.date_label = tk.Label(clock, text="01-01-2000", bg=self.BANNER_BG, fg="#1F1F1F", font=font_clock)
        self.date_label.pack(fill="x")
        self._clock_win = self.canvas.create_window(0, 0, window=clock, anchor="nw")

        banner = tk.Frame(
            self.canvas,
            bg=self.BANNER_BG,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        banner.pack_propagate(False)
        banner.configure(width=520, height=34)
        tk.Label(
            banner,
            text="Quản lý thông tin lịch học",
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=font_banner,
        ).pack(expand=True)
        self._banner_win = self.canvas.create_window(0, 0, window=banner, anchor="n")

        back_box = tk.Frame(
            self.canvas,
            bg=self.BANNER_BG,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        back_box.pack_propagate(False)
        back_box.configure(width=110, height=34)
        tk.Button(
            back_box,
            text="Quay lại",
            command=self.on_back,
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=("times new roman", 11, "bold"),
            bd=0,
            cursor="hand2",
        ).pack(fill="both", expand=True)
        self._back_win = self.canvas.create_window(0, 0, window=back_box, anchor="ne")

    
    # ---------- background & layout ----------
    def _on_canvas_configure(self, event: tk.Event) -> None:  # type: ignore[name-defined]
        self._last_size = (int(event.width), int(event.height))
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(30, self._redraw)

    def _redraw(self) -> None:
        if not self._last_size:
            return
        width, height = self._last_size
        self._draw_background(width, height)
        self._layout_widgets(width, height)

    def _start_clock(self) -> None:
        now = datetime.now()
        self.time_label.config(text=now.strftime("%I:%M:%S %p"))
        self.date_label.config(text=now.strftime("%d-%m-%Y"))
        self.after(1000, self._start_clock)

    def _draw_background(self, width: int, height: int) -> None:
        if self._bg_path is None:
            self.canvas.configure(bg=self.FALLBACK_BG)
            if self._bg_image_id is not None:
                self.canvas.delete(self._bg_image_id)
                self._bg_image_id = None
            return

        if Image is not None and ImageTk is not None:
            if self._bg_original is None:
                try:
                    self._bg_original = Image.open(self._bg_path).convert("RGB")
                except Exception:  # noqa: BLE001
                    self._bg_original = None
            if self._bg_original is not None:
                resized = self._bg_original.resize((width, height), Image.LANCZOS)
                self._bg_photo = ImageTk.PhotoImage(resized)
        else:
            try:
                self._bg_photo = tk.PhotoImage(file=str(self._bg_path))
            except tk.TclError:
                self._bg_photo = None

        if self._bg_photo is None:
            self.canvas.configure(bg=self.FALLBACK_BG)
            return

        if self._bg_image_id is None:
            self._bg_image_id = self.canvas.create_image(0, 0, image=self._bg_photo, anchor="nw")
        else:
            self.canvas.itemconfigure(self._bg_image_id, image=self._bg_photo)

        self.canvas.tag_lower(self._bg_image_id)

    def _layout_widgets(self, width: int, height: int) -> None:
        margin = 12
        top_reserved = 70

        self.canvas.coords(self._clock_win, margin, margin)
        self.canvas.coords(self._banner_win, width / 2, margin)
        self.canvas.coords(self._back_win, width - margin, margin)

        # Chỉ layout content nếu đã được build
        if hasattr(self, "_content_win"):
            content_x = margin
            content_y = top_reserved
            content_w = max(0, width - margin * 2)
            content_h = max(0, height - top_reserved - margin)
            self.canvas.coords(self._content_win, content_x, content_y)
            self.canvas.itemconfigure(self._content_win, width=content_w, height=content_h)

    
    def _build_content(self) -> None:
        outer = tk.Frame(
            self.canvas,
            bg=self.PANEL_BG,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        self._content_win = self.canvas.create_window(0, 0, window=outer, anchor="nw")

        left = tk.Frame(outer, bg=self.PANEL_BG)
        sep = tk.Frame(outer, bg="#CFCFCF", width=1)
        right = tk.Frame(outer, bg=self.PANEL_BG)

        outer.grid_columnconfigure(0, weight=1, uniform="columns")
        outer.grid_columnconfigure(1, weight=0)
        outer.grid_columnconfigure(2, weight=2, uniform="columns")
        outer.grid_rowconfigure(0, weight=1)

        left.grid(row=0, column=0, sticky="nsew", padx=(12, 10), pady=12)
        sep.grid(row=0, column=1, sticky="ns", pady=12)
        right.grid(row=0, column=2, sticky="nsew", padx=(10, 12), pady=12)

        self._build_left_section(left)
        self._build_right_section(right)


    def _build_left_section(self, parent: tk.Frame) -> None:
        font_label = ("times new roman", 10)
        font_label_bold = ("times new roman", 10, "bold")
        font_title = ("times new roman", 13, "bold")

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=0)
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_rowconfigure(3, weight=0)

        # Tiêu đề căn giữa, màu đỏ, có gạch dưới nhẹ
        title_frame = tk.Frame(parent, bg=self.PANEL_BG)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(6, 2))
        tk.Label(
            title_frame,
            text="Thông tin giáo viên",
            bg=self.PANEL_BG,
            fg=self.TITLE_RED,
            font=font_title,
            anchor="center",
        ).pack(fill="x")
        tk.Frame(title_frame, bg="#E0E0E0", height=1).pack(fill="x", pady=(4, 0))

        # Form fields
        form = tk.Frame(parent, bg=self.PANEL_BG)
        form.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 0))
        form.grid_columnconfigure(0, weight=0, minsize=110)
        form.grid_columnconfigure(1, weight=1)

        def add_row(r: int, label: str, var: tk.StringVar, *, readonly: bool = False) -> tk.Entry:
            tk.Label(
                form, text=label, bg=self.PANEL_BG,
                font=font_label_bold, anchor="w"
            ).grid(row=r, column=0, sticky="w", pady=5, padx=(4, 0))
            ent = tk.Entry(
                form, textvariable=var, font=font_label,
                bd=1, relief="solid", bg="#FFFFFF"
            )
            if readonly:
                ent.configure(state="readonly", readonlybackground="#F5F5F5")
            ent.grid(row=r, column=1, sticky="ew", padx=(6, 4), pady=5, ipady=4)
            return ent

        add_row(0, "ID Buổi học:",   self.lesson_id_var,   readonly=True)
        add_row(1, "Giờ bắt đầu:",  self.start_time_var)
        add_row(2, "Giờ kết thúc:", self.end_time_var)

        # Hàng Ngày có mũi tên dropdown giả lập bằng Combobox
        tk.Label(
            form, text="Ngày:", bg=self.PANEL_BG,
            font=font_label_bold, anchor="w"
        ).grid(row=3, column=0, sticky="w", pady=5, padx=(4, 0))

        style = ttk.Style()
        style.configure("Lesson.TCombobox", font=("times new roman", 10))
        date_cb = ttk.Combobox(
            form, textvariable=self.date_var,
            font=font_label, style="Lesson.TCombobox",
            state="normal",
        )
        date_cb.grid(row=3, column=1, sticky="ew", padx=(6, 4), pady=5, ipady=3)

        add_row(4, "ID giáo viên:",  self.teacher_id_var)
        add_row(5, "Tên giáo viên:", self.teacher_name_var)
        add_row(6, "ID Môn học:",    self.subject_id_var)
        add_row(7, "Tên Môn học:",   self.subject_name_var)

        # Spacer
        tk.Frame(parent, bg=self.PANEL_BG).grid(row=2, column=0, sticky="nsew")

        # Buttons
        btn_frame = tk.Frame(parent, bg=self.PANEL_BG)
        btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(6, 10))
        btn_frame.grid_columnconfigure(0, weight=1, uniform="b")
        btn_frame.grid_columnconfigure(1, weight=1, uniform="b")

        btn_cfg = dict(
            bg=self.ACTION_BLUE,
            activebackground=self.ACTION_BLUE_ACTIVE,
            fg="white",
            activeforeground="white",
            font=font_label_bold,
            bd=0,
            relief="flat",
            cursor="hand2",
            pady=7,
        )

        tk.Button(btn_frame, text="Thêm mới", command=self._handle_save,    **btn_cfg).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=4)
        tk.Button(btn_frame, text="Xóa",      command=self._handle_delete,  **btn_cfg).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=4)
        tk.Button(btn_frame, text="Cập nhật", command=self._handle_update,  **btn_cfg).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=4)
        tk.Button(btn_frame, text="Làm mới",  command=self._handle_refresh, **btn_cfg).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=4)

    def _build_right_section(self, parent: tk.Frame) -> None:
        font_label = ("times new roman", 10)
        font_label_bold = ("times new roman", 10, "bold")

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)

        # ── Thanh tìm kiếm ──
        search = tk.Frame(parent, bg=self.PANEL_BG)
        search.grid(row=0, column=0, sticky="ew", padx=4, pady=(6, 4))
        search.grid_columnconfigure(1, weight=0)
        search.grid_columnconfigure(2, weight=1)
        search.grid_columnconfigure(3, weight=0)
        search.grid_columnconfigure(4, weight=0)

        tk.Label(search, text="Tìm kiếm theo :", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=0, column=0, sticky="w", padx=(4, 6)
        )

        self.search_field_var = tk.StringVar(value="ID Buổi học")
        field_cb = ttk.Combobox(
            search,
            textvariable=self.search_field_var,
            values=["ID Buổi học", "Giờ bắt đầu", "Giờ kết thúc", "Ngày", "ID giáo viên", "ID Môn học"],
            font=font_label,
            state="readonly",
            width=14,
        )
        field_cb.grid(row=0, column=1, sticky="w", padx=(0, 6), ipady=3)

        self.search_var = tk.StringVar()
        tk.Entry(search, textvariable=self.search_var, font=font_label, bd=1, relief="solid").grid(
            row=0, column=2, sticky="ew", padx=(0, 8), ipady=4
        )

        btn_cfg = dict(
            bg=self.ACTION_BLUE,
            activebackground=self.ACTION_BLUE_ACTIVE,
            fg="white", activeforeground="white",
            font=font_label_bold,
            bd=0, relief="flat",
            cursor="hand2",
            padx=14, pady=5,
        )
        tk.Button(search, text="Tìm kiếm", command=self._handle_search, **btn_cfg).grid(
            row=0, column=3, padx=(0, 6)
        )
        tk.Button(search, text="Xem tất cả", command=self._handle_all, **btn_cfg).grid(
            row=0, column=4, padx=(0, 4)
        )

        # ── Bảng dữ liệu ──
        table = tk.Frame(parent, bg=self.PANEL_BG)
        table.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 6))
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(0, weight=1)

        cols = ("lesson_id", "start_time", "end_time", "date", "teacher_id", "subject_id")
        style = ttk.Style()
        style.configure("Lesson.Treeview", font=("times new roman", 10), rowheight=22)
        style.configure("Lesson.Treeview.Heading", font=("times new roman", 10, "bold"))

        self.lesson_tree = ttk.Treeview(
            table, columns=cols, show="headings",
            height=18, style="Lesson.Treeview"
        )

        headings = {
            "lesson_id":   ("ID Buổi học", 80),
            "start_time":  ("Giờ bắt đầu", 100),
            "end_time":    ("Giờ kết thúc", 100),
            "date":        ("Ngày",         100),
            "teacher_id":  ("ID giáo viên", 100),
            "subject_id":  ("ID Môn học",   100),
        }
        for col, (text, width) in headings.items():
            self.lesson_tree.heading(col, text=text)
            self.lesson_tree.column(col, width=width, anchor="center", stretch=True)

        y_scroll = ttk.Scrollbar(table, orient="vertical", command=self.lesson_tree.yview)
        self.lesson_tree.configure(yscrollcommand=y_scroll.set)
        self.lesson_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")

        self.lesson_tree.bind("<<TreeviewSelect>>", self._on_select_row)


    def _handle_search(self) -> None:
        pass  # làm sau

    def _handle_all(self) -> None:
        pass  # làm sau

    def _on_select_row(self, _: object) -> None:
        sel = self.lesson_tree.selection()
        if not sel:
            return
        values = self.lesson_tree.item(sel[0], "values")
        if len(values) >= 6:
            self.lesson_id_var.set(values[0])
            self.start_time_var.set(values[1])
            self.end_time_var.set(values[2])
            self.date_var.set(values[3])
            self.teacher_id_var.set(values[4])
            self.subject_id_var.set(values[5])

    def set_table_rows(self, lessons: list[LessonModel]) -> None:
        self.lesson_tree.delete(*self.lesson_tree.get_children())
        for l in lessons:
            self.lesson_tree.insert("", "end", values=(
                l.lesson_id, l.start_time, l.end_time,
                l.date, l.teacher_id, l.subject_id
            ))
    def _handle_save(self) -> None: 
        pass
    def _handle_delete(self) -> None: 
        pass
    def _handle_update(self) -> None: 
        pass
    def _handle_refresh(self) -> None: 
        pass


