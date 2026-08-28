import tkinter as tk
from tkinter import messagebox

import MetaTrader5 as mt5

from .chart_module import (
    draw_chart,
    start_auto,
    stop_auto,
    detect_symbol
)


# ============================================================
# COLORS
# ============================================================

BG = "#080f24"

CARD = "#111a32"
CARD_2 = "#16213d"

BORDER = "#263657"

TEXT = "#e5e7eb"
TEXT_MUTED = "#94a3b8"

BLUE = "#2563eb"
GREEN = "#22c55e"
RED = "#ef4444"
ORANGE = "#f97316"

YELLOW = "#facc15"


# ============================================================
# MAIN UI
# ============================================================

def show_trend_ui(root, back, login_data=None):
    login_data = login_data or {}
    # ========================================================
    # ACCOUNT PERFORMANCE
    # ========================================================

    account_info = mt5.account_info()

    if account_info is not None:
        initial_balance_value = float(account_info.balance)
        account_currency = account_info.currency
    else:
        initial_balance_value = 0.0
        account_currency = ""

    username = login_data.get("username")
    license_days = login_data.get("licenseDays", 0)
    license_expired_dt = login_data.get("licenseExpiredDt")
    # ========================================================
    # CLEAR ROOT
    # ========================================================

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(
        bg="#080F24"
    )

    # ========================================================
    # MAIN CONTAINER
    # ========================================================

    container = tk.Frame(
        root,
        bg="#080F24"
    )

    container.pack(
        fill="both",
        expand=False,
        padx=10,
        pady=8
    )

    # ========================================================
    # HEADER
    # ========================================================

    header = tk.Frame(
        container,
        bg="#080F24"
    )

    header.pack(
        fill="x",
        pady=(2, 10)
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title_frame = tk.Frame(
        header,
        bg="#080F24"
    )

    title_frame.pack(
        side="left"
    )

    tk.Label(
        title_frame,
        text="FOREX BOT PRO",
        bg="#080F24",
        fg=TEXT,
        font=("Arial", 17, "bold")
    ).pack(
        side="left"
    )

    tk.Label(
        title_frame,
        text="   v3.4 | Commercial Edition",
        bg="#080F24",
        fg="#5b7b9e",
        font=("Arial", 9, "bold")
    ).pack(
        side="left",
        pady=(5, 0)
    )

    # --------------------------------------------------------
    # HEADER RIGHT
    # --------------------------------------------------------

    header_right = tk.Frame(
        header,
        bg="#080F24"
    )

    header_right.pack(
        side="right"
    )

    tk.Label(
        header_right,
        text=f"👤 {username}",
        bg="#f1f5f9",
        fg="#334155",
        font=("Arial", 9, "bold"),
        padx=10,
        pady=7
    ).pack(
        side="left",
        padx=5
    )
    # ========================================================
    # LICENSE STATUS
    # ========================================================

    if license_days > 0:

        license_status_text = "● LICENSED"
        license_status_bg = "#15803d"

    else:

        license_status_text = "● LICENSE EXPIRED"
        license_status_bg = "#b91c1c"


    tk.Label(
        header_right,
        text=license_status_text,
        bg=license_status_bg,
        fg="white",
        font=("Arial", 9, "bold"),
        padx=15,
        pady=7
    ).pack(
        side="left",
        padx=5
    )

    tk.Label(
        header_right,
        text=f"Còn {license_days} Ngày",
        bg="#9a4f14",
        fg="white",
        font=("Arial", 9, "bold"),
        padx=15,
        pady=7
    ).pack(
        side="left"
    )
    # ========================================================
    # CONTENT
    # ========================================================

    content = tk.Frame(
        container,
        bg="#080F24"
    )

    content.pack(
        fill="x",
        expand=False
    )
    # ========================================================
    # SECTION HELPER
    # ========================================================

    def create_section(
        number,
        title
    ):

        section = tk.Frame(
            content,
            bg="#080F24"
        )

        section.pack(
            fill="x",
            pady=(0, 14)
        )

        tk.Label(
            section,
            text=f"{number}. {title}",
            bg="#080F24",
            fg="#4da3d8",
            font=("Arial", 11, "bold")
        ).pack(
            anchor="w",
            padx=8,
            pady=(0, 7)
        )

        card = tk.Frame(
            section,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        card.pack(
            fill="x"
        )

        return card

    # ========================================================
    # 1. ACCOUNT OVERVIEW
    # ========================================================

    account_card = create_section(
        1,
        "TỔNG QUAN TÀI KHOẢN"
    )

    account_inner = tk.Frame(
        account_card,
        bg=CARD_2
    )

    account_inner.pack(
        fill="x",
        padx=8,
        pady=8
    )

    account_inner.grid_columnconfigure(
        0,
        weight=1
    )

    account_inner.grid_columnconfigure(
        1,
        weight=1
    )

    # ========================================================
    # LEFT ACCOUNT
    # ========================================================

    left_account = tk.Frame(
        account_inner,
        bg=CARD_2
    )

    left_account.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=10,
        pady=4
    )
    # --------------------------------------------------------
    # ACCOUNT PERFORMANCE
    # --------------------------------------------------------

    performance_frame = tk.Frame(
        account_inner,
        bg=CARD_2
    )

    performance_frame.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=10,
        pady=8
    )

    initial_balance_label = tk.Label(
        performance_frame,
        text=f"Vốn ban đầu: {initial_balance_value:.2f} {account_currency}",
        bg=CARD_2,
        fg="#75b8d6",
        font=("Arial", 9, "bold")
    )

    initial_balance_label.pack(
        side="left",
        padx=(0, 20)
    )

    current_balance_label = tk.Label(
        performance_frame,
        text=f"Số dư: {initial_balance_value:.2f} {account_currency}",
        bg=CARD_2,
        fg=TEXT,
        font=("Arial", 9, "bold")
    )

    current_balance_label.pack(
        side="left",
        padx=(0, 20)
    )

    profit_label = tk.Label(
        performance_frame,
        text=f"P/L: +0.00 {account_currency} (+0.00%)",
        bg="#071b17",
        fg=GREEN,
        font=("Arial", 9, "bold"),
        padx=10,
        pady=5
    )

    profit_label.pack(
        side="left"
    )
    tk.Label(
        left_account,
        text="Lot Ban Đầu Vào Lệnh:",
        bg=CARD_2,
        fg="#75b8d6",
        font=("Arial", 9, "bold")
    ).grid(
        row=1,
        column=0,
        sticky="w",
        pady=6
    )
    initial_lot = tk.Entry(
        left_account,
        bg="#080f24",
        fg=TEXT,
        insertbackground="white",
        relief="flat",
        justify="center",
        width=14
    )

    initial_lot.insert(
        0,
        "0.01"
    )

    initial_lot.grid(
        row=1,
        column=1,
        sticky="w",
        padx=15
    )

    # ========================================================
    # RIGHT ACCOUNT
    # ========================================================

    right_account = tk.Frame(
        account_inner,
        bg=CARD_2
    )

    right_account.grid(
        row=1,
        column=1,
        sticky="nsew",
        padx=10,
        pady=4
    )
    
        # ========================================================
    # UPDATE ACCOUNT PERFORMANCE
    # ========================================================

    def update_account_performance():

        try:

            # Nếu root đã bị destroy thì dừng
            if not root.winfo_exists():
                return

            account_info = mt5.account_info()

            if account_info is not None:

                current_balance = float(
                    account_info.balance
                )

                currency = account_info.currency

                # -----------------------------------------------
                # CURRENT BALANCE
                # -----------------------------------------------

                current_balance_label.config(
                    text=f"Số dư: {current_balance:.2f} {currency}"
                )

                # -----------------------------------------------
                # P/L
                # -----------------------------------------------

                profit = (
                    current_balance
                    - initial_balance_value
                )

                if initial_balance_value != 0:

                    profit_percent = (
                        profit
                        / initial_balance_value
                        * 100
                    )

                else:

                    profit_percent = 0.0

                sign = "+" if profit >= 0 else ""

                profit_label.config(
                    text=(
                        f"P/L: {sign}{profit:.2f} {currency} "
                        f"({sign}{profit_percent:.2f}%)"
                    ),
                    fg=(
                        GREEN
                        if profit >= 0
                        else RED
                    ),
                    bg=(
                        "#071b17"
                        if profit >= 0
                        else "#2a0d0d"
                    )
                )

        except tk.TclError:
            return

        except Exception as e:
            print(
                f"[ACCOUNT UPDATE ERROR] {e}"
            )
            return

        # Chỉ đăng ký callback tiếp theo nếu UI còn tồn tại
        try:

            if root.winfo_exists():

                root.after(
                    1000,
                    update_account_performance
                )

        except tk.TclError:
            pass
    # --------------------------------------------------------
    # RR
    # --------------------------------------------------------

    tk.Label(
        right_account,
        text="Tỷ Lệ R : R:",
        bg=CARD_2,
        fg="#75b8d6",
        font=("Arial", 9, "bold")
    ).grid(
        row=2,
        column=0,
        sticky="w",
        pady=6
    )

    rr_frame = tk.Frame(
        right_account,
        bg=CARD_2
    )

    rr_frame.grid(
        row=2,
        column=1,
        sticky="w",
        padx=15
    )

    rr_risk = tk.Entry(
        rr_frame,
        width=5,
        bg="#080f24",
        fg=TEXT,
        insertbackground="white",
        relief="flat",
        justify="center"
    )

    rr_risk.insert(
        0,
        "1.0"
    )

    rr_risk.pack(
        side="left"
    )

    tk.Label(
        rr_frame,
        text=" : ",
        bg=CARD_2,
        fg=TEXT,
        font=("Arial", 10, "bold")
    ).pack(
        side="left"
    )

    rr_reward = tk.Entry(
        rr_frame,
        width=5,
        bg="#080f24",
        fg=TEXT,
        insertbackground="white",
        relief="flat",
        justify="center"
    )

    rr_reward.insert(
        0,
        "0.9"
    )

    rr_reward.pack(
        side="left"
    )

    # ========================================================
    # LOT MANAGEMENT
    # ========================================================

    lot_frame = tk.Frame(
        account_inner,
        bg=CARD_2
    )

    lot_frame.grid(
        row=2,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=10,
        pady=(8, 5)
    )

    # --------------------------------------------------------
    # LOT MODE
    # --------------------------------------------------------

    use_lot_chain = tk.BooleanVar(
        value=False
    )

    lot_type = tk.StringVar(
        value="default"
    )

    tk.Label(
        lot_frame,
        text="Quản Lý Chuỗi Lot:",
        bg=CARD_2,
        fg="#75b8d6",
        font=("Arial", 9, "bold")
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 15)
    )

    # --------------------------------------------------------
    # CHECKBOX
    # --------------------------------------------------------

    tk.Checkbutton(
        lot_frame,
        text="Sử dụng Chuỗi Lot",
        variable=use_lot_chain,
        command=lambda: show_lot_chain(),
        bg=CARD_2,
        fg=TEXT,
        selectcolor=BG,
        activebackground=CARD_2,
        activeforeground=TEXT,
        font=("Arial", 9, "bold")
    ).grid(
        row=0,
        column=1,
        sticky="w",
        padx=5
    )

    # --------------------------------------------------------
    # LOT TYPE
    # --------------------------------------------------------

    lot_type_frame = tk.Frame(
        lot_frame,
        bg=CARD_2
    )

    lot_type_frame.grid(
        row=0,
        column=2,
        sticky="w",
        padx=15
    )

    tk.Radiobutton(
        lot_type_frame,
        text="Mặc định",
        variable=lot_type,
        value="default",
        command=lambda: show_lot_chain(),
        bg=CARD_2,
        fg=TEXT,
        selectcolor=BG,
        activebackground=CARD_2,
        activeforeground=TEXT
    ).pack(
        side="left"
    )

    tk.Radiobutton(
        lot_type_frame,
        text="Tự đặt",
        variable=lot_type,
        value="custom",
        command=lambda: show_lot_chain(),
        bg=CARD_2,
        fg=TEXT,
        selectcolor=BG,
        activebackground=CARD_2,
        activeforeground=TEXT
    ).pack(
        side="left",
        padx=10
    )

    # --------------------------------------------------------
    # DEFAULT LOT
    # 0.01 -> 0.02 -> 0.04 -> ...
    # --------------------------------------------------------

    default_lots = [
        round(0.01 * (i + 1), 2)
        for i in range(5)
    ]

    # --------------------------------------------------------
    # LOT VALUES FRAME
    # --------------------------------------------------------

    lot_values_frame = tk.Frame(
        lot_frame,
        bg=CARD_2
    )

    lot_values_frame.grid(
        row=1,
        column=0,
        columnspan=3,
        sticky="ew",
        pady=(10, 3)
    )

    for i in range(10):

        lot_values_frame.grid_columnconfigure(
            i,
            weight=1
        )

    # ========================================================
    # LOT ITEMS
    # ========================================================

    lot_items = []

    lot_entries = []

    current_lot_index = 0


    # ========================================================
    # UPDATE CURRENT LOT
    # ========================================================

    def update_current_lot(index):

        nonlocal current_lot_index

        current_lot_index = index

        # Không dùng chuỗi lot
        if not use_lot_chain.get():
            return

        # Kiểm tra index
        if index < 0:
            return

        if index >= len(default_lots):
            return

        # ====================================================
        # LẤY GIÁ TRỊ LOT HIỆN TẠI
        # ====================================================

        if lot_type.get() == "default":

            value = default_lots[index]

        else:

            try:

                value = float(
                    lot_entries[index].get()
                )

            except (ValueError, IndexError):

                return

        # ====================================================
        # CẬP NHẬT LOT BAN ĐẦU
        # ====================================================

        initial_lot.config(
            state="normal"
        )

        initial_lot.delete(
            0,
            tk.END
        )

        initial_lot.insert(
            0,
            f"{value:.2f}"
        )

        # ====================================================
        # KHÓA LOT BAN ĐẦU
        # ====================================================

        initial_lot.config(
            state="disabled"
        )

        # ====================================================
        # UPDATE HIGHLIGHT
        # ====================================================

        for i, item in enumerate(lot_items):

            if i == index:

                # Lot đang chạy
                item.config(
                    bg="#123d2b",
                    highlightbackground=GREEN,
                    highlightthickness=2
                )

                for widget in item.winfo_children():

                    widget.config(
                        bg="#123d2b"
                    )

            else:

                # Lot không chạy
                item.config(
                    bg=CARD_2,
                    highlightbackground=BORDER,
                    highlightthickness=1
                )

                for widget in item.winfo_children():

                    if isinstance(
                        widget,
                        tk.Entry
                    ):

                        widget.config(
                            bg="#080f24"
                        )

                    else:

                        widget.config(
                            bg=CARD_2
                        )


    # ========================================================
    # SHOW LOT CHAIN
    # ========================================================

    def show_lot_chain():

        # ====================================================
        # XÓA UI CŨ
        # ====================================================

        for widget in lot_values_frame.winfo_children():

            widget.destroy()

        lot_entries.clear()

        lot_items.clear()

        # ====================================================
        # KHÔNG DÙNG CHUỖI LOT
        # ====================================================

        if not use_lot_chain.get():

            lot_type_frame.grid_remove()

            lot_values_frame.grid_remove()

            # Mở khóa Lot ban đầu
            initial_lot.config(
                state="normal"
            )

            return

        # ====================================================
        # DÙNG CHUỖI LOT
        # ====================================================

        lot_type_frame.grid()

        lot_values_frame.grid()

        # ====================================================
        # DEFAULT LOT
        # ====================================================

        if lot_type.get() == "default":

            for i, value in enumerate(
                default_lots
            ):

                item = tk.Frame(
                    lot_values_frame,
                    bg=CARD_2,
                    highlightbackground=BORDER,
                    highlightthickness=1
                )

                item.grid(
                    row=0,
                    column=i,
                    sticky="ew",
                    padx=3
                )

                lot_items.append(
                    item
                )

                tk.Label(
                    item,
                    text=f"L{i + 1}",
                    bg=CARD_2,
                    fg=TEXT_MUTED,
                    font=("Arial", 8, "bold")
                ).pack()

                tk.Label(
                    item,
                    text=f"{value:.2f}",
                    bg="#080f24",
                    fg=TEXT,
                    width=7,
                    pady=4
                ).pack(
                    pady=(2, 0)
                )

        # ====================================================
        # CUSTOM LOT
        # ====================================================

        else:

            for i, value in enumerate(
                default_lots
            ):

                item = tk.Frame(
                    lot_values_frame,
                    bg=CARD_2,
                    highlightbackground=BORDER,
                    highlightthickness=1
                )

                item.grid(
                    row=0,
                    column=i,
                    sticky="ew",
                    padx=3
                )

                lot_items.append(
                    item
                )

                tk.Label(
                    item,
                    text=f"L{i + 1}",
                    bg=CARD_2,
                    fg=TEXT_MUTED,
                    font=("Arial", 8, "bold")
                ).pack()

                entry = tk.Entry(
                    item,
                    width=7,
                    bg="#080f24",
                    fg=TEXT,
                    insertbackground="white",
                    relief="flat",
                    justify="center"
                )

                entry.insert(
                    0,
                    f"{value:.2f}"
                )

                entry.pack(
                    pady=(2, 0)
                )

                lot_entries.append(
                    entry
                )

        # ====================================================
        # HIỂN THỊ LOT HIỆN TẠI
        # ====================================================

        update_current_lot(
            current_lot_index
        )


    # ========================================================
    # INITIAL LOT DISPLAY
    # ========================================================

    show_lot_chain()

    # ========================================================
    # SAFETY OPTIONS
    # ========================================================

    safety_frame = tk.Frame(
        account_inner,
        bg=CARD_2
    )

    safety_frame.grid(
        row=3,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=10,
        pady=5
    )

    be_var = tk.BooleanVar(
        value=True
    )

    trailing_var = tk.BooleanVar(
        value=True
    )

    friday_var = tk.BooleanVar(
        value=True
    )

    tk.Checkbutton(
        safety_frame,
        text="Tự Dời SL Về Entry (Hòa Vốn Tự Động)",
        variable=be_var,
        bg=CARD_2,
        fg=TEXT,
        selectcolor="#2563eb",
        activebackground=CARD_2,
        activeforeground=TEXT
    ).pack(
        side="left",
        padx=5
    )

    tk.Checkbutton(
        safety_frame,
        text="Trailing Stop Khóa Lời (>50% TP)",
        variable=trailing_var,
        bg=CARD_2,
        fg=TEXT,
        selectcolor="#2563eb",
        activebackground=CARD_2,
        activeforeground=TEXT
    ).pack(
        side="left",
        padx=20
    )

    # ========================================================
    # FRIDAY LOCK
    # ========================================================

    tk.Checkbutton(
        account_inner,
        text="Khóa Lệnh Trước Đêm Thứ 6 Hàng Tuần (Tránh Gap Cuối Tuần)",
        variable=friday_var,
        bg=CARD_2,
        fg="#f3b85f",
        selectcolor="#2563eb",
        activebackground=CARD_2,
        activeforeground="#f3b85f",
        font=("Arial", 9, "bold")
    ).grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="w",
        padx=10,
        pady=5
    )

    # ========================================================
    # STATUS
    # ========================================================

    status_box = tk.Label(
        account_inner,
        text=(
            "Trạng thái: An toàn • "
            "Tự động tính toán khối lượng theo số dư khả dụng"
        ),
        bg="#07152c",
        fg=TEXT_MUTED,
        anchor="w",
        padx=12,
        pady=8
    )

    status_box.grid(
        row=5,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=10,
        pady=(5, 8)
    )

    # ========================================================
    # 2. STRATEGY
    # ========================================================

    strategy_card = create_section(
        2,
        "PHƯƠNG PHÁP GỢI Ý (LỰA CHỌN CHIẾN LƯỢC)"
    )

    strategy_frame = tk.Frame(
        strategy_card,
        bg=CARD
    )

    strategy_frame.pack(
        fill="x",
        padx=8,
        pady=8
    )

    strategy_frame.grid_columnconfigure(
        0,
        weight=1
    )

    strategy_frame.grid_columnconfigure(
        1,
        weight=1
    )


    # ========================================================
    # STRATEGY STATE
    # ========================================================

    selected_strategy = tk.StringVar(
        value="low"
    )

    low_config = tk.StringVar(
        value="default"
    )

    high_config = tk.StringVar(
        value="default"
    )


    # ========================================================
    # DEFAULT CONFIG - LOW PROFIT
    # ========================================================

    LOW_DEFAULT_CONFIG = {

        "ma_cross": True,
        "ma_fast": 9,
        "ma_slow": 21,

        "ma_trend": True,
        "ma_value": 200,

        "sideway_filter": True,
        "anti_fomo": True
    }


    # ========================================================
    # DEFAULT CONFIG - HIGH PROFIT
    # ========================================================

    HIGH_DEFAULT_CONFIG = {

        "ma_cross": True,
        "ma_fast": 9,
        "ma_slow": 21,

        "ma_trend": False,
        "ma_value": 0,

        "sideway_filter": True,
        "anti_fomo": True
    }


    # ========================================================
    # CUSTOM CONFIG
    # ========================================================

    low_custom_config = LOW_DEFAULT_CONFIG.copy()

    high_custom_config = HIGH_DEFAULT_CONFIG.copy()


    # ========================================================
    # EXPERT POPUP
    # ========================================================

    def open_expert_popup(
        strategy,
        editable=False
    ):

        # ====================================================
        # CONFIG SOURCE
        # ====================================================

        if strategy == "low":

            config = (
                low_custom_config
                if editable
                else LOW_DEFAULT_CONFIG
            )

            title = (
                "TÙY CHỈNH THAM SỐ CHUYÊN GIA\n"
                "PHƯƠNG PHÁP LỢI NHUẬN THẤP"
            )

        else:

            config = (
                high_custom_config
                if editable
                else HIGH_DEFAULT_CONFIG
            )

            title = (
                "TÙY CHỈNH THAM SỐ CHUYÊN GIA\n"
                "PHƯƠNG PHÁP LỢI NHUẬN CAO"
            )

        # ====================================================
        # EXPERT POPUP UI
        # ====================================================

        popup = tk.Toplevel(root)

        popup.overrideredirect(True)

        popup.configure(
            bg="#00AEEF"
        )

        popup.transient(root)

        popup.lift()
        popup.focus_force()

        POPUP_W = 620
        POPUP_H = 500

        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()

        x = (screen_w - POPUP_W) // 2
        y = (screen_h - POPUP_H) // 2

        popup.geometry(
            f"{POPUP_W}x{POPUP_H}+{x}+{y}"
        )
        popup.lift()
        popup.focus_force()

        # ====================================================
        # OUTER BORDER
        # ====================================================

        outer = tk.Frame(
            popup,
            bg="#00AEEF"
        )

        outer.pack(
            fill="both",
            expand=True,
            padx=2,
            pady=2
        )

        # ====================================================
        # MAIN CONTAINER
        # ====================================================

        main = tk.Frame(
            outer,
            bg="#080F24"
        )

        main.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # HEADER
        # ====================================================

        # ====================================================
        # HEADER
        # ====================================================

        header = tk.Frame(
            main,
            bg="#182440",
            height=62
        )

        header.pack(
            fill="x",
            padx=10,
            pady=(10, 0)
        )

        header.pack_propagate(False)

        title_text = (
            "TÙY CHỈNH THAM SỐ CHUYÊN GIA (EXPERT MODE)"
        )

        title_label = tk.Label(
            header,
            text=title_text,
            bg="#182440",
            fg="#F8FAFC",
            font=("Arial", 11, "bold"),
            anchor="w"
        )

        title_label.pack(
            side="left",
            padx=18
        )

        # ====================================================
        # CLOSE BUTTON
        # ====================================================

        close_btn = tk.Button(
            header,
            text="×",
            command=popup.destroy,
            bg="#334155",
            fg="#E2E8F0",
            activebackground="#475569",
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            font=("Arial", 12, "bold"),
            width=3,
            cursor="hand2"
        )

        close_btn.pack(
            side="right",
            padx=12
        )

        # ====================================================
        # BODY
        # ====================================================

        # ====================================================
        # BODY
        # ====================================================

        body = tk.Frame(
            main,
            bg="#080F24"
        )

        body.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=18
        )

        body.grid_columnconfigure(
            0,
            weight=1
        )

        body.grid_columnconfigure(
            1,
            weight=0
        )

        body.grid_columnconfigure(
            2,
            weight=0
        )

        # ====================================================
        # VARIABLES
        # ====================================================
        sideway_var = tk.BooleanVar(
            value=config["sideway_filter"]
        )

        fomo_var = tk.BooleanVar(
            value=config["anti_fomo"]
        )

        # ====================================================
        # MA TREND
        # CHỈ CÓ LOW
        # ====================================================

        ma_trend_entry = None

        if strategy == "low":

            tk.Label(
                body,
                text="MA Trend (Xu hướng lớn):",
                bg="#080F24",
                fg=TEXT,
                font=("Arial", 9, "bold")
            ).grid(
                row=0,
                column=0,
                sticky="w",
                pady=10
            )

            tk.Label(
                body,
                text="Chu kỳ:",
                bg="#080F24",
                fg=TEXT_MUTED,
                font=("Arial", 9)
            ).grid(
                row=0,
                column=1,
                sticky="e",
                padx=10
            )

            ma_trend_entry = tk.Entry(
                body,
                width=8,
                bg="#101A32",
                fg="#F8FAFC",
                insertbackground="white",
                justify="center",
                relief="flat",
                highlightthickness=1,
                highlightbackground="#263653",
                highlightcolor="#2563EB",
                font=("Arial", 10, "bold")
            )

            ma_trend_entry.insert(
                0,
                str(
                    config["ma_value"]
                )
            )

            ma_trend_entry.grid(
                row=0,
                column=2,
                sticky="w"
            )

            current_row = 1

        else:

            current_row = 0

        # ====================================================
        # MA CROSS
        # ====================================================

        tk.Label(
            body,
            text="MA Cross Tín Hiệu:",
            bg="#080F24",
            fg=TEXT,
            font=("Arial", 9, "bold")
        ).grid(
            row=current_row,
            column=0,
            sticky="w",
            pady=10
        )

        tk.Label(
            body,
            text="Fast:",
            bg="#080F24",
            fg=TEXT_MUTED
        ).grid(
            row=current_row,
            column=1,
            sticky="e",
            padx=5
        )

        ma_fast_entry = tk.Entry(
            body,
            width=7,
            bg="#101A32",
            fg="#F8FAFC",
            insertbackground="white",
            justify="center",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#263653",
            highlightcolor="#2563EB",
            font=("Arial", 10, "bold")
        )

        ma_fast_entry.insert(
            0,
            str(
                config["ma_fast"]
            )
        )

        ma_fast_entry.grid(
            row=current_row,
            column=2,
            sticky="w"
        )

        tk.Label(
            body,
            text="Slow:",
            bg="#080F24",
            fg=TEXT_MUTED
        ).grid(
            row=current_row + 1,
            column=1,
            sticky="e",
            padx=5
        )

        ma_slow_entry = tk.Entry(
            body,
            width=7,
            bg="#101A32",
            fg="#F8FAFC",
            insertbackground="white",
            justify="center",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#263653",
            highlightcolor="#2563EB",
            font=("Arial", 10, "bold")
        )

        ma_slow_entry.insert(
            0,
            str(
                config["ma_slow"]
                if "ma_slow" in config
                else config["ma_slow"]
            )
        )

        ma_slow_entry.grid(
            row=current_row + 1,
            column=2,
            sticky="w"
        )

        # ====================================================
        # SIDEWAY
        # ====================================================

        sideway_row = current_row + 2

        # ====================================================
        # SIDEWAY
        # ====================================================

        # ====================================================
        # SIDEWAY
        # ====================================================

        if editable:

            sideway_check = tk.Checkbutton(
                body,
                text="AI Lọc Thị Trường Đi Ngang (Sideway Range)",
                variable=sideway_var,
                bg="#080F24",
                fg="#E2E8F0",
                selectcolor="#2563EB",
                activebackground="#080F24",
                activeforeground="#FFFFFF",
                font=("Arial", 9),
                anchor="w",
                relief="flat",
                borderwidth=0,
                highlightthickness=0
            )

        else:

            sideway_check = tk.Label(
                body,
                text="✓ AI Lọc Thị Trường Đi Ngang (Sideway Range)",
                bg="#080F24",
                fg=GREEN,
                font=("Arial", 9, "bold"),
                anchor="w"
            )

        sideway_check.grid(
            row=sideway_row,
            column=0,
            columnspan=2,
            sticky="w",
            pady=8
        )


        tk.Label(
            body,
            text="AI ACTIVE",
            bg="#3159A8",
            fg="#EAF2FF",
            padx=12,
            pady=5,
            font=("Arial", 8, "bold")
        ).grid(
            row=sideway_row,
            column=2,
            sticky="w"
        )

        # ====================================================
        # FOMO
        # ====================================================

        fomo_row = sideway_row + 1

        # ====================================================
        # FOMO
        # ====================================================

        # ====================================================
        # FOMO
        # ====================================================

        if editable:

            fomo_check = tk.Checkbutton(
                body,
                text="AI Lọc Chống Đánh Đuổi Giá (Anti FOMO Filter)",
                variable=fomo_var,
                bg="#080F24",
                fg="#E2E8F0",
                selectcolor="#2563EB",
                activebackground="#080F24",
                activeforeground="#FFFFFF",
                font=("Arial", 9),
                anchor="w",
                relief="flat",
                borderwidth=0,
                highlightthickness=0
            )

        else:

            fomo_check = tk.Label(
                body,
                text="✓ AI Lọc Chống Đánh Đuổi Giá (Anti FOMO Filter)",
                bg="#080F24",
                fg=GREEN,
                font=("Arial", 9, "bold"),
                anchor="w"
            )

        fomo_check.grid(
            row=fomo_row,
            column=0,
            columnspan=2,
            sticky="w",
            pady=8
        )
        # ====================================================
        sideway_var.set(
            bool(config["sideway_filter"])
        )

        fomo_var.set(
            bool(config["anti_fomo"])
        )
        tk.Label(
            body,
            text="AI ACTIVE",
            bg="#3159a8",
            fg="white",
            padx=10,
            pady=4,
            font=("Arial", 8, "bold")
        ).grid(
            row=fomo_row,
            column=2,
            sticky="w"
        )

        # ====================================================
        # DEFAULT = READ ONLY
        # ====================================================

        # ====================================================
        # DEFAULT = READ ONLY
        # ====================================================

        if not editable:

            # ====================================================
            # MA READ ONLY
            # ====================================================

            if ma_trend_entry:
                ma_trend_entry.config(
                    state="disabled"
                )

            ma_fast_entry.config(
                state="disabled"
            )

            ma_slow_entry.config(
                state="disabled"
            )

            # ====================================================
            # SIDEWAY + FOMO
            # VẪN HIỆN TICK NHƯNG KHÔNG CHO CLICK
            # ====================================================

            sideway_check.bind(
                "<Button-1>",
                lambda event: "break"
            )

            fomo_check.bind(
                "<Button-1>",
                lambda event: "break"
            )        # ====================================================
        # BUTTON FRAME
        # ====================================================

        button_frame = tk.Frame(
            main,
            bg="#080F24"
        )

        button_frame.pack(
            side="bottom",
            pady=(5, 25)
        )

        # ====================================================
        # RESET
        # ====================================================

        def reset_config():

            defaults = (
                LOW_DEFAULT_CONFIG
                if strategy == "low"
                else HIGH_DEFAULT_CONFIG
            )

            # MA TREND
            if ma_trend_entry:

                ma_trend_entry.config(
                    state="normal"
                )

                ma_trend_entry.delete(
                    0,
                    tk.END
                )

                ma_trend_entry.insert(
                    0,
                    str(
                        defaults["ma_value"]
                    )
                )

            # MA CROSS
            ma_fast_entry.config(
                state="normal"
            )

            ma_fast_entry.delete(
                0,
                tk.END
            )

            ma_fast_entry.insert(
                0,
                str(
                    defaults["ma_fast"]
                )
            )

            ma_slow_entry.config(
                state="normal"
            )

            ma_slow_entry.delete(
                0,
                tk.END
            )

            ma_slow_entry.insert(
                0,
                str(
                    defaults["ma_slow"]
                )
            )

            # FILTER
            sideway_var.set(
                defaults["sideway_filter"]
            )

            fomo_var.set(
                defaults["anti_fomo"]
            )

            # LOCK AGAIN
            if not editable:

                if ma_trend_entry:

                    ma_trend_entry.config(
                        state="disabled"
                    )

                ma_fast_entry.config(
                    state="disabled"
                )

                ma_slow_entry.config(
                    state="disabled"
                )

                

        # ====================================================
        # SAVE
        # ====================================================

        def save_config():

            try:

                new_config = {

                    # MA CROSS
                    "ma_cross": True,

                    "ma_fast":
                        int(
                            ma_fast_entry.get()
                        ),

                    "ma_slow":
                        int(
                            ma_slow_entry.get()
                        ),

                    # MA TREND
                    "ma_trend":
                        strategy == "low",

                    "ma_value":
                        int(
                            ma_trend_entry.get()
                        )
                        if ma_trend_entry
                        else 0,

                    # FILTER
                    "sideway_filter":
                        sideway_var.get(),

                    "anti_fomo":
                        fomo_var.get()
                }

            except ValueError:

                messagebox.showerror(
                    "Lỗi",
                    "Vui lòng nhập đúng thông số.",
                    parent=popup
                )

                return

            # ==================================================
            # SAVE LOW
            # ==================================================

            if strategy == "low":

                low_custom_config.clear()

                low_custom_config.update(
                    new_config
                )

                low_config.set(
                    "custom"
                )

            # ==================================================
            # SAVE HIGH
            # ==================================================

            else:

                high_custom_config.clear()

                high_custom_config.update(
                    new_config
                )

                high_config.set(
                    "custom"
                )

            popup.destroy()

            # Đánh dấu nút Tự cài đặt
            if strategy == "low":

                low_default_btn.config(
                    bg="#26334f"
                )

                low_custom_btn.config(
                    bg=BLUE,
                    fg="white"
                )

            else:

                high_default_btn.config(
                    bg="#26334f"
                )

                high_custom_btn.config(
                    bg=BLUE,
                    fg="white"
                )

        # ====================================================
        # RESET BUTTON
        # ====================================================

        if editable:

            tk.Button(
                button_frame,
                text="ĐẶT LẠI",
                width=15,
                height=2,
                bg="#334155",
                fg="#F8FAFC",
                activebackground="#475569",
                activeforeground="white",
                relief="flat",
                borderwidth=0,
                font=("Arial", 9, "bold"),
                cursor="hand2",
                command=reset_config
            ).pack(
                side="left",
                padx=10
            )

            tk.Button(
                button_frame,
                text="LƯU CẤU HÌNH",
                width=17,
                height=2,
                bg="#22C55E",
                fg="white",
                activebackground="#16A34A",
                activeforeground="white",
                relief="flat",
                borderwidth=0,
                font=("Arial", 9, "bold"),
                cursor="hand2",
                command=save_config
            ).pack(
                side="left",
                padx=10
            )

        else:

            tk.Button(
                button_frame,
                text="ĐÓNG",
                width=17,
                height=2,
                bg="#334155",
                fg="#F8FAFC",
                activebackground="#475569",
                activeforeground="white",
                relief="flat",
                borderwidth=0,
                font=("Arial", 9, "bold"),
                cursor="hand2",
                command=popup.destroy
            ).pack(
                side="left",
                padx=10
            )


    # ========================================================
    # LOW PROFIT CARD
    # ========================================================

    low_card = tk.Frame(
        strategy_frame,
        bg="#101b38",
        highlightbackground=BORDER,
        highlightthickness=1
    )

    low_card.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 5)
    )

    tk.Label(
        low_card,
        text="PHƯƠNG PHÁP LỢI NHUẬN THẤP",
        bg="#101b38",
        fg=TEXT,
        font=("Arial", 10, "bold")
    ).pack(
        anchor="w",
        padx=12,
        pady=(10, 2)
    )

    tk.Label(
        low_card,
        text="",
        bg="#101b38",
        fg="#f0a84b",
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        padx=12
    )

    low_select_btn = tk.Button(
        low_card,
        text="✓ ĐÃ CHỌN",
        bg=GREEN,
        fg="white",
        activebackground="#16a34a",
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        font=("Arial", 9, "bold"),
        command=lambda: select_strategy("low")
    )

    low_select_btn.pack(
        anchor="w",
        padx=12,
        pady=8
    )

    low_options = tk.Frame(
        low_card,
        bg="#101b38"
    )

    low_options.pack(
        fill="x",
        padx=12,
        pady=(0, 12)
    )

    low_default_btn = tk.Button(
        low_options,
        text="Mặc định",
        width=14,
        bg=BLUE,
        fg="white",
        activebackground=BLUE,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        state="normal",
        command=lambda: select_low_config("default")
    )

    low_default_btn.pack(
        side="left",
        padx=(0, 8)
    )

    low_custom_btn = tk.Button(
        low_options,
        text="Tự cài đặt",
        width=14,
        bg="#26334f",
        fg=TEXT,
        activebackground=BLUE,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        state="normal",
        command=lambda: select_low_config("custom")
    )

    low_custom_btn.pack(
        side="left"
    )


    # ========================================================
    # HIGH PROFIT CARD
    # ========================================================

    high_card = tk.Frame(
        strategy_frame,
        bg="#101b38",
        highlightbackground=BORDER,
        highlightthickness=1
    )

    high_card.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(5, 0)
    )

    tk.Label(
        high_card,
        text="PHƯƠNG PHÁP LỢI NHUẬN CAO",
        bg="#101b38",
        fg=TEXT,
        font=("Arial", 10, "bold")
    ).pack(
        anchor="w",
        padx=12,
        pady=(10, 2)
    )

    tk.Label(
        high_card,
        text="",
        bg="#101b38",
        fg="#f0a84b",
        font=("Arial", 9, "bold")
    ).pack(
        anchor="w",
        padx=12
    )

    high_select_btn = tk.Button(
        high_card,
        text="CHỌN PHƯƠNG PHÁP",
        bg="#26334f",
        fg=TEXT,
        activebackground=BLUE,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        font=("Arial", 9, "bold"),
        command=lambda: select_strategy("high")
    )

    high_select_btn.pack(
        anchor="w",
        padx=12,
        pady=8
    )

    high_options = tk.Frame(
        high_card,
        bg="#101b38"
    )

    high_options.pack(
        fill="x",
        padx=12,
        pady=(0, 12)
    )

    high_default_btn = tk.Button(
        high_options,
        text="Mặc định",
        width=14,
        bg="#26334f",
        fg=TEXT,
        activebackground=BLUE,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        state="disabled",
        command=lambda: select_high_config("default")
    )

    high_default_btn.pack(
        side="left",
        padx=(0, 8)
    )

    high_custom_btn = tk.Button(
        high_options,
        text="Tự cài đặt",
        width=14,
        bg="#26334f",
        fg=TEXT,
        activebackground=BLUE,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        state="disabled",
        command=lambda: select_high_config("custom")
    )

    high_custom_btn.pack(
        side="left"
    )


    # ========================================================
    # SELECT MAIN STRATEGY
    # ========================================================

    def select_strategy(strategy):

        selected_strategy.set(
            strategy
        )

        if strategy == "low":

            low_card.config(
                highlightbackground=BLUE,
                highlightthickness=2
            )

            high_card.config(
                highlightbackground=BORDER,
                highlightthickness=1
            )

            low_select_btn.config(
                text="✓ ĐÃ CHỌN",
                bg=GREEN
            )

            high_select_btn.config(
                text="CHỌN PHƯƠNG PHÁP",
                bg="#26334f"
            )

            low_default_btn.config(
                state="normal"
            )

            low_custom_btn.config(
                state="normal"
            )

            high_default_btn.config(
                state="disabled"
            )

            high_custom_btn.config(
                state="disabled"
            )

        else:

            high_card.config(
                highlightbackground=BLUE,
                highlightthickness=2
            )

            low_card.config(
                highlightbackground=BORDER,
                highlightthickness=1
            )

            high_select_btn.config(
                text="✓ ĐÃ CHỌN",
                bg=GREEN
            )

            low_select_btn.config(
                text="CHỌN PHƯƠNG PHÁP",
                bg="#26334f"
            )

            high_default_btn.config(
                state="normal"
            )

            high_custom_btn.config(
                state="normal"
            )

            low_default_btn.config(
                state="disabled"
            )

            low_custom_btn.config(
                state="disabled"
            )


    # ========================================================
    # LOW CONFIG
    # ========================================================

    def select_low_config(config):

        low_config.set(
            config
        )

        if config == "default":

            low_default_btn.config(
                bg=BLUE,
                fg="white"
            )

            low_custom_btn.config(
                bg="#26334f",
                fg=TEXT
            )

            # MỞ POPUP MẶC ĐỊNH - KHÔNG CHO SỬA
            open_expert_popup(
                "low",
                editable=False
            )

        elif config == "custom":

            low_custom_btn.config(
                bg=BLUE,
                fg="white"
            )

            low_default_btn.config(
                bg="#26334f",
                fg=TEXT
            )

            # MỞ POPUP CUSTOM - CHO SỬA
            open_expert_popup(
                "low",
                editable=True
            )            

        


    # ========================================================
    # HIGH CONFIG
    # ========================================================

    def select_high_config(config):

        high_config.set(
            config
        )

        if config == "default":

            high_default_btn.config(
                bg=BLUE,
                fg="white"
            )

            high_custom_btn.config(
                bg="#26334f",
                fg=TEXT
            )

            # MỞ POPUP MẶC ĐỊNH - KHÔNG CHO SỬA
            open_expert_popup(
                "high",
                editable=False
            )

        elif config == "custom":

            high_custom_btn.config(
                bg=BLUE,
                fg="white"
            )

            high_default_btn.config(
                bg="#26334f",
                fg=TEXT
            )

            # MỞ POPUP CUSTOM - CHO SỬA
            open_expert_popup(
                "high",
                editable=True
            )


    # ========================================================
    # DEFAULT STRATEGY
    # ========================================================

    # ========================================================
    # DEFAULT STRATEGY
    # ========================================================

    selected_strategy.set(
        "low"
    )

    low_config.set(
        "default"
    )

    high_config.set(
        "default"
    )


    # LOW CARD = SELECTED

    low_card.config(
        highlightbackground=BLUE,
        highlightthickness=2
    )

    high_card.config(
        highlightbackground=BORDER,
        highlightthickness=1
    )


    # LOW MAIN BUTTON

    low_select_btn.config(
        text="✓ ĐÃ CHỌN",
        bg=GREEN
    )

    high_select_btn.config(
        text="CHỌN PHƯƠNG PHÁP",
        bg="#26334f"
    )


    # LOW CONFIG BUTTON

    low_default_btn.config(
        bg=BLUE,
        fg="white",
        state="normal"
    )

    low_custom_btn.config(
        bg="#26334f",
        fg=TEXT,
        state="normal"
    )


    # HIGH CONFIG DISABLED

    high_default_btn.config(
        bg="#26334f",
        fg=TEXT,
        state="disabled"
    )

    high_custom_btn.config(
        bg="#26334f",
        fg=TEXT,
        state="disabled"
    )
    # ========================================================
    # 3. QUICK ACTION
    # ========================================================

    action_card = create_section(
        3,
        "BẢNG THAO TÁC LỆNH NHANH"
    )

    action_frame = tk.Frame(
        action_card,
        bg=CARD
    )

    action_frame.pack(
        fill="x",
        padx=15,
        pady=8
    )

    action_frame.grid_columnconfigure(
        0,
        weight=1
    )

    action_frame.grid_columnconfigure(
        1,
        weight=1
    )

    action_frame.grid_columnconfigure(
        2,
        weight=1
    )

    # ========================================================
    # LOG
    # ========================================================


    def write_log(msg, color="white"):
        pass

    # ========================================================
    # BOT STATUS
    # ========================================================

    status_label = tk.Label(
        action_card,
        text="● Đã dừng",
        bg=CARD,
        fg=GREEN,
        font=("Arial", 9, "bold")
    )

    status_label.pack(
        anchor="w",
        padx=15,
        pady=(0, 5)
    )

    # ========================================================
    # START
    # ========================================================

    def start_ui():

        success = start_auto(
            write_log,
            get_active,
            close_all
        )

        if not success:
            return

        status_label.config(
            text="● ĐANG CHẠY AUTO",
            fg=RED
        )
    

    # ========================================================
    # STOP
    # ========================================================

    def stop_ui():

        confirm = messagebox.askyesno(
            "Xác nhận",
            "Bạn có muốn tắt Auto Trade không?\n"
            "Tất cả lệnh hiện tại sẽ được đóng!"
        )

        if not confirm:
            return

        stop_auto(
            write_log
        )

        status_label.config(
            text="● Đã dừng",
            fg=GREEN
        )

    # ========================================================
    # CLOSE ALL
    # ========================================================
    def close_all():
        try:
            stop_auto(write_log)
        except:
            pass

        try:
            mt5.shutdown()
        except:
            pass

        root.destroy()
    

    # ========================================================
    # START BUTTON
    # ========================================================

    tk.Button(
        action_frame,
        text="▶ START BOT",
        command=start_ui,
        bg=GREEN,
        fg="white",
        activebackground="#16a34a",
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        font=("Arial", 10, "bold"),
        height=2
    ).grid(
        row=0,
        column=0,
        sticky="ew",
        padx=5
    )

    # ========================================================
    # STOP BUTTON
    # ========================================================

    tk.Button(
        action_frame,
        text="■ STOP BOT",
        command=stop_ui,
        bg=RED,
        fg="white",
        activebackground="#dc2626",
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        font=("Arial", 10, "bold"),
        height=2
    ).grid(
        row=0,
        column=1,
        sticky="ew",
        padx=5
    )

    # ========================================================
    # CLOSE ALL BUTTON
    # ========================================================

    tk.Button(
        action_frame,
        text="✕ CLOSE ALL",
        command=close_all,
        bg=ORANGE,
        fg="white",
        activebackground="#ea580c",
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        font=("Arial", 10, "bold"),
        height=2
    ).grid(
        row=0,
        column=2,
        sticky="ew",
        padx=5
    )

    # ========================================================
    # BOT CONFIG
    # ========================================================

    # ========================================================
    # BOT CONFIG
    # ========================================================

    def get_active():

        # ====================================================
        # 1. LOT
        # ====================================================

        if use_lot_chain.get():

            if lot_type.get() == "default":

                lots = default_lots.copy()

            else:

                lots = []

                for entry in lot_entries:

                    try:

                        value = float(
                            entry.get()
                        )

                        lots.append(value)

                    except (ValueError, TypeError):

                        lots.append(0.0)

        else:

            lots = []


        # ====================================================
        # 2. NORMAL LOT
        # ====================================================

        try:

            normal_lot = float(
                initial_lot.get()
                or 0.01
            )

        except (ValueError, TypeError):

            normal_lot = 0.01


        # ====================================================
        # 3. RR
        # ====================================================

        try:

            rr_risk_value = float(
                rr_risk.get()
                or 1.0
            )

        except (ValueError, TypeError):

            rr_risk_value = 1.0


        try:

            rr_reward_value = float(
                rr_reward.get()
                or 0.9
            )

        except (ValueError, TypeError):

            rr_reward_value = 0.9


        # ====================================================
        # 4. XÁC ĐỊNH CẤU HÌNH CHIẾN LƯỢC
        # ====================================================

        strategy = selected_strategy.get()


        # ====================================================
        # 5. LẤY CONFIG
        # ====================================================

        if strategy == "low":

            # -----------------------------------------------
            # LOW - DEFAULT
            # -----------------------------------------------

            if low_config.get() == "default":

                strategy_config = LOW_DEFAULT_CONFIG.copy()

            # -----------------------------------------------
            # LOW - CUSTOM
            # -----------------------------------------------

            else:

                strategy_config = low_custom_config.copy()


        else:

            # -----------------------------------------------
            # HIGH - DEFAULT
            # -----------------------------------------------

            if high_config.get() == "default":

                strategy_config = HIGH_DEFAULT_CONFIG.copy()

            # -----------------------------------------------
            # HIGH - CUSTOM
            # -----------------------------------------------

            else:

                strategy_config = high_custom_config.copy()


        # ====================================================
        # 6. LẤY POSITION HIỆN TẠI
        # ====================================================

        symbol = detect_symbol()

        positions = None

        if symbol:

            positions = mt5.positions_get(
                symbol=symbol
            )


        # ====================================================
        # 7. BUILD CONFIG
        # ====================================================

        return {

            # ==================================================
            # STRATEGY
            # ==================================================

            "strategy":
                strategy,

            "strategy_config":
                low_config.get()
                if strategy == "low"
                else high_config.get(),


            # ==================================================
            # MA CROSS
            # ==================================================

            "ma_cross":
                bool(
                    strategy_config.get(
                        "ma_cross",
                        True
                    )
                ),

            "ma_fast":
                int(
                    strategy_config.get(
                        "ma_fast",
                        9
                    )
                ),

            "ma_slow":
                int(
                    strategy_config.get(
                        "ma_slow",
                        21
                    )
                ),


            # ==================================================
            # MA TREND
            # ==================================================

            "ma_trend":
                bool(
                    strategy_config.get(
                        "ma_trend",
                        False
                    )
                ),

            "ma_value":
                int(
                    strategy_config.get(
                        "ma_value",
                        0
                    )
                ),


            # ==================================================
            # EMA CUSTOM
            # Không dùng trong 2 phương pháp hiện tại
            # ==================================================

            "ema_custom":
                False,

            "ema_value":
                50,


            # ==================================================
            # ORDER
            # ==================================================

            "buy_limit":
                False,

            "dca":
                False,


            # ==================================================
            # TRAILING
            # ==================================================

            "trailing":
                trailing_var.get(),


            # ==================================================
            # BUFFER
            # ==================================================

            "buffer":
                10,


            # ==================================================
            # BREAK EVEN
            # ==================================================

            "be":
                be_var.get(),

            "friday_lock":
                friday_var.get(),
            # ==================================================
            # REVERSE
            # ==================================================

            "reverse":
                False,


            # ==================================================
            # SIDEWAY
            # ==================================================

            "sideway_filter":
                bool(
                    strategy_config.get(
                        "sideway_filter",
                        True
                    )
                ),


            # ==================================================
            # ANTI FOMO
            # ==================================================

            "anti_fomo":
                bool(
                    strategy_config.get(
                        "anti_fomo",
                        True
                    )
                ),


            # ==================================================
            # SESSION
            # ==================================================

            "auto_session":
                False,

            "sessions":
                [],


            # ==================================================
            # INDICATORS
            # ==================================================

            "bollinger":
                False,

            "supertrend":
                False,


            # ==================================================
            # NORMAL LOT
            # ==================================================

            "lot":
                normal_lot,


            # ==================================================
            # MULTI LOT
            # ==================================================

            "multi_lot":
                use_lot_chain.get(),

            "lots":
                lots,


            # ==================================================
            # RR
            # ==================================================

            "rr_risk":
                rr_risk_value,

            "rr_reward":
                rr_reward_value,


            # ==================================================
            # POSITION
            # ==================================================

            "has_position":
                bool(positions)
        }

    # ========================================================
    # HIDDEN CHART
    #
    # Không pack frame này.
    #
    # draw_chart vẫn chạy để giữ bot loop.
    # ========================================================

    hidden_chart = tk.Frame(
        root,
        width=1,
        height=1
    )

    draw_chart(
        hidden_chart,
        get_active,
        write_log,
        update_current_lot,
        username=username,
        close_app=close_all
    )
    # ========================================================
    # INITIAL LOG
    # ========================================================

    write_log(
        "⚙ FOREX BOT PRO READY"
    )

    write_log(
        "⚙ Phase 1 UI | Strategy configuration pending"
    )
    update_account_performance()
    # ========================================================
    # AUTO FIT WINDOW TO CONTENT
    # ========================================================

    # ========================================================
    # AUTO FIT WINDOW TO CONTENT
    # ========================================================

    root.update_idletasks()

    window_width = 1120

    # Chiều cao nội dung Tkinter yêu cầu
    content_height = root.winfo_reqheight()

    # Cộng thêm phần title bar + border của Windows
    window_height = content_height + 60

    # Không cho cửa sổ vượt quá màn hình
    screen_height = root.winfo_screenheight()

    max_height = screen_height - 40

    if window_height > max_height:
        window_height = max_height

    root.geometry(
        f"{window_width}x{window_height}"
    )

    root.resizable(
        False,
        False
    )