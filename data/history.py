import json, os
from datetime import datetime

DATA_DIR = os.path.join(os.path.expanduser("~"), "mt5_bot")
os.makedirs(DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(DATA_DIR, "trade_history.json")

trade_history = []
cycle_id = 0

def load_history():
    global trade_history
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            raw = json.load(f)
            trade_history = []
            for t in raw:
                t["time"] = datetime.fromisoformat(t["time"])
                trade_history.append(t)

def save_history():
    data = []
    for t in trade_history:
        item = t.copy()
        item["time"] = item["time"].isoformat()
        data.append(item)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def record_trade(symbol, mode, action, profit, direction):
    global trade_history, cycle_id

    trade_history.append({
        "time": datetime.now(),
        "mode": mode,
        "action": action,
        "profit": profit,
        "direction": direction,
        "cycle_id": cycle_id
    })

    if len(trade_history) > 5000:
        trade_history.pop(0)

    save_history()