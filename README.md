# XT-ScalperPro Mobile Trading Bot

Advanced scalping bot for XT Exchange USDT-M Futures with mobile support.

## Features

- **Multiple Signal Modes**: ULTRA, SAFE, and HYBRID trading strategies
- **Advanced Stop-Loss**: 8 different SL methods for risk management
- **Mobile Interface**: Kivy-based Android app with WebView
- **Real-time Monitoring**: Live position tracking and signal detection
- **Auto Trading**: Automated order placement based on technical indicators

## Configuration

### Signal Modes
- **ULTRA**: Aggressive scalping (RSI < 32 for buy, > 68 for sell)
- **SAFE**: Conservative approach (RSI < 28 for buy, > 72 for sell)
- **HYBRID**: Balanced strategy (RSI < 35 for buy, > 65 for sell)

### SL Methods (1-8)
1. STOP_MARKET
2. STOP
3. STOP_LIMIT
4. LIMIT
5. OCO (One-Cancels-Other)
6. LIMIT with reduceOnly
7. MARKET
8. GUARD with buffer

## Running the App

### Desktop/Web Version
```bash
python main.py
```
Access at: http://localhost:5000

### Mobile/Kivy Version
```bash
python kivy_app.py
```

### Building APK
```bash
buildozer android debug
```

## API Configuration

Update your XT Exchange API credentials in `main.py` or use environment variables:
- `XT_API_KEY`
- `XT_API_SECRET`

## Requirements

- Python 3.11+
- Kivy
- ccxt
- pandas
- gradio
- buildozer (for APK building)

## Safety Notice

This bot trades with real money. Always:
- Test with small amounts first
- Monitor positions regularly
- Use proper risk management
- Keep API keys secure
