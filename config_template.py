# config_rava_251214.py – TALAK 100 % COMPLETO – 14/12/2025 18:00 AR

# -----------------------------------------------------------------------------
# --- CONFIGURACIÓN PRINCIPAL ---
# -----------------------------------------------------------------------------
API_KEY = "YOUR_BINANCE_API_KEY"
SECRET_KEY = "YOUR_BINANCE_SECRET_KEY"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

SYMBOLS = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "SUI-USDT"]

# TIMEFRAMES
ENABLE_15M = True
ENABLE_4H  = True

# INDICATORS
RSI_LENGTH      = 14
EMA10_LENGTH    = 10
EMA20_LENGTH    = 20
EMA50_LENGTH    = 50
MACD_FAST       = 12
MACD_SLOW       = 26
MACD_SIGNAL     = 9
STOCH_K         = 14
STOCH_D         = 3
STOCH_SMOOTH    = 3
VOLUME_LOOKBACK = 20

# TALAK CONDITIONS
STOCH_OVERSOLD   = 28
STOCH_OVERBOUGHT = 72

# SAFETY (only for catastrophes, never blocks normal trades)
SAFETY_LONG_MACDH  = {"BTC-USDT": -250, "ETH-USDT": -250, "SOL-USDT": -250, "SUI-USDT": -250}
SAFETY_SHORT_MACDH = {"BTC-USDT": +250, "ETH-USDT": +250, "SOL-USDT": +250, "SUI-USDT": +250}

# HARD STOP LOSS
SL_PCT = -1.8   # 1.8 % maximum loss (you can change to -1.5 if you want)

# COOLDOWN between same symbol/timeframe entries
COOLDOWN_MINUTES = 30

# NEW — 5X LEVERAGE FOR BINGX
LEVERAGE = 5
MARGIN_MODE = "isolated"   # or "cross" if you prefer