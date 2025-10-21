# XT-ScalperPro Mobile Trading Bot

## Overview
Advanced cryptocurrency scalping bot for XT Exchange USDT-M Futures with mobile (Android APK) support via Kivy. The bot features multiple trading signal modes, advanced stop-loss strategies, and real-time position monitoring through a Gradio web interface.

## Recent Changes (October 21, 2025)
- **Refactored** to use `ccxt.async_support` for proper async operations
- **Fixed** critical trading logic: separated entry orders from stop-loss orders
- **Removed** hardcoded API credentials for security (now uses environment variables only)
- **Improved** order placement with dedicated functions for entry, stop-loss, and take-profit
- **Updated** Kivy app to be Android-compatible (removed subprocess calls)
- **Enhanced** buildozer.spec with complete dependency list for APK building

## Project Architecture

### Main Components
1. **main.py** - Core trading bot with Gradio web UI
   - Async CCXT integration for XT Exchange
   - Three signal modes: ULTRA, SAFE, HYBRID
   - Eight stop-loss methods
   - Real-time position monitoring
   - Technical indicators: EMA (20, 50, 100), RSI (14)

2. **kivy_app.py** - Simplified mobile wrapper
   - Android-compatible interface
   - Configuration guide display
   - No subprocess dependencies (Android-safe)

3. **buildozer.spec** - APK build configuration
   - Complete Python dependencies list
   - Android API 31, minimum API 21
   - Permissions: INTERNET, NETWORK_STATE, STORAGE

### Trading Strategy
- **Signal Detection**: Uses EMA crossovers and RSI levels
- **Position Management**: Automatic TP1 (1.5%), TP2 (2.5%)
- **Risk Management**: Configurable SL methods with 1% default protection
- **Order Flow**: Market entry → Separate SL order → TP monitoring

## User Preferences
- API keys stored securely in environment variables
- No hardcoded credentials in source code
- Async-first design for concurrent operations

## Dependencies
- Python 3.11
- kivy==2.3.0
- ccxt (async support)
- pandas
- gradio
- python-dotenv
- buildozer (for APK generation)

## Environment Variables Required
- `XT_API_KEY` - XT Exchange API key (Futures trading permissions)
- `XT_API_SECRET` - XT Exchange API secret

## Building Android APK
```bash
buildozer android debug
```

The APK will be generated in `bin/` directory.

## Security Notes
- Never commit API credentials to version control
- Always use environment variables for sensitive data
- API keys require "Futures Trading" permissions on XT Exchange
