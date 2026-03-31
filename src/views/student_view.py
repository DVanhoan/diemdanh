from __future__ import annotations

from datetime import datetime
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from typing import Callable


try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

try:
    from tkcalendar import DateEntry
except Exception:
    DateEntry = None

from src.controllers.class_controller import ClassController


class StudentView(tk.Frame):

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
        on_capture: Callable[..., object],
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
        self.on_capture = on_capture
        self.on_back = on_back

        self._bg_path = self._resolve_background_path()
        self._bg_original = None
        self._bg_photo = None
        self._bg_image_id: int | None = None
        self._resize_job: str | None = None
        self._last_size: tuple[int, int] | None = None

        self.student_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="Nam")
        self.dob_var = tk.StringVar()
        self.id_card_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()

        self.year_var = tk.StringVar(value="2023-2024")
        self.semester_var = tk.StringVar(value="Học kì I")
        self.photo_var = tk.StringVar(value="Không ảnh")

        self.search_type_var = tk.StringVar(value="ID Học sinh")
        self.search_var = tk.StringVar()

        self.class_search_var = tk.StringVar()
        self.class_id_var = tk.StringVar()
        self.class_name_var = tk.StringVar()

        self._configure_styles()

        self._class_controller = ClassController()

        self._class_label_to_id: dict[str, str] = {}

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self.FALLBACK_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._build_top_widgets()
        self._build_content()
        self._start_clock()

        self._students_cache: list[object] = []


    def _resolve_background_path(self) -> Path | None:
        candidates = [
            self.assets_dir / "bg.jpg",
            self.assets_dir / "bg.png",
            self.assets_dir / "student_bg.png",
            self.assets_dir / "student_bg.jpg",
        ]
        for path in candidates:
            if path.exists():
                return path
        return None

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.configure(
            "Student.Treeview",
            font=("times new roman", 10),
            rowheight=24,
        )
        style.configure(
            "Student.Treeview.Heading",
            font=("times new roman", 10, "bold"),
        )
        style.configure("Student.TCombobox", font=("times new roman", 10))


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

        content_x = margin
        content_y = top_reserved
        content_w = max(0, width - margin * 2)
        content_h = max(0, height - top_reserved - margin)
        self.canvas.coords(self._content_win, content_x, content_y)
        self.canvas.itemconfigure(self._content_win, width=content_w, height=content_h)


    def _build_top_widgets(self) -> None:
        clock = tk.Frame(
            self.canvas,
            bg=self.BANNER_BG,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        clock.pack_propagate(False)
        clock.configure(width=120, height=44)

        self.time_label = tk.Label(
            clock,
            text="00:00:00 AM",
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=("times new roman", 11, "bold"),
        )
        self.time_label.pack(fill="x")
        self.date_label = tk.Label(
            clock,
            text="01-01-2000",
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=("times new roman", 10, "bold"),
        )
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
            text="Quản lý thông tin Học sinh",
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=("times new roman", 14, "bold"),
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
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)  # title
        parent.grid_rowconfigure(1, weight=0)  # course
        parent.grid_rowconfigure(2, weight=1)  # info (expand)
        parent.grid_rowconfigure(3, weight=0)  # buttons (bottom)

        # Prefer times new roman for consistent font.
        font_label = ("times new roman", 10)
        font_label_bold = ("times new roman", 10, "bold")
        font_title = ("times new roman", 12, "bold")

        tk.Label(
            parent,
            text="Thông tin Học sinh",
            bg=self.PANEL_BG,
            fg=self.TITLE_RED,
            font=font_title,
        ).grid(row=0, column=0, sticky="ew", pady=(0, 10))

        course = tk.LabelFrame(
            parent,
            text="Thông tin khóa học",
            bg=self.PANEL_BG,
            fg="#1F1F1F",
            font=font_label_bold,
            padx=10,
            pady=10,
        )
        course.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        tk.Label(course, text="Năm học", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=8
        )
        ttk.Combobox(
            course,
            textvariable=self.year_var,
            values=["2021-2022", "2022-2023", "2023-2024"],
            state="readonly",
            width=18,
            style="Student.TCombobox",
        ).grid(row=0, column=1, sticky="ew", pady=8, ipady=3)

        tk.Label(course, text="Học kì", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=0, column=2, sticky="w", padx=(16, 8), pady=8
        )
        ttk.Combobox(
            course,
            textvariable=self.semester_var,
            values=["Học kì I", "Học kì II"],
            state="readonly",
            width=18,
            style="Student.TCombobox",
        ).grid(row=0, column=3, sticky="ew", pady=8, ipady=3)

        course.grid_columnconfigure(1, weight=1)
        course.grid_columnconfigure(3, weight=1)

        info = tk.LabelFrame(
            parent,
            text="Thông tin lớp học",
            bg=self.PANEL_BG,
            fg="#1F1F1F",
            font=font_label_bold,
            padx=10,
            pady=10,
        )
        info.grid(row=2, column=0, sticky="nsew")

        info.grid_columnconfigure(0, weight=0)
        info.grid_columnconfigure(1, weight=1)
        info.grid_columnconfigure(2, weight=0)
        info.grid_columnconfigure(3, weight=1)

        def _mk_entry(row: int, col: int, var: tk.Variable, *, padx: tuple[int, int]) -> tk.Entry:
            ent = tk.Entry(info, textvariable=var, font=font_label, bd=1, relief="solid")
            ent.grid(row=row, column=col, sticky="ew", pady=8, padx=padx, ipady=3)
            return ent

        def _row(r: int, l1: str, v1: tk.Variable, l2: str, v2: tk.Variable) -> None:
            tk.Label(info, text=l1, bg=self.PANEL_BG, font=font_label_bold).grid(
                row=r, column=0, sticky="w", pady=8
            )
            _mk_entry(r, 1, v1, padx=(8, 18))
            tk.Label(info, text=l2, bg=self.PANEL_BG, font=font_label_bold).grid(
                row=r, column=2, sticky="w", pady=8
            )
            _mk_entry(r, 3, v2, padx=(8, 0))

        _row(0, "ID Học sinh:", self.student_id_var, "Tên Học sinh:", self.name_var)
        # Row: Class as Combobox (populated from DB) + ID card
        tk.Label(info, text="Lớp học:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=1, column=0, sticky="w", pady=8
        )
        class_labels = self._refresh_class_combobox_values()
        self.class_cb = ttk.Combobox(
            info,
            state="readonly" if class_labels else "normal",
            style="Student.TCombobox",
        )
        self.class_cb.configure(values=tuple(class_labels))
        self.class_cb.grid(row=1, column=1, sticky="ew", pady=8, padx=(8, 18), ipady=3)

        def _on_class_selected(_: object) -> None:
            label = self.class_cb.get().strip()
            class_id = self._class_label_to_id.get(label)
            if class_id is not None:
                self.class_var.set(class_id)

        self.class_cb.bind("<<ComboboxSelected>>", _on_class_selected)

        tk.Label(info, text="CMND:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=1, column=2, sticky="w", pady=8
        )
        _mk_entry(1, 3, self.id_card_var, padx=(8, 0))

        tk.Label(info, text="Giới tính:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=2, column=0, sticky="w", pady=8
        )
        ttk.Combobox(
            info,
            textvariable=self.gender_var,
            values=["Nam", "Nữ", "Khác"],
            state="readonly",
            style="Student.TCombobox",
        ).grid(row=2, column=1, sticky="ew", pady=8, padx=(8, 18), ipady=3)

        tk.Label(info, text="Ngày sinh:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=2, column=2, sticky="w", pady=8
        )
        if DateEntry is not None:
            dob_widget = DateEntry(
                info,
                textvariable=self.dob_var,
                date_pattern="dd-mm-yyyy",
                font=font_label,
                background=self.ACTION_BLUE,
                foreground="white",
                borderwidth=1,
            )
            dob_widget.grid(row=2, column=3, sticky="ew", pady=8, padx=(8, 0), ipady=3)
        else:
            _mk_entry(2, 3, self.dob_var, padx=(8, 0))

        _row(3, "Email:", self.email_var, "SĐT:", self.phone_var)

        tk.Label(info, text="Địa chỉ:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=4, column=0, sticky="w", pady=8
        )
        addr = tk.Entry(info, textvariable=self.address_var, font=font_label, bd=1, relief="solid")
        addr.grid(row=4, column=1, columnspan=3, sticky="ew", pady=8, padx=(8, 0), ipady=3)

        # Align the "Ảnh" radio row with existing label/value columns.
        tk.Label(info, text="Ảnh:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=5, column=0, sticky="w", pady=8
        )
        photo_wrap = tk.Frame(info, bg=self.PANEL_BG)
        photo_wrap.grid(row=5, column=1, columnspan=3, sticky="w", pady=8, padx=(8, 0))
        tk.Radiobutton(
            photo_wrap,
            text="Có ảnh",
            value="Có ảnh",
            variable=self.photo_var,
            bg=self.PANEL_BG,
            activebackground=self.PANEL_BG,
            fg="#1F1F1F",
            selectcolor=self.PANEL_BG,
            font=font_label,
            bd=0,
            highlightthickness=0,
        ).grid(row=0, column=0, sticky="w", padx=(0, 14))
        tk.Radiobutton(
            photo_wrap,
            text="Không ảnh",
            value="Không ảnh",
            variable=self.photo_var,
            bg=self.PANEL_BG,
            activebackground=self.PANEL_BG,
            fg="#1F1F1F",
            selectcolor=self.PANEL_BG,
            font=font_label,
            bd=0,
            highlightthickness=0,
        ).grid(row=0, column=1, sticky="w")

        # Buttons pinned to bottom.
        buttons = tk.Frame(parent, bg=self.PANEL_BG)
        buttons.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_rowconfigure(0, weight=0)
        buttons.grid_rowconfigure(1, weight=0)

        action_row = tk.Frame(buttons, bg=self.PANEL_BG)
        action_row.grid(row=0, column=0, sticky="ew")
        for c in range(4):
            action_row.grid_columnconfigure(c, weight=1, uniform="student_action")

        btn_cfg = dict(
            bg=self.ACTION_BLUE,
            activebackground=self.ACTION_BLUE_ACTIVE,
            fg="white",
            activeforeground="white",
            font=font_label_bold,
            bd=1,
            relief="solid",
            cursor="hand2",
        )

        btn_cfg_action = dict(btn_cfg, pady=6)

        tk.Button(action_row, text="Lưu", command=self._handle_save, **btn_cfg_action).grid(
            row=0, column=0, sticky="ew", padx=4, pady=4
        )
        tk.Button(action_row, text="Sửa", command=self._handle_update, **btn_cfg_action).grid(
            row=0, column=1, sticky="ew", padx=4, pady=4
        )
        tk.Button(action_row, text="Xóa", command=self._handle_delete, **btn_cfg_action).grid(
            row=0, column=2, sticky="ew", padx=4, pady=4
        )
        tk.Button(action_row, text="Làm mới", command=self._handle_refresh, **btn_cfg_action).grid(
            row=0, column=3, sticky="ew", padx=4, pady=4
        )

        bottom_row = tk.Frame(buttons, bg=self.PANEL_BG)
        bottom_row.grid(row=1, column=0, sticky="ew")
        for c in range(2):
            bottom_row.grid_columnconfigure(c, weight=1, uniform="student_bottom")

        btn_cfg_bottom = dict(btn_cfg, pady=7)
        tk.Button(bottom_row, text="Lấy ảnh Học sinh", command=self.on_capture, **btn_cfg_bottom).grid(
            row=0, column=0, sticky="ew", padx=4, pady=4
        )
        tk.Button(bottom_row, text="Training Data", command=lambda: None, **btn_cfg_bottom).grid(
            row=0, column=1, sticky="ew", padx=4, pady=4
        )

    def _build_right_section(self, parent: tk.Frame) -> None:
        font_label = ("times new roman", 10)
        font_label_bold = ("times new roman", 10, "bold")

        # --- Student search block ---
        search_group = tk.LabelFrame(
            parent,
            text="Hệ thống Tìm kiếm",
            bg=self.PANEL_BG,
            fg="#1F1F1F",
            font=font_label_bold,
            padx=10,
            pady=10,
        )
        search_group.pack(fill="x")

        tk.Label(
            search_group,
            text="Tìm kiếm theo:",
            bg=self.PANEL_BG,
            fg=self.TITLE_RED,
            font=font_label_bold,
        ).grid(row=0, column=0, sticky="w", pady=6)
        ttk.Combobox(
            search_group,
            textvariable=self.search_type_var,
            values=["ID Học sinh", "Tên học sinh", "Lớp học"],
            state="readonly",
            width=14,
            style="Student.TCombobox",
        ).grid(row=0, column=1, sticky="w", padx=(8, 10), pady=6, ipady=3)
        tk.Entry(
            search_group,
            textvariable=self.search_var,
            font=font_label,
            bd=1,
            relief="solid",
        ).grid(row=0, column=2, sticky="ew", pady=6, ipady=3)
        tk.Button(
            search_group,
            text="Tìm kiếm",
            command=self._handle_search,
            bg=self.ACTION_BLUE,
            activebackground=self.ACTION_BLUE_ACTIVE,
            fg="white",
            activeforeground="white",
            font=font_label_bold,
            bd=1,
            relief="solid",
            padx=14,
            pady=4,
            cursor="hand2",
        ).grid(row=0, column=3, sticky="e", padx=(10, 6), pady=6)
        tk.Button(
            search_group,
            text="Xem tất cả",
            command=self._handle_show_all,
            bg=self.ACTION_BLUE,
            activebackground=self.ACTION_BLUE_ACTIVE,
            fg="white",
            activeforeground="white",
            font=font_label_bold,
            bd=1,
            relief="solid",
            padx=14,
            pady=4,
            cursor="hand2",
        ).grid(row=0, column=4, sticky="e", pady=6)
        search_group.columnconfigure(2, weight=1)

        # --- Student table ---
        table_wrap = tk.Frame(parent, bg=self.PANEL_BG)
        table_wrap.pack(fill="both", expand=True, pady=(10, 10))

        columns = (
            "student_id",
            "year",
            "semester",
            "name",
            "class",
            "id_card",
        )
        self.student_tree = ttk.Treeview(
            table_wrap,
            columns=columns,
            show="headings",
            height=10,
            style="Student.Treeview",
        )
        headings = {
            "student_id": "ID Học sinh",
            "year": "Năm học",
            "semester": "Học kì",
            "name": "Họ tên",
            "class": "Lớp học",
            "id_card": "CMND",
        }
        for key, title in headings.items():
            self.student_tree.heading(key, text=title)
            if key == "name":
                self.student_tree.column(key, width=160, anchor="center")
            else:
                self.student_tree.column(key, width=105, anchor="center")

        y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.student_tree.yview)
        x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.student_tree.xview)
        self.student_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.student_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        self.student_tree.bind("<<TreeviewSelect>>", self._on_student_select)

        # --- Class management block ---
        class_group = tk.LabelFrame(
            parent,
            text="Quản lý lớp học",
            bg=self.PANEL_BG,
            fg=self.TITLE_RED,
            font=font_label_bold,
            padx=10,
            pady=10,
        )
        class_group.pack(fill="both", expand=True)

        class_body = tk.Frame(class_group, bg=self.PANEL_BG)
        class_body.grid(row=0, column=0, sticky="nsew")
        class_group.grid_rowconfigure(0, weight=1)
        class_group.grid_columnconfigure(0, weight=1)

        # Grid 1x2: left (inputs) + right (table).
        class_body.grid_rowconfigure(0, weight=1)
        class_body.grid_columnconfigure(0, weight=2)  # ~40%
        class_body.grid_columnconfigure(1, weight=3)  # ~60%

        left = tk.Frame(class_body, bg=self.PANEL_BG)
        right = tk.Frame(class_body, bg=self.PANEL_BG)
        left.grid(row=0, column=0, sticky="nsew")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Left side: search row + input area + button row
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=0)
        left.grid_rowconfigure(1, weight=0)
        left.grid_rowconfigure(2, weight=1)
        left.grid_rowconfigure(3, weight=0)

        # Search Row (one single row, responsive)
        search_row = tk.Frame(left, bg=self.PANEL_BG)
        search_row.grid(row=0, column=0, sticky="ew")
        search_row.grid_columnconfigure(0, weight=0)
        search_row.grid_columnconfigure(1, weight=1)  # entry expands
        search_row.grid_columnconfigure(2, weight=0)
        search_row.grid_columnconfigure(3, weight=0)

        ttk.Combobox(
            search_row,
            values=["Lớp"],
            state="readonly",
            width=7,
            style="Student.TCombobox",
        ).grid(row=0, column=0, sticky="w", pady=4, ipady=3)

        tk.Entry(
            search_row,
            textvariable=self.class_search_var,
            width=15,
            font=font_label,
            bd=1,
            relief="solid",
        ).grid(row=0, column=1, sticky="ew", padx=8, pady=4, ipady=3)

        search_btn_cfg = dict(
            bg=self.ACTION_BLUE,
            activebackground=self.ACTION_BLUE_ACTIVE,
            fg="white",
            activeforeground="white",
            font=font_label_bold,
            bd=1,
            relief="solid",
            padx=12,
            pady=4,
            cursor="hand2",
        )
        # Keep buttons compact so they don't force overflow on small widths.
        tk.Button(search_row, text="Tìm kiếm", command=lambda: None, **search_btn_cfg).grid(
            row=0, column=2, sticky="e", padx=(0, 6), pady=4
        )
        tk.Button(search_row, text="Xem tất cả", command=lambda: None, **search_btn_cfg).grid(
            row=0, column=3, sticky="e", pady=4
        )

        # Input Area
        input_area = tk.Frame(left, bg=self.PANEL_BG)
        input_area.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        input_area.grid_columnconfigure(0, weight=0)
        input_area.grid_columnconfigure(1, weight=1)

        tk.Label(input_area, text="Lớp học:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=0, column=0, sticky="w", pady=10
        )
        tk.Entry(
            input_area,
            textvariable=self.class_id_var,
            font=font_label,
            bd=1,
            relief="solid",
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=10, ipady=4)

        tk.Label(input_area, text="Tên lớp học:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=1, column=0, sticky="w", pady=10
        )
        tk.Entry(
            input_area,
            textvariable=self.class_name_var,
            font=font_label,
            bd=1,
            relief="solid",
        ).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=10, ipady=4)

        # Spacer to keep buttons at bottom of left area
        tk.Frame(left, bg=self.PANEL_BG).grid(row=2, column=0, sticky="nsew")


        btn_row = tk.Frame(left, bg=self.PANEL_BG)
        btn_row.grid(row=3, column=0, sticky="ew")
        for c in range(2):
            btn_row.grid_columnconfigure(c, weight=1, uniform="class_btns")

        class_btn_cfg = dict(
            bg=self.ACTION_YELLOW,
            activebackground=self.ACTION_YELLOW_ACTIVE,
            fg="#1F1F1F",
            font=("times new roman", 10, "bold"),
            bd=1,
            relief="solid",
            pady=6,
            cursor="hand2",
        )
        btn_texts = ["Thêm mới", "Xóa", "Cập nhật", "Làm mới"]
        btn_cmds = [self._handle_class_create, self._handle_class_delete, self._handle_class_update, self._handle_class_refresh]
        for idx, text in enumerate(btn_texts):
            r = idx // 2
            c = idx % 2
            tk.Button(btn_row, text=text, command=btn_cmds[idx], **class_btn_cfg).grid(
                row=r, column=c, sticky="ew", padx=4, pady=2
            )

        # Right side: Treeview
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)
        right.grid_columnconfigure(1, weight=0)

        class_cols = ("class_id", "class_name")
        self.class_tree = ttk.Treeview(
            right,
            columns=class_cols,
            show="headings",
            height=9,
            style="Student.Treeview",
        )
        self.class_tree.heading("class_id", text="Lớp học", anchor="center")
        self.class_tree.heading("class_name", text="Tên", anchor="center")

        self.class_tree.column("class_id", width=100, minwidth=80, anchor="center", stretch=False)
        self.class_tree.column("class_name", width=200, minwidth=120, anchor="center", stretch=True)

        class_scroll = ttk.Scrollbar(right, orient="vertical", command=self.class_tree.yview)
        self.class_tree.configure(yscrollcommand=class_scroll.set)
        self.class_tree.grid(row=0, column=0, sticky="nsew")
        class_scroll.grid(row=0, column=1, sticky="ns")

        self.class_tree.bind("<<TreeviewSelect>>", self._on_class_select)

        # Initial load
        self._handle_class_refresh(show_message=False)


    # ----------------- Student actions (handlers) -----------------
    def _handle_save(self) -> None:
        ok, msg = self.on_save(
            self.student_id_var.get().strip(),
            self.name_var.get().strip(),
            self.class_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip(),
            self.year_var.get().strip(),
            self.semester_var.get().strip(),
            self.gender_var.get().strip(),
            self.dob_var.get().strip(),
            self.address_var.get().strip(),
            self.photo_var.get().strip(),
        )
        self._show_result(ok, msg)
        if ok:
            self._clear_form()

    def _handle_update(self) -> None:
        ok, msg = self.on_update(
            self.student_id_var.get().strip(),
            self.name_var.get().strip(),
            self.class_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip(),
            self.year_var.get().strip(),
            self.semester_var.get().strip(),
            self.gender_var.get().strip(),
            self.dob_var.get().strip(),
            self.address_var.get().strip(),
            self.photo_var.get().strip(),
        )
        self._show_result(ok, msg)

    def _handle_delete(self) -> None:
        ok, msg = self.on_delete(self.student_id_var.get().strip())
        self._show_result(ok, msg)
        if ok:
            self._clear_form()

    def _handle_refresh(self) -> None:
        ok, msg = self.on_refresh()
        # refresh should not be an error popup
        if msg:
            self._show_result(ok, msg)
        self._clear_form()

    def _handle_search(self) -> None:
        ok, msg = self.on_search(self.search_type_var.get().strip(), self.search_var.get().strip())
        if self.search_var.get().strip():
            self._show_result(ok, msg)

    def _handle_show_all(self) -> None:
        self.search_var.set("")
        self.on_search(self.search_type_var.get().strip(), "")

    def _on_student_select(self, _: object) -> None:
        sel = self.student_tree.selection()
        if not sel:
            return
        values = self.student_tree.item(sel[0], "values")
        if len(values) >= 6:
            self.student_id_var.set(values[0])
            self.year_var.set(values[1])
            self.semester_var.set(values[2])
            self.name_var.set(values[3])
            class_id = values[4]
            self.class_var.set(class_id)
            # Update displayed label in combobox if we have mapping.
            try:
                id_to_label = {v: k for k, v in getattr(self, "_class_label_to_id", {}).items()}
                label = id_to_label.get(class_id)
                if label:
                    self.class_cb.set(label)
                else:
                    self.class_cb.set(class_id)
            except Exception:
                self.class_cb.set(class_id)
            self.id_card_var.set(values[5])

    def _clear_form(self) -> None:
        self.student_id_var.set("")
        self.name_var.set("")
        self.class_var.set("")
        self.gender_var.set("Nam")
        self.dob_var.set("")
        self.id_card_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.photo_var.set("Không ảnh")

    @staticmethod
    def _show_result(ok: bool, msg: str) -> None:
        if ok:
            messagebox.showinfo("Thông báo", msg)
        else:
            messagebox.showerror("Lỗi", msg)

    # ----------------- Table rendering -----------------
    def set_table_rows(self, students: list[object]) -> None:
        self._students_cache = students
        self.student_tree.delete(*self.student_tree.get_children())
        for st in students:
            # StudentModel attributes in this project: student_id, year, semester, name, class_name, ...
            st_id = getattr(st, "student_id", "")
            year = getattr(st, "year", "") or ""
            semester = getattr(st, "semester", "") or ""
            name = getattr(st, "name", "") or ""
            class_name = getattr(st, "class_name", "") or ""
            id_card = getattr(st, "roll", "") or ""  # fallback: some UI shows CMND but schema uses Roll
            self.student_tree.insert("", "end", values=(st_id, year, semester, name, class_name, id_card))

    # ----------------- Class management (embedded) -----------------
    def _refresh_class_combobox_values(self) -> list[str]:
        self._class_label_to_id = {}
        labels: list[str] = []
        try:
            classes = self._class_controller.list_all()
            for c in classes:
                class_id, class_name = c.class_id, c.name
                label = class_name
                if label in self._class_label_to_id and self._class_label_to_id[label] != class_id:
                    label = f"{class_name} ({class_id})"
                self._class_label_to_id[label] = class_id
                labels.append(label)
        except Exception:
            pass
        return labels

    def _render_class_rows(self, rows: list[tuple[str, str]]) -> None:
        if not hasattr(self, "class_tree"):
            return
        self.class_tree.delete(*self.class_tree.get_children())
        for class_id, class_name in rows:
            self.class_tree.insert("", "end", values=(class_id, class_name))

    def _handle_class_refresh(self, *, show_message: bool = True) -> None:
        rows = [(m.class_id, m.name) for m in self._class_controller.list_all()]
        self._render_class_rows(rows)

        # Update student class combobox values if it exists.
        if hasattr(self, "class_cb"):
            labels = self._refresh_class_combobox_values()
            self.class_cb.configure(values=tuple(labels))

        if show_message:
            self._show_result(True, "Đã làm mới danh sách lớp.")

    def _on_class_select(self, _: object) -> None:
        sel = self.class_tree.selection()
        if not sel:
            return
        values = self.class_tree.item(sel[0], "values")
        if len(values) >= 2:
            self.class_id_var.set(values[0])
            self.class_name_var.set(values[1])

    def _handle_class_create(self) -> None:
        class_id = self.class_id_var.get().strip()
        class_name = self.class_name_var.get().strip()
        ok, msg = self._class_controller.create(class_id, class_name)
        self._show_result(ok, msg)
        if ok:
            self._handle_class_refresh(show_message=False)

    def _handle_class_update(self) -> None:
        class_id = self.class_id_var.get().strip()
        class_name = self.class_name_var.get().strip()
        ok, msg = self._class_controller.update(class_id, class_name)
        self._show_result(ok, msg)
        if ok:
            self._handle_class_refresh(show_message=False)

    def _handle_class_delete(self) -> None:
        class_id = self.class_id_var.get().strip()
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa lớp này?") is False:
            return
        ok, msg = self._class_controller.delete(class_id)
        self._show_result(ok, msg)
        if ok:
            self.class_id_var.set("")
            self.class_name_var.set("")
            self._handle_class_refresh(show_message=False)

