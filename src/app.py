from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Optional
from db.database import DatabaseConnection


class App:
    STANDARD_MIN_WIDTH = 1100
    STANDARD_MIN_HEIGHT = 640

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Face Recognition Attendance System")

        self.project_root = Path(__file__).resolve().parents[1]
        self.assets_dir = self.project_root / "assets"

        self._current_view: Optional[tk.Widget] = None

        self._apply_fullscreen_window_geometry()
        self._apply_window_icon()

        self.database = DatabaseConnection()

        from src.router import Router

        self.router = Router(self)

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def _apply_fullscreen_window_geometry(self) -> None:
        self.root.minsize(self.STANDARD_MIN_WIDTH, self.STANDARD_MIN_HEIGHT)

        try:
            self.root.state("zoomed")
            return
        except tk.TclError:
            pass

        try:
            self.root.attributes("-fullscreen", True)
        except tk.TclError:
            try:
                screen_w = self.root.winfo_screenwidth()
                screen_h = self.root.winfo_screenheight()
                self.root.geometry(f"{screen_w}x{screen_h}+0+0")
            except Exception:  # noqa: BLE001
                pass

    def _find_icon_file(self) -> Path | None:
        supported = ["*.ico", "*.png", "*.gif"]
        for pattern in supported:
            matches = list(self.assets_dir.glob(pattern))
            if matches:
                return matches[0]
        return None

    def _apply_window_icon(self) -> None:
        icon_path = self._find_icon_file()
        if not icon_path:
            return

        try:
            if icon_path.suffix.lower() == ".ico":
                self.root.iconbitmap(default=str(icon_path))
            else:
                icon_image = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon_image)
                # keep reference
                self.root._icon_ref = icon_image
        except tk.TclError:
            pass

    def set_view(self, view: tk.Widget) -> None:
        if self._current_view is not None:
            self._current_view.pack_forget()
            self._current_view.destroy()
        self._current_view = view
        self._current_view.pack(fill="both", expand=True)

        self._apply_fullscreen_window_geometry()

    def on_exit(self) -> None:
        try:
            self.database._close()
        finally:
            self.root.destroy()

    def run(self) -> None:
        self.router.show("login")
        self.root.mainloop()

