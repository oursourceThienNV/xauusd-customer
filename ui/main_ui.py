import tkinter as tk

log_box = None

def set_log(widget):
    global log_box
    log_box = widget
    log_text.tag_config("buy", foreground="green")
    log_text.tag_config("sell", foreground="red")

def log(msg):
    if log_box:
        if "BUY" in msg:
            log_box.insert(tk.END, msg + "\n", "buy")
        elif "SELL" in msg:
            log_box.insert(tk.END, msg + "\n", "sell")
        else:
            log_box.insert(tk.END, msg + "\n")

        log_box.see(tk.END)

def build_ui(root):
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    log_text = tk.Text(frame, height=15)
    log_text.pack()

    set_log(log_text)

    return frame