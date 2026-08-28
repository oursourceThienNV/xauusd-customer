import tkinter as tk
from tkinter import messagebox
import MetaTrader5 as mt5
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import requests
from config import API_BASE_URL
auto_running = False
mt5_connected = False
first_trade_after_bot_start = False
cross_points = []
last_params = None
max_profit_map = {}
global_log = None
last_log_time = {}
log_buffer = []
LOG_BATCH_SIZE = 2
import datetime
import time
def now_utc_iso():
    return datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat().replace("+00:00", "Z")
last_trade_config = {}
last_open_tickets = set()
saved_closed_tickets = set()
multi_lot_index = 0
current_multi_lot = False
multi_lot_values = []
update_current_lot = None
loss_streak = 0
last_loss_signal = None
check_sideway = False
last_signal_price = None
last_entry_price = None
pending_closed_ticket = None
pending_closed_trade = None
pending_close_time = None
pending_close_timeout = 360
current_username = None
def get_multi_lot_index():
    return multi_lot_index
def is_auto_running():
    return auto_running
def parse_time_to_minutes(time_str):

    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except:
        return 0
def detect_symbol():
    symbols = mt5.symbols_get()
    for s in symbols:
        if "XAUUSD" in s.name.upper():
            return s.name
    return None

def get_data(symbol=None, bars=500):
    global mt5_connected

    if not mt5_connected:
        if not mt5.initialize():
            return None
        mt5_connected = True

    if symbol is None:
        symbol = detect_symbol()

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, bars)

    if rates is None or len(rates) == 0:
        return None

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df
def is_sideway(df):

    if len(df) < 100:
        return False

    price = df['close']

    high = df['high'].iloc[-20:].max()
    low = df['low'].iloc[-20:].min()

    range_price = high - low

    avg_range = (
        df['high'].rolling(20).max()
        - df['low'].rolling(20).min()
    )

    avg_range = avg_range.iloc[-50:].mean()

    ema50 = price.ewm(span=50).mean()

    ema_distance = abs(
        price.iloc[-1]
        - ema50.iloc[-1]
    )

    return (
        range_price < avg_range * 0.5
        and ema_distance < avg_range * 0.2
    )
def is_fomo_candle(df):

    if len(df) < 30:
        return False

    # ===== Nến vừa đóng =====
    open_price = df["open"].iloc[-2]
    close_price = df["close"].iloc[-2]
    high = df["high"].iloc[-2]
    low = df["low"].iloc[-2]

    body = abs(close_price - open_price)

    # ===== Trung bình thân 20 nến trước =====
    avg_body = (
        abs(df["close"] - df["open"])
        .iloc[:-2]
        .tail(20)
        .mean()
    )

    multiplier = 2.3
    min_body_ratio = 0.7

    threshold = avg_body * multiplier

    candle_range = high - low
    body_ratio = body / candle_range if candle_range > 0 else 0

    # ===== Không phải FOMO =====
    if body <= threshold:
        return False

    if body_ratio <= min_body_ratio:
        return False

    # ===== FOMO =====
    log_common(
        "🚫 Anti FOMO: Bỏ qua tín hiệu | "
        f"Thân nến={body:.2f} "
        f"(TB20={avg_body:.2f} x {multiplier} = {threshold:.2f}) | "
        f"Body chiếm {body_ratio*100:.1f}% chiều dài nến "
        f"(Yêu cầu > {min_body_ratio*100:.0f}%)"
    )

    return True
def get_sl_tp(signal, price, df, symbol, current):
    info = mt5.symbol_info(symbol)
    if info is None:
        log_common("❌ Không lấy được symbol info")
        return None, None

    point = info.point

    buffer_pip = current.get("buffer", 10)
    buffer = buffer_pip * point   # 10 pip như hình bạn
    risk = current.get("rr_risk", 1)
    reward = current.get("rr_reward", 1)

    if risk == 0:
        risk = 1

    rr = reward / risk
    if signal == "BUY":
        sl = df['low'].iloc[-10:].min() - buffer
        risk = price - sl
        tp = price + risk * rr
    else:
        sl = df['high'].iloc[-10:].max() + buffer
        risk = sl - price
        tp = price - risk * rr

    return sl, tp
def save_trading_transaction(transaction_data):
    try:
        response = requests.post(
            f"{API_BASE_URL}/trading-transaction",
            json=transaction_data,
            timeout=10
        )

        log_common(
            f"📡 Trading API Response | "
            f"Status={response.status_code} | "
            f"Body={response.text}"
        )

        response.raise_for_status()

        # API trả body rỗng vẫn là thành công
        if not response.text or not response.text.strip():
            log_common(
                "✅ Trading transaction API thành công | "
                f"HTTP={response.status_code} | Empty response"
            )
            return True

        try:
            data = response.json()

            log_common(
                f"✅ Trading transaction API thành công | "
                f"HTTP={response.status_code} | "
                f"Response={data}"
            )

            return True

        except ValueError as e:
            log_common(
                f"⚠️ API HTTP thành công nhưng response không phải JSON | "
                f"HTTP={response.status_code} | "
                f"Body={response.text} | "
                f"Error={e}"
            )
            return True

    except requests.exceptions.HTTPError as e:
        response = e.response

        log_common(
            f"❌ Trading transaction API HTTP ERROR | "
            f"Status={response.status_code if response else 'UNKNOWN'} | "
            f"Body={response.text if response else 'NO RESPONSE'}"
        )

        return False

    except requests.exceptions.Timeout:
        log_common(
            "❌ Trading transaction API TIMEOUT | "
            "Server không phản hồi trong thời gian quy định"
        )

        return False

    except requests.exceptions.ConnectionError as e:
        log_common(
            f"❌ Trading transaction API CONNECTION ERROR | "
            f"Error={e}"
        )

        return False

    except Exception as e:
        log_common(
            f"❌ Trading transaction API UNKNOWN ERROR | "
            f"Type={type(e).__name__} | "
            f"Error={e}"
        )

        return False
def process_trade_result(result, ticket):

    global multi_lot_index
    global loss_streak
    global last_loss_signal
    global last_entry_price

    # Lấy thông tin lệnh đang chờ
    trade = pending_closed_trade or {}

    # ==========================================
    # 1. WIN / LOSS
    # ==========================================

    if result == "WIN":

        loss_streak = 0
        last_entry_price = None
        last_loss_signal = None

        log_common(
            f"✅ WIN | Position={ticket}"
        )

    elif result == "LOSS":

        loss_streak += 1

        last_loss_signal = trade.get("signal")
        last_entry_price = trade.get("entry")

        log_common(
            f"❌ LOSS | Position={ticket}"
        )

    else:

        log_common(
            f"❌ Result không hợp lệ | "
            f"Position={ticket} | "
            f"Result={result}"
        )

        return False

    # ==========================================
    # 2. MULTI LOT
    # ==========================================

    if current_multi_lot and multi_lot_values:

        MAX_LEVEL = min(
            5,
            len(multi_lot_values)
        )

        if result == "WIN":

            multi_lot_index = 0

            log_common(
                "✅ WIN -> Reset L1"
            )

        elif result == "LOSS":

            # Chưa đến level cuối
            if multi_lot_index < MAX_LEVEL - 1:

                multi_lot_index += 1

                log_common(
                    f"❌ LOSS -> L{multi_lot_index + 1}"
                )

            # Loss ở level cuối -> Reset L1
            else:

                multi_lot_index = 0

                log_common(
                    f"❌ LOSS L{MAX_LEVEL} -> Reset L1"
                )

        if update_current_lot:

            update_current_lot(
                multi_lot_index
            )

    return True
def place_order(signal, lot, df, log, current):

    symbol = detect_symbol()
    if symbol is None:
        log_common("❌ Không tìm thấy symbol")
        return

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log_common("❌ Không lấy được giá")
        return

    if len(df) < 2:
        log_common("❌ Không đủ dữ liệu")
        return
    entry_price = (
        tick.ask
        if signal == "BUY"
        else tick.bid
    )
    order_type = (
        mt5.ORDER_TYPE_BUY
        if signal == "BUY"
        else mt5.ORDER_TYPE_SELL
    )

    action = mt5.TRADE_ACTION_DEAL

    sl, tp = get_sl_tp(signal, entry_price, df, symbol, current)

    log_common(f"🚀 {signal} | Lot: {lot}")
    log_common(f"Entry: {entry_price} | SL: {sl} | TP: {tp}")
    filling_modes = [
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_FOK,
        mt5.ORDER_FILLING_RETURN
    ]

    result = None
    used_filling = None

    # Chống mở trùng trước khi gửi lệnh
    existing_positions = mt5.positions_get(
        symbol=symbol
    )

    if existing_positions:
        log_common(
            "⛔ Đã có position đang mở, không mở thêm"
        )
        return

    # Thử từng Filling Mode
    for filling in filling_modes:

        request = {
            "action": action,
            "symbol": symbol,
            "volume": float(lot),
            "type": order_type,
            "price": float(entry_price),
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20,
            "magic": 999999,
            "comment": "AUTO BOT",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling
        }

        log_common(
            f"📤 Đang gửi lệnh MT5 | "
            f"Filling={filling}"
        )

        result = mt5.order_send(request)

        log_common(
            f"📥 MT5 Response | "
            f"Filling={filling} | "
            f"Result={result}"
        )

        if result is None:

            log_common(
                f"❌ order_send trả về None | "
                f"Error={mt5.last_error()}"
            )

            continue

        if result.retcode == mt5.TRADE_RETCODE_DONE:

            used_filling = filling

            log_common(
                f"✅ Order thành công | "
                f"Filling={used_filling} | "
                f"Order={result.order} | "
                f"Deal={result.deal}"
            )

            break

        log_common(
            f"⚠️ Filling={filling} thất bại | "
            f"Retcode={result.retcode} | "
            f"Comment={getattr(result, 'comment', '')}"
        )

    # Không filling mode nào thành công
    if (
        result is None
        or result.retcode != mt5.TRADE_RETCODE_DONE
    ):
        log_common(
            "❌ Mở lệnh thất bại với tất cả Filling Mode"
        )
        return
    global last_trade_config

    last_trade_config = {
        "strategy_version":
            "trend_v1",

        "ma_cross":
            current.get("ma_cross"),

        "ma_fast":
            current.get("ma_fast"),

        "ma_slow":
            current.get("ma_slow"),

        "ma_trend":
            current.get("ma_trend"),

        "ma_value":
            current.get("ma_value"),

        "ema_custom":
            current.get("ema_custom"),

        "ema_value":
            current.get("ema_value"),
        "trailing":
            current.get("trailing"),

        "be":
            current.get("be"),

        "sideway_filter":
            current.get("sideway_filter"),

        "anti_fomo":
            current.get("anti_fomo"),
        

        "lot":
            lot,

        "rr_reward":
            current.get("rr_reward"),

        "rr_risk":
            current.get("rr_risk"),

        "signal":
            signal,
        "entry": entry_price,

        "fomo_market":
            bool(is_fomo_candle(df)),

        "time_open":
            datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        
    }
   
    positions = None

    for _ in range(5):

        time.sleep(0.5)

        positions = mt5.positions_get(
            symbol=symbol
        )

        if positions:
            break

    if not positions:
        log_common(
            "❌ Không tìm thấy position sau khi mở lệnh"
        )
        return

    position_id = positions[0].ticket
    last_trade_config["ticket"] = position_id
    global last_open_tickets

    last_open_tickets = {
        p.ticket
        for p in positions
    }

    if position_id is None:
        log_common(
            "❌ Không xác định được Position Ticket"
        )
        return

    account_info = mt5.account_info()

    open_balance = (
        float(account_info.balance)
        if account_info
        else 0
    )
    global first_trade_after_bot_start

    is_first_trade = first_trade_after_bot_start
    trade_data = {

        # ==============================
        # TICKET
        # ==============================

        "ticket": position_id,

        # ==============================
        # ACCOUNT
        # ==============================

        "account": current_username,

        # ==============================
        # TRADE
        # ==============================

        "type": signal,

        "lot": float(lot),

        "openPrice": float(entry_price),

        "openTime": now_utc_iso(),

        "tradeStatus": "OPEN",

        # ==============================
        # ACCOUNT BALANCE
        # ==============================

        "openBalance": open_balance,

        # ==============================
        # BOT CONFIG
        # ==============================

        "strategy": current.get(
            "strategy",
            "trend_v1"
        ),

        "multiLot": bool(
            current.get("multi_lot", False)
        ),

        "lotChain": ",".join(
            str(x)
            for x in current.get("lots", [])
        ),

        # ==============================
        # RR
        # ==============================

        "rrRisk": float(
            current.get("rr_risk", 1)
        ),

        "rrReward": float(
            current.get("rr_reward", 1)
        ),

        # ==============================
        # MA
        # ==============================

        "maFast": current.get("ma_fast"),

        "maSlow": current.get("ma_slow"),

        "maTrendValue": current.get(
            "ma_value"
        ),

        # ==============================
        # FILTER
        # ==============================

        "sideway": bool(
            current.get(
                "sideway_filter",
                False
            )
        ),

        "fomo": bool(
            current.get(
                "anti_fomo",
                False
            )
        ),

        # ==============================
        # SYNC
        # ==============================

        "syncStatus": "SYNCED",

        "syncedDt": now_utc_iso(),

        # ==============================
        # SYSTEM
        # ==============================

        "createdDt": now_utc_iso(),

        "updatedDt": now_utc_iso(),

        # ==============================
        # FIRST TRADE
        # ==============================

        "firstTradeAfterBotStart": is_first_trade
    }
    save_trading_transaction(trade_data)
    if is_first_trade:
        first_trade_after_bot_start = False

        log_common(
            "✅ Đây là lệnh đầu tiên sau khi START BOT"
        )
    
def update_sl(position, new_sl, log):
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": position.ticket,
        "sl": new_sl,
        "tp": position.tp,
    }

    result = mt5.order_send(request)
    log_common(f"🔄 Update SL -> {new_sl} | KQ: {result}")
def trailing_stop_percent(pos, log):
    symbol = pos.symbol

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return

    price = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask
    entry = pos.price_open
    tp = pos.tp

    # ❗ phải có TP
    if tp == 0:
        return

    # ===== khoảng TP =====
    if pos.type == mt5.POSITION_TYPE_BUY:
        total_tp_distance = tp - entry
        current_profit_distance = price - entry
    else:
        total_tp_distance = entry - tp
        current_profit_distance = entry - price

    if total_tp_distance <= 0:
        return

    progress = current_profit_distance / total_tp_distance

    # ===== ĐẠT 50% TP → DỜI SL VỀ ENTRY =====
    if progress >= 0.5:
        if pos.type == mt5.POSITION_TYPE_BUY:
            if pos.sl < entry:
                log_common("🔒 BE: Dời SL về Entry")
                update_sl(pos, entry, log)

        else:
            if pos.sl > entry:
                log_common("🔒 BE: Dời SL về Entry")
                update_sl(pos, entry, log)
def trailing_after_be(pos, log):
    symbol = pos.symbol

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return

    price = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask
    entry = pos.price_open
    tp = pos.tp

    if tp == 0:
        return

    # ===== TÍNH PROGRESS =====
    if pos.type == mt5.POSITION_TYPE_BUY:
        total = tp - entry
        current = price - entry
    else:
        total = entry - tp
        current = entry - price

    if total <= 0:
        return

    progress = current / total

    # ❌ chưa đạt 50% thì bỏ
    if progress < 0.5:
        return

    # ===== TRAILING =====
    keep_ratio = 0.6  # giữ 60% lợi nhuận

    locked_profit = current * keep_ratio

    if pos.type == mt5.POSITION_TYPE_BUY:
        new_sl = entry + locked_profit

        if new_sl > pos.sl:
            log_common(f"🔄 Trailing BUY → SL: {round(new_sl,2)}")
            update_sl(pos, new_sl, log)

    else:
        new_sl = entry - locked_profit

        if new_sl < pos.sl:
            log_common(f"🔄 Trailing SELL → SL: {round(new_sl,2)}")
            update_sl(pos, new_sl, log)
def close_position(pos, log):
    symbol = pos.symbol

    if pos.type == mt5.POSITION_TYPE_BUY:
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": pos.volume,
        "type": order_type,
        "position": pos.ticket,
        "price": price,
        "deviation": 20,
        "magic": 999999,
        "comment": "AUTO CLOSE",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
def update_closed_trade(ticket):

    log_common(
        f"🔄 UPDATE | Đang tìm history Ticket={ticket}"
    )

    for i in range(30):

        deals = mt5.history_deals_get(
            position=ticket
        )

        close_deals = [
            d
            for d in (deals or [])
            if getattr(d, "symbol", "") == detect_symbol()
            and getattr(d, "position_id", None) == ticket
            and getattr(d, "entry", None) in (
                mt5.DEAL_ENTRY_OUT,
                mt5.DEAL_ENTRY_OUT_BY,
                mt5.DEAL_ENTRY_INOUT
            )
        ]

        if close_deals:

            profit = sum(
                float(d.profit)
                for d in close_deals
            )

            close_price = float(
                close_deals[-1].price
            )

            account_info = mt5.account_info()

            close_balance = (
                float(account_info.balance)
                if account_info
                else 0
            )

            update_data = {

                "ticket": ticket,

                "closePrice": close_price,

                "closeTime": now_utc_iso(),

                "profit": round(profit, 2),

                "closeBalance": close_balance,

                "tradeStatus": "CLOSED",

                "result":
                    "WIN"
                    if profit >= 0
                    else "LOSS",

                "syncStatus": "SYNCED",

                "syncedDt": now_utc_iso(),

                "updatedDt": now_utc_iso()
            }
            log_common(
                f"📤 UPDATE DB Request | "
                f"Data={update_data}"
            )
            success = save_trading_transaction(
                update_data
            )

            if success:

                log_common(
                    f"✅ UPDATE DB thành công | "
                    f"Ticket={ticket} | "
                    f"Profit={round(profit, 2)}"
                )
            else:
                log_common(
                    f"❌ UPDATE DB thất bại | "
                    f"Ticket={ticket} | "
                    f"Result={update_data['result']}"
                )
            return success

        log_common(
            f"⏳ Chưa có history | "
            f"Ticket={ticket} | "
            f"{i + 1}/30"
        )

        time.sleep(2)

    log_common(
        f"❌ Không tìm thấy history | "
        f"Ticket={ticket}"
    )

    return False
def close_all_positions(log):
    symbol = detect_symbol()
    global pending_closed_ticket
    global pending_close_time
    global pending_closed_trade

    if symbol is None:
        log_common("❌ Không tìm thấy symbol")
        return False

    positions = mt5.positions_get(symbol=symbol)

    if positions is None or len(positions) == 0:
        log_common("ℹ️ Không có lệnh cần đóng")
        return True

    log_common(
        f"🔒 WEEKEND LOCK | Đóng {len(positions)} lệnh"
    )

    for pos in positions:

        tick = mt5.symbol_info_tick(pos.symbol)

        if tick is None:
            continue

        if pos.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": pos.ticket,
            "price": price,
            "deviation": 20,
            "magic": 999999,
            "comment": "WEEKEND CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)

        log_common(
            f"❌ Đóng lệnh {pos.ticket} | KQ: {result}"
        )

        if result and result.retcode == mt5.TRADE_RETCODE_DONE:

            update_closed_trade(
                pos.ticket
            )

        else:

            log_common(
                f"❌ Đóng lệnh thất bại | "
                f"Ticket={pos.ticket}"
            )

    return True
def check_closed_positions(symbol):

    global multi_lot_index
    global auto_running
    global current_multi_lot
    global update_current_lot
    global last_open_tickets
    global loss_streak
    global last_loss_signal
    global last_entry_price

    global pending_closed_ticket
    global pending_closed_trade
    global pending_close_time

    positions = mt5.positions_get(symbol=symbol)

    current_tickets = set()

    if positions:
        current_tickets = {
            p.ticket for p in positions
        }

    # ==================================================
    # 1. PHÁT HIỆN POSITION VỪA ĐÓNG
    # ==================================================

    closed_tickets = (
        last_open_tickets
        - current_tickets
    )

    for ticket in closed_tickets:

        # Nếu đang chờ một lệnh khác thì không ghi đè
        if pending_closed_ticket is not None:
            continue

        pending_closed_ticket = ticket

        pending_closed_trade = {
            "position_id": ticket,
            "signal": last_trade_config.get("signal"),
            "entry": last_trade_config.get("entry"),
            "time_open": last_trade_config.get("time_open")
        }

        pending_close_time = datetime.datetime.now()

        log_common(
            f"⏳ Lệnh vừa đóng | "
            f"Position={ticket} | "
            f"Chờ history xác nhận..."
        )

    # ==================================================
    # 2. CHƯA CÓ LỆNH ĐANG CHỜ XÁC NHẬN
    # ==================================================

    if pending_closed_ticket is None:

        last_open_tickets = current_tickets
        return

    # ==================================================
    # 3. CHỜ 2 GIÂY SAU KHI POSITION ĐÓNG
    # ==================================================

    elapsed = (
        datetime.datetime.now()
        - pending_close_time
    ).total_seconds()

    if elapsed < 2:

        last_open_tickets = current_tickets
        return

    # ==================================================
    # 4. TÌM HISTORY ĐÚNG POSITION_ID
    # ==================================================

    try:

        deals = mt5.history_deals_get(
            position=pending_closed_ticket
        )

        log_common(
            f"🔎 HISTORY | "
            f"Position={pending_closed_ticket} | "
            f"Deals={len(deals) if deals else 0}"
        )

        if deals:
            for d in deals:

                if getattr(d, "symbol", "") != symbol:
                    continue

                log_common(
                    f"🔎 DEAL | "
                    f"ticket={getattr(d, 'ticket', None)} | "
                    f"order={getattr(d, 'order', None)} | "
                    f"position_id={getattr(d, 'position_id', None)} | "
                    f"entry={getattr(d, 'entry', None)} | "
                    f"profit={getattr(d, 'profit', None)} | "
                    f"reason={getattr(d, 'reason', None)}"
                )

        close_deals = []
        if deals:

            close_deals = [
                d
                for d in deals
                if getattr(d, "symbol", "") == symbol
                and getattr(
                    d,
                    "position_id",
                    None
                ) == pending_closed_ticket
                and getattr(
                    d,
                    "entry",
                    None
                ) in (
                    mt5.DEAL_ENTRY_OUT,
                    mt5.DEAL_ENTRY_OUT_BY,
                    mt5.DEAL_ENTRY_INOUT
                )
            ]

        # ==================================================
        # 5. CHƯA TÌM THẤY → GIỮ PENDING
        # ==================================================

        if not close_deals:

            log_common(
                f"⏳ Chưa tìm thấy history | "
                f"Position={pending_closed_ticket}"
            )

            # KHÔNG reset pending
            # Lần update sau sẽ tìm tiếp

            last_open_tickets = current_tickets
            return

        # ==================================================
        # 6. ĐÃ TÌM THẤY → TÍNH PROFIT
        # ==================================================

        profit = sum(
            float(d.profit)
            for d in close_deals
        )

        ticket = pending_closed_ticket
        trade = pending_closed_trade

        close_time = datetime.datetime.now()

        log_common(
            f"📕 {symbol} | "
            f"Position={ticket} | "
            f"Profit={round(profit, 2)}"
        )

        # ==================================================
        # 7. TÍNH THỜI GIAN GIAO DỊCH
        # ==================================================

        try:

            open_time = datetime.datetime.strptime(
                trade["time_open"],
                "%Y-%m-%d %H:%M:%S"
            )

            duration = int(
                (
                    close_time
                    - open_time
                ).total_seconds()
            )

        except Exception:

            duration = 0

        # ==================================================
        # 8. XÁC ĐỊNH KẾT QUẢ
        # ==================================================

        trade_result = (
            "WIN"
            if profit >= 0
            else "LOSS"
        )

        # ==================================================
        # 9. XỬ LÝ KẾT QUẢ - CHỈ 1 NƠI
        # ==================================================

        processed = process_trade_result(
            trade_result,
            ticket
        )

        if not processed:
            return

        close_price = None

        if close_deals:
            close_price = float(close_deals[-1].price)

        account_info = mt5.account_info()

        close_balance = (
            float(account_info.balance)
            if account_info
            else 0
        )

        update_data = {
            "ticket": ticket,

            "closePrice": close_price,

            "closeTime":
                close_time.astimezone(
                    datetime.timezone.utc
                ).isoformat().replace(
                    "+00:00",
                    "Z"
                ),

            "profit":
                round(profit, 2),

            "closeBalance":
                close_balance,

            "tradeStatus":
                "CLOSED",

            "result":trade_result,
                
            "syncStatus":
                "SYNCED",

            "syncedDt":
                now_utc_iso(),

            "updatedDt":
                now_utc_iso()
        }

        success = save_trading_transaction(update_data)

        if success:

            log_common(
                "✅ Đã xử lý WIN/LOSS và cập nhật DB xong"
            )

        else:

            log_common(
                f"❌ UPDATE DB thất bại | "
                f"Position={ticket} | "
            )
    # ==========================================
        pending_closed_ticket = None
        pending_closed_trade = None
        pending_close_time = None
        return

    except Exception as e:

        log_common(
            f"⚠️ History error: {e}"
        )

        # QUAN TRỌNG:
        # Không reset pending.
        # Lần update sau sẽ thử lại.

    last_open_tickets = current_tickets
def get_signal(df, current, log):
    global check_sideway
    global last_signal_price
    price = df['close']

    use_cross = current.get("ma_cross")
    use_ma = current.get("ma_trend")
    use_ema = current.get("ema_custom")
    
    signal = None
    

    # ===== MA CROSS =====
    if use_cross:

        ema_fast = price.ewm(span=current["ma_fast"]).mean()
        ema_slow = price.ewm(span=current["ma_slow"]).mean()

        buy = ema_fast.iloc[-2] < ema_slow.iloc[-2] and ema_fast.iloc[-1] > ema_slow.iloc[-1]
        sell = ema_fast.iloc[-2] > ema_slow.iloc[-2] and ema_fast.iloc[-1] < ema_slow.iloc[-1]

        if buy:
            signal = "BUY"
            last_signal_price = price.iloc[-1]
        elif sell:
            signal = "SELL"
            last_signal_price = price.iloc[-1]
        else:
            log_common("❌ MA Cross chưa xảy ra")
            check_sideway=False;
            return None
        

    # ===== MA =====
    if use_ma:

        ma = price.rolling(
            current["ma_value"]
        ).mean()
        trend = "BUY" if price.iloc[-1] > ma.iloc[-1] else "SELL"

        if not use_cross:
            signal = trend
        else:
            if signal != trend:
                log_common("❌ Sai MA Trend")
                return None

    # ===== EMA =====
    if use_ema:

        ema = price.ewm(span=current["ema_value"]).mean()
        trend = "BUY" if price.iloc[-1] > ema.iloc[-1] else "SELL"

        if not use_cross:
            signal = trend
        else:
            if signal != trend:
                log_common("❌ Sai EMA Trend")
                return None
    if not use_cross and not use_ma and not use_ema:
        log_common("❌ Chưa chọn chiến lược")
        return None

    # ===== CHƯA CÓ TÍN HIỆU =====
    if signal is None:
        return None

    # ===== SIDEWAY =====
    # ===== SIDEWAY =====
    if current.get("sideway_filter"):

        global loss_streak
        global last_loss_signal
        if loss_streak >= 1 and last_entry_price is not None:
            if check_sideway:
               log_common("⏳ 🔒 Sideway Chờ MA Cross mới")
               return None
            check_sideway=True
            if (
                last_entry_price - 3
                <= last_signal_price
                <= last_entry_price + 3
            ):
                log_common(
                    f"🔒 Sideway | LOSS={loss_streak} | "
                    f"LastEntry={last_entry_price:.2f} | "
                    f"SignalEntry={last_signal_price:.2f}"
                )
                return None
            log_common(
                f"✅ Sideway PASS | LOSS={loss_streak} | "
                f"LastEntry={last_entry_price:.2f} | "
                f"SignalEntry={last_signal_price:.2f}"
            )
    # ===== ANTI FOMO =====
    if current.get("anti_fomo"):

        if is_fomo_candle(df):

            log_common("🚫 Anti FOMO -> bỏ qua")

            return None
    return signal
def apply_session(current):

    if not current.get("auto_session"):
        return current

    sessions = current.get("sessions", [])

    now = datetime.datetime.now()

    current_minutes = now.hour * 60 + now.minute

    for s in sessions:

        if not s.get("enable"):
            continue

        start = parse_time_to_minutes(s["start"])
        end = parse_time_to_minutes(s["end"])

        if start <= current_minutes < end:

            current["ma_cross"] = s.get("ma_cross", False)

            current["ma_fast"] = s.get("ma_fast", 5)
            current["ma_slow"] = s.get("ma_slow", 12)

            current["ma_trend"] = s.get("ma_trend", False)
            current["ma_value"] = s.get("ma_value", 34)

            current["ema_custom"] = s.get("ema_custom", False)
            current["ema_value"] = s.get("ema_value", 50)

            current["buffer"] = s.get("buffer", 10)

            if not current.get("multi_lot"):
                current["lot"] = s.get("lot",0.1)

            current["rr_reward"] = s.get("rr_reward", 1.5)
            current["rr_risk"] = s.get("rr_risk", 1)

            current["trailing"] = s.get("trailing", False)

            current["be"] = s.get("be", False)

            current["sideway_filter"] = s.get("sideway_filter", False)

            current["anti_fomo"] = s.get("anti_fomo", False)
            log_common(
                f"🕒 Session Active "
                f"{s['start']}->{s['end']}"
            )

            return current

    return current
def is_weekend_lock():
    """
    True:
    - Từ 00:01 thứ 7
    - Đến hết chủ nhật

    False:
    - Thứ 2 -> thứ 6
    """

    now = datetime.datetime.now()

    # Saturday = 5
    # Sunday   = 6

    if now.weekday() == 5:
        # Thứ 7: từ 00:01 trở đi
        return (
            now.hour > 0
            or (now.hour == 0 and now.minute >= 1)
        )

    if now.weekday() == 6:
        return True

    return False
def check_mt5_auto_trading():

    terminal = mt5.terminal_info()

    if terminal is None:
        return False, "Không lấy được thông tin MT5"

    if not terminal.connected:
        return False, "MT5 chưa kết nối server"

    if not terminal.trade_allowed:
        return False, "Algo Trading trên MT5 đang TẮT"

    if terminal.tradeapi_disabled:
        return False, "MT5 đang chặn giao dịch từ Python"

    account = mt5.account_info()

    if account is None:
        return False, "Không lấy được thông tin tài khoản MT5"

    if not account.trade_allowed:
        return False, "Tài khoản MT5 không được phép giao dịch"

    if not account.trade_expert:
        return False, "Tài khoản MT5 không cho phép Expert/Algo Trading"

    return True, None


def start_auto(log, get_config=None, close_app=None):

    global auto_running
    global global_log
    global multi_lot_index
    global first_trade_after_bot_start

    # ==========================================
    # CHECK MT5 TRƯỚC KHI START
    # ==========================================

    allowed, message = check_mt5_auto_trading()

    if not allowed:

        auto_running = False

        messagebox.showwarning(
            "Không thể START BOT",
            "Vui lòng bật Algo Trading trên MetaTrader 5.\n\n"
            "Sau khi bật Algo Trading, "
            "hãy bấm START BOT lại."
        )

        return False

    # ==========================================
    # START BOT
    # ==========================================

    first_trade_after_bot_start = True

    multi_lot_index = 0

    if update_current_lot:
        update_current_lot(0)

    # Đây mới là hàm ghi log
    global_log = log

    auto_running = True

    log_common(
        "🟢 START BOT | Algo Trading đang bật"
    )

    return True
def stop_auto(log):
    global auto_running
    auto_running = False

    symbol = detect_symbol()

    if symbol is None:
        log_common("❌ Không tìm thấy symbol")
        return

    positions = mt5.positions_get(symbol=symbol)

    if positions is None or len(positions) == 0:
        log_common("⛔ Không có lệnh để đóng")
        return

    log_common("🛑 Đang đóng tất cả lệnh...")

    for pos in positions:

        ticket = pos.ticket

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            log_common(
                f"❌ Không lấy được giá | Ticket={ticket}"
            )
            continue

        if pos.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid

        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 999999,
            "comment": "AUTO CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        log_common(
            f"❌ Đóng lệnh {ticket} | KQ: {result}"
        )

        # ==========================================
        # ĐÓNG THÀNH CÔNG → UPDATE DB
        # ==========================================

        if (
            result
            and result.retcode == mt5.TRADE_RETCODE_DONE
        ):

            log_common(
                f"🔄 Bắt đầu UPDATE | Ticket={ticket}"
            )

            update_closed_trade(ticket)

        else:

            log_common(
                f"❌ Đóng lệnh thất bại | "
                f"Ticket={ticket}"
            )

    multi_lot_index = 0

    if update_current_lot:
        update_current_lot(0)

    log_common(
        "✅ Đã đóng tất cả lệnh"
    )
def write_log_api(logs):
    global current_username

    try:
        if not current_username:
            print("❌ WRITE LOG: Không có username")
            return False

        data = {
            "account": current_username,
            "logs": "\n".join(logs)
        }

        response = requests.post(
            f"{API_BASE_URL}/write-log",
            json=data,
            timeout=10
        )

        return response.status_code == 200

    except Exception as e:
        print(f"❌ WRITE LOG API ERROR: {e}")
        return False
def log_common(msg, delay=2):
    global global_log
    global last_log_time
    global log_buffer

    # ==========================================
    # HIỂN THỊ LOG TRÊN UI
    # ==========================================

    if global_log is None:
        print(msg)

    else:
        key = (
            msg.split(" ")[-1]
            if "❌" in msg or "⏳" in msg
            else msg
        )

        now = time.time()

        if (
            key not in last_log_time
            or now - last_log_time[key] > delay
        ):
            global_log(msg)
            last_log_time[key] = now

    # ==========================================
    # LẤY ACCOUNT
    # ==========================================

    account_info = mt5.account_info()

    global current_username

    account = current_username or "UNKNOWN"

    # ==========================================
    # LƯU LOG
    # ==========================================

    now = datetime.datetime.now()

    log_text = (
        f"account: {account} | "
        f"{now.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"{msg}"
    )

    log_buffer.append(log_text)

    # ==========================================
    # ĐỦ 60 LOG → GỬI API
    # ==========================================

    if len(log_buffer) >= LOG_BATCH_SIZE:

        logs_to_send = log_buffer[:LOG_BATCH_SIZE]

        success = write_log_api(logs_to_send)

        if success:
            del log_buffer[:LOG_BATCH_SIZE]
def draw_chart(
    parent,
    active,
    log,
    update_current_lot_callback,
    username=None,
    close_app=None
):
    global update_current_lot
    global current_username

    # Lưu username đã login
    current_username = username

    update_current_lot = update_current_lot_callback
    fig, ax = plt.subplots(figsize=(9, 5))

    # ===== UI PRO =====
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#020617")

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    candles = []
    signals = []

    # ========================
    # CROSSHAIR
    # ========================
    vline = ax.axvline(color="#64748b", linestyle="--", alpha=0.5)
    hline = ax.axhline(color="#64748b", linestyle="--", alpha=0.5)

    price_text = ax.text(0, 0, "", color="#e2e8f0",
                         bbox=dict(facecolor="#020617"))

    def on_move(event):
        if not event.inaxes:
            return

        if event.xdata is None or event.ydata is None:
            return

        vline.set_xdata([event.xdata, event.xdata])
        hline.set_ydata([event.ydata, event.ydata])

        price_text.set_position((event.xdata, event.ydata))
        price_text.set_text(f"{round(event.ydata,2)}")

        canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", on_move)

    # ========================
    # ZOOM SCROLL
    # ========================
    def on_scroll(event):
        base_scale = 1.2
        cur_xlim = ax.get_xlim()

        xdata = event.xdata

        if event.button == 'up':
            scale_factor = 1/base_scale
        else:
            scale_factor = base_scale

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor

        ax.set_xlim([xdata - new_width/2, xdata + new_width/2])
        canvas.draw_idle()

    fig.canvas.mpl_connect('scroll_event', on_scroll)
    
    cursor = mplcursors.cursor(ax, hover=mplcursors.HoverMode.Transient)

    def on_hover(sel):
                artist = sel.artist

                # ===== CANDLE =====
                for c in candles:
                    if c["artist"] == artist:
                        sel.annotation.set_text(
                            f"Time: {c['time'].strftime('%H:%M:%S')}\n"
                            f"Open: {round(c['open'],2)}\n"
                            f"High: {round(c['high'],2)}\n"
                            f"Low: {round(c['low'],2)}\n"
                            f"Close: {round(c['close'],2)}"
                        )
                        return

                # ===== SIGNAL =====
                for s in signals:
                    if s["artist"] == artist:
                        sel.annotation.set_text(
                            f"{s['type']} SIGNAL\n"
                            f"Time: {s['time'].strftime('%H:%M:%S')}\n"
                            f"Price: {round(s['price'],2)}"
                        )
                        return

    cursor.connect("add", on_hover)
    def update():

        global cross_points, last_params
        global auto_running
        global current_multi_lot
        global multi_lot_values

        global pending_closed_ticket
        global pending_close_time

        # ==================================================
        # 1. LẤY DỮ LIỆU
        # ==================================================

        df = get_data()

        if df is None:

            parent.after(2000, update)
            return


        # ==================================================
        # 2. RESET DATA HIỂN THỊ
        # ==================================================

        candles.clear()
        signals.clear()
        cross_points.clear()

        x = df["time"]
        price = df["close"]


        # ==================================================
        # 3. LẤY CONFIG HIỆN TẠI
        # ==================================================

        current = active()
        current = apply_session(current)

        current_multi_lot = current.get(
            "multi_lot",
            False
        )

        multi_lot_values = current.get(
            "lots",
            []
        )


        # ==================================================
        # 4. AUTO TRADE
        # ==================================================

        if auto_running:


            # ==============================================
            # 4.1 WEEKEND LOCK
            # ==============================================

            if (
                current.get("friday_lock")
                and is_weekend_lock()
            ):

                log_common(
                    "🔒 WEEKEND LOCK | "
                    "00:01 Thứ 7 → đóng toàn bộ lệnh"
                )

                closed = close_all_positions(log)

                if closed:

                    auto_running = False

                    log_common(
                        "🛑 Đã đóng tất cả lệnh và cập nhật DB"
                    )

                    if close_app:
                        close_app()

                parent.after(2000, update)
                return


            # ==============================================
            # 4.2 XÁC ĐỊNH SYMBOL
            # ==============================================

            symbol = detect_symbol()

            if symbol is None:

                log_common(
                    "❌ Không tìm thấy symbol"
                )

                parent.after(2000, update)
                return


            # ==============================================
            # 4.3 KIỂM TRA LỆNH VỪA ĐÓNG
            #
            # QUAN TRỌNG:
            #
            # Hàm này phải xử lý:
            #
            # Position đóng
            # → lấy MT5 history
            # → xác định WIN/LOSS
            # → process_trade_result()
            # → update DB
            #
            # pending chỉ được clear khi hoàn tất
            # ==============================================

            check_closed_positions(symbol)


            # ==============================================
            # 4.4 NẾU CÒN PENDING
            #
            # TUYỆT ĐỐI KHÔNG CHECK TÍN HIỆU MỚI
            # TUYỆT ĐỐI KHÔNG VÀO LỆNH MỚI
            # ==============================================

            if pending_closed_ticket is not None:

                # ==========================================
                # KIỂM TRA TIMEOUT
                # ==========================================

                if pending_close_time is not None:

                    elapsed = (
                        datetime.datetime.now()
                        - pending_close_time
                    ).total_seconds()

                    if elapsed >= pending_close_timeout:

                        ticket = pending_closed_ticket

                        log_common(
                            f"🚨 Không thể hoàn tất xử lý "
                            f"lệnh đã đóng sau "
                            f"{int(elapsed)} giây | "
                            f"Position={ticket}"
                        )

                        auto_running = False

                        messagebox.showwarning(
                            "Bot tạm dừng",
                            "Không thể hoàn tất xử lý giao dịch "
                            "từ MT5 trong thời gian cho phép.\n\n"
                            "Bot đã tạm dừng để tránh tiếp tục "
                            "giao dịch với sai mức lot.\n\n"
                            "Vui lòng kiểm tra:\n"
                            "- Kết nối mạng\n"
                            "- Kết nối MT5\n"
                            "- MT5 Terminal\n"
                            "- Server Database\n\n"
                            "Sau khi kiểm tra, vui lòng "
                            "khởi động lại bot."
                        )

                        parent.after(2000, update)
                        return


                # ==========================================
                # VẪN ĐANG XỬ LÝ
                # ==========================================

                log_common(
                    f"⏳ Đang xử lý lệnh vừa đóng | "
                    f"Position={pending_closed_ticket} | "
                    f"Không vào lệnh mới"
                )

                parent.after(2000, update)
                return


            # ==================================================
            # TỚI ĐƯỢC ĐÂY CÓ NGHĨA:
            #
            # - Không có lệnh pending
            # - WIN/LOSS đã xử lý xong
            # - Logic Multi Lot đã xử lý xong
            # - DB đã update xong
            #
            # → BÂY GIỜ MỚI ĐƯỢC CHECK LỆNH MỚI
            # ==================================================


            # ==============================================
            # 4.5 KIỂM TRA POSITION HIỆN TẠI
            # ==============================================

            positions = mt5.positions_get(
                symbol=symbol
            )

            orders = mt5.orders_get(
                symbol=symbol
            )


            # ==============================================
            # 4.6 ĐANG CÓ POSITION
            # ==============================================

            if positions is not None and len(positions) > 0:

                if len(positions) >= 2:

                    log_common(
                        "⛔ Đã đủ 2 lệnh"
                    )

                else:

                    pos = sorted(
                        positions,
                        key=lambda x: x.time
                    )[0]

                    log_common(
                        f"📊 Đang có lệnh | "
                        f"Profit: {round(pos.profit, 2)}"
                    )


                    # ======================================
                    # BREAK EVEN
                    # ======================================

                    if current.get("be"):

                        trailing_stop_percent(
                            pos,
                            log
                        )


                    # ======================================
                    # TRAILING
                    # ======================================

                    if current.get("trailing"):

                        trailing_after_be(
                            pos,
                            log
                        )


            # ==============================================
            # 4.7 CÓ PENDING ORDER
            # ==============================================

            elif orders is not None and len(orders) > 0:

                log_common(
                    "⏳ Đang có lệnh chờ (pending)..."
                )


            # ==============================================
            # 4.8 KHÔNG CÓ POSITION
            # → BÂY GIỜ MỚI ĐƯỢC TÌM TÍN HIỆU MỚI
            # ==============================================

            else:

                signal = get_signal(
                    df,
                    current,
                    log
                )


                if signal:

                    log_common(
                        f"🎯 Tín hiệu: {signal}"
                    )


                    # ======================================
                    # LOT MẶC ĐỊNH
                    # ======================================

                    lot = current.get(
                        "lot",
                        0.1
                    )


                    # ======================================
                    # MULTI LOT
                    # ======================================

                    if current_multi_lot:

                        if not multi_lot_values:

                            log_common(
                                "❌ Chưa nhập Multi Lot"
                            )

                            # Không vào lệnh nếu bật
                            # Multi Lot nhưng chưa có dữ liệu
                            parent.after(2000, update)
                            return


                        MAX_LEVEL = min(
                            5,
                            len(multi_lot_values)
                        )

                        index = min(
                            multi_lot_index,
                            MAX_LEVEL - 1
                        )

                        lot = multi_lot_values[index]


                        log_common(
                            f"📊 Multi Lot | "
                            f"L{index + 1} | "
                            f"Lot={lot}"
                        )


                    # ======================================
                    # VÀO LỆNH
                    # ======================================

                    place_order(
                        signal,
                        lot,
                        df,
                        log,
                        current
                    )


        # ==================================================
        # 5. CHẠY LẠI UPDATE
        # ==================================================

        parent.after(2000, update)


    update()