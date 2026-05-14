# bot_talak_clase8_VIOLETA_V14.py
# Profesor Eduardo Talak – Clase 8 – 16/12/2025
# Leverage 5x in messages + SL EMA20/10

import time
import requests
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from config_rava_251214 import *

positions = {}
last_entry = {}
heartbeat = 0

def tg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                      json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except:
        pass

def price(sym):
    try:
        return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={sym.replace('-','')}").json()["price"])
    except:
        return None

def get_df(sym, tf):
    try:
        raw = requests.get("https://api.binance.com/api/v3/klines",
                           params={"symbol": sym.replace("-",""), "interval": tf, "limit": 300}, timeout=10).json()
        df = pd.DataFrame(raw, columns=["ts","o","h","l","c","v","ct","qv","trades","tbbv","tbqv","ignore"])
        df = df[["o","h","l","c","v"]].astype(float)
        df["vol_avg"] = df["v"].rolling(VOLUME_LOOKBACK).mean()
        df["rsi"]     = ta.rsi(df["c"], RSI_LENGTH)
        df["ema10"]   = ta.ema(df["c"], EMA10_LENGTH)
        df["ema20"]   = ta.ema(df["c"], EMA20_LENGTH)
        df["ema50"]   = ta.ema(df["c"], EMA50_LENGTH)
        df["macd_h"]  = ta.macd(df["c"], fast=12, slow=26, signal=9)["MACDh_12_26_9"]
        st = ta.stoch(df["h"], df["l"], df["c"])
        df["k"] = st["STOCHk_14_3_3"]
        df["d"] = st["STOCHd_14_3_3"]
        df.dropna(inplace=True)
        return df
    except:
        return pd.DataFrame()

tg("<b>BOT TALAK CLASE 8 – VIOLETA V14</b>\nProfesor Eduardo Talak – 15/12/2025\nLeverage 5x + EMA SL")
print("BOT VIOLETA V14 – RUNNING")

while True:
    try:
        if time.time() - heartbeat >= 60:
            print(f"BOT VIVO – {datetime.now():%H:%M:%S} – {len(positions)} posiciones")
            heartbeat = time.time()

        for sym in SYMBOLS:
            df15 = get_df(sym, "15m") if ENABLE_15M else pd.DataFrame()
            df4h = get_df(sym, "4h")  if ENABLE_4H  else pd.DataFrame()
            if len(df15)<3 and len(df4h)<3: continue
            p = price(sym)
            if not p: continue

            for tf, df in [("15m", df15), ("4h", df4h)]:
                if len(df) < 4: continue
                prev = df.iloc[-2]
                cur  = df.iloc[-1]
                key  = f"{sym}_{tf}"

                k15p = df15.iloc[-2]["k"] if len(df15)>=2 else 0
                k15c = df15.iloc[-1]["k"] if len(df15)>=1 else 0
                d15p = df15.iloc[-2]["d"] if len(df15)>=2 else 0
                d15c = df15.iloc[-1]["d"] if len(df15)>=1 else 0
                k4hp = df4h.iloc[-2]["k"] if len(df4h)>=2 else 0
                k4hc = df4h.iloc[-1]["k"] if len(df4h)>=1 else 0
                d4hp = df4h.iloc[-2]["d"] if len(df4h)>=2 else 0
                d4hc = df4h.iloc[-1]["d"] if len(df4h)>=1 else 0

                vol = round(cur.v / cur.vol_avg, 2) if cur.vol_avg > 0 else 0
                ema = f"{cur.ema10:,.4f}|{cur.ema20:,.4f}|{cur.ema50:,.4f}"
                delta_talak = round(prev.macd_h - cur.macd_h, 6)

                vol_ok = (tf == "4h") or (vol >= 1.5)

                long  = prev.k <= 28 and cur.k > cur.d and cur.macd_h < 0 and delta_talak < 0 and vol_ok
                short = prev.k >= 72 and cur.k < cur.d and cur.macd_h > 0 and delta_talak > 0 and p < cur.ema20 * 0.995 and vol_ok

                cooldown = (datetime.now() - last_entry.get(key, datetime.min)).total_seconds() >= COOLDOWN_MINUTES * 60

                if (long or short) and key not in positions and cooldown:
                    direction = "LONG" if long else "SHORT"
                    positions[key] = {"dir": direction, "entry": p, "time": datetime.now(), "sl_price": cur.ema20 if direction == "LONG" else cur.ema10}
                    last_entry[key] = datetime.now()

                    vol_text = f" | Vol {vol}×" if tf == "15m" else ""
                    tg(f"<b>ENTRY {direction} {sym} {tf.upper()} [5x Leverage]</b> ${p:,.4f} – {datetime.now():%d/%m %H:%M}\n"
                       f"15m: K {k15p:.1f}→{k15c:.1f} | D {d15p:.1f}→{d15c:.1f}\n"
                       f"4h : K {k4hp:.1f}→{k4hc:.1f} | D {d4hp:.1f}→{d4hc:.1f}\n"
                       f"MACD-h {prev.macd_h:+.6f} → {cur.macd_h:+.6f}\n"
                       f"<b>Δ TALAK {delta_talak:+.6f}</b>\n"
                       f"RSI {cur.rsi:.1f}{vol_text}\n"
                       f"EMA10|20|50: {ema}")

                # EMA SL
                if key in positions:
                    pos = positions[key]
                    sl_price = pos["sl_price"]
                    if pos["dir"] == "LONG" and p < sl_price or pos["dir"] == "SHORT" and p > sl_price:
                        mins = int((datetime.now() - pos["time"]).total_seconds() / 60)
                        vol_text = f" | Vol {vol}×" if tf == "15m" else ""
                        tg(f"<b>EXIT {pos['dir']} {sym} {tf.upper()} – EMA SL</b>\n"
                           f"${p:,.4f} ← ${pos['entry']:,.4f}\n"
                           f"15m: K {k15p:.1f}→{k15c:.1f} | D {d15p:.1f}→{d15c:.1f}\n"
                           f"4h : K {k4hp:.1f}→{k4hc:.1f} | D {d4hp:.1f}→{d4hc:.1f}\n"
                           f"MACD-h {prev.macd_h:+.6f} → {cur.macd_h:+.6f}\n"
                           f"<b>Δ TALAK {delta_talak:+.6f}</b>\n"
                           f"RSI {cur.rsi:.1f}{vol_text}\n"
                           f"EMA10|20|50: {ema}")
                        del positions[key]

        time.sleep(2)

    except Exception as e:
        tg(f"<b>ERROR:</b> {str(e)}")
        time.sleep(10)