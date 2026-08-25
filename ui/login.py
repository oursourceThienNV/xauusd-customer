import tkinter as tk
from tkinter import messagebox
import threading
import requests
import MetaTrader5 as mt5

from config import *
from ui.main_ui import build_ui
from core.bot import bot_loop
from ui.trend_ui import show_trend_ui
from config import API_BASE_URL, APP_VERSION


ERROR_MAP = {
    "00": "Đăng nhập thành công",
    "03": "Tài khoản chưa tồn tại vui lòng đăng ký tài khoản",
    "04": "Tài khoản bị khóa",
    "05": "Đã có phiên bản mới, vui lòng cập nhật"
}


# =====================================
# API LOGIN
# =====================================

def api_login(account):
    try:

        # =====================================
        # CALL API
        # =====================================

        res = requests.post(
            f"{API_BASE_URL}/login",
            json={
                "username": str(account),
                "version": APP_VERSION
            },
            timeout=10
        )

        try:
            data = res.json()
            
        except:
            return {"ok": False, "msg": "API không trả JSON"}

        error_code = data.get("error_code")

        # =====================================
        # SUCCESS
        # =====================================
        if error_code == "00":
            return {
                "ok": True,
                "data": data
            }

        # =====================================
        # FAIL
        # =====================================

        msg = ERROR_MAP.get(error_code, "Lỗi không xác định")

        return {
            "ok": False,
            "msg": msg
        }

    except Exception:
        return {
            "ok": False,
            "msg": "Không kết nối được server"
        }


# =====================================
# LOGIN UI
# =====================================

def show_login(root):

    login_frame = tk.Frame(root)
    login_frame.pack(pady=80)

    tk.Label(
        login_frame,
        text="LOGIN",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    def login():

        def run():

            # =====================================
            # INIT MT5
            # =====================================

            if not mt5.initialize():

                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Lỗi",
                        "Không mở được MT5"
                    )
                )

                return

            # =====================================
            # GET ACCOUNT INFO
            # =====================================

            account_info = mt5.account_info()

            

            if account_info is None:

                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Lỗi",
                        "MT5 chưa đăng nhập tài khoản"
                    )
                )

                return

            # =====================================
            # GET ACCOUNT
            # =====================================

            account = account_info.login


            # =====================================
            # LOGIN API
            # =====================================

            result = api_login(account)

            # =====================================
            # LOGIN SUCCESS
            # =====================================

            if result["ok"]:

                def open_trend():

                    login_frame.destroy()

                    # Xóa toàn bộ UI hiện tại
                    for widget in root.winfo_children():
                        widget.destroy()

                    # Vào thẳng màn xu hướng
                    login_data = result["data"]

                    show_trend_ui(
                        root,
                        lambda: show_login(root),
                        login_data
                    )

                root.after(0, open_trend)

            # =====================================
            # LOGIN FAIL
            # =====================================

            else:

                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Lỗi",
                        result["msg"]
                    )
                )

        threading.Thread(
            target=run,
            daemon=True
        ).start()

    # =====================================
    # LOGIN BUTTON
    # =====================================

    tk.Button(
        login_frame,
        text="Login",
        width=20,
        height=2,
        bg="#2563eb",
        fg="white",
        font=("Arial", 11, "bold"),
        command=login
    ).pack(pady=10)


# =====================================
# COMBO UI
# =====================================

def show_combo_ui(root, back):

    for w in root.winfo_children():
        w.destroy()

    tk.Label(
        root,
        text="Combo (đang phát triển)"
    ).pack()

    tk.Button(
        root,
        text="Back",
        command=back
    ).pack()