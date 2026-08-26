import tkinter as tk
from tkinter import messagebox
import threading
import requests
import MetaTrader5 as mt5

from config import API_BASE_URL, APP_VERSION
from ui.trend_ui import show_trend_ui


# ============================================================
# CONFIG
# ============================================================

ERROR_MAP = {
    "00": "Đăng nhập thành công",
    "03": "Tài khoản chưa tồn tại. Vui lòng đăng ký tài khoản.",
    "04": "Tài khoản đang bị khóa.",
    "05": "Đã có phiên bản mới. Vui lòng cập nhật.",
}


# ============================================================
# API LOGIN
# ============================================================

def api_login(account):

    try:

        response = requests.post(
            f"{API_BASE_URL}/login",
            json={
                "username": str(account),
                "version": APP_VERSION,
            },
            timeout=10,
        )

        try:
            data = response.json()

        except Exception:
            return {
                "ok": False,
                "msg": "Server trả về dữ liệu không hợp lệ.",
            }

        error_code = data.get("error_code")

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if error_code == "00":

            return {
                "ok": True,
                "data": data,
            }

        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        return {
            "ok": False,
            "msg": ERROR_MAP.get(
                error_code,
                data.get("message") or "Đăng nhập thất bại.",
            ),
        }

    except requests.exceptions.Timeout:

        return {
            "ok": False,
            "msg": "Kết nối server quá thời gian.\nVui lòng thử lại.",
        }

    except requests.exceptions.ConnectionError:

        return {
            "ok": False,
            "msg": "Không thể kết nối đến server.",
        }

    except Exception as e:

        print("LOGIN API ERROR:", e)

        return {
            "ok": False,
            "msg": "Có lỗi xảy ra khi đăng nhập.",
        }


# ============================================================
# LOGIN UI
# ============================================================

def show_login(root):

    # ========================================================
    # CLEAR UI
    # ========================================================

    for widget in root.winfo_children():
        widget.destroy()

    # ========================================================
    # WINDOW
    # ========================================================

    root.title("Forex Bot Pro")

    try:
        root.geometry("900x650")
        root.minsize(760, 560)
    except Exception:
        pass

    # ========================================================
    # COLORS
    # ========================================================

    BG = "#0b1120"
    CARD = "#111827"
    CARD_DARK = "#0f172a"
    BORDER = "#1f2937"

    WHITE = "#f8fafc"
    MUTED = "#94a3b8"

    BLUE = "#2563eb"
    BLUE_HOVER = "#1d4ed8"

    GREEN = "#22c55e"
    RED = "#ef4444"
    YELLOW = "#f59e0b"

    root.configure(bg=BG)

    # ========================================================
    # MAIN BACKGROUND
    # ========================================================

    background = tk.Frame(
        root,
        bg=BG,
    )

    background.pack(
        fill="both",
        expand=True,
    )

    # ========================================================
    # TOP ACCENT
    # ========================================================

    tk.Frame(
        background,
        bg=BLUE,
        height=3,
    ).pack(
        fill="x",
        side="top",
    )

    # ========================================================
    # CENTER
    # ========================================================

    center = tk.Frame(
        background,
        bg=BG,
    )

    center.place(
        relx=0.5,
        rely=0.48,
        anchor="center",
    )

    # ========================================================
    # LOGO / BRAND
    # ========================================================

    brand = tk.Frame(
        center,
        bg=BG,
    )

    brand.pack(
        pady=(0, 18),
    )

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    logo = tk.Canvas(
        brand,
        width=66,
        height=66,
        bg=BG,
        highlightthickness=0,
    )

    logo.pack()

    # Outer circle

    logo.create_oval(
        4,
        4,
        62,
        62,
        fill=BLUE,
        outline="",
    )

    # Inner circle

    logo.create_oval(
        10,
        10,
        56,
        56,
        fill="#1e40af",
        outline="",
    )

    logo.create_text(
        33,
        33,
        text="FX",
        fill=WHITE,
        font=("Segoe UI", 16, "bold"),
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    tk.Label(
        brand,
        text="FOREX BOT PRO",
        bg=BG,
        fg=WHITE,
        font=("Segoe UI", 21, "bold"),
    ).pack(
        pady=(10, 2),
    )

    # --------------------------------------------------------
    # SUBTITLE
    # --------------------------------------------------------

    tk.Label(
        brand,
        text="Professional Automated Trading Platform",
        bg=BG,
        fg=MUTED,
        font=("Segoe UI", 9),
    ).pack()

    # ========================================================
    # LOGIN CARD
    # ========================================================

    card_border = tk.Frame(
        center,
        bg=BORDER,
        padx=1,
        pady=1,
    )

    card_border.pack()

    card = tk.Frame(
        card_border,
        bg=CARD,
        width=410,
        height=325,
    )

    card.pack()

    card.pack_propagate(False)

    # ========================================================
    # CARD TITLE
    # ========================================================

    tk.Label(
        card,
        text="Đăng nhập hệ thống",
        bg=CARD,
        fg=WHITE,
        font=("Segoe UI", 16, "bold"),
    ).pack(
        pady=(28, 3),
    )

    tk.Label(
        card,
        text="Tài khoản MetaTrader 5 sẽ được nhận diện tự động",
        bg=CARD,
        fg=MUTED,
        font=("Segoe UI", 9),
    ).pack()

    # ========================================================
    # MT5 STATUS
    # ========================================================

    status_box = tk.Frame(
        card,
        bg=CARD_DARK,
        height=52,
    )

    status_box.pack(
        fill="x",
        padx=28,
        pady=(24, 12),
    )

    status_box.pack_propagate(False)

    # --------------------------------------------------------
    # STATUS DOT
    # --------------------------------------------------------

    status_dot = tk.Label(
        status_box,
        text="●",
        bg=CARD_DARK,
        fg=MUTED,
        font=("Segoe UI", 12),
    )

    status_dot.pack(
        side="left",
        padx=(15, 7),
    )

    # --------------------------------------------------------
    # STATUS TEXT
    # --------------------------------------------------------

    status_text = tk.Label(
        status_box,
        text="Đang kiểm tra MetaTrader 5...",
        bg=CARD_DARK,
        fg=MUTED,
        font=("Segoe UI", 9),
        anchor="w",
    )

    status_text.pack(
        side="left",
        fill="x",
        expand=True,
    )

    # ========================================================
    # LOGIN BUTTON
    # ========================================================

    login_button = tk.Button(
        card,
        text="ĐĂNG NHẬP",
        bg=BLUE,
        fg=WHITE,
        activebackground=BLUE_HOVER,
        activeforeground=WHITE,
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
        height=2,
    )

    login_button.pack(
        fill="x",
        padx=28,
        pady=(4, 10),
    )

    # ========================================================
    # BUTTON HOVER
    # ========================================================

    def button_enter(event):

        if login_button["state"] != "disabled":

            login_button.configure(
                bg=BLUE_HOVER,
            )

    def button_leave(event):

        if login_button["state"] != "disabled":

            login_button.configure(
                bg=BLUE,
            )

    login_button.bind(
        "<Enter>",
        button_enter,
    )

    login_button.bind(
        "<Leave>",
        button_leave,
    )

    # ========================================================
    # FOOTER
    # ========================================================

    footer = tk.Frame(
        center,
        bg=BG,
    )

    footer.pack(
        pady=(16, 0),
    )

    tk.Label(
        footer,
        text=f"Version {APP_VERSION}",
        bg=BG,
        fg="#64748b",
        font=("Segoe UI", 8),
    ).pack()

    tk.Label(
        footer,
        text="© Forex Bot Pro  •  Secure Trading System",
        bg=BG,
        fg="#475569",
        font=("Segoe UI", 8),
    ).pack(
        pady=(3, 0),
    )

    # ========================================================
    # STATUS HELPER
    # ========================================================

    def set_status(
        text,
        color=MUTED,
    ):

        def update():

            try:

                status_dot.configure(
                    fg=color,
                )

                status_text.configure(
                    text=text,
                    fg=color,
                )

            except tk.TclError:
                pass

        root.after(
            0,
            update,
        )

    # ========================================================
    # BUTTON HELPER
    # ========================================================

    def set_button(
        text,
        enabled=True,
    ):

        def update():

            try:

                login_button.configure(
                    text=text,
                    state=(
                        "normal"
                        if enabled
                        else "disabled"
                    ),
                    bg=(
                        BLUE
                        if enabled
                        else "#334155"
                    ),
                    cursor=(
                        "hand2"
                        if enabled
                        else "arrow"
                    ),
                )

            except tk.TclError:
                pass

        root.after(
            0,
            update,
        )

    # ========================================================
    # LOGIN PROCESS
    # ========================================================

    def login():

        # ----------------------------------------------------
        # DISABLE BUTTON
        # ----------------------------------------------------

        login_button.configure(
            state="disabled",
            text="ĐANG XỬ LÝ...",
            bg="#334155",
            cursor="arrow",
        )

        set_status(
            "Đang kết nối MetaTrader 5...",
            BLUE,
        )

        # ----------------------------------------------------
        # BACKGROUND THREAD
        # ----------------------------------------------------

        def run():

            # =================================================
            # INIT MT5
            # =================================================

            try:

                mt5_ok = mt5.initialize()

            except Exception as e:

                print(
                    "MT5 INITIALIZE ERROR:",
                    e,
                )

                mt5_ok = False

            if not mt5_ok:

                set_status(
                    "Không thể kết nối MetaTrader 5",
                    RED,
                )

                set_button(
                    "ĐĂNG NHẬP",
                    True,
                )

                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "MetaTrader 5",
                        "Không mở được MetaTrader 5.\n\n"
                        "Vui lòng kiểm tra:\n"
                        "• MetaTrader 5 đã được cài đặt\n"
                        "• MetaTrader 5 đang được mở\n"
                        "• Algo Trading không ảnh hưởng đến đăng nhập",
                        parent=root,
                    ),
                )

                return

            # =================================================
            # ACCOUNT INFO
            # =================================================

            account_info = mt5.account_info()

            if account_info is None:

                set_status(
                    "MT5 chưa đăng nhập tài khoản",
                    YELLOW,
                )

                set_button(
                    "ĐĂNG NHẬP",
                    True,
                )

                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "MetaTrader 5",
                        "MT5 chưa đăng nhập tài khoản.\n\n"
                        "Vui lòng đăng nhập tài khoản trên MT5 "
                        "rồi thử lại.",
                        parent=root,
                    ),
                )

                return

            # =================================================
            # GET ACCOUNT
            # =================================================

            account = account_info.login

            set_status(
                f"Đang xác thực tài khoản MT5: {account}",
                BLUE,
            )

            # =================================================
            # API LOGIN
            # =================================================

            result = api_login(
                account,
            )

            # =================================================
            # SUCCESS
            # =================================================

            if result["ok"]:

                set_status(
                    "Đăng nhập thành công",
                    GREEN,
                )

                set_button(
                    "ĐĂNG NHẬP",
                    True,
                )

                def open_trend():

                    # -----------------------------------------
                    # CLEAR LOGIN
                    # -----------------------------------------

                    for widget in root.winfo_children():

                        widget.destroy()

                    # -----------------------------------------
                    # LOGIN DATA
                    # -----------------------------------------

                    login_data = result["data"]

                    # -----------------------------------------
                    # OPEN TREND UI
                    # -----------------------------------------

                    show_trend_ui(
                        root,
                        lambda: show_login(root),
                        login_data,
                    )

                root.after(
                    350,
                    open_trend,
                )

            # =================================================
            # LOGIN FAIL
            # =================================================

            else:

                set_status(
                    "Đăng nhập thất bại",
                    RED,
                )

                set_button(
                    "ĐĂNG NHẬP",
                    True,
                )

                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Đăng nhập thất bại",
                        result["msg"],
                        parent=root,
                    ),
                )

        threading.Thread(
            target=run,
            daemon=True,
        ).start()

    # ========================================================
    # BUTTON COMMAND
    # ========================================================

    login_button.configure(
        command=login,
    )

    # ========================================================
    # ENTER KEY
    # ========================================================

    root.bind(
        "<Return>",
        lambda event: login(),
    )

    # ========================================================
    # INITIAL MT5 STATUS CHECK
    # ========================================================

    def check_mt5():

        def run_check():

            try:

                initialized = mt5.initialize()

                if not initialized:

                    set_status(
                        "MetaTrader 5 chưa sẵn sàng",
                        RED,
                    )

                    return

                account_info = mt5.account_info()

                if account_info:

                    set_status(
                        f"MT5 sẵn sàng  •  Account {account_info.login}",
                        GREEN,
                    )

                else:

                    set_status(
                        "MT5 đã mở  •  Chưa đăng nhập tài khoản",
                        YELLOW,
                    )

            except Exception as e:

                print(
                    "MT5 CHECK ERROR:",
                    e,
                )

                set_status(
                    "Không kiểm tra được MetaTrader 5",
                    RED,
                )

        threading.Thread(
            target=run_check,
            daemon=True,
        ).start()

    check_mt5()


# ============================================================
# COMBO UI
# ============================================================

def show_combo_ui(
    root,
    back,
):

    # ========================================================
    # CLEAR UI
    # ========================================================

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(
        bg="#0b1120",
    )

    # ========================================================
    # CARD
    # ========================================================

    frame = tk.Frame(
        root,
        bg="#111827",
        padx=45,
        pady=45,
    )

    frame.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
    )

    # ========================================================
    # TITLE
    # ========================================================

    tk.Label(
        frame,
        text="COMBO",
        bg="#111827",
        fg="#f8fafc",
        font=("Segoe UI", 20, "bold"),
    ).pack(
        pady=(0, 8),
    )

    # ========================================================
    # DESCRIPTION
    # ========================================================

    tk.Label(
        frame,
        text="Tính năng đang được phát triển",
        bg="#111827",
        fg="#94a3b8",
        font=("Segoe UI", 10),
    ).pack(
        pady=(0, 25),
    )

    # ========================================================
    # BACK BUTTON
    # ========================================================

    tk.Button(
        frame,
        text="QUAY LẠI",
        command=back,
        bg="#2563eb",
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=28,
        pady=10,
        cursor="hand2",
        font=("Segoe UI", 9, "bold"),
    ).pack()