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

from models.teacher_model import TeacherModel


class TeacherView(tk.Frame):
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

        self._bg_path = self._resolve_background_path()
        self._bg_original = None
        self._bg_photo = None
        self._bg_image_id: int | None = None
        self._resize_job: str | None = None
        self._last_size: tuple[int, int] | None = None

        self.teacher_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.security_q_var = tk.StringVar(value="default")
        self.security_a_var = tk.StringVar(value="default")
        self.password_var = tk.StringVar()

        self.search_var = tk.StringVar()

        self._configure_styles()

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self.FALLBACK_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._build_top_widgets()
        self._build_content()
        self._start_clock()

    # ---------- helpers ----------
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

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.configure("Teacher.Treeview", font=("times new roman", 10), rowheight=24)
        style.configure("Teacher.Treeview.Heading", font=("times new roman", 10, "bold"))
        style.configure("Teacher.TCombobox", font=("times new roman", 10))

    # ---------- top banner ----------
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
            text="Quản lý thông tin Giảng viên",
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

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_rowconfigure(2, weight=0)

        tk.Label(parent, text="Thông tin Giảng viên", bg=self.PANEL_BG, fg=self.TITLE_RED, font=font_title).grid(
            row=0, column=0, sticky="ew", pady=(0, 10)
        )

        info = tk.LabelFrame(parent, text="Thông tin cơ bản", bg=self.PANEL_BG, fg="#1F1F1F", font=font_label_bold, padx=10, pady=10)
        info.grid(row=1, column=0, sticky="nsew")
        info.grid_columnconfigure(0, weight=0)
        info.grid_columnconfigure(1, weight=1)

        def add_row(r: int, label: str, var: tk.StringVar, *, show: str | None = None, readonly: bool = False) -> None:
            tk.Label(info, text=label, bg=self.PANEL_BG, font=font_label_bold).grid(row=r, column=0, sticky="w", pady=8)
            ent = tk.Entry(info, textvariable=var, font=font_label, bd=1, relief="solid", show=show)
            if readonly:
                ent.configure(state="readonly")
            ent.grid(row=r, column=1, sticky="ew", padx=(8, 0), pady=8, ipady=4)

        add_row(0, "Teacher ID:", self.teacher_id_var, readonly=True)
        add_row(1, "Họ tên:", self.name_var)
        add_row(2, "SĐT:", self.phone_var)
        add_row(3, "Email:", self.email_var)
        add_row(4, "Câu hỏi bảo mật:", self.security_q_var)
        add_row(5, "Trả lời:", self.security_a_var)
        add_row(6, "Mật khẩu:", self.password_var, show="*")

        buttons = tk.Frame(parent, bg=self.PANEL_BG)
        buttons.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        buttons.grid_columnconfigure(0, weight=1)

        action_row = tk.Frame(buttons, bg=self.PANEL_BG)
        action_row.grid(row=0, column=0, sticky="ew")

        action_row.grid_columnconfigure(0, weight=1, uniform="action")
        action_row.grid_columnconfigure(1, weight=1, uniform="action")

        btn_cfg = dict(
            bg=self.ACTION_BLUE,
            activebackground=self.ACTION_BLUE_ACTIVE,
            fg="white",
            activeforeground="white",
            font=font_label_bold,
            bd=1,
            relief="solid",
            cursor="hand2",
            pady=8,
        )

        tk.Button(action_row, text="Thêm", command=self._handle_save, **btn_cfg).grid(
            row=0, column=0, sticky="ew", padx=6, pady=4
        )
        tk.Button(action_row, text="Xóa", command=self._handle_delete, **btn_cfg).grid(
            row=0, column=1, sticky="ew", padx=6, pady=4
        )

        tk.Button(action_row, text="Cập nhật", command=self._handle_update, **btn_cfg).grid(
            row=1, column=0, sticky="ew", padx=6, pady=4
        )
        tk.Button(action_row, text="Làm mới", command=self._handle_refresh, **btn_cfg).grid(
            row=1, column=1, sticky="ew", padx=6, pady=4
        )

    def _build_right_section(self, parent: tk.Frame) -> None:
        font_label = ("times new roman", 10)
        font_label_bold = ("times new roman", 10, "bold")

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)

        search = tk.LabelFrame(parent, text="Tìm kiếm", bg=self.PANEL_BG, fg="#1F1F1F", font=font_label_bold, padx=10, pady=10)
        search.grid(row=0, column=0, sticky="ew")
        search.grid_columnconfigure(0, weight=0)
        search.grid_columnconfigure(1, weight=1)
        search.grid_columnconfigure(2, weight=0)
        search.grid_columnconfigure(3, weight=0)

        tk.Label(search, text="Từ khóa:", bg=self.PANEL_BG, font=font_label_bold).grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(search, textvariable=self.search_var, width=20, font=font_label, bd=1, relief="solid").grid(
            row=0, column=1, sticky="ew", padx=(8, 10), pady=4, ipady=3
        )
        tk.Button(
            search,
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
        ).grid(row=0, column=2, sticky="e", pady=4)

        tk.Button(
            search,
            text="Xem tất cả",
            command=self._handle_all,
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
        ).grid(row=0, column=3, sticky="e", pady=4, padx=(8, 0))

        # Enter to search for convenience.
        search_entry = None
        for child in search.winfo_children():
            if isinstance(child, tk.Entry):
                search_entry = child
                break
        if search_entry is not None:
            search_entry.bind("<Return>", lambda _e: self._handle_search())

        table = tk.Frame(parent, bg=self.PANEL_BG)
        table.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        table.grid_columnconfigure(0, weight=1)
        table.grid_rowconfigure(0, weight=1)

        cols = ("teacher_id", "name", "phone", "email")
        self.teacher_tree = ttk.Treeview(table, columns=cols, show="headings", height=12, style="Teacher.Treeview")
        self.teacher_tree.heading("teacher_id", text="ID")
        self.teacher_tree.heading("name", text="Họ tên")
        self.teacher_tree.heading("phone", text="SĐT")
        self.teacher_tree.heading("email", text="Email")

        self.teacher_tree.column("teacher_id", width=80, anchor="center", stretch=False)
        self.teacher_tree.column("name", width=180, anchor="center", stretch=True)
        self.teacher_tree.column("phone", width=120, anchor="center", stretch=False)
        self.teacher_tree.column("email", width=200, anchor="center", stretch=True)

        y_scroll = ttk.Scrollbar(table, orient="vertical", command=self.teacher_tree.yview)
        self.teacher_tree.configure(yscrollcommand=y_scroll.set)
        self.teacher_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")

        self.teacher_tree.bind("<<TreeviewSelect>>", self._on_select_row)

    # ---------- actions ----------
    def _handle_save(self) -> None:
        ok, msg = self.on_save(
            self.name_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip(),
            self.security_q_var.get().strip(),
            self.security_a_var.get().strip(),
            self.password_var.get(),
        )
        self._show_result(ok, msg)
        if ok:
            self._clear_form(keep_id=True)

    def _handle_update(self) -> None:
        ok, msg = self.on_update(
            self.teacher_id_var.get().strip(),
            self.name_var.get().strip(),
            self.phone_var.get().strip(),
            self.email_var.get().strip(),
            self.security_q_var.get().strip(),
            self.security_a_var.get().strip(),
            self.password_var.get(),
        )
        self._show_result(ok, msg)

    def _handle_delete(self) -> None:
        ok, msg = self.on_delete(self.teacher_id_var.get().strip())
        self._show_result(ok, msg)
        if ok:
            self._clear_form(keep_id=True)

    def _handle_refresh(self) -> None:
        ok, msg = self.on_refresh()
        self._show_result(ok, msg)
        self._clear_form(keep_id=True)

    def _handle_search(self) -> None:
        keyword = self.search_var.get().strip()
        ok, msg = self.on_search(keyword)
        if keyword:
            self._show_result(ok, msg)

    def _handle_all(self) -> None:
        ok, msg = self.on_search("")
        self._show_result(ok, msg)

    def _on_select_row(self, _: object) -> None:
        sel = self.teacher_tree.selection()
        if not sel:
            return
        values = self.teacher_tree.item(sel[0], "values")
        # columns: id, name, phone, email
        if len(values) >= 4:
            self.teacher_id_var.set(values[0])
            self.name_var.set(values[1])
            self.phone_var.set(values[2])
            self.email_var.set(values[3])

    def _clear_form(self, *, keep_id: bool = False) -> None:
        if not keep_id:
            self.teacher_id_var.set("")
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.security_q_var.set("default")
        self.security_a_var.set("default")
        self.password_var.set("")

    def _show_result(self, ok: bool, msg: str) -> None:
        if ok:
            messagebox.showinfo("Thông báo", msg)
        else:
            messagebox.showerror("Lỗi", msg)

    def set_table_rows(self, teachers: list[TeacherModel]) -> None:
        self.teacher_tree.delete(*self.teacher_tree.get_children())
        for t in teachers:
            self.teacher_tree.insert("", "end", values=(t.teacher_id, t.name, t.phone, t.email))

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

        content_x = margin
        content_y = top_reserved
        content_w = max(0, width - margin * 2)
        content_h = max(0, height - top_reserved - margin)
        self.canvas.coords(self._content_win, content_x, content_y)
        self.canvas.itemconfigure(self._content_win, width=content_w, height=content_h)

