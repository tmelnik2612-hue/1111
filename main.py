# ==========================
# main.py — XT-ScalperPro Android FULL (USDT-M FIXED)
# ==========================
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from decimal import Decimal
import logging
import gradio as gr
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# 📌 GLOBALS
# ==========================
API_KEY = os.getenv("XT_API_KEY")
API_SECRET = os.getenv("XT_API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("XT_API_KEY and XT_API_SECRET must be set in environment variables")

MIN_ORDER_USDT = 5
MAX_ORDER_USDT = 10
POSITION_SIZE_USDT = 10
SIGNAL_MODE = "ULTRA"
SL_METHOD = 1
GUARD_MODE = 1

bot_running = False
current_positions = {}
_all_symbols = []
live_messages = []

# ==========================
# 📌 EXCHANGE INIT (XT Futures USDT-M)
# ==========================
exchange = ccxt.xt({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
    "options": {
        "defaultType": "swap",
        "defaultSubType": "linear",
    },
})

# ==========================
# 📌 LOGGER
# ==========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("XT-ScalperPro")

# ==========================
# 📌 UTILS
# ==========================
async def fetch_ohlcv(symbol, timeframe='15m', limit=100):
    try:
        data = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume'])
        return df
    except Exception as e:
        logger.warning(f"fetch_ohlcv error {symbol}: {e}")
        return pd.DataFrame(columns=['timestamp','open','high','low','close','volume'])

async def get_last_price(symbol):
    try:
        ticker = await exchange.fetch_ticker(symbol)
        return float(ticker["last"])
    except Exception as e:
        logger.warning(f"get_last_price error {symbol}: {e}")
        return None

def calc_order_qty(usdt_amount, price):
    return round(usdt_amount / price, 4)

async def telegram_update(msg):
    live_messages.append(msg)
    logger.info(msg)

# ==========================
# 📊 SIGNALS
# ==========================
async def check_signal(symbol):
    try:
        df = await fetch_ohlcv(symbol, '15m', limit=120)
        if df.empty or len(df) < 50:
            return "none"

        df['ema_fast'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_trend'] = df['close'].ewm(span=100, adjust=False).mean()

        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss.replace(0, 1e-10)
        df['rsi'] = 100 - (100 / (1 + rs))

        last, prev = df.iloc[-1], df.iloc[-2]
        close, ema_f, ema_s, ema_tr, rsi = map(float, [last['close'], last['ema_fast'], last['ema_slow'], last['ema_trend'], last['rsi']])
        prev_close = float(prev['close'])

        if SIGNAL_MODE == "ULTRA":
            if rsi < 32 and close > ema_f > ema_s and close > prev_close:
                return "buy"
            if rsi > 68 and close < ema_f < ema_s and close < prev_close:
                return "sell"
        elif SIGNAL_MODE == "SAFE":
            if rsi < 28 and close > ema_f > ema_s > ema_tr and (close - prev_close) / prev_close > 0.002:
                return "buy"
            if rsi > 72 and close < ema_f < ema_s < ema_tr and (prev_close - close) / prev_close > 0.002:
                return "sell"
        elif SIGNAL_MODE == "HYBRID":
            if rsi < 35 and ema_f > ema_s and close > ema_f:
                return "buy"
            if rsi > 65 and ema_f < ema_s and close < ema_f:
                return "sell"
        return "none"
    except Exception as e:
        await telegram_update(f"⚠️ Signal check failed {symbol}: {e}")
        return "none"

# ==========================
# 📈 PLACE ORDER
# ==========================
async def place_entry_order(symbol, side, amount):
    """Place a market entry order"""
    try:
        order = await exchange.create_market_order(symbol, side, float(amount))
        await telegram_update(f"✅ ENTRY {side.upper()} {symbol} | Qty: {amount}")
        return order
    except Exception as e:
        await telegram_update(f"⚠️ Entry order failed {symbol}: {e}")
        logger.warning(f"Failed entry order {symbol}: {e}")
        return None

async def place_stop_loss_order(symbol, side, amount, entry_price, sl_method=None):
    """Place a separate stop-loss order after entry"""
    global SL_METHOD
    if sl_method is None:
        sl_method = SL_METHOD
    
    close_side = "sell" if side == "buy" else "buy"
    sl_price = entry_price * (0.99 if side == "buy" else 1.01)
    
    try:
        if sl_method in [1, 2, 3, 7]:
            order = await exchange.create_market_order(symbol, close_side, float(amount), {
                "stopPrice": float(sl_price),
                "reduceOnly": True
            })
            await telegram_update(f"🛡️ SL set {symbol} @ {sl_price:.4f} (Method {sl_method})")
        elif sl_method in [4, 6]:
            order = await exchange.create_limit_order(symbol, close_side, float(amount), float(sl_price), {
                "reduceOnly": True
            })
            await telegram_update(f"🛡️ SL LIMIT set {symbol} @ {sl_price:.4f}")
        else:
            await telegram_update(f"⚠️ SL method {sl_method} using market stop @ {sl_price:.4f}")
            order = await exchange.create_market_order(symbol, close_side, float(amount), {
                "stopPrice": float(sl_price),
                "reduceOnly": True
            })
        return order
    except Exception as e:
        await telegram_update(f"⚠️ SL order failed {symbol}: {e}")
        logger.warning(f"Failed SL order {symbol}: {e}")
        return None

async def place_take_profit_order(symbol, side, amount, price):
    """Place a take profit order"""
    close_side = "sell" if side == "buy" else "buy"
    try:
        order = await exchange.create_limit_order(symbol, close_side, float(amount), float(price), {
            "reduceOnly": True
        })
        await telegram_update(f"🎯 TP order placed {symbol} @ {price:.4f}")
        return order
    except Exception as e:
        await telegram_update(f"⚠️ TP order failed {symbol}: {e}")
        logger.warning(f"Failed TP order {symbol}: {e}")
        return None

# ==========================
# 📊 MONITOR POSITIONS
# ==========================
async def monitor_positions():
    """Monitor positions and manage TP levels manually if needed"""
    for sym, pos in list(current_positions.items()):
        last_price = await get_last_price(sym)
        if not last_price:
            continue

        side = pos["side"]
        amt = Decimal(str(pos["contracts"]))
        entry = Decimal(str(pos["entryPrice"]))
        tp1 = entry * (Decimal("1.015") if side == "buy" else Decimal("0.985"))
        tp2 = entry * (Decimal("1.025") if side == "buy" else Decimal("0.975"))

        if not pos.get("tp1_closed", False) and ((side == "buy" and last_price >= tp1) or (side == "sell" and last_price <= tp1)):
            await place_take_profit_order(sym, side, float(amt / 2), float(tp1))
            pos["tp1_closed"] = True
            await telegram_update(f"🏆 TP1 hit {sym}")

        if not pos.get("tp2_closed", False) and ((side == "buy" and last_price >= tp2) or (side == "sell" and last_price <= tp2)):
            await place_take_profit_order(sym, side, float(amt / 2), float(tp2))
            pos["tp2_closed"] = True
            await telegram_update(f"🏆 TP2 hit {sym}")

# ==========================
# 📌 UPDATE SYMBOLS
# ==========================
async def update_symbols():
    global _all_symbols
    try:
        markets = await exchange.load_markets()
        _all_symbols = [s for s in markets if s.endswith("USDT:USDT")]
        logger.info(f"Loaded {len(_all_symbols)} symbols.")
    except Exception as e:
        logger.warning(f"update_symbols error: {e}")

# ==========================
# 🤖 BOT LOGIC
# ==========================
async def start_bot():
    global bot_running
    bot_running = True
    await update_symbols()
    await telegram_update("🚀 XT-ScalperPro started")
    while bot_running:
        for sym in _all_symbols[:10]:
            if sym not in current_positions:
                sig = await check_signal(sym)
                if sig in ["buy", "sell"]:
                    price = await get_last_price(sym)
                    if price:
                        qty = calc_order_qty(MIN_ORDER_USDT, price)
                        if qty > 0:
                            entry_order = await place_entry_order(sym, sig, qty)
                            if entry_order:
                                current_positions[sym] = {
                                    "side": sig,
                                    "contracts": qty,
                                    "entryPrice": price,
                                    "tp1_closed": False,
                                    "tp2_closed": False,
                                }
                                await place_stop_loss_order(sym, sig, qty, price)
        await monitor_positions()
        await asyncio.sleep(3)

def stop_bot():
    global bot_running
    bot_running = False
    return "Bot stopped"

def get_positions():
    if not current_positions:
        return "No active positions"
    return "\n".join([f"{s} | {p['side']} | {p['contracts']} | entry {p['entryPrice']}" for s, p in current_positions.items()])

async def get_signals():
    sig_text = ""
    for sym in _all_symbols[:20]:
        sig = await check_signal(sym)
        if sig != "none":
            sig_text += f"{sym}: {sig}\n"
    return sig_text or "No signals"

def get_logs():
    return "\n".join(live_messages[-20:])

def update_signal_mode(mode):
    global SIGNAL_MODE
    SIGNAL_MODE = mode
    return f"Signal mode updated to {mode}"

def update_sl_method(method):
    global SL_METHOD
    SL_METHOD = int(method)
    return f"SL method updated to {int(method)}"

def update_guard_mode(mode):
    global GUARD_MODE
    GUARD_MODE = int(mode)
    return f"Guard mode updated to {int(mode)}"

# ==========================
# 🖥️ GRADIO UI
# ==========================
def create_gradio_interface():
    with gr.Blocks(title="XT-ScalperPro") as demo:
        gr.Markdown("# 🤖 XT-ScalperPro Android - USDT-M Futures")
        gr.Markdown("Advanced scalping bot for XT exchange with multiple signal modes and stop-loss strategies")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### ⚙️ Configuration")
                signal_mode = gr.Radio(["ULTRA", "SAFE", "HYBRID"], label="Signal Mode", value=SIGNAL_MODE)
                sl_method = gr.Slider(1, 8, value=SL_METHOD, step=1, label="SL Method (1-8)")
                guard_mode = gr.Slider(1, 4, value=GUARD_MODE, step=1, label="Guard Mode (1-4)")
                
                signal_mode.change(update_signal_mode, inputs=[signal_mode], outputs=[])
                sl_method.change(update_sl_method, inputs=[sl_method], outputs=[])
                guard_mode.change(update_guard_mode, inputs=[guard_mode], outputs=[])
                
            with gr.Column():
                gr.Markdown("### 🎮 Controls")
                start_btn = gr.Button("🟢 START BOT", variant="primary")
                stop_btn = gr.Button("🔴 STOP BOT", variant="stop")
                
                status_output = gr.Textbox(label="Status", lines=2)
                
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📊 Active Positions")
                positions_output = gr.Textbox(label="Positions", lines=10)
                positions_refresh = gr.Button("Refresh Positions")
                
            with gr.Column():
                gr.Markdown("### 📈 Signals")
                signals_output = gr.Textbox(label="Trading Signals", lines=10)
                signals_refresh = gr.Button("Refresh Signals")
        
        gr.Markdown("### 📋 Live Logs")
        logs_output = gr.Textbox(label="Logs", lines=8)
        logs_refresh = gr.Button("Refresh Logs")
        
        start_btn.click(lambda: asyncio.create_task(start_bot()) or "Bot started!", outputs=[status_output])
        stop_btn.click(stop_bot, outputs=[status_output])
        positions_refresh.click(get_positions, outputs=[positions_output])
        signals_refresh.click(get_signals, outputs=[signals_output])
        logs_refresh.click(get_logs, outputs=[logs_output])
        
    return demo

# ==========================
# 📌 MAIN
# ==========================
async def cleanup():
    """Cleanup exchange connection"""
    global bot_running
    bot_running = False
    await exchange.close()
    logger.info("Exchange connection closed")

if __name__ == "__main__":
    try:
        demo = create_gradio_interface()
        demo.launch(server_name="0.0.0.0", server_port=5000, share=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(cleanup())
        except:
            pass
