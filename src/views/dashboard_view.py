from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

import tkinter as tk

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None


class DashboardView(tk.Frame):

    FALLBACK_BG = "#355C8C"
    BANNER_BG = "#FFFFFF"
    BORDER_COLOR = "#B8B8B8"
    TILE_BG = "#FFFFFF"
    TILE_BORDER = "#D9D9D9"

    def __init__(
        self,
        master: tk.Tk,
        on_manage_students: Callable[[], None],
        on_face_recognition: Callable[[], None],
        on_attendance_report: Callable[[], None],
        on_subjects: Callable[[], None],
        on_statistics: Callable[[], None],
        on_teachers: Callable[[], None],
        on_lessons: Callable[[], None],
        on_view_images: Callable[[], None],
        on_exit: Callable[[], None],
        assets_dir: Path,
    ) -> None:
        super().__init__(master, bg=self.FALLBACK_BG)
        self.assets_dir = assets_dir

        self._bg_path = self.assets_dir / "bg.jpg"
        self._bg_original = None
        self._bg_photo = None
        self._bg_image_id: int | None = None
        self._resize_job: str | None = None
        self._last_size: tuple[int, int] | None = None

        self._tile_icon_refs: list[object] = []
        self._tile_windows: list[int] = []
        self._tiles: list[tuple[tk.Frame, Callable[[], None]]] = []

        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=self.FALLBACK_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self._build_top_widgets(on_exit)
        self._build_tiles(
            on_manage_students,
            on_face_recognition,
            on_attendance_report,
            on_subjects,
            on_statistics,
            on_teachers,
            on_lessons,
            on_view_images,
        )
        self._start_clock()


    def _load_icon(self, filenames: list[str], size: tuple[int, int]) -> object | None:
        for name in filenames:
            path = self.assets_dir / name
            if not path.exists():
                continue

            if Image is not None and ImageTk is not None:
                try:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize(size, Image.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except Exception:  
                    continue

            try:
                return tk.PhotoImage(file=str(path))
            except tk.TclError:
                continue

        return None

    def _build_top_widgets(self, on_exit: Callable[[], None]) -> None:
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
            text="Hệ thống nhận diện khuôn mặt",
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=("times new roman", 14, "bold"),
        ).pack(expand=True)
        self._banner_win = self.canvas.create_window(0, 0, window=banner, anchor="n")

        admin_box = tk.Frame(
            self.canvas,
            bg="#DFF0D8",
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        admin_box.pack_propagate(False)
        admin_box.configure(width=90, height=34)
        tk.Label(
            admin_box,
            text="Admin",
            bg="#DFF0D8",
            fg="#2E7D32",
            font=("times new roman", 11, "bold"),
        ).pack(expand=True)
        self._admin_win = self.canvas.create_window(0, 0, window=admin_box, anchor="ne")

        logout_box = tk.Frame(
            self.canvas,
            bg=self.BANNER_BG,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        logout_box.pack_propagate(False)
        logout_box.configure(width=130, height=34)
        tk.Button(
            logout_box,
            text="Đăng xuất",
            command=on_exit,
            bg=self.BANNER_BG,
            fg="#1F1F1F",
            font=("times new roman", 11, "bold"),
            bd=0,
            cursor="hand2",
        ).pack(fill="both", expand=True)
        self._logout_win = self.canvas.create_window(0, 0, window=logout_box, anchor="ne")

    def _build_tiles(
        self,
        on_manage_students: Callable[[], None],
        on_face_recognition: Callable[[], None],
        on_attendance_report: Callable[[], None],
        on_subjects: Callable[[], None],
        on_statistics: Callable[[], None],
        on_teachers: Callable[[], None],
        on_lessons: Callable[[], None],
        on_view_images: Callable[[], None],
    ) -> None:
        specs: list[tuple[list[str], str, str, Callable[[], None]]] = [
            (["icons/student.png"], "HS", "Học sinh", on_manage_students),
            (["icons/face-detection.png"], "ND", "Nhận diện", on_face_recognition),
            (["icons/attendance.png"], "DD", "Điểm danh", on_attendance_report),
            (["icons/books.png"], "MH", "Môn học", on_subjects),
            (["icons/dashboard.png"], "TK", "Thống kê", on_statistics),
            (["icons/teach.png"], "GV", "Giáo viên", on_teachers),
            (["icons/lesson.png"], "BH", "Buổi học", on_lessons),
            (["icons/gallery.png"], "XA", "Xem ảnh", on_view_images),
        ]

        for icon_files, fallback, label, callback in specs:
            tile = tk.Frame(
                self.canvas,
                bg=self.TILE_BG,
                highlightthickness=1,
                highlightbackground=self.TILE_BORDER,
                cursor="hand2",
            )
            tile.pack_propagate(False)
            tile.configure(width=170, height=150)

            icon = self._load_icon(icon_files, size=(64, 64))
            if icon is not None:
                self._tile_icon_refs.append(icon)
                icon_label = tk.Label(tile, image=icon, bg=self.TILE_BG)
                icon_label.pack(pady=(18, 8))
            else:
                icon_label = tk.Label(
                    tile,
                    text=fallback,
                    bg=self.TILE_BG,
                    fg="#1F1F1F",
                    font=("times new roman", 26, "bold"),
                )
                icon_label.pack(pady=(18, 8))

            text_label = tk.Label(
                tile,
                text=label,
                bg=self.TILE_BG,
                fg="#1F1F1F",
                font=("times new roman", 14, "bold"),
            )
            text_label.pack()

            def _on_click(_: object, cb: Callable[[], None] = callback) -> None:
                cb()

            for widget in (tile, icon_label, text_label):
                widget.bind("<Button-1>", _on_click)

            win_id = self.canvas.create_window(0, 0, window=tile, anchor="nw")
            self._tile_windows.append(win_id)
            self._tiles.append((tile, callback))

    def _on_canvas_configure(self, event: tk.Event) -> None:
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
                except Exception:  
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
            self._bg_image_id = self.canvas.create_image(
                0,
                0,
                image=self._bg_photo,
                anchor="nw",
            )
        else:
            self.canvas.itemconfigure(self._bg_image_id, image=self._bg_photo)

        self.canvas.tag_lower(self._bg_image_id)

    def _layout_widgets(self, width: int, height: int) -> None:
        margin = 12

        self.canvas.coords(self._clock_win, margin, margin)
        self.canvas.coords(self._banner_win, width / 2, margin)

        logout_right = width - margin
        self.canvas.coords(self._logout_win, logout_right, margin)
        self.canvas.coords(self._admin_win, logout_right - 130 - 10, margin)

        cols = 4
        rows = 2
        tile_w = 170
        tile_h = 150
        top_reserved = 110

        if width <= cols * tile_w + 20:
            gap_x = 10
        else:
            gap_x = int((width - cols * tile_w) / (cols + 1))
            gap_x = max(18, gap_x)

        available_h = max(0, height - top_reserved)
        if available_h <= rows * tile_h + 20:
            gap_y = 10
        else:
            gap_y = int((available_h - rows * tile_h) / (rows + 1))
            gap_y = max(18, gap_y)

        x0 = gap_x
        y0 = top_reserved + gap_y

        for index, win_id in enumerate(self._tile_windows):
            row = index // cols
            col = index % cols
            x = x0 + col * (tile_w + gap_x)
            y = y0 + row * (tile_h + gap_y)
            self.canvas.coords(win_id, x, y)
