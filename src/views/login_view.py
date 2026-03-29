
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from typing import Callable


class LoginView(tk.Frame):

    FALLBACK_LEFT_BG = "#CFCFCF"
    FALLBACK_RIGHT_BG = "#9C9C9C"
    CARD_BG = "#FFFFFF"
    TITLE_COLOR = "#1CA3C8"
    BUTTON_BLUE = "#3399FF"

    def __init__(
        self,
        master: tk.Tk,
        on_login: Callable[[str, str], None],
        assets_dir: Path,
    ) -> None:
        super().__init__(master, bg=self.FALLBACK_LEFT_BG)
        self._on_login = on_login
        self.assets_dir = assets_dir
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.use_admin_var = tk.BooleanVar(value=False)
        self._bg_image_ref: tk.PhotoImage | None = None

        self._build_ui()

    def _load_image(self, filename: str) -> tk.PhotoImage | None:
        image_path = self.assets_dir / filename
        if not image_path.exists():
            return None
        try:
            return tk.PhotoImage(file=str(image_path))
        except tk.TclError:
            return None

    def _build_ui(self) -> None:
        self._bg_image_ref = self._load_image("login_bg.png")
        if self._bg_image_ref is not None:
            tk.Label(self, image=self._bg_image_ref, bd=0).place(
                relx=0,
                rely=0,
                relwidth=1,
                relheight=1,
            )
        else:
            tk.Frame(self, bg=self.FALLBACK_LEFT_BG).place(
                relx=0,
                rely=0,
                relwidth=0.5,
                relheight=1,
            )
            tk.Frame(self, bg=self.FALLBACK_RIGHT_BG).place(
                relx=0.5,
                rely=0,
                relwidth=0.5,
                relheight=1,
            )

        form_card = tk.Frame(self, bg=self.CARD_BG, bd=0)
        form_card.place(relx=0.5, rely=0.5, anchor="center", width=540, height=320)

        body = tk.Frame(form_card, bg=self.CARD_BG)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Đăng nhập",
            fg=self.TITLE_COLOR,
            bg=self.CARD_BG,
            font=("times new roman", 18, "bold"),
        ).place(relx=0.5, y=40, anchor="center")

        tk.Label(
            body,
            text="Email",
            bg=self.CARD_BG,
            fg="#5B5B5B",
            font=("times new roman", 11, "bold"),
        ).place(x=160, y=86)

        username_entry = tk.Entry(
            body,
            textvariable=self.username_var,
            width=20,
            font=("times new roman", 12),
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground="#B8B8B8",
            highlightcolor="#47B7E3",
        )
        username_entry.place(x=158, y=112, width=170, height=26)

        tk.Label(
            body,
            text="Mật khẩu",
            bg=self.CARD_BG,
            fg="#5B5B5B",
            font=("times new roman", 11, "bold"),
        ).place(x=160, y=154)

        password_entry = tk.Entry(
            body,
            textvariable=self.password_var,
            show="*",
            width=20,
            font=("times new roman", 12),
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground="#B8B8B8",
            highlightcolor="#47B7E3",
        )
        password_entry.place(x=158, y=180, width=170, height=26)

        tk.Checkbutton(
            body,
            text="Đăng nhập bằng tài khoản Admin",
            variable=self.use_admin_var,
            bg=self.CARD_BG,
            fg="#2C2C2C",
            activebackground=self.CARD_BG,
            activeforeground="#2C2C2C",
            selectcolor=self.CARD_BG,
            font=("times new roman", 10),
            highlightthickness=0,
            bd=0,
        ).place(x=155, y=220)

        login_button = tk.Button(
            body,
            text="Đăng nhập",
            command=self._handle_login_click,
            bg=self.BUTTON_BLUE,
            fg="white",
            activebackground="#2C7AD9",
            activeforeground="white",
            font=("times new roman", 12, "bold"),
            bd=0,
            padx=14,
            pady=4,
            cursor="hand2",
        )
        login_button.place(x=160, y=260, width=140, height=34)

        self.bind_all("<Return>", lambda _: self._handle_login_click())
        username_entry.focus_set()

    def _handle_login_click(self) -> None:
        username_or_email = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if self.use_admin_var.get() and not username_or_email:
            username_or_email = "admin@gmail.com"

        self._on_login(username_or_email, password)

    @staticmethod
    def show_warning(message: str) -> None:
        messagebox.showwarning("Validation", message)

    @staticmethod
    def show_error(message: str) -> None:
        messagebox.showerror("Login", message)

    @staticmethod
    def show_info(message: str) -> None:
        messagebox.showinfo("Login", message)
