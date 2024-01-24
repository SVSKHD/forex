# Import the necessary libraries
import MetaTrader5 as mt5
import time
import pandas as pd

# Your MetaTrader 5 account credentials
account_number = 212678322  # Replace with your account number
password = '&Wem4EYY'  # Replace with your account password
server = 'OctaFX-Demo'  # Replace with your server name

# Connect to MetaTrader 5
def connect_to_mt5(account, password, server):
    if not mt5.initialize(login=account, password=password, server=server):
        print("Initialize() failed, error code =", mt5.last_error())
        quit()

# Calculate RSI
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    
    ma_up = up.rolling(window=period).mean()
    ma_down = down.rolling(window=period).mean()

    rsi = 100 - (100 / (1 + ma_up / ma_down))
    return rsi

# Calculate Moving Average
def calculate_moving_average(prices, period=20):
    return prices.rolling(window=period).mean()

# Calculate MACD
def calculate_macd(prices, slow=26, fast=12, signal=9):
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal

# Get historical data for a symbol
def get_historical_data(symbol, timeframe=mt5.TIMEFRAME_M1, n=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df.set_index('time')

# Calculate the highest high and lowest low
def calculate_high_low(prices, lookback_period=20):
    highest_high = prices['high'].rolling(window=lookback_period).max()
    lowest_low = prices['low'].rolling(window=lookback_period).min()
    return highest_high, lowest_low

# Decision making based on indicators
def make_decision(symbol, pip_scale):
    df = get_historical_data(symbol)
    # Calculate indicators
    df['rsi'] = calculate_rsi(df['close'])
    df['ma'] = calculate_moving_average(df['close'])
    df['macd'], df['macd_signal'] = calculate_macd(df['close'])
    df['highest_high'], df['lowest_low'] = calculate_high_low(df)

    latest_data = df.iloc[-1]

    # Decision logic for entry price with adjusted pips
    entry_price = None
    decision = "No Direction"
    if latest_data['close'] > latest_data['ma'] and latest_data['macd'] > latest_data['macd_signal'] and latest_data['close'] > latest_data['lowest_low'] + pip_scale:
        decision = "Long"
        entry_price = latest_data['close']
    elif latest_data['close'] < latest_data['ma'] and latest_data['macd'] < latest_data['macd_signal'] and latest_data['close'] < latest_data['highest_high'] - pip_scale:
        decision = "Short"
        entry_price = latest_data['close']

    return decision, entry_price

# Connect to MetaTrader 5 using your credentials
account_number = 212678322
password = '&Wem4EYY'
server = 'OctaFX-Demo'
connect_to_mt5(account_number, password, server)

# List of symbols you want to get data for
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

# Monitor and make trade decisions
try:
    print("Monitoring live market prices. Press Ctrl+C to stop.")
    while True:
        for symbol in symbols:
            pip_scale = 0.0025 if symbol in ["BTCUSD", "ETHUSD"] else 0.0015  # 25 pips for BTCUSD and ETHUSD, 15 pips for others
            decision, entry_price = make_decision(symbol, pip_scale)
            if entry_price:
                print(f"{symbol}: Trade Decision = {decision} at Price = {entry_price}")
            else:
                print(f"{symbol}: No Trade Decision")
        time.sleep(10)  # Wait for 60 seconds before the next update
except KeyboardInterrupt:
    print("Monitoring stopped.")

# Shutdown the MetaTrader 5 connection
mt5.shutdown()
