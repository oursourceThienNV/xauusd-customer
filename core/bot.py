import time
import MetaTrader5 as mt5
from config import *
from core.trade import open_trade, close_all
from data.history import record_trade
from ui.main_ui import log

def bot_loop():
    global running, cycle_profit, cycle_id

    while running:
        for symbol in symbols_state:

            pos = mt5.positions_get(symbol=symbol)

            if not pos:
                open_trade(symbol)
                time.sleep(1)
                continue

            p = max(pos, key=lambda x: x.time)
            profit = p.profit
            pos_type = "BUY" if p.type == 0 else "SELL"

            if profit >= TP_USD:
                close_all(symbol)
                log(f"[TP] {symbol}")
                record_trade(symbol, TRADE_MODE, "TP", profit, pos_type)
                open_trade(symbol)

            elif profit <= SL_USD:
                close_all(symbol)
                log(f"[SL] {symbol}")
                record_trade(symbol, TRADE_MODE, "SL", profit, pos_type)
                open_trade(symbol)

        time.sleep(1)