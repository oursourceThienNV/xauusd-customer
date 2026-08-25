import tkinter as tk
from tkinter import messagebox
import traceback
import sys

# ===== IMPORT LOGIN =====
from ui.login import show_login


def global_exception_handler(exc_type, exc_value, exc_traceback):

    error_text = "".join(
        traceback.format_exception(
            exc_type,
            exc_value,
            exc_traceback
        )
    )

    print(error_text)

    try:
        messagebox.showerror(
            "BOT ERROR",
            str(exc_value)
        )
    except:
        pass

    # KHÔNG raise lại
    # KHÔNG sys.exit()
    # KHÔNG root.destroy()

    return


sys.excepthook = global_exception_handler


# ===== UI APP =====
root = tk.Tk()

root.title("XAUUSD BOT")
root.geometry("900x850")
root.minsize(800, 700)
root.resizable(True, True)

show_login(root)

root.mainloop()