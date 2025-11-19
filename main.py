!pip install yfinance python-telegram-bot pandas ta nest_asyncio

import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
from telegram import Bot
import nest_asyncio
import asyncio

nest_asyncio.apply()  # برای کولب لازم است

BOT_TOKEN = "8490092715:AAE5Y5q49JQiak4Ljt2qdRB7Rc6BEONQOQM"
CHAT_ID = 5576089140

bot = Bot(BOT_TOKEN)

ATR_MULTIPLIER_SL = 1.0
ATR_MULTIPLIER_TP = 2.0
CHECK_INTERVAL = 15 * 60  # 15 دقیقه

async def gold_signal():
    gold = yf.Ticker("GC=F")
    data = gold.history(period="14d", interval="1h")

    # EMA
    data['EMA_short'] = EMAIndicator(data['Close'], window=10).ema_indicator()
    data['EMA_long'] = EMAIndicator(data['Close'], window=50).ema_indicator()

    # MACD
    macd = MACD(data['Close'], window_slow=26, window_fast=12, window_sign=9)
    data['MACD'] = macd.macd()
    data['MACD_signal'] = macd.macd_signal()

    # RSI
    data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()

    # Stochastic
    data['Stoch'] = StochasticOscillator(data['High'], data['Low'], data['Close'], window=14, smooth_window=3).stoch()

    # ATR
    data['ATR'] = AverageTrueRange(data['High'], data['Low'], data['Close'], window=14).average_true_range()

    last = data.iloc[-1]
    entry = last['Close']
    atr = last['ATR']
    trend = "بدون سیگنال ❌"
    stop = None
    take = None

    if last['EMA_short'] > last['EMA_long'] and last['RSI'] < 70 and last['MACD'] > last['MACD_signal'] and last['Stoch'] < 80:
        trend = "صعودی ⬆️"
        stop = entry - atr*ATR_MULTIPLIER_SL
        take = entry + atr*ATR_MULTIPLIER_TP
    elif last['EMA_short'] < last['EMA_long'] and last['RSI'] > 30 and last['MACD'] < last['MACD_signal'] and last['Stoch'] > 20:
        trend = "نزولی ⬇️"
        stop = entry + atr*ATR_MULTIPLIER_SL
        take = entry - atr*ATR_MULTIPLIER_TP

    msg = f"""📊 سیگنال حرفه‌ای طلا:
روند: {trend}
نقطه ورود: {entry:.2f}
"""
    if stop and take:
        msg += f"استاپ لاس: {stop:.2f}\nتی پی: {take:.2f}\n"

    await bot.send_message(chat_id=CHAT_ID, text=msg)
    print(msg)

async def main_loop():
    while True:
        await gold_signal()
        await asyncio.sleep(CHECK_INTERVAL)  # 15 دقیقه

# اجرای برنامه در کولب
loop = asyncio.get_event_loop()
loop.run_until_complete(main_loop())
