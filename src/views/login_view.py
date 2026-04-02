
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
    CARD_WIDTH = 640
    CARD_HEIGHT = 390
    TITLE_FONT = ("times new roman", 24, "bold")
    LABEL_FONT = ("times new roman", 13, "bold")
    ENTRY_FONT = ("times new roman", 14)
    CHECKBOX_FONT = ("times new roman", 12)
    BUTTON_FONT = ("times new roman", 14, "bold")

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
        form_card.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=self.CARD_WIDTH,
            height=self.CARD_HEIGHT,
        )

        body = tk.Frame(form_card, bg=self.CARD_BG)
        body.pack(fill="both", expand=True)

        tk.Label(
            body,
            text="Đăng nhập",
            fg=self.TITLE_COLOR,
            bg=self.CARD_BG,
            font=self.TITLE_FONT,
        ).place(relx=0.5, y=52, anchor="center")

        tk.Label(
            body,
            text="Email",
            bg=self.CARD_BG,
            fg="#5B5B5B",
            font=self.LABEL_FONT,
        ).place(x=188, y=105)

        username_entry = tk.Entry(
            body,
            textvariable=self.username_var,
            width=24,
            font=self.ENTRY_FONT,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground="#B8B8B8",
            highlightcolor="#47B7E3",
        )
        username_entry.place(x=186, y=135, width=265, height=34)

        tk.Label(
            body,
            text="Mật khẩu",
            bg=self.CARD_BG,
            fg="#5B5B5B",
            font=self.LABEL_FONT,
        ).place(x=188, y=185)

        password_entry = tk.Entry(
            body,
            textvariable=self.password_var,
            show="*",
            width=24,
            font=self.ENTRY_FONT,
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground="#B8B8B8",
            highlightcolor="#47B7E3",
        )
        password_entry.place(x=186, y=215, width=265, height=34)

        tk.Checkbutton(
            body,
            text="Đăng nhập bằng tài khoản Admin",
            variable=self.use_admin_var,
            bg=self.CARD_BG,
            fg="#2C2C2C",
            activebackground=self.CARD_BG,
            activeforeground="#2C2C2C",
            selectcolor=self.CARD_BG,
            font=self.CHECKBOX_FONT,
            highlightthickness=0,
            bd=0,
        ).place(x=183, y=267)

        login_button = tk.Button(
            body,
            text="Đăng nhập",
            command=self._handle_login_click,
            bg=self.BUTTON_BLUE,
            fg="white",
            activebackground="#2C7AD9",
            activeforeground="white",
            font=self.BUTTON_FONT,
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        login_button.place(x=186, y=315, width=170, height=42)

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
