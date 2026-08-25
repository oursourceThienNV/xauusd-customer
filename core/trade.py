import MetaTrader5 as mt5
import time
from config import *
from ui.main_ui import log

def get_filling(symbol):
    return mt5.ORDER_FILLING_IOC

def detect_symbol():
    symbols = mt5.symbols_get()

    for s in symbols:
        if "XAUUSDM" in s.name.upper():
            return s.name

    for s in symbols:
        if "XAUUSD" in s.name.upper():
            return s.name

    return None

def ensure_symbol(symbol):
    info = mt5.symbol_info(symbol)

    if info is None:
        log(f"❌ Symbol không tồn tại: {symbol}")
        return False

    if not info.visible:
        mt5.symbol_select(symbol, True)
        log(f"👁️ Đã bật symbol: {symbol}")

    return True

def open_trade(symbol):
    global symbols_state

    if not ensure_symbol(symbol):
        return

    last_open = symbols_state[symbol].get("open_time", 0)

    if USE_DELAY and last_open > 0:
        log(f"⏳ Nghỉ {DELAY_TIME}s trước khi vào lệnh {symbol}")
        time.sleep(DELAY_TIME)

    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        log(f"❌ Không lấy được giá {symbol}")
        return

    if TRADE_MODE == "BUY":
        direction = 1
    elif TRADE_MODE == "SELL":
        direction = -1
    else:
        direction = symbols_state[symbol]["direction"]

    price = tick.ask if direction == 1 else tick.bid

    result = mt5.order_send({
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": LOT,
        "type": mt5.ORDER_TYPE_BUY if direction == 1 else mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": 30,
        "type_filling": mt5.ORDER_FILLING_IOC,
        "type_time": mt5.ORDER_TIME_GTC,
    })

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        log(f"{'BUY' if direction==1 else 'SELL'} {symbol}")
        symbols_state[symbol]["open_time"] = time.time()
    else:
        log(f"❌ Open fail {symbol}: {result.retcode} | {result.comment}")

def close_all(symbol):
    if not ensure_symbol(symbol):
        return

    pos = mt5.positions_get(symbol=symbol)
    if not pos:
        return

    for p in pos:
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            continue

        close_price = tick.bid if p.type == 0 else tick.ask

        result = mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": p.volume,
            "type": mt5.ORDER_TYPE_SELL if p.type == 0 else mt5.ORDER_TYPE_BUY,
            "position": p.ticket,
            "price": close_price,
            "deviation": 30,
            "type_filling": mt5.ORDER_FILLING_IOC,
            "type_time": mt5.ORDER_TIME_GTC,
        })

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            log(f"❌ Đóng lệnh | {round(p.profit,2)}$")