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


def _show_result(ok: bool, msg: str) -> None:
    if ok:
        messagebox.showinfo("Thông báo", msg)
    else:
        messagebox.showerror("Lỗi", msg)


class AttendanceManagementView(tk.Frame):

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
            on_update: Callable[..., object],
            on_delete: Callable[..., object],
            on_refresh: Callable[..., object],
            on_search: Callable[..., object],
            on_export_csv: Callable[..., object],
            on_import_csv: Callable[..., object],
            on_today: Callable[..., object],
            on_all: Callable[..., object],
            on_back: Callable[[], None],
            assets_dir: Path,

    ) -> None:
        super().__init__(master, bg=self.FALLBACK_BG)
        self.assets_dir = assets_dir
        self.on_update = on_update
        self.on_delete = on_delete
        self.on_refresh = on_refresh
        self.on_search = on_search
        self.on_export_csv = on_export_csv
        self.on_import_csv = on_import_csv
        self.on_today = on_today
        self.on_all = on_all
        self.on_back = on_back

        self._bg_path = self._resolve_background_path()
        self._bg_original = None
        self._bg_photo = None
        self._bg_image_id: int | None = None
        self._resize_job: str | None = None
        self._last_size: tuple[int, int] | None = None

        self.attendance_id_var = tk.StringVar()
        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.time_in_var = tk.StringVar()
        self.time_out_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.attendance_status_var = tk.StringVar()
        self.lesson_id_var = tk.StringVar()

        self.search_type_var = tk.StringVar(value="ID Điểm Danh")
        self.search_var = tk.StringVar()

        self._configure_styles()

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
            text="Quản lý thông tin điểm danh",
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
        font_label = ("times new roman", 10)
        font_label_bold = ("times new roman", 10, "bold")
        font_title = ("times new roman", 12, "bold")

        # CẤU HÌNH DÒNG ĐỂ FORM CO GIÃN THEO CHIỀU DỌC
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)  # Tiêu đề
        parent.grid_rowconfigure(1, weight=1)  # Khung form sẽ mở rộng (chiếm hết khoảng trống)
        parent.grid_rowconfigure(2, weight=0)  # Khung chứa nút bấm cố định ở đáy

        # ======= TIÊU ĐỀ =======
        tk.Label(
            parent,
            text="Cập Nhật điểm danh",
            bg=self.PANEL_BG,
            fg="#2675BF",  # màu xanh giống hình
            font=font_title
        ).grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # ======= FORM INPUT =======
        form = tk.LabelFrame(
            parent,
            text="",
            bg=self.PANEL_BG,
            font=font_label_bold,
            padx=10,
            pady=10
        )
        form.grid(row=1, column=0, sticky="nsew")  # nsew giúp form giãn đa chiều
        form.grid_columnconfigure(1, weight=1)

        def add_row(r, label, var):
            tk.Label(form, text=label, bg=self.PANEL_BG, font=font_label_bold).grid(
                row=r, column=0, sticky="w", pady=4
            )
            tk.Entry(form, textvariable=var, font=font_label, bd=1, relief="solid").grid(
                row=r, column=1, sticky="ew", padx=6, pady=4, ipady=3
            )

        add_row(0, "ID Điểm Danh:", self.attendance_id_var)
        add_row(1, "ID Học sinh:", self.student_id_var)
        add_row(2, "Tên Học sinh:", self.student_name_var)
        add_row(3, "Lớp học:", self.class_var)
        add_row(4, "Giờ vào:", self.time_in_var)
        add_row(5, "Giờ ra:", self.time_out_var)
        add_row(6, "Ngày:", self.date_var)
        add_row(7, "Điểm danh:", self.attendance_status_var)
        add_row(8, "ID Bài học:", self.lesson_id_var)

        # ======= NHÓM TẤT CẢ NÚT XUỐNG ĐÁY =======
        buttons_frame = tk.Frame(parent, bg=self.PANEL_BG)
        buttons_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        buttons_frame.grid_columnconfigure(0, weight=1)

        # NÚT — DÒNG 1: 2 NÚT XANH
        row_btn = tk.Frame(buttons_frame, bg=self.PANEL_BG)
        row_btn.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        row_btn.grid_columnconfigure((0, 1), weight=1, uniform="btn_top")

        btn_blue = dict(
            bg="#4BA3E3",
            fg="white",
            activebackground="#1B83C9",
            activeforeground="white",
            font=font_label_bold,
            bd=1,
            relief="solid",
            pady=6,
            cursor="hand2"
        )
        tk.Button(row_btn, text="Nhập file CSV", **btn_blue,
                  command=self._handle_import).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Button(row_btn, text="Xuất file CSV", **btn_blue,
                  command=self._handle_export).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # NÚT — DÒNG 2: 2 NÚT VÀNG
        row_btn2 = tk.Frame(buttons_frame, bg=self.PANEL_BG)
        row_btn2.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        row_btn2.grid_columnconfigure((0, 1), weight=1, uniform="btn_mid")

        btn_yellow = dict(
            bg="#E9D748",
            fg="black",
            activebackground="#D1BF2C",
            font=font_label_bold,
            bd=1,
            relief="solid",
            pady=6,
            cursor="hand2"
        )
        tk.Button(row_btn2, text="Cập nhật", **btn_yellow,
                  command=self._handle_update).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Button(row_btn2, text="Làm mới", **btn_yellow,
                  command=self._handle_refresh).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # NÚT — DÒNG 3: NÚT ĐEN "Xem ảnh"
        tk.Button(
            buttons_frame,
            text="Xem ảnh",
            bg="black",
            fg="white",
            activebackground="#333333",
            font=font_label_bold,
            bd=1,
            relief="solid",
            pady=7,
            cursor="hand2",
            command=self._handle_show_image
        ).grid(row=2, column=0, sticky="ew", pady=(0, 5))

        # NÚT — DÒNG 4: NÚT ĐỎ "Xóa"
        tk.Button(
            buttons_frame,
            text="Xóa",
            bg="#DF2A2A",
            fg="white",
            activebackground="#B81F1F",
            font=font_label_bold,
            bd=1,
            relief="solid",
            pady=7,
            cursor="hand2",
            command=self._handle_delete
        ).grid(row=3, column=0, sticky="ew")

    def _build_right_section(self, parent: tk.Frame) -> None:
        font_label = ("times new roman", 10)
        font_label_bold = ("times new roman", 10, "bold")

        # ĐỒNG BỘ DÙNG PACK NHƯ TRANG STUDENT CHO ỔN ĐỊNH
        search_group = tk.LabelFrame(
            parent,
            bg=self.PANEL_BG,
            fg="#1F1F1F",
            font=font_label_bold,
            padx=10,
            pady=10,
        )
        search_group.pack(fill="x")

        tk.Label(search_group, text="Tìm kiếm theo:", bg=self.PANEL_BG, font=font_label_bold).grid(
            row=0, column=0, sticky="w", pady=6
        )
        ttk.Combobox(
            search_group,
            textvariable=self.search_type_var,
            values=["ID Điểm Danh", "ID Học sinh", "Tên học sinh", "Lớp học", "Ngày"],
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

        btn_cfg = dict(
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
        )
        tk.Button(search_group, text="Tìm Kiếm", command=self._handle_search, **btn_cfg).grid(
            row=0, column=3, sticky="e", padx=(10, 6), pady=6
        )
        tk.Button(search_group, text="Hôm nay", command=self._handle_today, **btn_cfg).grid(
            row=0, column=4, sticky="e", pady=6
        )
        tk.Button(search_group, text="Xem tất cả", command=self._handle_all, **btn_cfg).grid(
            row=0, column=5, sticky="e", padx=(10, 6), pady=6
        )
        search_group.grid_columnconfigure(2, weight=1)

        # TABLE BỌC BẰNG FRAME VÀ DÙNG PACK
        table_wrap = tk.Frame(parent, bg=self.PANEL_BG)
        table_wrap.pack(fill="both", expand=True, pady=(10, 10))

        columns = (
            "attendance_id",
            "student_id",
            "name",
            "class",
            "time_in",
            "time_out",
            "date",
            "lesson_id",
            "status",
        )
        self.attendance_tree = ttk.Treeview(
            table_wrap,
            columns=columns,
            show="headings",
            height=12,
            style="Student.Treeview",
        )
        headings = {
            "attendance_id": "ID",
            "student_id": "HS",
            "name": "Tên",
            "class": "Lớp",
            "time_in": "Giờ vào",
            "time_out": "Giờ ra",
            "date": "Ngày",
            "lesson_id": "Lesson",
            "status": "Trạng thái",
        }
        for key, title in headings.items():
            self.attendance_tree.heading(key, text=title)

        self.attendance_tree.column("attendance_id", width=130, anchor="center")
        self.attendance_tree.column("student_id", width=70, anchor="center")
        self.attendance_tree.column("name", width=150, anchor="w")
        self.attendance_tree.column("class", width=90, anchor="center")
        self.attendance_tree.column("time_in", width=90, anchor="center")
        self.attendance_tree.column("time_out", width=90, anchor="center")
        self.attendance_tree.column("date", width=95, anchor="center")
        self.attendance_tree.column("lesson_id", width=70, anchor="center")
        self.attendance_tree.column("status", width=110, anchor="center")

        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.attendance_tree.yview)
        x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.attendance_tree.xview)
        self.attendance_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.attendance_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.attendance_tree.bind("<<TreeviewSelect>>", self._on_select_row)

    def set_table_rows(self, rows: list[object]) -> None:
        # rows are AttendanceModel; keep signature loose to match other views.
        if not hasattr(self, "attendance_tree"):
            return
        self.attendance_tree.delete(*self.attendance_tree.get_children())
        for att in rows:
            self.attendance_tree.insert(
                "",
                "end",
                values=(
                    getattr(att, "attendance_id", ""),
                    getattr(att, "student_id", ""),
                    getattr(att, "name", ""),
                    getattr(att, "class_name", ""),
                    getattr(att, "time_in", ""),
                    getattr(att, "time_out", ""),
                    getattr(att, "date", ""),
                    getattr(att, "lesson_id", ""),
                    getattr(att, "attendance_status", ""),
                ),
            )

    def _on_select_row(self, _: object = None) -> None:
        selected = self.attendance_tree.selection()
        if not selected:
            return
        values = self.attendance_tree.item(selected[0], "values")
        if not values:
            return
        (
            attendance_id,
            student_id,
            name,
            class_name,
            time_in,
            time_out,
            day,
            lesson_id,
            status,
        ) = values
        self.attendance_id_var.set(attendance_id)
        self.student_id_var.set(student_id)
        self.student_name_var.set(name)
        self.class_var.set(class_name)
        self.time_in_var.set(time_in)
        self.time_out_var.set(time_out)
        self.date_var.set(day)
        self.lesson_id_var.set(lesson_id)
        self.attendance_status_var.set(status)

    def _handle_show_image(self) -> None:
        att_id = self.attendance_id_var.get().strip()
        if not att_id:
            messagebox.showwarning("Cảnh báo", "Chưa chọn bản ghi để xem ảnh.")
            return
        ok, msg = self.on_show_image(att_id)
        _show_result(ok, msg)

    def _handle_import(self) -> None:
        ok, msg = self.on_import_csv()
        _show_result(ok, msg)

    def _handle_export(self) -> None:
        ok, msg = self.on_export_csv()
        _show_result(ok, msg)

    def _handle_update(self) -> None:
        ok, msg = self.on_update(
            self.attendance_id_var.get(),
            self.student_id_var.get(),
            self.student_name_var.get(),
            self.class_var.get(),
            self.time_in_var.get(),
            self.time_out_var.get(),
            self.date_var.get(),
            self.lesson_id_var.get(),
            self.attendance_status_var.get(),
        )
        _show_result(ok, msg)

    def _handle_delete(self) -> None:
        att_id = self.attendance_id_var.get().strip()
        if not att_id:
            messagebox.showwarning("Cảnh báo", "Chưa chọn bản ghi để xóa.")
            return
        if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa bản ghi này?"):
            return
        ok, msg = self.on_delete(att_id)
        _show_result(ok, msg)

    def _handle_refresh(self) -> None:
        ok, msg = self.on_refresh()
        _show_result(ok, msg)

    def _handle_search(self) -> None:
        ok, msg = self.on_search(self.search_type_var.get(), self.search_var.get())
        _show_result(ok, msg)

    def _handle_today(self) -> None:
        ok, msg = self.on_today()
        _show_result(ok, msg)

    def _handle_all(self) -> None:
        ok, msg = self.on_all()
        _show_result(ok, msg)

